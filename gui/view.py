import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter, QSizePolicy, QMenuBar, QActionGroup, QAction, QCheckBox, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class GuiView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SAM2 Segmentation")
        self.setGeometry(100, 100, 800, 600)
        

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
        self.side_options.layout().addWidget(self.checkbox_lock_layers)
        self.checkbox_lock_layers.setChecked(False)
        
        self.checkbox_selection_mode = QCheckBox("Selection mode")
        self.side_options.layout().addWidget(self.checkbox_selection_mode)
        self.checkbox_selection_mode.setChecked(False)
        
        self.side_options_layout.addStretch()


        self.left_splitter.addWidget(self.panel1)
        self.left_splitter.addWidget(self.panel4)
        self.right_splitter = QSplitter(Qt.Vertical)
        self.main_splitter.addWidget(self.right_splitter)
        self.right_splitter.addWidget(self.panel2)
        self.right_splitter.addWidget(self.panel3)
        self.main_splitter.addWidget(self.side_options)

        # Set initial sizes
        self.main_splitter.setSizes([400, 400, 200])
        self.left_splitter.setSizes([300, 300])
        self.right_splitter.setSizes([300, 300])

    def create_plot_panel(self, title): #NIE DODYKAĆ TEJ FUNCKJI
        canvas = FigureCanvas(plt.figure())
        canvas.figure.text(0.05, 0.05, title, color='white', fontsize=12, ha='left', va='bottom') #MUSI BYC PIERWSZE!!!
        canvas.figure.patch.set_facecolor('black')
        canvas.figure.text(0.5,0.5, "No data", color='white', fontsize=12, ha='center', va='center')
        return canvas

    def update_slice(self, panel, slice_data, slice_index):
        canvas = panel
        #clear panel text
        canvas.figure.texts = [canvas.figure.texts[0]]
        panel.figure.text(0.95, 0.05, f"Slice: {slice_index}", color="white", fontsize=12, ha='right', va='bottom')
        ax = canvas.figure.gca()
        ax.clear()
        ax.imshow(slice_data, cmap="gray")
        ax.axis("off")
        canvas.draw()

    def apply_light_mode(self):
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

