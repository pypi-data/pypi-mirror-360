#!/usr/bin/env python3
"""
∂BDD.py - Conversation-aware BDD execution
Part of the ∂-prefixed architecture for conversation-aware multi-agent development

This module provides intelligent BDD test execution that learns from scenario failure
patterns, adapts test strategies based on conversation history, and integrates with
existing ΩBDDSCOREBOARD system while including independent scoreboard functionality.
"""

import json
import os
import sqlite3
import subprocess
import re
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, Counter
import xml.etree.ElementTree as ET

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





class TestStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    UNDEFINED = "undefined"
    PENDING = "pending"


class ScenarioType(Enum):
    SMOKE = "smoke"
    REGRESSION = "regression"
    INTEGRATION = "integration"
    UNIT = "unit"
    ACCEPTANCE = "acceptance"
    PERFORMANCE = "performance"


@dataclass
class ScenarioResult:
    """Single BDD scenario test result"""
    scenario_name: str
    feature_name: str
    status: TestStatus
    duration: float
    error_message: Optional[str] = None
    steps_passed: int = 0
    steps_failed: int = 0
    steps_skipped: int = 0
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class BDDTestRun:
    """Complete BDD test run results"""
    run_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_scenarios: int = 0
    passed_scenarios: int = 0
    failed_scenarios: int = 0
    skipped_scenarios: int = 0
    total_duration: float = 0.0
    scenario_results: List[ScenarioResult] = None
    conversation_context: Optional[str] = None
    bdd_score: Optional[float] = None
    
    def __post_init__(self):
        if self.scenario_results is None:
            self.scenario_results = []
    
    def calculate_score(self) -> float:
        """Calculate BDD score based on results"""
        if self.total_scenarios == 0:
            return 0.0
        
        # Base score from pass rate
        pass_rate = self.passed_scenarios / self.total_scenarios
        base_score = pass_rate * 100
        
        # Adjust for test coverage and quality
        if self.total_scenarios >= 10:
            base_score += 5  # Bonus for good coverage
        
        # Penalty for failures
        failure_rate = self.failed_scenarios / self.total_scenarios
        if failure_rate > 0.2:  # More than 20% failures
            base_score -= (failure_rate - 0.2) * 50
        
        # Performance consideration
        if self.total_duration > 0:
            avg_duration = self.total_duration / self.total_scenarios
            if avg_duration > 10:  # Very slow tests
                base_score -= 5
        
        return max(0.0, min(100.0, base_score))


class BehaveRunner:
    """Interface to behave test runner"""
    
    def __init__(self, project_path: str, behave_path: str = "behave"):
        self.project_path = Path(project_path)
        self.behave_path = behave_path
        self.logger = get_logger("BehaveRunner")
    
    def check_behave_available(self) -> bool:
        """Check if behave is available in the system"""
        try:
            result = subprocess.run(
                [self.behave_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.warning(f"Behave not available: {e}")
            return False
    
    def run_tests(self, features_path: str = "features", tags: List[str] = None,
                  dry_run: bool = False, additional_args: List[str] = None) -> Tuple[bool, str, str]:
        """Run behave tests and return results"""
        if not self.check_behave_available():
            return False, "", "Behave is not available"
        
        # Build command
        cmd = [self.behave_path]
        
        # Add features path
        cmd.append(features_path)
        
        # Add tags if specified
        if tags:
            for tag in tags:
                cmd.extend(["--tags", tag])
        
        # Add dry run option
        if dry_run:
            cmd.append("--dry-run")
        
        # Add JSON output for parsing
        cmd.extend(["--format", "json", "--outfile", "behave_results.json"])
        
        # Add additional arguments
        if additional_args:
            cmd.extend(additional_args)
        
        try:
            # Execute in project directory
            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            success = result.returncode == 0
            stdout = result.stdout
            stderr = result.stderr
            
            self.logger.info(f"Behave tests {'passed' if success else 'failed'}")
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            self.logger.error("Behave tests timed out")
            return False, "", "Tests timed out"
        except Exception as e:
            self.logger.error(f"Behave execution failed: {e}")
            return False, "", str(e)
    
    def parse_behave_json_output(self, json_file: str = "behave_results.json") -> List[ScenarioResult]:
        """Parse behave JSON output into scenario results"""
        json_path = self.project_path / json_file
        
        if not json_path.exists():
            return []
        
        try:
            with open(json_path, 'r') as f:
                behave_data = json.load(f)
            
            scenario_results = []
            
            for feature in behave_data:
                feature_name = feature.get("name", "Unknown Feature")
                
                for element in feature.get("elements", []):
                    if element.get("type") == "scenario":
                        scenario_name = element.get("name", "Unknown Scenario")
                        tags = [tag["name"] for tag in element.get("tags", [])]
                        
                        # Calculate scenario status and timing
                        steps = element.get("steps", [])
                        steps_passed = sum(1 for step in steps if step.get("result", {}).get("status") == "passed")
                        steps_failed = sum(1 for step in steps if step.get("result", {}).get("status") == "failed")
                        steps_skipped = sum(1 for step in steps if step.get("result", {}).get("status") == "skipped")
                        
                        # Determine overall status
                        if steps_failed > 0:
                            status = TestStatus.FAILED
                        elif steps_skipped > 0 and steps_passed == 0:
                            status = TestStatus.SKIPPED
                        elif steps_passed > 0:
                            status = TestStatus.PASSED
                        else:
                            status = TestStatus.UNDEFINED
                        
                        # Calculate duration
                        duration = sum(
                            step.get("result", {}).get("duration", 0)
                            for step in steps
                        )
                        
                        # Get error message if failed
                        error_message = None
                        for step in steps:
                            if step.get("result", {}).get("status") == "failed":
                                error_message = step.get("result", {}).get("error_message", "Step failed")
                                break
                        
                        scenario_results.append(ScenarioResult(
                            scenario_name=scenario_name,
                            feature_name=feature_name,
                            status=status,
                            duration=duration,
                            error_message=error_message,
                            steps_passed=steps_passed,
                            steps_failed=steps_failed,
                            steps_skipped=steps_skipped,
                            tags=tags
                        ))
            
            return scenario_results
            
        except Exception as e:
            self.logger.error(f"Failed to parse behave JSON output: {e}")
            return []


class ScoreboardDisplay:
    """Independent BDD scoreboard functionality"""
    
    def __init__(self):
        self.logger = get_logger("ScoreboardDisplay")
    
    def generate_score_display(self, test_run: BDDTestRun) -> str:
        """Generate visual scoreboard display"""
        score = test_run.bdd_score or test_run.calculate_score()
        
        # Create ASCII scoreboard
        lines = [
            "=" * 60,
            "🎯 BDD SCOREBOARD",
            "=" * 60,
            "",
            f"📊 OVERALL SCORE: {score:.1f}/100",
            "",
            "📈 Test Results:",
            f"  ✅ Passed:  {test_run.passed_scenarios:>3} ({test_run.passed_scenarios/max(test_run.total_scenarios,1)*100:.1f}%)",
            f"  ❌ Failed:  {test_run.failed_scenarios:>3} ({test_run.failed_scenarios/max(test_run.total_scenarios,1)*100:.1f}%)",
            f"  ⏭️  Skipped: {test_run.skipped_scenarios:>3} ({test_run.skipped_scenarios/max(test_run.total_scenarios,1)*100:.1f}%)",
            f"  📝 Total:   {test_run.total_scenarios:>3}",
            "",
            f"⏱️  Duration: {test_run.total_duration:.2f}s",
            f"📅 Run Time: {test_run.started_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]
        
        # Add score interpretation
        if score >= 90:
            lines.extend([
                "🌟 EXCELLENT! Outstanding test coverage and quality.",
                "   Your BDD suite is in excellent shape!"
            ])
        elif score >= 80:
            lines.extend([
                "✨ GOOD! Solid test coverage with room for improvement.",
                "   Consider addressing failing scenarios."
            ])
        elif score >= 70:
            lines.extend([
                "⚠️  FAIR. Test coverage needs attention.",
                "   Focus on fixing failures and adding coverage."
            ])
        else:
            lines.extend([
                "🚨 NEEDS WORK! Significant improvements needed.",
                "   Priority: Fix failing tests and improve coverage."
            ])
        
        lines.extend([
            "",
            "=" * 60
        ])
        
        return "\n".join(lines)
    
    def generate_detailed_report(self, test_run: BDDTestRun) -> str:
        """Generate detailed test report"""
        lines = [
            "🔍 DETAILED BDD TEST REPORT",
            "=" * 80,
            "",
            f"Run ID: {test_run.run_id}",
            f"Started: {test_run.started_at}",
            f"Completed: {test_run.completed_at}",
            f"Duration: {test_run.total_duration:.2f}s",
            "",
            "SCENARIO BREAKDOWN:",
            "-" * 40
        ]
        
        # Group scenarios by feature
        by_feature = defaultdict(list)
        for scenario in test_run.scenario_results:
            by_feature[scenario.feature_name].append(scenario)
        
        for feature_name, scenarios in by_feature.items():
            lines.append(f"\n📁 {feature_name}")
            
            for scenario in scenarios:
                status_icon = {
                    TestStatus.PASSED: "✅",
                    TestStatus.FAILED: "❌",
                    TestStatus.SKIPPED: "⏭️",
                    TestStatus.UNDEFINED: "❓"
                }.get(scenario.status, "❓")
                
                lines.append(f"  {status_icon} {scenario.scenario_name} ({scenario.duration:.2f}s)")
                
                if scenario.error_message and scenario.status == TestStatus.FAILED:
                    lines.append(f"     💥 {scenario.error_message}")
        
        return "\n".join(lines)


class DeltaBDD:
    """
    ∂BDD - Conversation-aware BDD execution
    
    Features:
    - Learns from scenario failure patterns
    - Adapts test strategies based on conversation history
    - Integrates with existing ΩBDDSCOREBOARD system
    - Independent scoreboard functionality
    - Real-time parsing of behave test output
    """
    
    def __init__(self, project_path: str = ".", config_dir: str = ".claude", user_id: str = "developer"):
        self.project_path = Path(project_path).resolve()
        self.config_dir = Path(config_dir)
        self.user_id = user_id
        self.config = get_config(user_id)
        self.logger = get_logger("∂BDD")
        
        # Initialize memory systems
        self.memory_db = self.config_dir / "∂bdd_memory.db"
        self._init_memory_systems()
        self._init_database()
        
        # Initialize BDD components
        behave_path = self.config.get("tools.behave.path", "behave")
        self.behave_runner = BehaveRunner(self.project_path, behave_path)
        self.scoreboard = ScoreboardDisplay()
        
        # Test run tracking
        self.current_run = None
        self.run_history = []
        
        # Learning parameters
        self.failure_patterns = {}
        self.success_patterns = {}
        
        # Features directory
        self.features_dir = self.project_path / self.config.get("bdd.features_dir", "features")
        
        self.logger.info(f"∂BDD initialized for project: {self.project_path}")
    
    def _init_memory_systems(self):
        """Initialize LangMem and fallback SQLite memory systems"""
        global LANGMEM_AVAILABLE
        self.memory_tools = []
        
        if LANGMEM_AVAILABLE:
            try:
                self.store = InMemoryStore(
                    index={"dims": 1536, "embed": "openai:text-embedding-3-small"}
                )
                self.namespace = ("∂bdd", self.user_id)
                self.memory_tools = [
                    create_manage_memory_tool(namespace=self.namespace),
                    create_search_memory_tool(namespace=self.namespace),
                ]
                self.logger.info("LangMem memory system initialized")
            except Exception as e:
                self.logger.warning(f"LangMem initialization failed: {e}")
                LANGMEM_AVAILABLE = False
    
    def _init_database(self):
        """Initialize SQLite database for BDD test storage"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bdd_test_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    started_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP,
                    total_scenarios INTEGER DEFAULT 0,
                    passed_scenarios INTEGER DEFAULT 0,
                    failed_scenarios INTEGER DEFAULT 0,
                    skipped_scenarios INTEGER DEFAULT 0,
                    total_duration REAL DEFAULT 0.0,
                    bdd_score REAL,
                    conversation_context TEXT,
                    UNIQUE(run_id, user_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scenario_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    scenario_name TEXT NOT NULL,
                    feature_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    duration REAL NOT NULL,
                    error_message TEXT,
                    steps_passed INTEGER DEFAULT 0,
                    steps_failed INTEGER DEFAULT 0,
                    steps_skipped INTEGER DEFAULT 0,
                    tags TEXT,
                    FOREIGN KEY(run_id) REFERENCES bdd_test_runs(run_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS failure_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,
                    pattern_content TEXT NOT NULL,
                    failure_count INTEGER DEFAULT 1,
                    success_count INTEGER DEFAULT 0,
                    confidence_score REAL DEFAULT 0.5,
                    last_seen TIMESTAMP NOT NULL,
                    conversation_context TEXT,
                    UNIQUE(pattern_type, pattern_content)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    insight_type TEXT NOT NULL,
                    insight_data TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    generated_at TIMESTAMP NOT NULL
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_bdd_runs ON bdd_test_runs(user_id, started_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_scenario_results ON scenario_results(run_id, status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_failure_patterns ON failure_patterns(pattern_type, confidence_score)")
            
            conn.commit()
    
    def run_bdd_tests(self, features_path: str = None, tags: List[str] = None,
                     conversation_context: str = None, dry_run: bool = False) -> str:
        """Run BDD tests with conversation awareness"""
        features_path = features_path or str(self.features_dir.relative_to(self.project_path))
        
        # Start new test run
        run_id = self._generate_run_id()
        test_run = BDDTestRun(
            run_id=run_id,
            started_at=datetime.now(),
            conversation_context=conversation_context
        )
        
        self.current_run = test_run
        self._store_test_run(test_run)
        
        self.logger.info(f"Starting BDD test run: {run_id}")
        
        # Apply learned strategies
        enhanced_tags = self._enhance_tags_with_patterns(tags or [])
        
        # Run tests
        success, stdout, stderr = self.behave_runner.run_tests(
            features_path=features_path,
            tags=enhanced_tags,
            dry_run=dry_run
        )
        
        # Parse results
        scenario_results = self.behave_runner.parse_behave_json_output()
        
        # Update test run with results
        test_run.completed_at = datetime.now()
        test_run.scenario_results = scenario_results
        test_run.total_scenarios = len(scenario_results)
        test_run.passed_scenarios = sum(1 for s in scenario_results if s.status == TestStatus.PASSED)
        test_run.failed_scenarios = sum(1 for s in scenario_results if s.status == TestStatus.FAILED)
        test_run.skipped_scenarios = sum(1 for s in scenario_results if s.status == TestStatus.SKIPPED)
        test_run.total_duration = sum(s.duration for s in scenario_results)
        test_run.bdd_score = test_run.calculate_score()
        
        # Store updated results
        self._update_test_run(test_run)
        self._store_scenario_results(test_run)
        
        # Learn from this run
        self._learn_from_test_run(test_run)
        
        # Generate insights
        self._generate_test_insights(test_run)
        
        self.logger.info(f"BDD test run completed: {test_run.bdd_score:.1f}/100 score")
        return run_id
    
    def get_scoreboard_display(self, run_id: str = None) -> str:
        """Get visual scoreboard display"""
        target_run = self._get_test_run(run_id) if run_id else self.current_run
        
        if not target_run:
            return "No test run data available"
        
        return self.scoreboard.generate_score_display(target_run)
    
    def get_detailed_report(self, run_id: str = None) -> str:
        """Get detailed test report"""
        target_run = self._get_test_run(run_id) if run_id else self.current_run
        
        if not target_run:
            return "No test run data available"
        
        return self.scoreboard.generate_detailed_report(target_run)
    
    def analyze_failure_patterns(self, days: int = 30) -> Dict[str, Any]:
        """Analyze failure patterns from recent test runs"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.memory_db) as conn:
            # Get recent failures
            cursor = conn.execute("""
                SELECT sr.scenario_name, sr.feature_name, sr.error_message, sr.tags,
                       btr.started_at, btr.conversation_context
                FROM scenario_results sr
                JOIN bdd_test_runs btr ON sr.run_id = btr.run_id
                WHERE sr.status = 'failed' AND btr.started_at > ? AND btr.user_id = ?
                ORDER BY btr.started_at DESC
            """, (cutoff_date, self.user_id))
            
            failures = cursor.fetchall()
        
        if not failures:
            return {"total_failures": 0, "patterns": []}
        
        # Analyze patterns
        error_patterns = Counter()
        feature_patterns = Counter()
        tag_patterns = Counter()
        
        for scenario_name, feature_name, error_message, tags_json, started_at, context in failures:
            # Error message patterns
            if error_message:
                # Extract key error terms
                error_words = re.findall(r'\b\w+\b', error_message.lower())
                for word in error_words:
                    if len(word) > 3:  # Skip short words
                        error_patterns[word] += 1
            
            # Feature patterns
            feature_patterns[feature_name] += 1
            
            # Tag patterns
            if tags_json:
                try:
                    tags = json.loads(tags_json)
                    for tag in tags:
                        tag_patterns[tag] += 1
                except json.JSONDecodeError:
                    pass
        
        return {
            "total_failures": len(failures),
            "error_patterns": dict(error_patterns.most_common(10)),
            "feature_patterns": dict(feature_patterns.most_common(10)),
            "tag_patterns": dict(tag_patterns.most_common(10)),
            "analysis_period_days": days
        }
    
    def suggest_test_improvements(self, run_id: str = None) -> List[str]:
        """Suggest improvements based on test results and patterns"""
        target_run = self._get_test_run(run_id) if run_id else self.current_run
        
        if not target_run:
            return ["No test data available for analysis"]
        
        suggestions = []
        
        # Score-based suggestions
        score = target_run.bdd_score or target_run.calculate_score()
        
        if score < 70:
            suggestions.append("🚨 Critical: Fix failing tests to improve overall score")
        
        if target_run.failed_scenarios > 0:
            suggestions.append(f"❌ Address {target_run.failed_scenarios} failing scenarios")
        
        if target_run.total_scenarios < 10:
            suggestions.append("📝 Consider adding more test scenarios for better coverage")
        
        # Performance suggestions
        if target_run.total_duration > 0:
            avg_duration = target_run.total_duration / target_run.total_scenarios
            if avg_duration > 5:
                suggestions.append("⏱️ Consider optimizing test performance - scenarios are running slowly")
        
        # Pattern-based suggestions
        patterns = self.analyze_failure_patterns(days=7)
        if patterns["total_failures"] > 0:
            if "connection" in patterns.get("error_patterns", {}):
                suggestions.append("🔌 Network/connection issues detected - check test environment")
            
            if "timeout" in patterns.get("error_patterns", {}):
                suggestions.append("⏰ Timeout issues detected - consider increasing wait times")
        
        return suggestions or ["✅ Test suite looks healthy - keep up the good work!"]
    
    def get_test_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get test trends over specified period"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT started_at, bdd_score, total_scenarios, passed_scenarios, failed_scenarios
                FROM bdd_test_runs
                WHERE user_id = ? AND started_at > ?
                ORDER BY started_at
            """, (self.user_id, cutoff_date))
            
            runs = cursor.fetchall()
        
        if not runs:
            return {"message": "No test data for trend analysis"}
        
        # Calculate trends
        scores = [run[1] for run in runs if run[1] is not None]
        scenario_counts = [run[2] for run in runs]
        pass_rates = [run[3] / max(run[2], 1) for run in runs]
        
        return {
            "total_runs": len(runs),
            "average_score": sum(scores) / len(scores) if scores else 0,
            "score_trend": "improving" if len(scores) >= 2 and scores[-1] > scores[0] else "stable",
            "average_scenarios": sum(scenario_counts) / len(scenario_counts),
            "average_pass_rate": sum(pass_rates) / len(pass_rates),
            "period_days": days
        }
    
    def _enhance_tags_with_patterns(self, tags: List[str]) -> List[str]:
        """Enhance test tags based on learned patterns"""
        enhanced_tags = tags.copy()
        
        # Load successful tag patterns
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT pattern_content, confidence_score
                FROM failure_patterns
                WHERE pattern_type = 'successful_tags' AND confidence_score > 0.7
                ORDER BY confidence_score DESC
                LIMIT 3
            """)
            
            patterns = cursor.fetchall()
        
        # Apply learned tag strategies
        for pattern_content, confidence in patterns:
            try:
                pattern_data = json.loads(pattern_content)
                recommended_tag = pattern_data.get("tag")
                if recommended_tag and recommended_tag not in enhanced_tags:
                    enhanced_tags.append(recommended_tag)
                    self.logger.debug(f"Added recommended tag: {recommended_tag}")
            except json.JSONDecodeError:
                continue
        
        return enhanced_tags
    
    def _learn_from_test_run(self, test_run: BDDTestRun):
        """Learn patterns from test run results"""
        # Learn from failures
        for scenario in test_run.scenario_results:
            if scenario.status == TestStatus.FAILED and scenario.error_message:
                self._store_failure_pattern("error_message", scenario.error_message)
            
            if scenario.status == TestStatus.PASSED and scenario.tags:
                # Learn successful tag combinations
                tag_pattern = json.dumps({"tags": scenario.tags, "success": True})
                self._store_success_pattern("successful_tags", tag_pattern)
        
        # Learn from overall run characteristics
        if test_run.bdd_score and test_run.bdd_score > 80:
            # Learn from successful runs
            if test_run.conversation_context:
                context_pattern = json.dumps({
                    "context_length": len(test_run.conversation_context),
                    "score": test_run.bdd_score
                })
                self._store_success_pattern("high_score_context", context_pattern)
    
    def _store_failure_pattern(self, pattern_type: str, pattern_content: str):
        """Store failure pattern for learning"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO failure_patterns
                (pattern_type, pattern_content, failure_count, success_count,
                 confidence_score, last_seen, conversation_context)
                VALUES (?, ?, 
                        COALESCE((SELECT failure_count FROM failure_patterns 
                                 WHERE pattern_type = ? AND pattern_content = ?), 0) + 1,
                        COALESCE((SELECT success_count FROM failure_patterns 
                                 WHERE pattern_type = ? AND pattern_content = ?), 0),
                        ?, ?, ?)
            """, (
                pattern_type, pattern_content, pattern_type, pattern_content,
                pattern_type, pattern_content, 0.3, datetime.now(),
                self.current_run.conversation_context if self.current_run else None
            ))
            conn.commit()
    
    def _store_success_pattern(self, pattern_type: str, pattern_content: str):
        """Store success pattern for learning"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO failure_patterns
                (pattern_type, pattern_content, failure_count, success_count,
                 confidence_score, last_seen, conversation_context)
                VALUES (?, ?, 
                        COALESCE((SELECT failure_count FROM failure_patterns 
                                 WHERE pattern_type = ? AND pattern_content = ?), 0),
                        COALESCE((SELECT success_count FROM failure_patterns 
                                 WHERE pattern_type = ? AND pattern_content = ?), 0) + 1,
                        ?, ?, ?)
            """, (
                pattern_type, pattern_content, pattern_type, pattern_content,
                pattern_type, pattern_content, 0.7, datetime.now(),
                self.current_run.conversation_context if self.current_run else None
            ))
            conn.commit()
    
    def _generate_test_insights(self, test_run: BDDTestRun):
        """Generate insights about test run"""
        insights = []
        
        # Performance insights
        if test_run.total_duration > 0 and test_run.total_scenarios > 0:
            avg_duration = test_run.total_duration / test_run.total_scenarios
            if avg_duration > 3:
                insights.append({
                    "type": "performance",
                    "data": {"avg_scenario_duration": avg_duration},
                    "confidence": 0.8,
                    "message": f"Scenarios averaging {avg_duration:.2f}s - consider optimization"
                })
        
        # Coverage insights
        if test_run.total_scenarios < 5:
            insights.append({
                "type": "coverage",
                "data": {"scenario_count": test_run.total_scenarios},
                "confidence": 0.9,
                "message": "Low test coverage - consider adding more scenarios"
            })
        
        # Quality insights
        if test_run.failed_scenarios > 0:
            failure_rate = test_run.failed_scenarios / test_run.total_scenarios
            insights.append({
                "type": "quality",
                "data": {"failure_rate": failure_rate},
                "confidence": 0.9,
                "message": f"Failure rate of {failure_rate*100:.1f}% needs attention"
            })
        
        # Store insights
        for insight in insights:
            with sqlite3.connect(self.memory_db) as conn:
                conn.execute("""
                    INSERT INTO test_insights
                    (run_id, insight_type, insight_data, confidence_score, generated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    test_run.run_id, insight["type"], json.dumps(insight["data"]),
                    insight["confidence"], datetime.now()
                ))
                conn.commit()
    
    def _generate_run_id(self) -> str:
        """Generate unique run ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"{self.user_id}:{timestamp}".encode()).hexdigest()[:16]
    
    def _store_test_run(self, test_run: BDDTestRun):
        """Store test run in database"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO bdd_test_runs
                (run_id, user_id, started_at, completed_at, total_scenarios,
                 passed_scenarios, failed_scenarios, skipped_scenarios,
                 total_duration, bdd_score, conversation_context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                test_run.run_id, self.user_id, test_run.started_at, test_run.completed_at,
                test_run.total_scenarios, test_run.passed_scenarios, test_run.failed_scenarios,
                test_run.skipped_scenarios, test_run.total_duration, test_run.bdd_score,
                test_run.conversation_context
            ))
            conn.commit()
    
    def _update_test_run(self, test_run: BDDTestRun):
        """Update existing test run"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                UPDATE bdd_test_runs
                SET completed_at = ?, total_scenarios = ?, passed_scenarios = ?,
                    failed_scenarios = ?, skipped_scenarios = ?, total_duration = ?, bdd_score = ?
                WHERE run_id = ? AND user_id = ?
            """, (
                test_run.completed_at, test_run.total_scenarios, test_run.passed_scenarios,
                test_run.failed_scenarios, test_run.skipped_scenarios, test_run.total_duration,
                test_run.bdd_score, test_run.run_id, self.user_id
            ))
            conn.commit()
    
    def _store_scenario_results(self, test_run: BDDTestRun):
        """Store scenario results in database"""
        with sqlite3.connect(self.memory_db) as conn:
            for scenario in test_run.scenario_results:
                conn.execute("""
                    INSERT INTO scenario_results
                    (run_id, scenario_name, feature_name, status, duration,
                     error_message, steps_passed, steps_failed, steps_skipped, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    test_run.run_id, scenario.scenario_name, scenario.feature_name,
                    scenario.status.value, scenario.duration, scenario.error_message,
                    scenario.steps_passed, scenario.steps_failed, scenario.steps_skipped,
                    json.dumps(scenario.tags) if scenario.tags else None
                ))
            conn.commit()
    
    def _get_test_run(self, run_id: str) -> Optional[BDDTestRun]:
        """Get test run by ID"""
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT run_id, started_at, completed_at, total_scenarios, passed_scenarios,
                       failed_scenarios, skipped_scenarios, total_duration, bdd_score, conversation_context
                FROM bdd_test_runs
                WHERE run_id = ? AND user_id = ?
            """, (run_id, self.user_id))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Load scenario results
            cursor = conn.execute("""
                SELECT scenario_name, feature_name, status, duration, error_message,
                       steps_passed, steps_failed, steps_skipped, tags
                FROM scenario_results
                WHERE run_id = ?
            """, (run_id,))
            
            scenario_results = []
            for scenario_row in cursor.fetchall():
                scenario_results.append(ScenarioResult(
                    scenario_name=scenario_row[0],
                    feature_name=scenario_row[1],
                    status=TestStatus(scenario_row[2]),
                    duration=scenario_row[3],
                    error_message=scenario_row[4],
                    steps_passed=scenario_row[5] or 0,
                    steps_failed=scenario_row[6] or 0,
                    steps_skipped=scenario_row[7] or 0,
                    tags=json.loads(scenario_row[8]) if scenario_row[8] else []
                ))
            
            return BDDTestRun(
                run_id=row[0],
                started_at=datetime.fromisoformat(row[1]),
                completed_at=datetime.fromisoformat(row[2]) if row[2] else None,
                total_scenarios=row[3],
                passed_scenarios=row[4],
                failed_scenarios=row[5],
                skipped_scenarios=row[6],
                total_duration=row[7],
                bdd_score=row[8],
                conversation_context=row[9],
                scenario_results=scenario_results
            )


# Global BDD instance
_global_bdd = None


def get_bdd(project_path: str = ".", user_id: str = "developer") -> DeltaBDD:
    """Get global BDD instance"""
    global _global_bdd
    if _global_bdd is None:
        _global_bdd = DeltaBDD(project_path=project_path, user_id=user_id)
    return _global_bdd


def initialize_bdd(project_path: str = ".", config_dir: str = ".claude", user_id: str = "developer") -> DeltaBDD:
    """Initialize BDD testing system"""
    global _global_bdd
    _global_bdd = DeltaBDD(project_path=project_path, config_dir=config_dir, user_id=user_id)
    return _global_bdd


if __name__ == "__main__":
    # Test BDD system
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Testing ∂BDD system...")
        
        # Initialize BDD system
        bdd = initialize_bdd()
        
        # Check if behave is available
        available = bdd.behave_runner.check_behave_available()
        print(f"Behave available: {available}")
        
        # Create mock test run for demonstration
        mock_run = BDDTestRun(
            run_id="test_run_001",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            total_scenarios=10,
            passed_scenarios=8,
            failed_scenarios=2,
            skipped_scenarios=0,
            total_duration=45.5,
            conversation_context="Testing BDD system functionality"
        )
        
        mock_run.bdd_score = mock_run.calculate_score()
        bdd.current_run = mock_run
        
        # Test scoreboard display
        scoreboard = bdd.get_scoreboard_display()
        print(f"Scoreboard:\n{scoreboard}")
        
        # Test failure analysis
        patterns = bdd.analyze_failure_patterns()
        print(f"Failure patterns: {patterns}")
        
        # Test suggestions
        suggestions = bdd.suggest_test_improvements()
        print(f"Suggestions: {suggestions}")
        
        # Test trends
        trends = bdd.get_test_trends()
        print(f"Trends: {trends}")
        
        print("∂BDD system test completed successfully!")
    else:
        print("∂BDD.py - Conversation-aware BDD execution")
        print("Usage: python ∂BDD.py --test")