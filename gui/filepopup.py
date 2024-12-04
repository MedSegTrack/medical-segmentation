from PyQt5.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QPushButton, QLabel, QFileDialog
from PyQt5.QtGui import QPalette, QColor
from gui.guistyles import LIGHT_MODE_STYLES, DARK_MODE_STYLES

class LoadFileDialog(QDialog):
    """
    A dialog to load Nifti files and masks.

    Args:
        QDialog (QDialog): The base class for dialogs
    """
    def __init__(self, dark_mode=False):
        super().__init__()
        self.setWindowTitle("Load Files")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout(self)

        self.load_nifti_button = QPushButton("Load Nifti")
        self.load_nifti_button.clicked.connect(self.load_nifti_file)
        layout.addWidget(self.load_nifti_button)
        
        self.nifti_label = QLabel("No file loaded")
        layout.addWidget(self.nifti_label)

        self.checkbox = QCheckBox("Load Nifti Mask")
        self.checkbox.stateChanged.connect(self.toggle_mask)
        self.checkbox.setCheckable(False)
        layout.addWidget(self.checkbox)

        self.load_mask_button = QPushButton("Load Nifti Mask")
        self.load_mask_button.setEnabled(False)
        self.load_mask_button.clicked.connect(self.load_mask_file)
        layout.addWidget(self.load_mask_button)

        self.mask_label = QLabel("No mask loaded")
        layout.addWidget(self.mask_label)

        self.accept_button = QPushButton("Accept")
        self.accept_button.clicked.connect(self.accept_files)
        layout.addWidget(self.accept_button)

        if dark_mode:
            self.apply_dark_mode()
        else:
            self.apply_light_mode()

    def accept_files(self):
        self.accept()

    def toggle_mask(self, state):
        if state == 2:
            self.load_mask_button.setEnabled(True)
        else:
            self.load_mask_button.setEnabled(False)

    def load_nifti_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Nifti File", "", "Nifti Files (*.nii *.nii.gz)")
        if file_path:
            self.nifti_label.setText(file_path)
            self.nifti_path = file_path
            self.checkbox.setCheckable(True)

    def load_mask_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Nifti Mask File", "", "Nifti Files (*.nii *.nii.gz)")
        if file_path:
            self.mask_label.setText(file_path)
            self.mask_path = file_path

    def apply_light_mode(self):
        """
        Apply a light mode color scheme to the GUI.
        """
        stylesheet = (
            LIGHT_MODE_STYLES["CHECKBOX_STYLE"] +
            LIGHT_MODE_STYLES["BUTTON_STYLE"] +
            LIGHT_MODE_STYLES["LABEL_STYLE"] 
        )
        self.setStyleSheet(stylesheet)
        self.apply_palette(LIGHT_MODE_STYLES["PALETTE"])

    def apply_dark_mode(self):
        """
        Apply a dark mode color scheme to the GUI.
        """
        stylesheet = (
            DARK_MODE_STYLES["CHECKBOX_STYLE"] +
            DARK_MODE_STYLES["BUTTON_STYLE"] +
            DARK_MODE_STYLES["LABEL_STYLE"]
        )
        self.setStyleSheet(stylesheet)
        self.apply_palette(DARK_MODE_STYLES["PALETTE"])

    def apply_palette(self, palette_config):
        """
        Apply a color palette to the GUI.
        
        Args:
            palette_config (dict): A dictionary with the color palette configuration.
        """
        palette = self.palette()
        for role, color in palette_config.items():
            palette.setColor(getattr(QPalette, role), QColor(*color))
        self.setPalette(palette)