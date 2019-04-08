import logging

class Logger(object):
    """
    Logging mixin class, enabling logging functionality across modules.
    """

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

    def warn(self, message:str, decorate:bool=True) -> None:
        """
        Log a WARNING message.

        :param message: Message to log
        :param decorate: Choose to include decoration
        """
        if decorate:
            message = "[-] |%s| %s" % (self.__class__.__name__, message)
        logging.warning(message)

    def error(self, message:str, decorate:bool=True) -> None:
        """
        Log an ERROR message.

        :param message: Message to log
        :param decorate: Choose to include decoration
        """
        if decorate:
            message = "[!] |%s| %s" % (self.__class__.__name__, message)
        logging.error(message)