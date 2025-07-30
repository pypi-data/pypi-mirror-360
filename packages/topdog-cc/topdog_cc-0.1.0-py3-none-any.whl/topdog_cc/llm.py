#!/usr/bin/env python3
"""
∂LLM.py - Multi-provider LLM interface with memory
Part of the ∂-prefixed architecture for conversation-aware multi-agent development

This module provides a unified interface for multiple LLM providers with conversation
persistence, context window management, and learning from interaction patterns.
"""

import json
import asyncio
import time
import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, AsyncIterator
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import re

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

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





class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"


@dataclass
class LLMMessage:
    """Structured message for LLM conversations"""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime
    provider: LLMProvider
    model: str
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class LLMResponse:
    """Structured response from LLM"""
    content: str
    provider: LLMProvider
    model: str
    tokens_used: int
    cost: float
    latency: float
    metadata: Dict[str, Any]
    finish_reason: str


class LLMProviderInterface(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate_response(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Generate response from messages"""
        pass
    
    @abstractmethod
    async def stream_response(self, messages: List[LLMMessage], **kwargs) -> AsyncIterator[str]:
        """Stream response from messages"""
        pass
    
    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        pass
    
    @abstractmethod
    def get_context_window(self) -> int:
        """Get maximum context window size"""
        pass


class OpenAIProvider(LLMProviderInterface):
    """OpenAI provider implementation"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not available")
        
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model
        self.provider = LLMProvider.OPENAI
    
    async def generate_response(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Generate response using OpenAI API"""
        start_time = time.time()
        
        # Convert messages to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                **kwargs
            )
            
            latency = time.time() - start_time
            
            return LLMResponse(
                content=response.choices[0].message.content,
                provider=self.provider,
                model=self.model,
                tokens_used=response.usage.total_tokens,
                cost=self._calculate_cost(response.usage.total_tokens),
                latency=latency,
                metadata={"response_id": response.id},
                finish_reason=response.choices[0].finish_reason
            )
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def stream_response(self, messages: List[LLMMessage], **kwargs) -> AsyncIterator[str]:
        """Stream response using OpenAI API"""
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                stream=True,
                **kwargs
            )
            
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise Exception(f"OpenAI streaming error: {str(e)}")
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count using simple heuristic"""
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def get_context_window(self) -> int:
        """Get context window for model"""
        context_windows = {
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-16k": 16384
        }
        return context_windows.get(self.model, 8192)
    
    def _calculate_cost(self, tokens: int) -> float:
        """Calculate cost based on token usage"""
        # Simplified cost calculation (would need actual pricing)
        cost_per_1k_tokens = 0.002  # Example rate
        return (tokens / 1000) * cost_per_1k_tokens


class AnthropicProvider(LLMProviderInterface):
    """Anthropic provider implementation"""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic package not available")
        
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model
        self.provider = LLMProvider.ANTHROPIC
    
    async def generate_response(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Generate response using Anthropic API"""
        start_time = time.time()
        
        # Convert messages to Anthropic format
        system_message = None
        anthropic_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 1000),
                messages=anthropic_messages,
                system=system_message,
                **{k: v for k, v in kwargs.items() if k != "max_tokens"}
            )
            
            latency = time.time() - start_time
            
            return LLMResponse(
                content=response.content[0].text,
                provider=self.provider,
                model=self.model,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                cost=self._calculate_cost(response.usage.input_tokens + response.usage.output_tokens),
                latency=latency,
                metadata={"response_id": response.id},
                finish_reason=response.stop_reason
            )
            
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
    
    async def stream_response(self, messages: List[LLMMessage], **kwargs) -> AsyncIterator[str]:
        """Stream response using Anthropic API"""
        system_message = None
        anthropic_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        try:
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 1000),
                messages=anthropic_messages,
                system=system_message
            ) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            raise Exception(f"Anthropic streaming error: {str(e)}")
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count using simple heuristic"""
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def get_context_window(self) -> int:
        """Get context window for model"""
        context_windows = {
            "claude-3-sonnet-20240229": 200000,
            "claude-3-opus-20240229": 200000,
            "claude-3-haiku-20240307": 200000
        }
        return context_windows.get(self.model, 200000)
    
    def _calculate_cost(self, tokens: int) -> float:
        """Calculate cost based on token usage"""
        # Simplified cost calculation (would need actual pricing)
        cost_per_1k_tokens = 0.003  # Example rate
        return (tokens / 1000) * cost_per_1k_tokens


class DeltaLLM:
    """
    ∂LLM - Multi-provider LLM interface with memory
    
    Features:
    - Provider abstraction (OpenAI, Anthropic, Google, local models)
    - Conversation persistence using Agno/DSPy patterns
    - Context window management and truncation
    - Learning from interaction patterns
    - Cost and performance tracking
    """
    
    def __init__(self, config_dir: str = ".claude", user_id: str = "developer"):
        self.config_dir = Path(config_dir)
        self.user_id = user_id
        self.config = get_config(user_id)
        self.logger = get_logger("∂LLM")
        
        # Initialize memory systems
        self.memory_db = self.config_dir / "∂llm_memory.db"
        self._init_memory_systems()
        self._init_database()
        
        # Initialize providers
        self.providers = {}
        self._init_providers()
        
        # Conversation state
        self.conversation_id = None
        self.conversation_messages = []
        self.conversation_metadata = {}
        
        # Performance tracking
        self.performance_stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "average_latency": 0.0
        }
        
        self.logger.info("∂LLM initialized with available providers")
    
    def _init_memory_systems(self):
        """Initialize LangMem and fallback SQLite memory systems"""
        global LANGMEM_AVAILABLE
        self.memory_tools = []
        
        if LANGMEM_AVAILABLE:
            try:
                self.store = InMemoryStore(
                    index={"dims": 1536, "embed": "openai:text-embedding-3-small"}
                )
                self.namespace = ("∂llm", self.user_id)
                self.memory_tools = [
                    create_manage_memory_tool(namespace=self.namespace),
                    create_search_memory_tool(namespace=self.namespace),
                ]
                self.logger.info("LangMem memory system initialized")
            except Exception as e:
                self.logger.warning(f"LangMem initialization failed: {e}")
                LANGMEM_AVAILABLE = False
    
    def _init_database(self):
        """Initialize SQLite database for conversation persistence"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    last_updated TIMESTAMP NOT NULL,
                    message_count INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    total_cost REAL DEFAULT 0.0,
                    metadata TEXT,
                    UNIQUE(conversation_id, user_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    tokens_used INTEGER,
                    cost REAL,
                    metadata TEXT,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(conversation_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS provider_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    tokens_used INTEGER NOT NULL,
                    cost REAL NOT NULL,
                    latency REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    error_message TEXT
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_conversation_id ON messages(conversation_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_provider_perf ON provider_performance(provider, model)")
            
            conn.commit()
    
    def _init_providers(self):
        """Initialize available LLM providers"""
        # OpenAI
        if OPENAI_AVAILABLE:
            openai_key = self.config.get("ai_providers.openai.api_key")
            if openai_key:
                try:
                    self.providers[LLMProvider.OPENAI] = OpenAIProvider(
                        api_key=openai_key,
                        model=self.config.get("ai_providers.openai.model", "gpt-4")
                    )
                    self.logger.info("OpenAI provider initialized")
                except Exception as e:
                    self.logger.warning(f"OpenAI provider initialization failed: {e}")
        
        # Anthropic
        if ANTHROPIC_AVAILABLE:
            anthropic_key = self.config.get("ai_providers.anthropic.api_key")
            if anthropic_key:
                try:
                    self.providers[LLMProvider.ANTHROPIC] = AnthropicProvider(
                        api_key=anthropic_key,
                        model=self.config.get("ai_providers.anthropic.model", "claude-3-sonnet-20240229")
                    )
                    self.logger.info("Anthropic provider initialized")
                except Exception as e:
                    self.logger.warning(f"Anthropic provider initialization failed: {e}")
        
        # Set primary provider
        primary_provider = self.config.get("ai_providers.primary", "anthropic")
        if primary_provider == "openai" and LLMProvider.OPENAI in self.providers:
            self.primary_provider = LLMProvider.OPENAI
        elif primary_provider == "anthropic" and LLMProvider.ANTHROPIC in self.providers:
            self.primary_provider = LLMProvider.ANTHROPIC
        else:
            # Use first available provider
            self.primary_provider = next(iter(self.providers.keys())) if self.providers else None
        
        if not self.primary_provider:
            self.logger.warning("No LLM providers available")
    
    def start_conversation(self, conversation_id: str, metadata: Dict[str, Any] = None):
        """Start a new conversation or resume existing one"""
        self.conversation_id = conversation_id
        self.conversation_metadata = metadata or {}
        self.conversation_messages = []
        
        # Load existing conversation if it exists
        self._load_conversation()
        
        # Create conversation record if new
        if not self.conversation_messages:
            self._create_conversation()
        
        self.logger.conversation(
            f"Started conversation: {conversation_id}",
            {"metadata": self.conversation_metadata}
        )
    
    def _load_conversation(self):
        """Load existing conversation from database"""
        with sqlite3.connect(self.memory_db) as conn:
            # Load conversation metadata
            cursor = conn.execute("""
                SELECT metadata FROM conversations
                WHERE conversation_id = ? AND user_id = ?
            """, (self.conversation_id, self.user_id))
            
            row = cursor.fetchone()
            if row and row[0]:
                self.conversation_metadata.update(json.loads(row[0]))
            
            # Load messages
            cursor = conn.execute("""
                SELECT role, content, timestamp, provider, model, tokens_used, cost, metadata
                FROM messages
                WHERE conversation_id = ?
                ORDER BY timestamp
            """, (self.conversation_id,))
            
            for row in cursor.fetchall():
                message = LLMMessage(
                    role=row[0],
                    content=row[1],
                    timestamp=datetime.fromisoformat(row[2]),
                    provider=LLMProvider(row[3]),
                    model=row[4],
                    tokens_used=row[5],
                    cost=row[6],
                    metadata=json.loads(row[7]) if row[7] else None
                )
                self.conversation_messages.append(message)
    
    def _create_conversation(self):
        """Create new conversation record"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO conversations
                (conversation_id, user_id, created_at, last_updated, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                self.conversation_id, self.user_id, datetime.now(),
                datetime.now(), json.dumps(self.conversation_metadata)
            ))
            conn.commit()
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add message to conversation"""
        message = LLMMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            provider=self.primary_provider,
            model="",  # Will be set when response is generated
            metadata=metadata
        )
        
        self.conversation_messages.append(message)
        self._store_message(message)
        
        self.logger.conversation(
            f"Added {role} message to conversation",
            {"length": len(content), "metadata": metadata}
        )
    
    def _store_message(self, message: LLMMessage):
        """Store message in database"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT INTO messages
                (conversation_id, role, content, timestamp, provider, model, 
                 tokens_used, cost, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.conversation_id, message.role, message.content,
                message.timestamp, message.provider.value if message.provider else "",
                message.model, message.tokens_used, message.cost,
                json.dumps(message.metadata) if message.metadata else None
            ))
            
            # Update conversation stats
            conn.execute("""
                UPDATE conversations
                SET message_count = message_count + 1,
                    last_updated = ?,
                    total_tokens = total_tokens + COALESCE(?, 0),
                    total_cost = total_cost + COALESCE(?, 0.0)
                WHERE conversation_id = ? AND user_id = ?
            """, (
                datetime.now(), message.tokens_used or 0, message.cost or 0.0,
                self.conversation_id, self.user_id
            ))
            
            conn.commit()
    
    async def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response using primary provider"""
        if not self.primary_provider or self.primary_provider not in self.providers:
            raise ValueError("No primary provider available")
        
        # Add user message
        self.add_message("user", prompt)
        
        # Manage context window
        managed_messages = self._manage_context_window()
        
        # Generate response
        provider = self.providers[self.primary_provider]
        
        try:
            response = await provider.generate_response(managed_messages, **kwargs)
            
            # Add assistant message
            assistant_message = LLMMessage(
                role="assistant",
                content=response.content,
                timestamp=datetime.now(),
                provider=response.provider,
                model=response.model,
                tokens_used=response.tokens_used,
                cost=response.cost,
                metadata=response.metadata
            )
            
            self.conversation_messages.append(assistant_message)
            self._store_message(assistant_message)
            
            # Update performance stats
            self._update_performance_stats(response)
            
            # Store performance data
            self._store_performance_data(response, True)
            
            self.logger.info(
                f"Generated response using {response.provider.value}",
                {
                    "model": response.model,
                    "tokens": response.tokens_used,
                    "cost": response.cost,
                    "latency": response.latency
                }
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Response generation failed: {str(e)}")
            self._store_performance_data(None, False, str(e))
            raise
    
    async def stream_response(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream response using primary provider"""
        if not self.primary_provider or self.primary_provider not in self.providers:
            raise ValueError("No primary provider available")
        
        # Add user message
        self.add_message("user", prompt)
        
        # Manage context window
        managed_messages = self._manage_context_window()
        
        # Stream response
        provider = self.providers[self.primary_provider]
        
        try:
            full_response = ""
            async for chunk in provider.stream_response(managed_messages, **kwargs):
                full_response += chunk
                yield chunk
            
            # Add complete assistant message
            assistant_message = LLMMessage(
                role="assistant",
                content=full_response,
                timestamp=datetime.now(),
                provider=self.primary_provider,
                model=provider.model,
                tokens_used=provider.estimate_tokens(full_response),
                cost=provider._calculate_cost(provider.estimate_tokens(full_response)),
            )
            
            self.conversation_messages.append(assistant_message)
            self._store_message(assistant_message)
            
            self.logger.info(
                f"Streamed response using {self.primary_provider.value}",
                {"tokens": assistant_message.tokens_used}
            )
            
        except Exception as e:
            self.logger.error(f"Response streaming failed: {str(e)}")
            raise
    
    def _manage_context_window(self) -> List[LLMMessage]:
        """Manage context window by truncating old messages if needed"""
        if not self.primary_provider or self.primary_provider not in self.providers:
            return self.conversation_messages
        
        provider = self.providers[self.primary_provider]
        max_context = provider.get_context_window()
        
        # Estimate total tokens
        total_tokens = sum(
            provider.estimate_tokens(msg.content)
            for msg in self.conversation_messages
        )
        
        # If within limit, return all messages
        if total_tokens <= max_context * 0.8:  # Leave 20% buffer
            return self.conversation_messages
        
        # Truncate old messages, keeping system messages and recent context
        managed_messages = []
        token_count = 0
        
        # Keep system messages
        for msg in self.conversation_messages:
            if msg.role == "system":
                managed_messages.append(msg)
                token_count += provider.estimate_tokens(msg.content)
        
        # Keep recent messages within context window
        recent_messages = []
        for msg in reversed(self.conversation_messages):
            if msg.role != "system":
                msg_tokens = provider.estimate_tokens(msg.content)
                if token_count + msg_tokens <= max_context * 0.8:
                    recent_messages.insert(0, msg)
                    token_count += msg_tokens
                else:
                    break
        
        managed_messages.extend(recent_messages)
        
        if len(managed_messages) < len(self.conversation_messages):
            self.logger.warning(
                f"Truncated conversation: {len(self.conversation_messages)} -> {len(managed_messages)} messages",
                {"estimated_tokens": token_count, "max_context": max_context}
            )
        
        return managed_messages
    
    def _update_performance_stats(self, response: LLMResponse):
        """Update performance statistics"""
        self.performance_stats["total_requests"] += 1
        self.performance_stats["total_tokens"] += response.tokens_used
        self.performance_stats["total_cost"] += response.cost
        
        # Update average latency
        old_avg = self.performance_stats["average_latency"]
        count = self.performance_stats["total_requests"]
        self.performance_stats["average_latency"] = (
            (old_avg * (count - 1) + response.latency) / count
        )
    
    def _store_performance_data(self, response: LLMResponse = None, success: bool = True, error: str = None):
        """Store performance data in database"""
        if not self.primary_provider:
            return
        
        provider = self.providers[self.primary_provider]
        
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT INTO provider_performance
                (provider, model, timestamp, tokens_used, cost, latency, success, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.primary_provider.value,
                provider.model,
                datetime.now(),
                response.tokens_used if response else 0,
                response.cost if response else 0.0,
                response.latency if response else 0.0,
                success,
                error
            ))
            conn.commit()
    
    def get_conversation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history"""
        messages = self.conversation_messages[-limit:] if limit else self.conversation_messages
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "provider": msg.provider.value if msg.provider else None,
                "model": msg.model,
                "tokens_used": msg.tokens_used,
                "cost": msg.cost
            }
            for msg in messages
        ]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            **self.performance_stats,
            "primary_provider": self.primary_provider.value if self.primary_provider else None,
            "available_providers": [p.value for p in self.providers.keys()]
        }
    
    def get_provider_performance(self, days: int = 7) -> Dict[str, Any]:
        """Get provider performance analysis"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT provider, model, 
                       COUNT(*) as total_requests,
                       SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_requests,
                       AVG(latency) as avg_latency,
                       SUM(tokens_used) as total_tokens,
                       SUM(cost) as total_cost
                FROM provider_performance
                WHERE timestamp > ?
                GROUP BY provider, model
                ORDER BY total_requests DESC
            """, (cutoff_date,))
            
            results = {}
            for row in cursor.fetchall():
                provider_key = f"{row[0]}:{row[1]}"
                results[provider_key] = {
                    "total_requests": row[2],
                    "successful_requests": row[3],
                    "success_rate": row[3] / row[2] if row[2] > 0 else 0,
                    "average_latency": row[4],
                    "total_tokens": row[5],
                    "total_cost": row[6]
                }
            
            return results
    
    def switch_provider(self, provider: LLMProvider):
        """Switch to different provider"""
        if provider in self.providers:
            self.primary_provider = provider
            self.logger.info(f"Switched to provider: {provider.value}")
        else:
            self.logger.warning(f"Provider not available: {provider.value}")
    
    def export_conversation(self, conversation_id: str = None) -> Dict[str, Any]:
        """Export conversation data"""
        target_id = conversation_id or self.conversation_id
        
        with sqlite3.connect(self.memory_db) as conn:
            # Get conversation metadata
            cursor = conn.execute("""
                SELECT created_at, last_updated, message_count, total_tokens, total_cost, metadata
                FROM conversations
                WHERE conversation_id = ? AND user_id = ?
            """, (target_id, self.user_id))
            
            conv_row = cursor.fetchone()
            if not conv_row:
                return {"error": "Conversation not found"}
            
            # Get messages
            cursor = conn.execute("""
                SELECT role, content, timestamp, provider, model, tokens_used, cost, metadata
                FROM messages
                WHERE conversation_id = ?
                ORDER BY timestamp
            """, (target_id,))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    "role": row[0],
                    "content": row[1],
                    "timestamp": row[2],
                    "provider": row[3],
                    "model": row[4],
                    "tokens_used": row[5],
                    "cost": row[6],
                    "metadata": json.loads(row[7]) if row[7] else None
                })
            
            return {
                "conversation_id": target_id,
                "created_at": conv_row[0],
                "last_updated": conv_row[1],
                "message_count": conv_row[2],
                "total_tokens": conv_row[3],
                "total_cost": conv_row[4],
                "metadata": json.loads(conv_row[5]) if conv_row[5] else None,
                "messages": messages
            }


# Global LLM instance
_global_llm = None


def get_llm(user_id: str = "developer") -> DeltaLLM:
    """Get global LLM instance"""
    global _global_llm
    if _global_llm is None:
        _global_llm = DeltaLLM(user_id=user_id)
    return _global_llm


def initialize_llm(config_dir: str = ".claude", user_id: str = "developer") -> DeltaLLM:
    """Initialize LLM system"""
    global _global_llm
    _global_llm = DeltaLLM(config_dir=config_dir, user_id=user_id)
    return _global_llm


if __name__ == "__main__":
    # Test LLM system
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Testing ∂LLM system...")
        
        # Initialize LLM
        llm = initialize_llm()
        
        # Test conversation
        llm.start_conversation("test_conversation_001")
        
        # Test message addition
        llm.add_message("user", "Hello, how are you?")
        
        # Test conversation history
        history = llm.get_conversation_history()
        print(f"Conversation history: {len(history)} messages")
        
        # Test performance stats
        stats = llm.get_performance_stats()
        print(f"Performance stats: {stats}")
        
        # Test provider performance
        perf = llm.get_provider_performance()
        print(f"Provider performance: {perf}")
        
        # Test export
        export_data = llm.export_conversation()
        print(f"Exported conversation with {len(export_data.get('messages', []))} messages")
        
        print("∂LLM system test completed successfully!")
    else:
        print("∂LLM.py - Multi-provider LLM interface with memory")
        print("Usage: python ∂LLM.py --test")