# ===================================================================
# Cabeçalho do Programa
# Nome e RAs: Lucas Soares - 324155365, Robert Zica - 323112024, Leonardo Vieira - 323119033, Asafe Orneles - 324172578, Bruno Eduardo - 322123429
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

import logging  # Importa o módulo padrão de logging do Python
from logging import Logger  # Importa a classe Logger para tipagem
from .paths import get_data_dir  # Importa a função para obter o diretório de dados (onde os logs serão salvos)

_LOGGER_CACHE = {}  # Dicionário global para armazenar loggers já criados e evitar duplicação (padrão Singleton)

def get_app_logger(name: str = "app_metric") -> Logger:  # Define a função que retorna uma instância de Logger configurada

    if name in _LOGGER_CACHE:  # Verifica se um logger com esse nome já existe no cache
        return _LOGGER_CACHE[name]  # Se existir, retorna a instância cacheada para economizar recursos

    logger = logging.getLogger(name)  # Cria (ou recupera) um objeto logger com o nome fornecido
    logger.setLevel(logging.INFO)  # Define o nível mínimo de log como INFO (ignora DEBUG)
    logger.propagate = False  # Impede que os logs subam para o logger raiz (evita logs duplicados no console)

    logs_dir = get_data_dir("logs", create=True)  # Obtém o caminho da pasta de logs, criando-a se não existir
    log_file = logs_dir / "app_metric.log"  # Define o caminho completo do arquivo de log (app_metric.log)

    fmt = logging.Formatter("[%(levelname)s][%(name)s] %(message)s")  # Define o formato da mensagem: [NÍVEL][NOME] Mensagem

    fh = logging.FileHandler(log_file, encoding="utf-8")  # Cria um manipulador para escrever logs em arquivo (FileHandler)
    fh.setLevel(logging.INFO)  # Define que o arquivo registrará logs de nível INFO ou superior
    fh.setFormatter(fmt)  # Aplica o formato definido anteriormente ao arquivo
    logger.addHandler(fh)  # Adiciona o manipulador de arquivo ao logger

    ch = logging.StreamHandler()  # Cria um manipulador para escrever logs no console (StreamHandler)
    ch.setLevel(logging.INFO)  # Define que o console mostrará logs de nível INFO ou superior
    ch.setFormatter(fmt)  # Aplica o formato definido anteriormente ao console
    logger.addHandler(ch)  # Adiciona o manipulador de console ao logger

    _LOGGER_CACHE[name] = logger  # Salva o logger configurado no cache global
    return logger  # Retorna o objeto logger pronto para uso
