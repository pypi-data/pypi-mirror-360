"""Parser for HiPER multichip data
"""

import logging

import numpy as np

from naludaq.helpers.exceptions import BadDataError
from naludaq.parsers.headers import get_header_parser

LOGGER = logging.getLogger("naludaq.parsers.hiper")


# check for chips in data. GEt the location on the first of each of the chips
# Multi-cip functions
class HiperParser:
    """Class to repackage HiPER multichip data.

    Use instead of the normal packager
    """

    def __init__(self, params):
        self.params = params

        # TODO(Marcus): Replace with aardvarc header parser
        self._parse_event_headers = get_header_parser(self.params["model"])

        # TODO(Marcus): connect all the params to the input.
        self.test_amount_windows = 3
        self.samples = self.params.get("samples", 64)
        self.windows = self.params.get("windows", 512)
        self.channels = self.params.get("channels", 4)
        self.num_evt_headers = self.params.get("num_evt_headers", 3)
        self.num_channel_headers = self.params.get("num_channel_headers", 1)
        self.num_window_headers = self.params.get("num_window_headers", 1)
        self.data_bitmask = self.params.get("data_bitmask", 8191)
        self.chanmask = self.params.get("chanmask", 3072)
        self.windmask = self.params.get("windmask", 1022)
        self.chanshift = self.params.get("chanshift", 10)
        # self.num_footer_words = self.params.get("num_footer_words", 2)
        # self.last_bits = self.params.get("lastbits", 1)
        self.chan_step_size = self.samples + self.num_channel_headers
        self.chips = 14
        self.channels_per_chip = 4
        self.channels = self.channels_per_chip * self.chips
        self.samples = 64
        self.splitwords = {
            bytes.fromhex(f"bbb{hex(x)[2:]}"): bytes.fromhex(f"fff{hex(x)[2:]}")
            for x in range(self.chips)
        }

        self._valid_splits = []

    @property
    def valid_splits(self):
        return self._valid_splits

    @valid_splits.setter
    def valid_splits(self, splits):
        self._valid_splits = []
        for spl in splits:
            self._valid_splits.append(bytes.fromhex(f"bbb{hex(spl)[2:]}"))

    def _validate_input_package(self, in_data):
        """Validate the input data.
        Raises:
            BadDataException if:
            - there is no data.
            - there is not a en event amount of bytes, since 8-bits are combined to 16-bit words.
            - the data is not divisable by sample_num + window_headers.
        """
        # if not isinstance(in_data, dict):
        #     raise TypeError("raw_data is not a dict it's a %s", type(in_data))

        # if in_data['rawdata'] == b"":
        #     raise BadDataError('No Data Found')

        # # Edge case, data doesn't contain valid words.
        # if len(in_data['rawdata']) % 2 != 0:
        #     raise BadDataError(
        #         f"Bad package no {in_data.get('pkg_num', 'unknown')}, "
        #         f"length is not an even amount of words, "
        #         f"len {len(in_data['rawdata'])}"
        #     )

    def parse(self, indata):
        """Takes a set of binary data and split&parse it to events"""
        # data["rawdata"][0:24].hex()
        if indata.get("rawdata", None):
            data = indata["rawdata"]
        else:
            raise BadDataError("Datapackage is invalid")
        output = []

        if not self.valid_splits:
            valid_splits = self._check_for_chips(data)
        else:
            valid_splits = self.valid_splits
        # print(f"valid splits: {valid_splits}")
        if valid_splits:
            split_data = self.split_data_into_packs(data, valid_splits[0])
        else:
            split_data = [indata["rawdata"]]
        # print(f"Len of data: {len(split_data)}")
        # put in foor loop
        all_chippacks = []
        for idx, split in enumerate(split_data):
            # print(f"Len of split: {len(split)}")
            all_chippacks.append(self.split_packs_into_chippacks(split, valid_splits))

        # this needs to be done in a loop too:

        for chippack in all_chippacks:
            # print(f"Len of chippack: {len(chippack)}")
            eventpack = self.split_chippacks_into_events(chippack)
            self.parse_eventpacks(eventpack, output)
        # print(f"Parsed package: {output[0]}")
        try:
            output[0]["event_num"] = indata["pkg_num"]
            return output[0]
        except Exception:
            indata["event_num"] = indata["pkg_num"]
            return indata

    def _check_for_chips(self, idata) -> list:
        """Checks which chips are present in the data.
        Args:
        Returns:
            the (start,end) string tuple for the available chips.
        """
        p = -1
        valid_splits = []
        for spl, _ in self.splitwords.items():
            p = idata.find(spl)
            if p != -1:
                valid_splits.append(spl)
        return valid_splits

    def _extract_chipnum(self, data: bytearray) -> str:
        """Extract the hex chipnum from data"""
        return data[0:2].hex()[-1]

    # Find all splits for the first chip available, creating the packs with events
    # each following chip will contain the following pieces of the events.
    def split_data_into_packs(self, idata, splitword):
        """Takes all the indata and splits into packs
        A pack is from the header of the first(lowest number) chip until it's found again.
        Args:
            idata: All captured data.
            splitword: header of the lowest numbered chip
        Returns:
            list of packs to process.
        """
        splits = []
        running = True
        p = idata.find(splitword)
        while running:
            p2 = idata.find(splitword, p + 1)
            if p2 == -1:
                p2 = len(idata)
                running = False
            splits.append(idata[p:p2])
            p = p2
        return splits

    # for each pack, extract the data for each chip
    # that extracted data will later be reassembled into events.
    # Split the pack
    def split_packs_into_chippacks(self, datpack, splitwords):
        chippacks = []
        for splitstart in splitwords:
            splitend = self.splitwords[splitstart]
            p = datpack.find(splitstart)
            p2 = datpack.find(splitend)
            if p != -1 and p2 != -1:
                chippacks.append(datpack[p:p2])

        return chippacks

    # split chippack into events
    def split_chippacks_into_events(self, chippacks):
        """Split the chippacks into individual events
        The events are then stored in a dict with their chip number for reassebly.
        Args:
            all_chippacks (list[list]): All chippacks in a list, each list in the list contains data from all each chip.
        Returns:
            {chipnum(hex): [events]}
        """
        event_footer = bytes.fromhex("a5af5afc3c3c")
        eventpack = {
            hex(x)[2:]: [] for x in range(self.chips)
        }  # TODO: Not needed parse and reassmeble in one step

        for idx, chip in enumerate(chippacks):
            # extract chip number
            try:
                chipnum = self._extract_chipnum(chip)
            except Exception:
                LOGGER.error(
                    f"Failed, failing idx: {idx}/{len(chippacks)}, data: {chip}"
                )
            # split the events
            events = [
                x[2:] for x in chip.split(event_footer) if len(x) > 0
            ]  # OR always toss last piece? either incomplete data or no data? IMPORTANT! FIGURE OUT!

            eventpack[chipnum] = events

        eventpack = {k: v for k, v in eventpack.items() if len(v) > 0}
        return eventpack

    # parse the data
    def parse_eventpacks(self, eventpack, output):
        """Parses eventpacks into deque of events"""
        idx = 0

        while True:
            event = {}
            for k in eventpack.keys():
                try:
                    next_pack = eventpack[k][idx]
                except Exception:
                    continue
                else:
                    try:
                        event = self.parse_digital_data(next_pack, k, event)
                    except Exception as e:
                        LOGGER.error(f"Parsing data failed: {e}")
                        continue
                    event["time"] = self._add_xaxis_to_event(event)

            if not event:
                break
            output.append(event)
            idx += 1

    def parse_digital_data(self, in_data, chipid, event={}):
        """Print the header for each end every word in the data.
        Warning, long list...
        Args:
            data (np.array or list): all the data, not multi dimensional so one channel at the time.
        """
        # TODO(Marcus): Need logic for the different channels. Since this needs to be processed from readout data.
        self.samples
        chipchannels = self.channels_per_chip
        self.chips
        chipid = int(chipid, 16)
        channels = self.channels

        hex_data = in_data.hex()
        header_len = 9
        stepsize = 65 * 3
        split_word = "FC3C3C"
        readout_data = hex_data[header_len:]
        if not event:
            event = {
                "header": hex_data[:header_len],
                "data": [[] for _ in range(channels)],
                "window_labels": [[] for _ in range(channels)],
                "start_window": int(readout_data[0:3], 16) & (2**7 - 1),
            }

        for block in readout_data.upper().split(split_word):
            # chip_header = block[:4]

            for idx in range(0, len(block) - stepsize, stepsize):
                header = block[idx : idx + 3]
                chan = (int(header, 16) >> 9) & 3
                channel = (chipid * chipchannels) + chan
                window = int(header, 16) & (2**7 - 1)
                pack = block[idx + 3 : idx + stepsize]
                windata = [self._hex_comb(x, pack) for x in range(0, len(pack), 3)]

                event["data"][channel].extend(windata)
                event["window_labels"][channel].append(window)
        event["start_window"]
        # event['data'] = np.array(event['data'])
        event["event_num"] = 0

        return event

    @staticmethod
    def _hex_comb(index, data):
        """Combines hexnibbles into 12bit data"""
        outp = (
            (int(data[index], 16) << 8)
            | (int(data[index + 1], 16) << 4)
            | (int(data[index + 2], 16))
        )
        return outp

    def _add_xaxis_to_event(self, event):
        """Adds an x-axis to the data.
        Based on the amount of channels and samples it will add a timeaxis
        per channel to the event dict.
        Returns:
            numpy array with sample numbers for each channel.
        """
        times = list()
        samples = self.samples
        channels = self.channels
        start_window = event["start_window"]
        for chan in range(0, channels):
            # LOGGER.debug("winds=%s", event["window_labels"][chan])
            winds = np.array(event["window_labels"][chan])
            winds += self.windows * (winds < start_window)
            winds -= start_window

            tim = (samples * np.repeat(winds, samples)) + (
                np.ones((len(winds), samples), dtype=int)
                * np.arange(0, samples, dtype=int)
            ).flatten()

            times.append(tim)

        return times
