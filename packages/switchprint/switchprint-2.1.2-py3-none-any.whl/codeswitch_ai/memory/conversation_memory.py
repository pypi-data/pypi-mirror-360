"""Conversation memory storage and management."""

import sqlite3
import json
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import pickle
import os


class ConversationEntry:
    """Represents a single conversation entry."""
    
    def __init__(self, text: str, switch_stats: Dict, embeddings: Dict[str, np.ndarray],
                 timestamp: Optional[datetime] = None, user_id: str = "default",
                 session_id: str = "default"):
        self.text = text
        self.switch_stats = switch_stats
        self.embeddings = embeddings
        self.timestamp = timestamp or datetime.now()
        self.user_id = user_id
        self.session_id = session_id
        self.entry_id = None  # Set when saved to database
    
    def to_dict(self) -> Dict:
        """Convert entry to dictionary format."""
        return {
            "text": self.text,
            "switch_stats": self.switch_stats,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "session_id": self.session_id,
            "entry_id": self.entry_id
        }


class ConversationMemory:
    """Manages conversation history and embeddings storage."""
    
    def __init__(self, db_path: str = "conversation_memory.db", 
                 embeddings_dir: str = "embeddings"):
        """Initialize conversation memory.
        
        Args:
            db_path: Path to SQLite database file.
            embeddings_dir: Directory to store embedding files.
        """
        self.db_path = db_path
        self.embeddings_dir = embeddings_dir
        self._ensure_directories()
        self._init_database()
    
    def _ensure_directories(self):
        """Create necessary directories."""
        os.makedirs(self.embeddings_dir, exist_ok=True)
    
    def _init_database(self):
        """Initialize the SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    switch_stats TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    embedding_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_id ON conversations(user_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_id ON conversations(session_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations(timestamp)
            """)
    
    def create_and_store_conversation(self, text: str, user_id: str, switch_stats: Dict,
                                     session_id: str = None, metadata: Dict = None) -> str:
        """Helper method to create and store a conversation entry.
        
        Args:
            text: Conversation text
            user_id: User identifier
            switch_stats: Code-switching statistics
            session_id: Optional session identifier
            metadata: Optional metadata (not used in storage but can be passed)
            
        Returns:
            Entry ID of the stored conversation.
        """
        import datetime
        import uuid
        
        entry = ConversationEntry(
            text=text,
            user_id=user_id,
            switch_stats=switch_stats,
            timestamp=datetime.datetime.now(),
            session_id=session_id or str(uuid.uuid4()),
            embeddings={}  # Will be generated automatically
        )
        
        return self.store_conversation(entry)

    def store_conversation(self, entry: ConversationEntry) -> str:
        """Store a conversation entry.
        
        Args:
            entry: ConversationEntry to store.
            
        Returns:
            Entry ID of the stored conversation.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO conversations 
                (text, switch_stats, timestamp, user_id, session_id, embedding_path)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                entry.text,
                json.dumps(entry.switch_stats),
                entry.timestamp.isoformat(),
                entry.user_id,
                entry.session_id,
                None  # Will be set when embeddings are stored
            ))
            
            entry_id = str(cursor.lastrowid)
            entry.entry_id = entry_id
            
            # Store embeddings separately
            embedding_path = self._store_embeddings(entry_id, entry.embeddings)
            
            # Update embedding path in database
            conn.execute("""
                UPDATE conversations SET embedding_path = ? WHERE id = ?
            """, (embedding_path, entry_id))
            
            return entry_id
    
    def get_conversation(self, entry_id: str) -> Optional[ConversationEntry]:
        """Retrieve a conversation entry by ID.
        
        Args:
            entry_id: ID of the conversation entry.
            
        Returns:
            ConversationEntry if found, None otherwise.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT text, switch_stats, timestamp, user_id, session_id, embedding_path
                FROM conversations WHERE id = ?
            """, (entry_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            text, switch_stats_json, timestamp_str, user_id, session_id, embedding_path = row
            
            # Load embeddings
            embeddings = self._load_embeddings(embedding_path) if embedding_path else {}
            
            entry = ConversationEntry(
                text=text,
                switch_stats=json.loads(switch_stats_json),
                embeddings=embeddings,
                timestamp=datetime.fromisoformat(timestamp_str),
                user_id=user_id,
                session_id=session_id
            )
            entry.entry_id = entry_id
            
            return entry
    
    def get_user_conversations(self, user_id: str, limit: int = 100) -> List[ConversationEntry]:
        """Get conversations for a specific user.
        
        Args:
            user_id: User identifier.
            limit: Maximum number of conversations to return.
            
        Returns:
            List of ConversationEntry objects.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id FROM conversations 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (user_id, limit))
            
            entry_ids = [str(row[0]) for row in cursor.fetchall()]
            
        return [self.get_conversation(entry_id) for entry_id in entry_ids 
                if self.get_conversation(entry_id) is not None]
    
    def get_session_conversations(self, session_id: str, user_id: str = None) -> List[ConversationEntry]:
        """Get conversations for a specific session.
        
        Args:
            session_id: Session identifier.
            user_id: Optional user identifier for filtering.
            
        Returns:
            List of ConversationEntry objects.
        """
        with sqlite3.connect(self.db_path) as conn:
            if user_id:
                cursor = conn.execute("""
                    SELECT id FROM conversations 
                    WHERE session_id = ? AND user_id = ?
                    ORDER BY timestamp ASC
                """, (session_id, user_id))
            else:
                cursor = conn.execute("""
                    SELECT id FROM conversations 
                    WHERE session_id = ?
                    ORDER BY timestamp ASC
                """, (session_id,))
            
            entry_ids = [str(row[0]) for row in cursor.fetchall()]
        
        return [self.get_conversation(entry_id) for entry_id in entry_ids
                if self.get_conversation(entry_id) is not None]
    
    def delete_conversation(self, entry_id: str) -> bool:
        """Delete a conversation entry.
        
        Args:
            entry_id: ID of the conversation to delete.
            
        Returns:
            True if deleted successfully, False otherwise.
        """
        # Get embedding path before deletion
        entry = self.get_conversation(entry_id)
        if not entry:
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM conversations WHERE id = ?
            """, (entry_id,))
            
            if cursor.rowcount > 0:
                # Delete embedding file
                embedding_path = os.path.join(self.embeddings_dir, f"{entry_id}.pkl")
                if os.path.exists(embedding_path):
                    os.remove(embedding_path)
                return True
        
        return False
    
    def get_conversation_stats(self, user_id: str = None) -> Dict:
        """Get statistics about stored conversations.
        
        Args:
            user_id: Optional user identifier for filtering.
            
        Returns:
            Dictionary with conversation statistics.
        """
        with sqlite3.connect(self.db_path) as conn:
            if user_id:
                cursor = conn.execute("""
                    SELECT COUNT(*), 
                           COUNT(DISTINCT session_id),
                           MIN(timestamp),
                           MAX(timestamp)
                    FROM conversations WHERE user_id = ?
                """, (user_id,))
            else:
                cursor = conn.execute("""
                    SELECT COUNT(*),
                           COUNT(DISTINCT user_id),
                           COUNT(DISTINCT session_id), 
                           MIN(timestamp),
                           MAX(timestamp)
                    FROM conversations
                """)
            
            row = cursor.fetchone()
            
            if user_id:
                total_conversations, unique_sessions, min_time, max_time = row
                return {
                    "total_conversations": total_conversations,
                    "unique_sessions": unique_sessions,
                    "earliest_conversation": min_time,
                    "latest_conversation": max_time,
                    "user_id": user_id
                }
            else:
                total_conversations, unique_users, unique_sessions, min_time, max_time = row
                return {
                    "total_conversations": total_conversations,
                    "unique_users": unique_users,
                    "unique_sessions": unique_sessions,
                    "earliest_conversation": min_time,
                    "latest_conversation": max_time
                }
    
    def _store_embeddings(self, entry_id: str, embeddings: Dict[str, np.ndarray]) -> str:
        """Store embeddings to disk.
        
        Args:
            entry_id: Entry identifier.
            embeddings: Dictionary of embeddings.
            
        Returns:
            Path to stored embedding file.
        """
        embedding_path = os.path.join(self.embeddings_dir, f"{entry_id}.pkl")
        
        with open(embedding_path, 'wb') as f:
            pickle.dump(embeddings, f)
        
        return embedding_path
    
    def _load_embeddings(self, embedding_path: str) -> Dict[str, np.ndarray]:
        """Load embeddings from disk.
        
        Args:
            embedding_path: Path to embedding file.
            
        Returns:
            Dictionary of embeddings.
        """
        if not os.path.exists(embedding_path):
            return {}
        
        try:
            with open(embedding_path, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return {}
    
    def cleanup_old_conversations(self, days_old: int = 90, user_id: str = None):
        """Remove conversations older than specified days.
        
        Args:
            days_old: Number of days old to consider for cleanup.
            user_id: Optional user identifier for filtering.
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        with sqlite3.connect(self.db_path) as conn:
            if user_id:
                cursor = conn.execute("""
                    SELECT id, embedding_path FROM conversations 
                    WHERE timestamp < ? AND user_id = ?
                """, (cutoff_date.isoformat(), user_id))
            else:
                cursor = conn.execute("""
                    SELECT id, embedding_path FROM conversations 
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
            
            old_entries = cursor.fetchall()
            
            # Delete embedding files
            for entry_id, embedding_path in old_entries:
                if embedding_path and os.path.exists(embedding_path):
                    os.remove(embedding_path)
            
            # Delete database entries
            if user_id:
                conn.execute("""
                    DELETE FROM conversations 
                    WHERE timestamp < ? AND user_id = ?
                """, (cutoff_date.isoformat(), user_id))
            else:
                conn.execute("""
                    DELETE FROM conversations WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))