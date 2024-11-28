import sys
from PyQt5.QtWidgets import QApplication
from gui.controller import GuiController
from gui.model import GuiModel
from gui.view import GuiView


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    model = GuiModel()
    view = GuiView()
    controller = GuiController(model, view)
    
    view.show()
    sys.exit(app.exec_())