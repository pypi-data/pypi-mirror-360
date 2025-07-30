"""Command-line interface for the code-switch aware AI library."""

import os
import json
from typing import List, Optional
from datetime import datetime
from ..detection import EnhancedCodeSwitchDetector, LanguageDetector
from ..memory import ConversationMemory, ConversationEntry, EmbeddingGenerator
from ..retrieval import SimilarityRetriever


class CLI:
    """Command-line interface for code-switch detection and memory."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize CLI with necessary components.
        
        Args:
            data_dir: Directory to store data files.
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize components
        self.language_detector = LanguageDetector()
        self.enhanced_detector = EnhancedCodeSwitchDetector(self.language_detector)
        self.memory = ConversationMemory(
            db_path=os.path.join(data_dir, "conversations.db"),
            embeddings_dir=os.path.join(data_dir, "embeddings")
        )
        self.embedding_generator = EmbeddingGenerator()
        self.retriever = SimilarityRetriever(
            self.memory,
            index_dir=os.path.join(data_dir, "indices")
        )
        
        # User settings
        self.current_user = "default"
        self.current_session = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.user_languages = []
    
    def display_welcome(self):
        """Display welcome message."""
        print("=" * 60)
        print("🌍 Code-Switch Aware AI Library")
        print("=" * 60)
        print("Welcome! This tool helps analyze multilingual code-switching patterns.")
        print("Type 'help' to see available commands.")
        print("-" * 60)
    
    def display_help(self):
        """Display help information."""
        help_text = """
Available Commands:

📝 Text Analysis:
  analyze <text>          - Analyze text for code-switching
  enhanced <text>         - Enhanced analysis with user guidance
  
👤 User Settings:
  set-user <user_id>      - Set current user ID
  set-languages <langs>   - Set user languages (comma-separated)
  get-user               - Show current user settings
  
💾 Memory Management:
  remember <text>         - Store text in conversation memory
  search <text>          - Search for similar conversations
  recent [limit]         - Show recent conversations
  stats                  - Show memory statistics
  
🔍 Advanced Features:
  build-index            - Build similarity index for current user
  profile                - Show user's language style profile
  
⚙️  System:
  help                   - Show this help message
  clear                  - Clear screen
  exit                   - Exit the application
  
Examples:
  enhanced Hello, how are you? ¿Cómo estás?
  set-languages english,spanish
  remember I love mixing English and español!
        """
        print(help_text)
    
    def set_user(self, user_id: str):
        """Set current user ID."""
        self.current_user = user_id.strip()
        self.current_session = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"✅ User set to: {self.current_user}")
    
    def set_languages(self, languages_str: str):
        """Set user languages."""
        self.user_languages = [lang.strip() for lang in languages_str.split(',')]
        print(f"✅ User languages set to: {', '.join(self.user_languages)}")
    
    def get_user_info(self):
        """Display current user information."""
        print(f"👤 Current User: {self.current_user}")
        print(f"🗣️  User Languages: {', '.join(self.user_languages) if self.user_languages else 'None set'}")
        print(f"📅 Current Session: {self.current_session}")
    
    def analyze_text_basic(self, text: str):
        """Analyze text using basic detection."""
        if not text.strip():
            print("❌ Please provide text to analyze.")
            return
        
        print(f"\n📝 Analyzing: '{text}'")
        print("-" * 40)
        
        # Basic language detection
        primary_lang = self.language_detector.detect_primary_language(text)
        lang_distribution = self.language_detector.get_language_distribution(text)
        is_multilingual = self.language_detector.is_multilingual(text)
        
        print(f"🔍 Primary Language: {primary_lang or 'Unknown'}")
        print(f"🌐 Multilingual: {'Yes' if is_multilingual else 'No'}")
        
        if lang_distribution:
            print("\n📊 Language Distribution:")
            for lang, confidence in lang_distribution.items():
                print(f"  {lang}: {confidence:.2%}")
        
        # Sentence-level analysis
        sentence_langs = self.language_detector.detect_sentence_languages(text)
        if len(sentence_langs) > 1:
            print("\n📄 Sentence Analysis:")
            for i, sentence_data in enumerate(sentence_langs, 1):
                print(f"  {i}. '{sentence_data['sentence']}' → {sentence_data['language']}")
    
    def analyze_text_enhanced(self, text: str):
        """Analyze text using enhanced detection."""
        if not text.strip():
            print("❌ Please provide text to analyze.")
            return
        
        print(f"\n🧠 Enhanced Analysis: '{text}'")
        print("-" * 50)
        
        # Enhanced detection
        result = self.enhanced_detector.analyze_with_user_guidance(text, self.user_languages)
        stats = self.enhanced_detector.get_detection_statistics(result)
        
        print(f"🔍 Detected Languages: {', '.join(result.detected_languages) if result.detected_languages else 'None'}")
        print(f"🎯 Overall Confidence: {result.confidence:.2%}")
        print(f"👤 User Language Match: {'Yes' if result.user_language_match else 'No'}")
        print(f"🔤 Romanization Detected: {'Yes' if result.romanization_detected else 'No'}")
        print(f"🔀 Switch Points: {len(result.switch_points)}")
        
        if result.switch_points:
            print(f"   Positions: {result.switch_points}")
        
        # Show phrase clusters
        if result.phrases:
            print(f"\n📋 Phrase Clusters ({len(result.phrases)}):")
            for i, phrase in enumerate(result.phrases, 1):
                marker = "👤" if phrase.is_user_language else "🌐"
                print(f"  {i}. {marker} '{phrase.text}' → {phrase.language} ({phrase.confidence:.2%})")
        
        # Show detailed statistics
        if stats['language_breakdown']:
            print(f"\n📊 Language Breakdown:")
            for lang_stat in stats['language_breakdown']:
                print(f"  {lang_stat['language']}: {lang_stat['token_count']} tokens "
                      f"({lang_stat['percentage']:.1f}%) - "
                      f"avg confidence: {lang_stat['average_confidence']:.2%}")
        
        print(f"\n📈 Statistics:")
        print(f"  Switch Density: {stats['switch_density']:.3f}")
        print(f"  Avg Words/Phrase: {stats['average_words_per_phrase']:.1f}")
    
    def remember_conversation(self, text: str):
        """Store conversation in memory."""
        if not text.strip():
            print("❌ Please provide text to remember.")
            return
        
        try:
            # Analyze the text
            result = self.enhanced_detector.analyze_with_user_guidance(text, self.user_languages)
            stats = self.enhanced_detector.get_detection_statistics(result)
            
            # Generate embeddings
            embeddings = self.embedding_generator.generate_conversation_embedding({
                'text': text,
                'switch_stats': stats,
                'metadata': {
                    'user_id': self.current_user,
                    'session_id': self.current_session,
                    'timestamp': datetime.now().timestamp()
                }
            })
            
            # Create conversation entry
            entry = ConversationEntry(
                text=text,
                switch_stats=stats,
                embeddings=embeddings,
                user_id=self.current_user,
                session_id=self.current_session
            )
            
            # Store in memory
            entry_id = self.memory.store_conversation(entry)
            
            # Update retrieval index
            self.retriever.update_index(entry, user_id=self.current_user)
            
            print(f"✅ Conversation stored with ID: {entry_id}")
            print(f"📊 Detected {len(result.detected_languages)} languages, "
                  f"{len(result.switch_points)} switch points")
            
        except Exception as e:
            print(f"❌ Error storing conversation: {e}")
    
    def search_conversations(self, query: str, limit: int = 5):
        """Search for similar conversations."""
        if not query.strip():
            print("❌ Please provide a search query.")
            return
        
        try:
            # Search using different methods
            print(f"\n🔍 Searching for: '{query}'")
            print("-" * 40)
            
            # Semantic search
            semantic_results = self.retriever.search_by_text(
                query, self.embedding_generator, 
                user_id=self.current_user, k=limit
            )
            
            if semantic_results:
                print(f"📝 Semantic Search Results:")
                for i, (conv, score) in enumerate(semantic_results, 1):
                    print(f"  {i}. Score: {score:.3f}")
                    print(f"     Text: '{conv.text[:60]}{'...' if len(conv.text) > 60 else ''}'")
                    print(f"     Languages: {', '.join(conv.switch_stats.get('detected_languages', []))}")
                    print()
            else:
                print("📝 No semantic matches found.")
            
        except Exception as e:
            print(f"❌ Error searching conversations: {e}")
    
    def show_recent_conversations(self, limit: int = 5):
        """Show recent conversations."""
        try:
            conversations = self.memory.get_user_conversations(self.current_user, limit)
            
            if not conversations:
                print(f"📝 No conversations found for user '{self.current_user}'.")
                return
            
            print(f"\n📚 Recent Conversations ({len(conversations)}):")
            print("-" * 50)
            
            for i, conv in enumerate(conversations, 1):
                detected_langs = conv.switch_stats.get('detected_languages', [])
                switch_count = conv.switch_stats.get('total_switches', 0)
                
                print(f"{i}. ID: {conv.entry_id}")
                print(f"   Text: '{conv.text[:60]}{'...' if len(conv.text) > 60 else ''}'")
                print(f"   Languages: {', '.join(detected_langs) if detected_langs else 'None'}")
                print(f"   Switches: {switch_count}")
                print(f"   Time: {conv.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                print()
                
        except Exception as e:
            print(f"❌ Error retrieving conversations: {e}")
    
    def show_memory_stats(self):
        """Show memory statistics."""
        try:
            stats = self.memory.get_conversation_stats(self.current_user)
            
            print(f"\n📊 Memory Statistics for '{self.current_user}':")
            print("-" * 40)
            print(f"Total Conversations: {stats.get('total_conversations', 0)}")
            print(f"Unique Sessions: {stats.get('unique_sessions', 0)}")
            
            if stats.get('earliest_conversation'):
                print(f"First Conversation: {stats['earliest_conversation']}")
            if stats.get('latest_conversation'):
                print(f"Latest Conversation: {stats['latest_conversation']}")
            
        except Exception as e:
            print(f"❌ Error retrieving statistics: {e}")
    
    def build_similarity_index(self):
        """Build similarity index for current user."""
        try:
            print(f"🔨 Building similarity index for user '{self.current_user}'...")
            self.retriever.build_index(user_id=self.current_user, force_rebuild=True)
            print("✅ Index built successfully!")
            
        except Exception as e:
            print(f"❌ Error building index: {e}")
    
    def show_user_profile(self):
        """Show user's language style profile."""
        try:
            profile = self.retriever.get_user_style_profile(
                self.current_user, self.embedding_generator
            )
            
            if not profile:
                print(f"📋 No profile data found for user '{self.current_user}'.")
                return
            
            print(f"\n👤 Language Style Profile for '{self.current_user}':")
            print("-" * 50)
            print(f"Total Conversations: {profile.get('total_conversations', 0)}")
            print(f"Total Switches: {profile.get('total_switches', 0)}")
            print(f"Languages Used: {profile.get('languages_used', 0)}")
            print(f"Avg Switch Density: {profile.get('avg_switch_density', 0):.3f}")
            print(f"Avg Confidence: {profile.get('avg_confidence', 0):.2%}")
            
            unique_languages = profile.get('unique_languages', [])
            if unique_languages:
                print(f"Languages: {', '.join(unique_languages)}")
                
        except Exception as e:
            print(f"❌ Error retrieving profile: {e}")
    
    def run(self):
        """Run the CLI interface."""
        self.display_welcome()
        
        while True:
            try:
                user_input = input(f"\n[{self.current_user}] > ").strip()
                
                if not user_input:
                    continue
                
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                if command == "exit":
                    print("👋 Goodbye!")
                    break
                elif command == "help":
                    self.display_help()
                elif command == "clear":
                    os.system('clear' if os.name == 'posix' else 'cls')
                elif command == "analyze":
                    self.analyze_text_basic(args)
                elif command == "enhanced":
                    self.analyze_text_enhanced(args)
                elif command == "set-user":
                    if args:
                        self.set_user(args)
                    else:
                        print("❌ Please provide a user ID.")
                elif command == "set-languages":
                    if args:
                        self.set_languages(args)
                    else:
                        print("❌ Please provide languages (comma-separated).")
                elif command == "get-user":
                    self.get_user_info()
                elif command == "remember":
                    self.remember_conversation(args)
                elif command == "search":
                    self.search_conversations(args)
                elif command == "recent":
                    limit = int(args) if args.isdigit() else 5
                    self.show_recent_conversations(limit)
                elif command == "stats":
                    self.show_memory_stats()
                elif command == "build-index":
                    self.build_similarity_index()
                elif command == "profile":
                    self.show_user_profile()
                else:
                    print(f"❌ Unknown command: {command}")
                    print("Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Main CLI entry point."""
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()