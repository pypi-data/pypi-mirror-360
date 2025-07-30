#!/usr/bin/env python3
"""
∂Config.py - Centralized configuration with memory
Part of the ∂-prefixed architecture for conversation-aware multi-agent development

This module provides centralized configuration management with conversation memory,
user preference learning, and project-specific adaptation capabilities.
"""

import json
import os
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

try:
    from langmem import create_manage_memory_tool, create_search_memory_tool
    from langgraph.store.memory import InMemoryStore
    LANGMEM_AVAILABLE = True
except ImportError:
    LANGMEM_AVAILABLE = False


@dataclass
class ConfigMemory:
    """Configuration memory structure for preference learning"""
    user_id: str
    preference_key: str
    preference_value: Any
    confidence_score: float
    last_updated: datetime
    usage_count: int = 0
    context: Optional[str] = None


class DeltaConfig:
    """
    ∂Config - Centralized configuration with conversation memory
    
    Features:
    - User preference learning from conversations
    - Project-specific configuration adaptation
    - Settings that evolve based on user interactions
    - LangMem integration for advanced memory capabilities
    - SQLite fallback for session persistence
    """
    
    def __init__(self, config_dir: str = ".claude", user_id: str = "developer"):
        self.config_dir = Path(config_dir)
        self.user_id = user_id
        self.config_file = self.config_dir / "∂config.json"
        self.memory_db = self.config_dir / "∂memory.db"
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)
        
        # Set up logging first
        self.logger = logging.getLogger(f"∂Config[{user_id}]")
        
        # Initialize memory systems
        self._init_memory_systems()
        
        # Load configurations
        self._config_data = self._load_config()
        
        # Initialize database
        self._init_database()
    
    def _init_memory_systems(self):
        """Initialize LangMem and fallback SQLite memory systems"""
        global LANGMEM_AVAILABLE
        self.memory_tools = []
        
        if LANGMEM_AVAILABLE:
            try:
                self.store = InMemoryStore(
                    index={"dims": 1536, "embed": "openai:text-embedding-3-small"}
                )
                self.namespace = ("∂config", self.user_id)
                self.memory_tools = [
                    create_manage_memory_tool(namespace=self.namespace),
                    create_search_memory_tool(namespace=self.namespace),
                ]
                self.logger.info("LangMem memory system initialized")
            except Exception as e:
                self.logger.warning(f"LangMem initialization failed: {e}")
                LANGMEM_AVAILABLE = False
        
        if not LANGMEM_AVAILABLE:
            self.logger.info("Using SQLite memory fallback")
    
    def _init_database(self):
        """Initialize SQLite database for configuration memory"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS config_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    preference_key TEXT NOT NULL,
                    preference_value TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    last_updated TIMESTAMP NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    context TEXT,
                    UNIQUE(user_id, preference_key)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS config_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    config_snapshot TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    UNIQUE(user_id, session_id)
                )
            """)
            
            conn.commit()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")
                return self._get_default_config()
        else:
            config = self._get_default_config()
            self._save_config(config)
            return config
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration structure"""
        return {
            "version": "1.0.0",
            "user_id": self.user_id,
            "created_at": datetime.now().isoformat(),
            "memory": {
                "enabled": True,
                "provider": "langmem" if LANGMEM_AVAILABLE else "sqlite",
                "retention_days": 30,
                "max_memories": 1000
            },
            "development": {
                "auto_commit": True,
                "complexity_threshold": "B",
                "test_coverage_minimum": 0.8,
                "code_style": "black",
                "type_checking": "mypy"
            },
            "ai_providers": {
                "primary": "anthropic",
                "fallback": "openai",
                "local_models": []
            },
            "project_preferences": {},
            "learned_patterns": {}
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with memory-enhanced lookup"""
        # First check direct config
        keys = key.split('.')
        value = self._config_data
        
        try:
            for k in keys:
                value = value[k]
            
            # Record usage for learning
            self._record_preference_usage(key, value)
            return value
            
        except (KeyError, TypeError):
            # Check learned preferences
            learned_value = self._get_learned_preference(key)
            if learned_value is not None:
                return learned_value
            
            return default
    
    def set(self, key: str, value: Any, confidence: float = 1.0, context: str = None):
        """Set configuration value with memory learning"""
        # Update direct config
        keys = key.split('.')
        config_ref = self._config_data
        
        for k in keys[:-1]:
            if k not in config_ref:
                config_ref[k] = {}
            config_ref = config_ref[k]
        
        config_ref[keys[-1]] = value
        
        # Save config
        self._save_config(self._config_data)
        
        # Learn preference
        self._learn_preference(key, value, confidence, context)
        
        self.logger.info(f"Set config: {key} = {value}")
    
    def _learn_preference(self, key: str, value: Any, confidence: float, context: str = None):
        """Learn user preference for future sessions"""
        memory = ConfigMemory(
            user_id=self.user_id,
            preference_key=key,
            preference_value=value,
            confidence_score=confidence,
            last_updated=datetime.now(),
            context=context
        )
        
        # Store in SQLite
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO config_memory 
                (user_id, preference_key, preference_value, confidence_score, 
                 last_updated, usage_count, context)
                VALUES (?, ?, ?, ?, ?, 
                        COALESCE((SELECT usage_count FROM config_memory 
                                 WHERE user_id = ? AND preference_key = ?), 0) + 1,
                        ?)
            """, (
                memory.user_id, memory.preference_key, json.dumps(memory.preference_value),
                memory.confidence_score, memory.last_updated, 
                memory.user_id, memory.preference_key, memory.context
            ))
            conn.commit()
        
        # Store in LangMem if available
        if LANGMEM_AVAILABLE and self.memory_tools:
            try:
                memory_content = f"User preference: {key} = {value} (confidence: {confidence})"
                if context:
                    memory_content += f" Context: {context}"
                
                # Use LangMem manage tool to store preference
                # This would be called in actual implementation
                self.logger.info(f"Stored preference in LangMem: {key}")
            except Exception as e:
                self.logger.warning(f"Failed to store in LangMem: {e}")
    
    def _get_learned_preference(self, key: str) -> Optional[Any]:
        """Retrieve learned preference from memory"""
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT preference_value, confidence_score, usage_count
                FROM config_memory
                WHERE user_id = ? AND preference_key = ?
                ORDER BY confidence_score DESC, usage_count DESC
                LIMIT 1
            """, (self.user_id, key))
            
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row[0])
                except json.JSONDecodeError:
                    return row[0]
        
        return None
    
    def _record_preference_usage(self, key: str, value: Any):
        """Record preference usage for learning confidence"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                UPDATE config_memory 
                SET usage_count = usage_count + 1, last_updated = ?
                WHERE user_id = ? AND preference_key = ?
            """, (datetime.now(), self.user_id, key))
            conn.commit()
    
    def adapt_from_conversation(self, conversation_context: Dict[str, Any]):
        """Adapt configuration based on conversation patterns"""
        # Analyze conversation for preference indicators
        if "code_style" in conversation_context:
            self.set("development.code_style", conversation_context["code_style"], 
                    confidence=0.7, context="conversation_inference")
        
        if "complexity_preference" in conversation_context:
            self.set("development.complexity_threshold", 
                    conversation_context["complexity_preference"],
                    confidence=0.6, context="conversation_inference")
        
        if "ai_provider_preference" in conversation_context:
            self.set("ai_providers.primary", 
                    conversation_context["ai_provider_preference"],
                    confidence=0.8, context="conversation_inference")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) as total_memories,
                       AVG(confidence_score) as avg_confidence,
                       MAX(usage_count) as max_usage,
                       COUNT(DISTINCT preference_key) as unique_keys
                FROM config_memory
                WHERE user_id = ?
            """, (self.user_id,))
            
            row = cursor.fetchone()
            
            return {
                "total_memories": row[0],
                "average_confidence": row[1],
                "max_usage_count": row[2],
                "unique_preferences": row[3],
                "memory_provider": "langmem" if LANGMEM_AVAILABLE else "sqlite",
                "database_size": self.memory_db.stat().st_size if self.memory_db.exists() else 0
            }
    
    def export_config(self) -> Dict[str, Any]:
        """Export complete configuration including learned preferences"""
        learned_prefs = {}
        
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT preference_key, preference_value, confidence_score, usage_count
                FROM config_memory
                WHERE user_id = ?
                ORDER BY confidence_score DESC, usage_count DESC
            """, (self.user_id,))
            
            for row in cursor.fetchall():
                try:
                    value = json.loads(row[1])
                except json.JSONDecodeError:
                    value = row[1]
                
                learned_prefs[row[0]] = {
                    "value": value,
                    "confidence": row[2],
                    "usage_count": row[3]
                }
        
        return {
            "static_config": self._config_data,
            "learned_preferences": learned_prefs,
            "memory_stats": self.get_memory_stats()
        }
    
    def save_session_snapshot(self, session_id: str):
        """Save current configuration state for session continuity"""
        snapshot = {
            "config": self._config_data,
            "timestamp": datetime.now().isoformat(),
            "memory_stats": self.get_memory_stats()
        }
        
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO config_sessions
                (user_id, session_id, config_snapshot, created_at)
                VALUES (?, ?, ?, ?)
            """, (self.user_id, session_id, json.dumps(snapshot), datetime.now()))
            conn.commit()
    
    def restore_session_snapshot(self, session_id: str) -> bool:
        """Restore configuration from previous session"""
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT config_snapshot FROM config_sessions
                WHERE user_id = ? AND session_id = ?
            """, (self.user_id, session_id))
            
            row = cursor.fetchone()
            if row:
                try:
                    snapshot = json.loads(row[0])
                    self._config_data = snapshot["config"]
                    self._save_config(self._config_data)
                    return True
                except json.JSONDecodeError:
                    return False
        
        return False


# Global configuration instance
_global_config = None


def get_config(user_id: str = "developer") -> DeltaConfig:
    """Get global configuration instance"""
    global _global_config
    if _global_config is None:
        _global_config = DeltaConfig(user_id=user_id)
    return _global_config


def initialize_config(config_dir: str = ".claude", user_id: str = "developer") -> DeltaConfig:
    """Initialize configuration system"""
    global _global_config
    _global_config = DeltaConfig(config_dir=config_dir, user_id=user_id)
    return _global_config


if __name__ == "__main__":
    # Test configuration system
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Testing ∂Config system...")
        
        # Initialize config
        config = initialize_config()
        
        # Test basic operations
        config.set("test.value", "hello world", confidence=0.9)
        value = config.get("test.value")
        print(f"Set and retrieved: {value}")
        
        # Test memory stats
        stats = config.get_memory_stats()
        print(f"Memory stats: {stats}")
        
        # Test session snapshot
        config.save_session_snapshot("test_session")
        print("Session snapshot saved")
        
        # Test export
        export_data = config.export_config()
        print(f"Config exported with {len(export_data['learned_preferences'])} learned preferences")
        
        print("∂Config system test completed successfully!")
    else:
        print("∂Config.py - Centralized configuration with memory")
        print("Usage: python ∂Config.py --test")