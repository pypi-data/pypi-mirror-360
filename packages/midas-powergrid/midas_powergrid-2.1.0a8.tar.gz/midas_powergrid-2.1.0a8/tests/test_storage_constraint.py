import unittest
from unittest.mock import MagicMock, patch

import pandapower as pp

from midas_powergrid.constraints.storage import PPStorage, TimedVoltage


class TestPPStorage(unittest.TestCase):
    def setUp(self):
        # Create a mocked grid
        self.grid = MagicMock()
        self.grid.get_value.side_effect = lambda etype, idx, key: {
            "in_service": True,
            "p_mw": 1.0,
            "q_mvar": 0.5,
            "bus": 0,
            "vm_pu": 1.01,
        }[key]

        self.storage = PPStorage(index=0, grid=self.grid, value=0.02)

    def test_initialization(self):
        self.assertEqual(self.storage.index, 0)
        self.assertEqual(self.storage.etype, "storage")
        self.assertEqual(self.storage.expected_value, 0.02)
        self.assertEqual(self.storage.p_mw, 1.0)
        self.assertEqual(self.storage.q_mvar, 0.5)
        self.assertEqual(self.storage.in_service, True)
        self.assertEqual(self.storage.bus, 0)

    def test_prune_voltage_history(self):
        self.storage.time_frame = 5
        self.storage.time_voltages = [
            TimedVoltage(0, 1.0),
            TimedVoltage(2, 1.01),
            TimedVoltage(10, 0.99),
        ]
        self.storage._prune_voltage_history(time=10)
        self.assertEqual(len(self.storage.time_voltages), 1)
        self.assertEqual(self.storage.time_voltages[0], TimedVoltage(10, 0.99))

    def test_replace_or_append_voltage(self):
        self.storage.time_voltages = [TimedVoltage(0, 1.0)]
        self.storage._replace_or_append_voltage(0, 1.05)
        self.assertEqual(self.storage.time_voltages[0].value, 1.05)

        self.storage._replace_or_append_voltage(1, 1.03)
        self.assertEqual(len(self.storage.time_voltages), 2)

    def test_calculate_voltage_change(self):
        self.storage.time_voltages = [
            TimedVoltage(0, 0.98),
            TimedVoltage(10, 1.02),
        ]
        v_change, t_dist = self.storage._calculate_voltage_change()
        self.assertAlmostEqual(v_change, 0.04082, places=5)
        self.assertEqual(t_dist, 10)

    @patch("midas_powergrid.constraints.storage.pp.LoadflowNotConverged")
    def test_try_enable_storage_success(self, _):
        self.grid.run_powerflow.return_value = None
        result = self.storage._try_enable_storage()
        self.assertTrue(result)

    @patch(
        "midas_powergrid.constraints.storage.pp.LoadflowNotConverged",
        new=pp.LoadflowNotConverged,
    )
    def test_try_enable_storage_failure(self):
        self.grid.run_powerflow.side_effect = [pp.LoadflowNotConverged, None]
        result = self.storage._try_enable_storage()
        self.assertFalse(result)

    @patch("midas_powergrid.constraints.storage.LOG")
    def test_finalize_state_change_logs_and_runs_pf(self, mock_log):
        self.grid.run_powerflow.reset_mock()
        self.storage._finalize_state_change(
            time=5, old_state=False, voltage=1.0
        )
        self.assertTrue(self.grid.run_powerflow.called)

    def test_step_voltage_ok_storage_remains_on(self):
        self.storage.time_voltages = [TimedVoltage(0, 1.01)]
        self.grid.get_value.side_effect = lambda etype, idx, key: {
            "in_service": True,
            "p_mw": 1.0,
            "q_mvar": 0.5,
            "bus": 0,
            "vm_pu": 1.01,
        }[key]
        changed = self.storage.step(1)
        self.assertFalse(changed)
        self.assertTrue(self.storage.in_service)

    def test_step_voltage_exceeds_threshold_storage_disabled(self):
        self.storage.expected_value = 0.01
        self.storage.time_voltages = [TimedVoltage(0, 1.0)]
        self.grid.get_value.side_effect = lambda etype, idx, key: {
            "in_service": True,
            "p_mw": 1.0,
            "q_mvar": 0.5,
            "bus": 0,
            "vm_pu": 1.05,
        }[key]
        changed = self.storage.step(61)
        self.assertTrue(changed)
        self.assertFalse(self.storage.in_service)


if __name__ == "__main__":
    unittest.main()
