import sys, logging

from .utility import DEBUG

# Configure logging (WARNING+ -> stderr)
STREAM = sys.stderr
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO if DEBUG else logging.WARNING)
HANDLER = logging.StreamHandler(STREAM)
HANDLER.setLevel(logging.INFO if DEBUG else logging.WARNING)
LOGGER.addHandler(HANDLER)

class Logger(object):
    """
    Logging mixin class, enabling logging functionality across modules.
    """
    _log_logger = LOGGER
    _log_handler = HANDLER
    _log_stream = STREAM

    class Exception(Exception):
        """
        Custom exception class to handle framework-specific errors.
        """
        @classmethod
        def throw(cls, e:object):
            """
            Handle an exception by throwing its contents.

            :param e: Exception which was caught
            """
            raise(cls("%s: %s" % (e.__class__.__name__, str(e))))

    def throw(self, e:object):
        """
        Handle an exception by throwing its contents in relation to its originating
        object.

        :param e: Exception which was caught
        """
        raise(self.Exception("|%s| %s: %s" % (self.__class__.__name__, e.__class__.__name__, str(e))))

    def info(self, message:str, decorate:bool=True) -> None:
        """
        Log an INFO message (only printed with the `verbose` flag set).

        :param message: Message to log
        :param decorate: Choose to include decoration
        """
        if decorate:
            message = "[+] |%s| %s" % (self.__class__.__name__, message)
        logging.info(message)

    def warn(self, message:str, decorate:bool=True, confirm:bool=False) -> None:
        """
        Log a WARNING message.

        :param message: Message to log
        :param decorate: Choose to include decoration
        :param confirm: Choose to confirm with user before proceeding
        """
        if decorate:
            message = "[-] |%s| %s" % (self.__class__.__name__, message)
        if confirm:
            message = "%s [Press Enter to continue]" % message
        logging.warning(message)
        if confirm:
            input()

    def error(self, message:str, decorate:bool=True, confirm:bool=False) -> None:
        """
        Log an ERROR message.

        :param message: Message to log
        :param decorate: Choose to include decoration
        :param confirm: Choose to confirm with user before proceeding
        """
        if decorate:
            message = "[!] |%s| %s" % (self.__class__.__name__, message)
        if confirm:
            message = "%s [Press Enter to continue]" % message
        logging.error(message)
        if confirm:
            input()