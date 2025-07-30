import csv
import logging
import os
from abc import ABC, abstractclassmethod, abstractmethod
from importlib import import_module
from os.path import join
from pathlib import Path
from typing import Any, cast

import joblib
import numpy as np
import pandas as pd
from typing_extensions import override

from midas_powergrid.model.pp_grid import PPGrid

LOG = logging.getLogger(__name__)
try:
    import torch  # type: ignore[reportMissingImports]
except ImportError:
    LOG.info(
        "Torch is not available. Cannot load surrogate models from torch. "
        "Please install torch if you need this functionality."
    )


class SurrogateGrid(PPGrid):
    def __init__(
        self,
        grid_name: str,
        grid_params: dict[str, Any],
        surrogate_params: dict[str, Any],
    ):
        super().__init__(grid_name, grid_params)

        capsule = Capsule()
        self._model = capsule.load(
            join(surrogate_params["base_path"], surrogate_params["model_path"])
        )
        self._input_map: dict[str, int] = capsule.input_map
        self._output_map: dict[str, int] = capsule.output_map

        self._evaluate = surrogate_params.get("evaluate", False)

        self._save_path = surrogate_params.get("save_path", ".")
        self._model_result_path: os.PathLike = join(
            self._save_path,
            surrogate_params.get("save_model_results_to", "model_results.csv"),
        )
        self._ppg_results_path: os.PathLike = join(
            self._save_path,
            surrogate_params.get("save_ppgrid_results_to", "ppg_results.csv"),
        )

        self._inputs: np.ndarray = np.zeros((len(self._input_map),))
        self._outputs: np.ndarray = np.zeros((len(self._output_map),))
        self._rmses: dict[str, list[float]] = {
            "vm_pu": [],
            "va_degree": [],
            "bus_p_mw": [],
            "bus_q_mvar": [],
            "line_loading": [],
            "trafo_loading": [],
            "eg_p_mw": [],
            "eg_q_mvar": [],
        }
        self._model_results: list[list[float]] = []
        self._ppg_results: list[list[float]] = []
        self._load_inputs_from_grid: bool = True

    def set_value(
        self, etype: str, idx: int, attr: str, val: float | int | bool
    ):
        self._load_inputs()
        key = f"{etype.capitalize()}_{idx:03d}__{attr}"
        self._inputs[self._input_map[key]] = val

        if self._evaluate:
            super().set_value(etype, idx, attr, val)

    def run_powerflow(self):
        self._load_inputs()
        self._outputs = self._model.predict(
            self._inputs.reshape(1, -1)
        ).flatten()

        if self._inputs.sum() == 0.0 or self._evaluate:
            super().run_powerflow()

        if self._evaluate:
            self._model_results.append(list(self._outputs))
            self._ppg_results.append(
                list(self._grid.res_bus.vm_pu.values[1:])
                + list(self._grid.res_bus.va_degree.values[1:])
                + list(self._grid.res_bus.p_mw.values[1:])
                + list(self._grid.res_bus.q_mvar.values[1:])
                + list(self._grid.res_line.loading_percent.values)
                + list(self._grid.res_trafo.loading_percent.values)
                + list(self._grid.res_ext_grid.p_mw.values)
                + list(self._grid.res_ext_grid.q_mvar.values)
            )

    def get_value(self, etype, idx=None, attr=None):
        self._load_inputs()
        if etype.startswith("res_"):
            etype_ = etype.split("_", 1)[1]
        else:
            etype_ = etype
        if idx is not None and attr is not None:
            key = f"{etype_.capitalize()}_{idx:03d}__{attr}"
            if key in self._input_map:
                return self._inputs[self._input_map[key]].item()
            elif key in self._output_map:
                return self._outputs[self._output_map[key]].item()
            else:
                return super().get_value(etype, idx, attr)
        elif attr is not None:
            keys = [
                k
                for k in self._input_map
                if (etype_.capitalize() in k and attr in k)
            ]
            if keys:
                return [self._inputs[self._input_map[k]] for k in keys]
            keys = [
                k
                for k in self._output_map
                if (etype_.capitalize() in k and attr in k)
            ]
            if keys:
                return [self._outputs[self._output_map[k]] for k in keys]

        return super().get_value(etype, idx, attr)

    def get_element_values(self, etype: str) -> pd.DataFrame:
        """Return a slice of all elements of *etype*."""
        element = super().get_element_values(etype)
        keys = []
        if etype.startswith("res_"):
            etype_ = etype.split("_", 1)[1].capitalize()
            for k, i in self._output_map.items():
                if etype_ in k:
                    keys.append((k, i))

            for k, i in keys:
                el, attr = k.split("__")
                index = el.rsplit("_", 1)[1]
                val = self._outputs[i]
                if attr in ("in_service", "closed"):
                    val = False if val == 0 else True
                element.at[int(index), attr] = val
        else:
            etype_ = etype.capitalize()
            for k, i in self._input_map.items():
                if etype_ in k in k:
                    keys.append((k, i))

            for k, i in keys:
                el, attr = k.split("__")
                index = el.rsplit("_", 1)[1]
                val = self._inputs[i]
                if attr in ("in_service", "closed"):
                    val = False if val == 0 else True
                element.at[int(index), attr] = val

        return cast(pd.DataFrame, element)

    @override
    def get_element_at_index_values(self, etype: str, idx: int) -> pd.Series:
        element = super().get_element_at_index_values(etype, idx)
        keys = []
        if etype.startswith("res_"):
            etype_ = etype.split("_", 1)[1].capitalize()
            for k, i in self._output_map.items():
                if etype_ in k and f"{idx:03d}" in k:
                    keys.append((k, i))
            for k, i in keys:
                attr = k.split("__")[1]
                val = self._outputs[i]
                if attr in ("in_service", "closed"):
                    val = False if val == 0 else True
                element[attr] = val
        else:
            etype_ = etype.capitalize()

            for k, i in self._input_map.items():
                if etype_ in k and f"{idx:03d}" in k:
                    keys.append((k, i))
            for k, i in keys:
                attr = k.split("__")[1]
                val = self._inputs[i]
                if attr in ("in_service", "closed"):
                    val = False if val == 0 else True
                element[attr] = val

        return cast(pd.Series, element)

    def finalize(self):
        if self._evaluate:
            with open(
                join(os.getcwd(), self._model_result_path), "w", newline=None
            ) as csv_file:
                writer = csv.writer(
                    csv_file,
                    delimiter=",",
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL,
                )

                writer.writerow(list(self._output_map.keys()))
                for idx in range(len(self._model_results)):
                    row = self._model_results[idx]
                    writer.writerow(row)

            with open(
                join(os.getcwd(), self._ppg_results_path), "w", newline=None
            ) as csv_file:
                writer = csv.writer(
                    csv_file,
                    delimiter=",",
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL,
                )

                writer.writerow(list(self._output_map.keys()))
                for idx in range(len(self._ppg_results)):
                    row = self._ppg_results[idx]
                    writer.writerow(row)

    def _load_inputs(self):
        if self._load_inputs_from_grid:
            self._load_inputs_from_grid = False
            for key, val in self._input_map.items():
                etype_no, attr = key.split("__")
                etype, idx = etype_no.rsplit("_", 1)
                self._inputs[val] = self._grid[etype.lower()].at[
                    int(idx), attr
                ]
        if self._grid.res_bus.empty:
            super().run_powerflow()


class BaseModel(ABC):
    @abstractmethod
    def fit(self, features: np.ndarray, labels: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    @abstractmethod
    def predict(self, features: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    @abstractmethod
    def get_metadata(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def save_to_disc(self, path: str, model_name: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def load_from_disc(self, filename: str, metadata: dict[str, Any]) -> None:
        raise NotImplementedError


class Capsule:
    def __init__(self):
        self.model: BaseModel | None = None
        self.input_map: dict[str, int] = {}
        self.output_map: dict[str, int] = {}

    def fit(self, features: np.ndarray, labels: np.ndarray) -> np.ndarray:
        if self.model is None:
            msg = "Model was not initialized. Call `load` before using `fit`"
            raise ValueError(msg)

        return self.model.fit(features, labels)

    def predict(self, features: np.ndarray) -> np.ndarray:
        if self.model is None:
            msg = (
                "Model was not initialized. Call `load` before using `predict`"
            )
            raise ValueError(msg)
        return self.model.predict(features)

    def load(self, filename: os.PathLike) -> Any:
        """Load model with optional device override for torch models."""

        path, fn = os.path.split(filename)
        name, suf = fn.rsplit(".", 1)
        metadata_path = Path(path) / f"metadata_{name}.{suf}"

        data = cast(dict[str, Any], joblib.load(metadata_path))
        model_meta = data["model_data"]
        module_name, clazz_name = model_meta["import_str"].split(":")
        module = import_module(module_name)
        clazz = getattr(module, clazz_name)

        self.model = clazz(*model_meta["args"], **model_meta["kwargs"])
        self.model.load_from_disc(Path(path) / data["model_file"], model_meta)

        self.input_map = data["input_map"]
        self.output_map = data["output_map"]

        return self.model

    def save(
        self,
        filename: os.PathLike,
        model: Any,
        input_map: dict[str, int],
        output_map: dict[str, int],
    ) -> None:
        """Save model to disk and move it to cpu for torch models."""
        self.model = model
        self.input_map = input_map
        self.output_map = output_map

        path, fn = os.path.split(filename)
        name, suf = fn.rsplit(".", 1)

        metadata_path = Path(path) / f"metadata_{name}.{suf}"

        model_meta = self.model.get_metadata()
        model_file = self.model.save_to_disc(path, name)

        data = {
            "model_file": model_file,
            "model_data": model_meta,
            "input_map": self.input_map,
            "output_map": self.output_map,
        }
        joblib.dump(data, metadata_path)
