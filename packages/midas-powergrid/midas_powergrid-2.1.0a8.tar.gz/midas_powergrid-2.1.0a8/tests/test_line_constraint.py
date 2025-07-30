import unittest
from unittest.mock import MagicMock

from pandapower.powerflow import LoadflowNotConverged

from midas_powergrid.constraints.line import PPLine


class TestPPLineConstraint(unittest.TestCase):
    def setUp(self):
        self.grid = MagicMock()
        self.grid.get_value.return_value = 50.0
        self.grid.run_powerflow.return_value = None

        self.line = PPLine(index=0, grid=self.grid, value=80)

    def test_line_kept_disabled_if_powerflow_fails_when_trying_to_enable(self):
        # Force the line to be initially disabled
        self.line.in_service = False

        # Simulate:
        # - First call to get_value → 50% (low loading, valid for
        #   checking enabling attempt)
        # - run_powerflow() → raise exception (fail to enable)
        # - Second call to get_value (after failed powerflow) → not called,
        #   because powerflow failed
        self.grid.get_value.side_effect = [50.0]  # loading check before enable
        self.grid.run_powerflow.side_effect = LoadflowNotConverged()

        changed = self.line.step(time=5)

        self.assertFalse(changed)
        self.assertFalse(self.line.in_service)
        self.grid.set_value.assert_any_call("line", 0, "in_service", True)
        self.grid.set_value.assert_any_call("line", 0, "in_service", False)
        self.assertEqual(self.grid.run_powerflow.call_count, 2)

    def test_line_reenables_if_loading_is_ok(self):
        # Initially disabled
        self.line.in_service = False
        # Enable succeeds, loading is OK
        self.grid.get_value.side_effect = [
            50.0,
            50.0,
        ]  # pre-check + post-check
        self.grid.run_powerflow.return_value = None

        changed = self.line.step(time=6)

        self.assertTrue(changed)
        self.assertTrue(self.line.in_service)

    def test_line_disables_if_loading_too_high(self):
        self.grid.get_value.return_value = 120.0  # Above threshold
        self.line.in_service = True

        changed = self.line.step(time=1)

        self.assertTrue(changed)
        self.assertFalse(self.line.in_service)

    def test_line_remains_in_service_if_loading_ok(self):
        self.grid.get_value.return_value = 50.0
        self.line.in_service = True

        changed = self.line.step(time=2)

        self.assertFalse(changed)
        self.assertTrue(self.line.in_service)

    def test_line_logs_state_change(self):
        self.grid.get_value.return_value = 120.0
        self.line.in_service = True

        with self.assertLogs(
            "midas_powergrid.constraints.line", level="DEBUG"
        ) as log:
            self.line.step(time=10)

        self.assertIn("Line 0 out of service", log.output[0])


if __name__ == "__main__":
    unittest.main()
