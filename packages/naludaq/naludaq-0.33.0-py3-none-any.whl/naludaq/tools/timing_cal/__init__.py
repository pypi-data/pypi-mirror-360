"""Timing calibration

Uses an array of 128 timing constants to correct the naluscopes timing.
The timing constants can be generated using a separate tool.

The timing constanst will correct the spacing between the samples.
The boards clock is broken down internally in the ASIC into 128 pieces, the
general asusmtion is that the clock feeding the chip can be considered exact since it feeds all
 parts equally. Thus the 128 spacing.

The timing calibration is a tool that corrects the ASICs internal timing jidder.
The internal timing jidder is aslo assumed to be constants over time, meaning it will not change
significant from one capture to the next. Once the timing constants have been generated they can
be saved and used indefinitely.
"""
from .calibration import TimingCalibration
from .correcter import TimingCorrecter
