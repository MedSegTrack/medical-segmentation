import os
import unittest
import sys
from model.data_manager import DataManager

# from gui.controller import GuiController
from gui.guicontroller import GUIController
from gui.guiview import GUI
from PyQt5.QtWidgets import QApplication
from qt_material import apply_stylesheet

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "test")))


def run_tests():
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir="test", pattern="test_*.py")
    runner = unittest.TextTestRunner()
    runner.run(suite)


def main():
    app = QApplication(sys.argv)

    # Create components
    data_manager = DataManager()
    view = GUI()
    GUIController(data_manager, view)
    apply_stylesheet(app, theme="dark_blue.xml")

    view.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    # run_tests()
    main()
