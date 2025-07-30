"""Legal stuff

"""
import copy
from logging import getLogger

import numpy as np

from naludaq.helpers.exceptions import BadDataError

LOGGER = getLogger(__name__)


class PedestalsCorrecter:
    """Pedestals correct

    Apply the pedestals correction to events and remove it later if necessary.
    Correct an event with previously generated pedestals or remove the correction.
    Removing the correction requires the pedestals to be stored.

    Attributes:
        params: dictionary with channel, windows, and samples
        pedestals

    """

    def __init__(self, params: dict = None, pedestals: dict = None):
        self.params = params
        self._pedestals = None
        self.pedestals = pedestals

    @property
    def pedestals(self):
        """Get/Set the pedestals for the parser to use.

        Can be set to None to run without subtraction.
        Doesn't raise an error if invalid pedestals, just sets the value to None.
        """
        return self._pedestals

    @pedestals.setter
    def pedestals(self, peds):
        if isinstance(peds, type(None)):
            self._pedestals = None
        else:
            shape = (
                self.params["channels"],
                self.params["windows"] * self.params["samples"],
            )
            channels = np.ones(shape=shape)
            for chan in range(self.params["channels"]):
                channels[chan] = np.concatenate(peds["data"][chan]).ravel()[0:]

            self._pedestals = channels

    def run(self, event: dict, correct_in_place: bool = True) -> dict:
        """Pedestals correct an event.

        The function assumes the board is carrying the pedestals,
        if there are no pedestals on the board just returns the event unchanged.

        Args:
            event (dict or object):
            correct_in_place (bool): Whether to directly modify the event
                passed to this function. If set to False, a deep copy is
                made and altered instead (this is much slower).

        Returns:
            event (dict or object) with pedestals corrected data.

        Raises:
            BadDataError if the event is bad.
        """
        if not correct_in_place:
            event = copy.deepcopy(event)

        if self.pedestals is None:
            return event

        if not isinstance(event, dict):
            raise BadDataError(f"Not a valid event, got type: {type(event)}")

        if "data" not in event.keys():
            LOGGER.debug("Event is not parsed, didn't contain a data field.")
            return event

        corr_event = self._correct_pedestals(event)

        return corr_event

    def _correct_pedestals(self, event) -> dict:
        """Subtracts pedestals from a raw event.

        Corrects te pedestals using numpy for a significant speed boost.
        The function modifies the supplied event.
        This function must be run before any further post-processing.

        Args:
            event(dict): Target to subtract pedestals from.
        """
        if "data" in event.keys():
            evtdata = event["data"]
            window_labels = event["window_labels"]

            event["data"] = self._create_pedestals_corrected_data(
                evtdata, window_labels
            )
            event["pedestals_corrected"] = True
        else:
            LOGGER.debug("Event does not contain a data field.")
        return event

    def _create_pedestals_corrected_data(self, evtdata, window_labels):
        """Correct the data with the board.pedestals

        By fetching the window labels from the pedestals and applying the data to
        the event the pedestals are corrected. The pedestals contains corrections
        for all samples in all windows.

        Args:
            evtdata (np.array): With the data to be corrected.
            window_labels (list): List of window labels to pedestal correct.

        Returns:
            Pedestals corrected data in the same shape and format as before
        """
        samples = self.params["samples"]
        channels = self.params["channels"]

        pedcorrected = list()

        for chan in range(channels):
            winds = window_labels[chan]
            num_winds = len(winds)
            if num_winds == 0:
                pedcorrected.append(np.array([], dtype="float"))
                continue

            ped_locs = (samples * np.repeat(winds, samples)) + (
                np.ones((num_winds, samples), dtype=int)
                * np.arange(0, samples, dtype=int)
            ).flatten()
            nan_mask = np.isnan(ped_locs)
            ped_locs_fixed = np.where(nan_mask, 0, ped_locs).astype(np.int64)
            p1 = self._pedestals[chan].take(ped_locs_fixed, mode="wrap")
            p1[nan_mask] = np.nan
            p2 = evtdata[chan]
            corrected = p2 - p1
            pedcorrected.append(corrected)

        pedcorrected = np.array(pedcorrected)

        return pedcorrected
