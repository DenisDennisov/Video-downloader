from unittest import TestCase

from PyQt5 import QtWidgets

from src.GUI import MainWindow


class TestMainWindow(TestCase):
    """ Test class MainWindow. """

    def test_main_window_initialization(self):
        app = QtWidgets.QApplication([])
        main_window = MainWindow()
        self.assertIsNotNone(main_window)
        app.quit()
