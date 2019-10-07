# -*- coding: utf-8 -*-
"""
created on 18/12/2018 14:59
@author: fgiely
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime
import os


class Logger:
    def __init__(self, path, log_level="ERROR"):
        if not os.path.exists(path):
            os.mkdir(path)
        now = datetime.now()
        self._path = (
            path
            + "/"
            + str(now.year)
            + "_"
            + str(now.month)
            + "_"
            + str(now.day)
            + ".log"
        )
        self._error_creating_log = None

        self._log_level = logging.getLevelName(log_level)
        self.logger = logging.getLogger()
        self.logger.setLevel(self._log_level)

        formatter = logging.Formatter("%(asctime)s :: %(levelname)s :: %(message)s")
        self._file_handler = RotatingFileHandler(
            self._path, "a", 1000000, 1, encoding="utf-8"
        )

        self._file_handler.setLevel(self._log_level)
        self._file_handler.setFormatter(formatter)
        self.logger.addHandler(self._file_handler)

        self.logger_stdout = logging.getLogger()
        self.logger_stdout.setLevel(self._log_level)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s :: %(levelname)s :: %(message)s")

        handler.setLevel(self._log_level)
        handler.setFormatter(formatter)
        self.logger_stdout.addHandler(handler)

    def __del__(self):
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
