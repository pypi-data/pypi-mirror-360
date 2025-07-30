#!/usr/bin/env python3
"""Optimized FAISS-based similarity retrieval with GPU support and advanced indices."""

import faiss
import numpy as np
import pickle
import os
import json
import time
from typing import List, Dict, Tuple, Optional, Union, Any
from dataclasses import dataclass

from ..memory.conversation_memory import ConversationMemory, ConversationEntry


@dataclass
class SearchResult:
    """Enhanced search result with additional metadata."""
    conversation: ConversationEntry
    similarity_score: float
    embedding_type: str
    search_time: float
    index_stats: Dict[str, Any]


class OptimizedSimilarityRetriever:
    """Advanced FAISS-based retrieval with GPU support and optimized indices."""
    
    def __init__(self, 
                 memory: ConversationMemory, 
                 index_dir: str = "faiss_indices",
                 use_gpu: bool = None,
                 index_type: str = "auto",
                 quantization: bool = True):
        """Initialize the optimized similarity retriever.
        
        Args:
            memory: ConversationMemory instance
            index_dir: Directory to store FAISS indices
            use_gpu: Whether to use GPU acceleration (auto-detect if None)
            index_type: Type of index ('flat', 'ivf', 'hnsw', 'auto')
            quantization: Whether to use product quantization for memory efficiency
        """
        self.memory = memory
        self.index_dir = index_dir
        self.quantization = quantization
        self.index_type = index_type
        
        # GPU setup
        self.use_gpu = self._setup_gpu(use_gpu)
        self.gpu_resource = None
        if self.use_gpu:
            self.gpu_resource = faiss.StandardGpuResources()
        
        # Index management
        self.indices = {}  # Dict of embedding_type -> faiss.Index
        self.id_mappings = {}  # Dict of embedding_type -> List[entry_id]
        self.index_metadata = {}  # Dict storing index configuration and stats
        
        # Performance tracking
        self.search_stats = {
            'total_searches': 0,
            'total_search_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # Simple cache for frequent queries
        self.query_cache = {}
        self.cache_max_size = 1000
        
        self._ensure_directories()
    
    def _setup_gpu(self, use_gpu: Optional[bool]) -> bool:
        """Setup GPU resources if available."""
        if use_gpu is False:
            return False
        
        try:
            if use_gpu is None:
                # Auto-detect GPU
                ngpus = faiss.get_num_gpus()
                if ngpus > 0:
                    print(f"✓ Detected {ngpus} GPU(s), enabling GPU acceleration")
                    return True
                else:
                    print("○ No GPU detected, using CPU")
                    return False
            else:
                # Force GPU usage
                ngpus = faiss.get_num_gpus()
                if ngpus > 0:
                    print(f"✓ Using GPU acceleration ({ngpus} GPU(s))")
                    return True
                else:
                    print("⚠ GPU requested but not available, falling back to CPU")
                    return False
                    
        except Exception as e:
            print(f"⚠ GPU setup failed: {e}, using CPU")
            return False
    
    def _ensure_directories(self):
        """Create necessary directories."""
        os.makedirs(self.index_dir, exist_ok=True)
        os.makedirs(os.path.join(self.index_dir, "metadata"), exist_ok=True)
    
    def _choose_index_type(self, n_vectors: int, dimension: int) -> str:
        """Choose optimal index type based on data characteristics."""
        if self.index_type != "auto":
            return self.index_type
        
        # Auto-selection based on size and performance characteristics
        if n_vectors < 1000:
            return "flat"  # Exact search for small datasets
        elif n_vectors < 50000:
            return "ivf"   # IVF for medium datasets
        else:
            return "hnsw"  # HNSW for large datasets
    
    def _create_index(self, dimension: int, n_vectors: int, index_type: str = None) -> faiss.Index:
        """Create optimized FAISS index based on configuration."""
        if index_type is None:
            index_type = self._choose_index_type(n_vectors, dimension)
        
        print(f"Creating {index_type} index for {n_vectors} vectors of dimension {dimension}")
        
        if index_type == "flat":
            # Exact search using inner product (for cosine similarity)
            index = faiss.IndexFlatIP(dimension)
        
        elif index_type == "ivf":
            # IVF (Inverted File) with optimized parameters
            n_centroids = min(max(int(np.sqrt(n_vectors)), 16), 65536)
            quantizer = faiss.IndexFlatIP(dimension)
            
            if self.quantization and dimension >= 64:
                # Use PQ for memory efficiency
                m = min(dimension // 4, 64)  # Number of sub-quantizers
                index = faiss.IndexIVFPQ(quantizer, dimension, n_centroids, m, 8)
            else:
                index = faiss.IndexIVFFlat(quantizer, dimension, n_centroids)
            
            # Set search parameters
            index.nprobe = min(max(n_centroids // 10, 1), 128)
        
        elif index_type == "hnsw":
            # HNSW (Hierarchical Navigable Small World)
            m = 32  # Number of connections per node
            index = faiss.IndexHNSWFlat(dimension, m)
            index.hnsw.efConstruction = 200
            index.hnsw.efSearch = 128
        
        else:
            # Default to flat index
            index = faiss.IndexFlatIP(dimension)
        
        # Move to GPU if available
        if self.use_gpu and self.gpu_resource:
            try:
                if index_type == "hnsw":
                    # HNSW doesn't support GPU, keep on CPU
                    print("○ HNSW index running on CPU (GPU not supported)")
                else:
                    index = faiss.index_cpu_to_gpu(self.gpu_resource, 0, index)
                    print("✓ Index moved to GPU")
            except Exception as e:
                print(f"⚠ Failed to move index to GPU: {e}")
        
        return index
    
    def build_index(self, 
                   user_id: str = None, 
                   embedding_types: List[str] = None,
                   force_rebuild: bool = False):
        """Build optimized FAISS indices for similarity search.
        
        Args:
            user_id: Optional user ID to filter conversations
            embedding_types: List of embedding types to index
            force_rebuild: Whether to force rebuilding existing indices
        """
        if embedding_types is None:
            embedding_types = ["semantic", "style", "combined"]
        
        conversations = self.memory.get_user_conversations(user_id) if user_id else []
        if not conversations:
            print("No conversations found to index.")
            return
        
        for emb_type in embedding_types:
            index_key = f"{emb_type}_{user_id or 'global'}"
            index_path = os.path.join(self.index_dir, f"{index_key}.index")
            metadata_path = os.path.join(self.index_dir, "metadata", f"{index_key}.json")
            
            if os.path.exists(index_path) and not force_rebuild:
                self._load_index(emb_type, user_id)
                continue
            
            # Collect embeddings
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
            n_vectors, dimension = embeddings_array.shape
            
            # Create optimized index
            chosen_index_type = self._choose_index_type(n_vectors, dimension)
            index = self._create_index(dimension, n_vectors, chosen_index_type)
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings_array)
            
            # Train index if needed (for IVF indices)
            if hasattr(index, 'is_trained') and not index.is_trained:
                print(f"Training {chosen_index_type} index...")
                start_time = time.time()
                
                # Use subset for training if dataset is large
                training_size = min(n_vectors, 100000)
                training_data = embeddings_array[:training_size]
                
                index.train(training_data)
                print(f"Training completed in {time.time() - start_time:.2f}s")
            
            # Add vectors to index
            print(f"Adding {n_vectors} vectors to index...")
            start_time = time.time()
            index.add(embeddings_array)
            add_time = time.time() - start_time
            print(f"Vectors added in {add_time:.2f}s")
            
            # Store index and mappings
            self.indices[index_key] = index
            self.id_mappings[index_key] = entry_ids
            
            # Store metadata
            metadata = {
                'index_type': chosen_index_type,
                'dimension': dimension,
                'n_vectors': n_vectors,
                'quantization': self.quantization,
                'gpu_enabled': self.use_gpu,
                'build_time': add_time,
                'timestamp': time.time()
            }
            self.index_metadata[index_key] = metadata
            
            # Save to disk
            self._save_index(index_key, metadata_path)
            
            print(f"✓ Built optimized {chosen_index_type} index with {n_vectors} vectors")
    
    def search_similar(self, 
                      query_embedding: np.ndarray, 
                      embedding_type: str = "combined",
                      user_id: str = None, 
                      k: int = 5,
                      search_params: Dict = None) -> List[SearchResult]:
        """Search for similar conversations with enhanced performance tracking.
        
        Args:
            query_embedding: Query embedding vector
            embedding_type: Type of embedding to search with
            user_id: Optional user ID for user-specific search
            k: Number of similar conversations to return
            search_params: Optional search parameters for tuning
            
        Returns:
            List of SearchResult objects
        """
        start_time = time.time()
        index_key = f"{embedding_type}_{user_id or 'global'}"
        
        # Check cache first
        cache_key = self._get_cache_key(query_embedding, embedding_type, user_id, k)
        if cache_key in self.query_cache:
            self.search_stats['cache_hits'] += 1
            return self.query_cache[cache_key]
        
        self.search_stats['cache_misses'] += 1
        
        # Load index if needed
        if index_key not in self.indices:
            self._load_index(embedding_type, user_id)
        
        if index_key not in self.indices:
            print(f"No index found for {embedding_type} with user_id={user_id}")
            return []
        
        index = self.indices[index_key]
        id_mapping = self.id_mappings[index_key]
        
        # Apply search parameters
        if search_params and hasattr(index, 'nprobe'):
            index.nprobe = search_params.get('nprobe', index.nprobe)
        
        # Normalize query embedding
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Perform search
        search_start = time.time()
        similarities, indices = index.search(query_embedding, k)
        search_time = time.time() - search_start
        
        # Build results
        results = []
        for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
            if idx < len(id_mapping) and idx >= 0:
                entry_id = id_mapping[idx]
                conversation = self.memory.get_conversation(entry_id)
                if conversation:
                    result = SearchResult(
                        conversation=conversation,
                        similarity_score=float(similarity),
                        embedding_type=embedding_type,
                        search_time=search_time,
                        index_stats=self.index_metadata.get(index_key, {})
                    )
                    results.append(result)
        
        total_time = time.time() - start_time
        
        # Update stats
        self.search_stats['total_searches'] += 1
        self.search_stats['total_search_time'] += total_time
        
        # Cache results
        if len(self.query_cache) < self.cache_max_size:
            self.query_cache[cache_key] = results
        
        return results
    
    def hybrid_search_optimized(self, 
                               query_text: str, 
                               switch_stats: Dict, 
                               embedding_generator,
                               user_id: str = None, 
                               k: int = 5,
                               weights: Dict[str, float] = None) -> List[SearchResult]:
        """Optimized hybrid search with parallel execution."""
        if weights is None:
            weights = {"semantic": 0.7, "style": 0.3}
        
        # Generate embeddings in parallel (if we had threading)
        semantic_embedding = embedding_generator.generate_text_embedding(query_text)
        style_embedding = embedding_generator.generate_style_embedding(switch_stats)
        
        # Perform searches
        semantic_results = self.search_similar(
            semantic_embedding, "semantic", user_id, k*2
        )
        style_results = self.search_similar(
            style_embedding, "style", user_id, k*2
        )
        
        # Combine results with weighted scoring
        combined_scores = {}
        
        for result in semantic_results:
            entry_id = result.conversation.entry_id
            weighted_score = weights["semantic"] * result.similarity_score
            combined_scores[entry_id] = combined_scores.get(entry_id, 0) + weighted_score
        
        for result in style_results:
            entry_id = result.conversation.entry_id
            weighted_score = weights["style"] * result.similarity_score
            combined_scores[entry_id] = combined_scores.get(entry_id, 0) + weighted_score
        
        # Sort and return top k
        sorted_entries = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:k]
        
        final_results = []
        for entry_id, score in sorted_entries:
            conversation = self.memory.get_conversation(entry_id)
            if conversation:
                result = SearchResult(
                    conversation=conversation,
                    similarity_score=score,
                    embedding_type="hybrid",
                    search_time=0.0,  # Combined time not tracked
                    index_stats={}
                )
                final_results.append(result)
        
        return final_results
    
    def get_index_statistics(self) -> Dict[str, Any]:
        """Get comprehensive index statistics."""
        stats = {
            'total_indices': len(self.indices),
            'search_performance': self.search_stats.copy(),
            'indices': {}
        }
        
        for index_key, metadata in self.index_metadata.items():
            index = self.indices.get(index_key)
            index_stats = metadata.copy()
            
            if index:
                index_stats['current_size'] = index.ntotal
                index_stats['memory_usage_mb'] = self._estimate_index_memory(index)
            
            stats['indices'][index_key] = index_stats
        
        return stats
    
    def optimize_search_parameters(self, 
                                  query_embeddings: List[np.ndarray],
                                  embedding_type: str = "semantic",
                                  user_id: str = None) -> Dict[str, Any]:
        """Optimize search parameters based on query patterns."""
        index_key = f"{embedding_type}_{user_id or 'global'}"
        
        if index_key not in self.indices:
            return {}
        
        index = self.indices[index_key]
        
        # Only optimize for IVF indices
        if not hasattr(index, 'nprobe'):
            return {}
        
        # Test different nprobe values
        nprobe_values = [1, 4, 8, 16, 32, 64, 128]
        results = {}
        
        for nprobe in nprobe_values:
            index.nprobe = nprobe
            
            total_time = 0
            for query_emb in query_embeddings[:10]:  # Test on subset
                start_time = time.time()
                index.search(query_emb.reshape(1, -1), 10)
                total_time += time.time() - start_time
            
            avg_time = total_time / min(len(query_embeddings), 10)
            results[nprobe] = avg_time
        
        # Find optimal nprobe (balance between speed and accuracy)
        optimal_nprobe = min(results.keys(), key=lambda k: results[k])
        index.nprobe = optimal_nprobe
        
        return {
            'optimal_nprobe': optimal_nprobe,
            'performance_profile': results
        }
    
    def _save_index(self, index_key: str, metadata_path: str):
        """Save index and metadata to disk."""
        index_path = os.path.join(self.index_dir, f"{index_key}.index")
        mapping_path = os.path.join(self.index_dir, f"{index_key}.mapping")
        
        # Save index
        if self.use_gpu and index_key in self.indices:
            # Move to CPU before saving
            try:
                cpu_index = faiss.index_gpu_to_cpu(self.indices[index_key])
                faiss.write_index(cpu_index, index_path)
            except:
                faiss.write_index(self.indices[index_key], index_path)
        else:
            faiss.write_index(self.indices[index_key], index_path)
        
        # Save mapping
        with open(mapping_path, 'wb') as f:
            pickle.dump(self.id_mappings[index_key], f)
        
        # Save metadata
        with open(metadata_path, 'w') as f:
            json.dump(self.index_metadata[index_key], f, indent=2)
    
    def _load_index(self, embedding_type: str, user_id: str = None):
        """Load optimized index from disk."""
        index_key = f"{embedding_type}_{user_id or 'global'}"
        index_path = os.path.join(self.index_dir, f"{index_key}.index")
        mapping_path = os.path.join(self.index_dir, f"{index_key}.mapping")
        metadata_path = os.path.join(self.index_dir, "metadata", f"{index_key}.json")
        
        if not all(os.path.exists(p) for p in [index_path, mapping_path]):
            return
        
        try:
            # Load index
            index = faiss.read_index(index_path)
            
            # Move to GPU if available
            if self.use_gpu and self.gpu_resource:
                try:
                    index = faiss.index_cpu_to_gpu(self.gpu_resource, 0, index)
                except:
                    pass  # Keep on CPU if GPU transfer fails
            
            # Load mapping
            with open(mapping_path, 'rb') as f:
                id_mapping = pickle.load(f)
            
            # Load metadata
            metadata = {}
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
            
            self.indices[index_key] = index
            self.id_mappings[index_key] = id_mapping
            self.index_metadata[index_key] = metadata
            
            print(f"✓ Loaded optimized index: {index_key}")
            
        except Exception as e:
            print(f"Failed to load optimized index {index_key}: {e}")
    
    def _get_cache_key(self, embedding: np.ndarray, embedding_type: str, 
                      user_id: str, k: int) -> str:
        """Generate cache key for query."""
        emb_hash = hash(embedding.tobytes())
        return f"{emb_hash}_{embedding_type}_{user_id}_{k}"
    
    def _estimate_index_memory(self, index) -> float:
        """Estimate memory usage of index in MB."""
        try:
            if hasattr(index, 'ntotal') and hasattr(index, 'd'):
                # Rough estimation: ntotal * dimension * bytes_per_float
                return (index.ntotal * index.d * 4) / (1024 * 1024)
            return 0.0
        except:
            return 0.0