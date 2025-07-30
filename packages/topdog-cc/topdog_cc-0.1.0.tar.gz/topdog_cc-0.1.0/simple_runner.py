#!/usr/bin/env python3
"""
Simple Runner - Use the ∂ architecture without complexity
"""
import importlib.util
import asyncio

def load_component(name, file):
    """Load a ∂ component"""
    spec = importlib.util.spec_from_file_location(name, file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def analyze_project():
    """Simple project analysis"""
    print("🔍 Analyzing your project...")
    
    # Tech stack detection
    ts = load_component("techstack", "∂TechStack.py")
    tech = ts.get_techstack()
    result = tech.detect_tech_stack(".")
    
    print(f"\n📊 RESULTS:")
    print(f"Primary Language: {result.primary_language}")
    print(f"Frameworks found: {len(result.frameworks)}")
    for fw in result.frameworks[:5]:
        print(f"  - {fw.name} (confidence: {fw.confidence:.2f})")

def check_complexity():
    """Simple complexity check"""
    print("\n📈 Checking code complexity...")
    
    r = load_component("radon", "∂Radon.py")
    radon = r.get_radon()
    analysis_id = radon.analyze_project_complexity()
    
    print(f"Complexity analysis: {analysis_id}")
    
    # Get simple report
    report = radon.generate_complexity_report(format="text")
    lines = report.split("\n")[:10]  # First 10 lines
    print("\n".join(lines))

async def orchestrate():
    """Use the orchestrator"""
    print("\n🎯 Using orchestrator...")
    
    topdog = load_component("topdog", "∂TOPDOG.py")
    orchestrator = topdog.DeltaTopdog()
    
    result = await orchestrator.coordinate_development_workflow(
        "Analyze this project and provide insights"
    )
    
    print(f"Orchestration result: {result.get('status', 'completed')}")

def main():
    """Main runner"""
    print("🚀 ∂ ARCHITECTURE SIMPLE RUNNER")
    print("=" * 40)
    
    try:
        analyze_project()
        check_complexity()
        print("\n🎉 Analysis complete!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
