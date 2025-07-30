#!/usr/bin/env python3
"""Custom model fine-tuning for domain-specific code-switching detection."""

import os
import json
import torch
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import time
from collections import defaultdict
import pickle

try:
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        TrainingArguments, Trainer, EarlyStoppingCallback,
        DataCollatorWithPadding
    )
    from datasets import Dataset
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠ Transformers not available. Install with: pip install transformers datasets")

try:
    import fasttext
    FASTTEXT_AVAILABLE = True
except ImportError:
    FASTTEXT_AVAILABLE = False
    print("⚠ FastText not available. Install with: pip install fasttext")


@dataclass
class FineTuningConfig:
    """Configuration for model fine-tuning."""
    model_name: str = "bert-base-multilingual-cased"
    num_labels: int = 2  # binary: code-switched or not
    learning_rate: float = 2e-5
    batch_size: int = 16
    num_epochs: int = 3
    warmup_steps: int = 500
    weight_decay: float = 0.01
    evaluation_strategy: str = "steps"
    eval_steps: int = 500
    save_steps: int = 1000
    logging_steps: int = 100
    load_best_model_at_end: bool = True
    metric_for_best_model: str = "eval_f1"
    greater_is_better: bool = True
    early_stopping_patience: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class FineTuningResults:
    """Results from model fine-tuning."""
    model_name: str
    final_accuracy: float
    final_f1: float
    training_time: float
    best_checkpoint: str
    evaluation_history: List[Dict[str, float]]
    domain_performance: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def summary(self) -> str:
        """Generate summary report."""
        return f"""
Fine-tuning Results:
===================
Model: {self.model_name}
Final Accuracy: {self.final_accuracy:.4f}
Final F1-Score: {self.final_f1:.4f}
Training Time: {self.training_time:.2f}s
Best Checkpoint: {self.best_checkpoint}

Domain Performance:
{self._format_domain_performance()}
"""
    
    def _format_domain_performance(self) -> str:
        """Format domain-specific performance."""
        lines = []
        for domain, score in self.domain_performance.items():
            lines.append(f"  {domain}: {score:.4f}")
        return "\n".join(lines)


class CustomModelTrainer:
    """Custom model trainer for domain-specific fine-tuning."""
    
    def __init__(self, config: FineTuningConfig):
        """Initialize trainer with configuration.
        
        Args:
            config: Fine-tuning configuration
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("Transformers required for fine-tuning")
        
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize model and tokenizer
        print(f"📥 Loading {config.model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(config.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            config.model_name,
            num_labels=config.num_labels
        )
        self.model.to(self.device)
        
        # Training components
        self.trainer = None
        self.training_results = None
        
        print(f"✓ Model loaded on {self.device}")
    
    def prepare_dataset(self, texts: List[str], labels: List[int], 
                       domains: Optional[List[str]] = None) -> Dataset:
        """Prepare dataset for training.
        
        Args:
            texts: Input texts
            labels: Binary labels (0: monolingual, 1: code-switched)
            domains: Optional domain labels for tracking
            
        Returns:
            Prepared dataset
        """
        print(f"📊 Preparing dataset with {len(texts)} samples...")
        
        # Tokenize texts
        encodings = self.tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors="pt"
        )
        
        # Create dataset
        dataset_dict = {
            'input_ids': encodings['input_ids'],
            'attention_mask': encodings['attention_mask'],
            'labels': torch.tensor(labels, dtype=torch.long)
        }
        
        # Add domain information if provided
        if domains:
            domain_to_id = {domain: i for i, domain in enumerate(set(domains))}
            domain_ids = [domain_to_id[domain] for domain in domains]
            dataset_dict['domains'] = torch.tensor(domain_ids, dtype=torch.long)
        
        dataset = Dataset.from_dict({
            k: v.tolist() if isinstance(v, torch.Tensor) else v 
            for k, v in dataset_dict.items()
        })
        
        print(f"✓ Dataset prepared: {len(dataset)} samples")
        return dataset
    
    def compute_metrics(self, eval_pred) -> Dict[str, float]:
        """Compute evaluation metrics.
        
        Args:
            eval_pred: Evaluation predictions
            
        Returns:
            Dictionary of metrics
        """
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        # Compute standard metrics
        accuracy = accuracy_score(labels, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, predictions, average='weighted'
        )
        
        return {
            'accuracy': accuracy,
            'f1': f1,
            'precision': precision,
            'recall': recall
        }
    
    def train(self, train_dataset: Dataset, eval_dataset: Optional[Dataset] = None,
             output_dir: str = "./fine_tuned_model") -> FineTuningResults:
        """Train the model.
        
        Args:
            train_dataset: Training dataset
            eval_dataset: Optional evaluation dataset
            output_dir: Output directory for checkpoints
            
        Returns:
            Training results
        """
        print(f"🚀 Starting fine-tuning...")
        print(f"Training samples: {len(train_dataset)}")
        if eval_dataset:
            print(f"Evaluation samples: {len(eval_dataset)}")
        
        # Set up training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            learning_rate=self.config.learning_rate,
            per_device_train_batch_size=self.config.batch_size,
            per_device_eval_batch_size=self.config.batch_size,
            num_train_epochs=self.config.num_epochs,
            warmup_steps=self.config.warmup_steps,
            weight_decay=self.config.weight_decay,
            logging_dir=f"{output_dir}/logs",
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            report_to=None,
            save_total_limit=2,
        )
        
        # Set up trainer
        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            tokenizer=self.tokenizer,
            data_collator=DataCollatorWithPadding(self.tokenizer),
            compute_metrics=self.compute_metrics,
        )
        
        # Train model
        start_time = time.time()
        train_result = self.trainer.train()
        training_time = time.time() - start_time
        
        # Save final model
        self.trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        # Evaluate final model
        if eval_dataset:
            eval_result = self.trainer.evaluate()
            final_accuracy = eval_result['eval_accuracy']
            final_f1 = eval_result['eval_f1']
        else:
            final_accuracy = 0.0
            final_f1 = 0.0
        
        # Get training history
        evaluation_history = []
        if hasattr(self.trainer.state, 'log_history'):
            evaluation_history = [
                log for log in self.trainer.state.log_history 
                if 'eval_accuracy' in log
            ]
        
        # Compute domain-specific performance
        domain_performance = {}
        if eval_dataset and 'domains' in eval_dataset.features:
            domain_performance = self._evaluate_by_domain(eval_dataset)
        
        # Create results
        results = FineTuningResults(
            model_name=self.config.model_name,
            final_accuracy=final_accuracy,
            final_f1=final_f1,
            training_time=training_time,
            best_checkpoint=output_dir,
            evaluation_history=evaluation_history,
            domain_performance=domain_performance
        )
        
        self.training_results = results
        
        print(f"✓ Fine-tuning completed in {training_time:.2f}s")
        print(f"📊 Final accuracy: {final_accuracy:.4f}")
        print(f"📊 Final F1-score: {final_f1:.4f}")
        
        return results
    
    def _evaluate_by_domain(self, eval_dataset: Dataset) -> Dict[str, float]:
        """Evaluate model performance by domain.
        
        Args:
            eval_dataset: Evaluation dataset with domain labels
            
        Returns:
            Domain-specific performance scores
        """
        # Get predictions for entire dataset
        predictions = self.trainer.predict(eval_dataset)
        pred_labels = np.argmax(predictions.predictions, axis=1)
        true_labels = predictions.label_ids
        
        # Group by domain
        domains = eval_dataset['domains']
        domain_scores = {}
        
        unique_domains = set(domains)
        for domain_id in unique_domains:
            domain_mask = np.array(domains) == domain_id
            domain_true = np.array(true_labels)[domain_mask]
            domain_pred = pred_labels[domain_mask]
            
            if len(domain_true) > 0:
                domain_accuracy = accuracy_score(domain_true, domain_pred)
                domain_scores[f"domain_{domain_id}"] = domain_accuracy
        
        return domain_scores
    
    def save_config(self, output_dir: str) -> None:
        """Save training configuration.
        
        Args:
            output_dir: Output directory
        """
        config_path = os.path.join(output_dir, "training_config.json")
        with open(config_path, 'w') as f:
            json.dump(self.config.to_dict(), f, indent=2)
        print(f"✓ Config saved to {config_path}")


class FastTextDomainTrainer:
    """FastText trainer for domain-specific models."""
    
    def __init__(self, config: Optional[FineTuningConfig] = None):
        """Initialize FastText trainer.
        
        Args:
            config: Optional configuration (for compatibility).
        """
        if not FASTTEXT_AVAILABLE:
            raise ImportError("FastText required for training")
        
        self.config = config  # Store config for potential future use
        self.model = None
        self.training_file = None
    
    def prepare_training_data(self, texts: List[str], labels: List[str], 
                            output_file: str = "fasttext_training.txt") -> str:
        """Prepare training data in FastText format.
        
        Args:
            texts: Input texts
            labels: String labels (e.g., 'monolingual', 'code_switched')
            output_file: Output file path
            
        Returns:
            Path to training file
        """
        print(f"📝 Preparing FastText training data...")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for text, label in zip(texts, labels):
                # FastText format: __label__<label> <text>
                clean_text = text.replace('\n', ' ').replace('\r', ' ')
                f.write(f"__label__{label} {clean_text}\n")
        
        self.training_file = output_file
        print(f"✓ Training data saved to {output_file}: {len(texts)} samples")
        return output_file
    
    def train(self, training_file: str, model_output: str = "domain_fasttext.bin",
             **kwargs) -> str:
        """Train FastText model.
        
        Args:
            training_file: Path to training data
            model_output: Output model file
            **kwargs: Additional FastText parameters
            
        Returns:
            Path to trained model
        """
        print(f"🚀 Training FastText model...")
        
        # Default parameters optimized for code-switching
        default_params = {
            'lr': 0.1,
            'dim': 100,
            'ws': 5,
            'epoch': 50,
            'minCount': 1,
            'minn': 3,
            'maxn': 6,
            'neg': 5,
            'wordNgrams': 2,
            'loss': 'softmax',
            'bucket': 2000000,
            'thread': 4,
            'lrUpdateRate': 100,
            't': 0.0001
        }
        
        # Update with user parameters
        params = {**default_params, **kwargs}
        
        # Train model
        start_time = time.time()
        self.model = fasttext.train_supervised(training_file, **params)
        training_time = time.time() - start_time
        
        # Save model
        self.model.save_model(model_output)
        
        print(f"✓ FastText training completed in {training_time:.2f}s")
        print(f"✓ Model saved to {model_output}")
        
        return model_output
    
    def evaluate(self, test_file: str) -> Dict[str, float]:
        """Evaluate trained model.
        
        Args:
            test_file: Path to test data
            
        Returns:
            Evaluation metrics
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        print(f"📊 Evaluating model on {test_file}...")
        
        # FastText evaluation
        results = self.model.test(test_file)
        
        # Extract metrics
        num_samples = results[0]
        precision = results[1]
        recall = results[2]
        
        metrics = {
            'num_samples': num_samples,
            'precision': precision,
            'recall': recall,
            'f1': 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        }
        
        print(f"✓ Evaluation completed: P={precision:.4f}, R={recall:.4f}, F1={metrics['f1']:.4f}")
        
        return metrics


def create_synthetic_domain_data(domain: str, num_samples: int = 1000) -> Tuple[List[str], List[int]]:
    """Create synthetic domain-specific training data.
    
    Args:
        domain: Domain name (e.g., 'social_media', 'academic', 'business')
        num_samples: Number of samples to generate
        
    Returns:
        Tuple of (texts, labels)
    """
    np.random.seed(42)
    
    # Domain-specific templates
    domain_templates = {
        'social_media': {
            'monolingual': [
                "Just had an amazing day!",
                "Can't wait for the weekend",
                "Love this new song",
                "Working from home today",
                "Great weather outside"
            ],
            'code_switched': [
                "Just had an amazing día!",
                "Can't wait for el weekend",
                "Love this nueva canción",
                "Working desde casa today",
                "Great tiempo outside"
            ]
        },
        'academic': {
            'monolingual': [
                "The research methodology was comprehensive",
                "Data analysis revealed significant patterns",
                "Literature review covers relevant studies",
                "Experimental design follows standard protocols",
                "Results demonstrate clear correlations"
            ],
            'code_switched': [
                "The investigación methodology was comprehensive",
                "Data análisis revealed significant patterns",
                "Literature revisión covers relevant studies",
                "Experimental diseño follows standard protocols",
                "Results demonstrate clear correlaciones"
            ]
        },
        'business': {
            'monolingual': [
                "The quarterly report shows growth",
                "Market analysis indicates opportunities",
                "Client feedback has been positive",
                "Sales targets were exceeded",
                "New product launch scheduled"
            ],
            'code_switched': [
                "The quarterly reporte shows growth",
                "Market análisis indicates opportunities",
                "Cliente feedback has been positive",
                "Sales objetivos were exceeded",
                "New producto launch scheduled"
            ]
        }
    }
    
    if domain not in domain_templates:
        domain = 'social_media'  # Default fallback
    
    templates = domain_templates[domain]
    texts = []
    labels = []
    
    for _ in range(num_samples):
        # 50% monolingual, 50% code-switched
        is_code_switched = int(np.random.choice([0, 1]))
        template_type = 'code_switched' if is_code_switched else 'monolingual'
        
        # Select random template and add some variation
        template = np.random.choice(templates[template_type])
        
        # Add some random variation
        if np.random.random() < 0.3:
            # Add punctuation variation
            if template.endswith('.'):
                template = template[:-1] + np.random.choice(['!', '?', '.'])
        
        texts.append(template)
        labels.append(is_code_switched)
    
    return texts, labels


def main():
    """Example usage of custom model training."""
    print("🔬 Custom Model Fine-tuning Example")
    print("=" * 40)
    
    # Generate synthetic training data
    print("📊 Generating synthetic training data...")
    train_texts, train_labels = create_synthetic_domain_data('social_media', 800)
    eval_texts, eval_labels = create_synthetic_domain_data('social_media', 200)
    
    print(f"Training samples: {len(train_texts)}")
    print(f"Evaluation samples: {len(eval_texts)}")
    
    # Test FastText training
    if FASTTEXT_AVAILABLE:
        print("\n🚀 Testing FastText domain training...")
        
        try:
            ft_trainer = FastTextDomainTrainer()
            
            # Prepare data
            train_file = ft_trainer.prepare_training_data(
                train_texts, 
                ['code_switched' if label else 'monolingual' for label in train_labels]
            )
            
            # Train model
            model_path = ft_trainer.train(train_file, epoch=10)
            
            print("✓ FastText domain training completed")
            
        except Exception as e:
            print(f"❌ FastText training failed: {e}")
    
    # Test transformer fine-tuning (if available)
    if TRANSFORMERS_AVAILABLE:
        print("\n🚀 Testing transformer fine-tuning...")
        
        try:
            # Use smaller model for testing
            config = FineTuningConfig(
                model_name="distilbert-base-multilingual-cased",
                num_epochs=1,  # Quick test
                batch_size=8,
                eval_steps=100,
                save_steps=200
            )
            
            trainer = CustomModelTrainer(config)
            
            # Prepare datasets
            train_dataset = trainer.prepare_dataset(train_texts[:50], train_labels[:50])
            eval_dataset = trainer.prepare_dataset(eval_texts[:20], eval_labels[:20])
            
            # Train model
            results = trainer.train(
                train_dataset, 
                eval_dataset, 
                output_dir="./test_fine_tuned"
            )
            
            print("✓ Transformer fine-tuning completed")
            print(results.summary())
            
        except Exception as e:
            print(f"❌ Transformer fine-tuning failed: {e}")
    
    print("\n✓ Custom model training examples completed")


if __name__ == "__main__":
    main()