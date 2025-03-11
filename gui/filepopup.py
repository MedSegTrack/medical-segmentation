from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QCheckBox,
    QPushButton,
    QLabel,
    QFileDialog,
)


class LoadFileDialog(QDialog):
    """
    A dialog to load Nifti files and masks.

    Args:
        QDialog (QDialog): The base class for dialogs
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Load Files")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout(self)
        self.nifti_label = QLabel("No file loaded")
        self.load_nifti_button = QPushButton("Load Nifti")
        self.checkbox = QCheckBox("Load Nifti Mask")
        self.load_mask_button = QPushButton("Load Nifti Mask")
        self.mask_label = QLabel("No mask loaded")
        self.accept_button = QPushButton("Accept")

        layout.addWidget(self.load_nifti_button)
        layout.addWidget(self.nifti_label)
        layout.addWidget(self.load_mask_button)
        layout.addWidget(self.mask_label)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.accept_button)

        self.load_nifti_button.clicked.connect(self.load_nifti_file)
        self.accept_button.clicked.connect(self.accept_files)
        self.checkbox.stateChanged.connect(self.toggle_mask)
        self.load_mask_button.clicked.connect(self.load_mask_file)

        self.checkbox.setCheckable(False)
        self.load_mask_button.setEnabled(False)

    def accept_files(self):
        self.accept()

    def toggle_mask(self, state):
        if state == 2:
            self.load_mask_button.setEnabled(True)
        else:
            self.load_mask_button.setEnabled(False)

    def load_nifti_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Nifti File", "", "Nifti Files (*.nii *.nii.gz)"
        )
        if file_path:
            self.nifti_label.setText(file_path)
            self.nifti_path = file_path
            self.checkbox.setCheckable(True)

    def load_mask_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Nifti Mask File", "", "Nifti Files (*.nii *.nii.gz)"
        )
        if file_path:
            self.mask_label.setText(file_path)
            self.mask_path = file_path
