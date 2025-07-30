from __future__ import annotations

import collections
import logging
from typing import TYPE_CHECKING

import pandapower as pp

from midas_powergrid.constraints.base import GridElementConstraint

if TYPE_CHECKING:
    from midas_powergrid.model.pp_grid import PPGrid

LOG = logging.getLogger(__name__)

TimedVoltage = collections.namedtuple("TimedVoltage", ["time", "value"])


class PPStorage(GridElementConstraint):
    """Represents a storage unit in a power grid simulation.

    This class models the behavior of a storage element under voltage
    stability constraints. It behaves like a load when consuming power
    and (theoretically) like a static generator (sgen) when supplying,
    although only consumption behavior is currently supported.

    The storage monitors bus voltage over a sliding time window
    (`time_frame`). If voltage fluctuations exceed a specified
    threshold (`expected_value`), the unit is marked as out of service.
    The `step` method is called for each simulation time step to update
    power values and assess service status.

    Attributes
    ----------
    index: int
        Index of the storage element in the pandapower grid.
    grid: PPGrid
        The grid model containing all power elements.
    expected_value: float
        Allowed percentage change in voltage over the `time_frame`
        before shutdown.
    etype: str
        Element type, set to "storage".
    current_bus_voltage: float
        Latest measured bus voltage (pu).
    in_service: bool
        Whether the unit is currently in service.
    p_mw: float
        Active power consumption (MW).
    q_mvar: float
        Reactive power consumption (MVar).
    bus: int
        Index of the bus to which the storage is connected.
    time_frame: int
        Time window (in simulation steps) for voltage monitoring.
    time_voltages: list[TimedVoltage]
        History of voltage values with timestamps.
    """

    def __init__(
        self,
        index: int,
        grid: PPGrid,
        value: float = 0.02,
        etype: str = "storage",
    ):
        self.grid: PPGrid = grid
        self.index: int = index
        self.expected_value: float = value
        self.etype: str = etype

        self.current_bus_voltage: float = 1.0
        self.in_service: bool = grid.get_value(self.etype, index, "in_service")
        self.p_mw: float = grid.get_value(self.etype, index, "p_mw")
        self.q_mvar: float = grid.get_value(self.etype, index, "q_mvar")
        self.bus: int = grid.get_value(self.etype, self.index, "bus")

        self.time_frame: int = 60
        self.time_voltages: list[TimedVoltage] = []

        LOG.debug(
            "Loading constraint for storage %d with value %.2f", index, value
        )

    def step(self, time: int) -> bool:
        """Execute one simulation step for the storage unit.

        Parameters
        ----------
        time : int
            Current simulation time step.

        Returns
        -------
        bool
            True if the service state changed during the step, False otherwise.
        """
        old_state = self.in_service
        self.p_mw = self.grid.get_value(self.etype, self.index, "p_mw")
        self.q_mvar = self.grid.get_value(self.etype, self.index, "q_mvar")
        self.current_bus_voltage = self.grid.get_value(
            "res_bus", self.bus, "vm_pu"
        )

        self._prune_voltage_history(time)

        if not old_state:
            if not self._try_enable_storage():
                self._replace_or_append_voltage(time, self.current_bus_voltage)
                return False

            # Append new voltage after hypothetical activation
            self._replace_or_append_voltage(
                time, self.grid.get_value("res_bus", self.bus, "vm_pu")
            )
        else:
            self._replace_or_append_voltage(time, self.current_bus_voltage)

        v_change, t_dist = self._calculate_voltage_change()

        if v_change > self.expected_value * max(1, t_dist / self.time_frame):
            self.in_service = False
            if not old_state:
                # Do not want to keep what-if-voltage
                self.time_voltages.pop(-1)
                self.time_voltages.append(
                    TimedVoltage(time=time, value=self.current_bus_voltage)
                )
        else:
            self.in_service = True
            self.current_bus_voltage = self.time_voltages[-1].value
        self.grid.set_value(
            self.etype, self.index, "in_service", self.in_service
        )

        self._finalize_state_change(time, old_state, self.current_bus_voltage)

        return old_state != self.in_service

    def _prune_voltage_history(self, time: int) -> None:
        """Remove outdated voltage entries beyond the time frame.

        Parameters
        ----------
        time : int
            Current simulation time step.
        """
        time_voltages = [
            tv
            for tv in self.time_voltages
            if time - tv.time <= self.time_frame
        ]
        if not time_voltages and self.time_voltages:
            time_voltages.append(self.time_voltages[-1])
        self.time_voltages = time_voltages

    def _replace_or_append_voltage(self, time: int, voltage: float) -> None:
        """Add or replace voltage entry for the given time step.

        Parameters
        ----------
        time : int
            Simulation time step.
        voltage : float
            Voltage value to store.
        """
        replace_idx = -1
        for idx, tv in enumerate(self.time_voltages):
            if tv.time == time:
                replace_idx = idx

        tv = TimedVoltage(time=time, value=voltage)
        if replace_idx < 0:
            self.time_voltages.append(tv)
        else:
            self.time_voltages[replace_idx] = tv

    def _calculate_voltage_change(self) -> tuple[float, int]:
        """Calculate the relative voltage change and duration.

        Returns
        -------
        tuple of (float, int)
            The relative voltage change and time difference (in steps)
            across the monitored time window.
        """
        v_values = [tv.value for tv in self.time_voltages]
        t_dist = self.time_voltages[-1].time - self.time_voltages[0].time
        v_change = round(abs(max(v_values) - min(v_values)) / v_values[0], 6)
        return v_change, t_dist

    def _try_enable_storage(self) -> bool:
        """Attempt to re-enable the storage unit and run powerflow.

        Returns
        -------
        bool
            True if powerflow converged with the unit enabled,
            False if enabling fails and is rolled back.
        """
        self.grid.set_value(self.etype, self.index, "in_service", True)
        try:
            self.grid.run_powerflow()
            return True
        except pp.LoadflowNotConverged:
            self.grid.set_value(self.etype, self.index, "in_service", False)
            try:
                self.grid.run_powerflow()
            except pp.LoadflowNotConverged:
                pass
            return False

    def _finalize_state_change(
        self, time: int, old_state: bool, voltage: float
    ) -> None:
        """Run powerflow and log info if the service state changed.

        Parameters
        ----------
        time : int
            Current time step.
        old_state : bool
            Service status before this step.
        voltage : float
            Voltage before potential reactivation.
        """
        if old_state != self.in_service:
            self._log_storage_status(time, voltage)
            try:
                self.grid.run_powerflow()
            except pp.LoadflowNotConverged:
                LOG.debug(
                    "%s %s. PF not converging.",
                    self.etype,
                    "re-enabled" if self.in_service else "disabled",
                )
        elif not old_state:
            LOG.debug("%s %d could not be re-enabled.", self.etype, self.index)
            try:
                self.grid.run_powerflow()
            except pp.LoadflowNotConverged:
                pass

    def _log_storage_status(self, time: int, voltage: float) -> None:
        """Log debug messages about storage state transitions.

        Parameters
        ----------
        time : int
            Current simulation time step.
        voltage : float
            Voltage at the time of logging.
        """
        if not self.in_service:
            LOG.debug(
                "At step %d: %s %d with p=%.5f and q=%.5f out of service"
                " (Bus voltage: %.5f)",
                time,
                self.etype,
                self.index,
                self.p_mw,
                self.q_mvar,
                self.current_bus_voltage,
            )
        else:
            LOG.debug(
                "At step %d: %s %d back in service.",
                time,
                self.etype,
                self.index,
            )
