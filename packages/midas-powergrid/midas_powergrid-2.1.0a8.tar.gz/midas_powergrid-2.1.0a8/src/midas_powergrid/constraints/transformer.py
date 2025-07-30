import logging
from typing import TYPE_CHECKING

import numpy as np
import pandapower as pp

from midas_powergrid.constraints.base import GridElementConstraint

if TYPE_CHECKING:
    from ..model.pp_grid import PPGrid

LOG = logging.getLogger(__name__)


class PPTransformer(GridElementConstraint):
    """Represents a transformer in a power grid.

    PPTransformer manages the trafo element of the powergrid and
    tracks the number of changes of the tap_changer. When there are
    too many changes per hour, a change will be rejected.

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
    changes_per_hour : int
        Maximum number of changes allowed per hour.
    changes: dict[int, int]
        Contains the time and the value of changes that actually
        happen, i.e., that were not rejected by this element.
    tap_pos: int
        The current position of the tap_changer
    """

    def __init__(self, index, grid, value):
        self.grid: PPGrid = grid
        self.index: int = index
        self.etype: str = "trafo"
        self.res_etype: str = "res_trafo"

        self.changes_per_hour = value
        self.changes: dict[int, int] = {}
        self.tap_pos: int = 0

        LOG.debug(
            "Loading constraint for trafo %d with value %d", index, value
        )

    def step(self, time: int) -> bool:
        """Execute one simulation step for the transformer unit.

        Parameters
        ----------
        time : int
            Current simulation time step.

        Returns
        -------
        bool
            True if the service state changed during the step, False otherwise.
        """
        old_state = self.tap_pos
        self.tap_pos = self._get_tap()

        if old_state == self.tap_pos:
            return False

        self.changes[time] = self.tap_pos
        if self._check_tap_changes(time):
            return True

        self.changes.pop(time)

        self._try_run_powerflow(old_state)

        return False

    def _get_tap(self) -> int:
        """Return the tap position for this element.

        Handles possible errors and returns 0 if any error occurs.

        Returns
        -------
        int
            The tap position of this transformer
        """
        try:
            tap_pos = self.grid.get_value(self.etype, self.index, "tap_pos")
            if np.isnan(tap_pos):
                tap_pos = 0
        except KeyError:
            tap_pos = 0
        return int(tap_pos)

    def _check_tap_changes(self, time: int) -> bool:
        """Checks if the tap change constrained is violated.

        Parameter
        ---------
        time: int
            Current time in the simulation

        Returns
        -------
        bool
            True if the constraint is satisfied, False otherwise.
        """

        t_start = max(0, time - 3600)
        self.changes = {
            t: c for t, c in self.changes.items() if (t_start < t <= time)
        }
        return len(self.changes) <= self.changes_per_hour

    def _try_run_powerflow(self, pos: int) -> bool:
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
        self.grid.set_value(self.etype, self.index, "tap_pos", pos)
        self.tap_pos = pos
        try:
            self.grid.run_powerflow()
            return True
        except pp.LoadflowNotConverged:
            return False
