#!/usr/bin/env python3
"""
Test script to verify Jupyter Server compatibility for escobar extension.
"""

import sys
import importlib.util

def test_import():
    """Test that escobar can be imported successfully."""
    try:
        import escobar
        print("✅ escobar import successful")
        return True
    except ImportError as e:
        print(f"❌ escobar import failed: {e}")
        return False

def test_extension_app():
    """Test that EscobarExtensionApp is available for Jupyter Server 2.x."""
    try:
        import escobar
        if hasattr(escobar, 'EscobarExtensionApp') and escobar.EscobarExtensionApp is not None:
            print("✅ EscobarExtensionApp available (Jupyter Server 2.x support)")
            return True
        else:
            print("⚠️  EscobarExtensionApp not available (Jupyter Server 2.x classes not found)")
            return False
    except Exception as e:
        print(f"❌ EscobarExtensionApp test failed: {e}")
        return False

def test_legacy_functions():
    """Test that legacy functions are available for Jupyter Server 1.x."""
    try:
        import escobar
        functions = [
            '_jupyter_labextension_paths',
            '_jupyter_server_extension_points', 
            '_load_jupyter_server_extension'
        ]
        
        missing = []
        for func in functions:
            if not hasattr(escobar, func):
                missing.append(func)
        
        if not missing:
            print("✅ All legacy functions available (Jupyter Server 1.x support)")
            return True
        else:
            print(f"❌ Missing legacy functions: {missing}")
            return False
    except Exception as e:
        print(f"❌ Legacy functions test failed: {e}")
        return False

def test_jupyter_server_detection():
    """Test Jupyter Server version detection."""
    try:
        # Try to import Jupyter Server and check version
        spec = importlib.util.find_spec("jupyter_server")
        if spec is None:
            print("⚠️  jupyter-server not installed")
            return False
            
        import jupyter_server
        version = getattr(jupyter_server, '__version__', 'unknown')
        print(f"📋 Jupyter Server version: {version}")
        
        # Test ExtensionApp availability
        try:
            from jupyter_server.extension.application import ExtensionApp
            print("✅ Jupyter Server 2.x ExtensionApp available")
            return True
        except ImportError:
            print("⚠️  Jupyter Server 1.x detected (ExtensionApp not available)")
            return True  # This is still valid for 1.x
            
    except Exception as e:
        print(f"❌ Jupyter Server detection failed: {e}")
        return False

def test_python_version():
    """Test Python version compatibility."""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version >= (3, 8):
        print("✅ Python version supported")
        return True
    else:
        print("❌ Python version too old (requires 3.8+)")
        return False

def main():
    """Run all compatibility tests."""
    print("🧪 Testing Jupyter Server compatibility for escobar extension")
    print("=" * 60)
    
    tests = [
        ("Python Version", test_python_version),
        ("Import Test", test_import),
        ("Jupyter Server Detection", test_jupyter_server_detection),
        ("Extension App (2.x)", test_extension_app),
        ("Legacy Functions (1.x)", test_legacy_functions),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n🔍 {name}:")
        result = test_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All compatibility tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed - check compatibility requirements")
        return 1

if __name__ == "__main__":
    sys.exit(main())
