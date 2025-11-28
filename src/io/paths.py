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
Este módulo é responsável por centralizar e gerenciar todos os caminhos de diretórios do projeto.
Ele define funções utilitárias para localizar a raiz do projeto e garantir que as pastas de dados 
(como 'raw' para vídeos originais e 'results' para relatórios) existam e sejam acessíveis.
Isso evita o uso de caminhos absolutos (hard-coded), garantindo que o software funcione corretamente 
em qualquer sistema operacional ou computador.
'''
#################

from pathlib import Path  # Importa a classe Path para manipulação de caminhos de forma orientada a objetos
from typing import Literal  # Importa Literal para definir valores específicos permitidos em argumentos

def get_project_root() -> Path:  # Define função que retorna o caminho raiz do projeto
    # Retorna o diretório pai do pai do pai deste arquivo (sobe 3 níveis: io -> src -> Project)
    return Path(__file__).resolve().parents[2]

def get_data_dir(subdir: Literal["raw", "processed", "results", "logs"] = "results",  # Define função para obter subdiretórios de dados
                 create: bool = True) -> Path:  # Argumento opcional para criar a pasta se não existir

    root = get_project_root()  # Obtém a raiz do projeto
    data_dir = root / "data"  # Define o caminho da pasta 'data'

    if subdir == "logs":  # Se o subdiretório pedido for 'logs'
        path = data_dir / "results" / "logs"  # Define o caminho dentro de results/logs
    else:
        path = data_dir / subdir  # Para outros casos, define data/subdir

    if create:  # Se a flag de criação estiver ativa
        path.mkdir(parents=True, exist_ok=True)  # Cria a pasta e seus pais se necessário, sem erro se já existir

    return path  # Retorna o objeto Path do diretório

def get_timestamped_results_dir(prefix: str = "exec") -> Path:  # Função para criar pasta de resultados com data/hora

    from datetime import datetime  # Importa datetime localmente

    base_dir = get_data_dir("results", create=True)  # Obtém a pasta base de resultados
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")  # Gera timestamp atual
    result_dir = base_dir / f"{prefix}_{ts}"  # Cria nome da nova pasta com prefixo e timestamp
    result_dir.mkdir(parents=True, exist_ok=True)  # Cria a pasta no disco
    return result_dir  # Retorna o caminho da nova pasta
