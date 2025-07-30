"""This module contains a wrapper for pandapower grids."""

from typing import Any

import numpy as np
import pandapower as pp
from mosaik_api_v3.types import OutputData

from midas_powergrid.constraints.base import GridElementConstraint
from midas_powergrid.constraints.bus import PPBus
from midas_powergrid.constraints.line import PPLine
from midas_powergrid.constraints.load import PPLoad
from midas_powergrid.constraints.sgen import PPSgen
from midas_powergrid.constraints.storage import PPStorage
from midas_powergrid.constraints.transformer import PPTransformer
from midas_powergrid.meta import ATTRIBUTE_MAP
from midas_powergrid.model import LOG
from midas_powergrid.model.pp_grid import PPGrid
from midas_powergrid.model.surrogate import SurrogateGrid


class PandapowerGrid:
    """A model for pandapower grids."""

    def __init__(
        self,
        gridfile: str,
        pp_params: dict[str, Any] | None = None,
        constraints: list[tuple[str, float]] | None = None,
        *,
        surrogate_params: dict[str, Any] | None = None,
        include_slack_bus: bool = False,
        grid_idx=0,
    ) -> None:
        if pp_params is None:
            pp_params = {}
        if constraints is None:
            constraints = []
        if surrogate_params is None:
            surrogate_params = {}
        self.entity_map: dict[str, dict[str, Any]] = {}
        self.grid_idx: int = grid_idx
        self.time_step: int = 0
        self.ids: dict[str, dict[str, Any]] = {}
        self.cache: OutputData = {}
        self.constraints: dict[str, list[GridElementConstraint]] = {}

        self.run_diagnostic: bool = False
        self.lf_converged: bool = False
        self._lf_states: list[bool] = []
        self._include_slack_bus: bool = include_slack_bus

        self.grid: PPGrid
        if surrogate_params:
            self.grid = SurrogateGrid(gridfile, pp_params, surrogate_params)
        else:
            self.grid = PPGrid(gridfile, pp_params)

        self._load_grid_ids()
        self._load_entity_map()

        # To save some time during runtime
        self.run_powerflow(-1)

        self._constraints_to_load: list[tuple[str, float]] = constraints
        self._load_constraints()

    def set_inputs(self, etype: str, idx: int, data: dict[str, Any]) -> None:
        """Set input from other simulators."""
        etype = etype.lower()
        if etype not in ["load", "sgen", "trafo", "switch", "storage"]:
            LOG.info("Invalid etype %s. Skipping.", etype)
            return

        for name, value in data.items():
            # Add try/except ?
            if value is None or np.isnan(value):
                # print(f"Skipping {etype}-{idx}-{name} because of None")
                continue
            # else:
            #     print(f"Setting {etype}-{idx}-{name}: {value}")

            if etype == "switch" and name == "closed":
                if not isinstance(value, bool):
                    if isinstance(value, float):
                        value = (
                            value >= 0.5
                        )  # workaround since no hybrid SAC available
                    else:
                        value = value != 0

            if etype == "trafo" and name == "delta_tap_pos":
                name = "tap_pos"
                current_val = self.grid.get_value(etype, idx, name)
                if np.isnan(current_val):
                    continue

                value = current_val + value

            if etype == "trafo" and name == "tap_pos":
                try:
                    minv = self.grid.get_value(etype, idx, "tap_min")
                    maxv = self.grid.get_value(etype, idx, "tap_max")
                    if np.isnan(minv) or np.isnan(maxv):
                        LOG.info(
                            "One of 'tap_min' (%f) or 'tap_max' (%f)"
                            "is NaN, cannot check boundaries of "
                            "'tap_pos' of Trafo %d. Proceeding with 0.",
                            minv,
                            maxv,
                            idx,
                        )
                        minv = 0.0
                        maxv = 0.0
                        value = 0
                except KeyError:
                    value = 0
                    LOG.warning(
                        "Trying to access 'tap_min' and 'tap_max' but"
                        "those do not exist in the grid. Will set "
                        "value to 0."
                    )
                else:
                    value = min(maxv, max(minv, value))

                # self.grid.set_value(etype, idx, name, )

            if name == "in_service":
                if not isinstance(value, bool):
                    if isinstance(value, float):
                        value = value >= 0.5
                    else:
                        value = value != 0

            self.grid.set_value(etype, idx, name, value)

            # if etype in self.constraints:
            #     # Constraint can change the value
            #     setattr(self.constraints[etype][idx], name, value)

    def run_powerflow(self, time: int, max_iter=2):
        """Run the powerflow calculation."""
        if self.constraints:
            self._run_constraints(time)
        else:
            self._run_powerflow(time)

    def _run_powerflow(self, time):
        """Run the powerflow calculation."""
        try:
            self.grid.run_powerflow()
            self.lf_converged = True
        except pp.LoadflowNotConverged:
            LOG.info(
                "At step %d: Loadflow did not converge. Set "
                "*run_diagnostic* to True "
                "to run pandapower diagnostics.",
                time,
            )
            self.lf_converged = False

            if self.run_diagnostic:
                pp.diagnostic(self.grid)

        self.cache = {}

    def _run_constraints(self, time, max_iter=2):
        self._lf_states.append(self.lf_converged)  # previous state

        # Run once to check current state
        self._run_powerflow(time)

        if time < 0:
            # The first step is done before the simulation to make use
            # of numba's speed-up during the simulation
            return

        state_changed = False

        # Now constraints can change the input state if necessary
        # Constraints will definitively change the state of the grid
        # so another power flow calculation is required afterwards
        for key in ["trafo", "load", "sgen", "storage", "line", "bus"]:
            if key not in self.constraints:
                continue
            for element in self.constraints[key]:
                state_changed = element.step(time) or state_changed

        # Maybe more elements were put out of service than necessary
        # e.g., when the critical element is the last one checked.
        # Performing another iteration allows elements to switch on
        # again if no constraints are violated.
        if max_iter > 1:
            return self._run_constraints(time, max_iter - 1)

        self._run_powerflow(time)
        if state_changed:
            if not self._lf_states[0] and self.lf_converged:
                LOG.info(f"At step {time}: Constraints fixed failing LF.")
            if not self._lf_states[0] and not self.lf_converged:
                LOG.info(f"At step {time}: LF still not converging.")
            if self._lf_states[0] and not self.lf_converged:
                LOG.info(f"At step {time}: LF broke due to constraints.")
            if self._lf_states[0] and self.lf_converged:
                LOG.info(f"At step {time}: LF still converging.")

        self._lf_states = []

    def get_outputs(self) -> OutputData:
        if self.cache:
            return self.cache

        for eid, attrs in self.entity_map.items():
            data = {}
            for otype, outputs in ATTRIBUTE_MAP[attrs["etype"]].items():
                element = {}
                try:
                    element = self.grid.get_element_at_index_values(
                        otype, attrs["idx"]
                    )
                except IndexError:
                    LOG.exception(
                        f"Failed to get element {otype} from index "
                        f"{attrs['idx']}"
                    )
                for output in outputs:
                    if otype == "trafo" and output[0] == "delta_tap_pos":
                        data[output[0]] = 0

                    elif otype == "switch" and output[0] == "closed":
                        if self.lf_converged:
                            if np.isnan(element["closed"]):
                                value = 0.0
                            else:
                                value = 1.0 if element["closed"] else 0.0
                        else:
                            value = 0.0
                        data[output[0]] = value
                    else:
                        data[output[0]] = (
                            _convert_bool(element[output[0]])
                            if self.lf_converged
                            else 0
                        )
            self.cache[eid] = data

        return self.cache

    def to_json(self):
        return pp.to_json(self.grid)

    def _load_grid_ids(self):
        """Create a dictionary containing the names of the components.

        Use generic names and map to actual names?

        """
        self.ids["slack"] = self.grid.get_element_attribute_values(
            "ext_grid", "bus"
        ).to_dict()
        self.ids["bus"] = self.grid.get_element_attribute_values(
            "bus", "name"
        ).to_dict()
        self.ids["load"] = self.grid.get_element_attribute_values(
            "load", "name"
        ).to_dict()
        self.ids["sgen"] = self.grid.get_element_attribute_values(
            "sgen", "name"
        ).to_dict()
        self.ids["line"] = self.grid.get_element_attribute_values(
            "line", "name"
        ).to_dict()
        self.ids["trafo"] = self.grid.get_element_attribute_values(
            "trafo", "name"
        ).to_dict()
        self.ids["switch"] = self.grid.get_element_attribute_values(
            "switch", "name"
        ).to_dict()
        self.ids["storage"] = self.grid.get_element_attribute_values(
            "storage", "name"
        ).to_dict()

    def _load_entity_map(self):
        """Load the entity map for the mosaik simulator."""

        self._get_slack()
        self._get_buses()
        self._get_loads()
        self._get_sgens()
        self._get_lines()
        self._get_trafos()
        self._get_switches()
        self._get_storages()

    def _get_slack(self):
        """Create an entity for the slack bus."""
        for idx in self.ids["slack"]:
            element = self.grid.get_element_at_index_values("ext_grid", idx)
            eid = self._create_eid(
                "ext_grid", idx, self.grid.get_value("ext_grid", idx, "bus")
            )

            self.entity_map[eid] = {
                "etype": "Ext_grid",
                "idx": int(idx),
                "static": {
                    "name": element["name"],
                    "vm_pu": float(element["vm_pu"]),
                    "va_degree": float(element["va_degree"]),
                },
            }

    def _is_slack_bus(self, bus_id):
        for bus in self.ids["slack"].values():
            if bus == bus_id:
                return True

        return False

    def _get_buses(self):
        """Create entities for buses."""
        for idx in self.ids["bus"]:
            if not self._include_slack_bus and self._is_slack_bus(idx):
                continue

            element = self.grid.get_element_at_index_values("bus", idx)
            eid = self._create_eid("bus", idx)
            self.entity_map[eid] = {
                "etype": "Bus",
                "idx": int(idx),
                "static": {
                    "name": element["name"],
                    "vn_kv": float(element["vn_kv"]),
                },
            }

    def _get_loads(self):
        """Create entities for loads."""
        for idx in self.ids["load"]:
            element = self.grid.get_element_at_index_values("load", idx)
            eid = self._create_eid("load", idx, element["bus"])
            bid = self._create_eid("bus", element["bus"])
            element_data = element.to_dict()

            keys_to_del = [
                "profile",
                "voltLvl",
                "const_z_percent",
                "const_i_percent",
                "min_q_mvar",
                "min_p_mw",
                "max_q_mvar",
                "max_p_mw",
            ]
            element_data_static = {
                key: element_data[key]
                for key in element_data
                if key not in keys_to_del
            }

            self.entity_map[eid] = {
                "etype": "Load",
                "idx": int(idx),
                "static": element_data_static,
                "related": [bid],
            }

    def _get_sgens(self):
        """Create entities for sgens."""
        for idx in self.ids["sgen"]:
            element = self.grid.get_element_at_index_values("sgen", idx)
            eid = self._create_eid("sgen", idx, element["bus"])
            bid = self._create_eid("bus", element["bus"])
            element_data = element.to_dict()

            keys_to_del = [
                "profile",
                "voltLvl",
                "min_q_mvar",
                "min_p_mw",
                "max_q_mvar",
                "max_p_mw",
            ]
            element_data_static = {
                key: element_data[key]
                for key in element_data
                if key not in keys_to_del
            }

            self.entity_map[eid] = {
                "etype": "Sgen",
                "idx": int(idx),
                "static": element_data_static,
                "related": [bid],
            }

    def _get_lines(self):
        """Create entities for lines."""
        for idx in self.ids["line"]:
            element = self.grid.get_element_at_index_values("line", idx)
            eid = self._create_eid("line", idx)
            fbid = self._create_eid("bus", element["from_bus"])
            tbid = self._create_eid("bus", element["to_bus"])

            element_data = element.to_dict()
            keys_to_del = ["from_bus", "to_bus"]
            element_data_static = {
                key: element_data[key]
                for key in element_data
                if key not in keys_to_del
            }

            self.entity_map[eid] = {
                "etype": "Line",
                "idx": int(idx),
                "static": element_data_static,
                "related": [fbid, tbid],
            }

    def _get_trafos(self):
        """Create entities for trafos."""
        for idx in self.ids["trafo"]:
            element = self.grid.get_element_at_index_values("trafo", idx)
            eid = self._create_eid("trafo", idx)
            hv_bid = self._create_eid("bus", element["hv_bus"])
            lv_bid = self._create_eid("bus", element["lv_bus"])

            element_data = element.to_dict()
            keys_to_del = ["hv_bus", "lv_bus"]
            element_data_static = {
                key: element_data[key]
                for key in element_data
                if key not in keys_to_del
            }

            self.entity_map[eid] = {
                "etype": "Trafo",
                "idx": int(idx),
                "static": element_data_static,
                "related": [hv_bid, lv_bid],
            }

    def _get_switches(self):
        """Create entities for switches."""
        for idx in self.ids["switch"]:
            element = self.grid.get_element_at_index_values("switch", idx)
            eid = self._create_eid("switch", idx)
            bid = self._create_eid("bus", element["bus"])
            oid = ""

            if element["et"] == "l":
                oid = self._create_eid("line", element["element"])
            elif element["et"] == "t":
                oid = self._create_eid("trafo", element["element"])
            elif element["et"] == "b":
                oid = self._create_eid("bus", element["element"])

            element_data = element.to_dict()
            keys_to_del = ["element"]
            element_data_static = {
                key: element_data[key]
                for key in element_data
                if key not in keys_to_del
            }

            self.entity_map[eid] = {
                "etype": "Switch",
                "idx": int(idx),
                "static": element_data_static,
                "related": [bid, oid],
            }

    def _get_storages(self):
        """Create entities for storages."""
        for idx in self.ids.get("storage", list()):
            element = self.grid.get_element_at_index_values("storage", idx)
            eid = self._create_eid("storage", idx, element["bus"])
            bid = self._create_eid("bus", element["bus"])
            element_data = element.to_dict()

            keys_to_del = []
            element_data_static = {
                key: element_data[key]
                for key in element_data
                if key not in keys_to_del
            }

            self.entity_map[eid] = {
                "etype": "Storage",
                "idx": int(idx),
                "static": element_data_static,
                "related": [bid],
            }

    def _create_eid(self, name, idx, bus_id=None):
        eid = f"{self.grid_idx}-{name}-{idx}"
        if bus_id is not None:
            eid = f"{eid}-{bus_id}"
        return eid

    def finalize(self):
        self.grid.finalize()

    def _load_constraints(self):
        for constr in self._constraints_to_load:
            etype, value = constr
            self.constraints.setdefault(etype, list())
            for idx in range(len(self.grid.get_element_values(etype))):
                self.constraints[etype].append(self._create(etype, idx, value))

    def _create(self, etype, index, value):
        if etype == "trafo":
            clazz = PPTransformer
        elif etype == "bus":
            clazz = PPBus
        elif etype == "load":
            clazz = PPLoad
        elif etype == "sgen":
            clazz = PPSgen
        elif etype == "line":
            clazz = PPLine
        elif etype == "storage":
            clazz = PPStorage
        else:
            msg = (
                f"Invalid constraint type {etype}. Valid types are "
                "trafo, bus, load, sgen, storage, and line"
            )
            raise ValueError(msg)
        return clazz(index, self.grid, value)

    @property
    def grid_type(self) -> str:
        return self.grid.plot_type


def _convert_bool(val):
    if isinstance(val, bool):
        val = 1 if val else 0
    try:
        if not isinstance(val, str):
            if np.isnan(val):
                val = 0
    except TypeError:
        print(f"value: {val} ({type(val)})")
        raise
    return val
