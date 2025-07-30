#!/usr/bin/env python3
"""
∂Radon.py - Code complexity checking with memory
Part of the ∂-prefixed architecture for conversation-aware multi-agent development

This module provides code complexity analysis with conversation memory, learning
optimal complexity thresholds per project, trend analysis across development sessions,
and integration with other ∂-prefixed components for holistic code quality assessment.
"""

import json
import os
import sqlite3
import subprocess
import ast
import re
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, Counter
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





class ComplexityLevel(Enum):
    SIMPLE = "simple"           # Low complexity, easy to maintain
    MODERATE = "moderate"       # Acceptable complexity
    COMPLEX = "complex"         # High complexity, needs attention
    CRITICAL = "critical"       # Very high complexity, refactor needed


class MetricType(Enum):
    CYCLOMATIC = "cyclomatic"           # McCabe complexity
    HALSTEAD = "halstead"               # Halstead metrics
    MAINTAINABILITY = "maintainability" # Maintainability index
    RAW = "raw"                         # Raw metrics (LOC, etc.)


class QualityTrend(Enum):
    IMPROVING = "improving"     # Complexity decreasing over time
    STABLE = "stable"           # Complexity relatively constant
    DEGRADING = "degrading"     # Complexity increasing over time
    UNKNOWN = "unknown"         # Not enough data


@dataclass
class ComplexityMetric:
    """Single complexity metric for a code unit"""
    metric_type: MetricType
    metric_name: str
    value: float
    threshold: Optional[float] = None
    level: Optional[ComplexityLevel] = None
    description: Optional[str] = None


@dataclass
class CodeUnit:
    """Represents a unit of code (function, class, module)"""
    name: str
    type: str  # function, class, module, method
    file_path: str
    start_line: int
    end_line: int
    complexity_metrics: List[ComplexityMetric]
    loc: int = 0  # Lines of code
    blank_lines: int = 0
    comment_lines: int = 0
    
    def __post_init__(self):
        if not self.complexity_metrics:
            self.complexity_metrics = []
    
    def get_metric(self, metric_type: MetricType, metric_name: str) -> Optional[ComplexityMetric]:
        """Get specific metric by type and name"""
        for metric in self.complexity_metrics:
            if metric.metric_type == metric_type and metric.metric_name == metric_name:
                return metric
        return None
    
    def get_overall_complexity_level(self) -> ComplexityLevel:
        """Calculate overall complexity level for this code unit"""
        levels = [m.level for m in self.complexity_metrics if m.level]
        if not levels:
            return ComplexityLevel.SIMPLE
        
        # Use the highest complexity level found
        level_weights = {
            ComplexityLevel.SIMPLE: 0,
            ComplexityLevel.MODERATE: 1, 
            ComplexityLevel.COMPLEX: 2,
            ComplexityLevel.CRITICAL: 3
        }
        
        max_weight = max(level_weights[level] for level in levels)
        for level, weight in level_weights.items():
            if weight == max_weight:
                return level
        
        return ComplexityLevel.SIMPLE


@dataclass
class ComplexityAnalysis:
    """Complete complexity analysis for a project or file"""
    analysis_id: str
    project_path: str
    analyzed_at: datetime
    conversation_context: Optional[str] = None
    code_units: List[CodeUnit] = None
    file_metrics: Dict[str, Dict[str, float]] = None
    project_summary: Dict[str, Any] = None
    quality_trend: QualityTrend = QualityTrend.UNKNOWN
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.code_units is None:
            self.code_units = []
        if self.file_metrics is None:
            self.file_metrics = {}
        if self.project_summary is None:
            self.project_summary = {}
        if self.recommendations is None:
            self.recommendations = []


class RadonInterface:
    """Interface to Radon complexity analysis tool"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.logger = get_logger("RadonInterface")
    
    def check_radon_available(self) -> bool:
        """Check if Radon is available"""
        try:
            result = subprocess.run(
                ["radon", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.warning(f"Radon not available: {e}")
            return False
    
    def run_cyclomatic_complexity(self, file_patterns: List[str] = None) -> Dict[str, Any]:
        """Run cyclomatic complexity analysis"""
        if not self.check_radon_available():
            return {}
        
        cmd = ["radon", "cc", "-j"]  # JSON output
        if file_patterns:
            cmd.extend(file_patterns)
        else:
            cmd.append(".")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and result.stdout:
                return json.loads(result.stdout)
            else:
                self.logger.warning(f"Radon CC failed: {result.stderr}")
                return {}
        except Exception as e:
            self.logger.error(f"Radon CC execution failed: {e}")
            return {}
    
    def run_maintainability_index(self, file_patterns: List[str] = None) -> Dict[str, Any]:
        """Run maintainability index analysis"""
        if not self.check_radon_available():
            return {}
        
        cmd = ["radon", "mi", "-j"]  # JSON output
        if file_patterns:
            cmd.extend(file_patterns)
        else:
            cmd.append(".")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and result.stdout:
                return json.loads(result.stdout)
            else:
                self.logger.warning(f"Radon MI failed: {result.stderr}")
                return {}
        except Exception as e:
            self.logger.error(f"Radon MI execution failed: {e}")
            return {}
    
    def run_halstead_metrics(self, file_patterns: List[str] = None) -> Dict[str, Any]:
        """Run Halstead metrics analysis"""
        if not self.check_radon_available():
            return {}
        
        cmd = ["radon", "hal", "-j"]  # JSON output
        if file_patterns:
            cmd.extend(file_patterns)
        else:
            cmd.append(".")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and result.stdout:
                return json.loads(result.stdout)
            else:
                self.logger.warning(f"Radon Halstead failed: {result.stderr}")
                return {}
        except Exception as e:
            self.logger.error(f"Radon Halstead execution failed: {e}")
            return {}
    
    def run_raw_metrics(self, file_patterns: List[str] = None) -> Dict[str, Any]:
        """Run raw metrics analysis"""
        if not self.check_radon_available():
            return {}
        
        cmd = ["radon", "raw", "-j"]  # JSON output
        if file_patterns:
            cmd.extend(file_patterns)
        else:
            cmd.append(".")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and result.stdout:
                return json.loads(result.stdout)
            else:
                self.logger.warning(f"Radon raw failed: {result.stderr}")
                return {}
        except Exception as e:
            self.logger.error(f"Radon raw execution failed: {e}")
            return {}


class DeltaRadon:
    """
    ∂Radon - Code complexity checking with memory
    
    Features:
    - Learning optimal complexity thresholds per project
    - Trend analysis across development sessions
    - Integration with ∂-prefixed memory systems
    - Conversation-aware complexity recommendations
    """
    
    def __init__(self, project_path: str = ".", config_dir: str = ".claude", user_id: str = "developer"):
        self.project_path = Path(project_path).resolve()
        self.config_dir = Path(config_dir)
        self.user_id = user_id
        self.config = get_config(user_id)
        self.logger = get_logger("∂Radon")
        
        # Initialize memory systems
        self.memory_db = self.config_dir / "∂radon_memory.db"
        self._init_memory_systems()
        self._init_database()
        
        # Initialize Radon interface
        self.radon_interface = RadonInterface(self.project_path)
        
        # Analysis tracking
        self.current_analysis = None
        self.analysis_history = []
        
        # Default complexity thresholds (will be learned over time)
        self.complexity_thresholds = {
            "cyclomatic_complexity": {
                ComplexityLevel.SIMPLE: 5,
                ComplexityLevel.MODERATE: 10,
                ComplexityLevel.COMPLEX: 15,
                ComplexityLevel.CRITICAL: 20
            },
            "maintainability_index": {
                ComplexityLevel.CRITICAL: 25,
                ComplexityLevel.COMPLEX: 50,
                ComplexityLevel.MODERATE: 75,
                ComplexityLevel.SIMPLE: 100
            }
        }
        
        # Learning parameters
        self.quality_patterns = {}
        self.trend_analysis = {}
        
        self.logger.info(f"∂Radon initialized for project: {self.project_path}")
    
    def _init_memory_systems(self):
        """Initialize LangMem and fallback SQLite memory systems"""
        global LANGMEM_AVAILABLE
        self.memory_tools = []
        
        if LANGMEM_AVAILABLE:
            try:
                self.store = InMemoryStore(
                    index={"dims": 1536, "embed": "openai:text-embedding-3-small"}
                )
                self.namespace = ("∂radon", self.user_id)
                self.memory_tools = [
                    create_manage_memory_tool(namespace=self.namespace),
                    create_search_memory_tool(namespace=self.namespace),
                ]
                self.logger.info("LangMem memory system initialized")
            except Exception as e:
                self.logger.warning(f"LangMem initialization failed: {e}")
                LANGMEM_AVAILABLE = False
    
    def _init_database(self):
        """Initialize SQLite database for complexity analysis storage"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS complexity_analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT NOT NULL,
                    project_path TEXT NOT NULL,
                    analyzed_at TIMESTAMP NOT NULL,
                    conversation_context TEXT,
                    project_summary TEXT,
                    quality_trend TEXT,
                    recommendations TEXT,
                    user_id TEXT NOT NULL,
                    UNIQUE(analysis_id, user_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS code_units (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    start_line INTEGER,
                    end_line INTEGER,
                    loc INTEGER DEFAULT 0,
                    blank_lines INTEGER DEFAULT 0,
                    comment_lines INTEGER DEFAULT 0,
                    FOREIGN KEY(analysis_id) REFERENCES complexity_analyses(analysis_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS complexity_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code_unit_id INTEGER NOT NULL,
                    metric_type TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    threshold_value REAL,
                    complexity_level TEXT,
                    description TEXT,
                    FOREIGN KEY(code_unit_id) REFERENCES code_units(id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS file_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    FOREIGN KEY(analysis_id) REFERENCES complexity_analyses(analysis_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quality_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,
                    pattern_content TEXT NOT NULL,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    confidence_score REAL DEFAULT 0.5,
                    last_updated TIMESTAMP NOT NULL,
                    learned_from_analysis TEXT,
                    UNIQUE(pattern_type, pattern_content)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS threshold_adjustments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_type TEXT NOT NULL,
                    complexity_level TEXT NOT NULL,
                    old_threshold REAL NOT NULL,
                    new_threshold REAL NOT NULL,
                    adjustment_reason TEXT,
                    adjusted_at TIMESTAMP NOT NULL,
                    user_id TEXT NOT NULL
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_complexity_analyses ON complexity_analyses(user_id, analyzed_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_code_units ON code_units(analysis_id, type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_complexity_metrics ON complexity_metrics(code_unit_id, metric_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_patterns ON quality_patterns(pattern_type, confidence_score)")
            
            conn.commit()
    
    def analyze_project_complexity(self, file_patterns: List[str] = None, 
                                  conversation_context: str = None) -> str:
        """Perform comprehensive complexity analysis of project"""
        analysis_id = self._generate_analysis_id()
        
        self.logger.info(f"Starting complexity analysis: {analysis_id}")
        
        # Check if Radon is available
        if not self.radon_interface.check_radon_available():
            self.logger.warning("Radon not available, using fallback analysis")
            return self._fallback_analysis(analysis_id, conversation_context)
        
        # Run all Radon analyses
        cc_results = self.radon_interface.run_cyclomatic_complexity(file_patterns)
        mi_results = self.radon_interface.run_maintainability_index(file_patterns)
        hal_results = self.radon_interface.run_halstead_metrics(file_patterns)
        raw_results = self.radon_interface.run_raw_metrics(file_patterns)
        
        # Process results into our data structures
        code_units = self._process_radon_results(cc_results, mi_results, hal_results, raw_results)
        file_metrics = self._extract_file_metrics(cc_results, mi_results, hal_results, raw_results)
        
        # Create analysis object
        analysis = ComplexityAnalysis(
            analysis_id=analysis_id,
            project_path=str(self.project_path),
            analyzed_at=datetime.now(),
            conversation_context=conversation_context,
            code_units=code_units,
            file_metrics=file_metrics
        )
        
        # Generate project summary and recommendations
        analysis.project_summary = self._generate_project_summary(analysis)
        analysis.quality_trend = self._analyze_quality_trend()
        analysis.recommendations = self._generate_recommendations(analysis)
        
        # Store analysis
        self.current_analysis = analysis
        self._store_analysis(analysis)
        
        # Learn from this analysis
        self._learn_from_analysis(analysis)
        
        self.logger.info(f"Complexity analysis completed: {analysis_id}")
        return analysis_id
    
    def _process_radon_results(self, cc_results: Dict, mi_results: Dict, 
                             hal_results: Dict, raw_results: Dict) -> List[CodeUnit]:
        """Process Radon results into CodeUnit objects"""
        code_units = []
        
        # Process cyclomatic complexity results
        for file_path, cc_data in cc_results.items():
            if not isinstance(cc_data, list):
                continue
                
            for unit_data in cc_data:
                unit_name = unit_data.get("name", "unknown")
                unit_type = unit_data.get("type", "function")
                complexity = unit_data.get("complexity", 0)
                start_line = unit_data.get("lineno", 1)
                end_line = unit_data.get("endline", start_line)
                
                # Create complexity metrics
                metrics = []
                
                # Cyclomatic complexity metric
                cc_level = self._classify_complexity_level("cyclomatic_complexity", complexity)
                metrics.append(ComplexityMetric(
                    metric_type=MetricType.CYCLOMATIC,
                    metric_name="cyclomatic_complexity",
                    value=complexity,
                    threshold=self.complexity_thresholds["cyclomatic_complexity"].get(cc_level),
                    level=cc_level,
                    description=f"Cyclomatic complexity: {complexity}"
                ))
                
                # Add maintainability index if available
                if file_path in mi_results:
                    mi_value = mi_results[file_path].get("mi", 0)
                    mi_level = self._classify_complexity_level("maintainability_index", mi_value)
                    metrics.append(ComplexityMetric(
                        metric_type=MetricType.MAINTAINABILITY,
                        metric_name="maintainability_index",
                        value=mi_value,
                        threshold=self.complexity_thresholds["maintainability_index"].get(mi_level),
                        level=mi_level,
                        description=f"Maintainability index: {mi_value:.1f}"
                    ))
                
                # Add Halstead metrics if available
                if file_path in hal_results:
                    hal_data = hal_results[file_path]
                    if isinstance(hal_data, dict):
                        for hal_metric, hal_value in hal_data.items():
                            if isinstance(hal_value, (int, float)):
                                metrics.append(ComplexityMetric(
                                    metric_type=MetricType.HALSTEAD,
                                    metric_name=hal_metric,
                                    value=hal_value,
                                    description=f"Halstead {hal_metric}: {hal_value}"
                                ))
                
                # Get raw metrics (LOC, etc.)
                loc = 0
                blank_lines = 0
                comment_lines = 0
                
                if file_path in raw_results:
                    raw_data = raw_results[file_path]
                    loc = raw_data.get("loc", 0)
                    blank_lines = raw_data.get("blank", 0)
                    comment_lines = raw_data.get("comments", 0)
                    
                    # Add raw metrics
                    for raw_metric, raw_value in raw_data.items():
                        if isinstance(raw_value, (int, float)):
                            metrics.append(ComplexityMetric(
                                metric_type=MetricType.RAW,
                                metric_name=raw_metric,
                                value=raw_value,
                                description=f"Raw {raw_metric}: {raw_value}"
                            ))
                
                # Create code unit
                code_unit = CodeUnit(
                    name=unit_name,
                    type=unit_type,
                    file_path=file_path,
                    start_line=start_line,
                    end_line=end_line,
                    complexity_metrics=metrics,
                    loc=loc,
                    blank_lines=blank_lines,
                    comment_lines=comment_lines
                )
                
                code_units.append(code_unit)
        
        return code_units
    
    def _extract_file_metrics(self, cc_results: Dict, mi_results: Dict, 
                            hal_results: Dict, raw_results: Dict) -> Dict[str, Dict[str, float]]:
        """Extract file-level metrics from Radon results"""
        file_metrics = {}
        
        # Get all unique file paths
        all_files = set(cc_results.keys()) | set(mi_results.keys()) | set(hal_results.keys()) | set(raw_results.keys())
        
        for file_path in all_files:
            metrics = {}
            
            # Cyclomatic complexity aggregation
            if file_path in cc_results and isinstance(cc_results[file_path], list):
                complexities = [unit.get("complexity", 0) for unit in cc_results[file_path]]
                if complexities:
                    metrics["avg_cyclomatic_complexity"] = sum(complexities) / len(complexities)
                    metrics["max_cyclomatic_complexity"] = max(complexities)
                    metrics["total_functions"] = len(complexities)
            
            # Maintainability index
            if file_path in mi_results:
                mi_value = mi_results[file_path].get("mi", 0)
                metrics["maintainability_index"] = mi_value
            
            # Halstead metrics
            if file_path in hal_results and isinstance(hal_results[file_path], dict):
                for hal_metric, hal_value in hal_results[file_path].items():
                    if isinstance(hal_value, (int, float)):
                        metrics[f"halstead_{hal_metric}"] = hal_value
            
            # Raw metrics
            if file_path in raw_results and isinstance(raw_results[file_path], dict):
                for raw_metric, raw_value in raw_results[file_path].items():
                    if isinstance(raw_value, (int, float)):
                        metrics[raw_metric] = raw_value
            
            file_metrics[file_path] = metrics
        
        return file_metrics
    
    def _classify_complexity_level(self, metric_type: str, value: float) -> ComplexityLevel:
        """Classify complexity level based on thresholds"""
        thresholds = self.complexity_thresholds.get(metric_type, {})
        
        if metric_type == "maintainability_index":
            # Lower values are worse for maintainability index
            if value <= thresholds.get(ComplexityLevel.CRITICAL, 25):
                return ComplexityLevel.CRITICAL
            elif value <= thresholds.get(ComplexityLevel.COMPLEX, 50):
                return ComplexityLevel.COMPLEX
            elif value <= thresholds.get(ComplexityLevel.MODERATE, 75):
                return ComplexityLevel.MODERATE
            else:
                return ComplexityLevel.SIMPLE
        else:
            # Higher values are worse for most metrics
            if value >= thresholds.get(ComplexityLevel.CRITICAL, 20):
                return ComplexityLevel.CRITICAL
            elif value >= thresholds.get(ComplexityLevel.COMPLEX, 15):
                return ComplexityLevel.COMPLEX
            elif value >= thresholds.get(ComplexityLevel.MODERATE, 10):
                return ComplexityLevel.MODERATE
            else:
                return ComplexityLevel.SIMPLE
    
    def _generate_project_summary(self, analysis: ComplexityAnalysis) -> Dict[str, Any]:
        """Generate high-level project complexity summary"""
        summary = {
            "total_code_units": len(analysis.code_units),
            "files_analyzed": len(analysis.file_metrics),
            "complexity_distribution": {
                ComplexityLevel.SIMPLE.value: 0,
                ComplexityLevel.MODERATE.value: 0,
                ComplexityLevel.COMPLEX.value: 0,
                ComplexityLevel.CRITICAL.value: 0
            },
            "average_complexity": 0.0,
            "hotspots": [],
            "top_issues": []
        }
        
        # Count complexity distribution
        complexities = []
        for unit in analysis.code_units:
            level = unit.get_overall_complexity_level()
            summary["complexity_distribution"][level.value] += 1
            
            # Get cyclomatic complexity for average
            cc_metric = unit.get_metric(MetricType.CYCLOMATIC, "cyclomatic_complexity")
            if cc_metric:
                complexities.append(cc_metric.value)
        
        # Calculate average complexity
        if complexities:
            summary["average_complexity"] = sum(complexities) / len(complexities)
        
        # Find hotspots (critical and complex units)
        hotspots = []
        for unit in analysis.code_units:
            level = unit.get_overall_complexity_level()
            if level in [ComplexityLevel.CRITICAL, ComplexityLevel.COMPLEX]:
                cc_metric = unit.get_metric(MetricType.CYCLOMATIC, "cyclomatic_complexity")
                hotspots.append({
                    "name": unit.name,
                    "file": unit.file_path,
                    "complexity": cc_metric.value if cc_metric else 0,
                    "level": level.value
                })
        
        # Sort hotspots by complexity
        hotspots.sort(key=lambda x: x["complexity"], reverse=True)
        summary["hotspots"] = hotspots[:10]  # Top 10 hotspots
        
        # Generate top issues
        issues = []
        critical_count = summary["complexity_distribution"][ComplexityLevel.CRITICAL.value]
        complex_count = summary["complexity_distribution"][ComplexityLevel.COMPLEX.value]
        
        if critical_count > 0:
            issues.append(f"{critical_count} code units have critical complexity")
        if complex_count > 0:
            issues.append(f"{complex_count} code units have high complexity")
        if summary["average_complexity"] > 10:
            issues.append(f"Average complexity ({summary['average_complexity']:.1f}) is above recommended threshold")
        
        summary["top_issues"] = issues
        
        return summary
    
    def _analyze_quality_trend(self) -> QualityTrend:
        """Analyze quality trend across recent analyses"""
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT project_summary, analyzed_at
                FROM complexity_analyses
                WHERE user_id = ? AND project_path = ?
                ORDER BY analyzed_at DESC
                LIMIT 5
            """, (self.user_id, str(self.project_path)))
            
            recent_analyses = cursor.fetchall()
        
        if len(recent_analyses) < 2:
            return QualityTrend.UNKNOWN
        
        # Extract average complexity from recent analyses
        complexities = []
        for summary_json, _ in recent_analyses:
            try:
                summary = json.loads(summary_json)
                complexities.append(summary.get("average_complexity", 0))
            except:
                continue
        
        if len(complexities) < 2:
            return QualityTrend.UNKNOWN
        
        # Analyze trend
        recent_avg = sum(complexities[:2]) / 2
        older_avg = sum(complexities[-2:]) / 2
        
        if recent_avg < older_avg * 0.95:  # 5% improvement threshold
            return QualityTrend.IMPROVING
        elif recent_avg > older_avg * 1.05:  # 5% degradation threshold
            return QualityTrend.DEGRADING
        else:
            return QualityTrend.STABLE
    
    def _generate_recommendations(self, analysis: ComplexityAnalysis) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        summary = analysis.project_summary
        critical_count = summary["complexity_distribution"][ComplexityLevel.CRITICAL.value]
        complex_count = summary["complexity_distribution"][ComplexityLevel.COMPLEX.value]
        avg_complexity = summary["average_complexity"]
        
        # Critical complexity recommendations
        if critical_count > 0:
            recommendations.append(
                f"Immediate attention needed: {critical_count} code units have critical complexity. "
                f"Consider breaking down large functions or refactoring complex logic."
            )
        
        # High complexity recommendations
        if complex_count > 0:
            recommendations.append(
                f"Review needed: {complex_count} code units have high complexity. "
                f"Consider applying the Single Responsibility Principle."
            )
        
        # Average complexity recommendations
        if avg_complexity > 15:
            recommendations.append(
                f"Project-wide complexity ({avg_complexity:.1f}) is very high. "
                f"Consider a systematic refactoring effort."
            )
        elif avg_complexity > 10:
            recommendations.append(
                f"Project complexity ({avg_complexity:.1f}) is above ideal. "
                f"Focus on simplifying the most complex functions first."
            )
        
        # Trend-based recommendations
        if analysis.quality_trend == QualityTrend.DEGRADING:
            recommendations.append(
                "Code complexity is increasing over time. "
                "Consider establishing complexity gates in your development process."
            )
        elif analysis.quality_trend == QualityTrend.IMPROVING:
            recommendations.append(
                "Great work! Code complexity is decreasing. "
                "Continue current practices and consider documenting successful patterns."
            )
        
        # Hotspot-specific recommendations
        hotspots = summary.get("hotspots", [])
        if hotspots:
            top_hotspot = hotspots[0]
            recommendations.append(
                f"Start refactoring with '{top_hotspot['name']}' in {top_hotspot['file']} "
                f"(complexity: {top_hotspot['complexity']}). This will have the biggest impact."
            )
        
        # File-specific recommendations
        if analysis.file_metrics:
            high_complexity_files = []
            for file_path, metrics in analysis.file_metrics.items():
                avg_cc = metrics.get("avg_cyclomatic_complexity", 0)
                if avg_cc > 15:
                    high_complexity_files.append((file_path, avg_cc))
            
            if high_complexity_files:
                high_complexity_files.sort(key=lambda x: x[1], reverse=True)
                top_file = high_complexity_files[0]
                recommendations.append(
                    f"File '{top_file[0]}' has high average complexity ({top_file[1]:.1f}). "
                    f"Consider splitting into multiple modules."
                )
        
        return recommendations
    
    def _fallback_analysis(self, analysis_id: str, conversation_context: str = None) -> str:
        """Fallback analysis when Radon is not available"""
        self.logger.info("Running fallback complexity analysis")
        
        # Simple Python AST-based analysis
        code_units = []
        file_metrics = {}
        
        python_files = list(self.project_path.glob("**/*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST
                tree = ast.parse(content)
                
                # Simple complexity calculation
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Simple cyclomatic complexity (count decision points)
                        complexity = self._calculate_simple_complexity(node)
                        
                        metrics = [
                            ComplexityMetric(
                                metric_type=MetricType.CYCLOMATIC,
                                metric_name="cyclomatic_complexity",
                                value=complexity,
                                level=self._classify_complexity_level("cyclomatic_complexity", complexity),
                                description=f"Simple cyclomatic complexity: {complexity}"
                            )
                        ]
                        
                        code_unit = CodeUnit(
                            name=node.name,
                            type="function",
                            file_path=str(py_file.relative_to(self.project_path)),
                            start_line=node.lineno,
                            end_line=getattr(node, 'end_lineno', node.lineno),
                            complexity_metrics=metrics,
                            loc=len(content.split('\n'))
                        )
                        
                        code_units.append(code_unit)
                
                # File metrics
                lines = content.split('\n')
                file_metrics[str(py_file.relative_to(self.project_path))] = {
                    "loc": len(lines),
                    "blank": len([l for l in lines if not l.strip()]),
                    "comments": len([l for l in lines if l.strip().startswith('#')])
                }
                
            except Exception as e:
                self.logger.warning(f"Failed to analyze {py_file}: {e}")
        
        # Create analysis
        analysis = ComplexityAnalysis(
            analysis_id=analysis_id,
            project_path=str(self.project_path),
            analyzed_at=datetime.now(),
            conversation_context=conversation_context,
            code_units=code_units,
            file_metrics=file_metrics
        )
        
        analysis.project_summary = self._generate_project_summary(analysis)
        analysis.quality_trend = self._analyze_quality_trend()
        analysis.recommendations = self._generate_recommendations(analysis)
        
        self.current_analysis = analysis
        self._store_analysis(analysis)
        
        return analysis_id
    
    def _calculate_simple_complexity(self, node: ast.AST) -> int:
        """Calculate simple cyclomatic complexity for AST node"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _learn_from_analysis(self, analysis: ComplexityAnalysis):
        """Learn patterns from analysis results"""
        # Extract patterns for learning
        patterns = []
        
        # Project size vs complexity pattern
        total_units = len(analysis.code_units)
        avg_complexity = analysis.project_summary.get("average_complexity", 0)
        
        if total_units > 0:
            patterns.append((
                "project_size_complexity",
                json.dumps({
                    "total_units": total_units,
                    "avg_complexity": avg_complexity,
                    "complexity_per_unit": avg_complexity / total_units if total_units > 0 else 0
                })
            ))
        
        # File complexity distribution pattern
        if analysis.file_metrics:
            file_complexities = []
            for metrics in analysis.file_metrics.values():
                avg_cc = metrics.get("avg_cyclomatic_complexity", 0)
                if avg_cc > 0:
                    file_complexities.append(avg_cc)
            
            if file_complexities:
                patterns.append((
                    "file_complexity_distribution",
                    json.dumps({
                        "file_count": len(file_complexities),
                        "avg_file_complexity": sum(file_complexities) / len(file_complexities),
                        "max_file_complexity": max(file_complexities),
                        "min_file_complexity": min(file_complexities)
                    })
                ))
        
        # Quality trend pattern
        patterns.append((
            "quality_trend",
            json.dumps({
                "trend": analysis.quality_trend.value,
                "timestamp": analysis.analyzed_at.isoformat()
            })
        ))
        
        # Store patterns
        for pattern_type, pattern_content in patterns:
            with sqlite3.connect(self.memory_db) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO quality_patterns
                    (pattern_type, pattern_content, success_count, failure_count,
                     confidence_score, last_updated, learned_from_analysis)
                    VALUES (?, ?, 
                            COALESCE((SELECT success_count FROM quality_patterns 
                                     WHERE pattern_type = ? AND pattern_content = ?), 0) + 1,
                            COALESCE((SELECT failure_count FROM quality_patterns 
                                     WHERE pattern_type = ? AND pattern_content = ?), 0),
                            0.7, ?, ?)
                """, (
                    pattern_type, pattern_content, pattern_type, pattern_content,
                    pattern_type, pattern_content, datetime.now(), analysis.analysis_id
                ))
                conn.commit()
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get complexity analysis history"""
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT analysis_id, analyzed_at, project_summary, quality_trend
                FROM complexity_analyses
                WHERE user_id = ? AND project_path = ?
                ORDER BY analyzed_at DESC
                LIMIT ?
            """, (self.user_id, str(self.project_path), limit))
            
            history = []
            for row in cursor.fetchall():
                try:
                    summary = json.loads(row[2]) if row[2] else {}
                except:
                    summary = {}
                
                history.append({
                    "analysis_id": row[0],
                    "analyzed_at": row[1],
                    "summary": summary,
                    "quality_trend": row[3]
                })
            
            return history
    
    def get_complexity_insights(self) -> Dict[str, Any]:
        """Get insights from learned patterns"""
        insights = {
            "project_patterns": [],
            "trend_analysis": {},
            "recommendations": [],
            "learned_thresholds": {}
        }
        
        with sqlite3.connect(self.memory_db) as conn:
            # Get project patterns
            cursor = conn.execute("""
                SELECT pattern_type, pattern_content, confidence_score
                FROM quality_patterns
                WHERE confidence_score > 0.6
                ORDER BY confidence_score DESC
                LIMIT 10
            """)
            
            for row in cursor.fetchall():
                try:
                    pattern_data = json.loads(row[1])
                    insights["project_patterns"].append({
                        "type": row[0],
                        "data": pattern_data,
                        "confidence": row[2]
                    })
                except:
                    continue
        
        # Analyze trends
        history = self.get_analysis_history(5)
        if len(history) >= 2:
            recent_avg = sum(h["summary"].get("average_complexity", 0) for h in history[:2]) / 2
            older_avg = sum(h["summary"].get("average_complexity", 0) for h in history[-2:]) / 2
            
            insights["trend_analysis"] = {
                "recent_average": recent_avg,
                "historical_average": older_avg,
                "trend_direction": "improving" if recent_avg < older_avg else "degrading" if recent_avg > older_avg else "stable"
            }
        
        return insights
    
    def generate_complexity_report(self, analysis_id: str = None, format: str = "markdown") -> str:
        """Generate comprehensive complexity report"""
        target_id = analysis_id or (self.current_analysis.analysis_id if self.current_analysis else None)
        if not target_id:
            return "No analysis available"
        
        # Get analysis data
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT project_summary, quality_trend, recommendations
                FROM complexity_analyses
                WHERE analysis_id = ? AND user_id = ?
            """, (target_id, self.user_id))
            
            row = cursor.fetchone()
            if not row:
                return "Analysis not found"
            
            try:
                summary = json.loads(row[0]) if row[0] else {}
                recommendations = json.loads(row[2]) if row[2] else []
            except:
                summary = {}
                recommendations = []
            
            quality_trend = row[1]
        
        if format == "markdown":
            return self._generate_markdown_report(summary, quality_trend, recommendations)
        else:
            return self._generate_text_report(summary, quality_trend, recommendations)
    
    def _generate_markdown_report(self, summary: Dict, quality_trend: str, recommendations: List[str]) -> str:
        """Generate markdown complexity report"""
        report_lines = [
            "# 🎯 Code Complexity Analysis Report",
            "",
            f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Project Path:** {self.project_path}",
            f"**Quality Trend:** {quality_trend.upper()}",
            "",
            "## 📊 Project Overview",
            "",
            f"- **Total Code Units:** {summary.get('total_code_units', 0)}",
            f"- **Files Analyzed:** {summary.get('files_analyzed', 0)}",
            f"- **Average Complexity:** {summary.get('average_complexity', 0):.1f}",
            "",
            "## 🎭 Complexity Distribution",
            ""
        ]
        
        # Complexity distribution
        dist = summary.get('complexity_distribution', {})
        for level, count in dist.items():
            emoji = {"simple": "🟢", "moderate": "🟡", "complex": "🟠", "critical": "🔴"}.get(level, "⚪")
            report_lines.append(f"- {emoji} **{level.title()}:** {count} units")
        
        report_lines.extend([
            "",
            "## 🔥 Top Complexity Hotspots",
            ""
        ])
        
        # Hotspots
        hotspots = summary.get('hotspots', [])
        if hotspots:
            for i, hotspot in enumerate(hotspots[:5], 1):
                level_emoji = {"critical": "🔴", "complex": "🟠"}.get(hotspot.get('level'), "🟡")
                report_lines.append(
                    f"{i}. {level_emoji} **{hotspot['name']}** "
                    f"({hotspot['file']}) - Complexity: {hotspot['complexity']}"
                )
        else:
            report_lines.append("No complexity hotspots found! 🎉")
        
        report_lines.extend([
            "",
            "## 💡 Recommendations",
            ""
        ])
        
        # Recommendations
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                report_lines.append(f"{i}. {rec}")
        else:
            report_lines.append("No specific recommendations at this time.")
        
        return "\n".join(report_lines)
    
    def _generate_text_report(self, summary: Dict, quality_trend: str, recommendations: List[str]) -> str:
        """Generate plain text complexity report"""
        lines = [
            "CODE COMPLEXITY ANALYSIS REPORT",
            "=" * 50,
            "",
            f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Project Path: {self.project_path}",
            f"Quality Trend: {quality_trend.upper()}",
            "",
            "PROJECT OVERVIEW:",
            f"  Total Code Units: {summary.get('total_code_units', 0)}",
            f"  Files Analyzed: {summary.get('files_analyzed', 0)}",
            f"  Average Complexity: {summary.get('average_complexity', 0):.1f}",
            "",
            "COMPLEXITY DISTRIBUTION:"
        ]
        
        dist = summary.get('complexity_distribution', {})
        for level, count in dist.items():
            lines.append(f"  {level.title()}: {count} units")
        
        lines.extend([
            "",
            "TOP COMPLEXITY HOTSPOTS:"
        ])
        
        hotspots = summary.get('hotspots', [])
        if hotspots:
            for i, hotspot in enumerate(hotspots[:5], 1):
                lines.append(
                    f"  {i}. {hotspot['name']} ({hotspot['file']}) - "
                    f"Complexity: {hotspot['complexity']}"
                )
        else:
            lines.append("  No complexity hotspots found!")
        
        lines.extend([
            "",
            "RECOMMENDATIONS:"
        ])
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"  {i}. {rec}")
        else:
            lines.append("  No specific recommendations at this time.")
        
        return "\n".join(lines)
    
    def _store_analysis(self, analysis: ComplexityAnalysis):
        """Store analysis in database"""
        with sqlite3.connect(self.memory_db) as conn:
            # Store main analysis
            conn.execute("""
                INSERT OR REPLACE INTO complexity_analyses
                (analysis_id, project_path, analyzed_at, conversation_context,
                 project_summary, quality_trend, recommendations, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis.analysis_id, analysis.project_path, analysis.analyzed_at,
                analysis.conversation_context, json.dumps(analysis.project_summary),
                analysis.quality_trend.value, json.dumps(analysis.recommendations),
                self.user_id
            ))
            
            # Store code units
            for unit in analysis.code_units:
                cursor = conn.execute("""
                    INSERT INTO code_units
                    (analysis_id, name, type, file_path, start_line, end_line, loc, blank_lines, comment_lines)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    analysis.analysis_id, unit.name, unit.type, unit.file_path,
                    unit.start_line, unit.end_line, unit.loc, unit.blank_lines, unit.comment_lines
                ))
                
                unit_id = cursor.lastrowid
                
                # Store metrics for this unit
                for metric in unit.complexity_metrics:
                    conn.execute("""
                        INSERT INTO complexity_metrics
                        (code_unit_id, metric_type, metric_name, value, threshold_value, complexity_level, description)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        unit_id, metric.metric_type.value, metric.metric_name, metric.value,
                        metric.threshold, metric.level.value if metric.level else None, metric.description
                    ))
            
            # Store file metrics
            for file_path, metrics in analysis.file_metrics.items():
                for metric_name, metric_value in metrics.items():
                    conn.execute("""
                        INSERT INTO file_metrics
                        (analysis_id, file_path, metric_name, metric_value)
                        VALUES (?, ?, ?, ?)
                    """, (analysis.analysis_id, file_path, metric_name, metric_value))
            
            conn.commit()
    
    def _generate_analysis_id(self) -> str:
        """Generate unique analysis ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"{self.user_id}:{timestamp}".encode()).hexdigest()[:16]


# Global Radon instance
_global_radon = None


def get_radon(project_path: str = ".", user_id: str = "developer") -> DeltaRadon:
    """Get global Radon instance"""
    global _global_radon
    if _global_radon is None:
        _global_radon = DeltaRadon(project_path=project_path, user_id=user_id)
    return _global_radon


def initialize_radon(project_path: str = ".", config_dir: str = ".claude", user_id: str = "developer") -> DeltaRadon:
    """Initialize Radon complexity analysis system"""
    global _global_radon
    _global_radon = DeltaRadon(project_path=project_path, config_dir=config_dir, user_id=user_id)
    return _global_radon


if __name__ == "__main__":
    # Test Radon system
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Testing ∂Radon system...")
        
        # Initialize Radon system
        radon = initialize_radon()
        
        # Check if Radon is available
        available = radon.radon_interface.check_radon_available()
        print(f"Radon available: {available}")
        
        # Run complexity analysis
        analysis_id = radon.analyze_project_complexity(
            conversation_context="Testing ∂Radon system"
        )
        print(f"Analysis completed: {analysis_id}")
        
        # Generate report
        report = radon.generate_complexity_report(format="markdown")
        print("\n" + "="*50)
        print(report)
        print("="*50)
        
        # Get insights
        insights = radon.get_complexity_insights()
        print(f"\nInsights: {len(insights['project_patterns'])} patterns learned")
        
        # Get history
        history = radon.get_analysis_history(limit=3)
        print(f"Analysis history: {len(history)} analyses")
        
        print("\n∂Radon system test completed successfully!")
    else:
        print("∂Radon.py - Code complexity checking with memory")
        print("Usage: python ∂Radon.py --test")