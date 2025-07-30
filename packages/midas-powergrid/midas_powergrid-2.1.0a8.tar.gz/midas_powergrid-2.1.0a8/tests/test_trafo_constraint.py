import unittest
from unittest.mock import Mock

import numpy as np
import pandapower as pp

from midas_powergrid.constraints.transformer import PPTransformer


class TestPPTransformer(unittest.TestCase):
    def setUp(self):
        self.grid = Mock()
        self.grid.set_value = Mock()
        self.grid.run_powerflow = Mock()

        # Transformer with 2 allowed changes/hour
        self.trafo = PPTransformer(index=0, grid=self.grid, value=2)

    def test_no_tap_change(self):
        self.trafo.tap_pos = 1
        self.grid.get_value.return_value = 1  # Same tap position

        changed = self.trafo.step(time=10)

        self.assertFalse(changed)
        self.assertEqual(self.trafo.tap_pos, 1)
        self.grid.run_powerflow.assert_not_called()

    def test_tap_change_within_limit(self):
        self.trafo.tap_pos = 0
        self.trafo.changes = {}
        self.grid.get_value.return_value = 1

        changed = self.trafo.step(time=100)

        self.assertTrue(changed)
        self.assertEqual(self.trafo.tap_pos, 1)
        self.grid.run_powerflow.assert_not_called()

    def test_tap_change_exceeds_limit(self):
        # Simulate recent tap changes
        self.trafo.tap_pos = 0
        self.trafo.changes = {900: 1, 950: 2}  # 2 changes already
        self.grid.get_value.return_value = 3

        changed = self.trafo.step(time=1000)

        self.assertFalse(changed)
        self.assertNotIn(1000, self.trafo.changes)
        self.grid.run_powerflow.assert_called_once()

    def test_get_tap_handles_nan(self):
        self.grid.get_value.return_value = np.nan
        self.assertEqual(self.trafo._get_tap(), 0)

    def test_get_tap_handles_key_error(self):
        self.grid.get_value.side_effect = KeyError
        self.assertEqual(self.trafo._get_tap(), 0)

    def test_powerflow_failure_does_not_crash(self):
        self.trafo.tap_pos = 0
        self.grid.get_value.return_value = 1
        self.grid.run_powerflow.side_effect = pp.LoadflowNotConverged

        changed = self.trafo.step(time=1234)

        self.assertTrue(changed)
        self.grid.run_powerflow.assert_not_called()


if __name__ == "__main__":
    unittest.main()
