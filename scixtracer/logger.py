"""Set of classes to log program state """
from abc import ABC
from abc import abstractmethod
from pathlib import Path

COLOR_WARNING = '\033[93m'
COLOR_ERROR = '\033[91m'
COLOR_GREEN = '\033[92m'
COLOR_ENDC = '\033[0m'


class SLoggerInterface(ABC):
    """Default logger

    A logger is used to print the warnings, errors and progress.
    A logger can be used to print in the console or in a log file

    """
    def __init__(self):
        self.prefix = ''

    @abstractmethod
    def new_line(self):
        """Print a new line in the log"""
        raise NotImplementedError()

    @abstractmethod
    def info(self, message: str):
        """Log a any information

        :param message: Message to log
        """
        raise NotImplementedError()

    @abstractmethod
    def error(self, message: str):
        """Log an error message

        :param message: Message to log
        """
        raise NotImplementedError()

    @abstractmethod
    def warning(self, message: str):
        """Log a warning

        :param message: Message to log
        """
        raise NotImplementedError()

    @abstractmethod
    def progress(self, iteration: int, total: int, prefix: str, suffix: str):
        """Log progress

        :param iteration: Current iteration
        :param total: Total number of iteration
        :param prefix: Text to print before the progress
        :param suffix: Text to print after the message
        """
        raise NotImplementedError()

    @abstractmethod
    def close(self):
        """Close the logger"""
        raise NotImplementedError()


class SLogger:
    """Observable pattern

    This pattern allows to set multiple progress logger to
    one app

    """
    def __init__(self):
        self._loggers = []

    def set_prefix(self, prefix: str):
        """Set the prefix for all loggers

        The prefix is a printed str at the beginning of each line

        :param prefix: Prefix content
        """
        for logger_ in self._loggers:
            logger_.prefix = prefix

    def add_logger(self, logger_interface: SLoggerInterface):
        """Add a logger to the observer

        :param logger_interface: Logger to add to the observer
        """
        self._loggers.append(logger_interface)

    def new_line(self):
        """Print a new line in the loggers"""
        for logger_ in self._loggers:
            logger_.new_line()

    def info(self, message: str):
        """Log a default message

        :param message: Message to log
        """
        for logger_ in self._loggers:
            logger_.info(message)

    def error(self, message: str):
        """Log an error message

        :param message: Message to log
        """
        for logger_ in self._loggers:
            logger_.error(message)

    def warning(self, message: str):
        """Log a warning message

        :param message: Message to log
        """
        for logger_ in self._loggers:
            logger_.warning(message)

    def progress(self, iteration: int, total: int, prefix: str, suffix: str):
        """Log progress

        :param iteration: Current iteration
        :param total: Total number of iteration
        :param prefix: Text to print before the progress
        :param suffix: Text to print after the message
        """
        for logger_ in self._loggers:
            logger_.progress(iteration, total, prefix, suffix)

    def close(self):
        """Close the loggers"""
        for logger_ in self._loggers:
            logger_.close()


class SFileLogger(SLoggerInterface):
    """Logger to write logs into txt file

    :param filepath: Path of the log file
    """
    def __init__(self, filepath: Path):
        super().__init__()
        with open(filepath, 'a', encoding="utf8") as file:
            self.file = file

    def new_line(self):
        self.file.write(f"{self.prefix}:\n")

    def info(self, message):
        self.file.write(f'{self.prefix}: {message}\n')

    def error(self, message):
        self.file.write(f'{COLOR_ERROR}{self.prefix} ERROR: '
                        f'{message}{COLOR_ENDC}\n')

    def warning(self, message):
        self.file.write(f'{COLOR_WARNING}{self.prefix} WARNING: '
                        f'{message}{COLOR_ENDC}\n')

    def progress(self, iteration, total, prefix, suffix):
        self.file.write(f'{prefix}: iteration '
                        f'{iteration}/{total} ({suffix})\n')

    def close(self):
        self.file.close()


class SConsoleLogger(SLoggerInterface):
    """Console logger displaying a progress bar

    The progress bar displays the basic information of a batch loop (loss,
    batch id, time/remaining time)

    """
    def __init__(self):
        super().__init__()
        self.decimals = 1
        self.print_end = "\r"
        self.length = 100
        self.fill = '█'

    def new_line(self):
        print(f"{self.prefix}:\n")

    def info(self, message):
        print(f'{self.prefix}: {message}')

    def error(self, message):
        print(f'{COLOR_ERROR}{self.prefix} ERROR: '
              f'{message}{COLOR_ENDC}')

    def warning(self, message):
        print(f'{COLOR_WARNING}{self.prefix} WARNING: '
              f'{message}{COLOR_ENDC}')

    def progress(self, iteration, total, prefix, suffix):
        percent = ("{0:." + str(self.decimals) + "f}").format(
            100 * (iteration / float(total)))
        filled_length = int(self.length * iteration // total)
        bar_ = self.fill * filled_length + ' ' * (self.length - filled_length)
        print(f'\r{prefix} {percent}% |{bar_}| {suffix}',
              end=self.print_end)

    def close(self):
        pass


__LOGGER = None


def logger() -> SLogger:
    """Retrieve the logger"""
    global __LOGGER  # pylint: disable=W0603

    if __LOGGER is None:
        __LOGGER = SLogger()
        __LOGGER.add_logger(SConsoleLogger())

    return __LOGGER
