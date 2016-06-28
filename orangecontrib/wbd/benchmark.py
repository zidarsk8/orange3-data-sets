import time
import logging

logger = logging.getLogger(__name__)


class Benchmark(object):

    def __init__(self, message):
        self.message = message

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, exc_type, exc_value, exc_trace):
        end = time.time()
        logger.info("{:7.4f} {}".format(end - self.start, self.message))
