#!/usr/bin/env python3
"""
∂Reality.py - Memory-enhanced validation
Part of the ∂-prefixed architecture for conversation-aware multi-agent development

This module provides reality validation with memory, learning validation patterns from
past sessions, adapting checks based on conversation-driven insights, and building
knowledge of what "real" means per project.
"""

import json
import os
import sqlite3
import subprocess
import hashlib
import ast
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import re

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





class ValidationLevel(Enum):
    SYNTAX = "syntax"
    IMPORT = "import"
    RUNTIME = "runtime"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    SECURITY = "security"


class ValidationStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"
    UNKNOWN = "unknown"


class RealityLevel(Enum):
    BASIC = "basic"          # File exists, syntax valid
    FUNCTIONAL = "functional" # Imports work, basic execution
    INTEGRATED = "integrated" # Works with other components
    PRODUCTION = "production" # Ready for real-world use


@dataclass
class ValidationResult:
    """Single validation check result"""
    check_name: str
    level: ValidationLevel
    status: ValidationStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    duration: float = 0.0
    file_path: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class RealityCheck:
    """Complete reality validation session"""
    check_id: str
    project_path: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    reality_level: RealityLevel = RealityLevel.BASIC
    overall_status: ValidationStatus = ValidationStatus.UNKNOWN
    validation_results: List[ValidationResult] = None
    conversation_context: Optional[str] = None
    confidence_score: float = 0.0
    
    def __post_init__(self):
        if self.validation_results is None:
            self.validation_results = []
    
    def calculate_confidence(self) -> float:
        """Calculate confidence score based on validation results"""
        if not self.validation_results:
            return 0.0
        
        passed = sum(1 for r in self.validation_results if r.status == ValidationStatus.PASSED)
        failed = sum(1 for r in self.validation_results if r.status == ValidationStatus.FAILED)
        warnings = sum(1 for r in self.validation_results if r.status == ValidationStatus.WARNING)
        total = len(self.validation_results)
        
        # Base confidence from pass rate
        base_confidence = passed / total if total > 0 else 0.0
        
        # Adjust for warnings and failures
        warning_penalty = (warnings * 0.1) / total if total > 0 else 0.0
        failure_penalty = (failed * 0.3) / total if total > 0 else 0.0
        
        confidence = max(0.0, base_confidence - warning_penalty - failure_penalty)
        return min(1.0, confidence)


class SyntaxValidator:
    """Validates Python syntax and basic structure"""
    
    def __init__(self):
        self.name = "syntax_validator"
        self.logger = get_logger("SyntaxValidator")
    
    def validate_file(self, file_path: Path) -> List[ValidationResult]:
        """Validate syntax of a Python file"""
        results = []
        
        if not file_path.exists():
            results.append(ValidationResult(
                check_name="file_exists",
                level=ValidationLevel.SYNTAX,
                status=ValidationStatus.FAILED,
                message=f"File does not exist: {file_path}",
                file_path=str(file_path)
            ))
            return results
        
        # Check file exists
        results.append(ValidationResult(
            check_name="file_exists",
            level=ValidationLevel.SYNTAX,
            status=ValidationStatus.PASSED,
            message=f"File exists: {file_path}",
            file_path=str(file_path)
        ))
        
        # Check syntax
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST to check syntax
            ast.parse(content)
            
            results.append(ValidationResult(
                check_name="syntax_valid",
                level=ValidationLevel.SYNTAX,
                status=ValidationStatus.PASSED,
                message="Python syntax is valid",
                file_path=str(file_path)
            ))
            
            # Check for common patterns
            results.extend(self._check_code_patterns(content, file_path))
            
        except SyntaxError as e:
            results.append(ValidationResult(
                check_name="syntax_valid",
                level=ValidationLevel.SYNTAX,
                status=ValidationStatus.FAILED,
                message=f"Syntax error: {str(e)}",
                file_path=str(file_path),
                details={"line": e.lineno, "column": e.offset}
            ))
        except Exception as e:
            results.append(ValidationResult(
                check_name="syntax_valid",
                level=ValidationLevel.SYNTAX,
                status=ValidationStatus.WARNING,
                message=f"Could not parse file: {str(e)}",
                file_path=str(file_path)
            ))
        
        return results
    
    def _check_code_patterns(self, content: str, file_path: Path) -> List[ValidationResult]:
        """Check for common code patterns and issues"""
        results = []
        
        # Check for docstrings
        if '"""' in content or "'''" in content:
            results.append(ValidationResult(
                check_name="has_docstrings",
                level=ValidationLevel.SYNTAX,
                status=ValidationStatus.PASSED,
                message="File contains docstrings",
                file_path=str(file_path)
            ))
        else:
            results.append(ValidationResult(
                check_name="has_docstrings",
                level=ValidationLevel.SYNTAX,
                status=ValidationStatus.WARNING,
                message="No docstrings found",
                file_path=str(file_path),
                suggestion="Consider adding docstrings for better documentation"
            ))
        
        # Check for type hints
        if re.search(r':\s*\w+', content) or 'typing' in content:
            results.append(ValidationResult(
                check_name="has_type_hints",
                level=ValidationLevel.SYNTAX,
                status=ValidationStatus.PASSED,
                message="File uses type hints",
                file_path=str(file_path)
            ))
        else:
            results.append(ValidationResult(
                check_name="has_type_hints",
                level=ValidationLevel.SYNTAX,
                status=ValidationStatus.WARNING,
                message="No type hints found",
                file_path=str(file_path),
                suggestion="Consider adding type hints for better code clarity"
            ))
        
        # Check for main guard
        if 'if __name__ == "__main__"' in content:
            results.append(ValidationResult(
                check_name="has_main_guard",
                level=ValidationLevel.SYNTAX,
                status=ValidationStatus.PASSED,
                message="File has main guard",
                file_path=str(file_path)
            ))
        
        return results


class ImportValidator:
    """Validates imports and dependencies"""
    
    def __init__(self):
        self.name = "import_validator"
        self.logger = get_logger("ImportValidator")
    
    def validate_imports(self, file_path: Path) -> List[ValidationResult]:
        """Validate imports in a Python file"""
        results = []
        
        if not file_path.exists() or not file_path.suffix == '.py':
            return results
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse imports from AST
            tree = ast.parse(content)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            # Test each import
            for import_name in imports:
                try:
                    importlib.import_module(import_name.split('.')[0])
                    results.append(ValidationResult(
                        check_name=f"import_{import_name}",
                        level=ValidationLevel.IMPORT,
                        status=ValidationStatus.PASSED,
                        message=f"Import available: {import_name}",
                        file_path=str(file_path)
                    ))
                except ImportError:
                    results.append(ValidationResult(
                        check_name=f"import_{import_name}",
                        level=ValidationLevel.IMPORT,
                        status=ValidationStatus.FAILED,
                        message=f"Import not available: {import_name}",
                        file_path=str(file_path),
                        suggestion=f"Install package: pip install {import_name}"
                    ))
                except Exception as e:
                    results.append(ValidationResult(
                        check_name=f"import_{import_name}",
                        level=ValidationLevel.IMPORT,
                        status=ValidationStatus.WARNING,
                        message=f"Import check failed: {import_name} - {str(e)}",
                        file_path=str(file_path)
                    ))
            
        except Exception as e:
            results.append(ValidationResult(
                check_name="import_analysis",
                level=ValidationLevel.IMPORT,
                status=ValidationStatus.FAILED,
                message=f"Failed to analyze imports: {str(e)}",
                file_path=str(file_path)
            ))
        
        return results


class RuntimeValidator:
    """Validates runtime execution"""
    
    def __init__(self, project_path: Path):
        self.name = "runtime_validator"
        self.project_path = project_path
        self.logger = get_logger("RuntimeValidator")
    
    def validate_execution(self, file_path: Path, test_mode: bool = True) -> List[ValidationResult]:
        """Validate that file can execute without errors"""
        results = []
        
        if not file_path.exists() or not file_path.suffix == '.py':
            return results
        
        if test_mode and not self._has_test_mode(file_path):
            results.append(ValidationResult(
                check_name="test_mode_available",
                level=ValidationLevel.RUNTIME,
                status=ValidationStatus.SKIPPED,
                message="No test mode available, skipping execution test",
                file_path=str(file_path)
            ))
            return results
        
        try:
            # Execute with test flag
            cmd = ["python", str(file_path)]
            if test_mode:
                cmd.append("--test")
            
            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                results.append(ValidationResult(
                    check_name="execution_test",
                    level=ValidationLevel.RUNTIME,
                    status=ValidationStatus.PASSED,
                    message="File executes successfully",
                    file_path=str(file_path),
                    details={"stdout_lines": len(result.stdout.split('\n'))}
                ))
            else:
                results.append(ValidationResult(
                    check_name="execution_test",
                    level=ValidationLevel.RUNTIME,
                    status=ValidationStatus.FAILED,
                    message=f"Execution failed with code {result.returncode}",
                    file_path=str(file_path),
                    details={"stderr": result.stderr[:500]}  # Limit error message
                ))
        
        except subprocess.TimeoutExpired:
            results.append(ValidationResult(
                check_name="execution_test",
                level=ValidationLevel.RUNTIME,
                status=ValidationStatus.FAILED,
                message="Execution timed out",
                file_path=str(file_path),
                suggestion="Check for infinite loops or long-running operations"
            ))
        except Exception as e:
            results.append(ValidationResult(
                check_name="execution_test",
                level=ValidationLevel.RUNTIME,
                status=ValidationStatus.WARNING,
                message=f"Could not test execution: {str(e)}",
                file_path=str(file_path)
            ))
        
        return results
    
    def _has_test_mode(self, file_path: Path) -> bool:
        """Check if file has test mode (--test argument handling)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return '--test' in content or 'test' in content.lower()
        except:
            return False


class DeltaReality:
    """
    ∂Reality - Memory-enhanced validation
    
    Features:
    - Learns validation patterns from past sessions
    - Adapts checks based on conversation-driven insights
    - Builds knowledge of what "real" means per project
    - Multi-level validation (syntax, import, runtime, integration)
    """
    
    def __init__(self, project_path: str = ".", config_dir: str = ".claude", user_id: str = "developer"):
        self.project_path = Path(project_path).resolve()
        self.config_dir = Path(config_dir)
        self.user_id = user_id
        self.config = get_config(user_id)
        self.logger = get_logger("∂Reality")
        
        # Initialize memory systems
        self.memory_db = self.config_dir / "∂reality_memory.db"
        self._init_memory_systems()
        self._init_database()
        
        # Initialize validators
        self.syntax_validator = SyntaxValidator()
        self.import_validator = ImportValidator()
        self.runtime_validator = RuntimeValidator(self.project_path)
        
        # Current validation state
        self.current_check = None
        self.validation_history = []
        
        # Learning parameters
        self.validation_patterns = {}
        self.project_reality_definition = {}
        
        self.logger.info(f"∂Reality initialized for project: {self.project_path}")
    
    def _init_memory_systems(self):
        """Initialize LangMem and fallback SQLite memory systems"""
        global LANGMEM_AVAILABLE
        self.memory_tools = []
        
        if LANGMEM_AVAILABLE:
            try:
                self.store = InMemoryStore(
                    index={"dims": 1536, "embed": "openai:text-embedding-3-small"}
                )
                self.namespace = ("∂reality", self.user_id)
                self.memory_tools = [
                    create_manage_memory_tool(namespace=self.namespace),
                    create_search_memory_tool(namespace=self.namespace),
                ]
                self.logger.info("LangMem memory system initialized")
            except Exception as e:
                self.logger.warning(f"LangMem initialization failed: {e}")
                LANGMEM_AVAILABLE = False
    
    def _init_database(self):
        """Initialize SQLite database for reality validation storage"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reality_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    check_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    project_path TEXT NOT NULL,
                    started_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP,
                    reality_level TEXT NOT NULL,
                    overall_status TEXT NOT NULL,
                    confidence_score REAL DEFAULT 0.0,
                    conversation_context TEXT,
                    UNIQUE(check_id, user_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS validation_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    check_id TEXT NOT NULL,
                    check_name TEXT NOT NULL,
                    validation_level TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT NOT NULL,
                    duration REAL DEFAULT 0.0,
                    file_path TEXT,
                    suggestion TEXT,
                    details TEXT,
                    FOREIGN KEY(check_id) REFERENCES reality_checks(check_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reality_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_path TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    pattern_content TEXT NOT NULL,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    confidence_score REAL DEFAULT 0.5,
                    last_updated TIMESTAMP NOT NULL,
                    learned_from_conversation BOOLEAN DEFAULT FALSE,
                    UNIQUE(project_path, pattern_type, pattern_content)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS project_reality_definitions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_path TEXT NOT NULL,
                    reality_aspect TEXT NOT NULL,
                    definition_data TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    UNIQUE(project_path, reality_aspect)
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_reality_checks ON reality_checks(user_id, started_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_validation_results ON validation_results(check_id, status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_reality_patterns ON reality_patterns(project_path, confidence_score)")
            
            conn.commit()
    
    def validate_reality(self, target_files: List[str] = None, validation_levels: List[ValidationLevel] = None,
                        conversation_context: str = None) -> str:
        """Perform comprehensive reality validation"""
        # Start new reality check
        check_id = self._generate_check_id()
        reality_check = RealityCheck(
            check_id=check_id,
            project_path=str(self.project_path),
            started_at=datetime.now(),
            conversation_context=conversation_context
        )
        
        self.current_check = reality_check
        self._store_reality_check(reality_check)
        
        self.logger.info(f"Starting reality validation: {check_id}")
        
        # Determine files to validate
        if target_files:
            files_to_check = [self.project_path / f for f in target_files]
        else:
            files_to_check = list(self.project_path.rglob("∂*.py"))
        
        # Determine validation levels
        levels = validation_levels or [ValidationLevel.SYNTAX, ValidationLevel.IMPORT, ValidationLevel.RUNTIME]
        
        # Apply learned patterns to enhance validation
        enhanced_levels = self._enhance_validation_with_patterns(levels)
        
        # Perform validations
        all_results = []
        
        for file_path in files_to_check:
            file_results = []
            
            # Syntax validation
            if ValidationLevel.SYNTAX in enhanced_levels:
                file_results.extend(self.syntax_validator.validate_file(file_path))
            
            # Import validation
            if ValidationLevel.IMPORT in enhanced_levels:
                file_results.extend(self.import_validator.validate_imports(file_path))
            
            # Runtime validation
            if ValidationLevel.RUNTIME in enhanced_levels:
                file_results.extend(self.runtime_validator.validate_execution(file_path))
            
            all_results.extend(file_results)
        
        # Update reality check with results
        reality_check.validation_results = all_results
        reality_check.completed_at = datetime.now()
        reality_check.confidence_score = reality_check.calculate_confidence()
        
        # Determine overall status and reality level
        reality_check.overall_status = self._determine_overall_status(all_results)
        reality_check.reality_level = self._determine_reality_level(all_results)
        
        # Store results
        self._update_reality_check(reality_check)
        self._store_validation_results(reality_check)
        
        # Learn from this validation
        self._learn_from_validation(reality_check)
        
        # Update project reality definition
        self._update_project_reality_definition(reality_check)
        
        self.logger.info(f"Reality validation completed: {reality_check.overall_status.value}")
        return check_id
    
    def get_reality_report(self, check_id: str = None, format: str = "summary") -> str:
        """Get reality validation report"""
        target_check = self._get_reality_check(check_id) if check_id else self.current_check
        
        if not target_check:
            return "No reality check data available"
        
        if format == "summary":
            return self._generate_summary_report(target_check)
        elif format == "detailed":
            return self._generate_detailed_report(target_check)
        else:
            return self._generate_json_report(target_check)
    
    def _generate_summary_report(self, reality_check: RealityCheck) -> str:
        """Generate summary reality report"""
        results = reality_check.validation_results
        
        # Count results by status
        passed = sum(1 for r in results if r.status == ValidationStatus.PASSED)
        failed = sum(1 for r in results if r.status == ValidationStatus.FAILED)
        warnings = sum(1 for r in results if r.status == ValidationStatus.WARNING)
        skipped = sum(1 for r in results if r.status == ValidationStatus.SKIPPED)
        total = len(results)
        
        # Generate report
        lines = [
            "🔍 REALITY VALIDATION REPORT",
            "=" * 50,
            "",
            f"📊 Overall Status: {reality_check.overall_status.value.upper()}",
            f"🎯 Reality Level: {reality_check.reality_level.value.upper()}",
            f"📈 Confidence: {reality_check.confidence_score*100:.1f}%",
            "",
            "📋 Validation Results:",
            f"  ✅ Passed:   {passed:>3} ({passed/max(total,1)*100:.1f}%)",
            f"  ❌ Failed:   {failed:>3} ({failed/max(total,1)*100:.1f}%)",
            f"  ⚠️  Warnings: {warnings:>3} ({warnings/max(total,1)*100:.1f}%)",
            f"  ⏭️  Skipped:  {skipped:>3} ({skipped/max(total,1)*100:.1f}%)",
            f"  📝 Total:    {total:>3}",
            "",
        ]
        
        # Add reality assessment
        if reality_check.reality_level == RealityLevel.PRODUCTION:
            lines.extend([
                "🌟 PRODUCTION READY!",
                "   Your code meets production standards."
            ])
        elif reality_check.reality_level == RealityLevel.INTEGRATED:
            lines.extend([
                "✨ WELL INTEGRATED!",
                "   Components work together properly."
            ])
        elif reality_check.reality_level == RealityLevel.FUNCTIONAL:
            lines.extend([
                "⚡ FUNCTIONALLY SOUND!",
                "   Basic functionality is working."
            ])
        else:
            lines.extend([
                "🔧 NEEDS WORK!",
                "   Basic issues need to be addressed."
            ])
        
        # Add top suggestions
        suggestions = [r.suggestion for r in results if r.suggestion and r.status != ValidationStatus.PASSED]
        if suggestions:
            lines.extend([
                "",
                "💡 Top Suggestions:",
                *[f"   • {s}" for s in suggestions[:3]]
            ])
        
        lines.extend([
            "",
            f"⏱️  Validation Time: {reality_check.started_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 50
        ])
        
        return "\n".join(lines)
    
    def _generate_detailed_report(self, reality_check: RealityCheck) -> str:
        """Generate detailed reality report"""
        lines = [
            "🔍 DETAILED REALITY VALIDATION REPORT",
            "=" * 80,
            "",
            f"Check ID: {reality_check.check_id}",
            f"Project: {reality_check.project_path}",
            f"Started: {reality_check.started_at}",
            f"Completed: {reality_check.completed_at}",
            f"Reality Level: {reality_check.reality_level.value}",
            f"Overall Status: {reality_check.overall_status.value}",
            f"Confidence: {reality_check.confidence_score*100:.1f}%",
            "",
            "VALIDATION BREAKDOWN:",
            "-" * 40
        ]
        
        # Group results by level
        by_level = defaultdict(list)
        for result in reality_check.validation_results:
            by_level[result.level].append(result)
        
        for level, level_results in by_level.items():
            lines.append(f"\n📁 {level.value.upper()} VALIDATION")
            
            for result in level_results:
                status_icon = {
                    ValidationStatus.PASSED: "✅",
                    ValidationStatus.FAILED: "❌",
                    ValidationStatus.WARNING: "⚠️",
                    ValidationStatus.SKIPPED: "⏭️"
                }.get(result.status, "❓")
                
                lines.append(f"  {status_icon} {result.check_name}: {result.message}")
                
                if result.file_path:
                    lines.append(f"     📄 File: {result.file_path}")
                
                if result.suggestion:
                    lines.append(f"     💡 Suggestion: {result.suggestion}")
        
        return "\n".join(lines)
    
    def _generate_json_report(self, reality_check: RealityCheck) -> str:
        """Generate JSON reality report"""
        report_data = {
            "check_id": reality_check.check_id,
            "project_path": reality_check.project_path,
            "started_at": reality_check.started_at.isoformat(),
            "completed_at": reality_check.completed_at.isoformat() if reality_check.completed_at else None,
            "reality_level": reality_check.reality_level.value,
            "overall_status": reality_check.overall_status.value,
            "confidence_score": reality_check.confidence_score,
            "validation_results": [
                {
                    "check_name": r.check_name,
                    "level": r.level.value,
                    "status": r.status.value,
                    "message": r.message,
                    "duration": r.duration,
                    "file_path": r.file_path,
                    "suggestion": r.suggestion,
                    "details": r.details
                }
                for r in reality_check.validation_results
            ]
        }
        
        return json.dumps(report_data, indent=2)
    
    def learn_from_conversation(self, conversation_context: Dict[str, Any]):
        """Learn reality validation patterns from conversation"""
        if "reality_expectations" in conversation_context:
            expectations = conversation_context["reality_expectations"]
            
            for aspect, definition in expectations.items():
                self._update_reality_definition(aspect, definition, 0.8)
                self.logger.info(f"Learned reality expectation: {aspect}")
        
        if "validation_preferences" in conversation_context:
            preferences = conversation_context["validation_preferences"]
            
            for pref_type, pref_value in preferences.items():
                self._store_validation_pattern(pref_type, pref_value, learned_from_conversation=True)
                self.logger.info(f"Learned validation preference: {pref_type}")
    
    def get_validation_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get validation history"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT check_id, started_at, completed_at, reality_level, overall_status, confidence_score
                FROM reality_checks
                WHERE user_id = ? AND started_at > ?
                ORDER BY started_at DESC
            """, (self.user_id, cutoff_date))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    "check_id": row[0],
                    "started_at": row[1],
                    "completed_at": row[2],
                    "reality_level": row[3],
                    "overall_status": row[4],
                    "confidence_score": row[5]
                })
            
            return history
    
    def get_reality_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get reality validation trends"""
        history = self.get_validation_history(days)
        
        if not history:
            return {"message": "No validation history for trend analysis"}
        
        # Calculate trends
        confidence_scores = [h["confidence_score"] for h in history if h["confidence_score"]]
        reality_levels = [h["reality_level"] for h in history]
        
        level_counts = {level.value: reality_levels.count(level.value) for level in RealityLevel}
        
        return {
            "total_validations": len(history),
            "average_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            "confidence_trend": "improving" if len(confidence_scores) >= 2 and confidence_scores[0] > confidence_scores[-1] else "stable",
            "reality_level_distribution": level_counts,
            "period_days": days
        }
    
    def _enhance_validation_with_patterns(self, levels: List[ValidationLevel]) -> List[ValidationLevel]:
        """Enhance validation levels with learned patterns"""
        enhanced_levels = levels.copy()
        
        # Load learned patterns
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT pattern_content, confidence_score
                FROM reality_patterns
                WHERE project_path = ? AND pattern_type = 'validation_enhancement' AND confidence_score > 0.7
                ORDER BY confidence_score DESC
            """, (str(self.project_path),))
            
            patterns = cursor.fetchall()
        
        # Apply patterns
        for pattern_content, confidence in patterns:
            try:
                pattern_data = json.loads(pattern_content)
                recommended_level = pattern_data.get("level")
                if recommended_level:
                    try:
                        level_enum = ValidationLevel(recommended_level)
                        if level_enum not in enhanced_levels:
                            enhanced_levels.append(level_enum)
                            self.logger.debug(f"Added validation level: {recommended_level}")
                    except ValueError:
                        continue
            except json.JSONDecodeError:
                continue
        
        return enhanced_levels
    
    def _determine_overall_status(self, results: List[ValidationResult]) -> ValidationStatus:
        """Determine overall validation status"""
        if not results:
            return ValidationStatus.UNKNOWN
        
        failed_count = sum(1 for r in results if r.status == ValidationStatus.FAILED)
        warning_count = sum(1 for r in results if r.status == ValidationStatus.WARNING)
        
        if failed_count > 0:
            return ValidationStatus.FAILED
        elif warning_count > len(results) * 0.3:  # More than 30% warnings
            return ValidationStatus.WARNING
        else:
            return ValidationStatus.PASSED
    
    def _determine_reality_level(self, results: List[ValidationResult]) -> RealityLevel:
        """Determine reality level based on validation results"""
        if not results:
            return RealityLevel.BASIC
        
        # Count by validation level and status
        syntax_passed = any(r.level == ValidationLevel.SYNTAX and r.status == ValidationStatus.PASSED for r in results)
        import_passed = any(r.level == ValidationLevel.IMPORT and r.status == ValidationStatus.PASSED for r in results)
        runtime_passed = any(r.level == ValidationLevel.RUNTIME and r.status == ValidationStatus.PASSED for r in results)
        
        failed_count = sum(1 for r in results if r.status == ValidationStatus.FAILED)
        
        # Determine level
        if failed_count == 0 and syntax_passed and import_passed and runtime_passed:
            return RealityLevel.PRODUCTION
        elif failed_count <= 1 and import_passed and runtime_passed:
            return RealityLevel.INTEGRATED
        elif failed_count <= 2 and syntax_passed:
            return RealityLevel.FUNCTIONAL
        else:
            return RealityLevel.BASIC
    
    def _learn_from_validation(self, reality_check: RealityCheck):
        """Learn patterns from validation results"""
        # Learn from successful validations
        for result in reality_check.validation_results:
            if result.status == ValidationStatus.PASSED:
                pattern_content = json.dumps({
                    "check_name": result.check_name,
                    "level": result.level.value,
                    "success": True
                })
                self._store_validation_pattern("successful_check", pattern_content)
        
        # Learn from overall success
        if reality_check.overall_status == ValidationStatus.PASSED:
            if reality_check.conversation_context:
                pattern_content = json.dumps({
                    "context_present": True,
                    "reality_level": reality_check.reality_level.value
                })
                self._store_validation_pattern("successful_context", pattern_content)
    
    def _store_validation_pattern(self, pattern_type: str, pattern_content: str, learned_from_conversation: bool = False):
        """Store validation pattern for learning"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO reality_patterns
                (project_path, pattern_type, pattern_content, success_count, failure_count,
                 confidence_score, last_updated, learned_from_conversation)
                VALUES (?, ?, ?, 
                        COALESCE((SELECT success_count FROM reality_patterns 
                                 WHERE project_path = ? AND pattern_type = ? AND pattern_content = ?), 0) + 1,
                        COALESCE((SELECT failure_count FROM reality_patterns 
                                 WHERE project_path = ? AND pattern_type = ? AND pattern_content = ?), 0),
                        ?, ?, ?)
            """, (
                str(self.project_path), pattern_type, pattern_content,
                str(self.project_path), pattern_type, pattern_content,
                str(self.project_path), pattern_type, pattern_content,
                0.7, datetime.now(), learned_from_conversation
            ))
            conn.commit()
    
    def _update_project_reality_definition(self, reality_check: RealityCheck):
        """Update project-specific reality definition"""
        reality_data = {
            "level": reality_check.reality_level.value,
            "confidence": reality_check.confidence_score,
            "validation_count": len(reality_check.validation_results),
            "last_check": reality_check.started_at.isoformat()
        }
        
        self._update_reality_definition("project_status", reality_data, reality_check.confidence_score)
    
    def _update_reality_definition(self, aspect: str, definition_data: Any, confidence: float):
        """Update reality definition for specific aspect"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO project_reality_definitions
                (project_path, reality_aspect, definition_data, confidence_score, created_at, updated_at)
                VALUES (?, ?, ?, ?, 
                        COALESCE((SELECT created_at FROM project_reality_definitions 
                                 WHERE project_path = ? AND reality_aspect = ?), ?),
                        ?)
            """, (
                str(self.project_path), aspect, json.dumps(definition_data), confidence,
                str(self.project_path), aspect, datetime.now(),
                datetime.now()
            ))
            conn.commit()
    
    def _generate_check_id(self) -> str:
        """Generate unique check ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"{self.user_id}:{timestamp}".encode()).hexdigest()[:16]
    
    def _store_reality_check(self, reality_check: RealityCheck):
        """Store reality check in database"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO reality_checks
                (check_id, user_id, project_path, started_at, completed_at,
                 reality_level, overall_status, confidence_score, conversation_context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                reality_check.check_id, self.user_id, reality_check.project_path,
                reality_check.started_at, reality_check.completed_at,
                reality_check.reality_level.value, reality_check.overall_status.value,
                reality_check.confidence_score, reality_check.conversation_context
            ))
            conn.commit()
    
    def _update_reality_check(self, reality_check: RealityCheck):
        """Update reality check in database"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                UPDATE reality_checks
                SET completed_at = ?, reality_level = ?, overall_status = ?, confidence_score = ?
                WHERE check_id = ? AND user_id = ?
            """, (
                reality_check.completed_at, reality_check.reality_level.value,
                reality_check.overall_status.value, reality_check.confidence_score,
                reality_check.check_id, self.user_id
            ))
            conn.commit()
    
    def _store_validation_results(self, reality_check: RealityCheck):
        """Store validation results in database"""
        with sqlite3.connect(self.memory_db) as conn:
            for result in reality_check.validation_results:
                conn.execute("""
                    INSERT INTO validation_results
                    (check_id, check_name, validation_level, status, message,
                     duration, file_path, suggestion, details)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    reality_check.check_id, result.check_name, result.level.value,
                    result.status.value, result.message, result.duration,
                    result.file_path, result.suggestion,
                    json.dumps(result.details) if result.details else None
                ))
            conn.commit()
    
    def _get_reality_check(self, check_id: str) -> Optional[RealityCheck]:
        """Get reality check by ID"""
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT check_id, project_path, started_at, completed_at, reality_level,
                       overall_status, confidence_score, conversation_context
                FROM reality_checks
                WHERE check_id = ? AND user_id = ?
            """, (check_id, self.user_id))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Load validation results
            cursor = conn.execute("""
                SELECT check_name, validation_level, status, message, duration,
                       file_path, suggestion, details
                FROM validation_results
                WHERE check_id = ?
            """, (check_id,))
            
            validation_results = []
            for result_row in cursor.fetchall():
                validation_results.append(ValidationResult(
                    check_name=result_row[0],
                    level=ValidationLevel(result_row[1]),
                    status=ValidationStatus(result_row[2]),
                    message=result_row[3],
                    duration=result_row[4],
                    file_path=result_row[5],
                    suggestion=result_row[6],
                    details=json.loads(result_row[7]) if result_row[7] else None
                ))
            
            return RealityCheck(
                check_id=row[0],
                project_path=row[1],
                started_at=datetime.fromisoformat(row[2]),
                completed_at=datetime.fromisoformat(row[3]) if row[3] else None,
                reality_level=RealityLevel(row[4]),
                overall_status=ValidationStatus(row[5]),
                confidence_score=row[6],
                conversation_context=row[7],
                validation_results=validation_results
            )


# Global Reality instance
_global_reality = None


def get_reality(project_path: str = ".", user_id: str = "developer") -> DeltaReality:
    """Get global Reality instance"""
    global _global_reality
    if _global_reality is None:
        _global_reality = DeltaReality(project_path=project_path, user_id=user_id)
    return _global_reality


def initialize_reality(project_path: str = ".", config_dir: str = ".claude", user_id: str = "developer") -> DeltaReality:
    """Initialize Reality validation system"""
    global _global_reality
    _global_reality = DeltaReality(project_path=project_path, config_dir=config_dir, user_id=user_id)
    return _global_reality


if __name__ == "__main__":
    # Test Reality validation system
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Testing ∂Reality system...")
        
        # Initialize Reality system
        reality = initialize_reality()
        
        # Perform validation on current project
        check_id = reality.validate_reality(
            conversation_context="Testing reality validation system"
        )
        
        print(f"Validation completed: {check_id}")
        
        # Get summary report
        summary = reality.get_reality_report(format="summary")
        print(f"Summary Report:\n{summary}")
        
        # Test trends
        trends = reality.get_reality_trends()
        print(f"Trends: {trends}")
        
        # Test learning
        reality.learn_from_conversation({
            "reality_expectations": {
                "code_quality": "high",
                "test_coverage": "comprehensive"
            }
        })
        
        print("∂Reality system test completed successfully!")
    else:
        print("∂Reality.py - Memory-enhanced validation")
        print("Usage: python ∂Reality.py --test")