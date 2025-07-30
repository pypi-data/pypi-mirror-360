import logging

from midas_powergrid.constraints.storage import PPStorage

LOG = logging.getLogger(__name__)


class PPLoad(PPStorage):
    def __init__(self, index, grid, value=0.02):
        super().__init__(index, grid, value, "load")

        LOG.debug(
            "Loading constraint for load %d with value %.2f", index, value
        )
