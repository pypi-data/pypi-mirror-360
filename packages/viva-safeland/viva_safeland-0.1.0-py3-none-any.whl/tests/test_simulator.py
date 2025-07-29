import pytest

from src.modules.simulator import Simulator


def test_simulator_initialization():
    """Tests that the Simulator can be initialized without errors."""
    try:
        Simulator(input_size=(3840, 2160), output_size=(480, 288), height_dron=110)
    except Exception as e:
        pytest.fail(f"Simulator initialization failed with an exception: {e}")
