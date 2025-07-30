import unittest

import pandapower as pp

from midas_powergrid.custom.bhv import build_grid
from midas_powergrid.model.static import PandapowerGrid


class TestBremerhaven(unittest.TestCase):
    def test_powerflow(self):
        grid = build_grid()
        self.assertTrue(grid.res_bus.empty)
        try:
            pp.runpp(grid)
        except pp.LoadflowNotConverged:
            self.assertTrue(False, "Load flow failed")
        self.assertFalse(grid.res_bus.empty)

    def test_powerflow_with_extension(self):
        grid = build_grid(use_extension=True)
        self.assertTrue(grid.res_bus.empty)
        try:
            pp.runpp(grid)
        except pp.LoadflowNotConverged:
            self.assertTrue(False, "Load flow failed")
        self.assertFalse(grid.res_bus.empty)

    def test_with_constraints(self):
        constraints = [
            ("line", 100),
            ("load", 0.02),
            ("sgen", 0.05),
            ("storage", 0.02),
            ("bus", 0.1),
        ]
        #     "disable_numba": False,
        # }

        grid = PandapowerGrid("bhv", {"add_storages": True}, constraints)

        try:
            grid.run_powerflow(0)
        except pp.LoadflowNotConverged:
            self.assertTrue(False, "Load flow failed")
        self.assertFalse(grid.grid._grid.res_bus.empty)  # type: ignore


if __name__ == "__main__":
    unittest.main()
