"""
Pytest configuration for image injection attack tests.

Provides shared fixtures and configuration for all image injection tests.
"""

import sys
from pathlib import Path
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def test_output_dir(tmp_path):
    """Create a temporary directory for test outputs."""
    return tmp_path


@pytest.fixture
def sample_test_image():
    """Create a simple test image."""
    from PIL import Image
    img = Image.new('RGB', (256, 256), color=(100, 150, 200))
    return img


@pytest.fixture
def attack_instance():
    """Create a basic PromptInjectionAttack instance."""
    from attacks.prompt_injection import PromptInjectionAttack
    return PromptInjectionAttack(
        injection_text="Test: INJECTED",
        technique="white_on_white",
        separator_type="syntax"
    )
