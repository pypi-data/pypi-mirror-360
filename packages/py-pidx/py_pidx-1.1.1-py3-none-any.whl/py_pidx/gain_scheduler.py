class GainScheduler:
    def __init__(self, schedule=None):
        """
        schedule: list of tuples [(min_val, max_val, (Kp, Ki, Kd)), ...]
        """
        self.schedule = schedule or []

    def get_gains(self, pv):
        """Return (Kp, Ki, Kd) based on current process variable (pv)."""
        for (min_val, max_val, gains) in self.schedule:
            if min_val <= pv < max_val:
                return gains
        # If pv is out of all ranges, return default gains (e.g. last or zeros)
        if self.schedule:
            return self.schedule[-1][2]
        else:
            return (1.0, 0.0, 0.0)  # fallback default
