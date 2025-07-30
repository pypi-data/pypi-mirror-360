import unittest

from midas_powergrid.model.static import PandapowerGrid


class TestConstraintedGrid(unittest.TestCase):
    def setUp(self) -> None:
        self.pp_params = {
            "constant_load_p_mw": 0.7,  # 0.5
            "constant_load_q_mvar": 0.23,  # 0.17
            "constant_sgen_p_mw": 0.4,  # 0.3
            "constant_sgen_q_mvar": -0.13,  # -0.1
        }
        self.line_constraints = [("line", 100.0)]
        self.slb_constraints = [("sgen", 0.05), ("load", 0.02), ("bus", 0.1)]
        self.storage_constraints = [("storage", 0.02)]
        self.trafo_constraints = [("trafo", 2.0)]

    def test_line_constraints(self):
        grid = PandapowerGrid("midasmv", self.pp_params, self.line_constraints)

        step_size = 60
        results = []
        setpoints = []
        for i in range(100):
            setpoints.append(0.7 + i * 0.05)
            grid.set_inputs("load", 1, {"p_mw": setpoints[-1]})
            grid.run_powerflow(i * step_size)
            results.append(grid.get_outputs())

        for i, res in enumerate(results):
            self._assert_line_loading_below_limit(res, 100, setpoints[i])

    def _assert_line_loading_below_limit(self, results, limit, p_set):
        lines = {k: v for k, v in results.items() if "line" in k}
        loadings = {
            line: val
            for line, data in lines.items()
            for key, val in data.items()
            if "loading" in key
        }
        checks = {}
        for line, loading in loadings.items():
            checks[line] = loading <= limit

            self.assertLessEqual(
                loading,
                limit,
                msg=f"Loading of line {line} is above limit: {loading} "
                f"/ {limit}",
            )

        return checks

    def test_voltage_constraints(self):
        ugrid = PandapowerGrid("midasmv", self.pp_params)
        grid = PandapowerGrid("midasmv", self.pp_params, self.slb_constraints)
        step_size = 60

        results = []
        uresults = []
        setpoints = []
        for i in range(100):
            setpoints.append(0.7 + i * 0.05)
            grid.set_inputs("load", 1, {"p_mw": setpoints[-1]})
            grid.run_powerflow(i * step_size)
            results.append(grid.get_outputs())

            ugrid.set_inputs("load", 1, {"p_mw": setpoints[-1]})
            ugrid.run_powerflow(i * step_size)
            uresults.append(ugrid.get_outputs())

        for res, p_set in zip(results, setpoints):
            self._assert_voltage_within_limits(res, 0.9, 1.1, p_set)

        success = True
        checks = []
        for res, p_set in zip(uresults, setpoints):
            checks.append(
                self._assert_voltage_within_limits(
                    res, 0.9, 1.1, p_set, allow_failure=True
                )
            )

        for c in checks:
            for val in c.values():
                success = success and val

        self.assertFalse(success)

    def _assert_voltage_within_limits(
        self, results, low, high, p_set=0.0, allow_failure=False
    ):
        buses = {k: v for k, v in results.items() if "bus" in k}
        vm_pus = {
            bus: val
            for bus, data in buses.items()
            for key, val in data.items()
            if "vm_pu" in key
        }

        checks = {}
        for bus in vm_pus:
            vm_pu = vm_pus[bus]
            checks[bus] = low <= vm_pu <= high

            if allow_failure:
                continue

            if vm_pu > high:
                msg = (
                    f"Voltage of bus {bus} is above limit: {vm_pus[bus]} "
                    f"/ {high}. p_set: {p_set}",
                )
                self.assertLessEqual(vm_pus[bus], high, msg=msg)
            if vm_pu < low:
                msg = (
                    f"Voltage of bus {bus} is below limit: {vm_pus[bus]} "
                    f"/ {low}. p_set: {p_set}",
                )
                self.assertGreaterEqual(vm_pus[bus], low, msg=msg)
        return checks

    def test_storage_constraints(self):
        self.pp_params["constant_load_p_mw"] = 0.4
        self.pp_params["constant_load_q_mvar"] = 0.13
        self.pp_params["constant_storage_p_mw"] = 0.4
        self.pp_params["constant_storage_q_mvar"] = 0.13
        grid = PandapowerGrid(
            "midasmv", self.pp_params, self.storage_constraints
        )

        step_size = 60
        setpoints = []
        results = []
        sign = 1
        for i in range(2):
            setpoints.append((0.7 + i * 0.2) * sign)
            grid.set_inputs("storage", 1, {"p_mw": setpoints[-1]})
            grid.run_powerflow(i * step_size)
            results.append(grid.get_outputs())
            sign *= -1

        # Storage 1 should be disabled in the second step (time=60)
        for idx, in_service in enumerate(
            grid.grid._grid.storage.in_service  # type: ignore[reportOptionalMemberAccess]
        ):
            if idx == 1:
                self.assertFalse(in_service, msg=f"1st: Failed for idx {idx}")
            else:
                self.assertTrue(in_service, msg=f"1st: Failed for idx {idx}")

        # Now storage 1 should be re-enabled again
        setpoints.append(0.4)
        grid.set_inputs("storage", 1, {"p_mw": setpoints[-1]})
        grid.run_powerflow(120)
        results.append(grid.get_outputs())

        for idx, in_service in enumerate(
            grid.grid._grid.storage.in_service  # type: ignore[reportOptionalMemberAccess]
        ):
            self.assertTrue(in_service, msg=f"2nd: Failed for idx {idx}")

        # Bonus; actually it is not guaranteed without bus constraints
        for res, p_set in zip(results, setpoints):
            self._assert_voltage_within_limits(res, 0.9, 1.1, p_set)

    def test_trafo_constraints(self):
        grid = PandapowerGrid("midasmv", {}, self.trafo_constraints)

        grid.run_powerflow(0)

        # First change, should be fine
        grid.set_inputs("trafo", 0, {"tap_pos": 1})
        grid.run_powerflow(10)
        self.assertEqual(1, grid.grid.get_value("trafo", 0, "tap_pos"))

        # Second change, should be fine
        grid.set_inputs("trafo", 0, {"tap_pos": -1})
        grid.run_powerflow(20)
        self.assertEqual(-1, grid.grid.get_value("trafo", 0, "tap_pos"))

        # Third change violates the constraint
        grid.set_inputs("trafo", 0, {"tap_pos": 0})
        grid.run_powerflow(30)
        self.assertEqual(-1, grid.grid.get_value("trafo", 0, "tap_pos"))

        # Fourth change still violates the constraint
        grid.set_inputs("trafo", 0, {"tap_pos": 0})
        grid.run_powerflow(3609)
        self.assertEqual(-1, grid.grid.get_value("trafo", 0, "tap_pos"))

        # Final change should work again
        grid.set_inputs("trafo", 0, {"tap_pos": 0})
        grid.run_powerflow(3610)
        self.assertEqual(0, grid.grid.get_value("trafo", 0, "tap_pos"))


if __name__ == "__main__":
    unittest.main()
