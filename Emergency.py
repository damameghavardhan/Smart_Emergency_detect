class EmergencyTrafficController:
    """Small, UI-independent state machine for the traffic-light demo."""

    def __init__(self) -> None:
        self.signal = "RED"
        self.vehicle = ""
        self.seconds_remaining = 0

    @property
    def emergency_active(self) -> bool:
        return self.seconds_remaining > 0

    def activate(self, vehicle: str, duration_seconds: int) -> None:
        vehicle = vehicle.strip()
        if not vehicle:
            raise ValueError("Vehicle type cannot be empty.")
        if duration_seconds < 1:
            raise ValueError("Duration must be at least one second.")

        self.signal = "GREEN"
        self.vehicle = vehicle
        self.seconds_remaining = duration_seconds

    def advance(self) -> bool:
        """Advance one second; return True when the emergency phase expires."""
        if not self.emergency_active:
            return False

        self.seconds_remaining -= 1
        if self.seconds_remaining == 0:
            self.reset()
            return True
        return False

    def reset(self) -> None:
        self.signal = "RED"
        self.vehicle = ""
        self.seconds_remaining = 0