#!/usr/bin/env python3
"""
∂Domain.py - Conversation-driven domain discovery
Part of the ∂-prefixed architecture for conversation-aware multi-agent development

This module provides intelligent domain understanding that learns from user corrections
and preferences, building domain knowledge over time through conversation interactions.
"""

import json
import os
import re
import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from enum import Enum
import statistics

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





class DomainType(Enum):
    WEB_DEVELOPMENT = "web_development"
    DATA_SCIENCE = "data_science"
    MACHINE_LEARNING = "machine_learning"
    MOBILE_DEVELOPMENT = "mobile_development"
    DESKTOP_APPLICATION = "desktop_application"
    BACKEND_API = "backend_api"
    DEVOPS_INFRASTRUCTURE = "devops_infrastructure"
    GAME_DEVELOPMENT = "game_development"
    BLOCKCHAIN = "blockchain"
    IOT_EMBEDDED = "iot_embedded"
    SCIENTIFIC_COMPUTING = "scientific_computing"
    BUSINESS_APPLICATION = "business_application"
    CONTENT_MANAGEMENT = "content_management"
    ECOMMERCE = "ecommerce"
    SOCIAL_PLATFORM = "social_platform"
    FINTECH = "fintech"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"
    UNKNOWN = "unknown"


@dataclass
class DomainIndicator:
    """Indicator for domain classification"""
    type: str  # file, keyword, pattern, framework, etc.
    value: str
    confidence: float
    source: str  # where this indicator was discovered
    context: Optional[str] = None


@dataclass
class DomainClassification:
    """Complete domain classification result"""
    primary_domain: DomainType
    secondary_domains: List[DomainType]
    confidence_score: float
    indicators: List[DomainIndicator]
    reasoning: str
    conversation_context: Optional[str] = None
    classification_timestamp: datetime = None
    
    def __post_init__(self):
        if self.classification_timestamp is None:
            self.classification_timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['primary_domain'] = self.primary_domain.value
        result['secondary_domains'] = [d.value for d in self.secondary_domains]
        result['classification_timestamp'] = self.classification_timestamp.isoformat()
        return result


class DomainAnalyzer:
    """Base class for domain analysis strategies"""
    
    def __init__(self, name: str):
        self.name = name
        self.confidence_weight = 1.0
    
    def analyze(self, project_path: Path, conversation_context: str = None) -> List[DomainIndicator]:
        """Analyze project for domain indicators"""
        raise NotImplementedError


class FileStructureAnalyzer(DomainAnalyzer):
    """Analyze domain based on file structure patterns"""
    
    def __init__(self):
        super().__init__("file_structure")
        self.domain_patterns = {
            DomainType.WEB_DEVELOPMENT: {
                "directories": ["static", "templates", "public", "assets", "components", "pages"],
                "files": ["index.html", "app.js", "main.css", "webpack.config.js", "package.json"],
                "extensions": [".html", ".css", ".js", ".jsx", ".tsx", ".vue", ".scss"]
            },
            DomainType.DATA_SCIENCE: {
                "directories": ["data", "notebooks", "analysis", "models", "datasets"],
                "files": ["requirements.txt", "environment.yml", "setup.py"],
                "extensions": [".ipynb", ".py", ".r", ".csv", ".json", ".parquet"]
            },
            DomainType.MACHINE_LEARNING: {
                "directories": ["models", "training", "inference", "data", "experiments"],
                "files": ["model.py", "train.py", "evaluate.py", "requirements.txt"],
                "extensions": [".py", ".ipynb", ".pkl", ".h5", ".pb", ".onnx"]
            },
            DomainType.MOBILE_DEVELOPMENT: {
                "directories": ["android", "ios", "lib", "assets", "resources"],
                "files": ["pubspec.yaml", "build.gradle", "Info.plist", "AndroidManifest.xml"],
                "extensions": [".dart", ".swift", ".kt", ".java", ".xml"]
            },
            DomainType.BACKEND_API: {
                "directories": ["api", "routes", "controllers", "middleware", "services"],
                "files": ["app.py", "server.js", "main.go", "requirements.txt", "package.json"],
                "extensions": [".py", ".js", ".go", ".java", ".rb", ".php"]
            },
            DomainType.DEVOPS_INFRASTRUCTURE: {
                "directories": ["terraform", "ansible", "docker", "k8s", "scripts"],
                "files": ["Dockerfile", "docker-compose.yml", "main.tf", "playbook.yml"],
                "extensions": [".yml", ".yaml", ".tf", ".json", ".sh"]
            },
            DomainType.GAME_DEVELOPMENT: {
                "directories": ["assets", "scenes", "scripts", "resources", "audio", "textures"],
                "files": ["game.py", "main.unity", "project.godot"],
                "extensions": [".py", ".cs", ".cpp", ".unity", ".prefab", ".png", ".wav"]
            }
        }
    
    def analyze(self, project_path: Path, conversation_context: str = None) -> List[DomainIndicator]:
        """Analyze project file structure for domain indicators"""
        indicators = []
        
        # Get all files and directories
        all_files = list(project_path.rglob("*"))
        all_dirs = [f for f in all_files if f.is_dir()]
        all_file_names = [f.name for f in all_files if f.is_file()]
        all_extensions = set(f.suffix.lower() for f in all_files if f.is_file() and f.suffix)
        
        # Analyze against each domain pattern
        for domain_type, patterns in self.domain_patterns.items():
            domain_score = 0.0
            matched_indicators = []
            
            # Check directory patterns
            if "directories" in patterns:
                for dir_pattern in patterns["directories"]:
                    if any(dir_pattern.lower() in str(d).lower() for d in all_dirs):
                        domain_score += 0.3
                        matched_indicators.append(f"directory:{dir_pattern}")
            
            # Check file patterns
            if "files" in patterns:
                for file_pattern in patterns["files"]:
                    if any(file_pattern.lower() in name.lower() for name in all_file_names):
                        domain_score += 0.4
                        matched_indicators.append(f"file:{file_pattern}")
            
            # Check extension patterns
            if "extensions" in patterns:
                matching_extensions = all_extensions.intersection(set(patterns["extensions"]))
                if matching_extensions:
                    domain_score += len(matching_extensions) * 0.2
                    matched_indicators.extend([f"extension:{ext}" for ext in matching_extensions])
            
            # Create indicator if significant match
            if domain_score > 0.5:
                indicators.append(DomainIndicator(
                    type="file_structure",
                    value=domain_type.value,
                    confidence=min(domain_score, 1.0),
                    source="file_structure_analyzer",
                    context=f"Matched: {', '.join(matched_indicators)}"
                ))
        
        return indicators


class ContentAnalyzer(DomainAnalyzer):
    """Analyze domain based on file content patterns"""
    
    def __init__(self):
        super().__init__("content_analysis")
        self.domain_keywords = {
            DomainType.WEB_DEVELOPMENT: [
                "react", "vue", "angular", "html", "css", "javascript", "frontend",
                "backend", "express", "django", "flask", "spring", "laravel"
            ],
            DomainType.DATA_SCIENCE: [
                "pandas", "numpy", "matplotlib", "seaborn", "plotly", "analysis",
                "dataset", "csv", "dataframe", "visualization", "statistics"
            ],
            DomainType.MACHINE_LEARNING: [
                "tensorflow", "pytorch", "scikit-learn", "keras", "model", "training",
                "neural", "network", "deep learning", "classifier", "regression"
            ],
            DomainType.MOBILE_DEVELOPMENT: [
                "flutter", "react native", "ios", "android", "mobile", "app",
                "swift", "kotlin", "dart", "xamarin"
            ],
            DomainType.BACKEND_API: [
                "api", "rest", "graphql", "microservice", "server", "database",
                "endpoint", "middleware", "authentication", "authorization"
            ],
            DomainType.DEVOPS_INFRASTRUCTURE: [
                "docker", "kubernetes", "terraform", "ansible", "ci/cd", "deployment",
                "infrastructure", "cloud", "aws", "azure", "gcp", "monitoring"
            ],
            DomainType.GAME_DEVELOPMENT: [
                "unity", "unreal", "game", "player", "scene", "sprite", "physics",
                "collision", "animation", "godot", "pygame"
            ],
            DomainType.BLOCKCHAIN: [
                "blockchain", "ethereum", "bitcoin", "smart contract", "web3",
                "cryptocurrency", "defi", "nft", "solidity", "truffle"
            ],
            DomainType.FINTECH: [
                "payment", "banking", "finance", "trading", "investment", "wallet",
                "transaction", "cryptocurrency", "risk", "compliance"
            ],
            DomainType.HEALTHCARE: [
                "patient", "medical", "health", "diagnosis", "treatment", "clinical",
                "hospital", "doctor", "nurse", "pharmacy", "telemedicine"
            ],
            DomainType.ECOMMERCE: [
                "shopping", "cart", "product", "order", "payment", "checkout",
                "inventory", "customer", "store", "marketplace", "retail"
            ]
        }
    
    def analyze(self, project_path: Path, conversation_context: str = None) -> List[DomainIndicator]:
        """Analyze project content for domain keywords"""
        indicators = []
        
        # Collect all text content
        all_content = ""
        content_files = []
        
        for file_path in project_path.rglob("*"):
            if file_path.is_file() and self._is_text_file(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        all_content += " " + content.lower()
                        content_files.append(str(file_path.relative_to(project_path)))
                except Exception:
                    continue
        
        # Analyze keywords for each domain
        for domain_type, keywords in self.domain_keywords.items():
            keyword_matches = []
            total_score = 0.0
            
            for keyword in keywords:
                # Count occurrences of keyword
                count = all_content.count(keyword.lower())
                if count > 0:
                    keyword_matches.append(f"{keyword}({count})")
                    # Logarithmic scoring to avoid overwhelming single keywords
                    total_score += min(0.1 * count, 0.5)
            
            # Create indicator if significant matches
            if total_score > 0.3:
                indicators.append(DomainIndicator(
                    type="content_keywords",
                    value=domain_type.value,
                    confidence=min(total_score, 1.0),
                    source="content_analyzer",
                    context=f"Keywords: {', '.join(keyword_matches[:10])}"  # Limit to top 10
                ))
        
        return indicators
    
    def _is_text_file(self, file_path: Path) -> bool:
        """Check if file is likely to contain readable text"""
        text_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.scss', '.less',
            '.java', '.cpp', '.c', '.h', '.rb', '.php', '.go', '.rs', '.swift',
            '.kt', '.scala', '.clj', '.hs', '.r', '.sql', '.sh', '.bat', '.ps1',
            '.yml', '.yaml', '.json', '.xml', '.md', '.txt', '.rst', '.cfg',
            '.ini', '.conf', '.properties', '.gradle', '.maven', '.dockerfile'
        }
        
        return file_path.suffix.lower() in text_extensions


class ConversationAnalyzer(DomainAnalyzer):
    """Analyze domain based on conversation context"""
    
    def __init__(self):
        super().__init__("conversation_analysis")
        self.domain_conversation_patterns = {
            DomainType.WEB_DEVELOPMENT: [
                "website", "frontend", "backend", "user interface", "web app",
                "responsive", "browser", "client-side", "server-side"
            ],
            DomainType.DATA_SCIENCE: [
                "data analysis", "visualization", "dataset", "statistics", "insights",
                "exploration", "cleaning", "preprocessing", "correlation"
            ],
            DomainType.MACHINE_LEARNING: [
                "model training", "prediction", "classification", "regression",
                "neural network", "deep learning", "ai", "artificial intelligence"
            ],
            DomainType.MOBILE_DEVELOPMENT: [
                "mobile app", "ios app", "android app", "smartphone", "tablet",
                "app store", "play store", "mobile ui"
            ],
            DomainType.BACKEND_API: [
                "api development", "microservice", "server", "database integration",
                "rest api", "graphql", "authentication", "authorization"
            ],
            DomainType.GAME_DEVELOPMENT: [
                "game", "player", "level", "character", "gameplay", "graphics",
                "animation", "physics", "collision detection"
            ]
        }
    
    def analyze(self, project_path: Path, conversation_context: str = None) -> List[DomainIndicator]:
        """Analyze conversation context for domain indicators"""
        indicators = []
        
        if not conversation_context:
            return indicators
        
        conversation_lower = conversation_context.lower()
        
        for domain_type, patterns in self.domain_conversation_patterns.items():
            matches = []
            total_confidence = 0.0
            
            for pattern in patterns:
                if pattern in conversation_lower:
                    matches.append(pattern)
                    total_confidence += 0.2
            
            if total_confidence > 0.3:
                indicators.append(DomainIndicator(
                    type="conversation_context",
                    value=domain_type.value,
                    confidence=min(total_confidence, 1.0),
                    source="conversation_analyzer",
                    context=f"Mentioned: {', '.join(matches)}"
                ))
        
        return indicators


class DeltaDomain:
    """
    ∂Domain - Conversation-driven domain discovery
    
    Features:
    - Conversation-driven domain understanding
    - Learns from user corrections and preferences
    - Builds domain knowledge over time
    - Multi-analyzer approach for robust classification
    """
    
    def __init__(self, config_dir: str = ".claude", user_id: str = "developer"):
        self.config_dir = Path(config_dir)
        self.user_id = user_id
        self.config = get_config(user_id)
        self.logger = get_logger("∂Domain")
        
        # Initialize memory systems
        self.memory_db = self.config_dir / "∂domain_memory.db"
        self._init_memory_systems()
        self._init_database()
        
        # Initialize analyzers
        self.analyzers = [
            FileStructureAnalyzer(),
            ContentAnalyzer(),
            ConversationAnalyzer()
        ]
        
        # Classification parameters
        self.confidence_threshold = 0.4
        self.learning_rate = 0.1
        
        # Classification cache
        self.classification_cache = {}
        self.cache_ttl = 600  # 10 minutes
        
        self.logger.info("∂Domain initialized with conversation-driven classification")
    
    def _init_memory_systems(self):
        """Initialize LangMem and fallback SQLite memory systems"""
        global LANGMEM_AVAILABLE
        self.memory_tools = []
        
        if LANGMEM_AVAILABLE:
            try:
                self.store = InMemoryStore(
                    index={"dims": 1536, "embed": "openai:text-embedding-3-small"}
                )
                self.namespace = ("∂domain", self.user_id)
                self.memory_tools = [
                    create_manage_memory_tool(namespace=self.namespace),
                    create_search_memory_tool(namespace=self.namespace),
                ]
                self.logger.info("LangMem memory system initialized")
            except Exception as e:
                self.logger.warning(f"LangMem initialization failed: {e}")
                LANGMEM_AVAILABLE = False
    
    def _init_database(self):
        """Initialize SQLite database for domain memory"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS domain_classifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_path TEXT NOT NULL,
                    project_hash TEXT NOT NULL,
                    primary_domain TEXT NOT NULL,
                    secondary_domains TEXT,
                    confidence_score REAL NOT NULL,
                    indicators TEXT NOT NULL,
                    reasoning TEXT,
                    conversation_context TEXT,
                    classification_timestamp TIMESTAMP NOT NULL,
                    user_validated BOOLEAN DEFAULT FALSE,
                    UNIQUE(project_path, project_hash)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS domain_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_path TEXT NOT NULL,
                    predicted_domain TEXT NOT NULL,
                    actual_domain TEXT NOT NULL,
                    feedback_timestamp TIMESTAMP NOT NULL,
                    conversation_context TEXT,
                    correction_reasoning TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learned_indicators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain_type TEXT NOT NULL,
                    indicator_type TEXT NOT NULL,
                    indicator_value TEXT NOT NULL,
                    confidence_weight REAL NOT NULL,
                    success_rate REAL DEFAULT 0.5,
                    usage_count INTEGER DEFAULT 1,
                    learned_from_conversation BOOLEAN DEFAULT FALSE,
                    last_updated TIMESTAMP NOT NULL,
                    UNIQUE(domain_type, indicator_type, indicator_value)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS domain_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain_type TEXT NOT NULL,
                    pattern_description TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    discovery_source TEXT NOT NULL,
                    created_timestamp TIMESTAMP NOT NULL
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_domain_project ON domain_classifications(project_path)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_domain_feedback ON domain_feedback(predicted_domain, actual_domain)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_learned_indicators ON learned_indicators(domain_type, success_rate)")
            
            conn.commit()
    
    def classify_project_domain(self, project_path: str, conversation_context: str = None) -> DomainClassification:
        """Classify project domain with conversation awareness"""
        project_path = Path(project_path).resolve()
        
        # Check cache first
        cache_key = f"{project_path}:{conversation_context or 'none'}"
        if cache_key in self.classification_cache:
            cached_result, timestamp = self.classification_cache[cache_key]
            if (datetime.now() - timestamp).total_seconds() < self.cache_ttl:
                self.logger.debug(f"Using cached classification for {project_path}")
                return cached_result
        
        self.logger.info(f"Classifying domain for: {project_path}")
        
        # Collect indicators from all analyzers
        all_indicators = []
        for analyzer in self.analyzers:
            try:
                indicators = analyzer.analyze(project_path, conversation_context)
                all_indicators.extend(indicators)
                self.logger.debug(f"{analyzer.name} found {len(indicators)} indicators")
            except Exception as e:
                self.logger.warning(f"Analyzer {analyzer.name} failed: {e}")
        
        # Apply learned patterns
        all_indicators.extend(self._apply_learned_indicators(project_path, conversation_context))
        
        # Classify domain
        classification = self._classify_from_indicators(all_indicators, conversation_context)
        
        # Store classification
        self._store_classification(classification, project_path)
        
        # Cache result
        self.classification_cache[cache_key] = (classification, datetime.now())
        
        self.logger.info(f"Classified as {classification.primary_domain.value} with {classification.confidence_score:.2f} confidence")
        return classification
    
    def _apply_learned_indicators(self, project_path: Path, conversation_context: str = None) -> List[DomainIndicator]:
        """Apply learned indicators to enhance classification"""
        indicators = []
        
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT domain_type, indicator_type, indicator_value, confidence_weight, success_rate
                FROM learned_indicators
                WHERE success_rate > 0.6
                ORDER BY success_rate DESC, usage_count DESC
            """)
            
            learned_indicators = cursor.fetchall()
        
        for domain_type, indicator_type, indicator_value, confidence_weight, success_rate in learned_indicators:
            # Apply learned indicators based on type
            if indicator_type == "file_pattern":
                if any(project_path.rglob(indicator_value)):
                    adjusted_confidence = confidence_weight * success_rate
                    indicators.append(DomainIndicator(
                        type="learned_file_pattern",
                        value=domain_type,
                        confidence=adjusted_confidence,
                        source="learned_indicators",
                        context=f"Pattern: {indicator_value} (success_rate: {success_rate:.2f})"
                    ))
            
            elif indicator_type == "content_keyword" and conversation_context:
                if indicator_value.lower() in conversation_context.lower():
                    adjusted_confidence = confidence_weight * success_rate
                    indicators.append(DomainIndicator(
                        type="learned_conversation_keyword",
                        value=domain_type,
                        confidence=adjusted_confidence,
                        source="learned_indicators",
                        context=f"Keyword: {indicator_value} (success_rate: {success_rate:.2f})"
                    ))
        
        return indicators
    
    def _classify_from_indicators(self, indicators: List[DomainIndicator], conversation_context: str = None) -> DomainClassification:
        """Classify domain from collected indicators"""
        if not indicators:
            return DomainClassification(
                primary_domain=DomainType.UNKNOWN,
                secondary_domains=[],
                confidence_score=0.0,
                indicators=[],
                reasoning="No domain indicators found",
                conversation_context=conversation_context
            )
        
        # Group indicators by domain
        domain_scores = defaultdict(list)
        for indicator in indicators:
            try:
                domain_type = DomainType(indicator.value)
                domain_scores[domain_type].append(indicator.confidence)
            except ValueError:
                # Skip invalid domain types
                continue
        
        # Calculate aggregate scores for each domain
        domain_confidences = {}
        for domain_type, confidences in domain_scores.items():
            # Use weighted average with diminishing returns
            if confidences:
                # Sort confidences in descending order
                sorted_confidences = sorted(confidences, reverse=True)
                
                # Apply diminishing returns: first indicator gets full weight,
                # subsequent indicators get reduced weight
                weighted_sum = 0.0
                total_weight = 0.0
                
                for i, confidence in enumerate(sorted_confidences):
                    weight = 1.0 / (1 + i * 0.3)  # Diminishing returns
                    weighted_sum += confidence * weight
                    total_weight += weight
                
                domain_confidences[domain_type] = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        # Sort domains by confidence
        sorted_domains = sorted(domain_confidences.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_domains:
            primary_domain = DomainType.UNKNOWN
            confidence_score = 0.0
            secondary_domains = []
            reasoning = "No valid domain indicators found"
        else:
            primary_domain = sorted_domains[0][0]
            confidence_score = sorted_domains[0][1]
            
            # Secondary domains with significant confidence
            secondary_domains = [
                domain for domain, conf in sorted_domains[1:]
                if conf > self.confidence_threshold * 0.6
            ]
            
            # Generate reasoning
            primary_indicators = [ind for ind in indicators if ind.value == primary_domain.value]
            reasoning = self._generate_reasoning(primary_domain, primary_indicators, confidence_score)
        
        return DomainClassification(
            primary_domain=primary_domain,
            secondary_domains=secondary_domains,
            confidence_score=confidence_score,
            indicators=indicators,
            reasoning=reasoning,
            conversation_context=conversation_context
        )
    
    def _generate_reasoning(self, domain: DomainType, indicators: List[DomainIndicator], confidence: float) -> str:
        """Generate human-readable reasoning for classification"""
        if not indicators:
            return f"Classified as {domain.value} with low confidence"
        
        # Group indicators by type
        indicator_groups = defaultdict(list)
        for indicator in indicators:
            indicator_groups[indicator.type].append(indicator)
        
        reasoning_parts = [f"Classified as {domain.value} (confidence: {confidence:.2f}) based on:"]
        
        for indicator_type, type_indicators in indicator_groups.items():
            if len(type_indicators) == 1:
                ind = type_indicators[0]
                reasoning_parts.append(f"- {indicator_type}: {ind.context or ind.value}")
            else:
                avg_confidence = statistics.mean(ind.confidence for ind in type_indicators)
                reasoning_parts.append(f"- {indicator_type}: {len(type_indicators)} indicators (avg confidence: {avg_confidence:.2f})")
        
        return " ".join(reasoning_parts)
    
    def _store_classification(self, classification: DomainClassification, project_path: Path):
        """Store classification in memory"""
        project_hash = self._calculate_project_hash(project_path)
        
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO domain_classifications
                (project_path, project_hash, primary_domain, secondary_domains,
                 confidence_score, indicators, reasoning, conversation_context, classification_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(project_path), project_hash, classification.primary_domain.value,
                json.dumps([d.value for d in classification.secondary_domains]),
                classification.confidence_score, json.dumps([ind.__dict__ for ind in classification.indicators]),
                classification.reasoning, classification.conversation_context,
                classification.classification_timestamp
            ))
            conn.commit()
    
    def _calculate_project_hash(self, project_path: Path) -> str:
        """Calculate hash of project for change detection"""
        # Simple hash based on key files and structure
        key_info = []
        
        try:
            # Include key files and their sizes
            for pattern in ["*.py", "*.js", "*.html", "*.json", "*.yml", "package.json", "requirements.txt"]:
                for file_path in project_path.rglob(pattern):
                    if file_path.is_file():
                        try:
                            stat = file_path.stat()
                            key_info.append(f"{file_path.name}:{stat.st_size}")
                        except Exception:
                            continue
                        
                        # Limit to avoid too many files
                        if len(key_info) > 50:
                            break
                
                if len(key_info) > 50:
                    break
        except Exception:
            # Fallback to simple timestamp
            key_info = [str(datetime.now().timestamp())]
        
        combined = "|".join(sorted(key_info))
        return hashlib.md5(combined.encode()).hexdigest()
    
    def provide_feedback(self, project_path: str, predicted_domain: str, actual_domain: str,
                        conversation_context: str = None, reasoning: str = None):
        """Provide feedback on domain classification accuracy"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT INTO domain_feedback
                (project_path, predicted_domain, actual_domain, feedback_timestamp,
                 conversation_context, correction_reasoning)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                project_path, predicted_domain, actual_domain, datetime.now(),
                conversation_context, reasoning
            ))
            conn.commit()
        
        # Update learned indicators based on feedback
        self._update_indicator_success_rates(predicted_domain, actual_domain)
        
        self.logger.info(f"Received feedback: {predicted_domain} -> {actual_domain}")
    
    def _update_indicator_success_rates(self, predicted_domain: str, actual_domain: str):
        """Update success rates for indicators based on feedback"""
        success = predicted_domain == actual_domain
        
        with sqlite3.connect(self.memory_db) as conn:
            # Update success rates for all indicators of the predicted domain
            cursor = conn.execute("""
                SELECT id, success_rate, usage_count FROM learned_indicators
                WHERE domain_type = ?
            """, (predicted_domain,))
            
            for indicator_id, current_success_rate, usage_count in cursor.fetchall():
                # Apply learning rate to update success rate
                if success:
                    new_success_rate = current_success_rate + self.learning_rate * (1.0 - current_success_rate)
                else:
                    new_success_rate = current_success_rate - self.learning_rate * current_success_rate
                
                new_success_rate = max(0.0, min(1.0, new_success_rate))
                
                conn.execute("""
                    UPDATE learned_indicators
                    SET success_rate = ?, usage_count = usage_count + 1, last_updated = ?
                    WHERE id = ?
                """, (new_success_rate, datetime.now(), indicator_id))
            
            conn.commit()
    
    def learn_from_conversation(self, conversation_context: Dict[str, Any]):
        """Learn new domain patterns from conversation"""
        if "domain_hints" in conversation_context:
            for domain_name, hints in conversation_context["domain_hints"].items():
                try:
                    domain_type = DomainType(domain_name)
                    
                    # Learn file patterns
                    if "file_patterns" in hints:
                        for pattern in hints["file_patterns"]:
                            self._store_learned_indicator(
                                domain_type.value, "file_pattern", pattern,
                                confidence_weight=0.7, learned_from_conversation=True
                            )
                    
                    # Learn keywords
                    if "keywords" in hints:
                        for keyword in hints["keywords"]:
                            self._store_learned_indicator(
                                domain_type.value, "content_keyword", keyword,
                                confidence_weight=0.5, learned_from_conversation=True
                            )
                    
                    self.logger.info(f"Learned new patterns for {domain_name}")
                    
                except ValueError:
                    self.logger.warning(f"Invalid domain type in conversation: {domain_name}")
    
    def _store_learned_indicator(self, domain_type: str, indicator_type: str, indicator_value: str,
                                confidence_weight: float, learned_from_conversation: bool = False):
        """Store learned indicator in database"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO learned_indicators
                (domain_type, indicator_type, indicator_value, confidence_weight,
                 success_rate, usage_count, learned_from_conversation, last_updated)
                VALUES (?, ?, ?, ?, 
                        COALESCE((SELECT success_rate FROM learned_indicators 
                                 WHERE domain_type = ? AND indicator_type = ? AND indicator_value = ?), 0.6),
                        COALESCE((SELECT usage_count FROM learned_indicators 
                                 WHERE domain_type = ? AND indicator_type = ? AND indicator_value = ?), 0) + 1,
                        ?, ?)
            """, (
                domain_type, indicator_type, indicator_value, confidence_weight,
                domain_type, indicator_type, indicator_value,
                domain_type, indicator_type, indicator_value,
                learned_from_conversation, datetime.now()
            ))
            conn.commit()
    
    def get_classification_history(self, project_path: str = None, days: int = 30) -> List[Dict[str, Any]]:
        """Get classification history"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.memory_db) as conn:
            if project_path:
                cursor = conn.execute("""
                    SELECT project_path, primary_domain, secondary_domains, confidence_score,
                           reasoning, conversation_context, classification_timestamp
                    FROM domain_classifications
                    WHERE project_path = ? AND classification_timestamp > ?
                    ORDER BY classification_timestamp DESC
                """, (project_path, cutoff_date))
            else:
                cursor = conn.execute("""
                    SELECT project_path, primary_domain, secondary_domains, confidence_score,
                           reasoning, conversation_context, classification_timestamp
                    FROM domain_classifications
                    WHERE classification_timestamp > ?
                    ORDER BY classification_timestamp DESC
                """, (cutoff_date,))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    "project_path": row[0],
                    "primary_domain": row[1],
                    "secondary_domains": json.loads(row[2]) if row[2] else [],
                    "confidence_score": row[3],
                    "reasoning": row[4],
                    "conversation_context": row[5],
                    "classification_timestamp": row[6]
                })
            
            return history
    
    def get_learned_indicators(self) -> List[Dict[str, Any]]:
        """Get all learned indicators"""
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT domain_type, indicator_type, indicator_value, confidence_weight,
                       success_rate, usage_count, learned_from_conversation, last_updated
                FROM learned_indicators
                ORDER BY success_rate DESC, usage_count DESC
            """)
            
            indicators = []
            for row in cursor.fetchall():
                indicators.append({
                    "domain_type": row[0],
                    "indicator_type": row[1],
                    "indicator_value": row[2],
                    "confidence_weight": row[3],
                    "success_rate": row[4],
                    "usage_count": row[5],
                    "learned_from_conversation": bool(row[6]),
                    "last_updated": row[7]
                })
            
            return indicators
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get domain classification performance metrics"""
        with sqlite3.connect(self.memory_db) as conn:
            # Overall accuracy
            cursor = conn.execute("""
                SELECT COUNT(*) as total_feedback,
                       SUM(CASE WHEN predicted_domain = actual_domain THEN 1 ELSE 0 END) as correct_predictions
                FROM domain_feedback
            """)
            
            row = cursor.fetchone()
            total_feedback = row[0] if row[0] else 0
            correct_predictions = row[1] if row[1] else 0
            accuracy = correct_predictions / total_feedback if total_feedback > 0 else 0.0
            
            # Domain-specific metrics
            cursor = conn.execute("""
                SELECT predicted_domain,
                       COUNT(*) as total_predictions,
                       SUM(CASE WHEN predicted_domain = actual_domain THEN 1 ELSE 0 END) as correct_predictions
                FROM domain_feedback
                GROUP BY predicted_domain
            """)
            
            domain_metrics = {}
            for row in cursor.fetchall():
                domain_metrics[row[0]] = {
                    "total_predictions": row[1],
                    "correct_predictions": row[2],
                    "accuracy": row[2] / row[1] if row[1] > 0 else 0.0
                }
            
            # Recent classifications
            cursor = conn.execute("""
                SELECT COUNT(*) as recent_classifications
                FROM domain_classifications
                WHERE classification_timestamp > datetime('now', '-7 days')
            """)
            
            recent_count = cursor.fetchone()[0]
            
            return {
                "overall_accuracy": accuracy,
                "total_feedback": total_feedback,
                "domain_metrics": domain_metrics,
                "recent_classifications": recent_count,
                "learned_indicators_count": len(self.get_learned_indicators())
            }


# Global domain instance
_global_domain = None


def get_domain(user_id: str = "developer") -> DeltaDomain:
    """Get global domain instance"""
    global _global_domain
    if _global_domain is None:
        _global_domain = DeltaDomain(user_id=user_id)
    return _global_domain


def initialize_domain(config_dir: str = ".claude", user_id: str = "developer") -> DeltaDomain:
    """Initialize domain classification system"""
    global _global_domain
    _global_domain = DeltaDomain(config_dir=config_dir, user_id=user_id)
    return _global_domain


if __name__ == "__main__":
    # Test domain classification
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Testing ∂Domain system...")
        
        # Initialize domain system
        domain = initialize_domain()
        
        # Test classification on current project
        project_path = "."
        classification = domain.classify_project_domain(
            project_path, 
            "I'm working on a Python framework detection system"
        )
        
        print(f"Primary domain: {classification.primary_domain.value}")
        print(f"Confidence: {classification.confidence_score:.2f}")
        print(f"Secondary domains: {[d.value for d in classification.secondary_domains]}")
        print(f"Reasoning: {classification.reasoning}")
        print(f"Indicators found: {len(classification.indicators)}")
        
        # Test learning
        domain.learn_from_conversation({
            "domain_hints": {
                "machine_learning": {
                    "file_patterns": ["*.model", "train_*.py"],
                    "keywords": ["neural network", "deep learning"]
                }
            }
        })
        
        # Test feedback
        domain.provide_feedback(
            project_path, 
            classification.primary_domain.value, 
            "backend_api",
            "Actually this is more of a backend API project"
        )
        
        # Test performance metrics
        metrics = domain.get_performance_metrics()
        print(f"Performance metrics: {metrics}")
        
        # Test learned indicators
        indicators = domain.get_learned_indicators()
        print(f"Learned indicators: {len(indicators)}")
        
        print("∂Domain system test completed successfully!")
    else:
        print("∂Domain.py - Conversation-driven domain discovery")
        print("Usage: python ∂Domain.py --test")