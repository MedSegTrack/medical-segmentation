import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAction,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QSlider,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

# Window dimensions
WINDOW_TITLE = "Medical Segmentation"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MAIN_SPLITTER_SIZES = [400, 400, 200]
LEFT_SPLITTER_SIZES = [300, 300]
RIGHT_SPLITTER_SIZES = [300, 300]


class GUI(QMainWindow):
    """
    Class that creates the main window for the application.
    Args:
        QMainWindow: The main window for the application.
    """

    def __init__(self):
        """
        Create the main window for the application
        """
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Create main menu bar
        self.menu_bar = QMenuBar(self)
        self.file_menu = QMenu("File", self)
        self.settings_menu = QMenu("Settings", self)
        self.modality_menu = QMenu("Modality", self)
        self.mask_menu = QMenu("Mask", self)
        self.menu_bar.addMenu(self.file_menu)
        self.menu_bar.addMenu(self.settings_menu)
        self.menu_bar.addMenu(self.modality_menu)
        self.menu_bar.addMenu(self.mask_menu)

        # Populate the file menu
        self.load_action = QAction("Load", self)
        self.exit_action = QAction("Exit", self)
        self.save_action = QAction("Save", self)

        # Set shortcuts for the actions
        self.load_action.setShortcut("Ctrl+L")
        self.save_action.setShortcut("Ctrl+S")
        self.exit_action.setShortcut("Ctrl+Q")

        self.file_menu.addAction(self.load_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.exit_action)

        self.save_action.setEnabled(False)

        # Populate settings menu
        self.lock_layers_action = QAction("Lock Layers While Scrolling", self)
        self.disable_3d_panel_action = QAction("Disable 3D Panel", self)

        self.lock_layers_action.setCheckable(True)
        self.lock_layers_action.setEnabled(False)
        self.disable_3d_panel_action.setCheckable(True)
        self.disable_3d_panel_action.setEnabled(False)

        self.settings_menu.addAction(self.lock_layers_action)
        self.settings_menu.addAction(self.disable_3d_panel_action)
        # Mask, and modality menu populated in the future

        # Create the main window layout
        self.central_widget = QWidget(self)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_splitter = QSplitter(self.central_widget)
        self.left_splitter = QSplitter(Qt.Orientation.Vertical)
        self.right_splitter = QSplitter(Qt.Orientation.Vertical)

        # Create 3 matplotlib Panels
        self.panelX = self.create_plot_panel("x")
        self.panelY = self.create_plot_panel("y")
        self.panelZ = self.create_plot_panel("z")
        self.panel3D = self.create_plot_panel("3d")

        # Create side options panel
        self.side_options = QWidget()
        self.side_options_layout = QVBoxLayout()

        self.checkbox_selection_mode = QCheckBox("Selection Mode")

        self.reset_layers_button = QPushButton("Reset Layers")
        self.run_segmentation_button = QPushButton("Run Segmentation")
        self.analyze_mask_button = QPushButton("Analyze Mask")
        self.reset_selection_button = QPushButton("Reset Selection")

        self.list_view = QListWidget()

        self.x_slice_slider = QSlider(Qt.Orientation.Horizontal)
        self.y_slice_slider = QSlider(Qt.Orientation.Horizontal)
        self.z_slice_slider = QSlider(Qt.Orientation.Horizontal)

        self.x_slice_label = QLabel("X: ")
        self.y_slice_label = QLabel("Y: ")
        self.z_slice_label = QLabel("Z: ")

        self.x_slice_label.setFixedWidth(40)
        self.y_slice_label.setFixedWidth(40)
        self.z_slice_label.setFixedWidth(40)

        x_layout = QHBoxLayout()
        y_layout = QHBoxLayout()
        z_layout = QHBoxLayout()

        x_layout.addWidget(self.x_slice_label)
        x_layout.addWidget(self.x_slice_slider)
        y_layout.addWidget(self.y_slice_label)
        y_layout.addWidget(self.y_slice_slider)
        z_layout.addWidget(self.z_slice_label)
        z_layout.addWidget(self.z_slice_slider)

        # Connect all layouts (order matters)
        self.side_options_layout.addWidget(self.checkbox_selection_mode)
        self.side_options_layout.addWidget(self.reset_layers_button)
        self.side_options_layout.addLayout(x_layout)
        self.side_options_layout.addLayout(y_layout)
        self.side_options_layout.addLayout(z_layout)
        self.side_options_layout.addWidget(self.list_view)
        self.side_options_layout.addWidget(self.run_segmentation_button)
        self.side_options_layout.addWidget(self.analyze_mask_button)
        self.side_options_layout.addWidget(self.reset_selection_button)
        self.side_options.setLayout(self.side_options_layout)

        self.left_splitter.addWidget(self.panelX)
        self.left_splitter.addWidget(self.panelZ)

        self.right_splitter.addWidget(self.panelY)
        self.right_splitter.addWidget(self.panel3D)

        self.main_splitter.addWidget(self.left_splitter)
        self.main_splitter.addWidget(self.right_splitter)
        self.main_splitter.addWidget(self.side_options)

        self.main_layout.addWidget(self.main_splitter)
        self.central_widget.setLayout(self.main_layout)
        self.setMenuBar(self.menu_bar)
        self.setCentralWidget(self.central_widget)

        # Set initial state
        self.main_splitter.setSizes(MAIN_SPLITTER_SIZES)
        self.left_splitter.setSizes(LEFT_SPLITTER_SIZES)
        self.right_splitter.setSizes(RIGHT_SPLITTER_SIZES)

        self.modality_menu.setEnabled(False)
        self.mask_menu.setEnabled(False)
        self.run_segmentation_button.setEnabled(False)
        self.analyze_mask_button.setEnabled(False)
        self.reset_selection_button.setEnabled(False)
        self.checkbox_selection_mode.setEnabled(False)
        self.reset_layers_button.setEnabled(False)

        self.lock_layers_action.setChecked(False)
        self.disable_3d_panel_action.setChecked(False)

        for slider in [
            self.x_slice_slider,
            self.y_slice_slider,
            self.z_slice_slider,
        ]:
            slider.setEnabled(False)

    def display_error_message(self, message):
        """
        Method to display an error message to the user.

        Args:
            message (str): The message to display
        """
        QMessageBox.critical(self, "Error:", message)

    def update_panel(self, panel, new_panel_data):
        if new_panel_data:
            panel.update_pixmap(new_panel_data)

    def create_plot_panel(self, title):
        """
        Helper method to create a panel with a matplotlib plot.

        Args:
            title (str): The title of the panel.

        Returns:
            FigureCanvas: The panel with the plot.
        """
        canvas = FigureCanvas(plt.figure())
        canvas.figure.text(
            0.05,
            0.05,
            title.upper(),
            color="white",
            fontsize=12,
            ha="left",
            va="bottom",
        )
        canvas.figure.patch.set_facecolor("black")
        canvas.figure.text(
            0.5, 0.5, "No data", color="white", fontsize=12, ha="center", va="center"
        )
        return canvas
