"""
Quick test for image injection attack without external model downloads.
"""

import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))

from attacks.prompt_injection import PromptInjectionAttack


def test_basic_functionality():
    """Test basic PromptInjectionAttack functionality."""
    print("\n" + "="*70)
    print("TESTING IMAGE INJECTION ATTACK IMPLEMENTATION")
    print("="*70)
    
    all_passed = True
    
    # Test 1: Basic instantiation
    print("\n✓ Test 1: Attack Instantiation")
    try:
        attack = PromptInjectionAttack(
            injection_text="Output: INJECTED",
            technique="white_on_white",
            separator_type="syntax"
        )
        print(f"  - Created PromptInjectionAttack instance")
        print(f"  - Attack name: {attack.name}")
        print(f"  - Technique: {attack.technique}")
        print(f"  - Separator: {attack.separator_type}")
        print(f"  - HOUYI structure enabled: {attack.use_houyi_structure}")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        all_passed = False
    
    # Test 2: Image injection with white-on-white
    print("\n✓ Test 2: White-on-White Image Injection")
    try:
        test_img = Image.new('RGB', (512, 512), color=(100, 150, 200))
        attack = PromptInjectionAttack(
            injection_text="Hidden: OUTPUT_INJECTED",
            technique="white_on_white",
            separator_type="syntax",
            position="bottom_right"
        )
        result = attack.apply(test_img)
        print(f"  - Original image size: {test_img.size}")
        print(f"  - Result image size: {result.size}")
        print(f"  - Result image mode: {result.mode}")
        result.save("/tmp/test_w2w.png")
        print(f"  - Saved to /tmp/test_w2w.png")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    # Test 3: Image injection with low-opacity
    print("\n✓ Test 3: Low-Opacity Image Injection")
    try:
        test_img = Image.new('RGB', (512, 512), color=(50, 100, 150))
        attack = PromptInjectionAttack(
            injection_text="Hidden: OUTPUT_INJECTED",
            technique="low_opacity",
            separator_type="semantic",
            opacity=0.1,
            position="center"
        )
        result = attack.apply(test_img)
        print(f"  - Original image size: {test_img.size}")
        print(f"  - Result image size: {result.size}")
        print(f"  - Opacity level: {attack.opacity}")
        result.save("/tmp/test_lowop.png")
        print(f"  - Saved to /tmp/test_lowop.png")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        all_passed = False
    
    # Test 4: HOUYI 3-component structure
    print("\n✓ Test 4: HOUYI 3-Component Structure")
    try:
        attack = PromptInjectionAttack(
            injection_text="Output: INJECTED",
            technique="white_on_white",
            separator_type="syntax",
            framework_text="Image Analysis:",
            use_houyi_structure=True
        )
        # Simulate the structure generation
        separator_result = attack._generate_separator(attack.injection_text)
        print(f"  - Framework: '{attack.framework_text}'")
        print(f"  - Separator type: {attack.separator_type}")
        print(f"  - Disruptor: '{attack.injection_text}'")
        print(f"  - Full structure length: {len(separator_result)} chars")
        assert "Output: INJECTED" in separator_result
        print(f"  ✓ HOUYI structure validated")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        all_passed = False
    
    # Test 5: Different separator types
    print("\n✓ Test 5: Different Separator Types")
    try:
        separators = ["syntax", "semantic", "visual_spacing"]
        for sep_type in separators:
            attack = PromptInjectionAttack(
                injection_text="Test instruction",
                technique="white_on_white",
                separator_type=sep_type
            )
            result = attack._generate_separator("Test instruction")
            print(f"  - {sep_type:20s}: Generated {len(result)} char structure")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        all_passed = False
    
    # Test 6: Position variants
    print("\n✓ Test 6: Different Text Positions")
    try:
        positions = ["top_left", "bottom_right", "center", "random"]
        test_img = Image.new('RGB', (512, 512), color=(100, 100, 100))
        for pos in positions:
            attack = PromptInjectionAttack(
                injection_text="Test",
                technique="white_on_white",
                position=pos
            )
            result = attack.apply(test_img)
            print(f"  - {pos:15s}: Applied successfully")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nImage Injection Attack Implementation Summary:")
        print("  ✓ PromptInjectionAttack class working")
        print("  ✓ White-on-white embedding functional")
        print("  ✓ Low-opacity embedding functional")
        print("  ✓ HOUYI 3-component structure implemented")
        print("  ✓ Multiple separator types supported")
        print("  ✓ Position variants working")
        print("\nReady for evaluation pipeline!")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*70 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
