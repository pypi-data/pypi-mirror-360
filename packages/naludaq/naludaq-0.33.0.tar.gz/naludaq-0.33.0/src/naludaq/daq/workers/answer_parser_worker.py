"""Answer parser.

"""

from logging import getLogger
from threading import Thread

from naludaq.parsers.answer_parser import get_answer_parser

logger = getLogger(__name__)


class AnswerParserWorker(Thread):
    """Answer parser separates the answer and question id from raw data."""

    def __init__(self, input_buffer, output_buffer: dict, lock):
        super().__init__()
        self.running = True
        self.daemon = True
        self.input_buffer = input_buffer
        self.answers = output_buffer
        self.lock = lock
        self.answer_parser = get_answer_parser(True)

    def run(self):
        logger.debug("Trying to start packager.")
        self._worker_loop()

    def stop(self):
        self.running = False

    def _worker_loop(self):
        """Parse answers in the input buffer.

        Waits until an answer is available in the buffer.

        The parsed answers have a specific format.
        HHVVIIEE:
        HH - header
        VV - value
        II - command unique id
        EE - end word

        """
        answer_parser = self.answer_parser
        while self.running:
            buff = b""
            try:
                buff = self.input_buffer.get(block=True, timeout=1)

            except:
                # logger.error("answer_parser buff: %s", buff)
                continue
            else:
                buff_data = buff["rawdata"]

            if len(buff_data) != 8:
                logger.error(
                    "DAQ.answer_parser couldn't parse answer due  length of package, expected 8 got: %s",
                    len(buff_data),
                )
                continue

            try:
                answer = answer_parser(buff_data)

            except Exception as error_msg:
                logger.error(
                    "DAQ.answer_parser couldn't unpack answer due to %s", error_msg
                )
                continue

            with self.lock:
                logger.error(
                    "Fond a response: %s with id: %s", answer["value"], answer["cmd_id"]
                )
                self.answers[answer["cmd_id"]] = answer["value"]
