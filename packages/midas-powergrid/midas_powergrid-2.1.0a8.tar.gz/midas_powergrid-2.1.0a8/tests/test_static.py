"""This module contains test cases for the pandapower grid model."""

import unittest

import numpy as np

from midas_powergrid.model.static import PandapowerGrid


class TestPandapowerGrid(unittest.TestCase):
    """Test case for the pandapower grid wrapper."""

    def test_cigre_lv(self):
        """Test for *common* pandapower grids."""
        model = PandapowerGrid("cigre_lv")

        model.run_powerflow(0)
        outputs = model.get_outputs()
        self.assertTrue(outputs)

    def test_cigre_mv(self):
        """Test for *common* pandapower grids."""
        model = PandapowerGrid("cigre_mv")

        model.run_powerflow(0)
        outputs = model.get_outputs()
        self.assertTrue(outputs)

    def test_cigre_hv(self):
        """Test for *common* pandapower grids."""
        model = PandapowerGrid("cigre_hv")

        model.run_powerflow(0)
        outputs = model.get_outputs()
        self.assertTrue(outputs)

    def test_midas_mv(self):
        """Test for midas pandapower grid variants."""
        model = PandapowerGrid("midasmv")

        model.run_powerflow(0)
        outputs = model.get_outputs()
        self.assertTrue(outputs)

    def test_midas_lv(self):
        """Test for midas pandapower grid variants."""
        model = PandapowerGrid("midaslv")

        model.run_powerflow(0)
        outputs = model.get_outputs()
        self.assertTrue(outputs)

    def test_simbench(self):
        """Test for simbench grids."""
        model = PandapowerGrid("1-LV-rural3--0-sw")

        model.run_powerflow(0)
        outputs = model.get_outputs()
        self.assertTrue(outputs)

    def test_json(self):
        """Test for a json grid."""
        pass

    def test_excel(self):
        """Test for a xlsx grid."""
        pass

    def test_set_inputs_load(self):
        """Test to set an input for a load."""
        model = PandapowerGrid("cigre_lv")

        self.assertEqual(model.grid.get_value("load", 0, "p_mw"), 0.19)
        self.assertEqual(model.grid.get_value("load", 0, "q_mvar"), 0.06244998)
        self.assertTrue(model.grid.get_value("load", 0, "in_service"))

        model.set_inputs(
            etype="Load",
            idx=0,
            data={"p_mw": 0.04, "q_mvar": 0.02, "in_service": False},
        )

        self.assertEqual(model.grid.get_value("load", 0, "p_mw"), 0.04)
        self.assertEqual(model.grid.get_value("load", 0, "q_mvar"), 0.02)
        self.assertFalse(model.grid.get_value("load", 0, "in_service"))

    def test_get_outputs(self):
        """Test to get the outputs after the powerflow."""

        model = PandapowerGrid("simple_four_bus_system")
        output = model.get_outputs()

        self.assertAlmostEqual(output["0-bus-1"]["vm_pu"], 0.996608)
        self.assertAlmostEqual(
            output["0-bus-1"]["va_degree"], -150.208, places=3
        )

        self.assertAlmostEqual(
            output["0-line-0"]["loading_percent"], 31.273, places=3
        )
        self.assertAlmostEqual(
            output["0-trafo-0"]["va_lv_degree"], -150.208, places=3
        )

        self.assertEqual(output["0-load-0-2"]["p_mw"], 0.03)
        self.assertEqual(output["0-sgen-1-3"]["p_mw"], 0.015)

    def test_trafo_pos_input(self):
        model = PandapowerGrid("midasmv")

        model.set_inputs(etype="trafo", idx=0, data={"tap_pos": 3})
        outputs = model.get_outputs()
        self.assertEqual(3, model.grid._grid.trafo.loc[0, "tap_pos"])
        self.assertEqual(3, outputs["0-trafo-0"]["tap_pos"])

        model.cache = {}
        model.set_inputs(etype="trafo", idx=1, data={"tap_pos": None})
        outputs = model.get_outputs()
        self.assertEqual(0, outputs["0-trafo-1"]["tap_pos"])

        model.cache = {}
        model.set_inputs(etype="trafo", idx=1, data={"tap_pos": np.nan})
        outputs = model.get_outputs()
        self.assertEqual(0, outputs["0-trafo-1"]["tap_pos"])

    def test_trafo_pos_input_bhv(self):
        model = PandapowerGrid("bhv")
        model.set_inputs(etype="trafo", idx=4, data={"tap_pos": 3})
        outputs = model.get_outputs()
        self.assertEqual(0, outputs["0-trafo-4"]["tap_pos"])

    def test_tap_pos_delta(self):
        model = PandapowerGrid("bhv")
        outputs1 = model.get_outputs()

        model.cache = {}
        model.set_inputs(etype="trafo", idx=4, data={"delta_tap_pos": -1})
        outputs = model.get_outputs()
        self.assertEqual(0, outputs["0-trafo-4"]["tap_pos"])

        model.cache = {}
        model.set_inputs(etype="trafo", idx=1, data={"delta_tap_pos": 1})
        outputs2 = model.get_outputs()
        self.assertEqual(0, outputs1["0-trafo-1"]["tap_pos"])
        self.assertEqual(1, outputs2["0-trafo-1"]["tap_pos"])

        model.cache = {}
        model.set_inputs(etype="trafo", idx=1, data={"delta_tap_pos": 1})
        outputs = model.get_outputs()
        self.assertEqual(2, outputs["0-trafo-1"]["tap_pos"])

        # Trafo 1 has tap_min=-2 and tap_max=+2, so should go higher than 2
        model.cache = {}
        model.set_inputs(etype="trafo", idx=1, data={"delta_tap_pos": 1})
        outputs = model.get_outputs()
        self.assertEqual(2, outputs["0-trafo-1"]["tap_pos"])


if __name__ == "__main__":
    unittest.main()
