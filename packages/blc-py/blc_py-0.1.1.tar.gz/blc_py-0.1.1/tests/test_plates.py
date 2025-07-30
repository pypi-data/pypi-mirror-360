"""
Tests for the Plates class.
"""
import pytest
from blc.plates import Plates, Plate


def test_plates_initialization():
    """Test that Plates initializes with correct default plates."""
    plates = Plates(use_collar=True)

    # Check that all default weights are initialized with quantity 8
    for weight in Plates.weights:
        assert plates.get_quantity(weight) == 8

    assert plates.use_collar is True


def test_add_plate():
    """Test adding plates to the collection."""
    plates = Plates()

    # Add 2 plates of 25kg
    plates.add_plate(25, 2)
    assert plates.get_quantity(25) == 10  # 8 default + 2 added

    # Add 4 more plates of 25kg
    plates.add_plate(25, 4)
    assert plates.get_quantity(25) == 14  # 10 + 4


def test_add_plate_odd_quantity():
    """Test adding an odd number of plates raises an error."""
    plates = Plates()

    with pytest.raises(ValueError, match="Quantity must be even"):
        plates.add_plate(25, 3)  # Odd quantity should raise error


def test_remove_plate():
    """Test removing plates from the collection."""
    plates = Plates()

    # Remove 2 plates of 25kg (from default 8)
    plates.remove_plate(25, 2)
    assert plates.get_quantity(25) == 6

    # Remove 4 more plates
    plates.remove_plate(25, 4)
    assert plates.get_quantity(25) == 2


def test_remove_plate_insufficient_quantity():
    """Test removing more plates than available raises an error."""
    plates = Plates()

    # Try to remove more plates than exist
    with pytest.raises(ValueError, match="Not enough plates"):
        plates.remove_plate(25, 10)  # Only 8 available by default


def test_set_quantity():
    """Test setting the quantity of a plate weight."""
    plates = Plates()

    plates.set_quantity(25, 4)
    assert plates.get_quantity(25) == 4

    with pytest.raises(ValueError, match="not in plates"):
        plates.set_quantity(100, 2)  # 100kg plates don't exist


def test_total_quantity():
    """Test getting the total quantity of all plates."""
    plates = Plates()

    # Default should have 8 of each weight
    total = plates.total_quantity()
    assert len(total) == len(Plates.weights)
    assert all(quantity == 8 for _, quantity in total)

    # After adding some plates
    plates.add_plate(25, 2)
    total = plates.total_quantity()
    assert any(weight == 25 and quantity == 10 for weight, quantity in total)


def test_iteration():
    """Test that Plates is iterable and returns weight, quantity pairs."""
    plates = Plates()

    # Should be able to iterate over plates
    for weight, quantity in plates:
        assert weight in Plates.weights
        assert quantity == 8  # Default quantity


def test_repr():
    """Test the string representation of Plates."""
    plates = Plates()

    # The repr should be a list of (weight, quantity) tuples
    rep = repr(plates)
    assert all(str((w, 8)) in rep for w in Plates.weights)
