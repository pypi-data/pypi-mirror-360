"""Embedding generation for text and code-switching patterns."""

import numpy as np
from typing import List, Dict, Optional, Union
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize
import json


class EmbeddingGenerator:
    """Generates embeddings for text with code-switching awareness."""
    
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """Initialize the embedding generator.
        
        Args:
            model_name: Name of the sentence transformer model to use.
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
        
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            self.model = SentenceTransformer(self.model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to load model {self.model_name}: {e}")
    
    def generate_text_embedding(self, text: str) -> np.ndarray:
        """Generate semantic embedding for text.
        
        Args:
            text: Input text.
            
        Returns:
            Normalized embedding vector.
        """
        if not text or not isinstance(text, str):
            return np.zeros(self.model.get_sentence_embedding_dimension())
        
        embedding = self.model.encode([text])[0]
        return normalize([embedding])[0]
    
    def generate_batch_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of input texts.
            
        Returns:
            Array of normalized embeddings.
        """
        if not texts:
            return np.array([])
        
        embeddings = self.model.encode(texts)
        return normalize(embeddings)
    
    def generate_style_embedding(self, switch_stats: Dict) -> np.ndarray:
        """Generate embedding representing code-switching style.
        
        Args:
            switch_stats: Statistics from SwitchPointDetector.
            
        Returns:
            Style embedding vector.
        """
        features = self._extract_style_features(switch_stats)
        return np.array(features, dtype=np.float32)
    
    def generate_combined_embedding(self, text: str, switch_stats: Dict, 
                                  weights: Dict[str, float] = None) -> np.ndarray:
        """Generate combined semantic and style embedding.
        
        Args:
            text: Input text.
            switch_stats: Code-switching statistics.
            weights: Weights for combining embeddings.
            
        Returns:
            Combined embedding vector.
        """
        if weights is None:
            weights = {"semantic": 0.7, "style": 0.3}
        
        semantic_emb = self.generate_text_embedding(text)
        style_emb = self.generate_style_embedding(switch_stats)
        
        semantic_weight = weights.get("semantic", 0.7)
        style_weight = weights.get("style", 0.3)
        
        style_emb_padded = self._pad_or_truncate(style_emb, len(semantic_emb))
        
        combined = (semantic_weight * semantic_emb + 
                   style_weight * style_emb_padded)
        
        return normalize([combined])[0]
    
    def generate_embeddings(self, text: str, switch_stats: Dict = None) -> Dict[str, np.ndarray]:
        """Generate embeddings for text (compatibility method).
        
        Args:
            text: Input text.
            switch_stats: Code-switching statistics (optional).
            
        Returns:
            Dict with different types of embeddings.
        """
        embeddings = {
            "semantic": self.generate_text_embedding(text)
        }
        
        if switch_stats:
            embeddings["style"] = self.generate_style_embedding(switch_stats)
            embeddings["combined"] = self.generate_combined_embedding(text, switch_stats)
        
        return embeddings
    
    def generate_conversation_embedding(self, conversation_data: Dict) -> Dict[str, np.ndarray]:
        """Generate embeddings for a complete conversation entry.
        
        Args:
            conversation_data: Dict with 'text', 'switch_stats', 'metadata'.
            
        Returns:
            Dict with different types of embeddings.
        """
        text = conversation_data.get("text", "")
        switch_stats = conversation_data.get("switch_stats", {})
        metadata = conversation_data.get("metadata", {})
        
        embeddings = {
            "semantic": self.generate_text_embedding(text),
            "style": self.generate_style_embedding(switch_stats),
            "combined": self.generate_combined_embedding(text, switch_stats),
            "metadata": self._generate_metadata_embedding(metadata)
        }
        
        return embeddings
    
    def compute_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Compute cosine similarity between two embeddings.
        
        Args:
            emb1: First embedding.
            emb2: Second embedding.
            
        Returns:
            Cosine similarity score.
        """
        if len(emb1) != len(emb2):
            min_len = min(len(emb1), len(emb2))
            emb1 = emb1[:min_len]
            emb2 = emb2[:min_len]
        
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    
    def _extract_style_features(self, switch_stats: Dict) -> List[float]:
        """Extract numerical features from code-switching statistics.
        
        Args:
            switch_stats: Code-switching statistics.
            
        Returns:
            List of numerical features.
        """
        features = [
            switch_stats.get("total_switches", 0),
            switch_stats.get("unique_languages", 0),
            switch_stats.get("switch_density", 0.0),
            switch_stats.get("avg_confidence", 0.0),
        ]
        
        languages = switch_stats.get("languages", [])
        max_languages = 10  # Limit to prevent feature explosion
        
        for i in range(max_languages):
            if i < len(languages):
                features.append(1.0)  # Language present
            else:
                features.append(0.0)  # Language absent
        
        return features
    
    def _generate_metadata_embedding(self, metadata: Dict) -> np.ndarray:
        """Generate embedding from conversation metadata.
        
        Args:
            metadata: Metadata dictionary.
            
        Returns:
            Metadata embedding vector.
        """
        features = [
            metadata.get("timestamp", 0) / 1e10,  # Normalized timestamp
            metadata.get("session_length", 0) / 100,  # Normalized session length
            float(metadata.get("user_id", 0)) / 1000,  # Normalized user ID
        ]
        
        return np.array(features, dtype=np.float32)
    
    def _pad_or_truncate(self, vector: np.ndarray, target_length: int) -> np.ndarray:
        """Pad or truncate vector to target length.
        
        Args:
            vector: Input vector.
            target_length: Desired length.
            
        Returns:
            Resized vector.
        """
        if len(vector) == target_length:
            return vector
        elif len(vector) < target_length:
            padding = np.zeros(target_length - len(vector))
            return np.concatenate([vector, padding])
        else:
            return vector[:target_length]
    
    def save_model_info(self, filepath: str):
        """Save model information for reproducibility.
        
        Args:
            filepath: Path to save model info.
        """
        info = {
            "model_name": self.model_name,
            "embedding_dimension": self.model.get_sentence_embedding_dimension(),
            "max_seq_length": getattr(self.model.get_max_seq_length(), 'max_seq_length', 512)
        }
        
        with open(filepath, 'w') as f:
            json.dump(info, f, indent=2)