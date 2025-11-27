# src/io/paths.py

"""
Utilitários de caminho para o app-metric.

Objetivo:
- Centralizar a lógica de onde ficam as pastas de dados (raw, processed, results, logs).
- Evitar ficar espalhando `os.path.join(...)` hard-coded pelo projeto.
"""

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
