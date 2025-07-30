import logging
from collections import deque

from naludaq.helpers.exceptions import OperationCanceledError

logger = logging.getLogger("naludaq.operations")


class ProgressReporter:
    def __init__(self, *args, **kwargs):
        """Base class for operations that report progress."""
        super().__init__(*args, **kwargs)
        self._progress = []

    @property
    def progress(self):
        """Get/set the object that stores the progress updates.

        The object must have an 'append' method.
        """
        return self._progress

    @progress.setter
    def progress(self, value):
        if not hasattr(value, "append"):
            raise TypeError(
                "Progress updates are stored in an object with an 'append' method"
            )
        self._progress = value

    def update_progress(self, percent: float, message: str):
        """Updates the progress with a percent and message.

        Args:
            percent (float): the percent completion of the task
            message (str): a description of what is currently taking place
        """
        logger.debug("%s: %s | %s", type(self).__name__, percent, message)
        if isinstance(self.progress, (list, deque)):
            self.progress.append((percent, message))
        else:
            try:
                self.progress.update_status(percent, message)
            except:
                raise TypeError(
                    "Progress updates are stored in an object with an 'append' method"
                )


class CancelableOperation:
    def __init__(self, *args, **kwargs):
        """Base class for operations that can be canceled."""
        super().__init__(*args, **kwargs)
        self._canceled = False

    @property
    def canceled(self):
        """Get whether the operation has been canceled."""
        return self._canceled

    def cancel(self):
        """Cancel the operation."""
        self._canceled = True

    def _raise_if_cancelled(self):
        """Raises an OperationCanceledError if the operation has been canceled."""
        if self.canceled:
            raise OperationCanceledError()
