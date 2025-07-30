import unittest
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
from pandapower import LoadflowNotConverged

from midas_powergrid.constraints.bus import PPBus


class TestPPBus(unittest.TestCase):
    def setUp(self):
        # Create a mock grid object
        self.grid = MagicMock()

        # Default vm_pu inside limits
        self.vm_pu = 1.01

        def get_value_mock(*args, **kwargs):
            key = args
            if key == ("bus", 0, "in_service"):
                return True
            elif key == ("res_bus", 0, "vm_pu"):
                return self.vm_pu
            elif key == ("load",):
                return pd.DataFrame({"bus": [0]}, index=[10])  # type: ignore[reportArgumentType]
            elif key == ("load", "bus"):
                return pd.Series([0], index=[10])
            elif key == ("sgen",):
                return pd.DataFrame({"bus": [0]}, index=[20])  # type: ignore[reportArgumentType]
            elif key == ("sgen", "bus"):
                return pd.Series([0], index=[20])
            elif key == ("storage",):
                return pd.DataFrame({"bus": [0]}, index=[30])  # type: ignore[reportArgumentType]
            elif key == ("storage", "bus"):
                return pd.Series([0], index=[30])
            else:
                return MagicMock()

        self.grid.get_value.side_effect = get_value_mock
        self.grid.run_powerflow.return_value = True

        self.bus = PPBus(index=0, grid=self.grid, value=0.05)  # ±5%

    def test_normal_voltage_no_state_change(self):
        self.vm_pu = 1.02  # within 1.05 limit
        changed = self.bus.step(time=1)
        self.assertFalse(changed)
        self.assertTrue(self.bus.in_service)

    def test_over_voltage_disables_sgens(self):
        self.vm_pu = 1.07  # above 1.05 max
        changed = self.bus.step(time=2)
        self.assertTrue(changed)
        self.assertFalse(self.bus.in_service)
        self.assertFalse(self.bus.sgens_is)

    def test_under_voltage_disables_loads(self):
        self.vm_pu = 0.93  # below 0.95 min
        changed = self.bus.step(time=3)
        self.assertTrue(changed)
        self.assertFalse(self.bus.in_service)
        self.assertFalse(self.bus.loads_is)

    def test_nan_voltage_triggers_disable_all(self):
        self.vm_pu = np.nan
        changed = self.bus.step(time=4)
        self.assertTrue(changed)
        self.assertFalse(self.bus.in_service)
        self.assertFalse(self.bus.loads_is)
        self.assertFalse(self.bus.sgens_is)
        self.assertFalse(self.bus.storages_is)

    def test_reenable_bus_when_voltage_stable(self):
        # Step 1: force it off due to low voltage
        self.vm_pu = 0.93
        self.bus.step(time=1)
        self.assertFalse(self.bus.in_service)

        # Step 2: now voltage is OK, expect re-enable
        self.vm_pu = 1.0
        changed = self.bus.step(time=2)
        self.assertTrue(changed)
        self.assertTrue(self.bus.in_service)
        self.assertTrue(self.bus.loads_is)
        self.assertTrue(self.bus.sgens_is)
        self.assertTrue(self.bus.storages_is)

    def test_bus_stays_off_if_voltage_still_violated(self):
        # Step 1: force it off
        self.vm_pu = 1.07
        self.bus.step(time=1)

        # Step 2: try re-enabling but still over voltage
        self.vm_pu = 1.06
        changed = self.bus.step(time=2)
        self.assertFalse(changed)
        self.assertFalse(self.bus.in_service)

    def test_powerflow_failure_disables_bus(self):
        self.grid.run_powerflow.side_effect = [True, LoadflowNotConverged()]
        self.vm_pu = 1.07
        changed = self.bus.step(time=3)
        self.assertTrue(changed)
        self.assertFalse(self.bus.in_service)


if __name__ == "__main__":
    unittest.main()
