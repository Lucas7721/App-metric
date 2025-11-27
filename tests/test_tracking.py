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