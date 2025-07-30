"""
TopDog-CC: Conversation-Aware Multi-Agent Development Framework

A sophisticated framework for building conversation-aware development tools
with memory persistence and multi-agent coordination.
"""

__version__ = "0.1.0"
__author__ = "TopDog Development"
__email__ = "dev@topdog.cc"

# Core imports for easy access
from .config import get_config
from .logger import get_logger  
from .tech_stack import get_techstack
from .orchestrator import get_topdog
from .domain import get_domain
from .claude import get_claude
from .llm import get_llm
from .aider import get_aider
from .bdd import get_bdd
from .reality import get_reality
from .radon import get_radon
from .feedback import get_feedback

# Component imports
from .config import DeltaConfig
from .logger import DeltaLogger
from .tech_stack import DeltaTechStack, TechStackProfile, FrameworkSignature
from .orchestrator import DeltaTopdog
from .domain import DeltaDomain
from .claude import DeltaClaude
from .llm import DeltaLLM
from .aider import DeltaAider
from .bdd import DeltaBDD
from .reality import DeltaReality
from .radon import DeltaRadon
from .feedback import DeltaFeedback

__all__ = [
    # Version info
    "__version__",
    "__author__", 
    "__email__",
    
    # Quick access functions
    "get_config",
    "get_logger",
    "get_techstack", 
    "get_topdog",
    "get_domain",
    "get_claude",
    "get_llm",
    "get_aider",
    "get_bdd", 
    "get_reality",
    "get_radon",
    "get_feedback",
    
    # Core classes
    "DeltaConfig",
    "DeltaLogger",
    "DeltaTechStack",
    "DeltaTopdog",
    "DeltaDomain",
    "DeltaClaude",
    "DeltaLLM",
    "DeltaAider",
    "DeltaBDD",
    "DeltaReality", 
    "DeltaRadon",
    "DeltaFeedback",
    
    # Data classes
    "TechStackProfile",
    "FrameworkSignature",
]