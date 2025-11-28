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
Este arquivo contém os testes unitários responsáveis por validar as dependências 
de Visão Computacional e a lógica de criação dos rastreadores (Trackers). 
Ele verifica se a biblioteca OpenCV está instalada corretamente e se os algoritmos 
de rastreamento (CSRT e KCF), necessários para acompanhar o movimento dos objetos, 
estão disponíveis e funcionais no ambiente de execução.
'''
#################

import unittest  # Importa o módulo unittest para criar e executar testes unitários
import sys  # Importa o módulo sys para manipular variáveis do sistema, como o path
import os  # Importa o módulo os para interagir com o sistema operacional (caminhos de arquivos)
import cv2  # Importa a biblioteca OpenCV para visão computacional

# Adiciona o diretório pai (raiz do projeto) ao sys.path para permitir a importação dos módulos do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importa a função privada _create_tracker do módulo src.core.tracking para ser testada
from src.core.tracking import _create_tracker

class TestTrackingLogic(unittest.TestCase):  # Define a classe de teste que herda de unittest.TestCase

    def test_opencv_version(self):  # Define o método de teste para verificar a versão do OpenCV
        # Imprime a versão do OpenCV detectada no console para fins de debug
        print(f"\nVersão do OpenCV detectada: {cv2.__version__}")
        # Verifica se a versão do OpenCV não é None (ou seja, se foi importada corretamente)
        self.assertIsNotNone(cv2.__version__)

    def test_create_tracker_csrt(self):  # Define o método de teste para o tracker CSRT
        try:  # Inicia um bloco try para capturar possíveis erros
            tracker = _create_tracker("CSRT")  # Tenta criar um tracker do tipo CSRT
            # Verifica se o tracker criado não é None (ou seja, foi criado com sucesso)
            self.assertIsNotNone(tracker, "O tracker CSRT não deve ser None")
        except AttributeError:  # Captura erro de atributo caso o tracker não exista na versão instalada
            # Falha o teste explicitamente com uma mensagem útil sobre a dependência opencv-contrib-python
            self.fail("Erro: Tracker CSRT não encontrado. Verifique se 'opencv-contrib-python' está instalado.")

    def test_create_tracker_kcf(self):  # Define o método de teste para o tracker KCF
        tracker = _create_tracker("KCF")  # Cria um tracker do tipo KCF
        # Verifica se o tracker criado não é None
        self.assertIsNotNone(tracker)

    def test_invalid_tracker(self):  # Define o método de teste para verificar comportamento com tracker inválido
        # Usa o gerenciador de contexto assertRaises para verificar se uma exceção RuntimeError é lançada
        with self.assertRaises(RuntimeError):
            # Tenta criar um tracker com um nome que não existe, esperando que falhe
            _create_tracker("TRACKER_QUE_NAO_EXISTE")

if __name__ == '__main__':  # Verifica se o script está sendo executado diretamente
    unittest.main()  # Executa todos os testes definidos na classe