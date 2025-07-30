# Set default logging handler to avoid "No handler found" warnings.
import logging
from logging import NullHandler

from naludaq._version import __version__

from .naludaq import HiperDaq, NaluDaq, UpacDaq

logging.getLogger(__name__).addHandler(NullHandler())
