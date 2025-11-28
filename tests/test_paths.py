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

import unittest  # Importa o framework de testes unitários do Python
import sys  # Importa o módulo sys para manipulação de variáveis do sistema
import os  # Importa o módulo os para interação com o sistema operacional
from pathlib import Path  # Importa a classe Path para manipulação moderna de caminhos de arquivos

# Adiciona o diretório pai (raiz do projeto) ao sys.path para permitir importar módulos internos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importa as funções get_project_root e get_data_dir do módulo src.io.paths para serem testadas
from src.io.paths import get_project_root, get_data_dir

class TestPaths(unittest.TestCase):  # Define a classe de testes herdando de unittest.TestCase

    def test_project_root_exists(self):  # Define o teste para verificar a existência da raiz do projeto
        root = get_project_root()  # Chama a função que deve retornar o caminho da raiz do projeto
        self.assertTrue(root.exists())  # Verifica se o caminho retornado realmente existe no disco
        # Verifica se dentro da raiz existe a pasta 'src', confirmando que é a pasta correta do projeto
        self.assertTrue((root / "src").exists())

    def test_data_dirs_creation(self):  # Define o teste para verificar a criação das pastas de dados
        raw_dir = get_data_dir("raw")  # Solicita o caminho da pasta 'raw' (dados brutos)
        results_dir = get_data_dir("results")  # Solicita o caminho da pasta 'results' (resultados)

        self.assertTrue(raw_dir.exists())  # Verifica se a pasta 'raw' foi criada/existe
        self.assertTrue(results_dir.exists())  # Verifica se a pasta 'results' foi criada/existe
        # Verifica se o caminho da pasta 'raw' termina corretamente com o nome "raw"
        self.assertTrue(str(raw_dir).endswith("raw"))

if __name__ == '__main__':  # Verifica se o arquivo está sendo executado diretamente
    unittest.main()  # Executa todos os testes definidos na classe