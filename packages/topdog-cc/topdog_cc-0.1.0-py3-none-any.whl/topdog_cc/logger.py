#!/usr/bin/env python3
"""
∂Logger.py - Conversation-aware comprehensive logging
Part of the ∂-prefixed architecture for conversation-aware multi-agent development

This module provides comprehensive logging with conversation context, cross-session
log correlation, and learning from log pattern analysis.
"""

import json
import logging
import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import traceback

try:
    from langmem import create_manage_memory_tool, create_search_memory_tool
    from langgraph.store.memory import InMemoryStore
    LANGMEM_AVAILABLE = True
except ImportError:
    LANGMEM_AVAILABLE = False

# Import using standard ASCII filenames
import importlib.util

# Load ∂Config module
from .config import get_config





class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    CONVERSATION = "CONVERSATION"
    PATTERN = "PATTERN"
    MEMORY = "MEMORY"


@dataclass
class ConversationLogEntry:
    """Structured log entry with conversation context"""
    timestamp: datetime
    level: LogLevel
    component: str
    message: str
    conversation_id: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None
    stack_trace: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "component": self.component,
            "message": self.message,
            "conversation_id": self.conversation_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "context": self.context,
            "correlation_id": self.correlation_id,
            "stack_trace": self.stack_trace
        }


class DeltaLogger:
    """
    ∂Logger - Conversation-aware comprehensive logging
    
    Features:
    - Structured logging with conversation context
    - Cross-session log correlation
    - Learning from log pattern analysis
    - LangMem integration for advanced memory capabilities
    - Real-time log analysis and anomaly detection
    """
    
    def __init__(self, component_name: str, config_dir: str = ".claude"):
        self.component_name = component_name
        self.config_dir = Path(config_dir)
        self.config = get_config()
        
        # Initialize paths
        self.log_dir = self.config_dir / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        self.log_file = self.log_dir / f"∂{component_name}.log"
        self.memory_db = self.config_dir / "∂logging_memory.db"
        
        # Session and conversation tracking
        self.session_id = self._generate_session_id()
        self.conversation_id = None
        self.user_id = self.config.get("user_id", "developer")
        
        # Initialize memory systems
        self._init_memory_systems()
        
        # Initialize database
        self._init_database()
        
        # Set up standard logging
        self._setup_standard_logging()
        
        # Pattern analysis
        self.pattern_cache = {}
        self.anomaly_threshold = 0.8
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Log startup
        self.info(f"∂Logger initialized for component: {component_name}")
    
    def _generate_session_id(self) -> str:
        """Generate unique session identifier"""
        return hashlib.md5(f"{datetime.now().isoformat()}_{self.component_name}".encode()).hexdigest()[:12]
    
    def _init_memory_systems(self):
        """Initialize LangMem and fallback SQLite memory systems"""
        global LANGMEM_AVAILABLE
        self.memory_tools = []
        
        if LANGMEM_AVAILABLE:
            try:
                self.store = InMemoryStore(
                    index={"dims": 1536, "embed": "openai:text-embedding-3-small"}
                )
                self.namespace = ("∂logger", self.user_id, self.component_name)
                self.memory_tools = [
                    create_manage_memory_tool(namespace=self.namespace),
                    create_search_memory_tool(namespace=self.namespace),
                ]
            except Exception as e:
                print(f"LangMem initialization failed: {e}")
                LANGMEM_AVAILABLE = False
    
    def _init_database(self):
        """Initialize SQLite database for log storage and analysis"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS log_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    level TEXT NOT NULL,
                    component TEXT NOT NULL,
                    message TEXT NOT NULL,
                    conversation_id TEXT,
                    session_id TEXT,
                    user_id TEXT,
                    context TEXT,
                    correlation_id TEXT,
                    stack_trace TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS log_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    component TEXT NOT NULL,
                    pattern_hash TEXT NOT NULL,
                    pattern_description TEXT NOT NULL,
                    occurrence_count INTEGER DEFAULT 1,
                    confidence_score REAL NOT NULL,
                    first_seen TIMESTAMP NOT NULL,
                    last_seen TIMESTAMP NOT NULL,
                    example_message TEXT,
                    UNIQUE(component, pattern_hash)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    conversation_id TEXT,
                    user_id TEXT NOT NULL,
                    component TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    message_count INTEGER DEFAULT 0,
                    error_count INTEGER DEFAULT 0,
                    warning_count INTEGER DEFAULT 0,
                    UNIQUE(session_id, component)
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_log_timestamp ON log_entries(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_log_component ON log_entries(component)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_log_conversation ON log_entries(conversation_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_log_session ON log_entries(session_id)")
            
            conn.commit()
    
    def _setup_standard_logging(self):
        """Set up standard Python logging integration"""
        self.logger = logging.getLogger(f"∂{self.component_name}")
        self.logger.setLevel(logging.DEBUG)
        
        # Create file handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - ∂%(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def set_conversation_context(self, conversation_id: str, user_id: str = None):
        """Set conversation context for subsequent logs"""
        self.conversation_id = conversation_id
        if user_id:
            self.user_id = user_id
        
        # Record session start
        self._record_session_start()
        
        self.info(f"Conversation context set: {conversation_id}")
    
    def _record_session_start(self):
        """Record session start in database"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO conversation_sessions
                (session_id, conversation_id, user_id, component, start_time)
                VALUES (?, ?, ?, ?, ?)
            """, (self.session_id, self.conversation_id, self.user_id, 
                  self.component_name, datetime.now()))
            conn.commit()
    
    def _log_entry(self, level: LogLevel, message: str, context: Dict[str, Any] = None, 
                   correlation_id: str = None, include_stack: bool = False):
        """Core logging method with conversation awareness"""
        with self._lock:
            # Create log entry
            entry = ConversationLogEntry(
                timestamp=datetime.now(),
                level=level,
                component=self.component_name,
                message=message,
                conversation_id=self.conversation_id,
                session_id=self.session_id,
                user_id=self.user_id,
                context=context,
                correlation_id=correlation_id,
                stack_trace=traceback.format_stack() if include_stack else None
            )
            
            # Store in database
            self._store_log_entry(entry)
            
            # Analyze patterns
            self._analyze_log_pattern(entry)
            
            # Store in LangMem if available
            if LANGMEM_AVAILABLE and self.memory_tools:
                self._store_in_langmem(entry)
            
            # Standard logging
            log_method = getattr(self.logger, level.value.lower(), self.logger.info)
            context_str = f" | Context: {json.dumps(context)}" if context else ""
            correlation_str = f" | Correlation: {correlation_id}" if correlation_id else ""
            
            log_method(f"{message}{context_str}{correlation_str}")
    
    def _store_log_entry(self, entry: ConversationLogEntry):
        """Store log entry in database"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT INTO log_entries
                (timestamp, level, component, message, conversation_id, session_id, 
                 user_id, context, correlation_id, stack_trace)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.timestamp, entry.level.value, entry.component, entry.message,
                entry.conversation_id, entry.session_id, entry.user_id,
                json.dumps(entry.context) if entry.context else None,
                entry.correlation_id, entry.stack_trace
            ))
            
            # Update session stats
            conn.execute("""
                UPDATE conversation_sessions
                SET message_count = message_count + 1,
                    error_count = error_count + CASE WHEN ? = 'ERROR' THEN 1 ELSE 0 END,
                    warning_count = warning_count + CASE WHEN ? = 'WARNING' THEN 1 ELSE 0 END
                WHERE session_id = ? AND component = ?
            """, (entry.level.value, entry.level.value, entry.session_id, entry.component))
            
            conn.commit()
    
    def _analyze_log_pattern(self, entry: ConversationLogEntry):
        """Analyze log entry for patterns and anomalies"""
        # Create pattern hash based on message structure
        pattern_hash = self._create_pattern_hash(entry.message)
        
        # Store/update pattern in database
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO log_patterns
                (component, pattern_hash, pattern_description, occurrence_count,
                 confidence_score, first_seen, last_seen, example_message)
                VALUES (?, ?, ?, 
                        COALESCE((SELECT occurrence_count FROM log_patterns 
                                 WHERE component = ? AND pattern_hash = ?), 0) + 1,
                        ?, 
                        COALESCE((SELECT first_seen FROM log_patterns 
                                 WHERE component = ? AND pattern_hash = ?), ?),
                        ?, ?)
            """, (
                entry.component, pattern_hash, self._describe_pattern(entry.message),
                entry.component, pattern_hash, self._calculate_confidence(entry),
                entry.component, pattern_hash, entry.timestamp,
                entry.timestamp, entry.message
            ))
            conn.commit()
    
    def _create_pattern_hash(self, message: str) -> str:
        """Create hash for message pattern recognition"""
        # Normalize message for pattern matching
        normalized = message.lower()
        
        # Replace numbers and paths with placeholders
        import re
        normalized = re.sub(r'\d+', '<NUM>', normalized)
        normalized = re.sub(r'/[^\s]+', '<PATH>', normalized)
        normalized = re.sub(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', '<UUID>', normalized)
        
        return hashlib.md5(normalized.encode()).hexdigest()[:16]
    
    def _describe_pattern(self, message: str) -> str:
        """Generate human-readable pattern description"""
        if "error" in message.lower():
            return "Error pattern"
        elif "warning" in message.lower():
            return "Warning pattern"
        elif "started" in message.lower() or "initialized" in message.lower():
            return "Initialization pattern"
        elif "completed" in message.lower() or "finished" in message.lower():
            return "Completion pattern"
        else:
            return "General pattern"
    
    def _calculate_confidence(self, entry: ConversationLogEntry) -> float:
        """Calculate confidence score for pattern"""
        base_confidence = 0.5
        
        # Higher confidence for errors and warnings
        if entry.level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            base_confidence += 0.3
        elif entry.level == LogLevel.WARNING:
            base_confidence += 0.2
        
        # Higher confidence for structured context
        if entry.context:
            base_confidence += 0.1
        
        # Higher confidence for conversation context
        if entry.conversation_id:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _store_in_langmem(self, entry: ConversationLogEntry):
        """Store log entry in LangMem for advanced pattern analysis"""
        try:
            memory_content = f"Log: {entry.level.value} - {entry.message}"
            if entry.context:
                memory_content += f" | Context: {json.dumps(entry.context)}"
            
            # This would use LangMem tools in actual implementation
            # For now, just cache for pattern analysis
            self.pattern_cache[entry.timestamp.isoformat()] = entry.to_dict()
            
        except Exception as e:
            self.logger.warning(f"Failed to store in LangMem: {e}")
    
    def debug(self, message: str, context: Dict[str, Any] = None, correlation_id: str = None):
        """Log debug message"""
        self._log_entry(LogLevel.DEBUG, message, context, correlation_id)
    
    def info(self, message: str, context: Dict[str, Any] = None, correlation_id: str = None):
        """Log info message"""
        self._log_entry(LogLevel.INFO, message, context, correlation_id)
    
    def warning(self, message: str, context: Dict[str, Any] = None, correlation_id: str = None):
        """Log warning message"""
        self._log_entry(LogLevel.WARNING, message, context, correlation_id)
    
    def error(self, message: str, context: Dict[str, Any] = None, correlation_id: str = None, 
              include_stack: bool = True):
        """Log error message"""
        self._log_entry(LogLevel.ERROR, message, context, correlation_id, include_stack)
    
    def critical(self, message: str, context: Dict[str, Any] = None, correlation_id: str = None, 
                 include_stack: bool = True):
        """Log critical message"""
        self._log_entry(LogLevel.CRITICAL, message, context, correlation_id, include_stack)
    
    def conversation(self, message: str, context: Dict[str, Any] = None, correlation_id: str = None):
        """Log conversation-specific message"""
        self._log_entry(LogLevel.CONVERSATION, message, context, correlation_id)
    
    def pattern(self, message: str, context: Dict[str, Any] = None, correlation_id: str = None):
        """Log pattern analysis message"""
        self._log_entry(LogLevel.PATTERN, message, context, correlation_id)
    
    def memory(self, message: str, context: Dict[str, Any] = None, correlation_id: str = None):
        """Log memory operation message"""
        self._log_entry(LogLevel.MEMORY, message, context, correlation_id)
    
    def get_conversation_logs(self, conversation_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get logs for specific conversation"""
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT timestamp, level, component, message, context, correlation_id
                FROM log_entries
                WHERE conversation_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (conversation_id, limit))
            
            logs = []
            for row in cursor.fetchall():
                logs.append({
                    "timestamp": row[0],
                    "level": row[1],
                    "component": row[2],
                    "message": row[3],
                    "context": json.loads(row[4]) if row[4] else None,
                    "correlation_id": row[5]
                })
            
            return logs
    
    def get_session_stats(self, session_id: str = None) -> Dict[str, Any]:
        """Get statistics for current or specified session"""
        target_session = session_id or self.session_id
        
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT message_count, error_count, warning_count, start_time
                FROM conversation_sessions
                WHERE session_id = ? AND component = ?
            """, (target_session, self.component_name))
            
            row = cursor.fetchone()
            if row:
                return {
                    "session_id": target_session,
                    "component": self.component_name,
                    "message_count": row[0],
                    "error_count": row[1],
                    "warning_count": row[2],
                    "start_time": row[3],
                    "duration": (datetime.now() - datetime.fromisoformat(row[3])).total_seconds()
                }
            else:
                return {"session_id": target_session, "status": "not_found"}
    
    def get_pattern_analysis(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get pattern analysis for recent logs"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT pattern_description, occurrence_count, confidence_score, 
                       first_seen, last_seen, example_message
                FROM log_patterns
                WHERE component = ? AND last_seen > ?
                ORDER BY occurrence_count DESC, confidence_score DESC
            """, (self.component_name, cutoff_date))
            
            patterns = []
            for row in cursor.fetchall():
                patterns.append({
                    "pattern": row[0],
                    "occurrences": row[1],
                    "confidence": row[2],
                    "first_seen": row[3],
                    "last_seen": row[4],
                    "example": row[5]
                })
            
            return patterns
    
    def detect_anomalies(self, threshold: float = None) -> List[Dict[str, Any]]:
        """Detect anomalous log patterns"""
        threshold = threshold or self.anomaly_threshold
        
        # Simple anomaly detection based on pattern frequency
        patterns = self.get_pattern_analysis(days=1)
        avg_occurrence = sum(p["occurrences"] for p in patterns) / len(patterns) if patterns else 0
        
        anomalies = []
        for pattern in patterns:
            if pattern["occurrences"] > avg_occurrence * 2:  # Significantly higher than average
                anomalies.append({
                    "type": "high_frequency",
                    "pattern": pattern["pattern"],
                    "occurrences": pattern["occurrences"],
                    "average": avg_occurrence,
                    "severity": "medium"
                })
        
        return anomalies
    
    def export_logs(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """Export logs with conversation context"""
        start_date = start_date or (datetime.now() - timedelta(days=7))
        end_date = end_date or datetime.now()
        
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT timestamp, level, component, message, conversation_id, 
                       session_id, user_id, context, correlation_id
                FROM log_entries
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp
            """, (start_date, end_date))
            
            logs = []
            for row in cursor.fetchall():
                logs.append({
                    "timestamp": row[0],
                    "level": row[1],
                    "component": row[2],
                    "message": row[3],
                    "conversation_id": row[4],
                    "session_id": row[5],
                    "user_id": row[6],
                    "context": json.loads(row[7]) if row[7] else None,
                    "correlation_id": row[8]
                })
            
            return {
                "logs": logs,
                "export_info": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "total_entries": len(logs),
                    "component": self.component_name
                }
            }
    
    def cleanup_old_logs(self, days: int = 30):
        """Clean up old log entries"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                DELETE FROM log_entries
                WHERE timestamp < ?
            """, (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            self.info(f"Cleaned up {deleted_count} old log entries")
    
    def close_session(self):
        """Close current session"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                UPDATE conversation_sessions
                SET end_time = ?
                WHERE session_id = ? AND component = ?
            """, (datetime.now(), self.session_id, self.component_name))
            conn.commit()
        
        self.info(f"Session {self.session_id} closed")


# Global logger instances
_loggers = {}


def get_logger(component_name: str, config_dir: str = ".claude") -> DeltaLogger:
    """Get logger instance for component"""
    if component_name not in _loggers:
        _loggers[component_name] = DeltaLogger(component_name, config_dir)
    return _loggers[component_name]


def create_correlation_id() -> str:
    """Create correlation ID for tracking related operations"""
    return hashlib.md5(f"{datetime.now().isoformat()}_{threading.current_thread().ident}".encode()).hexdigest()[:16]


if __name__ == "__main__":
    # Test logging system
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Testing ∂Logger system...")
        
        # Create logger
        logger = get_logger("test_component")
        
        # Set conversation context
        logger.set_conversation_context("test_conversation_001", "test_user")
        
        # Test various log levels
        correlation_id = create_correlation_id()
        
        logger.debug("Debug message", {"key": "value"}, correlation_id)
        logger.info("Info message", {"process": "initialization"}, correlation_id)
        logger.warning("Warning message", {"threshold": "exceeded"}, correlation_id)
        logger.error("Error message", {"error_code": "E001"}, correlation_id)
        logger.conversation("User asked about configuration", {"topic": "config"}, correlation_id)
        
        # Test pattern analysis
        patterns = logger.get_pattern_analysis(days=1)
        print(f"Found {len(patterns)} patterns")
        
        # Test session stats
        stats = logger.get_session_stats()
        print(f"Session stats: {stats}")
        
        # Test anomaly detection
        anomalies = logger.detect_anomalies()
        print(f"Detected {len(anomalies)} anomalies")
        
        # Close session
        logger.close_session()
        
        print("∂Logger system test completed successfully!")
    else:
        print("∂Logger.py - Conversation-aware comprehensive logging")
        print("Usage: python ∂Logger.py --test")