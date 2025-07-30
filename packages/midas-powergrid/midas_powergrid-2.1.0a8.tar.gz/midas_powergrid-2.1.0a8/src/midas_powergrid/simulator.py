"""This module implements the mosaik simulator API for the
pandapower model.

"""

import json
import logging
import sys
from typing import Any, Dict, List

import mosaik_api_v3
import numpy as np
from midas.util.dict_util import update
from midas.util.logging import set_and_init_logger
from mosaik_api_v3.types import (
    InputData,
    Meta,
    ModelName,
    OutputData,
    OutputRequest,
    SimId,
)
from typing_extensions import override

from midas_powergrid.meta import META
from midas_powergrid.model.static import PandapowerGrid
from midas_powergrid.plotter import Plotter

# Need to hard code the name because if started as separate
# procress, the __name__ is __main__ instead.
LOG = logging.getLogger("midas_powergrid.simulator")


class PandapowerSimulator(mosaik_api_v3.Simulator):
    """The pandapower simulator."""

    def __init__(self):
        super().__init__(META)
        self.sid: str = ""
        self.models: dict[str, PandapowerGrid] = {}
        self.entity_map: dict = {}
        self.entities: list = []

        self.step_size: int = 0
        self.now_dt = None
        self.cache: dict = {}

        self.plotting = False
        self.plotter_cfg: dict = {}
        self.plotter = None
        self._sim_time: int = 0

    @override
    def init(
        self,
        sid: SimId,
        time_resolution: float = 1.0,
        *,
        step_size: int = 900,
        plotting: bool = False,
        plot_path: str = "_plots",
        **sim_params,
    ) -> Meta:
        """Called exactly ones after the simulator has been started.

        Parameters
        ----------
        sid : str
            Simulator ID for this simulator.
        step_size : int, optional
            Step size for this simulator. Defaults to 900.

        Returns
        -------
        dict
            The meta dict (set by mosaik_api.Simulator)

        """
        self.sid = sid
        self.step_size = step_size
        self.plotting = plotting
        if self.plotting:
            self.plotter = Plotter()
            self.plotter_cfg["plot_path"] = plot_path

        return self.meta

    @override
    def create(
        self,
        num: int,
        model: ModelName,
        *,
        gridfile: str = "midasmv",
        pp_params: dict[str, Any] | None = None,
        include_slack_bus: bool = False,
        constraints: list[tuple[str, float]] | None = None,
        surrogate_params: dict[str, Any] | None = None,
        **model_params,
    ):
        """Initialize the simulation model instance (entity)

        Returns
        -------
        list
            A list with information on the created entity.

        """

        if pp_params is None:
            pp_params = {}
        if constraints is None:
            constraints = []
        if surrogate_params is None:
            surrogate_params = {}

        entities = []
        # use_constraints = model_params.get("use_constraints", False)

        for _ in range(num):
            gidx = len(self.models)
            eid = f"{model}-{gidx}"

            self.models[eid] = PandapowerGrid(
                gridfile,
                pp_params,
                constraints,
                surrogate_params=surrogate_params,
                include_slack_bus=include_slack_bus,
                grid_idx=gidx,
            )

            self.plotter_cfg[eid] = {
                "grid_type": self.models[eid].grid_type,
                "plot_name": gridfile,
                "plotting": self.plotting,
            }

            children = list()
            for cid, attrs in sorted(self.models[eid].entity_map.items()):
                assert cid not in self.entity_map
                self.entity_map[cid] = attrs
                etype = attrs["etype"]

                # We'll only add relations from lines to nodes (and not
                # from nodes to lines) because this is sufficient for
                # mosaik to build the entity graph
                relations = list()
                if etype.lower() in [
                    "trafo",
                    "line",
                    "load",
                    "sgen",
                    "storage",
                ]:
                    relations = attrs["related"]

                children.append({"eid": cid, "type": etype, "rel": relations})

            entity = {
                "eid": eid,
                "type": model,
                "rel": list(),
                "children": children,
            }
            entities.append(entity)
            self.entities.append(entity)

        return entities

    @override
    def step(self, time: int, inputs: InputData, max_advance: int = 0) -> int:
        """Perform a simulation step.

        Parameters
        ----------
        time : int
            The current simulation step (by convention in seconds since
            simulation start.
        inputs : dict
            A *dict* containing inputs for entities of this simulator.

        Returns
        -------
        int
            The next step this simulator wants to be stepped.

        """
        self._sim_time = time

        for eid, attrs in inputs.items():
            log_msg = {
                "id": f"{self.sid}.{eid}",
                "name": eid,
                "type": eid.split("-")[1],
                "sim_time": self._sim_time,
                "msg_type": "input",
                "src_eids": [],
            }
            gidx = eid.split("-")[0]
            grid = self.models.get(f"Grid-{gidx}", None)

            if grid is None:
                LOG.critical("No grid found for grid index %s!", gidx)
                raise KeyError

            idx = self.entity_map[eid]["idx"]
            etype = self.entity_map[eid]["etype"]

            for attr, src_ids in attrs.items():
                setpoint = 0.0
                all_none = True
                for src_id, val in src_ids.items():
                    if val is not None:
                        setpoint += float(val)
                        all_none = False
                        log_msg["src_eids"].append(src_id)
                if all_none:
                    setpoint = None

                attrs[attr] = setpoint  # type: ignore[reportArgumentType]
                log_msg[attr] = setpoint
            try:
                grid.set_inputs(etype, idx, attrs)
            except Exception as err:
                LOG.error(
                    f"Failed to set inputs {attrs} for etype {etype}"
                    f" at index {idx}: {err}"
                )
                raise ValueError(
                    f"Impossible input {attrs} for {etype} ({idx})."
                )
            log_msg["src_eids"] = list(set(log_msg["src_eids"]))
            LOG.info(json.dumps(log_msg))

        for eid, model in self.models.items():
            try:
                model.run_powerflow(time)
            except Exception:
                LOG.exception("Failed to perform power flow calculation.")
                # raise ValueError(
                #     f"Failed to perform power flow calculation: {err}"
                # )
                raise
            try:
                self.cache[eid] = model.get_outputs()
                for child, cache in self.cache[eid].items():
                    self.cache[child] = cache
            except Exception as err:
                LOG.error(f"Failed to get outputs: {err}")
                raise ValueError(f"Failed to get outputs: {err}")

            if self.plotter is not None and self.plotter_cfg[eid]["plotting"]:
                self.plotter.grid = model.grid._grid
                self.plotter.plot_path = self.plotter_cfg["plot_path"]
                self.plotter.plot_name = self.plotter_cfg[eid]["plot_name"]
                self.plotter.grid_type = self.plotter_cfg[eid]["grid_type"]
                self.plotter.plot(eid, int(time / self.step_size))

        return time + self.step_size

    @override
    def get_data(self, outputs: OutputRequest) -> OutputData:
        """Return the requested outputs (if feasible).

        Parameters
        ----------
        outputs : dict
            A *dict* containing requested outputs of each entity.

        Returns
        -------
        dict
            A *dict* containing the values of the requested outputs.

        """

        data: dict = {}
        grid_json: dict = {}

        for eid, attrs in outputs.items():
            if "Grid" in eid:
                self._get_grid_attributes(eid, attrs, data, grid_json)
            else:
                self._get_children_attributes(eid, attrs, data)

        update(data, grid_json)
        return data

    def finalize(self):
        for model in self.models.values():
            model.finalize()

    def _get_grid_attributes(
        self,
        eid: str,
        attrs: List[str],
        data: Dict[str, Dict[str, Any]],
        grid_json: Dict[str, Any],
    ) -> None:
        if "health" in attrs:
            health = (
                self.models[eid]
                .grid.get_element_attribute_values("res_bus", attr="vm_pu")[1:]
                .mean()
            )
            if np.isnan(health):
                LOG.debug(
                    "Grid health is NaN. This might be okay so "
                    "setting health to 0. Just that you know!"
                )
                health = 0
            data.setdefault(eid, dict())["health"] = health

        if "grid_json" in attrs:
            grid_json.setdefault(eid, dict())["grid_json"] = self.models[
                eid
            ].to_json()

    def _get_children_attributes(
        self, eid: str, attrs: List[str], data: Dict[str, Dict[str, Any]]
    ) -> None:
        log_msg = {
            "id": f"{self.sid}_{eid}",
            "name": eid,
            "type": eid.split("-")[1],
            "sim_time": self._sim_time,
            "msg_type": "output",
        }
        for attr in attrs:
            val = self.cache[eid][attr]
            if np.isnan(val):
                LOG.debug(f"{attr} for {eid} is NaN. Setting to 0.")
                val = 0
            if isinstance(val, np.bool_):
                val = bool(val)
            if isinstance(val, np.integer):
                val = int(val)
            if isinstance(val, np.floating):
                val = float(val)

            data.setdefault(eid, dict())[attr] = val
            log_msg[attr] = val

        try:
            LOG.info(json.dumps(log_msg))
        except TypeError:
            print(log_msg)
            sys.exit(-1)


if __name__ == "__main__":
    set_and_init_logger(
        0, "powergrid-logfile", "midas-powergrid.log", replace=True
    )
    LOG.info("Starting mosaik simulation...")
    mosaik_api_v3.start_simulation(PandapowerSimulator())
