from tb4_virtual_battery.battery_math import advance
import pytest

def step(p, dt=60, moving=False, charging=False, idle=0.03, drain=2.0, charge=12.0):
    return advance(p, dt, moving, charging, idle, drain, charge)

def test_moving_drain():
    assert step(16, moving=True) == pytest.approx(14)

def test_idle_drain():
    assert step(16) == pytest.approx(15.97)

def test_charge():
    assert step(16, charging=True) == pytest.approx(28)

def test_bounds():
    assert step(1, dt=300, moving=True) == 0
    assert step(98, charging=True) == 100

def test_charge_takes_priority_over_motion():
    assert step(16, moving=True, charging=True) == pytest.approx(28)

def test_bad_rates():
    with pytest.raises(ValueError):
        step(16, drain=-1)
