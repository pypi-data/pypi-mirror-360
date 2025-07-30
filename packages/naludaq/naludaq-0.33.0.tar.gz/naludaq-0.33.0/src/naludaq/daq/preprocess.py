"""Preprocess raw data into events.

This module is used to convert raw data into a processed events.


"""
import logging
from copy import deepcopy

import numpy as np

from naludaq.helpers.exceptions import BadDataError
from naludaq.parsers import get_parser
from naludaq.tools.adc2mv.adc_converter import ADC2mVConverter
from naludaq.tools.pedestals.pedestals_correcter import PedestalsCorrecter
from naludaq.tools.timing_cal import TimingCorrecter

LOGGER = logging.getLogger(__name__)


class Preprocess:
    def __init__(self, board):
        """Proprocessor will convert raw events to preprocessed events

        Preprocessing includes parsing, pedestals correct, mV conversion, and timing calibration.

        Args:
            board: class object containing params, timingcal, pedestals, and/or adc2mvcal. This
                can also be an acquisition.
        """
        self.board = board

    @property
    def board(self):
        return self._board

    @board.setter
    def board(self, value):
        self._board = value
        self.params = getattr(value, "params", None)
        self.timingcal = getattr(value, "timingcal", None)
        self.pedestals = getattr(value, "pedestals", None)
        self.adc2mvcal = getattr(value, "caldata", None)
        self.samplingrate = self._get_samplerate()
        self.parser = get_parser(self.params)
        self.adc2mvconverter = ADC2mVConverter(self.params, self.adc2mvcal)
        self.pedestals_correcter = PedestalsCorrecter(self.params, self.pedestals)
        self.timing_correcter = TimingCorrecter(self.timingcal)

    def run(
        self,
        to_process: dict,
        correct_pedestals: bool = False,
        convert_adc2mv: bool = False,
        correct_timing: bool = False,
        convert_samples2time: bool = False,
        process_in_place: bool = False,
        correct_ecc: bool = False,
    ):
        """Process the raw event, parse and correct both x and y-axis

        Will parse raw data if no parsed exist.
        """
        if process_in_place is False:
            event = deepcopy(to_process)  # Sad copy to avoid overwriting event data
        else:
            event = to_process

        event = self._get_parsed_event(event, correct_ecc)
        event = self._correct_yaxis(event, correct_pedestals, convert_adc2mv)
        event = self._correct_xaxis(event, correct_timing, convert_samples2time)

        return event

    def _get_parsed_event(self, to_process, correct_ecc: bool = False):
        """Parse event if it doesn't contain parsed data.

        Will check the event for parsed data and parse it if there is none.
        Event is a dict with a rawdata and data fields.

        Args:
            to_process: event to try and parse

        Returns:
            parsed event with a 'data' key.

        Raises:
            Doesn't raises errors but will return unparsed if parsing fails.
        """
        event = to_process
        if "data" not in event:
            try:
                event = self.parser.parse(
                    to_process, check_ecc=correct_ecc, correct_ecc=correct_ecc
                )
            except (Exception, BadDataError) as e_msg:
                LOGGER.error("process_event didn't work due to %s", e_msg)
        return event

    def _correct_yaxis(self, event, correct_pedestals: bool, correct_mv: bool):
        """Convert and correct the values on the Y-axis.

        Can either pedestals correct Y-axis or convert ADC counts to mV.
        Future upgrade would allow both.

        ## Important:
        Currently ADC to mV will run before pedestals correction. This means if the pedestals
        correction and convert_mV are enabled at the same time ONLY mV convertion will run!.

        Args:
            event(dict): Must contain a `data` field
            correct_mv(bool): True to enable ADC to mV conversion.
            correct_pedestals(bool): True to pedestals correct
        """
        if correct_mv:
            event = self.adc2mvconverter.run(event)
        elif correct_pedestals and self.pedestals is not None:
            event = self.pedestals_correcter.run(event)
        return event

    def _correct_xaxis(self, event, correct_time: bool, convert_time: bool):
        """Convert and timing correct values on time axis"""
        if correct_time:
            event["time"] = self.timing_correcter.run(event)

        if convert_time:
            # event = TimeConverter(self.board.params).convert(event)
            event["time"] = self._convert_sp_to_ns(event)
        return event

    def _convert_sp_to_ns(self, event):
        """Convert the time field in the event from samples to time.

        Using the sampling rate parameter

        Args:
            event

        Returns:
            Event with converted time if there is a time key, else just the event
        """
        xaxis = np.array(event.get("time", None))
        samplerate = self.samplingrate
        # np.arrays can't directly be checked against None, use `==`
        if np.any(xaxis is None) or samplerate is None:
            return xaxis

        return xaxis / samplerate

    def _get_samplerate(self):
        """Quick access function to sampling rate params"""
        return self.params.get("samplingrate", None)
