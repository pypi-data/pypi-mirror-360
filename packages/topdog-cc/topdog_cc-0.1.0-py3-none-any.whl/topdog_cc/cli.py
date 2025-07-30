#!/usr/bin/env python3
"""
TopDog-CC CLI: Main command-line interface for the conversation-aware multi-agent framework

This is the entry point that kicks off the entire orchestration process.
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Import our components
from .orchestrator import get_topdog
from .config import get_config
from .logger import get_logger
from .tech_stack import get_techstack
from . import __version__


def create_parser():
    """Create the command-line argument parser"""
    parser = argparse.ArgumentParser(
        prog="topdogcc",
        description="TopDog-CC: Conversation-aware multi-agent development framework",
        epilog="For more information, visit: https://github.com/topdog-cc/topdog-cc"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"topdogcc {__version__}"
    )
    
    parser.add_argument(
        "--project-path",
        "-p",
        default=".",
        help="Path to the project directory (default: current directory)"
    )
    
    parser.add_argument(
        "--user-id",
        "-u", 
        default="developer",
        help="User ID for memory and learning systems (default: 'developer')"
    )
    
    parser.add_argument(
        "--config-dir",
        "-c",
        default=".claude",
        help="Configuration directory for memory storage (default: '.claude')"
    )
    
    parser.add_argument(
        "--workflow",
        "-w",
        help="Specific workflow to execute (if not provided, runs full analysis)"
    )
    
    parser.add_argument(
        "--context",
        help="Additional context for the conversation-aware system"
    )
    
    parser.add_argument(
        "--quick",
        "-q",
        action="store_true",
        help="Run quick analysis only (skip complex operations)"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true", 
        help="Enable verbose logging output"
    )
    
    parser.add_argument(
        "--components",
        nargs="+",
        choices=["config", "logger", "llm", "techstack", "domain", "claude", 
                "aider", "bdd", "reality", "radon", "feedback", "all"],
        default=["all"],
        help="Specific components to run (default: all)"
    )
    
    return parser


async def run_full_orchestration(args):
    """Run the complete TopDog-CC orchestration"""
    logger = get_logger("topdogcc")
    
    if args.verbose:
        logger.info(f"Starting TopDog-CC v{__version__}")
        logger.info(f"Project path: {Path(args.project_path).resolve()}")
        logger.info(f"User ID: {args.user_id}")
        logger.info(f"Components: {', '.join(args.components)}")
    
    try:
        # Initialize the orchestrator
        topdog = get_topdog(
            project_path=args.project_path,
            user_id=args.user_id
        )
        
        # Prepare workflow context
        workflow_context = {
            "user_id": args.user_id,
            "project_path": args.project_path,
            "quick_mode": args.quick,
            "components": args.components,
            "cli_invocation": True
        }
        
        if args.context:
            workflow_context["additional_context"] = args.context
        
        # Determine workflow
        if args.workflow:
            workflow_description = args.workflow
        elif args.quick:
            workflow_description = "Quick project analysis and insights"
        else:
            workflow_description = "Complete conversation-aware multi-agent development analysis"
        
        # Execute the workflow
        logger.info("🚀 Initiating TopDog-CC orchestration...")
        
        result = await topdog.coordinate_development_workflow(
            workflow_description,
            context=workflow_context
        )
        
        # Display results
        print("\n" + "="*60)
        print("🎯 TOPDOG-CC ANALYSIS COMPLETE")
        print("="*60)
        
        if result.get("status") == "completed":
            print("✅ Orchestration completed successfully")
            
            # Show key insights
            if "insights" in result:
                print(f"\n📊 Key Insights:")
                for insight in result["insights"][:5]:  # Top 5 insights
                    print(f"   • {insight}")
            
            # Show component results
            if "component_results" in result:
                print(f"\n🔧 Component Results:")
                for component, comp_result in result["component_results"].items():
                    status = "✅" if comp_result.get("success") else "❌"
                    print(f"   {status} {component}: {comp_result.get('summary', 'Completed')}")
            
            # Show recommendations
            if "recommendations" in result:
                print(f"\n💡 Recommendations:")
                for rec in result["recommendations"][:3]:  # Top 3 recommendations
                    print(f"   • {rec}")
                    
        else:
            print(f"⚠️  Orchestration completed with status: {result.get('status', 'unknown')}")
            if "error" in result:
                print(f"   Error: {result['error']}")
        
        print(f"\n📝 Full results logged to: {args.config_dir}/")
        print("="*60)
        
        return 0
        
    except Exception as e:
        logger.error(f"TopDog-CC orchestration failed: {e}")
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def run_quick_analysis(args):
    """Run a quick project analysis without full orchestration"""
    logger = get_logger("topdogcc")
    
    try:
        print("🔍 Running quick TopDog-CC analysis...")
        
        # Quick tech stack detection
        if "techstack" in args.components or "all" in args.components:
            print("\n📊 Technology Stack Analysis:")
            techstack = get_techstack()
            profile = techstack.detect_tech_stack(
                args.project_path,
                conversation_context="CLI quick analysis"
            )
            
            print(f"   Primary Language: {profile.primary_language}")
            print(f"   Frameworks: {len(profile.frameworks)} detected")
            for fw in profile.frameworks[:5]:  # Top 5
                print(f"      • {fw.name} (confidence: {fw.confidence:.2f})")
        
        # Quick configuration check
        if "config" in args.components or "all" in args.components:
            print("\n⚙️  Configuration Status:")
            config = get_config(args.user_id)
            print(f"   Config directory: {Path(args.config_dir).resolve()}")
            print(f"   User profile: {args.user_id}")
        
        print(f"\n✅ Quick analysis complete!")
        print(f"   For full analysis, run: topdogcc (without --quick)")
        
        return 0
        
    except Exception as e:
        logger.error(f"Quick analysis failed: {e}")
        print(f"\n❌ Error: {e}")
        return 1


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Validate project path
    project_path = Path(args.project_path)
    if not project_path.exists():
        print(f"❌ Error: Project path does not exist: {project_path}")
        return 1
    
    # Create config directory if needed
    config_dir = Path(args.config_dir)
    config_dir.mkdir(exist_ok=True)
    
    try:
        if args.quick:
            # Run synchronous quick analysis
            return run_quick_analysis(args)
        else:
            # Run full async orchestration
            return asyncio.run(run_full_orchestration(args))
            
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())