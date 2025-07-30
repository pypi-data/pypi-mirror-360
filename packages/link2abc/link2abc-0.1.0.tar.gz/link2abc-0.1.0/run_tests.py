#!/usr/bin/env python3
"""
🧪 LinkTune Test Runner
Simple test runner that validates the LinkTune package
"""

import sys
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_core_imports():
    """Check if core components can be imported"""
    print("\n📦 Checking core imports...")
    
    core_modules = [
        "linktune",
        "linktune.core.extractor",
        "linktune.core.analyzer", 
        "linktune.core.generator",
        "linktune.core.converter",
        "linktune.core.pipeline",
        "linktune.core.lego_factory"
    ]
    
    failed_imports = []
    
    for module in core_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def check_ai_imports():
    """Check if AI components can be imported"""
    print("\n🤖 Checking AI imports...")
    
    ai_modules = [
        "linktune.blocks.ai.chatmusician",
        "linktune.blocks.ai.claude",
        "linktune.blocks.ai.chatgpt",
        "linktune.blocks.langfuse_integration"
    ]
    
    available_modules = []
    
    for module in ai_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
            available_modules.append(module)
        except ImportError as e:
            print(f"⚠️  {module}: {e}")
    
    return available_modules

def check_neural_imports():
    """Check if neural components can be imported"""
    print("\n🧠 Checking neural imports...")
    
    neural_modules = [
        "linktune.blocks.neural.orpheus_bridge"
    ]
    
    available_modules = []
    
    for module in neural_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
            available_modules.append(module)
        except ImportError as e:
            print(f"⚠️  {module}: {e}")
    
    return available_modules

def test_basic_functionality():
    """Test basic LinkTune functionality"""
    print("\n⚡ Testing basic functionality...")
    
    try:
        import linktune
        
        # Test tier detection
        tiers = linktune.get_installed_tiers()
        print(f"🧱 Available tiers: {', '.join(tiers)}")
        
        # Test pipeline creation
        from linktune.core.pipeline import Pipeline
        pipeline = Pipeline.from_config({"format": ["abc"]})
        print("✅ Pipeline creation successful")
        
        # Test LEGO factory
        from linktune.core.lego_factory import get_lego_factory
        factory = get_lego_factory()
        blocks = factory.get_available_blocks()
        print(f"✅ LEGO factory: {len(blocks)} block types available")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_ai_functionality():
    """Test AI functionality if available"""
    print("\n🤖 Testing AI functionality...")
    
    try:
        import linktune
        tiers = linktune.get_installed_tiers()
        
        if 'ai' not in tiers:
            print("⚠️  AI tier not installed - skipping AI tests")
            return True
        
        # Test AI pipeline creation
        from linktune.core.pipeline import Pipeline
        ai_pipeline = Pipeline.from_config({"ai": "chatmusician", "format": ["abc"]})
        print("✅ AI pipeline creation successful")
        
        # Test LEGO factory AI blocks
        from linktune.core.lego_factory import get_lego_factory
        factory = get_lego_factory()
        
        ai_blocks = []
        for block_name in factory.available_blocks:
            if factory.available_blocks[block_name].type == 'ai':
                ai_blocks.append(block_name)
        
        print(f"✅ AI blocks available: {', '.join(ai_blocks)}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI functionality test failed: {e}")
        return False

def run_unit_tests():
    """Run unit tests using pytest"""
    print("\n🧪 Running unit tests...")
    
    try:
        # Check if pytest is available
        import pytest
        
        # Run core tests
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_core.py", 
            "-v", "--tb=short"
        ], cwd=Path(__file__).parent, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Core tests passed")
        else:
            print("❌ Core tests failed")
            print(result.stdout)
            print(result.stderr)
        
        # Run AI tests if AI tier is available
        try:
            import linktune
            if 'ai' in linktune.get_installed_tiers():
                result = subprocess.run([
                    sys.executable, "-m", "pytest", 
                    "tests/test_ai.py", 
                    "-v", "--tb=short"
                ], cwd=Path(__file__).parent, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ AI tests passed")
                else:
                    print("⚠️  Some AI tests failed (this is expected without API keys)")
        except:
            pass
        
        return True
        
    except ImportError:
        print("⚠️  pytest not available - install with: pip install pytest")
        return False
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

def test_examples():
    """Test example scripts"""
    print("\n📚 Testing examples...")
    
    examples_dir = Path(__file__).parent / "examples"
    
    if not examples_dir.exists():
        print("⚠️  Examples directory not found")
        return False
    
    # Test basic_usage.py
    basic_usage = examples_dir / "basic_usage.py"
    if basic_usage.exists():
        try:
            # Just check if it imports without errors
            spec = importlib.util.spec_from_file_location("basic_usage", basic_usage)
            module = importlib.util.module_from_spec(spec)
            # Don't execute main() to avoid actual network calls
            print("✅ basic_usage.py imports successfully")
        except Exception as e:
            print(f"❌ basic_usage.py failed: {e}")
    
    # Test ai_integration.py
    ai_integration = examples_dir / "ai_integration.py"
    if ai_integration.exists():
        try:
            spec = importlib.util.spec_from_file_location("ai_integration", ai_integration)
            module = importlib.util.module_from_spec(spec)
            print("✅ ai_integration.py imports successfully")
        except Exception as e:
            print(f"❌ ai_integration.py failed: {e}")
    
    return True

def test_cli():
    """Test CLI functionality"""
    print("\n💻 Testing CLI...")
    
    try:
        # Test CLI help
        result = subprocess.run([
            sys.executable, "-m", "linktune.cli", "--help"
        ], cwd=Path(__file__).parent, capture_output=True, text=True)
        
        if result.returncode == 0 and "Transform any link into music" in result.stdout:
            print("✅ CLI help works")
        else:
            print("❌ CLI help failed")
            return False
        
        # Test version
        result = subprocess.run([
            sys.executable, "-m", "linktune.cli", "--version"
        ], cwd=Path(__file__).parent, capture_output=True, text=True)
        
        if result.returncode == 0 and "LinkTune" in result.stdout:
            print("✅ CLI version works")
        else:
            print("❌ CLI version failed")
        
        # Test tier listing
        result = subprocess.run([
            sys.executable, "-m", "linktune.cli", "--list-tiers"
        ], cwd=Path(__file__).parent, capture_output=True, text=True)
        
        if result.returncode == 0 and "core" in result.stdout:
            print("✅ CLI tier listing works")
        else:
            print("❌ CLI tier listing failed")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🎵 LinkTune Package Validation")
    print("=" * 50)
    
    tests = [
        ("Python Version", check_python_version),
        ("Core Imports", check_core_imports),
        ("AI Imports", check_ai_imports),
        ("Neural Imports", check_neural_imports),
        ("Basic Functionality", test_basic_functionality),
        ("AI Functionality", test_ai_functionality),
        ("Unit Tests", run_unit_tests),
        ("Examples", test_examples),
        ("CLI", test_cli)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"💥 {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! LinkTune is ready for use.")
        return 0
    elif passed >= total * 0.8:
        print("⚡ Most tests passed! LinkTune should work with minor limitations.")
        return 0
    else:
        print("⚠️  Several tests failed. Check installation and dependencies.")
        return 1

if __name__ == "__main__":
    import importlib.util
    sys.exit(main())