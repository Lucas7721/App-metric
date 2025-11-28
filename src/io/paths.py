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


from pathlib import Path
from typing import Literal

def get_project_root() -> Path:

    return Path(__file__).resolve().parents[2]

def get_data_dir(subdir: Literal["raw", "processed", "results", "logs"] = "results",
                 create: bool = True) -> Path:

    root = get_project_root()
    data_dir = root / "data"

    if subdir == "logs":
        path = data_dir / "results" / "logs"
    else:
        path = data_dir / subdir

    if create:
        path.mkdir(parents=True, exist_ok=True)

    return path

def get_timestamped_results_dir(prefix: str = "exec") -> Path:

    from datetime import datetime

    base_dir = get_data_dir("results", create=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_dir = base_dir / f"{prefix}_{ts}"
    result_dir.mkdir(parents=True, exist_ok=True)
    return result_dir
