import sys
from PyQt5.QtWidgets import (
    QLabel, QMainWindow, QWidget, QVBoxLayout, QSplitter, QMessageBox, QPushButton, QHBoxLayout, QAction, QCheckBox, QSlider, QListWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from gui.guistyles import LIGHT_MODE_STYLES, DARK_MODE_STYLES

# Constants
WINDOW_TITLE = "Medical Segmentation"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MAIN_SPLITTER_SIZES = [400, 400, 200]
LEFT_SPLITTER_SIZES = [300, 300]
RIGHT_SPLITTER_SIZES = [300, 300]

class GuiView(QMainWindow):
    """
    The main GUI view class.
    Args:
        QMainWindow (QWidget): The main window of the application
    """
    def __init__(self):
        """
        Initialize the main window and its components.
        """
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)


        # Create the menu bar
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu("File")
        self.settings_menu = self.menu_bar.addMenu("Settings")
        self.modality_menu = self.menu_bar.addMenu("Modality")
        self.modality_menu.setEnabled(False)
        self.mask_menu = self.menu_bar.addMenu("Mask")
        self.mask_menu.setEnabled(False)

        # File menu actions
        self.load_action = QAction("Load", self)
        self.save_action = QAction("Save", self)
        self.exit_action = QAction("Exit", self)
        self.file_menu.addAction(self.load_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        # Settings menu actions
        self.dark_mode_action = QAction("Dark Mode", self, checkable=True)
        self.settings_menu.addAction(self.dark_mode_action)

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # Main Splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.main_splitter, 1)

        # Left Splitter
        self.left_splitter = QSplitter(Qt.Vertical)
        self.main_splitter.addWidget(self.left_splitter)

        # Panels with matplotlib
        self.panel1 = self.create_plot_panel("X-Slice")
        self.panel4 = self.create_plot_panel("Z-Slice")
        self.panel2 = self.create_plot_panel("Y-Slice")
        self.panel3 = self.create_plot_panel("3D View")


        self.side_options = QWidget()
        self.side_options_layout = QVBoxLayout()
        self.side_options.setLayout(self.side_options_layout)

        self.checkbox_lock_layers = QCheckBox("Lock layers while scrolling")
        self.side_options.layout().addWidget(self.checkbox_lock_layers)
        self.checkbox_lock_layers.setChecked(False)

        self.checkbox_selection_mode = QCheckBox("Selection mode")
        self.side_options.layout().addWidget(self.checkbox_selection_mode)
        self.checkbox_selection_mode.setChecked(False)

        self.reset_layers_button = QPushButton("Reset Layers")
        self.side_options.layout().addWidget(self.reset_layers_button)

        self.x_slice_slider = QSlider(Qt.Horizontal)
        self.y_slice_slider = QSlider(Qt.Horizontal)
        self.z_slice_slider = QSlider(Qt.Horizontal)


        # Create labels for each slider
        self.x_slice_label = QLabel("X:")
        self.x_slice_label.setFixedWidth(40)
        self.y_slice_label = QLabel("Y:")
        self.y_slice_label.setFixedWidth(40)
        self.z_slice_label = QLabel("Z:")
        self.z_slice_label.setFixedWidth(40)
        
        # Create horizontal layouts for each slider and label
        x_layout = QHBoxLayout()
        x_layout.addWidget(self.x_slice_label)
        x_layout.addWidget(self.x_slice_slider)


        y_layout = QHBoxLayout()
        y_layout.addWidget(self.y_slice_label)
        y_layout.addWidget(self.y_slice_slider)


        z_layout = QHBoxLayout()
        z_layout.addWidget(self.z_slice_label)
        z_layout.addWidget(self.z_slice_slider)


        # Add the horizontal layouts to the main layout
        self.side_options_layout.addLayout(x_layout)
        self.side_options_layout.addLayout(y_layout)
        self.side_options_layout.addLayout(z_layout)

        self.reset_selection_button = QPushButton("Reset Selection")
        self.side_options_layout.addWidget(self.reset_selection_button)

        # Create the list view
        self.list_view = QListWidget()
        self.side_options_layout.addWidget(self.list_view)

        self.run_segmentation_button = QPushButton("Run segmentation")
        self.side_options_layout.addWidget(self.run_segmentation_button)

        self.side_options_layout.addStretch()

        self.left_splitter.addWidget(self.panel1)
        self.left_splitter.addWidget(self.panel4)
        self.right_splitter = QSplitter(Qt.Vertical)
        self.main_splitter.addWidget(self.right_splitter)
        self.right_splitter.addWidget(self.panel2)
        self.right_splitter.addWidget(self.panel3)
        self.main_splitter.addWidget(self.side_options)

        # Set initial sizes
        self.main_splitter.setSizes(MAIN_SPLITTER_SIZES)
        self.left_splitter.setSizes(LEFT_SPLITTER_SIZES)
        self.right_splitter.setSizes(RIGHT_SPLITTER_SIZES)

    def create_plot_panel(self, title): #DO NOT TOUCH
        """
        Create a panel with a matplotlib plot.
        
        Args:
            title (str): The title of the panel.
            
        Returns:
            FigureCanvas: The panel with the plot.
        """
        canvas = FigureCanvas(plt.figure())
        canvas.figure.text(0.05, 0.05, title, color='white', fontsize=12, ha='left', va='bottom')
        canvas.figure.patch.set_facecolor('black')
        canvas.figure.text(0.5,0.5, "No data", color='white', fontsize=12, ha='center', va='center')
        return canvas

    def update_slice(self, panel, slice_data, slice_index, mask_data=None, selection_list=None):
        """
        Update the slice data displayed in a panel.

        Args:
            panel (FigureCanvas): The panel to update.
            slice_data (np.ndarray): The slice data to display.
            slice_index (int): The slice index.
            mask_data (np.ndarray, optional): The mask data to overlay. Defaults to None.
            selection_list (list, optional): The list of selected points. Defaults to None.
        """
        canvas = panel
        # Clear panel text
        canvas.figure.texts = [canvas.figure.texts[0]]
        panel.figure.text(0.95, 0.05, f"Slice: {slice_index}", color="white", fontsize=12, ha='right', va='bottom')

        ax = canvas.figure.gca()
        ax.clear()

        # Display the slice data if it is not None
        if slice_data is not None:
            # Set the extent to match the pixel dimensions of the slice
            height, width = slice_data.shape
            extent = (0, width, height, 0)
            # Display the slice
            ax.imshow(slice_data, cmap="gray", aspect='equal', extent=extent)

            # Overlay the mask, if provided
            if mask_data is not None:
                ax.imshow(mask_data, alpha=0.4, aspect='equal', extent=extent)

            # Overlay the selected points, if any
            if selection_list is not None:
                for dimension, slice_number, x, y, t, in selection_list:
                    if (panel == self.panel1 and dimension == "x") or \
                    (panel == self.panel2 and dimension == "y") or \
                    (panel == self.panel4 and dimension == "z"):
                        if slice_number == slice_index:
                            if t == "P":
                                ax.plot(x, height-y, 'go')
                            else:
                                ax.plot(x, height-y, 'ro')
        else:
            # Display "No Data" message if slice_data is None
            ax.text(0.5, 0.5, 'No Data', color='red', fontsize=20, ha='center', va='center')

        ax.axis("off")
        canvas.draw()

    def display_error(self, message):
        """
        Display an error message in a message box.

        Args:
            message (str): The error message to display.
        """
        QMessageBox.critical(self, "Error", message)

    def apply_light_mode(self):
        """
        Apply a light mode color scheme to the GUI.
        """
        self.apply_palette(LIGHT_MODE_STYLES["PALETTE"])
        stylesheet = (
            LIGHT_MODE_STYLES["CHECKBOX_STYLE"] +
            LIGHT_MODE_STYLES["BUTTON_STYLE"] +
            LIGHT_MODE_STYLES["MENU_BAR_STYLE"] +
            LIGHT_MODE_STYLES["SLIDER_STYLE"] +
            LIGHT_MODE_STYLES["LABEL_STYLE"]
        )
        self.setStyleSheet(stylesheet)
        self.side_options.setStyleSheet("background-color: #f0f0f0; color: black;")
        self.reset_layers_button.setStyleSheet(LIGHT_MODE_STYLES["BUTTON_STYLE"])
        self.reset_selection_button.setStyleSheet(LIGHT_MODE_STYLES["BUTTON_STYLE"])
        self.run_segmentation_button.setStyleSheet(LIGHT_MODE_STYLES["BUTTON_STYLE"])

    def apply_dark_mode(self):
        """
        Apply a dark mode color scheme to the GUI.
        """
        self.apply_palette(DARK_MODE_STYLES["PALETTE"])
        stylesheet = (
            DARK_MODE_STYLES["CHECKBOX_STYLE"] +
            DARK_MODE_STYLES["BUTTON_STYLE"] +
            DARK_MODE_STYLES["MENU_BAR_STYLE"] +
            DARK_MODE_STYLES["SLIDER_STYLE"] +
            DARK_MODE_STYLES["LABEL_STYLE"]
        )
        self.setStyleSheet(stylesheet)
        self.side_options.setStyleSheet("background-color: #353535; color: white;")
        self.reset_layers_button.setStyleSheet(DARK_MODE_STYLES["BUTTON_STYLE"])
        self.reset_selection_button.setStyleSheet(DARK_MODE_STYLES["BUTTON_STYLE"])
        self.run_segmentation_button.setStyleSheet(DARK_MODE_STYLES["BUTTON_STYLE"])

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

