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


import unittest
import sys
import os
import cv2

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.tracking import _create_tracker

class TestTrackingLogic(unittest.TestCase):

    def test_opencv_version(self):
        print(f"\nVersão do OpenCV detectada: {cv2.__version__}")
        self.assertIsNotNone(cv2.__version__)

    def test_create_tracker_csrt(self):
        try:
            tracker = _create_tracker("CSRT")
            self.assertIsNotNone(tracker, "O tracker CSRT não deve ser None")
        except AttributeError:
            self.fail("Erro: Tracker CSRT não encontrado. Verifique se 'opencv-contrib-python' está instalado.")

    def test_create_tracker_kcf(self):
        tracker = _create_tracker("KCF")
        self.assertIsNotNone(tracker)

    def test_invalid_tracker(self):
        with self.assertRaises(RuntimeError):
            _create_tracker("TRACKER_QUE_NAO_EXISTE")

if __name__ == '__main__':
    unittest.main()