# ===================================================================
# Cabeçalho do Programa
# Nome e RAs: Lucas Soares - 324155365, Robert Zica - , Leonardo Vieira - 323119033, Asafe Orneles -, Bruno Eduardo - 
# Data: 27/11/2025
# Curso: Ciência da Computação
# Professor: EUZÉBIO D. DE SOUZA
# Trabalho: Detecção de Movimento usando Filtros Espaciais
# ===================================================================
# ANOTAÇÕES
# ===================================================================
'''
Este módulo implementa um sistema de logs centralizado para a aplicação.
Ele é responsável por registrar eventos importantes, erros e informações de debug
tanto no console quanto em arquivos de texto persistentes na pasta 'data/results/logs'.
Isso facilita o monitoramento da execução do software e a identificação de problemas
durante o uso ou desenvolvimento.
'''
#################


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
