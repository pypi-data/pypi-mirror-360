"""
Tests for the Barbell class.
"""
import pytest
from blc.barbell import Barbell


def test_barbell_initialization_men():
    """Test initialization of a men's barbell with default weight."""
    barbell = Barbell(weight=20, type="men")
    assert barbell.weight == 20
    assert barbell.type == "men"


def test_barbell_initialization_women():
    """Test initialization of a women's barbell (should always be 15kg)."""
    barbell = Barbell(weight=20, type="women")
    assert barbell.weight == 15  # Should override to 15kg for women's bar
    assert barbell.type == "women"


def test_barbell_initialization_default():
    """Test initialization with default parameters."""
    barbell = Barbell()
    assert barbell.weight == 20  # Default men's weight
    assert barbell.type == "men"  # Default type


def test_barbell_initialization_custom_weight():
    """Test initialization with a custom weight for men's barbell."""
    barbell = Barbell(weight=25, type="men")
    assert barbell.weight == 25  # Custom weight for men's bar
    assert barbell.type == "men"


def test_barbell_initialization_custom_weight_women():
    """Test that women's barbell always uses 15kg regardless of input weight."""
    # Even if we try to set a different weight, women's bar should be 15kg
    barbell = Barbell(weight=25, type="women")
    assert barbell.weight == 15  # Should be 15kg for women's bar
    assert barbell.type == "women"

    barbell = Barbell(weight=10, type="women")
    assert barbell.weight == 15  # Still 15kg even if we try to set less
