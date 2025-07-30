import logging
from typing import TYPE_CHECKING

import numpy as np
import pandapower as pp

from midas_powergrid.constraints.base import GridElementConstraint

if TYPE_CHECKING:
    from midas_powergrid.model.pp_grid import PPGrid

LOG = logging.getLogger(__name__)


class PPLine(GridElementConstraint):
    """Represents a line in a power grid.

    PPLine manages the line element of the powergrid and disables
    it if necessary. It will also try to enable it again.

    Attributes
    ----------
    index : int
        Index of the bus in the grid.
    grid : PPGrid
        Reference to the grid model.
    etype : str
        Element type identifier ("line").
    res_etype : str
        Result table identifier for loading values.
    in_service : bool
        Current service state of the bus.
    max_percentage: float
        Maximum loading percentage of the line
    """

    def __init__(self, index, grid, value=100):
        self.grid: PPGrid = grid
        self.index: int = index
        self.etype: str = "line"
        self.res_etype: str = "res_line"

        self.in_service = True
        self.max_percentage = value
        LOG.debug("Loading constraint for line %d with value %d", index, value)

    def step(self, time: int) -> bool:
        """Execute one simulation step for the line unit.

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

        self.in_service = self._check_loading()

        if old_state == self.in_service:
            return False

        if old_state:
            # Switch off and run powerflow for next element
            self._try_run_powerflow(in_service=False)

        else:
            # Try to switch on and run powerflow
            if not self._try_run_powerflow(in_service=True):
                # Powerflow failed, so switch off again
                self._try_run_powerflow(in_service=False)
                self.in_service = False
                return False

            self.in_service = self._check_loading()
            if not self.in_service:
                self._try_run_powerflow(in_service=False)
                return False

        self._log_status(time)

        return True

    def _check_loading(self) -> bool:
        """Check if the loading constraint is violated.

        Returns
        -------
        bool
            True if constraint is not violated, False otherwise.
        """
        loading = self.grid.get_value(
            self.res_etype, self.index, "loading_percent"
        )
        if np.isnan(loading):
            # NaN occurs when LF fails or the line is not connected
            # It is assumed that there is no violation then
            return True
        else:
            return loading <= self.max_percentage

    def _try_run_powerflow(self, in_service: bool) -> bool:
        """Attempt to run the power flow.

        Sets the in_service flag to the given value and runs the
        powerflow calculation.

        Parameters
        ----------
        in_service: bool
            Desired service status

        Returns
        -------
        bool
            True if the power flow converged, False otherwise.
        """
        self.grid.set_value(self.etype, self.index, "in_service", in_service)

        try:
            self.grid.run_powerflow()
            return True
        except pp.LoadflowNotConverged:
            return False

    def _log_status(self, time: int) -> None:
        """Log debug messages about line state transitions.

        Parameters
        ----------
        time : int
            Current simulation time step.
        """
        if not self.in_service:
            LOG.debug("At step %d: Line %d out of service.", time, self.index)
        else:
            LOG.debug("At step %d: Line %d back in service.", time, self.index)
