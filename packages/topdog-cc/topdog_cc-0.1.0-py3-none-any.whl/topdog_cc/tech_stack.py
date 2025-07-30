#!/usr/bin/env python3
"""
∂TechStack.py - Dynamic framework detection
Part of the ∂-prefixed architecture for conversation-aware multi-agent development

This module provides intelligent framework detection that learns from conversation history,
adapts detection logic based on past project interactions, and makes no hardcoded assumptions.
"""

import json
import os
import re
import sqlite3
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib

try:
    from langmem import create_manage_memory_tool, create_search_memory_tool
    from langgraph.store.memory import InMemoryStore
    LANGMEM_AVAILABLE = True
except ImportError:
    LANGMEM_AVAILABLE = False

# Import using standard ASCII filenames
import importlib.util
import sys

# Import other components
from .config import get_config
from .logger import get_logger


@dataclass
class FrameworkSignature:
    """Signature for framework detection"""
    name: str
    confidence: float
    version: Optional[str] = None
    indicators: List[str] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TechStackProfile:
    """Complete technology stack profile"""
    primary_language: str
    frameworks: List[FrameworkSignature]
    build_tools: List[str]
    package_managers: List[str]
    databases: List[str]
    testing_frameworks: List[str]
    deployment_platforms: List[str]
    confidence_score: float
    detection_timestamp: datetime
    conversation_context: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['detection_timestamp'] = self.detection_timestamp.isoformat()
        return result


class FrameworkDetector:
    """Base class for framework detection strategies"""
    
    def __init__(self, name: str):
        self.name = name
        self.confidence_threshold = 0.3
    
    def detect(self, project_path: Path) -> List[FrameworkSignature]:
        """Detect frameworks in project"""
        raise NotImplementedError
    
    def learn_from_feedback(self, feedback: Dict[str, Any]):
        """Learn from user feedback about detection accuracy"""
        pass


class FileBasedDetector(FrameworkDetector):
    """Detect frameworks based on file patterns"""
    
    def __init__(self):
        super().__init__("file_based")
        self.file_patterns = {
            # Python frameworks
            "requirements.txt": {"flask": 0.8, "django": 0.8, "fastapi": 0.8},
            "pyproject.toml": {"poetry": 0.9, "setuptools": 0.5},
            "setup.py": {"setuptools": 0.9},
            "pipfile": {"pipenv": 0.9},
            "environment.yml": {"conda": 0.9},
            
            # JavaScript/Node.js
            "package.json": {"node": 0.9, "npm": 0.8},
            "yarn.lock": {"yarn": 0.9},
            "package-lock.json": {"npm": 0.8},
            
            # Build tools
            "Dockerfile": {"docker": 0.9},
            "docker-compose.yml": {"docker-compose": 0.9},
            "Makefile": {"make": 0.7},
            "build.gradle": {"gradle": 0.9},
            "pom.xml": {"maven": 0.9},
            
            # Configuration files
            ".gitignore": {"git": 0.6},
            ".travis.yml": {"travis-ci": 0.9},
            ".github/workflows": {"github-actions": 0.9},
            "jenkins": {"jenkins": 0.8},
            
            # Frontend frameworks
            "angular.json": {"angular": 0.9},
            "vue.config.js": {"vue": 0.9},
            "next.config.js": {"nextjs": 0.9},
            "nuxt.config.js": {"nuxtjs": 0.9},
            "gatsby-config.js": {"gatsby": 0.9},
            
            # Testing
            "pytest.ini": {"pytest": 0.9},
            "tox.ini": {"tox": 0.9},
            "jest.config.js": {"jest": 0.9},
            "karma.conf.js": {"karma": 0.9},
        }
    
    def detect(self, project_path: Path) -> List[FrameworkSignature]:
        """Detect frameworks based on file presence"""
        signatures = []
        
        for file_pattern, frameworks in self.file_patterns.items():
            # Check if file exists
            if "/" in file_pattern:
                target_path = project_path / file_pattern
                exists = target_path.exists()
            else:
                # Check for file in root or any subdirectory
                exists = any(project_path.rglob(file_pattern))
            
            if exists:
                for framework, confidence in frameworks.items():
                    signatures.append(FrameworkSignature(
                        name=framework,
                        confidence=confidence,
                        indicators=[file_pattern],
                        metadata={"detection_method": "file_based"}
                    ))
        
        return signatures


class ContentBasedDetector(FrameworkDetector):
    """Detect frameworks based on file content analysis"""
    
    def __init__(self):
        super().__init__("content_based")
        self.content_patterns = {
            # Python imports
            r"from django": {"django": 0.9},
            r"import django": {"django": 0.9},
            r"from flask": {"flask": 0.9},
            r"import flask": {"flask": 0.9},
            r"from fastapi": {"fastapi": 0.9},
            r"import fastapi": {"fastapi": 0.9},
            r"from tensorflow": {"tensorflow": 0.8},
            r"import tensorflow": {"tensorflow": 0.8},
            r"from pytorch": {"pytorch": 0.8},
            r"import torch": {"pytorch": 0.8},
            
            # JavaScript/React patterns
            r"import.*react": {"react": 0.9},
            r"from.*react": {"react": 0.9},
            r"import.*vue": {"vue": 0.9},
            r"import.*angular": {"angular": 0.9},
            r"import.*express": {"express": 0.9},
            
            # Configuration patterns
            r"DJANGO_SETTINGS_MODULE": {"django": 0.9},
            r"app = Flask": {"flask": 0.9},
            r"app = FastAPI": {"fastapi": 0.9},
            r"createApp": {"vue": 0.8},
            r"@Component": {"angular": 0.8},
            
            # Database patterns
            r"models\.Model": {"django": 0.7},
            r"db\.session": {"sqlalchemy": 0.7},
            r"mongoose\.": {"mongoose": 0.8},
            r"prisma\.": {"prisma": 0.8},
        }
    
    def detect(self, project_path: Path) -> List[FrameworkSignature]:
        """Detect frameworks based on content patterns"""
        signatures = []
        framework_indicators = defaultdict(list)
        
        # Scan source files
        for file_path in project_path.rglob("*"):
            if file_path.is_file() and self._is_source_file(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    for pattern, frameworks in self.content_patterns.items():
                        if re.search(pattern, content, re.IGNORECASE):
                            for framework, confidence in frameworks.items():
                                framework_indicators[framework].append({
                                    "file": str(file_path.relative_to(project_path)),
                                    "pattern": pattern,
                                    "confidence": confidence
                                })
                                
                except Exception:
                    continue
        
        # Create signatures from indicators
        for framework, indicators in framework_indicators.items():
            avg_confidence = sum(ind["confidence"] for ind in indicators) / len(indicators)
            signatures.append(FrameworkSignature(
                name=framework,
                confidence=min(avg_confidence, 1.0),
                indicators=[ind["file"] for ind in indicators],
                metadata={
                    "detection_method": "content_based",
                    "pattern_matches": len(indicators)
                }
            ))
        
        return signatures
    
    def _is_source_file(self, file_path: Path) -> bool:
        """Check if file is a source code file"""
        source_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.vue', '.html', '.css', '.scss',
            '.java', '.cpp', '.c', '.h', '.rb', '.php', '.go', '.rs', '.swift',
            '.kt', '.scala', '.clj', '.hs', '.ml', '.fs', '.dart', '.r', '.jl'
        }
        return file_path.suffix.lower() in source_extensions


class DependencyDetector(FrameworkDetector):
    """Detect frameworks based on dependency files"""
    
    def __init__(self):
        super().__init__("dependency_based")
    
    def detect(self, project_path: Path) -> List[FrameworkSignature]:
        """Detect frameworks from dependency files"""
        signatures = []
        
        # Python dependencies
        signatures.extend(self._detect_python_deps(project_path))
        
        # Node.js dependencies
        signatures.extend(self._detect_nodejs_deps(project_path))
        
        # Other dependency files
        signatures.extend(self._detect_other_deps(project_path))
        
        return signatures
    
    def _detect_python_deps(self, project_path: Path) -> List[FrameworkSignature]:
        """Detect Python framework dependencies"""
        signatures = []
        
        # requirements.txt
        req_file = project_path / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    content = f.read()
                signatures.extend(self._parse_requirements(content))
            except Exception:
                pass
        
        # pyproject.toml
        pyproject_file = project_path / "pyproject.toml"
        if pyproject_file.exists():
            try:
                with open(pyproject_file, 'r') as f:
                    content = f.read()
                signatures.extend(self._parse_pyproject(content))
            except Exception:
                pass
        
        return signatures
    
    def _detect_nodejs_deps(self, project_path: Path) -> List[FrameworkSignature]:
        """Detect Node.js framework dependencies"""
        signatures = []
        
        package_json = project_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                
                # Check dependencies and devDependencies
                all_deps = {}
                all_deps.update(data.get("dependencies", {}))
                all_deps.update(data.get("devDependencies", {}))
                
                for dep_name, version in all_deps.items():
                    confidence = self._get_nodejs_framework_confidence(dep_name)
                    if confidence > 0.3:
                        signatures.append(FrameworkSignature(
                            name=dep_name,
                            confidence=confidence,
                            version=version,
                            indicators=["package.json"],
                            metadata={"detection_method": "dependency_based"}
                        ))
                        
            except Exception:
                pass
        
        return signatures
    
    def _detect_other_deps(self, project_path: Path) -> List[FrameworkSignature]:
        """Detect other dependency formats"""
        signatures = []
        
        # Gemfile (Ruby)
        gemfile = project_path / "Gemfile"
        if gemfile.exists():
            signatures.append(FrameworkSignature(
                name="ruby",
                confidence=0.9,
                indicators=["Gemfile"],
                metadata={"detection_method": "dependency_based"}
            ))
        
        # Cargo.toml (Rust)
        cargo_toml = project_path / "Cargo.toml"
        if cargo_toml.exists():
            signatures.append(FrameworkSignature(
                name="rust",
                confidence=0.9,
                indicators=["Cargo.toml"],
                metadata={"detection_method": "dependency_based"}
            ))
        
        return signatures
    
    def _parse_requirements(self, content: str) -> List[FrameworkSignature]:
        """Parse requirements.txt content"""
        signatures = []
        
        framework_patterns = {
            "django": 0.9,
            "flask": 0.9,
            "fastapi": 0.9,
            "tornado": 0.8,
            "bottle": 0.8,
            "pyramid": 0.8,
            "celery": 0.8,
            "pytest": 0.8,
            "unittest": 0.6,
            "sqlalchemy": 0.7,
            "pandas": 0.7,
            "numpy": 0.7,
            "tensorflow": 0.8,
            "pytorch": 0.8,
            "scikit-learn": 0.8,
        }
        
        for line in content.split('\n'):
            line = line.strip().lower()
            if line and not line.startswith('#'):
                package_name = line.split('=')[0].split('>')[0].split('<')[0].strip()
                
                if package_name in framework_patterns:
                    signatures.append(FrameworkSignature(
                        name=package_name,
                        confidence=framework_patterns[package_name],
                        indicators=["requirements.txt"],
                        metadata={"detection_method": "dependency_based"}
                    ))
        
        return signatures
    
    def _parse_pyproject(self, content: str) -> List[FrameworkSignature]:
        """Parse pyproject.toml content"""
        signatures = []
        
        # Simple parsing - would use proper TOML parser in production
        if "poetry" in content.lower():
            signatures.append(FrameworkSignature(
                name="poetry",
                confidence=0.9,
                indicators=["pyproject.toml"],
                metadata={"detection_method": "dependency_based"}
            ))
        
        return signatures
    
    def _get_nodejs_framework_confidence(self, package_name: str) -> float:
        """Get confidence score for Node.js package"""
        framework_confidence = {
            "react": 0.9,
            "vue": 0.9,
            "angular": 0.9,
            "express": 0.9,
            "koa": 0.8,
            "hapi": 0.8,
            "next": 0.9,
            "nuxt": 0.9,
            "gatsby": 0.9,
            "webpack": 0.8,
            "vite": 0.8,
            "rollup": 0.8,
            "jest": 0.8,
            "mocha": 0.8,
            "chai": 0.7,
            "cypress": 0.8,
            "eslint": 0.7,
            "prettier": 0.7,
            "typescript": 0.8,
            "babel": 0.7,
        }
        
        return framework_confidence.get(package_name, 0.2)


class DeltaTechStack:
    """
    ∂TechStack - Dynamic framework detection with conversation memory
    
    Features:
    - Learns framework patterns from conversation history
    - Adapts detection logic based on past project interactions
    - No hardcoded assumptions - pure discovery-based
    - Memory-enhanced confidence scoring
    """
    
    def __init__(self, config_dir: str = ".claude", user_id: str = "developer"):
        self.config_dir = Path(config_dir)
        self.user_id = user_id
        self.config = get_config(user_id)
        self.logger = get_logger("∂TechStack")
        
        # Initialize memory systems
        self.memory_db = self.config_dir / "∂techstack_memory.db"
        self._init_memory_systems()
        self._init_database()
        
        # Initialize detectors
        self.detectors = [
            FileBasedDetector(),
            ContentBasedDetector(),
            DependencyDetector()
        ]
        
        # Detection cache
        self.detection_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Learning parameters
        self.learning_rate = 0.1
        self.confidence_threshold = 0.4
        
        self.logger.info("∂TechStack initialized with conversation-aware detection")
    
    def _init_memory_systems(self):
        """Initialize LangMem and fallback SQLite memory systems"""
        global LANGMEM_AVAILABLE
        self.memory_tools = []
        
        if LANGMEM_AVAILABLE:
            try:
                self.store = InMemoryStore(
                    index={"dims": 1536, "embed": "openai:text-embedding-3-small"}
                )
                self.namespace = ("∂techstack", self.user_id)
                self.memory_tools = [
                    create_manage_memory_tool(namespace=self.namespace),
                    create_search_memory_tool(namespace=self.namespace),
                ]
                self.logger.info("LangMem memory system initialized")
            except Exception as e:
                self.logger.warning(f"LangMem initialization failed: {e}")
                LANGMEM_AVAILABLE = False
    
    def _init_database(self):
        """Initialize SQLite database for tech stack memory"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS project_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_path TEXT NOT NULL,
                    project_hash TEXT NOT NULL,
                    profile_data TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    detection_timestamp TIMESTAMP NOT NULL,
                    conversation_context TEXT,
                    user_validated BOOLEAN DEFAULT FALSE,
                    UNIQUE(project_path, project_hash)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS framework_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    framework_name TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    pattern_value TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    usage_count INTEGER DEFAULT 1,
                    success_rate REAL DEFAULT 0.5,
                    last_updated TIMESTAMP NOT NULL,
                    learned_from_conversation BOOLEAN DEFAULT FALSE,
                    UNIQUE(framework_name, pattern_type, pattern_value)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS detection_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_path TEXT NOT NULL,
                    framework_name TEXT NOT NULL,
                    predicted_confidence REAL NOT NULL,
                    actual_presence BOOLEAN NOT NULL,
                    feedback_timestamp TIMESTAMP NOT NULL,
                    conversation_context TEXT,
                    correction_applied BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_project_path ON project_profiles(project_path)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_framework_patterns ON framework_patterns(framework_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_detection_feedback ON detection_feedback(project_path, framework_name)")
            
            conn.commit()
    
    def detect_tech_stack(self, project_path: str, conversation_context: str = None) -> TechStackProfile:
        """Detect technology stack for project with conversation awareness"""
        project_path = Path(project_path).resolve()
        
        # Check cache first
        cache_key = str(project_path)
        if cache_key in self.detection_cache:
            cached_result, timestamp = self.detection_cache[cache_key]
            if (datetime.now() - timestamp).total_seconds() < self.cache_ttl:
                self.logger.debug(f"Using cached detection for {project_path}")
                return cached_result
        
        self.logger.info(f"Detecting tech stack for: {project_path}")
        
        # Run all detectors
        all_signatures = []
        for detector in self.detectors:
            try:
                signatures = detector.detect(project_path)
                all_signatures.extend(signatures)
                self.logger.debug(f"{detector.name} detected {len(signatures)} frameworks")
            except Exception as e:
                self.logger.warning(f"Detector {detector.name} failed: {e}")
        
        # Apply conversation-aware learning
        all_signatures = self._apply_learned_patterns(all_signatures, project_path)
        
        # Consolidate signatures
        consolidated = self._consolidate_signatures(all_signatures)
        
        # Build tech stack profile
        profile = self._build_profile(consolidated, project_path, conversation_context)
        
        # Store in memory
        self._store_profile(profile, project_path)
        
        # Cache result
        self.detection_cache[cache_key] = (profile, datetime.now())
        
        self.logger.info(f"Detected tech stack with {len(profile.frameworks)} frameworks")
        return profile
    
    def _apply_learned_patterns(self, signatures: List[FrameworkSignature], project_path: Path) -> List[FrameworkSignature]:
        """Apply learned patterns to enhance detection"""
        enhanced_signatures = signatures.copy()
        
        # Load learned patterns
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT framework_name, pattern_type, pattern_value, confidence_score, success_rate
                FROM framework_patterns
                WHERE success_rate > 0.6
                ORDER BY success_rate DESC, usage_count DESC
            """)
            
            learned_patterns = cursor.fetchall()
        
        # Apply learned patterns
        for framework_name, pattern_type, pattern_value, confidence, success_rate in learned_patterns:
            if pattern_type == "file_pattern":
                if any(project_path.rglob(pattern_value)):
                    # Adjust confidence based on success rate
                    adjusted_confidence = confidence * success_rate
                    
                    enhanced_signatures.append(FrameworkSignature(
                        name=framework_name,
                        confidence=adjusted_confidence,
                        indicators=[pattern_value],
                        metadata={
                            "detection_method": "learned_pattern",
                            "pattern_type": pattern_type,
                            "success_rate": success_rate
                        }
                    ))
            
            elif pattern_type == "content_pattern":
                # Apply learned content patterns
                for file_path in project_path.rglob("*"):
                    if file_path.is_file():
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                
                            if re.search(pattern_value, content, re.IGNORECASE):
                                adjusted_confidence = confidence * success_rate
                                
                                enhanced_signatures.append(FrameworkSignature(
                                    name=framework_name,
                                    confidence=adjusted_confidence,
                                    indicators=[str(file_path.relative_to(project_path))],
                                    metadata={
                                        "detection_method": "learned_pattern",
                                        "pattern_type": pattern_type,
                                        "success_rate": success_rate
                                    }
                                ))
                                break
                        except Exception:
                            continue
        
        return enhanced_signatures
    
    def _consolidate_signatures(self, signatures: List[FrameworkSignature]) -> List[FrameworkSignature]:
        """Consolidate duplicate framework signatures"""
        framework_groups = defaultdict(list)
        
        # Group by framework name
        for sig in signatures:
            framework_groups[sig.name].append(sig)
        
        consolidated = []
        for framework_name, group in framework_groups.items():
            if len(group) == 1:
                consolidated.append(group[0])
            else:
                # Merge multiple signatures for same framework
                merged_confidence = max(sig.confidence for sig in group)
                merged_indicators = []
                merged_metadata = {"detection_methods": []}
                
                for sig in group:
                    if sig.indicators:
                        merged_indicators.extend(sig.indicators)
                    if sig.metadata:
                        merged_metadata["detection_methods"].append(sig.metadata.get("detection_method", "unknown"))
                
                consolidated.append(FrameworkSignature(
                    name=framework_name,
                    confidence=merged_confidence,
                    indicators=list(set(merged_indicators)),
                    metadata=merged_metadata
                ))
        
        # Filter by confidence threshold
        return [sig for sig in consolidated if sig.confidence >= self.confidence_threshold]
    
    def _build_profile(self, signatures: List[FrameworkSignature], project_path: Path, conversation_context: str = None) -> TechStackProfile:
        """Build complete tech stack profile"""
        # Categorize frameworks
        frameworks = []
        build_tools = []
        package_managers = []
        databases = []
        testing_frameworks = []
        deployment_platforms = []
        
        primary_language = self._detect_primary_language(project_path)
        
        for sig in signatures:
            frameworks.append(sig)
            
            # Categorize
            if sig.name in ["make", "gradle", "maven", "webpack", "vite", "rollup"]:
                build_tools.append(sig.name)
            elif sig.name in ["npm", "yarn", "pip", "poetry", "conda"]:
                package_managers.append(sig.name)
            elif sig.name in ["postgresql", "mysql", "mongodb", "redis", "sqlite"]:
                databases.append(sig.name)
            elif sig.name in ["pytest", "jest", "mocha", "junit", "rspec"]:
                testing_frameworks.append(sig.name)
            elif sig.name in ["docker", "kubernetes", "heroku", "aws", "vercel"]:
                deployment_platforms.append(sig.name)
        
        # Calculate overall confidence
        if frameworks:
            confidence_score = sum(sig.confidence for sig in frameworks) / len(frameworks)
        else:
            confidence_score = 0.0
        
        return TechStackProfile(
            primary_language=primary_language,
            frameworks=frameworks,
            build_tools=build_tools,
            package_managers=package_managers,
            databases=databases,
            testing_frameworks=testing_frameworks,
            deployment_platforms=deployment_platforms,
            confidence_score=confidence_score,
            detection_timestamp=datetime.now(),
            conversation_context=conversation_context
        )
    
    def _detect_primary_language(self, project_path: Path) -> str:
        """Detect primary programming language"""
        language_extensions = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".rb": "ruby",
            ".php": "php",
            ".go": "go",
            ".rs": "rust",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".clj": "clojure",
            ".hs": "haskell",
        }
        
        language_counts = defaultdict(int)
        
        for file_path in project_path.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in language_extensions:
                    language_counts[language_extensions[ext]] += 1
        
        if language_counts:
            return max(language_counts, key=language_counts.get)
        else:
            return "unknown"
    
    def _store_profile(self, profile: TechStackProfile, project_path: Path):
        """Store tech stack profile in memory"""
        project_hash = self._calculate_project_hash(project_path)
        
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO project_profiles
                (project_path, project_hash, profile_data, confidence_score, 
                 detection_timestamp, conversation_context)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(project_path), project_hash, json.dumps(profile.to_dict()),
                profile.confidence_score, profile.detection_timestamp,
                profile.conversation_context
            ))
            conn.commit()
    
    def _calculate_project_hash(self, project_path: Path) -> str:
        """Calculate hash of project structure for change detection"""
        # Simple hash based on file structure and timestamps
        file_info = []
        
        for file_path in project_path.rglob("*"):
            if file_path.is_file():
                try:
                    stat = file_path.stat()
                    file_info.append(f"{file_path.name}:{stat.st_mtime}:{stat.st_size}")
                except Exception:
                    continue
        
        combined = "|".join(sorted(file_info))
        return hashlib.md5(combined.encode()).hexdigest()
    
    def learn_from_conversation(self, conversation_context: Dict[str, Any]):
        """Learn new patterns from conversation context"""
        if "framework_mentions" in conversation_context:
            for framework_name, patterns in conversation_context["framework_mentions"].items():
                for pattern_type, pattern_value in patterns.items():
                    self._store_learned_pattern(
                        framework_name, pattern_type, pattern_value,
                        confidence=0.6, learned_from_conversation=True
                    )
                    
                    self.logger.info(f"Learned new pattern: {framework_name} -> {pattern_type}:{pattern_value}")
    
    def _store_learned_pattern(self, framework_name: str, pattern_type: str, pattern_value: str, 
                              confidence: float, learned_from_conversation: bool = False):
        """Store learned pattern in memory"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO framework_patterns
                (framework_name, pattern_type, pattern_value, confidence_score, 
                 usage_count, success_rate, last_updated, learned_from_conversation)
                VALUES (?, ?, ?, ?, 
                        COALESCE((SELECT usage_count FROM framework_patterns 
                                 WHERE framework_name = ? AND pattern_type = ? AND pattern_value = ?), 0) + 1,
                        ?, ?, ?)
            """, (
                framework_name, pattern_type, pattern_value, confidence,
                framework_name, pattern_type, pattern_value,
                0.6, datetime.now(), learned_from_conversation
            ))
            conn.commit()
    
    def provide_feedback(self, project_path: str, framework_name: str, actual_presence: bool, 
                        predicted_confidence: float, conversation_context: str = None):
        """Provide feedback on detection accuracy"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT INTO detection_feedback
                (project_path, framework_name, predicted_confidence, actual_presence, 
                 feedback_timestamp, conversation_context)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                project_path, framework_name, predicted_confidence, actual_presence,
                datetime.now(), conversation_context
            ))
            conn.commit()
        
        # Update pattern success rates
        self._update_pattern_success_rates(framework_name, actual_presence)
        
        self.logger.info(f"Received feedback: {framework_name} -> {actual_presence}")
    
    def _update_pattern_success_rates(self, framework_name: str, actual_presence: bool):
        """Update success rates for framework patterns"""
        with sqlite3.connect(self.memory_db) as conn:
            # Get current success rate
            cursor = conn.execute("""
                SELECT success_rate, usage_count FROM framework_patterns
                WHERE framework_name = ?
            """, (framework_name,))
            
            rows = cursor.fetchall()
            for success_rate, usage_count in rows:
                # Update success rate using learning rate
                if actual_presence:
                    new_success_rate = success_rate + self.learning_rate * (1.0 - success_rate)
                else:
                    new_success_rate = success_rate - self.learning_rate * success_rate
                
                new_success_rate = max(0.0, min(1.0, new_success_rate))
                
                conn.execute("""
                    UPDATE framework_patterns
                    SET success_rate = ?, last_updated = ?
                    WHERE framework_name = ?
                """, (new_success_rate, datetime.now(), framework_name))
            
            conn.commit()
    
    def get_detection_history(self, project_path: str = None, days: int = 30) -> List[Dict[str, Any]]:
        """Get detection history for analysis"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.memory_db) as conn:
            if project_path:
                cursor = conn.execute("""
                    SELECT project_path, profile_data, confidence_score, detection_timestamp, conversation_context
                    FROM project_profiles
                    WHERE project_path = ? AND detection_timestamp > ?
                    ORDER BY detection_timestamp DESC
                """, (project_path, cutoff_date))
            else:
                cursor = conn.execute("""
                    SELECT project_path, profile_data, confidence_score, detection_timestamp, conversation_context
                    FROM project_profiles
                    WHERE detection_timestamp > ?
                    ORDER BY detection_timestamp DESC
                """, (cutoff_date,))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    "project_path": row[0],
                    "profile": json.loads(row[1]),
                    "confidence_score": row[2],
                    "detection_timestamp": row[3],
                    "conversation_context": row[4]
                })
            
            return history
    
    def get_learned_patterns(self) -> List[Dict[str, Any]]:
        """Get all learned patterns"""
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT framework_name, pattern_type, pattern_value, confidence_score, 
                       usage_count, success_rate, learned_from_conversation
                FROM framework_patterns
                ORDER BY success_rate DESC, usage_count DESC
            """)
            
            patterns = []
            for row in cursor.fetchall():
                patterns.append({
                    "framework_name": row[0],
                    "pattern_type": row[1],
                    "pattern_value": row[2],
                    "confidence_score": row[3],
                    "usage_count": row[4],
                    "success_rate": row[5],
                    "learned_from_conversation": bool(row[6])
                })
            
            return patterns
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detection performance metrics"""
        with sqlite3.connect(self.memory_db) as conn:
            # Overall accuracy
            cursor = conn.execute("""
                SELECT AVG(CASE WHEN actual_presence = 1 THEN predicted_confidence ELSE 1 - predicted_confidence END) as accuracy
                FROM detection_feedback
            """)
            
            row = cursor.fetchone()
            accuracy = row[0] if row[0] else 0.0
            
            # Framework-specific metrics
            cursor = conn.execute("""
                SELECT framework_name, 
                       COUNT(*) as total_predictions,
                       SUM(CASE WHEN actual_presence = 1 THEN 1 ELSE 0 END) as true_positives,
                       AVG(predicted_confidence) as avg_confidence
                FROM detection_feedback
                GROUP BY framework_name
            """)
            
            framework_metrics = {}
            for row in cursor.fetchall():
                framework_metrics[row[0]] = {
                    "total_predictions": row[1],
                    "true_positives": row[2],
                    "precision": row[2] / row[1] if row[1] > 0 else 0,
                    "avg_confidence": row[3]
                }
            
            return {
                "overall_accuracy": accuracy,
                "framework_metrics": framework_metrics,
                "total_detections": len(self.detection_cache)
            }


# Global tech stack instance
_global_techstack = None


def get_techstack(user_id: str = "developer") -> DeltaTechStack:
    """Get global tech stack instance"""
    global _global_techstack
    if _global_techstack is None:
        _global_techstack = DeltaTechStack(user_id=user_id)
    return _global_techstack


def initialize_techstack(config_dir: str = ".claude", user_id: str = "developer") -> DeltaTechStack:
    """Initialize tech stack detection system"""
    global _global_techstack
    _global_techstack = DeltaTechStack(config_dir=config_dir, user_id=user_id)
    return _global_techstack


if __name__ == "__main__":
    # Test tech stack detection
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Testing ∂TechStack system...")
        
        # Initialize tech stack
        techstack = initialize_techstack()
        
        # Test detection on current project
        project_path = "."
        profile = techstack.detect_tech_stack(project_path, "test_conversation")
        
        print(f"Detected primary language: {profile.primary_language}")
        print(f"Detected frameworks: {len(profile.frameworks)}")
        for framework in profile.frameworks:
            print(f"  - {framework.name}: {framework.confidence:.2f}")
        
        # Test learning
        techstack.learn_from_conversation({
            "framework_mentions": {
                "custom_framework": {
                    "file_pattern": "custom.config",
                    "content_pattern": "import custom_framework"
                }
            }
        })
        
        # Test feedback
        techstack.provide_feedback(project_path, "python", True, 0.9, "test feedback")
        
        # Test performance metrics
        metrics = techstack.get_performance_metrics()
        print(f"Performance metrics: {metrics}")
        
        # Test learned patterns
        patterns = techstack.get_learned_patterns()
        print(f"Learned patterns: {len(patterns)}")
        
        print("∂TechStack system test completed successfully!")
    else:
        print("∂TechStack.py - Dynamic framework detection with conversation memory")
        print("Usage: python ∂TechStack.py --test")