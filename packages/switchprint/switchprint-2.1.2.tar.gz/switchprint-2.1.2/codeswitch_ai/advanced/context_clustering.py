#!/usr/bin/env python3
"""Advanced context-aware clustering using mBERT and Next Sentence Prediction."""

import numpy as np
import torch
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
import json
from pathlib import Path
from collections import defaultdict
from sklearn.cluster import DBSCAN, KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

try:
    from transformers import (
        AutoTokenizer, AutoModel, AutoModelForNextSentencePrediction,
        BertTokenizer, BertForNextSentencePrediction
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠ Transformers not available. Install with: pip install transformers")

import umap
from sentence_transformers import SentenceTransformer


@dataclass
class ClusteringResult:
    """Result of context-aware clustering."""
    cluster_labels: List[int]
    cluster_centers: Optional[List[List[float]]]
    silhouette_score: float
    calinski_harabasz_score: float
    num_clusters: int
    num_noise_points: int
    coherence_scores: Dict[int, float]
    context_transitions: List[Tuple[int, int, float]]  # (from_cluster, to_cluster, nsp_score)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def summary(self) -> str:
        """Generate summary report."""
        return f"""
Context-Aware Clustering Results:
================================
Number of Clusters: {self.num_clusters}
Noise Points: {self.num_noise_points}
Silhouette Score: {self.silhouette_score:.4f}
Calinski-Harabasz: {self.calinski_harabasz_score:.4f}

Cluster Coherence:
{self._format_coherence_scores()}

Context Transitions:
{self._format_transitions()}
"""
    
    def _format_coherence_scores(self) -> str:
        """Format coherence scores."""
        lines = []
        for cluster_id, score in sorted(self.coherence_scores.items()):
            lines.append(f"Cluster {cluster_id:2d}: {score:.4f}")
        return "\n".join(lines)
    
    def _format_transitions(self) -> str:
        """Format context transitions."""
        lines = []
        sorted_transitions = sorted(self.context_transitions, key=lambda x: x[2], reverse=True)
        for from_cluster, to_cluster, nsp_score in sorted_transitions[:10]:  # Top 10
            lines.append(f"{from_cluster:2d} → {to_cluster:2d}: NSP={nsp_score:.3f}")
        return "\n".join(lines)


class ContextAwareClusterer:
    """Advanced clustering with mBERT Next Sentence Prediction."""
    
    def __init__(self, model_name: str = "bert-base-multilingual-cased", 
                 embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """Initialize context-aware clusterer.
        
        Args:
            model_name: mBERT model for NSP
            embedding_model: Sentence transformer for embeddings
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("Transformers required for context clustering")
        
        self.model_name = model_name
        self.embedding_model_name = embedding_model
        
        # Initialize models
        print(f"📥 Loading {model_name} for NSP...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.nsp_model = AutoModelForNextSentencePrediction.from_pretrained(model_name)
        
        print(f"📥 Loading {embedding_model} for embeddings...")
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # GPU support
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.nsp_model.to(self.device)
        
        print(f"✓ Models loaded on {self.device}")
        
        # Clustering parameters
        self.clustering_methods = {
            'dbscan': self._cluster_dbscan,
            'kmeans': self._cluster_kmeans,
            'hierarchical': self._cluster_hierarchical
        }
    
    def compute_sentence_embeddings(self, texts: List[str]) -> np.ndarray:
        """Compute sentence embeddings.
        
        Args:
            texts: List of input texts
            
        Returns:
            Embedding matrix
        """
        print(f"🔤 Computing embeddings for {len(texts)} texts...")
        
        # Use sentence transformer for multilingual embeddings
        embeddings = self.embedding_model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        return embeddings
    
    def compute_nsp_scores(self, texts: List[str], window_size: int = 3) -> np.ndarray:
        """Compute Next Sentence Prediction scores for context coherence.
        
        Args:
            texts: List of input texts
            window_size: Window size for NSP computation
            
        Returns:
            NSP coherence matrix
        """
        print(f"🧠 Computing NSP scores with window size {window_size}...")
        
        n_texts = len(texts)
        nsp_matrix = np.zeros((n_texts, n_texts))
        
        # Compute NSP scores for text pairs within window
        for i in range(n_texts):
            for j in range(max(0, i - window_size), min(n_texts, i + window_size + 1)):
                if i != j:
                    nsp_score = self._compute_nsp_pair(texts[i], texts[j])
                    nsp_matrix[i, j] = nsp_score
        
        return nsp_matrix
    
    def _compute_nsp_pair(self, text1: str, text2: str) -> float:
        """Compute NSP score for a pair of texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            NSP coherence score
        """
        try:
            # Tokenize the pair
            inputs = self.tokenizer(
                text1, text2,
                return_tensors='pt',
                truncation=True,
                padding=True,
                max_length=512
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get NSP prediction
            with torch.no_grad():
                outputs = self.nsp_model(**inputs)
                logits = outputs.logits
                
                # Convert to probability (higher = more coherent)
                probabilities = torch.softmax(logits, dim=-1)
                is_next_prob = probabilities[0, 0].cpu().item()  # "IsNext" probability
                
                return is_next_prob
                
        except Exception as e:
            print(f"⚠ NSP computation failed: {e}")
            return 0.5  # Neutral score
    
    def _cluster_dbscan(self, embeddings: np.ndarray, **kwargs) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Perform DBSCAN clustering.
        
        Args:
            embeddings: Input embeddings
            **kwargs: DBSCAN parameters
            
        Returns:
            Cluster labels and centers (None for DBSCAN)
        """
        eps = kwargs.get('eps', 0.3)
        min_samples = kwargs.get('min_samples', 3)
        
        clusterer = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
        labels = clusterer.fit_predict(embeddings)
        
        return labels, None
    
    def _cluster_kmeans(self, embeddings: np.ndarray, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """Perform K-means clustering.
        
        Args:
            embeddings: Input embeddings
            **kwargs: K-means parameters
            
        Returns:
            Cluster labels and centers
        """
        n_clusters = kwargs.get('n_clusters', 8)
        random_state = kwargs.get('random_state', 42)
        
        clusterer = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        labels = clusterer.fit_predict(embeddings)
        centers = clusterer.cluster_centers_
        
        return labels, centers
    
    def _cluster_hierarchical(self, embeddings: np.ndarray, **kwargs) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Perform hierarchical clustering.
        
        Args:
            embeddings: Input embeddings
            **kwargs: Hierarchical clustering parameters
            
        Returns:
            Cluster labels and centers (computed as centroids)
        """
        n_clusters = kwargs.get('n_clusters', 8)
        linkage = kwargs.get('linkage', 'ward')
        
        clusterer = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage)
        labels = clusterer.fit_predict(embeddings)
        
        # Compute cluster centers as centroids
        unique_labels = np.unique(labels)
        centers = []
        for label in unique_labels:
            if label != -1:  # Ignore noise points
                mask = labels == label
                center = embeddings[mask].mean(axis=0)
                centers.append(center)
        
        return labels, np.array(centers) if centers else None
    
    def compute_cluster_coherence(self, texts: List[str], labels: np.ndarray, 
                                nsp_matrix: np.ndarray) -> Dict[int, float]:
        """Compute cluster coherence using NSP scores.
        
        Args:
            texts: Input texts
            labels: Cluster labels
            nsp_matrix: NSP coherence matrix
            
        Returns:
            Coherence scores per cluster
        """
        coherence_scores = {}
        unique_labels = np.unique(labels)
        
        for label in unique_labels:
            if label == -1:  # Skip noise points
                continue
            
            # Get indices of texts in this cluster
            cluster_indices = np.where(labels == label)[0]
            
            if len(cluster_indices) < 2:
                coherence_scores[label] = 0.0
                continue
            
            # Compute average NSP score within cluster
            cluster_nsp_scores = []
            for i in range(len(cluster_indices)):
                for j in range(i + 1, len(cluster_indices)):
                    idx1, idx2 = cluster_indices[i], cluster_indices[j]
                    nsp_score = max(nsp_matrix[idx1, idx2], nsp_matrix[idx2, idx1])
                    cluster_nsp_scores.append(nsp_score)
            
            coherence_scores[label] = np.mean(cluster_nsp_scores) if cluster_nsp_scores else 0.0
        
        return coherence_scores
    
    def find_context_transitions(self, texts: List[str], labels: np.ndarray, 
                               nsp_matrix: np.ndarray) -> List[Tuple[int, int, float]]:
        """Find strong context transitions between clusters.
        
        Args:
            texts: Input texts
            labels: Cluster labels
            nsp_matrix: NSP coherence matrix
            
        Returns:
            List of (from_cluster, to_cluster, nsp_score) transitions
        """
        transitions = []
        unique_labels = np.unique(labels)
        
        for label1 in unique_labels:
            if label1 == -1:
                continue
            
            for label2 in unique_labels:
                if label1 >= label2 or label2 == -1:
                    continue
                
                # Get indices for both clusters
                indices1 = np.where(labels == label1)[0]
                indices2 = np.where(labels == label2)[0]
                
                # Find strongest transition
                max_nsp = 0.0
                for idx1 in indices1:
                    for idx2 in indices2:
                        nsp_score = max(nsp_matrix[idx1, idx2], nsp_matrix[idx2, idx1])
                        max_nsp = max(max_nsp, nsp_score)
                
                if max_nsp > 0.6:  # Threshold for strong transitions
                    transitions.append((label1, label2, max_nsp))
        
        return sorted(transitions, key=lambda x: x[2], reverse=True)
    
    def cluster_with_context(self, texts: List[str], method: str = 'dbscan', 
                           nsp_window: int = 3, **clustering_kwargs) -> ClusteringResult:
        """Perform context-aware clustering.
        
        Args:
            texts: Input texts
            method: Clustering method ('dbscan', 'kmeans', 'hierarchical')
            nsp_window: Window size for NSP computation
            **clustering_kwargs: Method-specific parameters
            
        Returns:
            Clustering results with context analysis
        """
        print(f"🎯 Starting context-aware clustering with {method}")
        print(f"📊 Processing {len(texts)} texts...")
        
        # Compute embeddings
        embeddings = self.compute_sentence_embeddings(texts)
        
        # Compute NSP scores for context coherence
        nsp_matrix = self.compute_nsp_scores(texts, nsp_window)
        
        # Enhance embeddings with NSP information
        enhanced_embeddings = self._enhance_embeddings_with_nsp(embeddings, nsp_matrix)
        
        # Perform clustering
        if method not in self.clustering_methods:
            raise ValueError(f"Unknown clustering method: {method}")
        
        print(f"🔍 Performing {method} clustering...")
        labels, centers = self.clustering_methods[method](enhanced_embeddings, **clustering_kwargs)
        
        # Compute clustering metrics
        unique_labels = np.unique(labels)
        num_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
        num_noise = np.sum(labels == -1)
        
        # Compute silhouette score (skip if only one cluster or all noise)
        if num_clusters > 1 and len(texts) - num_noise > 1:
            # Filter out noise points for silhouette computation
            valid_mask = labels != -1
            if np.sum(valid_mask) > 1:
                sil_score = silhouette_score(embeddings[valid_mask], labels[valid_mask])
                ch_score = calinski_harabasz_score(embeddings[valid_mask], labels[valid_mask])
            else:
                sil_score = 0.0
                ch_score = 0.0
        else:
            sil_score = 0.0
            ch_score = 0.0
        
        # Compute cluster coherence using NSP
        coherence_scores = self.compute_cluster_coherence(texts, labels, nsp_matrix)
        
        # Find context transitions
        transitions = self.find_context_transitions(texts, labels, nsp_matrix)
        
        result = ClusteringResult(
            cluster_labels=labels.tolist(),
            cluster_centers=centers.tolist() if centers is not None else None,
            silhouette_score=sil_score,
            calinski_harabasz_score=ch_score,
            num_clusters=num_clusters,
            num_noise_points=num_noise,
            coherence_scores=coherence_scores,
            context_transitions=transitions
        )
        
        print(f"✓ Clustering completed: {num_clusters} clusters, {num_noise} noise points")
        print(f"📈 Silhouette score: {sil_score:.4f}")
        
        return result
    
    def _enhance_embeddings_with_nsp(self, embeddings: np.ndarray, 
                                   nsp_matrix: np.ndarray, alpha: float = 0.1) -> np.ndarray:
        """Enhance embeddings with NSP context information.
        
        Args:
            embeddings: Base embeddings
            nsp_matrix: NSP coherence matrix
            alpha: Mixing parameter for NSP enhancement
            
        Returns:
            Enhanced embeddings
        """
        # Compute context vectors from NSP scores
        context_vectors = []
        
        for i in range(len(embeddings)):
            # Weight embeddings by NSP scores
            nsp_weights = nsp_matrix[i]
            nsp_weights = nsp_weights / (np.sum(nsp_weights) + 1e-8)  # Normalize
            
            # Compute context-weighted embedding
            context_vector = np.sum(embeddings * nsp_weights[:, np.newaxis], axis=0)
            context_vectors.append(context_vector)
        
        context_vectors = np.array(context_vectors)
        
        # Mix original embeddings with context vectors
        enhanced_embeddings = (1 - alpha) * embeddings + alpha * context_vectors
        
        # Normalize
        norms = np.linalg.norm(enhanced_embeddings, axis=1, keepdims=True)
        enhanced_embeddings = enhanced_embeddings / (norms + 1e-8)
        
        return enhanced_embeddings
    
    def visualize_clusters(self, embeddings: np.ndarray, labels: np.ndarray, 
                         method: str = 'umap', save_path: Optional[str] = None) -> None:
        """Visualize clusters in 2D.
        
        Args:
            embeddings: Input embeddings
            labels: Cluster labels
            method: Dimensionality reduction method ('umap', 'tsne', 'pca')
            save_path: Optional path to save plot
        """
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            print(f"📊 Creating {method.upper()} visualization...")
            
            # Reduce dimensionality
            if method == 'umap':
                reducer = umap.UMAP(n_components=2, random_state=42)
            elif method == 'tsne':
                reducer = TSNE(n_components=2, random_state=42, perplexity=min(30, len(embeddings)-1))
            elif method == 'pca':
                reducer = PCA(n_components=2, random_state=42)
            else:
                raise ValueError(f"Unknown visualization method: {method}")
            
            # Filter out noise points for visualization
            valid_mask = labels != -1
            if np.sum(valid_mask) < 2:
                print("⚠ Not enough valid points for visualization")
                return
            
            embeddings_2d = reducer.fit_transform(embeddings[valid_mask])
            valid_labels = labels[valid_mask]
            
            # Create plot
            plt.figure(figsize=(12, 8))
            
            # Plot clusters
            unique_labels = np.unique(valid_labels)
            colors = plt.cm.tab10(np.linspace(0, 1, len(unique_labels)))
            
            for label, color in zip(unique_labels, colors):
                mask = valid_labels == label
                plt.scatter(embeddings_2d[mask, 0], embeddings_2d[mask, 1], 
                          c=[color], label=f'Cluster {label}', alpha=0.7, s=50)
            
            # Plot noise points if any
            if np.sum(labels == -1) > 0:
                noise_embeddings = reducer.transform(embeddings[labels == -1])
                plt.scatter(noise_embeddings[:, 0], noise_embeddings[:, 1], 
                          c='black', label='Noise', alpha=0.5, s=30, marker='x')
            
            plt.xlabel(f'{method.upper()} Component 1')
            plt.ylabel(f'{method.upper()} Component 2')
            plt.title('Context-Aware Clustering Visualization')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"✓ Visualization saved to {save_path}")
            else:
                plt.show()
                
        except Exception as e:
            print(f"⚠ Visualization failed: {e}")


def main():
    """Example usage of context-aware clustering."""
    # Sample code-switching texts
    texts = [
        "Hello, how are you today?",
        "Hola, ¿cómo estás hoy?", 
        "I'm doing well, gracias.",
        "That's good to hear, me alegro.",
        "What are your plans for mañana?",
        "I have a meeting at trabajo.",
        "Good luck with your reunión.",
        "Thank you, hasta luego!",
        "See you later, adiós!",
        "Have a great día!"
    ]
    
    try:
        # Initialize clusterer
        clusterer = ContextAwareClusterer()
        
        # Perform clustering
        result = clusterer.cluster_with_context(
            texts, 
            method='dbscan', 
            eps=0.4, 
            min_samples=2
        )
        
        # Print results
        print(result.summary())
        
        # Show cluster assignments
        print("\nCluster Assignments:")
        print("=" * 20)
        for i, (text, label) in enumerate(zip(texts, result.cluster_labels)):
            print(f"[{label:2d}] {text}")
        
    except ImportError as e:
        print(f"❌ Required dependencies not available: {e}")
    except Exception as e:
        print(f"❌ Clustering failed: {e}")


if __name__ == "__main__":
    main()