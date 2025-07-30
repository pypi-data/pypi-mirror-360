#!/usr/bin/env python3
"""
∂Claude.py - Claude-specific interface with conversation memory
Part of the ∂-prefixed architecture for conversation-aware multi-agent development

This module provides a specialized interface for Claude interactions with SQLite
session storage, multi-turn conversation tracking, and context-aware prompt construction.
"""

import json
import sqlite3
import hashlib
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List, AsyncIterator
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import re

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

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




# Load ∂Logger module  
from .logger import get_logger





class ConversationState(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ConversationTurn:
    """Single turn in a Claude conversation"""
    turn_id: str
    conversation_id: str
    role: MessageRole
    content: str
    timestamp: datetime
    tokens_used: Optional[int] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    context_window_position: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['role'] = self.role.value
        result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class ConversationSession:
    """Complete conversation session with Claude"""
    session_id: str
    conversation_id: str
    user_id: str
    title: str
    state: ConversationState
    created_at: datetime
    last_updated: datetime
    turns: List[ConversationTurn]
    total_tokens: int = 0
    total_cost: float = 0.0
    context_summary: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['state'] = self.state.value
        result['created_at'] = self.created_at.isoformat()
        result['last_updated'] = self.last_updated.isoformat()
        result['turns'] = [turn.to_dict() for turn in self.turns]
        return result


class ContextManager:
    """Manages context window and conversation memory"""
    
    def __init__(self, max_context_window: int = 200000):
        self.max_context_window = max_context_window
        self.context_buffer_ratio = 0.8  # Use 80% of context window
        self.summary_threshold = 0.6  # Summarize when 60% full
    
    def manage_context(self, turns: List[ConversationTurn], new_content: str = "") -> List[ConversationTurn]:
        """Manage context window by summarizing or truncating old turns"""
        # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
        total_tokens = sum(len(turn.content) // 4 for turn in turns)
        new_tokens = len(new_content) // 4
        
        max_tokens = int(self.max_context_window * self.context_buffer_ratio)
        
        if total_tokens + new_tokens <= max_tokens:
            return turns
        
        # Need to manage context
        if total_tokens + new_tokens > max_tokens * self.summary_threshold:
            return self._summarize_old_context(turns, max_tokens - new_tokens)
        else:
            return self._truncate_old_context(turns, max_tokens - new_tokens)
    
    def _summarize_old_context(self, turns: List[ConversationTurn], target_tokens: int) -> List[ConversationTurn]:
        """Summarize older conversation turns to save context"""
        if not turns:
            return turns
        
        # Keep recent turns, summarize older ones
        recent_turns = []
        recent_tokens = 0
        
        # Work backwards from most recent
        for turn in reversed(turns):
            turn_tokens = len(turn.content) // 4
            if recent_tokens + turn_tokens <= target_tokens * 0.7:  # Reserve 30% for summary
                recent_turns.insert(0, turn)
                recent_tokens += turn_tokens
            else:
                break
        
        # If we need to summarize
        if len(recent_turns) < len(turns):
            older_turns = turns[:len(turns) - len(recent_turns)]
            summary_content = self._create_conversation_summary(older_turns)
            
            summary_turn = ConversationTurn(
                turn_id=f"summary_{datetime.now().timestamp()}",
                conversation_id=turns[0].conversation_id,
                role=MessageRole.SYSTEM,
                content=f"[CONVERSATION SUMMARY] {summary_content}",
                timestamp=older_turns[0].timestamp if older_turns else datetime.now(),
                metadata={"type": "context_summary", "summarized_turns": len(older_turns)}
            )
            
            return [summary_turn] + recent_turns
        
        return recent_turns
    
    def _truncate_old_context(self, turns: List[ConversationTurn], target_tokens: int) -> List[ConversationTurn]:
        """Truncate older turns to fit context window"""
        if not turns:
            return turns
        
        # Keep recent turns within token limit
        kept_turns = []
        total_tokens = 0
        
        for turn in reversed(turns):
            turn_tokens = len(turn.content) // 4
            if total_tokens + turn_tokens <= target_tokens:
                kept_turns.insert(0, turn)
                total_tokens += turn_tokens
            else:
                break
        
        return kept_turns
    
    def _create_conversation_summary(self, turns: List[ConversationTurn]) -> str:
        """Create a summary of conversation turns"""
        if not turns:
            return "No previous conversation"
        
        # Extract key topics and decisions
        user_messages = [turn.content for turn in turns if turn.role == MessageRole.USER]
        assistant_messages = [turn.content for turn in turns if turn.role == MessageRole.ASSISTANT]
        
        # Simple keyword extraction for summary
        all_content = " ".join(user_messages + assistant_messages).lower()
        
        # Extract potential topics (simple approach)
        topics = []
        common_patterns = [
            r'\b(implement|build|create|develop)\s+(\w+)',
            r'\b(fix|debug|solve)\s+(\w+)',
            r'\b(configure|setup|install)\s+(\w+)',
            r'\b(analyze|review|check)\s+(\w+)'
        ]
        
        for pattern in common_patterns:
            matches = re.findall(pattern, all_content)
            topics.extend([f"{action} {obj}" for action, obj in matches[:3]])  # Limit matches
        
        if topics:
            topic_summary = f"Key topics: {', '.join(topics[:5])}"
        else:
            topic_summary = "General development discussion"
        
        return f"Previous conversation ({len(turns)} turns): {topic_summary}. Last update: {turns[-1].timestamp.strftime('%Y-%m-%d %H:%M')}"


class DeltaClaude:
    """
    ∂Claude - Claude-specific interface with conversation memory
    
    Features:
    - SQLite session storage for persistence
    - Multi-turn conversation tracking
    - Context-aware prompt construction
    - Automatic context window management
    - Conversation analytics and insights
    """
    
    def __init__(self, config_dir: str = ".claude", user_id: str = "developer"):
        self.config_dir = Path(config_dir)
        self.user_id = user_id
        self.config = get_config(user_id)
        self.logger = get_logger("∂Claude")
        
        # Initialize memory systems
        self.memory_db = self.config_dir / "∂claude_memory.db"
        self._init_memory_systems()
        self._init_database()
        
        # Initialize Claude client if available
        self.client = None
        self._init_claude_client()
        
        # Context management
        self.context_manager = ContextManager()
        
        # Current session
        self.current_session = None
        self.current_conversation_id = None
        
        # Default model settings
        self.default_model = "claude-3-sonnet-20240229"
        self.default_max_tokens = 1000
        self.default_temperature = 0.7
        
        self.logger.info("∂Claude initialized with conversation memory")
    
    def _init_memory_systems(self):
        """Initialize LangMem and fallback SQLite memory systems"""
        global LANGMEM_AVAILABLE
        self.memory_tools = []
        
        if LANGMEM_AVAILABLE:
            try:
                self.store = InMemoryStore(
                    index={"dims": 1536, "embed": "openai:text-embedding-3-small"}
                )
                self.namespace = ("∂claude", self.user_id)
                self.memory_tools = [
                    create_manage_memory_tool(namespace=self.namespace),
                    create_search_memory_tool(namespace=self.namespace),
                ]
                self.logger.info("LangMem memory system initialized")
            except Exception as e:
                self.logger.warning(f"LangMem initialization failed: {e}")
                LANGMEM_AVAILABLE = False
    
    def _init_database(self):
        """Initialize SQLite database for conversation storage"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    conversation_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    state TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    last_updated TIMESTAMP NOT NULL,
                    total_tokens INTEGER DEFAULT 0,
                    total_cost REAL DEFAULT 0.0,
                    context_summary TEXT,
                    tags TEXT,
                    metadata TEXT,
                    UNIQUE(session_id, user_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    turn_id TEXT NOT NULL,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    tokens_used INTEGER,
                    model TEXT,
                    temperature REAL,
                    context_window_position INTEGER,
                    metadata TEXT,
                    FOREIGN KEY(conversation_id) REFERENCES conversation_sessions(conversation_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    calculated_at TIMESTAMP NOT NULL,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    insight_type TEXT NOT NULL,
                    insight_data TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    generated_at TIMESTAMP NOT NULL
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_conversation_id ON conversation_turns(conversation_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_user ON conversation_sessions(user_id, state)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_turn_timestamp ON conversation_turns(timestamp)")
            
            conn.commit()
    
    def _init_claude_client(self):
        """Initialize Claude API client"""
        if not ANTHROPIC_AVAILABLE:
            self.logger.warning("Anthropic package not available")
            return
        
        api_key = self.config.get("ai_providers.anthropic.api_key")
        if api_key:
            try:
                self.client = anthropic.AsyncAnthropic(api_key=api_key)
                self.logger.info("Claude API client initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Claude client: {e}")
        else:
            self.logger.warning("No Anthropic API key configured")
    
    def start_conversation(self, title: str = None, conversation_id: str = None, 
                          tags: List[str] = None, metadata: Dict[str, Any] = None) -> str:
        """Start a new conversation session"""
        if not conversation_id:
            conversation_id = self._generate_conversation_id()
        
        session_id = self._generate_session_id()
        
        if not title:
            title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Create session
        session = ConversationSession(
            session_id=session_id,
            conversation_id=conversation_id,
            user_id=self.user_id,
            title=title,
            state=ConversationState.ACTIVE,
            created_at=datetime.now(),
            last_updated=datetime.now(),
            turns=[],
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # Store in database
        self._store_session(session)
        
        # Set as current session
        self.current_session = session
        self.current_conversation_id = conversation_id
        
        self.logger.info(f"Started conversation: {conversation_id} with title: {title}")
        return conversation_id
    
    def resume_conversation(self, conversation_id: str) -> bool:
        """Resume an existing conversation"""
        session = self._load_session(conversation_id)
        if session:
            self.current_session = session
            self.current_conversation_id = conversation_id
            self.logger.info(f"Resumed conversation: {conversation_id}")
            return True
        else:
            self.logger.warning(f"Conversation not found: {conversation_id}")
            return False
    
    def add_user_message(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Add user message to current conversation"""
        if not self.current_session:
            raise ValueError("No active conversation. Start a conversation first.")
        
        turn_id = self._generate_turn_id()
        
        turn = ConversationTurn(
            turn_id=turn_id,
            conversation_id=self.current_conversation_id,
            role=MessageRole.USER,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata
        )
        
        self.current_session.turns.append(turn)
        self._store_turn(turn)
        self._update_session_timestamp()
        
        self.logger.debug(f"Added user message: {len(content)} characters")
        return turn_id
    
    async def generate_response(self, prompt: str = None, model: str = None, 
                               max_tokens: int = None, temperature: float = None,
                               system_prompt: str = None) -> str:
        """Generate Claude response with conversation context"""
        if not self.client:
            raise ValueError("Claude client not initialized")
        
        if not self.current_session:
            raise ValueError("No active conversation. Start a conversation first.")
        
        # Use provided prompt or add as user message
        if prompt:
            self.add_user_message(prompt)
        
        # Manage context window
        managed_turns = self.context_manager.manage_context(
            self.current_session.turns, 
            prompt or ""
        )
        
        # Prepare messages for Claude API
        messages = []
        system_message = system_prompt
        
        for turn in managed_turns:
            if turn.role == MessageRole.SYSTEM:
                if not system_message:
                    system_message = turn.content
                # Skip system messages in conversation flow
                continue
            elif turn.role == MessageRole.USER:
                messages.append({"role": "user", "content": turn.content})
            elif turn.role == MessageRole.ASSISTANT:
                messages.append({"role": "assistant", "content": turn.content})
        
        # Set default parameters
        model = model or self.default_model
        max_tokens = max_tokens or self.default_max_tokens
        temperature = temperature or self.default_temperature
        
        try:
            # Make API call to Claude
            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message,
                messages=messages
            )
            
            # Extract response content
            response_content = response.content[0].text
            
            # Create assistant turn
            turn_id = self._generate_turn_id()
            assistant_turn = ConversationTurn(
                turn_id=turn_id,
                conversation_id=self.current_conversation_id,
                role=MessageRole.ASSISTANT,
                content=response_content,
                timestamp=datetime.now(),
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                model=model,
                temperature=temperature,
                metadata={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "stop_reason": response.stop_reason
                }
            )
            
            # Add to session and store
            self.current_session.turns.append(assistant_turn)
            self.current_session.total_tokens += assistant_turn.tokens_used
            self.current_session.total_cost += self._calculate_cost(assistant_turn.tokens_used, model)
            
            self._store_turn(assistant_turn)
            self._update_session_stats()
            
            self.logger.info(f"Generated response: {len(response_content)} characters, {assistant_turn.tokens_used} tokens")
            return response_content
            
        except Exception as e:
            self.logger.error(f"Failed to generate response: {e}")
            raise
    
    async def stream_response(self, prompt: str = None, model: str = None,
                             max_tokens: int = None, temperature: float = None,
                             system_prompt: str = None) -> AsyncIterator[str]:
        """Stream Claude response with conversation context"""
        if not self.client:
            raise ValueError("Claude client not initialized")
        
        if not self.current_session:
            raise ValueError("No active conversation. Start a conversation first.")
        
        # Use provided prompt or add as user message
        if prompt:
            self.add_user_message(prompt)
        
        # Manage context window
        managed_turns = self.context_manager.manage_context(
            self.current_session.turns,
            prompt or ""
        )
        
        # Prepare messages
        messages = []
        system_message = system_prompt
        
        for turn in managed_turns:
            if turn.role == MessageRole.SYSTEM:
                if not system_message:
                    system_message = turn.content
                continue
            elif turn.role == MessageRole.USER:
                messages.append({"role": "user", "content": turn.content})
            elif turn.role == MessageRole.ASSISTANT:
                messages.append({"role": "assistant", "content": turn.content})
        
        # Set default parameters
        model = model or self.default_model
        max_tokens = max_tokens or self.default_max_tokens
        temperature = temperature or self.default_temperature
        
        try:
            full_response = ""
            
            async with self.client.messages.stream(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message,
                messages=messages
            ) as stream:
                async for text in stream.text_stream:
                    full_response += text
                    yield text
            
            # Store complete response
            turn_id = self._generate_turn_id()
            assistant_turn = ConversationTurn(
                turn_id=turn_id,
                conversation_id=self.current_conversation_id,
                role=MessageRole.ASSISTANT,
                content=full_response,
                timestamp=datetime.now(),
                tokens_used=len(full_response) // 4,  # Rough estimate
                model=model,
                temperature=temperature,
                metadata={"streaming": True}
            )
            
            self.current_session.turns.append(assistant_turn)
            self.current_session.total_tokens += assistant_turn.tokens_used
            self.current_session.total_cost += self._calculate_cost(assistant_turn.tokens_used, model)
            
            self._store_turn(assistant_turn)
            self._update_session_stats()
            
            self.logger.info(f"Streamed response completed: {len(full_response)} characters")
            
        except Exception as e:
            self.logger.error(f"Failed to stream response: {e}")
            raise
    
    def add_system_message(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Add system message to conversation"""
        if not self.current_session:
            raise ValueError("No active conversation. Start a conversation first.")
        
        turn_id = self._generate_turn_id()
        
        turn = ConversationTurn(
            turn_id=turn_id,
            conversation_id=self.current_conversation_id,
            role=MessageRole.SYSTEM,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata
        )
        
        self.current_session.turns.append(turn)
        self._store_turn(turn)
        self._update_session_timestamp()
        
        self.logger.debug(f"Added system message: {len(content)} characters")
        return turn_id
    
    def get_conversation_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get conversation history for current session"""
        if not self.current_session:
            return []
        
        turns = self.current_session.turns
        if limit:
            turns = turns[-limit:]
        
        return [turn.to_dict() for turn in turns]
    
    def search_conversations(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search conversations by content"""
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT DISTINCT cs.conversation_id, cs.title, cs.created_at, cs.last_updated
                FROM conversation_sessions cs
                JOIN conversation_turns ct ON cs.conversation_id = ct.conversation_id
                WHERE cs.user_id = ? AND (
                    ct.content LIKE ? OR cs.title LIKE ?
                )
                ORDER BY cs.last_updated DESC
                LIMIT ?
            """, (self.user_id, f"%{query}%", f"%{query}%", limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "conversation_id": row[0],
                    "title": row[1],
                    "created_at": row[2],
                    "last_updated": row[3]
                })
            
            return results
    
    def get_conversation_analytics(self, conversation_id: str = None) -> Dict[str, Any]:
        """Get analytics for conversation"""
        target_id = conversation_id or self.current_conversation_id
        if not target_id:
            return {}
        
        with sqlite3.connect(self.memory_db) as conn:
            # Basic stats
            cursor = conn.execute("""
                SELECT COUNT(*) as turn_count,
                       SUM(CASE WHEN role = 'user' THEN 1 ELSE 0 END) as user_turns,
                       SUM(CASE WHEN role = 'assistant' THEN 1 ELSE 0 END) as assistant_turns,
                       SUM(COALESCE(tokens_used, 0)) as total_tokens,
                       AVG(LENGTH(content)) as avg_message_length
                FROM conversation_turns
                WHERE conversation_id = ?
            """, (target_id,))
            
            row = cursor.fetchone()
            
            analytics = {
                "conversation_id": target_id,
                "turn_count": row[0],
                "user_turns": row[1],
                "assistant_turns": row[2],
                "total_tokens": row[3],
                "avg_message_length": row[4]
            }
            
            # Session info
            cursor = conn.execute("""
                SELECT title, created_at, last_updated, total_cost
                FROM conversation_sessions
                WHERE conversation_id = ? AND user_id = ?
            """, (target_id, self.user_id))
            
            session_row = cursor.fetchone()
            if session_row:
                analytics.update({
                    "title": session_row[0],
                    "duration_minutes": (
                        datetime.fromisoformat(session_row[2]) - 
                        datetime.fromisoformat(session_row[1])
                    ).total_seconds() / 60,
                    "total_cost": session_row[3]
                })
            
            return analytics
    
    def generate_conversation_insights(self, conversation_id: str = None) -> List[Dict[str, Any]]:
        """Generate insights about the conversation"""
        target_id = conversation_id or self.current_conversation_id
        if not target_id:
            return []
        
        insights = []
        
        # Load conversation content
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT role, content, timestamp, tokens_used
                FROM conversation_turns
                WHERE conversation_id = ?
                ORDER BY timestamp
            """, (target_id,))
            
            turns = cursor.fetchall()
        
        if not turns:
            return insights
        
        # Analyze conversation patterns
        user_messages = [turn[1] for turn in turns if turn[0] == 'user']
        assistant_messages = [turn[1] for turn in turns if turn[0] == 'assistant']
        
        # Topic extraction (simple keyword analysis)
        all_content = " ".join(user_messages + assistant_messages).lower()
        
        # Common development topics
        topic_keywords = {
            "web_development": ["web", "html", "css", "javascript", "react", "vue", "angular"],
            "backend": ["api", "server", "database", "backend", "microservice"],
            "data_science": ["data", "analysis", "pandas", "numpy", "visualization"],
            "machine_learning": ["model", "training", "neural", "ai", "prediction"],
            "devops": ["docker", "kubernetes", "deployment", "ci/cd", "infrastructure"]
        }
        
        detected_topics = []
        for topic, keywords in topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in all_content)
            if score > 0:
                detected_topics.append({
                    "topic": topic,
                    "score": score,
                    "confidence": min(score / len(keywords), 1.0)
                })
        
        if detected_topics:
            top_topic = max(detected_topics, key=lambda x: x["score"])
            insights.append({
                "type": "primary_topic",
                "data": top_topic,
                "confidence": top_topic["confidence"],
                "description": f"Primary discussion topic appears to be {top_topic['topic']}"
            })
        
        # Conversation flow analysis
        if len(user_messages) > 0 and len(assistant_messages) > 0:
            avg_user_length = sum(len(msg) for msg in user_messages) / len(user_messages)
            avg_assistant_length = sum(len(msg) for msg in assistant_messages) / len(assistant_messages)
            
            insights.append({
                "type": "conversation_style",
                "data": {
                    "avg_user_message_length": avg_user_length,
                    "avg_assistant_message_length": avg_assistant_length,
                    "interaction_ratio": len(assistant_messages) / len(user_messages)
                },
                "confidence": 0.8,
                "description": f"Conversation style: {'detailed' if avg_user_length > 100 else 'concise'} user messages"
            })
        
        # Store insights
        for insight in insights:
            with sqlite3.connect(self.memory_db) as conn:
                conn.execute("""
                    INSERT INTO conversation_insights
                    (conversation_id, insight_type, insight_data, confidence_score, generated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    target_id, insight["type"], json.dumps(insight["data"]),
                    insight["confidence"], datetime.now()
                ))
                conn.commit()
        
        return insights
    
    def list_conversations(self, limit: int = 20, state: ConversationState = None) -> List[Dict[str, Any]]:
        """List user's conversations"""
        with sqlite3.connect(self.memory_db) as conn:
            if state:
                cursor = conn.execute("""
                    SELECT conversation_id, title, state, created_at, last_updated, total_tokens, total_cost
                    FROM conversation_sessions
                    WHERE user_id = ? AND state = ?
                    ORDER BY last_updated DESC
                    LIMIT ?
                """, (self.user_id, state.value, limit))
            else:
                cursor = conn.execute("""
                    SELECT conversation_id, title, state, created_at, last_updated, total_tokens, total_cost
                    FROM conversation_sessions
                    WHERE user_id = ?
                    ORDER BY last_updated DESC
                    LIMIT ?
                """, (self.user_id, limit))
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append({
                    "conversation_id": row[0],
                    "title": row[1],
                    "state": row[2],
                    "created_at": row[3],
                    "last_updated": row[4],
                    "total_tokens": row[5],
                    "total_cost": row[6]
                })
            
            return conversations
    
    def archive_conversation(self, conversation_id: str = None):
        """Archive a conversation"""
        target_id = conversation_id or self.current_conversation_id
        if not target_id:
            return
        
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                UPDATE conversation_sessions
                SET state = ?, last_updated = ?
                WHERE conversation_id = ? AND user_id = ?
            """, (ConversationState.ARCHIVED.value, datetime.now(), target_id, self.user_id))
            conn.commit()
        
        if target_id == self.current_conversation_id:
            self.current_session = None
            self.current_conversation_id = None
        
        self.logger.info(f"Archived conversation: {target_id}")
    
    def export_conversation(self, conversation_id: str = None, format: str = "json") -> str:
        """Export conversation in specified format"""
        target_id = conversation_id or self.current_conversation_id
        if not target_id:
            return ""
        
        session = self._load_session(target_id)
        if not session:
            return ""
        
        if format == "json":
            return json.dumps(session.to_dict(), indent=2)
        elif format == "markdown":
            return self._export_to_markdown(session)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_to_markdown(self, session: ConversationSession) -> str:
        """Export conversation to markdown format"""
        lines = [
            f"# {session.title}",
            f"",
            f"**Conversation ID:** {session.conversation_id}",
            f"**Created:** {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Last Updated:** {session.last_updated.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Tokens:** {session.total_tokens}",
            f"**Total Cost:** ${session.total_cost:.4f}",
            f"",
            "---",
            f""
        ]
        
        for turn in session.turns:
            if turn.role == MessageRole.USER:
                lines.extend([
                    f"## User ({turn.timestamp.strftime('%H:%M:%S')})",
                    f"",
                    turn.content,
                    f""
                ])
            elif turn.role == MessageRole.ASSISTANT:
                lines.extend([
                    f"## Assistant ({turn.timestamp.strftime('%H:%M:%S')})",
                    f"",
                    turn.content,
                    f""
                ])
            elif turn.role == MessageRole.SYSTEM:
                lines.extend([
                    f"### System Message",
                    f"",
                    f"*{turn.content}*",
                    f""
                ])
        
        return "\n".join(lines)
    
    def _generate_conversation_id(self) -> str:
        """Generate unique conversation ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"{self.user_id}:{timestamp}".encode()).hexdigest()[:16]
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"session:{self.user_id}:{timestamp}".encode()).hexdigest()[:12]
    
    def _generate_turn_id(self) -> str:
        """Generate unique turn ID"""
        timestamp = datetime.now().timestamp()
        return f"turn_{int(timestamp * 1000)}"
    
    def _calculate_cost(self, tokens: int, model: str) -> float:
        """Calculate estimated cost for tokens"""
        # Simplified cost calculation - would use actual pricing
        cost_per_1k_tokens = {
            "claude-3-opus-20240229": 0.015,
            "claude-3-sonnet-20240229": 0.003,
            "claude-3-haiku-20240307": 0.00025
        }
        
        rate = cost_per_1k_tokens.get(model, 0.003)
        return (tokens / 1000) * rate
    
    def _store_session(self, session: ConversationSession):
        """Store session in database"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO conversation_sessions
                (session_id, conversation_id, user_id, title, state, created_at, 
                 last_updated, total_tokens, total_cost, context_summary, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_id, session.conversation_id, session.user_id,
                session.title, session.state.value, session.created_at,
                session.last_updated, session.total_tokens, session.total_cost,
                session.context_summary, json.dumps(session.tags) if session.tags else None,
                json.dumps(session.metadata) if session.metadata else None
            ))
            conn.commit()
    
    def _store_turn(self, turn: ConversationTurn):
        """Store turn in database"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT INTO conversation_turns
                (turn_id, conversation_id, role, content, timestamp, tokens_used,
                 model, temperature, context_window_position, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                turn.turn_id, turn.conversation_id, turn.role.value, turn.content,
                turn.timestamp, turn.tokens_used, turn.model, turn.temperature,
                turn.context_window_position, json.dumps(turn.metadata) if turn.metadata else None
            ))
            conn.commit()
    
    def _load_session(self, conversation_id: str) -> Optional[ConversationSession]:
        """Load session from database"""
        with sqlite3.connect(self.memory_db) as conn:
            # Load session data
            cursor = conn.execute("""
                SELECT session_id, conversation_id, user_id, title, state, created_at,
                       last_updated, total_tokens, total_cost, context_summary, tags, metadata
                FROM conversation_sessions
                WHERE conversation_id = ? AND user_id = ?
            """, (conversation_id, self.user_id))
            
            session_row = cursor.fetchone()
            if not session_row:
                return None
            
            # Load turns
            cursor = conn.execute("""
                SELECT turn_id, conversation_id, role, content, timestamp, tokens_used,
                       model, temperature, context_window_position, metadata
                FROM conversation_turns
                WHERE conversation_id = ?
                ORDER BY timestamp
            """, (conversation_id,))
            
            turns = []
            for turn_row in cursor.fetchall():
                turn = ConversationTurn(
                    turn_id=turn_row[0],
                    conversation_id=turn_row[1],
                    role=MessageRole(turn_row[2]),
                    content=turn_row[3],
                    timestamp=datetime.fromisoformat(turn_row[4]),
                    tokens_used=turn_row[5],
                    model=turn_row[6],
                    temperature=turn_row[7],
                    context_window_position=turn_row[8],
                    metadata=json.loads(turn_row[9]) if turn_row[9] else None
                )
                turns.append(turn)
            
            # Create session object
            session = ConversationSession(
                session_id=session_row[0],
                conversation_id=session_row[1],
                user_id=session_row[2],
                title=session_row[3],
                state=ConversationState(session_row[4]),
                created_at=datetime.fromisoformat(session_row[5]),
                last_updated=datetime.fromisoformat(session_row[6]),
                turns=turns,
                total_tokens=session_row[7],
                total_cost=session_row[8],
                context_summary=session_row[9],
                tags=json.loads(session_row[10]) if session_row[10] else [],
                metadata=json.loads(session_row[11]) if session_row[11] else {}
            )
            
            return session
    
    def _update_session_timestamp(self):
        """Update session last updated timestamp"""
        if not self.current_session:
            return
        
        self.current_session.last_updated = datetime.now()
        
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                UPDATE conversation_sessions
                SET last_updated = ?
                WHERE conversation_id = ? AND user_id = ?
            """, (self.current_session.last_updated, self.current_conversation_id, self.user_id))
            conn.commit()
    
    def _update_session_stats(self):
        """Update session statistics"""
        if not self.current_session:
            return
        
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                UPDATE conversation_sessions
                SET total_tokens = ?, total_cost = ?, last_updated = ?
                WHERE conversation_id = ? AND user_id = ?
            """, (
                self.current_session.total_tokens, self.current_session.total_cost,
                datetime.now(), self.current_conversation_id, self.user_id
            ))
            conn.commit()


# Global Claude instance
_global_claude = None


def get_claude(user_id: str = "developer") -> DeltaClaude:
    """Get global Claude instance"""
    global _global_claude
    if _global_claude is None:
        _global_claude = DeltaClaude(user_id=user_id)
    return _global_claude


def initialize_claude(config_dir: str = ".claude", user_id: str = "developer") -> DeltaClaude:
    """Initialize Claude conversation system"""
    global _global_claude
    _global_claude = DeltaClaude(config_dir=config_dir, user_id=user_id)
    return _global_claude


if __name__ == "__main__":
    # Test Claude conversation system
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Testing ∂Claude system...")
        
        # Initialize Claude system
        claude = initialize_claude()
        
        # Start a conversation
        conversation_id = claude.start_conversation(
            title="Test Conversation",
            tags=["test", "development"]
        )
        print(f"Started conversation: {conversation_id}")
        
        # Add user message
        claude.add_user_message("Hello, can you help me with Python development?")
        
        # Add system message
        claude.add_system_message("User is working on a Python development project")
        
        # Get conversation history
        history = claude.get_conversation_history()
        print(f"Conversation history: {len(history)} turns")
        
        # Get analytics
        analytics = claude.get_conversation_analytics()
        print(f"Analytics: {analytics}")
        
        # Generate insights
        insights = claude.generate_conversation_insights()
        print(f"Generated {len(insights)} insights")
        
        # List conversations
        conversations = claude.list_conversations(limit=5)
        print(f"Found {len(conversations)} conversations")
        
        # Export conversation
        export_data = claude.export_conversation(format="json")
        print(f"Exported conversation: {len(export_data)} characters")
        
        # Archive conversation
        claude.archive_conversation()
        print("Conversation archived")
        
        print("∂Claude system test completed successfully!")
    else:
        print("∂Claude.py - Claude-specific interface with conversation memory")
        print("Usage: python ∂Claude.py --test")