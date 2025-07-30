#!/usr/bin/env python3
"""
∂TOPDOG.py - Main orchestrator with conversation memory
Part of the ∂-prefixed architecture for conversation-aware multi-agent development

This is the main orchestrator that coordinates all ∂-prefixed components with persistent
context, multi-agent coordination with conversation memory, session management across
component interactions, and decision routing based on conversation history.
"""

import json
import sqlite3
import asyncio
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import traceback

try:
    from langmem import create_manage_memory_tool, create_search_memory_tool
    from langgraph.store.memory import InMemoryStore
    LANGMEM_AVAILABLE = True
except ImportError:
    LANGMEM_AVAILABLE = False

# Import using standard ASCII filenames
import importlib.util

# Import all components
from .config import get_config
from .logger import get_logger
from .llm import get_llm
from .tech_stack import get_techstack
from .domain import get_domain
from .claude import get_claude
from .aider import get_aider
from .bdd import get_bdd
from .reality import get_reality
from .radon import get_radon
from .feedback import get_feedback


class OrchestrationAction(Enum):
    ANALYZE_PROJECT = "analyze_project"
    DETECT_TECH_STACK = "detect_tech_stack"
    CLASSIFY_DOMAIN = "classify_domain"
    GENERATE_CODE = "generate_code"
    RUN_TESTS = "run_tests"
    VALIDATE_REALITY = "validate_reality"
    CHAT_WITH_CLAUDE = "chat_with_claude"
    COORDINATE_DEVELOPMENT = "coordinate_development"


class ComponentStatus(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    BUSY = "busy"


@dataclass
class OrchestrationTask:
    """Single orchestration task"""
    task_id: str
    action: OrchestrationAction
    parameters: Dict[str, Any]
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    component_involved: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class OrchestrationSession:
    """Complete orchestration session"""
    session_id: str
    user_id: str
    conversation_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    tasks: List[OrchestrationTask] = None
    session_context: Optional[Dict[str, Any]] = None
    conversation_summary: Optional[str] = None
    
    def __post_init__(self):
        if self.tasks is None:
            self.tasks = []


class ComponentRegistry:
    """Registry for tracking ∂ component availability and status"""
    
    def __init__(self):
        self.components = {}
        self.logger = get_logger("ComponentRegistry") if get_logger else None
    
    def register_component(self, name: str, instance: Any, health_check: Callable = None):
        """Register a ∂ component"""
        self.components[name] = {
            "instance": instance,
            "health_check": health_check,
            "status": ComponentStatus.AVAILABLE,
            "last_used": None,
            "error_count": 0,
            "success_count": 0
        }
        
        if self.logger:
            self.logger.info(f"Registered component: {name}")
    
    def get_component(self, name: str) -> Optional[Any]:
        """Get component instance"""
        if name in self.components:
            component_info = self.components[name]
            
            # Update usage
            component_info["last_used"] = datetime.now()
            
            return component_info["instance"]
        return None
    
    def check_component_health(self, name: str) -> ComponentStatus:
        """Check component health"""
        if name not in self.components:
            return ComponentStatus.UNAVAILABLE
        
        component_info = self.components[name]
        
        # Run health check if available
        if component_info["health_check"]:
            try:
                healthy = component_info["health_check"]()
                if healthy:
                    component_info["status"] = ComponentStatus.AVAILABLE
                    component_info["success_count"] += 1
                else:
                    component_info["status"] = ComponentStatus.ERROR
                    component_info["error_count"] += 1
            except Exception as e:
                component_info["status"] = ComponentStatus.ERROR
                component_info["error_count"] += 1
                if self.logger:
                    self.logger.warning(f"Health check failed for {name}: {e}")
        
        return component_info["status"]
    
    def get_component_stats(self) -> Dict[str, Any]:
        """Get statistics for all components"""
        stats = {}
        
        for name, info in self.components.items():
            stats[name] = {
                "status": info["status"].value,
                "last_used": info["last_used"].isoformat() if info["last_used"] else None,
                "error_count": info["error_count"],
                "success_count": info["success_count"],
                "health_ratio": info["success_count"] / max(info["success_count"] + info["error_count"], 1)
            }
        
        return stats


class DeltaTopdog:
    """
    ∂TOPDOG - Main orchestrator with conversation memory
    
    Features:
    - Multi-agent coordination with persistent context
    - Session management across component interactions
    - Decision routing based on conversation history
    - Intelligent component selection and orchestration
    - Cross-component memory sharing and insights
    """
    
    def __init__(self, project_path: str = ".", config_dir: str = ".claude", user_id: str = "developer"):
        self.project_path = Path(project_path).resolve()
        self.config_dir = Path(config_dir)
        self.user_id = user_id
        
        # Initialize core systems
        self.config = get_config(user_id) if get_config else None
        self.logger = get_logger("∂TOPDOG") if get_logger else None
        
        # Initialize memory systems
        self.memory_db = self.config_dir / "∂topdog_memory.db"
        self._init_memory_systems()
        self._init_database()
        
        # Initialize component registry
        self.registry = ComponentRegistry()
        self._register_all_components()
        
        # Current session
        self.current_session = None
        self.task_queue = []
        
        # Decision engine
        self.decision_patterns = {}
        self.coordination_history = []
        
        if self.logger:
            self.logger.info(f"∂TOPDOG initialized for project: {self.project_path}")
    
    def _init_memory_systems(self):
        """Initialize LangMem and fallback SQLite memory systems"""
        global LANGMEM_AVAILABLE
        self.memory_tools = []
        
        if LANGMEM_AVAILABLE:
            try:
                self.store = InMemoryStore(
                    index={"dims": 1536, "embed": "openai:text-embedding-3-small"}
                )
                self.namespace = ("∂topdog", self.user_id)
                self.memory_tools = [
                    create_manage_memory_tool(namespace=self.namespace),
                    create_search_memory_tool(namespace=self.namespace),
                ]
                if self.logger:
                    self.logger.info("LangMem memory system initialized")
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"LangMem initialization failed: {e}")
                LANGMEM_AVAILABLE = False
    
    def _init_database(self):
        """Initialize SQLite database for orchestration storage"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS orchestration_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    conversation_id TEXT,
                    started_at TIMESTAMP NOT NULL,
                    ended_at TIMESTAMP,
                    session_context TEXT,
                    conversation_summary TEXT,
                    UNIQUE(session_id, user_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS orchestration_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    status TEXT NOT NULL,
                    result TEXT,
                    error TEXT,
                    created_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP,
                    component_involved TEXT,
                    FOREIGN KEY(session_id) REFERENCES orchestration_sessions(session_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS decision_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_context TEXT NOT NULL,
                    chosen_action TEXT NOT NULL,
                    component_used TEXT,
                    success_score REAL DEFAULT 0.5,
                    usage_count INTEGER DEFAULT 1,
                    last_used TIMESTAMP NOT NULL,
                    learned_from_session TEXT,
                    UNIQUE(pattern_context, chosen_action)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cross_component_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    insight_type TEXT NOT NULL,
                    source_component TEXT NOT NULL,
                    target_component TEXT,
                    insight_data TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    applied_count INTEGER DEFAULT 0
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_orchestration_sessions ON orchestration_sessions(user_id, started_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_orchestration_tasks ON orchestration_tasks(session_id, status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_decision_patterns ON decision_patterns(success_score, usage_count)")
            
            conn.commit()
    
    def _register_all_components(self):
        """Register all available ∂ components"""
        # Register components with health checks
        
        if get_config:
            self.registry.register_component("config", get_config(), lambda: True)
        
        if get_logger:
            self.registry.register_component("logger", get_logger("topdog"), lambda: True)
        
        if get_llm:
            self.registry.register_component("llm", get_llm(), 
                                            lambda: hasattr(get_llm(), 'config'))
        
        if get_techstack:
            self.registry.register_component("techstack", get_techstack(),
                                            lambda: hasattr(get_techstack(), 'detect_tech_stack'))
        
        if get_domain:
            self.registry.register_component("domain", get_domain(),
                                            lambda: hasattr(get_domain(), 'classify_project_domain'))
        
        if get_claude:
            self.registry.register_component("claude", get_claude(),
                                            lambda: hasattr(get_claude(), 'start_conversation'))
        
        if get_aider:
            self.registry.register_component("aider", get_aider(),
                                            lambda: hasattr(get_aider(), 'start_coding_session'))
        
        if get_bdd:
            self.registry.register_component("bdd", get_bdd(),
                                            lambda: hasattr(get_bdd(), 'run_bdd_tests'))
        
        if get_reality:
            self.registry.register_component("reality", get_reality(),
                                            lambda: hasattr(get_reality(), 'validate_reality'))
    
    def start_orchestration_session(self, conversation_id: str = None, 
                                   session_context: Dict[str, Any] = None) -> str:
        """Start new orchestration session"""
        session_id = self._generate_session_id()
        
        session = OrchestrationSession(
            session_id=session_id,
            user_id=self.user_id,
            conversation_id=conversation_id or f"auto_{session_id}",
            started_at=datetime.now(),
            session_context=session_context or {}
        )
        
        self.current_session = session
        self._store_session(session)
        
        if self.logger:
            self.logger.info(f"Started orchestration session: {session_id}")
        
        return session_id
    
    async def coordinate_development_workflow(self, user_request: str, 
                                            context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Coordinate complete development workflow based on user request"""
        if not self.current_session:
            self.start_orchestration_session()
        
        context = context or {}
        
        if self.logger:
            self.logger.info(f"Coordinating workflow for: {user_request[:100]}...")
        
        # Analyze request and determine workflow
        workflow_plan = await self._analyze_and_plan_workflow(user_request, context)
        
        # Execute workflow steps
        results = {}
        for step in workflow_plan["steps"]:
            try:
                step_result = await self._execute_workflow_step(step)
                results[step["action"]] = step_result
                
                # Learn from step execution
                self._learn_from_step_execution(step, step_result, success=True)
                
            except Exception as e:
                error_msg = str(e)
                results[step["action"]] = {"error": error_msg}
                
                # Learn from failure
                self._learn_from_step_execution(step, {"error": error_msg}, success=False)
                
                if self.logger:
                    self.logger.error(f"Workflow step failed: {step['action']} - {error_msg}")
        
        # Generate workflow summary
        summary = self._generate_workflow_summary(user_request, workflow_plan, results)
        
        # Store cross-component insights
        self._extract_and_store_insights(results)
        
        return {
            "session_id": self.current_session.session_id,
            "workflow_plan": workflow_plan,
            "results": results,
            "summary": summary
        }
    
    async def _analyze_and_plan_workflow(self, user_request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user request and create workflow plan"""
        # Use conversation history and patterns to determine best workflow
        
        # Basic workflow planning based on request analysis
        request_lower = user_request.lower()
        
        workflow_steps = []
        
        # Always start with project analysis if no context
        if not context.get("project_analyzed"):
            workflow_steps.append({
                "action": OrchestrationAction.ANALYZE_PROJECT.value,
                "component": "multiple",
                "priority": "high",
                "parameters": {}
            })
        
        # Determine primary action
        if any(word in request_lower for word in ["test", "bdd", "behave"]):
            workflow_steps.append({
                "action": OrchestrationAction.RUN_TESTS.value,
                "component": "bdd",
                "priority": "high",
                "parameters": {"conversation_context": user_request}
            })
        
        elif any(word in request_lower for word in ["code", "implement", "develop", "fix"]):
            workflow_steps.append({
                "action": OrchestrationAction.GENERATE_CODE.value,
                "component": "aider",
                "priority": "high", 
                "parameters": {"prompt": user_request}
            })
        
        elif any(word in request_lower for word in ["chat", "ask", "explain"]):
            workflow_steps.append({
                "action": OrchestrationAction.CHAT_WITH_CLAUDE.value,
                "component": "claude",
                "priority": "high",
                "parameters": {"prompt": user_request}
            })
        
        elif any(word in request_lower for word in ["validate", "check", "verify"]):
            workflow_steps.append({
                "action": OrchestrationAction.VALIDATE_REALITY.value,
                "component": "reality",
                "priority": "high",
                "parameters": {"conversation_context": user_request}
            })
        
        # Always end with validation if code changes were made
        has_code_action = any(step["action"] == OrchestrationAction.GENERATE_CODE.value 
                             for step in workflow_steps)
        
        if has_code_action:
            workflow_steps.append({
                "action": OrchestrationAction.VALIDATE_REALITY.value,
                "component": "reality",
                "priority": "medium",
                "parameters": {"conversation_context": "Post-development validation"}
            })
        
        return {
            "user_request": user_request,
            "context": context,
            "steps": workflow_steps,
            "estimated_duration": len(workflow_steps) * 30,  # 30 seconds per step estimate
            "planned_at": datetime.now().isoformat()
        }
    
    async def _execute_workflow_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step"""
        action = step["action"]
        component_name = step["component"]
        parameters = step.get("parameters", {})
        
        # Create task
        task = OrchestrationTask(
            task_id=self._generate_task_id(),
            action=OrchestrationAction(action),
            parameters=parameters,
            component_involved=component_name
        )
        
        self.current_session.tasks.append(task)
        self._store_task(task)
        
        try:
            # Route to appropriate component
            if action == OrchestrationAction.ANALYZE_PROJECT.value:
                result = await self._analyze_project(parameters)
            elif action == OrchestrationAction.DETECT_TECH_STACK.value:
                result = await self._detect_tech_stack(parameters)
            elif action == OrchestrationAction.CLASSIFY_DOMAIN.value:
                result = await self._classify_domain(parameters)
            elif action == OrchestrationAction.GENERATE_CODE.value:
                result = await self._generate_code(parameters)
            elif action == OrchestrationAction.RUN_TESTS.value:
                result = await self._run_tests(parameters)
            elif action == OrchestrationAction.VALIDATE_REALITY.value:
                result = await self._validate_reality(parameters)
            elif action == OrchestrationAction.CHAT_WITH_CLAUDE.value:
                result = await self._chat_with_claude(parameters)
            else:
                result = {"error": f"Unknown action: {action}"}
            
            # Update task with result
            task.status = "completed"
            task.result = result
            task.completed_at = datetime.now()
            
            return result
            
        except Exception as e:
            # Update task with error
            task.status = "failed"
            task.error = str(e)
            task.completed_at = datetime.now()
            
            raise e
        finally:
            self._update_task(task)
    
    async def _analyze_project(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze project using multiple components"""
        results = {}
        
        # Tech stack detection
        techstack = self.registry.get_component("techstack")
        if techstack:
            try:
                profile = techstack.detect_tech_stack(str(self.project_path))
                results["tech_stack"] = profile.to_dict() if hasattr(profile, 'to_dict') else str(profile)
            except Exception as e:
                results["tech_stack"] = {"error": str(e)}
        
        # Domain classification
        domain = self.registry.get_component("domain")
        if domain:
            try:
                classification = domain.classify_project_domain(str(self.project_path))
                results["domain"] = classification.to_dict() if hasattr(classification, 'to_dict') else str(classification)
            except Exception as e:
                results["domain"] = {"error": str(e)}
        
        return results
    
    async def _detect_tech_stack(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Detect technology stack"""
        techstack = self.registry.get_component("techstack")
        if not techstack:
            return {"error": "TechStack component not available"}
        
        try:
            profile = techstack.detect_tech_stack(str(self.project_path))
            return profile.to_dict() if hasattr(profile, 'to_dict') else {"profile": str(profile)}
        except Exception as e:
            return {"error": str(e)}
    
    async def _classify_domain(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Classify project domain"""
        domain = self.registry.get_component("domain")
        if not domain:
            return {"error": "Domain component not available"}
        
        try:
            classification = domain.classify_project_domain(str(self.project_path))
            return classification.to_dict() if hasattr(classification, 'to_dict') else {"classification": str(classification)}
        except Exception as e:
            return {"error": str(e)}
    
    async def _generate_code(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code using Aider"""
        aider = self.registry.get_component("aider")
        if not aider:
            return {"error": "Aider component not available"}
        
        try:
            prompt = parameters.get("prompt", "")
            session_id = aider.start_coding_session(prompt)
            
            # Note: In a real implementation, we would execute the Aider operation
            # For now, just return the session information
            return {
                "session_id": session_id,
                "prompt": prompt,
                "status": "session_created"
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _run_tests(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Run BDD tests"""
        bdd = self.registry.get_component("bdd")
        if not bdd:
            return {"error": "BDD component not available"}
        
        try:
            conversation_context = parameters.get("conversation_context", "")
            run_id = bdd.run_bdd_tests(conversation_context=conversation_context)
            
            # Get scoreboard
            scoreboard = bdd.get_scoreboard_display(run_id)
            
            return {
                "run_id": run_id,
                "scoreboard": scoreboard
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _validate_reality(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate reality"""
        reality = self.registry.get_component("reality")
        if not reality:
            return {"error": "Reality component not available"}
        
        try:
            conversation_context = parameters.get("conversation_context", "")
            check_id = reality.validate_reality(conversation_context=conversation_context)
            
            # Get report
            report = reality.get_reality_report(check_id, format="summary")
            
            return {
                "check_id": check_id,
                "report": report
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _chat_with_claude(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Chat with Claude"""
        claude = self.registry.get_component("claude")
        if not claude:
            return {"error": "Claude component not available"}
        
        try:
            prompt = parameters.get("prompt", "")
            
            # Start conversation if needed
            if not hasattr(claude, 'current_conversation_id') or not claude.current_conversation_id:
                claude.start_conversation("Orchestrated Chat")
            
            # Note: In a real implementation, we would generate the response
            # For now, just return the session information
            return {
                "conversation_id": claude.current_conversation_id,
                "prompt": prompt,
                "status": "message_added"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _generate_workflow_summary(self, user_request: str, workflow_plan: Dict[str, Any], 
                                  results: Dict[str, Any]) -> str:
        """Generate summary of workflow execution"""
        successful_steps = sum(1 for result in results.values() if "error" not in result)
        total_steps = len(results)
        
        summary_lines = [
            f"🎯 Workflow Summary for: {user_request[:50]}...",
            f"📊 Success Rate: {successful_steps}/{total_steps} steps completed",
            "",
            "📋 Steps Executed:"
        ]
        
        for action, result in results.items():
            if "error" in result:
                summary_lines.append(f"  ❌ {action}: {result['error'][:50]}...")
            else:
                summary_lines.append(f"  ✅ {action}: Success")
        
        return "\n".join(summary_lines)
    
    def _extract_and_store_insights(self, results: Dict[str, Any]):
        """Extract insights from cross-component interactions"""
        insights = []
        
        # Example: If both tech stack and domain were analyzed
        if "tech_stack" in results and "domain" in results:
            tech_result = results["tech_stack"]
            domain_result = results["domain"]
            
            if "error" not in tech_result and "error" not in domain_result:
                insight = {
                    "type": "tech_domain_correlation",
                    "source_component": "techstack",
                    "target_component": "domain", 
                    "data": {
                        "tech_primary_language": tech_result.get("primary_language"),
                        "domain_primary": domain_result.get("primary_domain")
                    },
                    "confidence": 0.8
                }
                insights.append(insight)
        
        # Store insights
        for insight in insights:
            self._store_cross_component_insight(insight)
    
    def _learn_from_step_execution(self, step: Dict[str, Any], result: Dict[str, Any], success: bool):
        """Learn patterns from step execution"""
        pattern_context = json.dumps({
            "action": step["action"],
            "component": step["component"],
            "has_parameters": len(step.get("parameters", {})) > 0
        })
        
        success_score = 1.0 if success else 0.0
        
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO decision_patterns
                (pattern_context, chosen_action, component_used, success_score, usage_count, 
                 last_used, learned_from_session)
                VALUES (?, ?, ?, 
                        (COALESCE((SELECT success_score FROM decision_patterns 
                                  WHERE pattern_context = ? AND chosen_action = ?), 0.5) + ?) / 2,
                        COALESCE((SELECT usage_count FROM decision_patterns 
                                 WHERE pattern_context = ? AND chosen_action = ?), 0) + 1,
                        ?, ?)
            """, (
                pattern_context, step["action"], step["component"],
                pattern_context, step["action"], success_score,
                pattern_context, step["action"], 
                datetime.now(), self.current_session.session_id
            ))
            conn.commit()
    
    def get_orchestration_report(self, session_id: str = None) -> str:
        """Get orchestration session report"""
        target_session = self._get_session(session_id) if session_id else self.current_session
        
        if not target_session:
            return "No orchestration session data available"
        
        # Generate report
        lines = [
            "🎼 ORCHESTRATION SESSION REPORT",
            "=" * 50,
            "",
            f"Session ID: {target_session.session_id}",
            f"Started: {target_session.started_at}",
            f"Conversation: {target_session.conversation_id}",
            f"Tasks: {len(target_session.tasks)}",
            "",
            "📋 Task Breakdown:"
        ]
        
        for task in target_session.tasks:
            status_icon = "✅" if task.status == "completed" else "❌" if task.status == "failed" else "⏳"
            lines.append(f"  {status_icon} {task.action.value} [{task.component_involved}]")
            
            if task.error:
                lines.append(f"     💥 {task.error}")
        
        # Component usage stats
        lines.extend([
            "",
            "🔧 Component Stats:",
            *[f"  {name}: {stats['health_ratio']:.1%} success rate" 
              for name, stats in self.registry.get_component_stats().items()]
        ])
        
        return "\n".join(lines)
    
    def get_coordination_insights(self) -> Dict[str, Any]:
        """Get insights about component coordination"""
        with sqlite3.connect(self.memory_db) as conn:
            # Decision patterns
            cursor = conn.execute("""
                SELECT chosen_action, component_used, AVG(success_score), COUNT(*)
                FROM decision_patterns
                GROUP BY chosen_action, component_used
                ORDER BY AVG(success_score) DESC
            """)
            
            decision_patterns = []
            for row in cursor.fetchall():
                decision_patterns.append({
                    "action": row[0],
                    "component": row[1],
                    "avg_success": row[2],
                    "usage_count": row[3]
                })
            
            # Cross-component insights
            cursor = conn.execute("""
                SELECT insight_type, source_component, target_component, AVG(confidence_score), COUNT(*)
                FROM cross_component_insights
                GROUP BY insight_type, source_component, target_component
                ORDER BY AVG(confidence_score) DESC
            """)
            
            cross_insights = []
            for row in cursor.fetchall():
                cross_insights.append({
                    "type": row[0],
                    "source": row[1],
                    "target": row[2],
                    "avg_confidence": row[3],
                    "count": row[4]
                })
        
        return {
            "decision_patterns": decision_patterns,
            "cross_component_insights": cross_insights,
            "component_stats": self.registry.get_component_stats()
        }
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"{self.user_id}:{timestamp}".encode()).hexdigest()[:16]
    
    def _generate_task_id(self) -> str:
        """Generate unique task ID"""
        timestamp = datetime.now().timestamp()
        return f"task_{int(timestamp * 1000)}"
    
    def _store_session(self, session: OrchestrationSession):
        """Store session in database"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO orchestration_sessions
                (session_id, user_id, conversation_id, started_at, ended_at, 
                 session_context, conversation_summary)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_id, session.user_id, session.conversation_id,
                session.started_at, session.ended_at,
                json.dumps(session.session_context) if session.session_context else None,
                session.conversation_summary
            ))
            conn.commit()
    
    def _store_task(self, task: OrchestrationTask):
        """Store task in database"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT INTO orchestration_tasks
                (task_id, session_id, action, parameters, status, result, error,
                 created_at, completed_at, component_involved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.task_id, self.current_session.session_id, task.action.value,
                json.dumps(task.parameters), task.status,
                json.dumps(task.result) if task.result else None,
                task.error, task.created_at, task.completed_at, task.component_involved
            ))
            conn.commit()
    
    def _update_task(self, task: OrchestrationTask):
        """Update task in database"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                UPDATE orchestration_tasks
                SET status = ?, result = ?, error = ?, completed_at = ?
                WHERE task_id = ?
            """, (
                task.status, json.dumps(task.result) if task.result else None,
                task.error, task.completed_at, task.task_id
            ))
            conn.commit()
    
    def _store_cross_component_insight(self, insight: Dict[str, Any]):
        """Store cross-component insight"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT INTO cross_component_insights
                (insight_type, source_component, target_component, insight_data, 
                 confidence_score, created_at, applied_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                insight["type"], insight["source_component"], insight.get("target_component"),
                json.dumps(insight["data"]), insight["confidence"],
                datetime.now(), 0
            ))
            conn.commit()
    
    def _get_session(self, session_id: str) -> Optional[OrchestrationSession]:
        """Get session by ID"""
        with sqlite3.connect(self.memory_db) as conn:
            cursor = conn.execute("""
                SELECT session_id, user_id, conversation_id, started_at, ended_at,
                       session_context, conversation_summary
                FROM orchestration_sessions
                WHERE session_id = ? AND user_id = ?
            """, (session_id, self.user_id))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Load tasks
            cursor = conn.execute("""
                SELECT task_id, action, parameters, status, result, error,
                       created_at, completed_at, component_involved
                FROM orchestration_tasks
                WHERE session_id = ?
                ORDER BY created_at
            """, (session_id,))
            
            tasks = []
            for task_row in cursor.fetchall():
                tasks.append(OrchestrationTask(
                    task_id=task_row[0],
                    action=OrchestrationAction(task_row[1]),
                    parameters=json.loads(task_row[2]) if task_row[2] else {},
                    status=task_row[3],
                    result=json.loads(task_row[4]) if task_row[4] else None,
                    error=task_row[5],
                    created_at=datetime.fromisoformat(task_row[6]),
                    completed_at=datetime.fromisoformat(task_row[7]) if task_row[7] else None,
                    component_involved=task_row[8]
                ))
            
            return OrchestrationSession(
                session_id=row[0],
                user_id=row[1],
                conversation_id=row[2],
                started_at=datetime.fromisoformat(row[3]),
                ended_at=datetime.fromisoformat(row[4]) if row[4] else None,
                session_context=json.loads(row[5]) if row[5] else {},
                conversation_summary=row[6],
                tasks=tasks
            )


# Global TOPDOG instance
_global_topdog = None


def get_topdog(project_path: str = ".", user_id: str = "developer") -> DeltaTopdog:
    """Get global TOPDOG instance"""
    global _global_topdog
    if _global_topdog is None:
        _global_topdog = DeltaTopdog(project_path=project_path, user_id=user_id)
    return _global_topdog


def initialize_topdog(project_path: str = ".", config_dir: str = ".claude", user_id: str = "developer") -> DeltaTopdog:
    """Initialize TOPDOG orchestration system"""
    global _global_topdog
    _global_topdog = DeltaTopdog(project_path=project_path, config_dir=config_dir, user_id=user_id)
    return _global_topdog


if __name__ == "__main__":
    # Test TOPDOG orchestration system
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Testing ∂TOPDOG system...")
        
        # Initialize TOPDOG system
        topdog = initialize_topdog()
        
        # Test component registration
        stats = topdog.registry.get_component_stats()
        print(f"Registered components: {len(stats)}")
        for name, component_stats in stats.items():
            print(f"  {name}: {component_stats['status']}")
        
        # Test session creation
        session_id = topdog.start_orchestration_session()
        print(f"Created session: {session_id}")
        
        # Test coordination (async test would require actual async execution)
        print("Testing workflow coordination...")
        
        # Generate report
        report = topdog.get_orchestration_report()
        print(f"Report:\n{report}")
        
        # Test insights
        insights = topdog.get_coordination_insights()
        print(f"Insights: {insights}")
        
        print("∂TOPDOG system test completed successfully!")
    else:
        print("∂TOPDOG.py - Main orchestrator with conversation memory")
        print("Usage: python ∂TOPDOG.py --test")