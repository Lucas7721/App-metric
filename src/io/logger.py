# src/io/logger.py

"""
Logger simples para o app-metric.

- Grava logs em data/results/logs/app_metric.log
- Também imprime no console (stdout) para debug.
"""

import logging
from logging import Logger
from .paths import get_data_dir

_LOGGER_CACHE = {}

def get_app_logger(name: str = "app_metric") -> Logger:

    if name in _LOGGER_CACHE:
        return _LOGGER_CACHE[name]

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False  

    logs_dir = get_data_dir("logs", create=True)
    log_file = logs_dir / "app_metric.log"

    fmt = logging.Formatter("[%(levelname)s][%(name)s] %(message)s")

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    _LOGGER_CACHE[name] = logger
    return logger
