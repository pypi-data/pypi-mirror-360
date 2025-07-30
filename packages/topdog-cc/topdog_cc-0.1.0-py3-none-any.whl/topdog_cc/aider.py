#!/usr/bin/env python3
"""
∂Aider.py - Context-persistent code interface
Part of the ∂-prefixed architecture for conversation-aware multi-agent development

This module provides a context-persistent interface to Aider with session continuity
across code iterations, file change tracking with conversation context, and learning
from previous fix attempts.
"""

import json
import os
import sqlite3
import subprocess
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import re
import tempfile

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





class AiderOperation(Enum):
    CODE_EDIT = "code_edit"
    FILE_CREATE = "file_create"
    FILE_DELETE = "file_delete"
    REFACTOR = "refactor"
    BUG_FIX = "bug_fix"
    FEATURE_ADD = "feature_add"
    TEST_CREATE = "test_create"
    DOCUMENTATION = "documentation"


class OperationStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERTED = "reverted"


@dataclass
class FileChange:
    """Represents a single file change"""
    file_path: str
    operation_type: str
    lines_added: int
    lines_removed: int
    content_before: Optional[str] = None
    content_after: Optional[str] = None
    diff: Optional[str] = None


@dataclass
class AiderSession:
    """Represents an Aider coding session"""
    session_id: str
    conversation_id: str
    operation_type: AiderOperation
    prompt: str
    status: OperationStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    files_changed: List[FileChange] = None
    aider_output: Optional[str] = None
    error_message: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.files_changed is None:
            self.files_changed = []
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['operation_type'] = self.operation_type.value
        result['status'] = self.status.value
        result['created_at'] = self.created_at.isoformat()
        result['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        return result


class AiderInterface:
    """Interface to Aider command-line tool"""
    
    def __init__(self, project_path: str, aider_path: str = "aider"):
        self.project_path = Path(project_path)
        self.aider_path = aider_path
        self.logger = get_logger("AiderInterface")
    
    def check_aider_available(self) -> bool:
        """Check if Aider is available in the system"""
        try:
            result = subprocess.run(
                [self.aider_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.warning(f"Aider not available: {e}")
            return False
    
    def execute_aider_command(self, prompt: str, files: List[str] = None, 
                             model: str = None, additional_args: List[str] = None) -> Tuple[bool, str, str]:
        """Execute Aider command with given parameters"""
        if not self.check_aider_available():
            return False, "", "Aider is not available"
        
        # Build command
        cmd = [self.aider_path]
        
        # Add model if specified
        if model:
            cmd.extend(["--model", model])
        
        # Add files to edit
        if files:
            cmd.extend(files)
        
        # Add additional arguments
        if additional_args:
            cmd.extend(additional_args)
        
        # Add message
        cmd.extend(["--message", prompt])
        
        # Add auto-accept for non-interactive mode
        cmd.append("--yes")
        
        try:
            # Execute in project directory
            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            success = result.returncode == 0
            stdout = result.stdout
            stderr = result.stderr
            
            self.logger.info(f"Aider command {'succeeded' if success else 'failed'}")
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            self.logger.error("Aider command timed out")
            return False, "", "Command timed out"
        except Exception as e:
            self.logger.error(f"Aider command failed: {e}")
            return False, "", str(e)
    
    def get_git_diff(self, commit_range: str = "HEAD~1..HEAD") -> str:
        """Get git diff for recent changes"""
        try:
            result = subprocess.run(
                ["git", "diff", commit_range],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return ""
        except Exception as e:
            self.logger.warning(f"Failed to get git diff: {e}")
            return ""
    
    def get_file_changes_from_git(self, commit_range: str = "HEAD~1..HEAD") -> List[FileChange]:
        """Extract file changes from git diff"""
        diff_output = self.get_git_diff(commit_range)
        if not diff_output:
            return []
        
        changes = []
        current_file = None
        lines_added = 0
        lines_removed = 0
        
        for line in diff_output.split('\n'):
            if line.startswith('diff --git'):
                # Save previous file if exists
                if current_file:
                    changes.append(FileChange(
                        file_path=current_file,
                        operation_type="modified",
                        lines_added=lines_added,
                        lines_removed=lines_removed,
                        diff=diff_output  # Could extract per-file diff
                    ))
                
                # Start new file
                parts = line.split()
                if len(parts) >= 4:
                    current_file = parts[3][2:]  # Remove 'b/' prefix
                lines_added = 0
                lines_removed = 0
                
            elif line.startswith('+') and not line.startswith('+++'):
                lines_added += 1
            elif line.startswith('-') and not line.startswith('---'):
                lines_removed += 1
        
        # Save last file
        if current_file:
            changes.append(FileChange(
                file_path=current_file,
                operation_type="modified",
                lines_added=lines_added,
                lines_removed=lines_removed,
                diff=diff_output
            ))
        
        return changes


class DeltaAider:
    """
    ∂Aider - Context-persistent code interface
    
    Features:
    - Session continuity across code iterations
    - File change tracking with conversation context
    - Learning from previous fix attempts
    - Integration with ∂-prefixed memory systems
    """
    
    def __init__(self, project_path: str = ".", config_dir: str = ".claude", user_id: str = "developer"):
        self.project_path = Path(project_path).resolve()
        self.config_dir = Path(config_dir)
        self.user_id = user_id
        self.config = get_config(user_id)
        self.logger = get_logger("∂Aider")
        
        # Initialize memory systems
        self.memory_db = self.config_dir / "∂aider_memory.db"
        self._init_memory_systems()
        self._init_database()
        
        # Initialize Aider interface
        aider_path = self.config.get("tools.aider.path", "aider")
        self.aider_interface = AiderInterface(self.project_path, aider_path)
        
        # Session tracking
        self.current_session = None
        self.session_history = []
        
        # Learning parameters
        self.success_patterns = {}
        self.failure_patterns = {}
        
        # Default Aider settings
        self.default_model = self.config.get("tools.aider.model", "gpt-4")
        self.auto_commit = self.config.get("tools.aider.auto_commit", True)
        
        self.logger.info(f"∂Aider initialized for project: {self.project_path}")
    
    def _init_memory_systems(self):
        """Initialize LangMem and fallback SQLite memory systems"""
        global LANGMEM_AVAILABLE
        self.memory_tools = []
        
        if LANGMEM_AVAILABLE:
            try:
                self.store = InMemoryStore(
                    index={"dims": 1536, "embed": "openai:text-embedding-3-small"}
                )
                self.namespace = ("∂aider", self.user_id)
                self.memory_tools = [
                    create_manage_memory_tool(namespace=self.namespace),
                    create_search_memory_tool(namespace=self.namespace),
                ]
                self.logger.info("LangMem memory system initialized")
            except Exception as e:
                self.logger.warning(f"LangMem initialization failed: {e}")
                LANGMEM_AVAILABLE = False
    
    def _init_database(self):
        """Initialize SQLite database for Aider session storage"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS aider_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    conversation_id TEXT,
                    operation_type TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP,
                    aider_output TEXT,
                    error_message TEXT,
                    context_data TEXT,
                    user_id TEXT NOT NULL,
                    UNIQUE(session_id, user_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS file_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    operation_type TEXT NOT NULL,
                    lines_added INTEGER DEFAULT 0,
                    lines_removed INTEGER DEFAULT 0,
                    content_before TEXT,
                    content_after TEXT,
                    diff_content TEXT,
                    FOREIGN KEY(session_id) REFERENCES aider_sessions(session_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,
                    pattern_content TEXT NOT NULL,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    confidence_score REAL DEFAULT 0.5,
                    last_updated TIMESTAMP NOT NULL,
                    learned_from_session TEXT,
                    UNIQUE(pattern_type, pattern_content)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS aider_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    calculated_at TIMESTAMP NOT NULL
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_aider_session ON aider_sessions(user_id, status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_file_changes ON file_changes(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_patterns ON session_patterns(pattern_type, confidence_score)")
            
            conn.commit()
    
    def start_coding_session(self, prompt: str, operation_type: AiderOperation = AiderOperation.CODE_EDIT,
                           conversation_id: str = None, context_data: Dict[str, Any] = None) -> str:
        """Start a new Aider coding session"""
        session_id = self._generate_session_id()
        
        session = AiderSession(
            session_id=session_id,
            conversation_id=conversation_id,
            operation_type=operation_type,
            prompt=prompt,
            status=OperationStatus.PENDING,
            created_at=datetime.now(),
            context_data=context_data or {}
        )
        
        self.current_session = session
        self._store_session(session)
        
        self.logger.info(f"Started coding session: {session_id} - {operation_type.value}")
        return session_id
    
    def execute_aider_operation(self, files: List[str] = None, model: str = None,
                               additional_args: List[str] = None) -> bool:
        """Execute Aider operation for current session"""
        if not self.current_session:
            raise ValueError("No active session. Start a session first.")
        
        if not self.aider_interface.check_aider_available():
            self.current_session.status = OperationStatus.FAILED
            self.current_session.error_message = "Aider is not available"
            self._update_session_status()
            return False
        
        # Update session status
        self.current_session.status = OperationStatus.IN_PROGRESS
        self._update_session_status()
        
        # Apply learned patterns to improve prompt
        enhanced_prompt = self._enhance_prompt_with_patterns(self.current_session.prompt)
        
        # Get git state before changes
        git_commit_before = self._get_current_git_commit()
        
        # Execute Aider command
        model = model or self.default_model
        success, stdout, stderr = self.aider_interface.execute_aider_command(
            enhanced_prompt, files, model, additional_args
        )
        
        # Update session with results
        self.current_session.aider_output = stdout
        if not success:
            self.current_session.status = OperationStatus.FAILED
            self.current_session.error_message = stderr
        else:
            self.current_session.status = OperationStatus.COMPLETED
            
            # Track file changes
            self._track_file_changes(git_commit_before)
        
        self.current_session.completed_at = datetime.now()
        self._update_session_status()
        
        # Learn from this session
        self._learn_from_session(success)
        
        # Store analytics
        self._store_session_analytics()
        
        self.logger.info(f"Aider operation {'completed' if success else 'failed'}")
        return success
    
    def _enhance_prompt_with_patterns(self, original_prompt: str) -> str:
        """Enhance prompt with learned successful patterns"""
        enhanced_prompt = original_prompt
        
        # Load successful patterns
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT pattern_content, confidence_score
                FROM session_patterns
                WHERE pattern_type = 'prompt_enhancement' AND confidence_score > 0.7
                ORDER BY confidence_score DESC
                LIMIT 3
            """)
            
            patterns = cursor.fetchall()
        
        # Apply patterns
        for pattern_content, confidence in patterns:
            pattern_data = json.loads(pattern_content)
            if pattern_data.get("type") == "clarity_improvement":
                if "please" not in enhanced_prompt.lower():
                    enhanced_prompt = f"Please {enhanced_prompt.lower()}"
            elif pattern_data.get("type") == "context_addition":
                if "context:" not in enhanced_prompt.lower():
                    enhanced_prompt = f"Context: Working on {self.current_session.operation_type.value}. {enhanced_prompt}"
        
        if enhanced_prompt != original_prompt:
            self.logger.debug("Enhanced prompt with learned patterns")
        
        return enhanced_prompt
    
    def _track_file_changes(self, git_commit_before: str):
        """Track file changes made by Aider"""
        git_commit_after = self._get_current_git_commit()
        
        if git_commit_before == git_commit_after:
            self.logger.debug("No git changes detected")
            return
        
        # Get file changes from git
        changes = self.aider_interface.get_file_changes_from_git(f"{git_commit_before}..{git_commit_after}")
        
        # Store changes in session and database
        self.current_session.files_changed = changes
        
        for change in changes:
            with sqlite3.connect(self.memory_db) as conn:
                conn.execute("""
                    INSERT INTO file_changes
                    (session_id, file_path, operation_type, lines_added, lines_removed, diff_content)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    self.current_session.session_id, change.file_path, change.operation_type,
                    change.lines_added, change.lines_removed, change.diff
                ))
                conn.commit()
        
        self.logger.info(f"Tracked {len(changes)} file changes")
    
    def _learn_from_session(self, success: bool):
        """Learn patterns from session outcome"""
        if not self.current_session:
            return
        
        # Extract patterns from prompt
        prompt_patterns = self._extract_prompt_patterns(self.current_session.prompt)
        
        # Extract patterns from operation type
        operation_patterns = self._extract_operation_patterns()
        
        # Update pattern success/failure counts
        all_patterns = prompt_patterns + operation_patterns
        
        for pattern_type, pattern_content in all_patterns:
            with sqlite3.connect(self.memory_db) as conn:
                if success:
                    conn.execute("""
                        INSERT OR REPLACE INTO session_patterns
                        (pattern_type, pattern_content, success_count, failure_count, 
                         confidence_score, last_updated, learned_from_session)
                        VALUES (?, ?, 
                                COALESCE((SELECT success_count FROM session_patterns 
                                         WHERE pattern_type = ? AND pattern_content = ?), 0) + 1,
                                COALESCE((SELECT failure_count FROM session_patterns 
                                         WHERE pattern_type = ? AND pattern_content = ?), 0),
                                ?, ?, ?)
                    """, (
                        pattern_type, pattern_content, pattern_type, pattern_content,
                        pattern_type, pattern_content, self._calculate_confidence(True),
                        datetime.now(), self.current_session.session_id
                    ))
                else:
                    conn.execute("""
                        INSERT OR REPLACE INTO session_patterns
                        (pattern_type, pattern_content, success_count, failure_count,
                         confidence_score, last_updated, learned_from_session)
                        VALUES (?, ?, 
                                COALESCE((SELECT success_count FROM session_patterns 
                                         WHERE pattern_type = ? AND pattern_content = ?), 0),
                                COALESCE((SELECT failure_count FROM session_patterns 
                                         WHERE pattern_type = ? AND pattern_content = ?), 0) + 1,
                                ?, ?, ?)
                    """, (
                        pattern_type, pattern_content, pattern_type, pattern_content,
                        pattern_type, pattern_content, self._calculate_confidence(False),
                        datetime.now(), self.current_session.session_id
                    ))
                conn.commit()
    
    def _extract_prompt_patterns(self, prompt: str) -> List[Tuple[str, str]]:
        """Extract patterns from prompt text"""
        patterns = []
        
        # Prompt length pattern
        if len(prompt) < 50:
            patterns.append(("prompt_length", json.dumps({"type": "short", "length": len(prompt)})))
        elif len(prompt) > 200:
            patterns.append(("prompt_length", json.dumps({"type": "long", "length": len(prompt)})))
        else:
            patterns.append(("prompt_length", json.dumps({"type": "medium", "length": len(prompt)})))
        
        # Prompt style patterns
        if "please" in prompt.lower():
            patterns.append(("prompt_style", json.dumps({"type": "polite"})))
        
        if any(word in prompt.lower() for word in ["fix", "bug", "error", "issue"]):
            patterns.append(("prompt_intent", json.dumps({"type": "bug_fix"})))
        
        if any(word in prompt.lower() for word in ["add", "create", "implement", "build"]):
            patterns.append(("prompt_intent", json.dumps({"type": "feature_add"})))
        
        if any(word in prompt.lower() for word in ["refactor", "improve", "optimize", "clean"]):
            patterns.append(("prompt_intent", json.dumps({"type": "refactor"})))
        
        return patterns
    
    def _extract_operation_patterns(self) -> List[Tuple[str, str]]:
        """Extract patterns from operation context"""
        patterns = []
        
        # Operation type pattern
        patterns.append((
            "operation_type", 
            json.dumps({"type": self.current_session.operation_type.value})
        ))
        
        # Time of day pattern
        hour = datetime.now().hour
        if 6 <= hour < 12:
            time_period = "morning"
        elif 12 <= hour < 18:
            time_period = "afternoon"
        elif 18 <= hour < 22:
            time_period = "evening"
        else:
            time_period = "night"
        
        patterns.append(("time_context", json.dumps({"period": time_period})))
        
        return patterns
    
    def _calculate_confidence(self, success: bool) -> float:
        """Calculate confidence score for pattern"""
        base_confidence = 0.6 if success else 0.4
        return base_confidence
    
    def _store_session_analytics(self):
        """Store analytics for current session"""
        if not self.current_session:
            return
        
        analytics = []
        
        # Duration
        if self.current_session.completed_at:
            duration = (self.current_session.completed_at - self.current_session.created_at).total_seconds()
            analytics.append(("duration_seconds", duration))
        
        # Files changed count
        analytics.append(("files_changed_count", len(self.current_session.files_changed)))
        
        # Lines changed
        total_lines_added = sum(fc.lines_added for fc in self.current_session.files_changed)
        total_lines_removed = sum(fc.lines_removed for fc in self.current_session.files_changed)
        analytics.append(("lines_added", total_lines_added))
        analytics.append(("lines_removed", total_lines_removed))
        
        # Store analytics
        with sqlite3.connect(self.memory_db) as conn:
            for metric_name, metric_value in analytics:
                conn.execute("""
                    INSERT INTO aider_analytics
                    (session_id, metric_name, metric_value, calculated_at)
                    VALUES (?, ?, ?, ?)
                """, (self.current_session.session_id, metric_name, metric_value, datetime.now()))
            conn.commit()
    
    def get_session_history(self, limit: int = 20, operation_type: AiderOperation = None) -> List[Dict[str, Any]]:
        """Get session history with optional filtering"""
        with sqlite3.connect(self.memory_db) as conn:
            if operation_type:
                cursor = conn.execute("""
                    SELECT session_id, operation_type, prompt, status, created_at, completed_at
                    FROM aider_sessions
                    WHERE user_id = ? AND operation_type = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (self.user_id, operation_type.value, limit))
            else:
                cursor = conn.execute("""
                    SELECT session_id, operation_type, prompt, status, created_at, completed_at
                    FROM aider_sessions
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (self.user_id, limit))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    "session_id": row[0],
                    "operation_type": row[1],
                    "prompt": row[2],
                    "status": row[3],
                    "created_at": row[4],
                    "completed_at": row[5]
                })
            
            return history
    
    def get_session_analytics(self, session_id: str = None) -> Dict[str, Any]:
        """Get analytics for session"""
        target_id = session_id or (self.current_session.session_id if self.current_session else None)
        if not target_id:
            return {}
        
        with sqlite3.connect(self.memory_db) as conn:
            # Get session info
            cursor = conn.execute("""
                SELECT operation_type, status, created_at, completed_at, prompt
                FROM aider_sessions
                WHERE session_id = ? AND user_id = ?
            """, (target_id, self.user_id))
            
            session_row = cursor.fetchone()
            if not session_row:
                return {}
            
            # Get analytics
            cursor = conn.execute("""
                SELECT metric_name, metric_value
                FROM aider_analytics
                WHERE session_id = ?
            """, (target_id,))
            
            metrics = {}
            for row in cursor.fetchall():
                metrics[row[0]] = row[1]
            
            # Get file changes
            cursor = conn.execute("""
                SELECT COUNT(*) as change_count,
                       SUM(lines_added) as total_added,
                       SUM(lines_removed) as total_removed
                FROM file_changes
                WHERE session_id = ?
            """, (target_id,))
            
            change_row = cursor.fetchone()
            
            return {
                "session_id": target_id,
                "operation_type": session_row[0],
                "status": session_row[1],
                "created_at": session_row[2],
                "completed_at": session_row[3],
                "prompt_length": len(session_row[4]),
                "files_changed": change_row[0] if change_row else 0,
                "lines_added": change_row[1] if change_row else 0,
                "lines_removed": change_row[2] if change_row else 0,
                **metrics
            }
    
    def get_learned_patterns(self, pattern_type: str = None) -> List[Dict[str, Any]]:
        """Get learned patterns"""
        with sqlite3.connect(self.memory_db) as conn:
            if pattern_type:
                cursor = conn.execute("""
                    SELECT pattern_type, pattern_content, success_count, failure_count,
                           confidence_score, last_updated
                    FROM session_patterns
                    WHERE pattern_type = ?
                    ORDER BY confidence_score DESC
                """, (pattern_type,))
            else:
                cursor = conn.execute("""
                    SELECT pattern_type, pattern_content, success_count, failure_count,
                           confidence_score, last_updated
                    FROM session_patterns
                    ORDER BY confidence_score DESC
                """)
            
            patterns = []
            for row in cursor.fetchall():
                patterns.append({
                    "pattern_type": row[0],
                    "pattern_content": json.loads(row[1]) if row[1] else {},
                    "success_count": row[2],
                    "failure_count": row[3],
                    "confidence_score": row[4],
                    "last_updated": row[5]
                })
            
            return patterns
    
    def suggest_improvements(self, prompt: str, operation_type: AiderOperation) -> List[str]:
        """Suggest improvements based on learned patterns"""
        suggestions = []
        
        # Analyze prompt against successful patterns
        patterns = self.get_learned_patterns()
        
        for pattern in patterns:
            if pattern["confidence_score"] > 0.7:
                pattern_data = pattern["pattern_content"]
                
                if pattern["pattern_type"] == "prompt_style" and pattern_data.get("type") == "polite":
                    if "please" not in prompt.lower():
                        suggestions.append("Consider adding 'please' to make the request more polite")
                
                elif pattern["pattern_type"] == "prompt_length":
                    if pattern_data.get("type") == "medium" and len(prompt) < 50:
                        suggestions.append("Consider providing more detailed context in the prompt")
                    elif pattern_data.get("type") == "short" and len(prompt) > 200:
                        suggestions.append("Consider making the prompt more concise")
        
        return suggestions
    
    def revert_session(self, session_id: str) -> bool:
        """Revert changes made in a session"""
        # This would require git revert functionality
        # For now, just mark as reverted in database
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT status FROM aider_sessions
                WHERE session_id = ? AND user_id = ?
            """, (session_id, self.user_id))
            
            row = cursor.fetchone()
            if not row or row[0] != OperationStatus.COMPLETED.value:
                return False
            
            conn.execute("""
                UPDATE aider_sessions
                SET status = ?
                WHERE session_id = ? AND user_id = ?
            """, (OperationStatus.REVERTED.value, session_id, self.user_id))
            conn.commit()
            
            self.logger.info(f"Reverted session: {session_id}")
            return True
    
    def export_session(self, session_id: str, format: str = "json") -> str:
        """Export session data"""
        session_data = self.get_session_analytics(session_id)
        
        if format == "json":
            return json.dumps(session_data, indent=2)
        else:
            return str(session_data)
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"{self.user_id}:{timestamp}".encode()).hexdigest()[:16]
    
    def _get_current_git_commit(self) -> str:
        """Get current git commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return ""
    
    def _store_session(self, session: AiderSession):
        """Store session in database"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO aider_sessions
                (session_id, conversation_id, operation_type, prompt, status,
                 created_at, completed_at, aider_output, error_message, context_data, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_id, session.conversation_id, session.operation_type.value,
                session.prompt, session.status.value, session.created_at,
                session.completed_at, session.aider_output, session.error_message,
                json.dumps(session.context_data) if session.context_data else None,
                self.user_id
            ))
            conn.commit()
    
    def _update_session_status(self):
        """Update session status in database"""
        if not self.current_session:
            return
        
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                UPDATE aider_sessions
                SET status = ?, completed_at = ?, aider_output = ?, error_message = ?
                WHERE session_id = ? AND user_id = ?
            """, (
                self.current_session.status.value, self.current_session.completed_at,
                self.current_session.aider_output, self.current_session.error_message,
                self.current_session.session_id, self.user_id
            ))
            conn.commit()


# Global Aider instance
_global_aider = None


def get_aider(project_path: str = ".", user_id: str = "developer") -> DeltaAider:
    """Get global Aider instance"""
    global _global_aider
    if _global_aider is None:
        _global_aider = DeltaAider(project_path=project_path, user_id=user_id)
    return _global_aider


def initialize_aider(project_path: str = ".", config_dir: str = ".claude", user_id: str = "developer") -> DeltaAider:
    """Initialize Aider interface system"""
    global _global_aider
    _global_aider = DeltaAider(project_path=project_path, config_dir=config_dir, user_id=user_id)
    return _global_aider


if __name__ == "__main__":
    # Test Aider interface
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Testing ∂Aider system...")
        
        # Initialize Aider system
        aider = initialize_aider()
        
        # Check if Aider is available
        available = aider.aider_interface.check_aider_available()
        print(f"Aider available: {available}")
        
        # Start a coding session
        session_id = aider.start_coding_session(
            "Add a simple test file",
            AiderOperation.FILE_CREATE,
            context_data={"test": True}
        )
        print(f"Started session: {session_id}")
        
        # Test session analytics (without actually running Aider)
        analytics = aider.get_session_analytics()
        print(f"Session analytics: {analytics}")
        
        # Test pattern learning
        patterns = aider.get_learned_patterns()
        print(f"Learned patterns: {len(patterns)}")
        
        # Test suggestions
        suggestions = aider.suggest_improvements(
            "fix bug", 
            AiderOperation.BUG_FIX
        )
        print(f"Suggestions: {suggestions}")
        
        # Test session history
        history = aider.get_session_history(limit=5)
        print(f"Session history: {len(history)} sessions")
        
        print("∂Aider system test completed successfully!")
    else:
        print("∂Aider.py - Context-persistent code interface")
        print("Usage: python ∂Aider.py --test")