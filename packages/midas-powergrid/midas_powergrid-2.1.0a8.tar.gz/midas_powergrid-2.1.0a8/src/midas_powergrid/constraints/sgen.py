import logging

from midas_powergrid.constraints.storage import PPStorage

LOG = logging.getLogger(__name__)


class PPSgen(PPStorage):
    def __init__(self, index, grid, value=0.02):
        super().__init__(index, grid, value, "sgen")

        LOG.debug(
            "Loading constraint for sgen %d with value %.2f", index, value
        )
