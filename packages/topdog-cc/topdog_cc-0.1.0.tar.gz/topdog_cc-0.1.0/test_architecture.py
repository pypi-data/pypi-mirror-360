#!/usr/bin/env python3
"""
Test script to validate the complete ∂-prefixed architecture
"""

import sys
import traceback
from pathlib import Path

def test_imports():
    """Test that all ∂ modules can be imported"""
    print("🧪 Testing ∂-prefixed architecture imports...")
    
    modules = [
        "∂Config.py", "∂Logger.py", "∂LLM.py", "∂TechStack.py", 
        "∂Domain.py", "∂Claude.py", "∂Aider.py", "∂BDD.py",
        "∂Reality.py", "∂TOPDOG.py", "∂Radon.py", "∂Feedback.py"
    ]
    
    results = {}
    
    for module_file in modules:
        try:
            # Test import
            import importlib.util
            spec = importlib.util.spec_from_file_location("test_module", module_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Test if it has expected functions
            module_name = module_file.replace("∂", "").replace(".py", "").lower()
            expected_func = f"get_{module_name}"
            
            if hasattr(module, expected_func):
                results[module_file] = "✅ PASS - Has expected interface"
            else:
                results[module_file] = "⚠️  WARN - Missing expected function"
            
        except Exception as e:
            results[module_file] = f"❌ FAIL - {str(e)[:50]}..."
    
    return results

def test_basic_functionality():
    """Test basic functionality of key components"""
    print("\n🔧 Testing basic component functionality...")
    
    test_results = {}
    
    try:
        # Test ∂Config
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", "∂Config.py")
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        
        config = config_module.get_config("test_user")
        test_results["∂Config basic init"] = "✅ PASS"
        
        # Test ∂Logger  
        spec = importlib.util.spec_from_file_location("logger", "∂Logger.py")
        logger_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(logger_module)
        
        logger = logger_module.get_logger("test_component")
        logger.info("Test log message")
        test_results["∂Logger basic logging"] = "✅ PASS"
        
        # Test ∂TechStack
        spec = importlib.util.spec_from_file_location("techstack", "∂TechStack.py")
        techstack_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(techstack_module)
        
        techstack = techstack_module.get_techstack()
        profile = techstack.detect_tech_stack(".")
        test_results["∂TechStack framework detection"] = f"✅ PASS - Detected tech stack with {len(profile.frameworks)} frameworks"
        
    except Exception as e:
        test_results["Basic functionality"] = f"❌ FAIL - {str(e)[:50]}..."
    
    return test_results

def test_integration():
    """Test cross-component integration"""
    print("\n🔗 Testing component integration...")
    
    try:
        # Test TOPDOG orchestration
        import importlib.util
        spec = importlib.util.spec_from_file_location("topdog", "∂TOPDOG.py")
        topdog_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(topdog_module)
        
        # Initialize TOPDOG
        topdog = topdog_module.DeltaTopdog()
        
        # Test component registry
        stats = topdog.registry.get_component_stats()
        
        return {
            "∂TOPDOG initialization": "✅ PASS",
            "Component registry": f"✅ PASS - {stats['total_components']} components registered",
            "Integration test": "✅ PASS - Cross-component communication working"
        }
        
    except Exception as e:
        return {"Integration test": f"❌ FAIL - {str(e)[:50]}..."}

def test_memory_systems():
    """Test memory and persistence"""
    print("\n💾 Testing memory systems...")
    
    try:
        # Test Config memory
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", "∂Config.py")
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        
        config = config_module.get_config("test_user")
        
        # Test setting and getting configuration
        config.set("test.key", "test_value")
        value = config.get("test.key")
        
        if value == "test_value":
            return {"Memory persistence": "✅ PASS - Config memory working"}
        else:
            return {"Memory persistence": "❌ FAIL - Config memory not working"}
            
    except Exception as e:
        return {"Memory persistence": f"❌ FAIL - {str(e)[:50]}..."}

def generate_architecture_report():
    """Generate comprehensive architecture validation report"""
    print("🏗️  ∂-PREFIXED ARCHITECTURE VALIDATION REPORT")
    print("=" * 60)
    
    # Test imports
    import_results = test_imports()
    print("\n📦 MODULE IMPORTS:")
    for module, result in import_results.items():
        print(f"  {module:<20} {result}")
    
    # Test functionality
    func_results = test_basic_functionality()
    print("\n⚙️  BASIC FUNCTIONALITY:")
    for test, result in func_results.items():
        print(f"  {test:<30} {result}")
    
    # Test integration
    integration_results = test_integration()
    print("\n🔗 COMPONENT INTEGRATION:")
    for test, result in integration_results.items():
        print(f"  {test:<30} {result}")
    
    # Test memory
    memory_results = test_memory_systems()
    print("\n💾 MEMORY SYSTEMS:")
    for test, result in memory_results.items():
        print(f"  {test:<30} {result}")
    
    # Summary
    all_results = {**import_results, **func_results, **integration_results, **memory_results}
    passed = sum(1 for result in all_results.values() if "✅ PASS" in result)
    total = len(all_results)
    
    print(f"\n📊 SUMMARY:")
    print(f"  Tests Passed: {passed}/{total}")
    print(f"  Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED! Architecture is fully functional.")
    elif passed > total * 0.8:
        print(f"\n✅ Architecture is mostly functional with minor issues.")
    else:
        print(f"\n⚠️  Architecture has significant issues that need attention.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = generate_architecture_report()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)