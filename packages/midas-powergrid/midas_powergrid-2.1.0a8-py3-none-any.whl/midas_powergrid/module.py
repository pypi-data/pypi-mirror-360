"""This module contains the MIDAS powergrid upgrade."""

import json
import logging
import os
from importlib import import_module
from typing import cast

import numpy as np
from midas.scenario.upgrade_module import (
    ConstraintsConfig,
    ModuleParams,
    UpgradeModule,
)
from midas.util.dict_util import set_default_bool, set_default_float
from typing_extensions import override

from midas_powergrid.model.pp_grid import PPGrid

from .analysis.grid import analyze_grid
from .meta import ATTRIBUTE_MAP

LOG = logging.getLogger(__name__)


class PowergridModule(UpgradeModule):
    """The MIDAS powergrid update module."""

    def __init__(self):
        super().__init__(
            module_name="powergrid",
            default_scope_name="midasmv",
            default_sim_config_name="Powergrid",
            default_import_str=(
                "midas_powergrid.simulator:PandapowerSimulator"
            ),
            default_cmd_str=(
                "%(python)s -m midas_powergrid.simulator %(addr)s"
            ),
            log=LOG,
        )

        self.models = {}
        for entity, data in ATTRIBUTE_MAP.items():
            self.models.setdefault(entity, [])
            for attrs in data.values():
                for attr in attrs:
                    self.models[entity].append(attr)

        self._double_actuator_values: bool = False

    def check_module_params(self, mp: ModuleParams):
        """Check the module params for this upgrade."""

        set_default_bool(mp, "plotting", False)
        mp.setdefault(
            "plot_path",
            os.path.abspath(
                os.path.join(self.scenario.base.output_path, "plots")
            ),
        )
        set_default_bool(mp, "save_grid_json", False)
        mp.setdefault("constraints", cast(ConstraintsConfig, []))
        set_default_float(mp, "actuator_multiplier", 1.0)
        set_default_bool(mp, "exclude_slack_bus", False)

    def check_sim_params(self, mp: ModuleParams):
        """Check simulator params for a certain simulator."""

        self.sim_params.setdefault("gridfile", self.default_scope_name)
        self.sim_params.setdefault("grid_params", {})
        self._simp_from_modulep(mp, "plotting", dtype="bool")
        self._simp_from_modulep(mp, "plot_path")
        self._simp_from_modulep(mp, "save_grid_json", dtype="bool")
        self._simp_from_modulep(mp, "actuator_multiplier", dtype="float")
        self.sim_params.setdefault("grid_mapping", {})
        self._simp_from_modulep(mp, "exclude_slack_bus", dtype="bool")
        self.sim_params.setdefault("surrogate_params", {})

        self.sim_params.setdefault(
            "constraints", cast(ConstraintsConfig, mp["constraints"])
        )

    def start_models(self):
        """Start all models for this simulator.

        Since we want the grids to be able to be interconnected with
        each other, each grid model should have its own simulator.

        Parameters
        ----------
        sim_name : str
            The sim name, not to be confused with *sim_name* for
            mosaik's *sim_config*. **This** sim_name is the simulator
            key in the configuration yaml file.

        """
        model_key = self.scenario.generate_model_key(self)

        model_params = {
            "gridfile": self.sim_params["gridfile"],
            "pp_params": self.sim_params["grid_params"],
            "constraints": self.sim_params["constraints"],
            "include_slack_bus": not self.sim_params["exclude_slack_bus"],
            "surrogate_params": self.sim_params["surrogate_params"]
        }

        self.start_model(model_key, "Grid", model_params)

        if ":" in self.default_import_str:
            mod, clazz = self.default_import_str.split(":")
        else:
            mod, clazz = self.default_import_str.rsplit(".", 1)
        mod = import_module(mod)

        sim_dummy = getattr(mod, clazz)()
        sim_dummy.init(self.sid, **self.sim_params)
        entities = sim_dummy.create(1, "Grid", **model_params)
        grid_obj = sim_dummy.models[entities[0]["eid"]].grid
        self.scenario.add_to_model_extra_data(
            model_key, self.sim_key, {"grid": grid_obj}
        )
        self.scenario.add_to_world_state("grid_json", grid_obj.to_json())
        self.scenario.add_to_world_state(
            "grid_dict", json.loads(grid_obj.to_json())
        )

        # Backwards compatibility
        # Only works for midasmv anyways
        self._double_actuator_values = model_params["pp_params"].get(
            "double_actuator_values", False
        )
        if self._double_actuator_values:
            self.sim_params["actuator_multiplier"] = 2.0

        for entity in entities[0]["children"]:
            eid = entity["eid"]
            parts = eid.split("-")
            child_key = f"{model_key}"
            for part in parts[1:]:
                child_key += f"_{part}"

            self.scenario.script.model_start.append(
                f"{child_key} = [e for e in {model_key}.children "
                f'if e.eid == "{eid}"][0]\n'
            )
            self.scenario.add_model(
                child_key,
                self.sim_key,
                f"{entity['type']}",
                {},
                f"{self.sid}.{eid}",
                f"{self.sid}.{entities[0]['eid']}",
            )

    def connect(self, *args):
        # Nothing to do so far
        # Maybe to other grids in the future?
        pass

    def connect_to_db(self):
        """Add connections to the database."""

        grid_key = self.scenario.generate_model_key(self)
        db_key = self.scenario.find_first_model("store", "database")[0]
        if db_key is None:
            LOG.warning(
                "Could not find DB key in scenario. No connection to DB "
                "possible."
            )
            return
        for key, entity in self.scenario.get_models(self.sim_key).items():
            if grid_key not in key:
                continue
            mod_key = key

            # We only want to connect those attributes that are present
            # in the grid. That's why we iterate over existing entities
            # and not simply use the models defined above.
            if entity["name"] in self.models:
                self.connect_entities(
                    mod_key,
                    db_key,
                    [a[0] for a in self.models[entity["name"]]],
                )

        additional_attrs: list[str | tuple[str, str]] = ["health"]

        if self.sim_params["save_grid_json"]:
            additional_attrs.append("grid_json")

        self.connect_entities(grid_key, db_key, additional_attrs)

    def get_sensors(self):
        models = self.scenario.get_models(self.sim_key)
        for model_key, config in models.items():
            if config["name"] in self.models:
                for attr in self.models[config["name"]]:
                    name, dtype, low, high = attr

                    if dtype == "bool":
                        space = _int_box()
                    elif dtype == "int":
                        space = _int_box(low, high)
                    else:
                        space = _float_box(low, high)

                    self.scenario.sensors.append(
                        {"uid": f"{config['full_id']}.{name}", "space": space}
                    )

        grid_key = self.scenario.generate_model_key(self)
        grid = self.scenario.get_model(grid_key)
        if grid is None:
            msg = f"Could not get grid model '{grid_key}"
            raise ValueError(msg)

        self.scenario.sensors.append(
            {"uid": f"{grid['full_id']}.health", "space": _float_box(0, 1.2)}
        )
        # TODO:
        # self.scenario.sensors.append(
        #     {
        #         "uid": f"{grid.full_id}.grid_json",
        #         "space": ("Box(low=0, high=1, shape=(), dtype=np.float32)"),
        #     }
        # )

    def get_actuators(self):
        grid_key = self.scenario.generate_model_key(self)
        grid = self.scenario.get_model(grid_key)
        if grid is None:
            msg = "Grid object is None. Something went wrong, sorry!"
            raise ValueError(msg)
        try:
            pp_grid = grid["extra_data"]["grid"]
        except Exception:
            msg = "Could not retrieve grid object from model."
            raise ValueError(msg)

        models = self.scenario.get_models(self.sim_key)
        for model_key, config in models.items():
            if config["name"] == "Trafo":
                self.scenario.actuators.append(
                    {
                        "uid": f"{config['full_id']}.delta_tap_pos",
                        "space": _int_box(-1, 1),
                    }
                )
                tmin = tmax = 0
                etype = ""
                try:
                    _, etype, eidx = config["eid"].split("-")
                    try:
                        tmax = pp_grid.get_value(etype, int(eidx), "tap_max")
                        tmin = pp_grid.get_value(etype, int(eidx), "tap_min")
                        if np.isnan(tmin) or np.isnan(tmax):
                            raise KeyError(f"Trafo {etype} has no tmin/max")
                    except KeyError:
                        LOG.debug(
                            "No tap_min or tap_max found. Using maximum "
                            " integer values as limits."
                        )
                        tmin = np.iinfo(np.int32).min
                        tmax = np.iinfo(np.int32).max
                except Exception as err:
                    # print(err)
                    LOG.warning(
                        "Caught an error composing actuator information for "
                        f"{etype} with eid {config['eid']}: {type(err), err}. "
                        "Continuing with maximum integer values as limits.",
                        exc_info=err,
                    )
                    tmin = np.iinfo(np.int32).min
                    tmax = np.iinfo(np.int32).max
                self.scenario.actuators.append(
                    {
                        "uid": f"{config['full_id']}.tap_pos",
                        "space": _int_box(tmin, tmax),
                    }
                )
            if config["name"] == "Switch":
                self.scenario.actuators.append(
                    {
                        "uid": f"{config['full_id']}.closed",
                        "space": _int_box(0, 1),
                    }
                )
            if config["name"] in ("Load", "Sgen", "Storage"):
                _, etype, eidx, _ = config["eid"].split("-")
                p_min, p_max = get_min_and_max(
                    pp_grid,
                    etype,
                    int(eidx),
                    "p_mw",
                    cast(float, self.sim_params["actuator_multiplier"]),
                )
                q_min, q_max = get_min_and_max(
                    pp_grid,
                    etype,
                    int(eidx),
                    "q_mvar",
                    cast(float, self.sim_params["actuator_multiplier"]),
                )

                if q_max < q_min:
                    q_min = q_max
                    q_max = 0

                if p_min < p_max:
                    self.scenario.actuators.append(
                        {
                            "uid": f"{config['full_id']}.p_mw",
                            "space": _float_box(p_min, p_max),
                        }
                    )
                if q_min < q_max:
                    self.scenario.actuators.append(
                        {
                            "uid": f"{config['full_id']}.q_mvar",
                            "space": _float_box(q_min, q_max),
                        }
                    )

    @override
    def analyze(self, name, data, output_folder, start, end, step_size, full):
        all_grid_columns = [col for col in data.columns if "Powergrid" in col]
        sim_keys = list(
            dict.fromkeys([c.split(".", 1)[0] for c in all_grid_columns])
        )
        for sim_key in sim_keys:
            sim_columns = [col for col in data.columns if sim_key in col]
            grid_data = data[sim_columns]
            if start > 0:
                grid_data = grid_data.iloc[start:]
            if end > 0:
                grid_data = grid_data.iloc[:end]

            analyze_grid(
                grid_data,
                step_size,
                f"{name}-{sim_key.replace('/', '')}",
                output_folder,
                full,
            )

    def download(self, *args):  # type: ignore[reportIncompatibleMethodOverride]
        # No downloads, suppress logging output
        pass


def _float_box(low=0.0, high=1.0):
    return f"Box(low={low}, high={high}, shape=(), dtype=np.float32)"


def _int_box(low=0, high=1):
    return f"Box(low={low}, high={high}, shape=(), dtype=np.int32)"


def get_min_and_max(
    grid: PPGrid, etype: str, eidx: int, attr: str, multiplier: float
) -> tuple[float, float]:
    min_val = 0.0
    max_val = 0.0
    try:
        max_val = grid.get_value(etype, eidx, f"max_{attr}")
        assert not np.isnan(max_val)
    except (KeyError, AssertionError):
        LOG.debug("No or invalid max_%s found, using %s as max.", attr, attr)
        max_val = grid.get_value(etype, eidx, attr)

    try:
        min_val = grid.get_value(etype, eidx, f"min_{attr}")
        assert not np.isnan(min_val)
    except (KeyError, AssertionError):
        LOG.debug(
            "No or invalid min_%s found. Determining min value from etype."
        )
        if etype == "storage":
            min_val = max_val * -1
        else:
            min_val = 0.0

    return float(min_val) * multiplier, float(max_val) * multiplier
