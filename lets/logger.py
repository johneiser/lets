"""

Logging can be done from anywhere using the global *log* object, whose
format has been customized to use symbols to represent the severity level
of each message.

.. code-block:: python

    from lets.logger import log

    log.debug("Something is about to happen")
    log.info("Something happened")
    log.warning("Something unexpected happened")
    log.error("Something unexpected happened and we are exiting")
    
Note that debug messages will only be shown to the user if the *verbose*
flag is set.

"""
import sys, logging
from unittest import TestCase

FORMAT = "[%(levelname)s] |%(module)s| %(message)s"

LEVEL_DEV = logging.NOTSET + 1

class SymbolFormatter(logging.Formatter):
    """
    Custom formatter which replaces log levels with symbols.

    :meta private:
    """
    # NOTSET(0), DEBUG(10), INFO(20), WARNING(30), ERROR(40), CRITICAL(50)
    symbols = [' ', '.', '+', '-', '!', 'x']

    def format(self, record):
        # Make copy of record
        r = logging.makeLogRecord(vars(record))

        # Swap names for symbols
        for i,s in enumerate(self.symbols):
            if r.levelno >= i * 10:
                r.levelname = s

        return super(SymbolFormatter, self).format(r)

# Configure global logger
log = logging.getLogger(__package__)
log.setLevel(LEVEL_DEV)
formatter = SymbolFormatter(FORMAT)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
log.addHandler(handler)

class LoggerTests(TestCase):
    """
    Ensure logger works as expected.

    :meta private:
    """