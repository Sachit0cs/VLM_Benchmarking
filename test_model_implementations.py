#!/usr/bin/env python3
"""
Quick validation script for BLIP-2 and LLaVA implementations.
Tests that models can be imported and instantiated with correct parameters.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_imports():
    """Test that model classes can be imported."""
    print("Testing imports...")
    try:
        from models.blip2 import BLIP2Model
        print("  ✓ BLIP2Model imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import BLIP2Model: {e}")
        return False
    
    try:
        from models.llava import LLaVAModel
        print("  ✓ LLaVAModel imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import LLaVAModel: {e}")
        return False
    
    return True


def test_instantiation():
    """Test that model instances can be created with correct parameters."""
    print("\nTesting instantiation...")
    try:
        from models.blip2 import BLIP2Model
        
        # Test with different precisions
        blip2_fp16 = BLIP2Model(precision='fp16', device='cpu')
        print("  ✓ BLIP2Model(precision='fp16', device='cpu') created")
        
        blip2_fp32 = BLIP2Model(precision='fp32')
        print("  ✓ BLIP2Model(precision='fp32') created")
        
        blip2_int8 = BLIP2Model(precision='int8')
        print("  ✓ BLIP2Model(precision='int8') created")
        
    except Exception as e:
        print(f"  ✗ Failed to instantiate BLIP2Model: {e}")
        return False
    
    try:
        from models.llava import LLaVAModel
        
        # Test with different precisions
        llava_fp16 = LLaVAModel(precision='fp16', device='cpu')
        print("  ✓ LLaVAModel(precision='fp16', device='cpu') created")
        
        llava_fp32 = LLaVAModel(precision='fp32')
        print("  ✓ LLaVAModel(precision='fp32') created")
        
        llava_int8 = LLaVAModel(precision='int8')
        print("  ✓ LLaVAModel(precision='int8') created")
        
    except Exception as e:
        print(f"  ✗ Failed to instantiate LLaVAModel: {e}")
        return False
    
    return True


def test_interface():
    """Test that models have required methods."""
    print("\nTesting interface...")
    try:
        from models.blip2 import BLIP2Model
        from models.llava import LLaVAModel
        
        # Check BLIP-2
        blip2 = BLIP2Model()
        assert hasattr(blip2, 'query'), "BLIP2Model missing query() method"
        assert callable(blip2.query), "BLIP2Model.query is not callable"
        print("  ✓ BLIP2Model has callable query() method")
        
        # Check LLaVA
        llava = LLaVAModel()
        assert hasattr(llava, 'query'), "LLaVAModel missing query() method"
        assert callable(llava.query), "LLaVAModel.query is not callable"
        print("  ✓ LLaVAModel has callable query() method")
        
    except Exception as e:
        print(f"  ✗ Interface check failed: {e}")
        return False
    
    return True


def test_base_class():
    """Test that models inherit from BaseModel correctly."""
    print("\nTesting inheritance...")
    try:
        from models.base import BaseModel
        from models.blip2 import BLIP2Model
        from models.llava import LLaVAModel
        
        # Check BLIP-2
        assert issubclass(BLIP2Model, BaseModel), "BLIP2Model does not inherit from BaseModel"
        print("  ✓ BLIP2Model inherits from BaseModel")
        
        # Check LLaVA
        assert issubclass(LLaVAModel, BaseModel), "LLaVAModel does not inherit from BaseModel"
        print("  ✓ LLaVAModel inherits from BaseModel")
        
    except Exception as e:
        print(f"  ✗ Inheritance check failed: {e}")
        return False
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("VLM-ARB Model Implementation Validation")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_instantiation,
        test_interface,
        test_base_class,
    ]
    
    all_passed = True
    for test_func in tests:
        if not test_func():
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Models are ready for use!")
        print("\nNext steps:")
        print("1. Install transformers: pip install transformers")
        print("2. Test in Colab: Upload and run Notebook 2")
        print("3. Watch metrics stream to Firestore in real-time")
    else:
        print("❌ SOME TESTS FAILED - Please review errors above")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
