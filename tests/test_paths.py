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
Este arquivo contém os testes unitários responsáveis por validar a lógica de 
gerenciamento de caminhos e diretórios do projeto. 
Ele verifica se a raiz do projeto é identificada corretamente e se as pastas 
essenciais de dados ('raw' e 'results') são criadas e acessíveis. 
Isso garante que o software consiga ler os vídeos de entrada e salvar os 
relatórios de saída no local correto, independente do computador onde for executado.
'''
#################


import unittest
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.io.paths import get_project_root, get_data_dir

class TestPaths(unittest.TestCase):

    def test_project_root_exists(self):
        root = get_project_root()
        self.assertTrue(root.exists())
        self.assertTrue((root / "src").exists())

    def test_data_dirs_creation(self):
        raw_dir = get_data_dir("raw")
        results_dir = get_data_dir("results")

        self.assertTrue(raw_dir.exists())
        self.assertTrue(results_dir.exists())
        self.assertTrue(str(raw_dir).endswith("raw"))

if __name__ == '__main__':
    unittest.main()