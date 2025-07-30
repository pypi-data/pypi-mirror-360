"""Subpackage for software drivers used talk to devices on the board through I2C or SPI.

Examples of devices include temperature sensors and voltage monitors.
"""
from .eeprom import EEPROM
from .ltc2990 import LTC2990
