import logging


class CustomFormatter(logging.Formatter):
    def format(self, record):
        # Add prefix to warning messages
        if record.levelno == logging.INFO:
            record.levelname = '🔹 ' + record.levelname
        elif record.levelno == logging.WARNING:
            record.levelname = '🔸 ' + record.levelname
        # Add prefix to debug messages
        elif record.levelno == logging.DEBUG:
            record.levelname = '😈 ' + record.levelname
        elif record.levelno == logging.ERROR:
            record.levelname = '🆘 ' + record.levelname
        elif record.levelno == logging.FATAL:
            record.levelname = '🥊 ' + record.levelname
        return super().format(record)


formatter = CustomFormatter('%(levelname)s')
