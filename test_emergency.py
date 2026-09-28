import unittest

from Emergency import EmergencyTrafficController


class EmergencyTrafficControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.controller = EmergencyTrafficController()

    def test_activation_sets_green_and_counts_down(self) -> None:
        self.controller.activate("Ambulance", 2)

        self.assertEqual(self.controller.signal, "GREEN")
        self.assertEqual(self.controller.vehicle, "Ambulance")
        self.assertFalse(self.controller.advance())
        self.assertEqual(self.controller.seconds_remaining, 1)

    def test_expiration_restores_red(self) -> None:
        self.controller.activate("Ambulance", 1)

        self.assertTrue(self.controller.advance())
        self.assertEqual(self.controller.signal, "RED")
        self.assertFalse(self.controller.emergency_active)

    def test_invalid_activation_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.controller.activate("  ", 10)  
        with self.assertRaises(ValueError):
            self.controller.activate("Ambulance", 0)

    def test_reset_clears_active_priority(self) -> None:
        self.controller.activate("Ambulance", 10)

        self.controller.reset()

        self.assertEqual(self.controller.signal, "RED")
        self.assertEqual(self.controller.vehicle, "")
        self.assertEqual(self.controller.seconds_remaining, 0)


if __name__ == "__main__":
    unittest.main()