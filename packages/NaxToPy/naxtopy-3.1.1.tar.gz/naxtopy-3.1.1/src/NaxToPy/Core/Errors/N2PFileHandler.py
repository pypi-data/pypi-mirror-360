import logging


# Clase wrapper de logging.Handler para añadir funcionalidades extra ---------------------------------------------------
class FileHandler(logging.Handler):
    """ Custom wrapper class for logging.Handler to substitute logging.FileHandler.

        By default log is active and log records are stored in attribute buffered_records but not
        written in the log file.

        By setting active to False the file log is turned off and all log records are ignored.
        By setting immediate to True log records are written in the log file and not stored.
    """

    def __init__(self, path: str, mode: str = 'a', encoding=None):
        super().__init__()
        self.path: str = path
        self.mode: str = mode
        self.encoding: None = encoding
        self.buffered_records: list = []
        self.active: bool = True
        self.immediate: bool = False

    def emit(self, record) -> None:
        """
        Overwrites emit method of logging.Handler.

        If active = True log records are considered. If False they are ignored.

        If immediate = False log records are stored in the attribute buffered_records.
        If immediate = True log records are not stored, but are directly output to the log file.
        """
        if self.active:
            self.buffered_records.append(record)
            if self.immediate:
                with open(self.path, self.mode, encoding=self.encoding) as file:
                    file.write(self.format(record) + '\n')

    def immediate_logging(self, immediate: bool = True) -> None:
        """
            Switches the logger from storing logs or writing them directly to the log file.
        """
        self.immediate = immediate

    def write_buffered_records(self) -> None:
        """
            Writes all log statements stored while immediate = False in buffered_records.
        """

        if self.active:

            with open(self.path, self.mode, encoding=self.encoding) as file:
                for record in self.buffered_records:
                    file.write(self.format(record) + '\n')
            self.buffered_records.clear()
