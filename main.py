import sys
from PyQt5.QtWidgets import QApplication
from gui.controller import GuiController
from gui.filehandler import FileHandler
from gui.view import GuiView


if __name__ == "__main__":
    app = QApplication(sys.argv)

    file_handler = FileHandler()
    view = GuiView()
    controller = GuiController(file_handler, view)

    view.show()
    sys.exit(app.exec_())