"""Pure virtual battery transition model (percent units, not 0..1)."""

def advance(percent, dt, moving, charging, idle_rate, moving_rate, charge_rate):
    """Advance charge for dt simulated seconds; constrain result to [0,100]."""
    if dt < 0 or min(idle_rate, moving_rate, charge_rate) < 0:
        raise ValueError("time and rates must be nonnegative")
    rate = charge_rate if charging else -(moving_rate if moving else idle_rate)
    return max(0.0, min(100.0, percent + rate * dt / 60.0))
