import logging
from typing import TYPE_CHECKING

import numpy as np
import pandapower as pp

from midas_powergrid.constraints.base import GridElementConstraint

if TYPE_CHECKING:
    from midas_powergrid.model.pp_grid import PPGrid

LOG = logging.getLogger(__name__)


class PPBus(GridElementConstraint):
    """Represents a bus in a power grid.

    PPBus manages its connected elements (loads, static generators, and
    storages) based on voltage constraints.

    Attributes
    ----------
    index : int
        Index of the bus in the grid.
    grid : PPGrid
        Reference to the grid model.
    vm_pu_min : float
        Minimum acceptable per-unit voltage.
    vm_pu_max : float
        Maximum acceptable per-unit voltage.
    etype : str
        Element type identifier ("bus").
    res_etype : str
        Result table identifier for voltage values.
    over_voltage : bool
        True if the bus voltage is above the maximum threshold.
    under_voltage : bool
        True if the bus voltage is below the minimum threshold.
    in_service : bool
        Current service state of the bus.
    vm_pu : float
        Current per-unit voltage at the bus.
    loads_is : bool
        Service state of connected loads.
    sgens_is : bool
        Service state of connected static generators.
    storages_is : bool
        Service state of connected storages.
    load_indices : list[int]
        Indices of loads connected to this bus.
    sgen_indices : list[int]
        Indices of static generators connected to this bus.
    storage_indices : list[int]
        Indices of storages connected to this bus.
    """

    def __init__(self, index, grid, value):
        self.grid: PPGrid = grid
        self.index: int = index
        self.vm_pu_min: float = 1.0 - value
        self.vm_pu_max: float = 1.0 + value
        self.etype: str = "bus"
        self.res_etype: str = "res_bus"
        self.over_voltage: bool = False
        self.under_voltage: bool = False

        self.in_service: bool = grid.get_value(self.etype, index, "in_service")
        self.vm_pu: float = grid.get_value(self.res_etype, index, "vm_pu")
        self.loads_is: bool = self.in_service
        self.sgens_is: bool = self.in_service
        self.storages_is: bool = self.in_service

        self.load_indices: list[int] = self._get_element_indices("load")
        self.sgen_indices: list[int] = self._get_element_indices("sgen")
        self.storage_indices: list[int] = self._get_element_indices("storage")

    def step(self, time: int) -> bool:
        """Perform a simulation step of this constraint.

        Advance the simulation one step and update bus service state
        based on voltage constraints and load flow convergence.

        Parameters
        ----------
        time : int
            Current simulation time step.

        Returns
        -------
        bool
            True if the bus service state changed; False otherwise.
        """
        old_state = self.in_service

        if old_state:
            self._check_constraint()

            # Was enabled before but now constraint is violated
            if not self.under_voltage and not self.over_voltage:
                # Everything is fine
                return False
            else:
                self.in_service = False

            if self.over_voltage:
                self.set_sgen_service_state(in_service=False)
            if self.under_voltage:
                self.set_load_service_state(in_service=False)

            converged = self._try_powerflow()

            if converged:
                self._check_constraint()

            if not converged or self.over_voltage or self.under_voltage:
                # Disable storages as well and see what happens
                self.set_storage_service_state(in_service=False)
                converged = self._try_powerflow()
                self._check_constraint()
        else:
            # Was off; but can switch on now?
            self.set_load_service_state(in_service=True)
            self.set_sgen_service_state(in_service=True)
            self.set_storage_service_state(in_service=True)

            converged = self._try_powerflow()
            if converged:
                self._check_constraint()
            if not converged or self.over_voltage or self.under_voltage:
                # No, still violating the constraint or not converged
                self.set_load_service_state(in_service=False)
                self.set_sgen_service_state(in_service=False)
                self.set_storage_service_state(in_service=False)
                self._try_powerflow()
                self._check_constraint()
            else:
                # Everything works again
                self.in_service = True

        # Announce possible state changes
        if old_state != self.in_service:
            if not self.in_service:
                LOG.debug(
                    "At step %d: Bus %d out of service (vm_pu: %.3f)! "
                    "Disabling loads %s, sgens %s, and storages %s.",
                    time,
                    self.index,
                    self.vm_pu,
                    str(self.load_indices) if not self.loads_is else "[]",
                    str(self.sgen_indices) if not self.sgens_is else "[]",
                    str(self.storage_indices)
                    if not self.storages_is
                    else "[]",
                )

            else:
                LOG.debug(
                    "At step %d: Bus %d back in service!", time, self.index
                )

        return old_state != self.in_service

    def _check_constraint(self) -> None:
        """Check the constraints for this bus.

        Evaluate if the bus is within voltage constraints.
        Sets over_voltage and under_voltage flags.
        """
        self.vm_pu = self.grid.get_value(self.res_etype, self.index, "vm_pu")
        if np.isnan(self.vm_pu):
            # NaN usually means LF did not converge
            self.under_voltage = True
            self.over_voltage = True
        else:
            self.over_voltage = self.vm_pu > self.vm_pu_max
            self.under_voltage = self.vm_pu < self.vm_pu_min

    def _try_powerflow(self) -> bool:
        """Attempt to run the power flow.

        Returns
        -------
        bool
            True if the power flow converged, False otherwise.
        """
        try:
            self.grid.run_powerflow()
            return True
        except pp.LoadflowNotConverged:
            return False

    def set_load_service_state(self, in_service: bool) -> None:
        """Set the in-service status for all loads on the bus.

        Parameters
        ----------
        in_service : bool
            Desired service status.
        """
        for idx in self.load_indices:
            self.grid.set_value("load", idx, "in_service", in_service)
        self.loads_is = in_service

    def set_sgen_service_state(self, in_service: bool) -> None:
        """Set the in-service status for all generators on the bus.

        Parameters
        ----------
        in_service : bool
            Desired service status.
        """
        for idx in self.sgen_indices:
            self.grid.set_value("sgen", idx, "in_service", in_service)
        self.sgens_is = in_service

    def set_storage_service_state(self, in_service: bool) -> None:
        """Set the in-service status for all storages on the bus.

        Parameters
        ----------
        in_service : bool
            Desired service status.
        """
        for idx in self.storage_indices:
            self.grid.set_value("storage", idx, "in_service", in_service)
        self.storages_is = in_service

    def _get_element_indices(self, etype: str) -> list[int]:
        """Get list of indices for given etype.

        Return indices of elements of a given type connected to this bus.

        Parameters
        ----------
        etype : str
            Element type ("load", "sgen", or "storage").

        Returns
        -------
        list[int]
            List of indices connected to this bus.
        """
        return [
            int(idx)
            for idx, bus in zip(
                self.grid.get_element_values(etype).index.values,
                self.grid.get_element_attribute_values(etype, "bus").values,
            )
            if bus == self.index
        ]
