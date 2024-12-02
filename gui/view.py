import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter, QMessageBox, QPushButton, QActionGroup, QAction, QCheckBox, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Constants
WINDOW_TITLE = "Medical Segmentation"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MAIN_SPLITTER_SIZES = [400, 400, 200]
LEFT_SPLITTER_SIZES = [300, 300]
RIGHT_SPLITTER_SIZES = [300, 300]
# Stylesheet for checkboxes and buttons in light mode
LIGHT_MODE_CHECKBOX_STYLE = """
QCheckBox::indicator {
    width: 10px;
    height: 10px;
    border: 2px solid #7A7A7A;
    background-color: #FFFFFF;
    border-radius: 0px; 
}

QCheckBox::indicator:checked {
    background-color: #FFFFFF;
    border: 2px solid #7A7A7A; 
    image: url('assets/tick_icon_light.png'); 
}

QCheckBox {
    font-size: 14px;
    color: #5A5A5A;
    padding: 5px;
}
"""

LIGHT_MODE_BUTTON_STYLE = """
QPushButton {
    background-color: #5A5A5A;
    color: #FFFFFF;
    border: 2px solid #5A5A5A;
    padding: 8px;
    font-size: 12px;
    border-radius: 0px; 
}

QPushButton:hover {
    background-color: #4A4A4A; 
    color: #FFFFFF;
    border: 2px solid #4A4A4A;
}

QPushButton:pressed {
    background-color: #3A3A3A; 
    color: #FFFFFF;
    border: 2px solid #3A3A3A;
}
"""

# Stylesheet for checkboxes and buttons in dark mode
DARK_MODE_CHECKBOX_STYLE = """
QCheckBox::indicator {
    width: 10px;
    height: 10px;
    border: 2px solid #B0B0B0; 
    background-color: #5A5A5A;
    border-radius: 0px; 
}

QCheckBox::indicator:checked {
    background-color: #5A5A5A;
    border: 2px solid #B0B0B0; 
    image: url('assets/tick_icon_dark.png'); 
}

QCheckBox {
    font-size: 14px;
    color: #FFFFFF;
    padding: 5px;
}
"""

DARK_MODE_BUTTON_STYLE = """
QPushButton {
    background-color: #3A3A3A; 
    color: #FFFFFF;
    border: 2px solid #B0B0B0;
    padding: 8px;
    font-size: 12px;
    border-radius: 0px; 
}

QPushButton:hover {
    background-color: #2A2A2A; 
    color: #FFFFFF;
    border: 2px solid #B0B0B0;
}

QPushButton:pressed {
    background-color: #1A1A1A; 
    color: #FFFFFF;
    border: 2px solid #B0B0B0;
}
"""





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

        self.checkbox_lock_layers = QCheckBox("Lock layers")
        self.checkbox_lock_layers.setStyleSheet(LIGHT_MODE_CHECKBOX_STYLE)
        self.side_options.layout().addWidget(self.checkbox_lock_layers)
        self.checkbox_lock_layers.setChecked(False)

        self.checkbox_selection_mode = QCheckBox("Selection mode")
        self.checkbox_selection_mode.setStyleSheet(LIGHT_MODE_CHECKBOX_STYLE)
        self.side_options.layout().addWidget(self.checkbox_selection_mode)
        self.checkbox_selection_mode.setChecked(False)
        
        self.reset_layers_button = QPushButton("Reset Layers")
        self.reset_layers_button.setStyleSheet(LIGHT_MODE_BUTTON_STYLE)
        self.side_options.layout().addWidget(self.reset_layers_button)

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

    def update_slice(self, panel, slice_data, slice_index):
        """
        Update the slice data displayed in a panel.
        
        Args:
            panel (FigureCanvas): The panel to update.
            slice_data (np.ndarray): The slice data to display.
            slice_index (int): The slice index.
        """
        canvas = panel
        #clear panel text
        canvas.figure.texts = [canvas.figure.texts[0]]
        panel.figure.text(0.95, 0.05, f"Slice: {slice_index}", color="white", fontsize=12, ha='right', va='bottom')
        ax = canvas.figure.gca()
        ax.clear()
        # Display the slice data if it is not None
        if slice_data is not None:
            ax.imshow(slice_data, cmap="gray")
        else:
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
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.Base, QColor(240, 240, 240))
        palette.setColor(QPalette.AlternateBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        self.checkbox_lock_layers.setStyleSheet(LIGHT_MODE_CHECKBOX_STYLE)
        self.checkbox_selection_mode.setStyleSheet(LIGHT_MODE_CHECKBOX_STYLE)
        self.reset_layers_button.setStyleSheet(LIGHT_MODE_BUTTON_STYLE)
        self.setPalette(palette)
        self.menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #f0f0f0; 
                color: black;
            }
            QMenuBar::item::selected {
                background-color: #d0d0d0;
            }
            QMenuBar::item::pressed {
                background-color: #b0b0b0;
            }
        """)
        self.side_options.setStyleSheet("background-color: #f0f0f0; color: black;")

    def apply_dark_mode(self):
        """
        Apply a dark mode color scheme to the GUI.
        """
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(42, 42, 42))
        palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Highlight, QColor(142, 45, 197))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        self.checkbox_lock_layers.setStyleSheet(DARK_MODE_CHECKBOX_STYLE)
        self.checkbox_selection_mode.setStyleSheet(DARK_MODE_CHECKBOX_STYLE)
        self.reset_layers_button.setStyleSheet(DARK_MODE_BUTTON_STYLE)
        self.setPalette(palette)
        self.menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #353535; 
                color: white;
            }
            QMenuBar::item::selected {
                background-color: #454545;
            }
            QMenuBar::item::pressed {
                background-color: #555555;
            }
            QMenu {
                background-color: #353535;
                color: white;
            }
            QMenu::item::selected {
                background-color: #454545;
            }
            QMenu::item::pressed {
                background-color: #555555;
            }
        """)
        self.side_options.setStyleSheet("background-color: #353535; color: white;")



