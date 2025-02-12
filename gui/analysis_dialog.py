from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from gui.guistyles import LIGHT_MODE_STYLES, DARK_MODE_STYLES
from PyQt5.QtGui import QPalette, QColor

class AnalysisDialog(QDialog):
    def __init__(self, results: dict, dark_mode: bool = False):
        super().__init__()
        self.setWindowTitle("Mask Analysis Results")
        self.setMinimumWidth(300)

        layout = QVBoxLayout()
        
        for key, value in results.items():
            label = QLabel(f"{key}: {value}")
            layout.addWidget(label)
            
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
        
        if dark_mode:
            self.apply_dark_mode()
        else:
            self.apply_light_mode()

    def apply_light_mode(self):
        stylesheet = (
            LIGHT_MODE_STYLES["BUTTON_STYLE"] +
            LIGHT_MODE_STYLES["LABEL_STYLE"]
        )
        self.setStyleSheet(stylesheet)
        self.apply_palette(LIGHT_MODE_STYLES["PALETTE"])

    def apply_dark_mode(self):
        stylesheet = (
            DARK_MODE_STYLES["BUTTON_STYLE"] +
            DARK_MODE_STYLES["LABEL_STYLE"]
        )
        self.setStyleSheet(stylesheet)
        self.apply_palette(DARK_MODE_STYLES["PALETTE"])

    def apply_palette(self, palette_config):
        palette = self.palette()
        for role, color in palette_config.items():
            palette.setColor(getattr(QPalette, role), QColor(*color))
        self.setPalette(palette)