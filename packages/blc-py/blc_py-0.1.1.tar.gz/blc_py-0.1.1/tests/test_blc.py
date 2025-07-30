"""
Tests for the Blc (Barbell Load Calculator) class.
"""
import pytest
from blc.blc import Blc
from blc.plates import Plates
from blc.barbell import Barbell


def test_blc_initialization():
    """Test that Blc initializes with correct attributes."""
    plates = Plates(use_collar=True)
    barbell = Barbell(weight=20, type="men")
    blc = Blc(plates=plates, barbell=barbell)

    assert blc.plates == plates
    assert blc.barbell == barbell
    assert blc.plates_to_use == []


def test_calculate_plates_success():
    """Test successful calculation of plates."""
    plates = Plates(use_collar=True)
    # Add some plates for testing
    plates.add_plate(20, 4)  # 4 plates of 20kg
    plates.add_plate(10, 4)  # 4 plates of 10kg

    barbell = Barbell(weight=20, type="men")
    blc = Blc(plates=plates, barbell=barbell)

    # 100kg total = 20kg bar + 80kg plates (40kg per side)
    # With collar (2.5kg each side), we need 42.5kg per side
    # Should use: 2x20kg + 2x1.25kg (but since we don't have 1.25kg, it will use what's available)
    result = blc.calculate_plates(weight=100)

    # The exact result depends on the implementation, but we can check some basics
    assert len(result) > 0
    assert sum(result) * 2 <= 80  # Total plate weight should be <= 80kg (100kg - 20kg bar)


def test_remove_weight_not_available():
    """Test removing weight that's not on the barbell."""
    plates = Plates(use_collar=True)
    barbell = Barbell(weight=20, type="men")
    blc = Blc(plates=plates, barbell=barbell)

    with pytest.raises(ValueError):
        blc.remove_weight(10)  # Try to remove 10kg that's not there
