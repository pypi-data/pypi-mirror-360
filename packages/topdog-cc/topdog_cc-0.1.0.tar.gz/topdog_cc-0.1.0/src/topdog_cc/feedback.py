#!/usr/bin/env python3
"""
∂Feedback.py - Learning loop with conversation persistence
Part of the ∂-prefixed architecture for conversation-aware multi-agent development

This module provides the learning loop that ties together all ∂-prefixed components,
learning from development outcomes, adjusting strategies based on conversation patterns,
and completing the feedback cycle for continuous improvement.
"""

import json
import sqlite3
import hashlib
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, Counter
import re
import importlib.util

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





class FeedbackType(Enum):
    SUCCESS = "success"         # Positive outcome, reinforce pattern
    FAILURE = "failure"         # Negative outcome, adjust strategy
    NEUTRAL = "neutral"         # No clear signal
    PARTIAL = "partial"         # Mixed results, nuanced learning


class LearningCategory(Enum):
    TECHNICAL = "technical"                 # Code quality, architecture, tools
    PROCESS = "process"                     # Development workflow, methodology
    COMMUNICATION = "communication"        # User interaction, requirement clarity
    PERFORMANCE = "performance"            # Speed, efficiency, resource usage
    QUALITY = "quality"                     # Testing, validation, reliability


class ConfidenceLevel(Enum):
    LOW = "low"                 # 0.0 - 0.4
    MEDIUM = "medium"           # 0.4 - 0.7
    HIGH = "high"               # 0.7 - 0.9
    VERY_HIGH = "very_high"     # 0.9 - 1.0


@dataclass
class FeedbackEvent:
    """Single feedback event in the learning loop"""
    event_id: str
    timestamp: datetime
    feedback_type: FeedbackType
    category: LearningCategory
    context: str
    outcome: str
    components_involved: List[str]
    conversation_id: Optional[str] = None
    metrics: Optional[Dict[str, float]] = None
    raw_data: Optional[Dict[str, Any]] = None
    confidence: float = 0.5
    
    def __post_init__(self):
        if self.components_involved is None:
            self.components_involved = []
        if self.metrics is None:
            self.metrics = {}
        if self.raw_data is None:
            self.raw_data = {}
    
    def get_confidence_level(self) -> ConfidenceLevel:
        """Get confidence level enum from numeric confidence"""
        if self.confidence >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif self.confidence >= 0.7:
            return ConfidenceLevel.HIGH
        elif self.confidence >= 0.4:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW


@dataclass
class LearningPattern:
    """Learned pattern from feedback events"""
    pattern_id: str
    pattern_type: str
    pattern_content: Dict[str, Any]
    success_count: int = 0
    failure_count: int = 0
    neutral_count: int = 0
    confidence_score: float = 0.5
    last_updated: Optional[datetime] = None
    learned_from_events: List[str] = None
    effectiveness_score: float = 0.5
    
    def __post_init__(self):
        if self.learned_from_events is None:
            self.learned_from_events = []
        if self.last_updated is None:
            self.last_updated = datetime.now()
    
    def calculate_effectiveness(self) -> float:
        """Calculate pattern effectiveness based on outcomes"""
        total_events = self.success_count + self.failure_count + self.neutral_count
        if total_events == 0:
            return 0.5
        
        # Weight successes heavily, failures negatively, neutrals slightly positive
        weighted_score = (
            self.success_count * 1.0 + 
            self.neutral_count * 0.3 - 
            self.failure_count * 0.5
        ) / total_events
        
        # Normalize to 0-1 range
        return max(0.0, min(1.0, (weighted_score + 0.5) / 1.5))
    
    def update_with_feedback(self, feedback_type: FeedbackType, event_id: str):
        """Update pattern with new feedback"""
        if feedback_type == FeedbackType.SUCCESS:
            self.success_count += 1
        elif feedback_type == FeedbackType.FAILURE:
            self.failure_count += 1
        else:
            self.neutral_count += 1
        
        self.learned_from_events.append(event_id)
        self.last_updated = datetime.now()
        self.effectiveness_score = self.calculate_effectiveness()
        
        # Update confidence based on total experience and effectiveness
        total_events = self.success_count + self.failure_count + self.neutral_count
        experience_factor = min(1.0, total_events / 10.0)  # More experience = higher confidence
        
        self.confidence_score = (self.effectiveness_score * 0.7 + experience_factor * 0.3)


@dataclass
class LearningSession:
    """Complete learning session across multiple feedback events"""
    session_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    conversation_context: Optional[str] = None
    feedback_events: List[FeedbackEvent] = None
    patterns_discovered: List[str] = None
    insights_generated: List[str] = None
    recommendations: List[str] = None
    overall_outcome: Optional[FeedbackType] = None
    
    def __post_init__(self):
        if self.feedback_events is None:
            self.feedback_events = []
        if self.patterns_discovered is None:
            self.patterns_discovered = []
        if self.insights_generated is None:
            self.insights_generated = []
        if self.recommendations is None:
            self.recommendations = []


class ComponentAdapter:
    """Adapter to extract feedback from other ∂-prefixed components"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def extract_feedback_from_aider(self, session_data: Dict[str, Any]) -> List[FeedbackEvent]:
        """Extract feedback from ∂Aider session data"""
        events = []
        
        if not session_data:
            return events
        
        status = session_data.get("status", "unknown")
        session_id = session_data.get("session_id", "unknown")
        
        # Determine feedback type based on Aider session outcome
        if status == "completed":
            feedback_type = FeedbackType.SUCCESS
            outcome = "Aider session completed successfully"
        elif status == "failed":
            feedback_type = FeedbackType.FAILURE
            outcome = f"Aider session failed: {session_data.get('error_message', 'unknown error')}"
        else:
            feedback_type = FeedbackType.NEUTRAL
            outcome = f"Aider session status: {status}"
        
        # Extract metrics
        metrics = {}
        if "duration_seconds" in session_data:
            metrics["duration"] = session_data["duration_seconds"]
        if "files_changed_count" in session_data:
            metrics["files_changed"] = session_data["files_changed_count"]
        if "lines_added" in session_data:
            metrics["lines_added"] = session_data["lines_added"]
        if "lines_removed" in session_data:
            metrics["lines_removed"] = session_data["lines_removed"]
        
        event = FeedbackEvent(
            event_id=f"aider_{session_id}_{datetime.now().isoformat()}",
            timestamp=datetime.now(),
            feedback_type=feedback_type,
            category=LearningCategory.TECHNICAL,
            context=f"Aider session: {session_data.get('operation_type', 'unknown')}",
            outcome=outcome,
            components_involved=["∂Aider"],
            metrics=metrics,
            raw_data=session_data,
            confidence=0.8 if status in ["completed", "failed"] else 0.4
        )
        
        events.append(event)
        return events
    
    def extract_feedback_from_bdd(self, test_run_data: Dict[str, Any]) -> List[FeedbackEvent]:
        """Extract feedback from ∂BDD test run data"""
        events = []
        
        if not test_run_data:
            return events
        
        run_id = test_run_data.get("run_id", "unknown")
        passed = test_run_data.get("passed_scenarios", 0)
        failed = test_run_data.get("failed_scenarios", 0)
        total = test_run_data.get("total_scenarios", 0)
        
        # Determine feedback based on test results
        if total == 0:
            feedback_type = FeedbackType.NEUTRAL
            outcome = "No test scenarios found"
        elif failed == 0:
            feedback_type = FeedbackType.SUCCESS
            outcome = f"All {passed} test scenarios passed"
        elif passed == 0:
            feedback_type = FeedbackType.FAILURE
            outcome = f"All {failed} test scenarios failed"
        else:
            feedback_type = FeedbackType.PARTIAL
            outcome = f"{passed} passed, {failed} failed out of {total} scenarios"
        
        # Extract metrics
        metrics = {
            "pass_rate": passed / total if total > 0 else 0,
            "total_scenarios": total,
            "passed_scenarios": passed,
            "failed_scenarios": failed
        }
        
        if "total_duration" in test_run_data:
            metrics["duration"] = test_run_data["total_duration"]
        
        if "bdd_score" in test_run_data:
            metrics["bdd_score"] = test_run_data["bdd_score"]
        
        event = FeedbackEvent(
            event_id=f"bdd_{run_id}_{datetime.now().isoformat()}",
            timestamp=datetime.now(),
            feedback_type=feedback_type,
            category=LearningCategory.QUALITY,
            context=f"BDD test run with {total} scenarios",
            outcome=outcome,
            components_involved=["∂BDD"],
            metrics=metrics,
            raw_data=test_run_data,
            confidence=0.9  # Test results are highly reliable
        )
        
        events.append(event)
        return events
    
    def extract_feedback_from_reality(self, validation_data: Dict[str, Any]) -> List[FeedbackEvent]:
        """Extract feedback from ∂Reality validation data"""
        events = []
        
        if not validation_data:
            return events
        
        check_id = validation_data.get("check_id", "unknown")
        overall_status = validation_data.get("overall_status", "unknown")
        confidence_score = validation_data.get("confidence_score", 0.5)
        
        # Determine feedback based on validation status
        if overall_status == "passed":
            feedback_type = FeedbackType.SUCCESS
            outcome = "Reality validation passed"
        elif overall_status == "failed":
            feedback_type = FeedbackType.FAILURE
            outcome = "Reality validation failed"
        elif overall_status == "warning":
            feedback_type = FeedbackType.PARTIAL
            outcome = "Reality validation completed with warnings"
        else:
            feedback_type = FeedbackType.NEUTRAL
            outcome = f"Reality validation status: {overall_status}"
        
        # Extract metrics
        metrics = {
            "confidence_score": confidence_score,
            "validation_results_count": len(validation_data.get("validation_results", []))
        }
        
        event = FeedbackEvent(
            event_id=f"reality_{check_id}_{datetime.now().isoformat()}",
            timestamp=datetime.now(),
            feedback_type=feedback_type,
            category=LearningCategory.QUALITY,
            context="Reality validation check",
            outcome=outcome,
            components_involved=["∂Reality"],
            metrics=metrics,
            raw_data=validation_data,
            confidence=confidence_score
        )
        
        events.append(event)
        return events
    
    def extract_feedback_from_radon(self, analysis_data: Dict[str, Any]) -> List[FeedbackEvent]:
        """Extract feedback from ∂Radon complexity analysis data"""
        events = []
        
        if not analysis_data:
            return events
        
        analysis_id = analysis_data.get("analysis_id", "unknown")
        summary = analysis_data.get("summary", {})
        quality_trend = analysis_data.get("quality_trend", "unknown")
        
        avg_complexity = summary.get("average_complexity", 0)
        critical_count = summary.get("complexity_distribution", {}).get("critical", 0)
        
        # Determine feedback based on complexity analysis
        if avg_complexity <= 5 and critical_count == 0:
            feedback_type = FeedbackType.SUCCESS
            outcome = "Code complexity is within acceptable limits"
        elif avg_complexity > 15 or critical_count > 5:
            feedback_type = FeedbackType.FAILURE
            outcome = f"High code complexity detected (avg: {avg_complexity:.1f}, critical: {critical_count})"
        else:
            feedback_type = FeedbackType.PARTIAL
            outcome = f"Moderate code complexity (avg: {avg_complexity:.1f})"
        
        # Extract metrics
        metrics = {
            "average_complexity": avg_complexity,
            "critical_complexity_count": critical_count,
            "total_code_units": summary.get("total_code_units", 0),
            "files_analyzed": summary.get("files_analyzed", 0)
        }
        
        # Factor in quality trend
        trend_confidence = 0.7
        if quality_trend == "improving":
            feedback_type = FeedbackType.SUCCESS if feedback_type != FeedbackType.FAILURE else FeedbackType.PARTIAL
            trend_confidence = 0.8
        elif quality_trend == "degrading":
            feedback_type = FeedbackType.FAILURE if feedback_type != FeedbackType.SUCCESS else FeedbackType.PARTIAL
            trend_confidence = 0.8
        
        event = FeedbackEvent(
            event_id=f"radon_{analysis_id}_{datetime.now().isoformat()}",
            timestamp=datetime.now(),
            feedback_type=feedback_type,
            category=LearningCategory.QUALITY,
            context="Code complexity analysis",
            outcome=outcome,
            components_involved=["∂Radon"],
            metrics=metrics,
            raw_data=analysis_data,
            confidence=trend_confidence
        )
        
        events.append(event)
        return events


class DeltaFeedback:
    """
    ∂Feedback - Learning loop with conversation persistence
    
    Features:
    - Learning from development outcomes across all ∂-prefixed components
    - Adjusting strategies based on conversation patterns
    - Completing the feedback cycle for continuous improvement
    - Cross-component insight extraction and pattern discovery
    """
    
    def __init__(self, project_path: str = ".", config_dir: str = ".claude", user_id: str = "developer"):
        self.project_path = Path(project_path).resolve()
        self.config_dir = Path(config_dir)
        self.user_id = user_id
        self.config = get_config(user_id)
        self.logger = get_logger("∂Feedback")
        
        # Initialize memory systems
        self.memory_db = self.config_dir / "∂feedback_memory.db"
        self._init_memory_systems()
        self._init_database()
        
        # Component integration
        self.component_adapter = ComponentAdapter(self.logger)
        
        # Learning tracking
        self.current_session = None
        self.learned_patterns = {}
        self.insight_cache = {}
        
        # Learning parameters
        self.learning_rate = 0.1
        self.pattern_discovery_threshold = 0.7
        self.confidence_decay_rate = 0.05  # Patterns lose confidence over time if not reinforced
        
        self.logger.info(f"∂Feedback initialized for project: {self.project_path}")
    
    def _init_memory_systems(self):
        """Initialize LangMem and fallback SQLite memory systems"""
        global LANGMEM_AVAILABLE
        self.memory_tools = []
        
        if LANGMEM_AVAILABLE:
            try:
                self.store = InMemoryStore(
                    index={"dims": 1536, "embed": "openai:text-embedding-3-small"}
                )
                self.namespace = ("∂feedback", self.user_id)
                self.memory_tools = [
                    create_manage_memory_tool(namespace=self.namespace),
                    create_search_memory_tool(namespace=self.namespace),
                ]
                self.logger.info("LangMem memory system initialized")
            except Exception as e:
                self.logger.warning(f"LangMem initialization failed: {e}")
                LANGMEM_AVAILABLE = False
    
    def _init_database(self):
        """Initialize SQLite database for feedback and learning storage"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learning_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    started_at TIMESTAMP NOT NULL,
                    ended_at TIMESTAMP,
                    conversation_context TEXT,
                    insights_generated TEXT,
                    recommendations TEXT,
                    overall_outcome TEXT,
                    user_id TEXT NOT NULL,
                    UNIQUE(session_id, user_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL,
                    session_id TEXT,
                    timestamp TIMESTAMP NOT NULL,
                    feedback_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    context TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    components_involved TEXT,
                    conversation_id TEXT,
                    metrics TEXT,
                    raw_data TEXT,
                    confidence REAL DEFAULT 0.5,
                    FOREIGN KEY(session_id) REFERENCES learning_sessions(session_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learning_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_id TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    pattern_content TEXT NOT NULL,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    neutral_count INTEGER DEFAULT 0,
                    confidence_score REAL DEFAULT 0.5,
                    effectiveness_score REAL DEFAULT 0.5,
                    last_updated TIMESTAMP NOT NULL,
                    learned_from_events TEXT,
                    user_id TEXT NOT NULL,
                    UNIQUE(pattern_id, user_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cross_component_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    insight_id TEXT NOT NULL,
                    insight_type TEXT NOT NULL,
                    components_involved TEXT NOT NULL,
                    insight_content TEXT NOT NULL,
                    confidence_score REAL DEFAULT 0.5,
                    supporting_events TEXT,
                    discovered_at TIMESTAMP NOT NULL,
                    last_validated TIMESTAMP,
                    validation_count INTEGER DEFAULT 0,
                    user_id TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS strategy_adjustments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    adjustment_id TEXT NOT NULL,
                    component_name TEXT NOT NULL,
                    adjustment_type TEXT NOT NULL,
                    old_strategy TEXT,
                    new_strategy TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    expected_impact TEXT,
                    adjusted_at TIMESTAMP NOT NULL,
                    effectiveness_measured REAL,
                    user_id TEXT NOT NULL
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_learning_sessions ON learning_sessions(user_id, started_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_events ON feedback_events(session_id, timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_learning_patterns ON learning_patterns(user_id, confidence_score)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cross_component_insights ON cross_component_insights(user_id, confidence_score)")
            
            conn.commit()
    
    def start_learning_session(self, conversation_context: str = None) -> str:
        """Start a new learning session"""
        session_id = self._generate_session_id()
        
        session = LearningSession(
            session_id=session_id,
            started_at=datetime.now(),
            conversation_context=conversation_context
        )
        
        self.current_session = session
        self._store_learning_session(session)
        
        self.logger.info(f"Started learning session: {session_id}")
        return session_id
    
    def record_feedback_event(self, feedback_type: FeedbackType, category: LearningCategory,
                            context: str, outcome: str, components_involved: List[str],
                            conversation_id: str = None, metrics: Dict[str, float] = None,
                            raw_data: Dict[str, Any] = None, confidence: float = 0.5) -> str:
        """Record a single feedback event"""
        event_id = self._generate_event_id()
        
        event = FeedbackEvent(
            event_id=event_id,
            timestamp=datetime.now(),
            feedback_type=feedback_type,
            category=category,
            context=context,
            outcome=outcome,
            components_involved=components_involved,
            conversation_id=conversation_id,
            metrics=metrics or {},
            raw_data=raw_data or {},
            confidence=confidence
        )
        
        # Add to current session if available
        if self.current_session:
            self.current_session.feedback_events.append(event)
        
        # Store event
        self._store_feedback_event(event)
        
        # Process event for learning
        self._process_feedback_event(event)
        
        self.logger.info(f"Recorded feedback event: {event_id} ({feedback_type.value})")
        return event_id
    
    def process_component_feedback(self, component_name: str, component_data: Dict[str, Any]) -> List[str]:
        """Process feedback from a specific ∂-prefixed component"""
        events = []
        
        try:
            if component_name == "∂Aider":
                events = self.component_adapter.extract_feedback_from_aider(component_data)
            elif component_name == "∂BDD":
                events = self.component_adapter.extract_feedback_from_bdd(component_data)
            elif component_name == "∂Reality":
                events = self.component_adapter.extract_feedback_from_reality(component_data)
            elif component_name == "∂Radon":
                events = self.component_adapter.extract_feedback_from_radon(component_data)
            else:
                self.logger.warning(f"Unknown component for feedback processing: {component_name}")
                return []
            
            # Store and process all extracted events
            event_ids = []
            for event in events:
                if self.current_session:
                    self.current_session.feedback_events.append(event)
                
                self._store_feedback_event(event)
                self._process_feedback_event(event)
                event_ids.append(event.event_id)
            
            self.logger.info(f"Processed {len(events)} feedback events from {component_name}")
            return event_ids
            
        except Exception as e:
            self.logger.error(f"Error processing feedback from {component_name}: {e}")
            return []
    
    def _process_feedback_event(self, event: FeedbackEvent):
        """Process a feedback event for pattern discovery and learning"""
        # Extract patterns from the event
        patterns = self._extract_patterns_from_event(event)
        
        # Update existing patterns or create new ones
        for pattern_type, pattern_content in patterns:
            pattern_id = self._generate_pattern_id(pattern_type, pattern_content)
            
            # Get or create pattern
            pattern = self._get_or_create_pattern(pattern_id, pattern_type, pattern_content)
            
            # Update pattern with feedback
            pattern.update_with_feedback(event.feedback_type, event.event_id)
            
            # Store updated pattern
            self._store_learning_pattern(pattern)
            
            # Cache for quick access
            self.learned_patterns[pattern_id] = pattern
        
        # Check for cross-component insights
        if len(event.components_involved) > 1:
            self._discover_cross_component_insights(event)
        
        # Update strategy adjustments if pattern confidence is high enough
        self._consider_strategy_adjustments(event)
    
    def _extract_patterns_from_event(self, event: FeedbackEvent) -> List[Tuple[str, Dict[str, Any]]]:
        """Extract learning patterns from a feedback event"""
        patterns = []
        
        # Component-specific patterns
        for component in event.components_involved:
            patterns.append((
                f"component_{component.lower().replace('∂', '')}_outcome",
                {
                    "component": component,
                    "feedback_type": event.feedback_type.value,
                    "category": event.category.value,
                    "confidence": event.confidence
                }
            ))
        
        # Category-specific patterns
        patterns.append((
            f"category_{event.category.value}_pattern",
            {
                "category": event.category.value,
                "feedback_type": event.feedback_type.value,
                "context_keywords": self._extract_keywords(event.context),
                "outcome_keywords": self._extract_keywords(event.outcome)
            }
        ))
        
        # Metrics-based patterns
        if event.metrics:
            for metric_name, metric_value in event.metrics.items():
                # Classify metric value
                metric_level = "high" if metric_value > 0.7 else "medium" if metric_value > 0.3 else "low"
                
                patterns.append((
                    f"metric_{metric_name}_correlation",
                    {
                        "metric_name": metric_name,
                        "metric_level": metric_level,
                        "metric_value": metric_value,
                        "feedback_type": event.feedback_type.value
                    }
                ))
        
        # Temporal patterns
        hour = event.timestamp.hour
        time_period = "morning" if 6 <= hour < 12 else "afternoon" if 12 <= hour < 18 else "evening" if 18 <= hour < 22 else "night"
        
        patterns.append((
            f"temporal_{time_period}_pattern",
            {
                "time_period": time_period,
                "feedback_type": event.feedback_type.value,
                "category": event.category.value
            }
        ))
        
        # Multi-component patterns
        if len(event.components_involved) > 1:
            component_combo = "_".join(sorted(event.components_involved))
            patterns.append((
                f"multi_component_{component_combo}_pattern",
                {
                    "components": event.components_involved,
                    "feedback_type": event.feedback_type.value,
                    "interaction_type": "collaborative"
                }
            ))
        
        return patterns
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        # Simple keyword extraction (could be enhanced with NLP)
        text = text.lower()
        
        # Technical keywords
        technical_keywords = [
            "complexity", "test", "validation", "refactor", "implement", "fix", "bug",
            "feature", "code", "function", "class", "module", "error", "success",
            "performance", "quality", "maintainability", "documentation"
        ]
        
        found_keywords = []
        for keyword in technical_keywords:
            if keyword in text:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _discover_cross_component_insights(self, event: FeedbackEvent):
        """Discover insights from cross-component interactions"""
        if len(event.components_involved) < 2:
            return
        
        insight_id = self._generate_insight_id(event.components_involved, event.category)
        
        # Generate insight content based on the interaction
        insight_content = {
            "interaction_type": "cross_component",
            "components": event.components_involved,
            "category": event.category.value,
            "feedback_type": event.feedback_type.value,
            "outcome_summary": event.outcome,
            "discovered_at": event.timestamp.isoformat()
        }
        
        # Determine insight type
        if event.feedback_type == FeedbackType.SUCCESS:
            insight_type = "synergy_discovered"
            insight_content["insight"] = f"Positive synergy detected between {' and '.join(event.components_involved)}"
        elif event.feedback_type == FeedbackType.FAILURE:
            insight_type = "conflict_detected"
            insight_content["insight"] = f"Potential conflict or dependency issue between {' and '.join(event.components_involved)}"
        else:
            insight_type = "interaction_observed"
            insight_content["insight"] = f"Neutral interaction observed between {' and '.join(event.components_involved)}"
        
        # Store insight
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO cross_component_insights
                (insight_id, insight_type, components_involved, insight_content,
                 confidence_score, supporting_events, discovered_at, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                insight_id, insight_type, json.dumps(event.components_involved),
                json.dumps(insight_content), event.confidence, json.dumps([event.event_id]),
                event.timestamp, self.user_id
            ))
            conn.commit()
        
        self.logger.info(f"Discovered cross-component insight: {insight_type}")
    
    def _consider_strategy_adjustments(self, event: FeedbackEvent):
        """Consider if strategy adjustments are needed based on feedback patterns"""
        # Get recent patterns for the components involved
        recent_patterns = self._get_recent_patterns_for_components(event.components_involved)
        
        for component in event.components_involved:
            component_patterns = [p for p in recent_patterns if component in p.pattern_content.get("component", "")]
            
            if not component_patterns:
                continue
            
            # Calculate component success rate
            total_successes = sum(p.success_count for p in component_patterns)
            total_failures = sum(p.failure_count for p in component_patterns)
            total_events = total_successes + total_failures
            
            if total_events < 5:  # Need minimum events for reliable adjustment
                continue
            
            success_rate = total_successes / total_events
            
            # Consider adjustment if success rate is too low
            if success_rate < 0.6:
                self._create_strategy_adjustment(
                    component, 
                    "success_rate_improvement",
                    f"Current success rate ({success_rate:.1%}) is below threshold",
                    event
                )
            
            # Consider adjustment for high complexity components
            if event.category == LearningCategory.QUALITY and event.feedback_type == FeedbackType.FAILURE:
                complexity_metrics = event.metrics.get("average_complexity", 0)
                if complexity_metrics > 15:
                    self._create_strategy_adjustment(
                        component,
                        "complexity_reduction",
                        f"High complexity detected ({complexity_metrics:.1f})",
                        event
                    )
    
    def _create_strategy_adjustment(self, component: str, adjustment_type: str, reason: str, event: FeedbackEvent):
        """Create a strategy adjustment recommendation"""
        adjustment_id = self._generate_adjustment_id()
        
        # Generate strategy recommendations based on adjustment type
        if adjustment_type == "success_rate_improvement":
            new_strategy = {
                "approach": "enhanced_validation",
                "details": "Add more validation steps before execution",
                "parameters": {"validation_threshold": 0.8, "retry_count": 2}
            }
            expected_impact = "Improved success rate through better validation"
            
        elif adjustment_type == "complexity_reduction":
            new_strategy = {
                "approach": "complexity_gates",
                "details": "Implement complexity checks with automatic refactoring suggestions",
                "parameters": {"max_complexity": 10, "auto_suggest": True}
            }
            expected_impact = "Reduced code complexity through proactive management"
            
        else:
            new_strategy = {
                "approach": "general_improvement",
                "details": "Apply general best practices and monitoring",
                "parameters": {"monitoring_enabled": True}
            }
            expected_impact = "General improvement in component performance"
        
        # Store strategy adjustment
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT INTO strategy_adjustments
                (adjustment_id, component_name, adjustment_type, new_strategy,
                 reason, expected_impact, adjusted_at, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                adjustment_id, component, adjustment_type, json.dumps(new_strategy),
                reason, expected_impact, datetime.now(), self.user_id
            ))
            conn.commit()
        
        self.logger.info(f"Created strategy adjustment for {component}: {adjustment_type}")
    
    def _get_recent_patterns_for_components(self, components: List[str]) -> List[LearningPattern]:
        """Get recent learning patterns for specific components"""
        patterns = []
        
        with sqlite3.connect(self.memory_db) as conn:
            for component in components:
                cursor = conn.execute("""
                    SELECT pattern_id, pattern_type, pattern_content, success_count,
                           failure_count, neutral_count, confidence_score, effectiveness_score,
                           last_updated, learned_from_events
                    FROM learning_patterns
                    WHERE user_id = ? AND pattern_content LIKE ?
                    ORDER BY last_updated DESC
                    LIMIT 10
                """, (self.user_id, f"%{component}%"))
                
                for row in cursor.fetchall():
                    try:
                        pattern = LearningPattern(
                            pattern_id=row[0],
                            pattern_type=row[1],
                            pattern_content=json.loads(row[2]),
                            success_count=row[3],
                            failure_count=row[4],
                            neutral_count=row[5],
                            confidence_score=row[6],
                            effectiveness_score=row[7],
                            last_updated=datetime.fromisoformat(row[8]),
                            learned_from_events=json.loads(row[9]) if row[9] else []
                        )
                        patterns.append(pattern)
                    except Exception as e:
                        self.logger.warning(f"Failed to load pattern {row[0]}: {e}")
        
        return patterns
    
    def end_learning_session(self) -> Dict[str, Any]:
        """End current learning session and generate insights"""
        if not self.current_session:
            return {}
        
        # Generate insights from session
        insights = self._generate_session_insights()
        recommendations = self._generate_session_recommendations()
        
        # Determine overall outcome
        if not self.current_session.feedback_events:
            overall_outcome = FeedbackType.NEUTRAL
        else:
            success_count = sum(1 for e in self.current_session.feedback_events if e.feedback_type == FeedbackType.SUCCESS)
            failure_count = sum(1 for e in self.current_session.feedback_events if e.feedback_type == FeedbackType.FAILURE)
            
            if success_count > failure_count * 2:
                overall_outcome = FeedbackType.SUCCESS
            elif failure_count > success_count * 2:
                overall_outcome = FeedbackType.FAILURE
            else:
                overall_outcome = FeedbackType.PARTIAL
        
        # Update session
        self.current_session.ended_at = datetime.now()
        self.current_session.insights_generated = insights
        self.current_session.recommendations = recommendations
        self.current_session.overall_outcome = overall_outcome
        
        # Store updated session
        self._store_learning_session(self.current_session)
        
        session_summary = {
            "session_id": self.current_session.session_id,
            "duration": (self.current_session.ended_at - self.current_session.started_at).total_seconds(),
            "events_processed": len(self.current_session.feedback_events),
            "insights_generated": len(insights),
            "recommendations": len(recommendations),
            "overall_outcome": overall_outcome.value
        }
        
        self.logger.info(f"Ended learning session: {self.current_session.session_id}")
        self.current_session = None
        
        return session_summary
    
    def _generate_session_insights(self) -> List[str]:
        """Generate insights from current learning session"""
        if not self.current_session or not self.current_session.feedback_events:
            return []
        
        insights = []
        events = self.current_session.feedback_events
        
        # Component performance insights
        component_stats = defaultdict(lambda: {"success": 0, "failure": 0, "total": 0})
        for event in events:
            for component in event.components_involved:
                component_stats[component]["total"] += 1
                if event.feedback_type == FeedbackType.SUCCESS:
                    component_stats[component]["success"] += 1
                elif event.feedback_type == FeedbackType.FAILURE:
                    component_stats[component]["failure"] += 1
        
        for component, stats in component_stats.items():
            if stats["total"] >= 3:  # Minimum events for insight
                success_rate = stats["success"] / stats["total"]
                if success_rate >= 0.8:
                    insights.append(f"{component} demonstrated excellent performance ({success_rate:.1%} success rate)")
                elif success_rate <= 0.4:
                    insights.append(f"{component} needs attention ({success_rate:.1%} success rate, {stats['failure']} failures)")
        
        # Category insights
        category_stats = defaultdict(lambda: {"success": 0, "failure": 0, "total": 0})
        for event in events:
            category_stats[event.category.value]["total"] += 1
            if event.feedback_type == FeedbackType.SUCCESS:
                category_stats[event.category.value]["success"] += 1
            elif event.feedback_type == FeedbackType.FAILURE:
                category_stats[event.category.value]["failure"] += 1
        
        for category, stats in category_stats.items():
            if stats["total"] >= 2:
                success_rate = stats["success"] / stats["total"]
                if success_rate >= 0.8:
                    insights.append(f"{category.title()} activities are performing well ({success_rate:.1%} success rate)")
                elif success_rate <= 0.4:
                    insights.append(f"{category.title()} activities need improvement ({success_rate:.1%} success rate)")
        
        # Cross-component insights
        multi_component_events = [e for e in events if len(e.components_involved) > 1]
        if multi_component_events:
            success_count = sum(1 for e in multi_component_events if e.feedback_type == FeedbackType.SUCCESS)
            if success_count / len(multi_component_events) >= 0.7:
                insights.append("Cross-component collaboration is working effectively")
            elif success_count / len(multi_component_events) <= 0.3:
                insights.append("Cross-component interactions may need better coordination")
        
        return insights
    
    def _generate_session_recommendations(self) -> List[str]:
        """Generate recommendations from current learning session"""
        if not self.current_session or not self.current_session.feedback_events:
            return []
        
        recommendations = []
        events = self.current_session.feedback_events
        
        # High-confidence patterns that should be reinforced
        high_confidence_patterns = []
        for pattern in self.learned_patterns.values():
            if pattern.confidence_score >= 0.8 and pattern.effectiveness_score >= 0.7:
                high_confidence_patterns.append(pattern)
        
        if high_confidence_patterns:
            recommendations.append(
                f"Continue applying {len(high_confidence_patterns)} high-confidence patterns "
                f"that have shown consistent success"
            )
        
        # Components with repeated failures
        failure_events = [e for e in events if e.feedback_type == FeedbackType.FAILURE]
        component_failures = defaultdict(int)
        for event in failure_events:
            for component in event.components_involved:
                component_failures[component] += 1
        
        for component, failure_count in component_failures.items():
            if failure_count >= 2:
                recommendations.append(
                    f"Review {component} configuration and usage patterns "
                    f"({failure_count} failures detected)"
                )
        
        # Quality-specific recommendations
        quality_events = [e for e in events if e.category == LearningCategory.QUALITY]
        if quality_events:
            failure_rate = sum(1 for e in quality_events if e.feedback_type == FeedbackType.FAILURE) / len(quality_events)
            if failure_rate > 0.5:
                recommendations.append(
                    "Implement additional quality gates and validation steps "
                    "to improve overall code quality"
                )
        
        # Performance recommendations
        performance_events = [e for e in events if e.category == LearningCategory.PERFORMANCE]
        if performance_events:
            # Check for duration metrics
            durations = []
            for event in performance_events:
                if "duration" in event.metrics:
                    durations.append(event.metrics["duration"])
            
            if durations and sum(durations) / len(durations) > 300:  # 5 minutes
                recommendations.append(
                    "Consider optimizing performance-critical operations "
                    "as average execution time is high"
                )
        
        return recommendations
    
    def get_learning_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get comprehensive learning summary for recent period"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.memory_db) as conn:
            # Get recent sessions
            cursor = conn.execute("""
                SELECT COUNT(*), AVG(
                    CASE WHEN ended_at IS NOT NULL 
                    THEN (julianday(ended_at) - julianday(started_at)) * 24 * 3600 
                    ELSE NULL END
                ) as avg_duration
                FROM learning_sessions
                WHERE user_id = ? AND started_at >= ?
            """, (self.user_id, cutoff_date))
            
            session_stats = cursor.fetchone()
            
            # Get recent events
            cursor = conn.execute("""
                SELECT feedback_type, COUNT(*) as count
                FROM feedback_events
                WHERE timestamp >= ?
                GROUP BY feedback_type
            """, (cutoff_date,))
            
            event_stats = dict(cursor.fetchall())
            
            # Get top patterns
            cursor = conn.execute("""
                SELECT pattern_type, effectiveness_score, confidence_score
                FROM learning_patterns
                WHERE user_id = ? AND last_updated >= ?
                ORDER BY effectiveness_score DESC, confidence_score DESC
                LIMIT 10
            """, (self.user_id, cutoff_date))
            
            top_patterns = [
                {"type": row[0], "effectiveness": row[1], "confidence": row[2]}
                for row in cursor.fetchall()
            ]
            
            # Get recent insights
            cursor = conn.execute("""
                SELECT insight_type, COUNT(*) as count
                FROM cross_component_insights
                WHERE user_id = ? AND discovered_at >= ?
                GROUP BY insight_type
            """, (self.user_id, cutoff_date))
            
            insight_stats = dict(cursor.fetchall())
        
        total_events = sum(event_stats.values())
        success_rate = event_stats.get("success", 0) / total_events if total_events > 0 else 0
        
        return {
            "period_days": days,
            "sessions_count": session_stats[0] if session_stats else 0,
            "avg_session_duration": session_stats[1] if session_stats and session_stats[1] else 0,
            "total_events": total_events,
            "event_distribution": event_stats,
            "success_rate": success_rate,
            "top_patterns": top_patterns,
            "insights_discovered": insight_stats,
            "learning_velocity": total_events / days if days > 0 else 0
        }
    
    def get_component_feedback_analysis(self, component_name: str, days: int = 30) -> Dict[str, Any]:
        """Get detailed feedback analysis for a specific component"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.memory_db) as conn:
            # Get events for this component
            cursor = conn.execute("""
                SELECT feedback_type, category, confidence, metrics
                FROM feedback_events
                WHERE components_involved LIKE ? AND timestamp >= ?
            """, (f"%{component_name}%", cutoff_date))
            
            events = []
            for row in cursor.fetchall():
                try:
                    metrics = json.loads(row[3]) if row[3] else {}
                    events.append({
                        "feedback_type": row[0],
                        "category": row[1],
                        "confidence": row[2],
                        "metrics": metrics
                    })
                except:
                    continue
            
            # Get patterns for this component
            cursor = conn.execute("""
                SELECT pattern_type, effectiveness_score, confidence_score, success_count, failure_count
                FROM learning_patterns
                WHERE user_id = ? AND pattern_content LIKE ? AND last_updated >= ?
                ORDER BY effectiveness_score DESC
            """, (self.user_id, f"%{component_name}%", cutoff_date))
            
            patterns = [
                {
                    "type": row[0],
                    "effectiveness": row[1],
                    "confidence": row[2],
                    "success_count": row[3],
                    "failure_count": row[4]
                }
                for row in cursor.fetchall()
            ]
        
        if not events:
            return {"component": component_name, "message": "No feedback data available"}
        
        # Calculate statistics
        total_events = len(events)
        success_count = sum(1 for e in events if e["feedback_type"] == "success")
        failure_count = sum(1 for e in events if e["feedback_type"] == "failure")
        
        success_rate = success_count / total_events
        avg_confidence = sum(e["confidence"] for e in events) / total_events
        
        # Category distribution
        category_dist = Counter(e["category"] for e in events)
        
        # Extract common metrics
        all_metrics = {}
        for event in events:
            for metric_name, metric_value in event["metrics"].items():
                if metric_name not in all_metrics:
                    all_metrics[metric_name] = []
                all_metrics[metric_name].append(metric_value)
        
        avg_metrics = {
            name: sum(values) / len(values)
            for name, values in all_metrics.items()
            if len(values) > 0
        }
        
        return {
            "component": component_name,
            "analysis_period_days": days,
            "total_events": total_events,
            "success_rate": success_rate,
            "success_count": success_count,
            "failure_count": failure_count,
            "avg_confidence": avg_confidence,
            "category_distribution": dict(category_dist),
            "average_metrics": avg_metrics,
            "learned_patterns": patterns,
            "recommendation": self._generate_component_recommendation(
                component_name, success_rate, patterns, avg_metrics
            )
        }
    
    def _generate_component_recommendation(self, component_name: str, success_rate: float,
                                         patterns: List[Dict], avg_metrics: Dict[str, float]) -> str:
        """Generate recommendation for a specific component"""
        if success_rate >= 0.8:
            return f"{component_name} is performing excellently. Continue current practices."
        elif success_rate >= 0.6:
            return f"{component_name} is performing well but has room for improvement. " \
                   f"Review patterns with lower effectiveness scores."
        elif success_rate >= 0.4:
            return f"{component_name} needs attention. Consider adjusting configuration " \
                   f"or usage patterns based on failure analysis."
        else:
            return f"{component_name} requires immediate attention. High failure rate detected. " \
                   f"Review recent failures and consider alternative approaches."
    
    def _get_or_create_pattern(self, pattern_id: str, pattern_type: str, pattern_content: Dict[str, Any]) -> LearningPattern:
        """Get existing pattern or create new one"""
        if pattern_id in self.learned_patterns:
            return self.learned_patterns[pattern_id]
        
        # Try to load from database
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT pattern_type, pattern_content, success_count, failure_count,
                       neutral_count, confidence_score, effectiveness_score, last_updated,
                       learned_from_events
                FROM learning_patterns
                WHERE pattern_id = ? AND user_id = ?
            """, (pattern_id, self.user_id))
            
            row = cursor.fetchone()
            if row:
                try:
                    pattern = LearningPattern(
                        pattern_id=pattern_id,
                        pattern_type=row[0],
                        pattern_content=json.loads(row[1]),
                        success_count=row[2],
                        failure_count=row[3],
                        neutral_count=row[4],
                        confidence_score=row[5],
                        effectiveness_score=row[6],
                        last_updated=datetime.fromisoformat(row[7]),
                        learned_from_events=json.loads(row[8]) if row[8] else []
                    )
                    self.learned_patterns[pattern_id] = pattern
                    return pattern
                except Exception as e:
                    self.logger.warning(f"Failed to load pattern {pattern_id}: {e}")
        
        # Create new pattern
        pattern = LearningPattern(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            pattern_content=pattern_content
        )
        
        self.learned_patterns[pattern_id] = pattern
        return pattern
    
    def _store_learning_session(self, session: LearningSession):
        """Store learning session in database"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO learning_sessions
                (session_id, started_at, ended_at, conversation_context,
                 insights_generated, recommendations, overall_outcome, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_id, session.started_at, session.ended_at,
                session.conversation_context, json.dumps(session.insights_generated),
                json.dumps(session.recommendations), 
                session.overall_outcome.value if session.overall_outcome else None,
                self.user_id
            ))
            conn.commit()
    
    def _store_feedback_event(self, event: FeedbackEvent):
        """Store feedback event in database"""
        session_id = self.current_session.session_id if self.current_session else None
        
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT INTO feedback_events
                (event_id, session_id, timestamp, feedback_type, category, context,
                 outcome, components_involved, conversation_id, metrics, raw_data, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id, session_id, event.timestamp, event.feedback_type.value,
                event.category.value, event.context, event.outcome,
                json.dumps(event.components_involved), event.conversation_id,
                json.dumps(event.metrics), json.dumps(event.raw_data), event.confidence
            ))
            conn.commit()
    
    def _store_learning_pattern(self, pattern: LearningPattern):
        """Store learning pattern in database"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO learning_patterns
                (pattern_id, pattern_type, pattern_content, success_count, failure_count,
                 neutral_count, confidence_score, effectiveness_score, last_updated,
                 learned_from_events, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern.pattern_id, pattern.pattern_type, json.dumps(pattern.pattern_content),
                pattern.success_count, pattern.failure_count, pattern.neutral_count,
                pattern.confidence_score, pattern.effectiveness_score, pattern.last_updated,
                json.dumps(pattern.learned_from_events), self.user_id
            ))
            conn.commit()
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"session_{self.user_id}:{timestamp}".encode()).hexdigest()[:16]
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"event_{self.user_id}:{timestamp}".encode()).hexdigest()[:16]
    
    def _generate_pattern_id(self, pattern_type: str, pattern_content: Dict[str, Any]) -> str:
        """Generate unique pattern ID"""
        content_hash = hashlib.md5(json.dumps(pattern_content, sort_keys=True).encode()).hexdigest()[:8]
        return f"{pattern_type}_{content_hash}"
    
    def _generate_insight_id(self, components: List[str], category: LearningCategory) -> str:
        """Generate unique insight ID"""
        component_hash = hashlib.md5("_".join(sorted(components)).encode()).hexdigest()[:8]
        return f"insight_{category.value}_{component_hash}"
    
    def _generate_adjustment_id(self) -> str:
        """Generate unique adjustment ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"adjustment_{self.user_id}:{timestamp}".encode()).hexdigest()[:16]


# Global Feedback instance
_global_feedback = None


def get_feedback(project_path: str = ".", user_id: str = "developer") -> DeltaFeedback:
    """Get global Feedback instance"""
    global _global_feedback
    if _global_feedback is None:
        _global_feedback = DeltaFeedback(project_path=project_path, user_id=user_id)
    return _global_feedback


def initialize_feedback(project_path: str = ".", config_dir: str = ".claude", user_id: str = "developer") -> DeltaFeedback:
    """Initialize Feedback learning system"""
    global _global_feedback
    _global_feedback = DeltaFeedback(project_path=project_path, config_dir=config_dir, user_id=user_id)
    return _global_feedback


if __name__ == "__main__":
    # Test Feedback system
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Testing ∂Feedback system...")
        
        # Initialize Feedback system
        feedback = initialize_feedback()
        
        # Start learning session
        session_id = feedback.start_learning_session("Testing ∂Feedback system")
        print(f"Started learning session: {session_id}")
        
        # Record some test feedback events
        event1_id = feedback.record_feedback_event(
            FeedbackType.SUCCESS,
            LearningCategory.TECHNICAL,
            "Test code implementation",
            "Code implemented successfully",
            ["∂Aider"],
            metrics={"duration": 120.5, "lines_added": 50}
        )
        print(f"Recorded event 1: {event1_id}")
        
        event2_id = feedback.record_feedback_event(
            FeedbackType.FAILURE,
            LearningCategory.QUALITY,
            "Test validation",
            "Validation failed due to complexity",
            ["∂Reality", "∂Radon"],
            metrics={"complexity": 25.3, "validation_score": 0.3}
        )
        print(f"Recorded event 2: {event2_id}")
        
        # Test component feedback processing
        aider_data = {
            "session_id": "test_session",
            "status": "completed",
            "operation_type": "code_edit",
            "duration_seconds": 90,
            "files_changed_count": 2,
            "lines_added": 30,
            "lines_removed": 10
        }
        
        aider_events = feedback.process_component_feedback("∂Aider", aider_data)
        print(f"Processed Aider feedback: {len(aider_events)} events")
        
        # End learning session
        session_summary = feedback.end_learning_session()
        print(f"Session summary: {session_summary}")
        
        # Get learning summary
        learning_summary = feedback.get_learning_summary(days=1)
        print(f"Learning summary: {learning_summary}")
        
        # Get component analysis
        component_analysis = feedback.get_component_feedback_analysis("∂Aider", days=1)
        print(f"Component analysis: {component_analysis}")
        
        print("\n∂Feedback system test completed successfully!")
    else:
        print("∂Feedback.py - Learning loop with conversation persistence")
        print("Usage: python ∂Feedback.py --test")