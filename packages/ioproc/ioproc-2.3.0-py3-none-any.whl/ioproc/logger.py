#!/usr/bin/env python
# -*- coding:utf-8 -*-
import inspect
import logging
import logging.handlers
import pathlib as pt
import warnings


__author__ = [
    "Benjamin Fuchs",
]
__copyright__ = "Copyright 2020, German Aerospace Center (DLR)"
__credits__ = [
    "Felix Nitsch",
    "Judith Vesper",
    "Niklas Wulff",
    "Hedda Gardian",
    "Gabriel Pivaro",
    "Kai von Krbek",
]

__license__ = "MIT"
__maintainer__ = "Felix Nitsch"
__email__ = "ioProc@dlr.de"
__status__ = "Production"


class FancyLogger(logging.Logger):
    """
    This is a special logger, that by default (aka after calling self.setupDefault(PATH_TO_LOG_FILE))
    will have a stream handler and rotating file handler both set to DEBUG and a special format
    containing both the filename and line number of the logging call.
    """

    def info(self, *args, **kwargs):
        m = ["{}"] * len(args)
        m = (" ".join(m)).format(*args)
        super().info(m, **kwargs)

    def debug(self, *args, **kwargs):
        m = ["{}"] * len(args)
        m = (" ".join(m)).format(*args)
        super().debug(m, **kwargs)

    def error(self, *args, **kwargs):
        m = ["{}"] * len(args)
        m = (" ".join(m)).format(*args)
        super().error(m, **kwargs)

    def warn(self, *args, **kwargs):
        m = ["{}"] * len(args)
        m = (" ".join(m)).format(*args)
        super().warning(m, **kwargs)

    def warning(self, *args, **kwargs):
        m = ["{}"] * len(args)
        m = (" ".join(m)).format(*args)
        super().warning(m, **kwargs)

    def exception(self, *args, **kwargs):
        m = ["{}"] * len(args)
        m = (" ".join(m)).format(*args)
        super().exception(m, **kwargs)

    def log(self, level, *args, **kwargs):
        m = ["{}"] * len(args)
        m = (" ".join(m)).format(*args)
        super().log(level, m, **kwargs)

    def critical(self, *args, **kwargs):
        m = ["{}"] * len(args)
        m = (" ".join(m)).format(*args)
        super().critical(m, **kwargs)

    def _setLogRecordFactory(self):
        """
        Required to inject the correct line and file from which
        the logging call was emitted.
        :return: a valid record factory
        """
        old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)

            stack = inspect.stack()[5]

            record.filename = pt.Path(stack.filename).name
            record.lineno = stack.lineno
            return record

        logging.setLogRecordFactory(record_factory)

    def setupDefaultFormat(self):
        """
        Setup of the default output format for the logger.
        """
        self._setLogRecordFactory()
        fmt = logging.Formatter(
            "[{levelname:_<8}][{asctime}][{filename:_>15}][l.{lineno:>3}][{name}]: {msg}",
            style="{",
        )
        stream_fmt = logging.Formatter(
            "{msecs: >8}-[ioproc]: {msg}",
            style="{",
        )
        for ihandler in self.handlers:
            if isinstance(ihandler, logging.StreamHandler):
                ihandler.setFormatter(stream_fmt)
            else:
                ihandler.setFormatter(fmt)

        if len(self.handlers) == 0:
            warnings.warn(
                'no handler set for logger "{}". Call setupDefaultFormatter() _after_'
                "adding handlers or call setupDefault()"
            )

    def setupDefaultStreamHandlers(
        self,
        streamHandlerLevel=logging.DEBUG,
    ):
        """
        creates default file and stream handlers. File handler is a rotating one.
        :param fileHandlerPath: the path where files should be written to
        :param streamHandlerLevel: the log level for the console stream
        :param fileHandlerLevel: the log level for the log file
        """
        sh = logging.StreamHandler()
        sh.setLevel(streamHandlerLevel)
        self.addHandler(sh)
        self.setLevel(streamHandlerLevel)

    def setupDefaultFileHandlers(
        self,
        fileHandlerPath,
        fileHandlerLevel=logging.DEBUG,
    ):
        """
        creates default file and stream handlers. File handler is a rotating one.
        :param fileHandlerPath: the path where files should be written to
        :param fileHandlerLevel: the log level for the log file
        """
        fh = logging.handlers.RotatingFileHandler(fileHandlerPath)
        fh.setLevel(fileHandlerLevel)
        self.addHandler(fh)
        self.setLevel(fileHandlerLevel)

    def setupDefault(
        self,
        fileHandlerPath,
        streamHandlerLevel=logging.DEBUG,
        fileHandlerLevel=logging.DEBUG,
    ):
        """
        convenience method to create a default logger fully configured.
        :param fileHandlerPath: the path where files should be written to
        :param streamHandlerLevel: the log level for the console stream
        :param fileHandlerLevel: the log level for the log file
        """
        self.setupDefaultStreamHandlers(streamHandlerLevel)
        self.setupDefaultFileHandlers(fileHandlerPath, fileHandlerLevel)
        self.setupDefaultFormat()

    def setStrictLeve(self, level=logging.INFO):
        for i in self.handlers:
            i.setLevel(level)


logging.setLoggerClass(FancyLogger)

mainlogger = logging.getLogger("main")
mainlogger.setupDefaultStreamHandlers()
mainlogger.setupDefaultFormat()

datalogger = logging.getLogger("data")
datalogger.setupDefaultStreamHandlers()
datalogger.setupDefaultFormat()
