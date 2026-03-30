"""
Basic unit tests for PromptInjectionAttack.

Tests core functionality without requiring external model downloads:
- Attack instantiation
- Image embedding techniques (white-on-white, low-opacity)
- HOUYI 3-component structure
- Separator types
- Position variants
"""

import sys
from pathlib import Path
from PIL import Image
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from attacks.prompt_injection import PromptInjectionAttack


class TestAttackInstantiation:
    """Test PromptInjectionAttack instantiation and basic properties."""
    
    def test_basic_instantiation(self):
        """Test creating a basic attack instance."""
        attack = PromptInjectionAttack(
            injection_text="Output: INJECTED",
            technique="white_on_white",
            separator_type="syntax"
        )
        assert attack.injection_text == "Output: INJECTED"
        assert attack.technique == "white_on_white"
        assert attack.separator_type == "syntax"
    
    def test_with_houyi_structure(self):
        """Test instantiation with HOUYI structure enabled."""
        attack = PromptInjectionAttack(
            injection_text="Output: INJECTED",
            technique="white_on_white",
            separator_type="syntax",
            use_houyi_structure=True,
            framework_text="Image Analysis:"
        )
        assert attack.use_houyi_structure is True
        assert attack.framework_text == "Image Analysis:"
    
    def test_different_techniques(self):
        """Test instantiation with different embedding techniques."""
        techniques = ["white_on_white", "low_opacity", "steganography"]
        for technique in techniques:
            attack = PromptInjectionAttack(
                injection_text="Test",
                technique=technique,
                separator_type="syntax"
            )
            assert attack.technique == technique


class TestImageEmbedding:
    """Test image embedding functionality."""
    
    def test_white_on_white_embedding(self):
        """Test white-on-white text embedding."""
        test_img = Image.new('RGB', (512, 512), color=(100, 150, 200))
        
        attack = PromptInjectionAttack(
            injection_text="Hidden: OUTPUT_INJECTED",
            technique="white_on_white",
            separator_type="syntax",
            position="bottom_right"
        )
        
        result = attack.apply(test_img)
        
        assert result.size == test_img.size
        assert result.mode == test_img.mode
        # Verify the image was modified (pixels changed)
        assert list(result.getdata()) != list(test_img.getdata())
    
    def test_low_opacity_embedding(self):
        """Test low-opacity overlay embedding."""
        test_img = Image.new('RGB', (512, 512), color=(50, 100, 150))
        
        attack = PromptInjectionAttack(
            injection_text="Hidden: OUTPUT_INJECTED",
            technique="low_opacity",
            separator_type="semantic",
            opacity=0.1,
            position="center"
        )
        
        result = attack.apply(test_img)
        
        assert result.size == test_img.size
        assert result.mode == test_img.mode
        assert attack.opacity == 0.1
    
    def test_different_positions(self):
        """Test text placement at different positions."""
        positions = ["top_left", "bottom_right", "center", "random"]
        test_img = Image.new('RGB', (512, 512), color=(100, 100, 100))
        
        for pos in positions:
            attack = PromptInjectionAttack(
                injection_text="Test",
                technique="white_on_white",
                position=pos
            )
            result = attack.apply(test_img)
            assert result.size == test_img.size


class TestHOUYIStructure:
    """Test HOUYI 3-component structure."""
    
    def test_houyi_component_generation(self):
        """Test HOUYI component generation."""
        attack = PromptInjectionAttack(
            injection_text="Output: INJECTED",
            technique="white_on_white",
            separator_type="syntax",
            framework_text="Image Analysis:",
            use_houyi_structure=True
        )
        
        result = attack._generate_separator(attack.injection_text)
        
        # Verify all components are present
        assert attack.framework_text in result
        assert attack.injection_text in result
        assert "Output: INJECTED" in result
    
    def test_separator_types(self):
        """Test different separator types in HOUYI structure."""
        separators = ["syntax", "semantic", "visual_spacing"]
        
        for sep_type in separators:
            attack = PromptInjectionAttack(
                injection_text="Test instruction",
                technique="white_on_white",
                separator_type=sep_type
            )
            result = attack._generate_separator("Test instruction")
            
            # Verify separator structure is generated
            assert len(result) > 0
            assert "Test instruction" in result
    
    def test_syntax_separator(self):
        """Test syntax-based separator."""
        attack = PromptInjectionAttack(
            injection_text="Malicious instruction",
            separator_type="syntax"
        )
        result = attack._generate_separator("Malicious instruction")
        
        # Syntax separator should use --- symbols
        assert "---" in result
        assert "Malicious instruction" in result
    
    def test_semantic_separator(self):
        """Test semantic-based separator."""
        attack = PromptInjectionAttack(
            injection_text="Change output",
            separator_type="semantic"
        )
        result = attack._generate_separator("Change output")
        
        # Semantic separator should create reasoning-like structure
        assert "Change output" in result
        assert len(result) > len("Change output")


class TestMetricsIntegration:
    """Test integration with evaluation metrics."""
    
    def test_metrics_import(self):
        """Test that metrics can be imported and used."""
        from evaluator.metrics import (
            attack_success_rate,
            output_deviation_score,
            safety_bypass_rate
        )
        
        clean = "The image shows a cat"
        attacked = "The image shows a DOG"
        
        asr = attack_success_rate(clean, attacked, similarity_threshold=0.6)
        ods = output_deviation_score(clean, attacked)
        sbr = safety_bypass_rate("", attacked)
        
        assert isinstance(asr, (int, float))
        assert isinstance(ods, (int, float))
        assert isinstance(sbr, (int, float))
        assert 0 <= asr <= 1
        assert 0 <= ods <= 1
        assert 0 <= sbr <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
