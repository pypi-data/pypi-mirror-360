"""FAISS-based similarity retrieval for conversation memory."""

import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Tuple, Optional, Union
from ..memory.conversation_memory import ConversationMemory, ConversationEntry


class SimilarityRetriever:
    """FAISS-based retrieval system for conversation similarity search."""
    
    def __init__(self, memory: ConversationMemory, index_dir: str = "faiss_indices"):
        """Initialize the similarity retriever.
        
        Args:
            memory: ConversationMemory instance.
            index_dir: Directory to store FAISS indices.
        """
        self.memory = memory
        self.index_dir = index_dir
        self.indices = {}  # Dict of embedding_type -> faiss.Index
        self.id_mappings = {}  # Dict of embedding_type -> List[entry_id]
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories."""
        os.makedirs(self.index_dir, exist_ok=True)
    
    def build_index(self, user_id: str = None, embedding_types: List[str] = None,
                   force_rebuild: bool = False):
        """Build FAISS indices for similarity search.
        
        Args:
            user_id: Optional user ID to filter conversations.
            embedding_types: List of embedding types to index. Defaults to all.
            force_rebuild: Whether to force rebuilding existing indices.
        """
        if embedding_types is None:
            embedding_types = ["semantic", "style", "combined"]
        
        conversations = self.memory.get_user_conversations(user_id) if user_id else []
        if not conversations:
            print("No conversations found to index.")
            return
        
        for emb_type in embedding_types:
            index_path = os.path.join(self.index_dir, f"{emb_type}_{user_id or 'global'}.index")
            mapping_path = os.path.join(self.index_dir, f"{emb_type}_{user_id or 'global'}.mapping")
            
            if os.path.exists(index_path) and not force_rebuild:
                self._load_index(emb_type, user_id)
                continue
            
            embeddings = []
            entry_ids = []
            
            for conv in conversations:
                if emb_type in conv.embeddings:
                    embeddings.append(conv.embeddings[emb_type])
                    entry_ids.append(conv.entry_id)
            
            if not embeddings:
                print(f"No {emb_type} embeddings found.")
                continue
            
            embeddings_array = np.array(embeddings).astype('float32')
            dimension = embeddings_array.shape[1]
            
            # Create FAISS index
            index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings_array)
            index.add(embeddings_array)
            
            # Store index and mappings
            self.indices[f"{emb_type}_{user_id or 'global'}"] = index
            self.id_mappings[f"{emb_type}_{user_id or 'global'}"] = entry_ids
            
            # Save to disk
            faiss.write_index(index, index_path)
            with open(mapping_path, 'wb') as f:
                pickle.dump(entry_ids, f)
            
            print(f"Built {emb_type} index with {len(embeddings)} vectors.")
    
    def search_similar(self, query_embedding: np.ndarray, embedding_type: str = "combined",
                      user_id: str = None, k: int = 5, limit: int = None) -> List[Tuple[ConversationEntry, float]]:
        """Search for similar conversations.
        
        Args:
            query_embedding: Query embedding vector.
            embedding_type: Type of embedding to search with.
            user_id: Optional user ID for user-specific search.
            k: Number of similar conversations to return.
            limit: Alias for k parameter (for API compatibility).
            
        Returns:
            List of (ConversationEntry, similarity_score) tuples.
        """
        # Use limit if provided, otherwise use k
        if limit is not None:
            k = limit
        index_key = f"{embedding_type}_{user_id or 'global'}"
        
        if index_key not in self.indices:
            self._load_index(embedding_type, user_id)
        
        if index_key not in self.indices:
            print(f"No index found for {embedding_type} with user_id={user_id}")
            return []
        
        index = self.indices[index_key]
        id_mapping = self.id_mappings[index_key]
        
        # Normalize query embedding
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search
        similarities, indices = index.search(query_embedding, k)
        
        results = []
        for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
            if idx < len(id_mapping):
                entry_id = id_mapping[idx]
                conversation = self.memory.get_conversation(entry_id)
                if conversation:
                    results.append((conversation, float(similarity)))
        
        return results
    
    def search_by_text(self, query_text: str, embedding_generator, 
                      embedding_type: str = "semantic", user_id: str = None,
                      k: int = 5) -> List[Tuple[ConversationEntry, float]]:
        """Search for similar conversations using text query.
        
        Args:
            query_text: Text to search for.
            embedding_generator: EmbeddingGenerator instance.
            embedding_type: Type of embedding to use for search.
            user_id: Optional user ID for user-specific search.
            k: Number of results to return.
            
        Returns:
            List of (ConversationEntry, similarity_score) tuples.
        """
        if embedding_type == "semantic":
            query_embedding = embedding_generator.generate_text_embedding(query_text)
        else:
            # For other types, we need switch stats - return empty for now
            print(f"Text search not supported for {embedding_type} embeddings")
            return []
        
        return self.search_similar(query_embedding, embedding_type, user_id, k)
    
    def search_by_style(self, switch_stats: Dict, embedding_generator,
                       user_id: str = None, k: int = 5) -> List[Tuple[ConversationEntry, float]]:
        """Search for conversations with similar code-switching style.
        
        Args:
            switch_stats: Code-switching statistics.
            embedding_generator: EmbeddingGenerator instance.
            user_id: Optional user ID for user-specific search.
            k: Number of results to return.
            
        Returns:
            List of (ConversationEntry, similarity_score) tuples.
        """
        style_embedding = embedding_generator.generate_style_embedding(switch_stats)
        return self.search_similar(style_embedding, "style", user_id, k)
    
    def hybrid_search(self, query_text: str, switch_stats: Dict, embedding_generator,
                     user_id: str = None, k: int = 5, 
                     weights: Dict[str, float] = None) -> List[Tuple[ConversationEntry, float]]:
        """Perform hybrid search combining semantic and style similarity.
        
        Args:
            query_text: Text query.
            switch_stats: Code-switching statistics.
            embedding_generator: EmbeddingGenerator instance.
            user_id: Optional user ID for user-specific search.
            k: Number of results to return.
            weights: Weights for combining scores.
            
        Returns:
            List of (ConversationEntry, similarity_score) tuples.
        """
        if weights is None:
            weights = {"semantic": 0.7, "style": 0.3}
        
        # Get semantic results
        semantic_results = self.search_by_text(
            query_text, embedding_generator, "semantic", user_id, k*2
        )
        
        # Get style results
        style_results = self.search_by_style(
            switch_stats, embedding_generator, user_id, k*2
        )
        
        # Combine and re-rank results
        combined_scores = {}
        
        for conv, score in semantic_results:
            entry_id = conv.entry_id
            combined_scores[entry_id] = combined_scores.get(entry_id, 0) + weights["semantic"] * score
        
        for conv, score in style_results:
            entry_id = conv.entry_id
            combined_scores[entry_id] = combined_scores.get(entry_id, 0) + weights["style"] * score
        
        # Sort by combined score and get top k
        sorted_entries = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:k]
        
        results = []
        for entry_id, score in sorted_entries:
            conversation = self.memory.get_conversation(entry_id)
            if conversation:
                results.append((conversation, score))
        
        return results
    
    def get_user_style_profile(self, user_id: str, embedding_generator) -> Dict:
        """Generate a style profile for a user based on their conversation history.
        
        Args:
            user_id: User identifier.
            embedding_generator: EmbeddingGenerator instance.
            
        Returns:
            Dictionary containing user's style profile.
        """
        conversations = self.memory.get_user_conversations(user_id)
        if not conversations:
            return {}
        
        # Aggregate statistics
        total_switches = 0
        total_languages = set()
        switch_densities = []
        confidences = []
        
        for conv in conversations:
            stats = conv.switch_stats
            total_switches += stats.get("total_switches", 0)
            total_languages.update(stats.get("languages", []))
            switch_densities.append(stats.get("switch_density", 0))
            confidences.append(stats.get("avg_confidence", 0))
        
        return {
            "total_conversations": len(conversations),
            "total_switches": total_switches,
            "unique_languages": list(total_languages),
            "avg_switch_density": np.mean(switch_densities) if switch_densities else 0,
            "avg_confidence": np.mean(confidences) if confidences else 0,
            "languages_used": len(total_languages)
        }
    
    def find_similar_users(self, user_id: str, embedding_generator, k: int = 5) -> List[Tuple[str, float]]:
        """Find users with similar code-switching patterns.
        
        Args:
            user_id: Target user ID.
            embedding_generator: EmbeddingGenerator instance.
            k: Number of similar users to return.
            
        Returns:
            List of (user_id, similarity_score) tuples.
        """
        # This would require building user-level embeddings
        # For now, return empty list as it's a complex feature
        return []
    
    def _load_index(self, embedding_type: str, user_id: str = None):
        """Load FAISS index from disk.
        
        Args:
            embedding_type: Type of embedding index.
            user_id: Optional user ID.
        """
        index_key = f"{embedding_type}_{user_id or 'global'}"
        index_path = os.path.join(self.index_dir, f"{index_key}.index")
        mapping_path = os.path.join(self.index_dir, f"{index_key}.mapping")
        
        if not os.path.exists(index_path) or not os.path.exists(mapping_path):
            return
        
        try:
            index = faiss.read_index(index_path)
            with open(mapping_path, 'rb') as f:
                id_mapping = pickle.load(f)
            
            self.indices[index_key] = index
            self.id_mappings[index_key] = id_mapping
            
        except Exception as e:
            print(f"Failed to load index {index_key}: {e}")
    
    def update_index(self, conversation: ConversationEntry, embedding_type: str = "combined",
                    user_id: str = None):
        """Add a new conversation to the existing index.
        
        Args:
            conversation: New conversation entry.
            embedding_type: Type of embedding to update.
            user_id: Optional user ID.
        """
        index_key = f"{embedding_type}_{user_id or 'global'}"
        
        if index_key not in self.indices:
            self._load_index(embedding_type, user_id)
        
        if index_key not in self.indices:
            # Build new index if none exists
            self.build_index(user_id, [embedding_type])
            return
        
        if embedding_type not in conversation.embeddings:
            return
        
        embedding = conversation.embeddings[embedding_type].reshape(1, -1).astype('float32')
        faiss.normalize_L2(embedding)
        
        self.indices[index_key].add(embedding)
        self.id_mappings[index_key].append(conversation.entry_id)
        
        # Save updated index
        index_path = os.path.join(self.index_dir, f"{index_key}.index")
        mapping_path = os.path.join(self.index_dir, f"{index_key}.mapping")
        
        faiss.write_index(self.indices[index_key], index_path)
        with open(mapping_path, 'wb') as f:
            pickle.dump(self.id_mappings[index_key], f)