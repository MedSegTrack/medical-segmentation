# Light Mode Styles
LIGHT_MODE_STYLES = {
    "CHECKBOX_STYLE": """
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
    """,
    "LABEL_STYLE": """
    QLabel {
        color: #5A5A5A;
        font-size: 12px;
    }
    """,
    "BUTTON_STYLE": """
    QPushButton {
        background-color: #5A5A5A;
        color: #FFFFFF;
        border: 2px solid #5A5A5A;
        padding: 1px;
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
    """,
    "MENU_BAR_STYLE": """
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
    """,
    "SLIDER_STYLE": """
    QSlider::groove:horizontal {
        border: 1px solid #7A7A7A;
        background: #FFFFFF;
        height: 8px;
        border-radius: 4px;
    }

    QSlider::handle:horizontal {
        background: #5A5A5A;
        border: 2px solid #B0B0B0;
        width: 16px;
        height: 16px;
        border-radius: 8px;
        margin: -4px 0;
    }

    QSlider::handle:horizontal:hover {
        background: #4A4A4A;
        border: 2px solid #4A4A4A;
    }

    QSlider::handle:horizontal:pressed {
        background: #3A3A3A;
        border: 2px solid #3A3A3A;
    }

    QSlider::sub-page:horizontal {
        background: #7A7A7A;
        border: 1px solid #7A7A7A;
        height: 8px;
        border-radius: 4px;
    }

    QSlider::add-page:horizontal {
        background: #FFFFFF;
        border: 1px solid #7A7A7A;
        height: 8px;
        border-radius: 4px;
    }

    QSlider::groove:horizontal:disabled {
        background: #E0E0E0;
        border: 1px solid #C0C0C0;
    }

    QSlider::handle:horizontal:disabled {
        background: #D0D0D0;
        border: 2px solid #C0C0C0;
    }

    QSlider::sub-page:horizontal:disabled {
        background: #C0C0C0;
        border: 1px solid #C0C0C0;
    }

    QSlider::add-page:horizontal:disabled {
        background: #E0E0E0;
        border: 1px solid #C0C0C0;
    }

    QSplitter {
        background-color: #FFFFFF;
        background: 1px solid #FFFFFF;
    }
    
    QSplitter::handle {
    background-color: #FFFFFF; 
    }

    QSplitter::handle:horizontal {
        width: 3px;
    }

    QSplitter::handle:vertical {
        height: 3px;
    }
    
    QMainWindow {
        background-color: #f0f0f0;
        border: 1px solid #f0f0f0;
    }
    
    """,
    "PALETTE": {
        "Window": (255, 255, 255),
        "WindowText": (0, 0, 0),
        "Base": (240, 240, 240),
        "AlternateBase": (255, 255, 255),
        "ToolTipBase": (255, 255, 255),
        "ToolTipText": (0, 0, 0),
        "Text": (0, 0, 0),
        "BrightText": (255, 0, 0),
        "Highlight": (0, 120, 215),
        "HighlightedText": (255, 255, 255),
    }
}

# Dark Mode Styles
DARK_MODE_STYLES = {
    "CHECKBOX_STYLE": """
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
    """,
    "LABEL_STYLE": """
    QLabel {
        color: #FFFFFF;
        font-size: 12px;
    }
    """,
    "BUTTON_STYLE": """
    QPushButton {
        background-color: #3A3A3A; 
        color: #FFFFFF;
        border: 2px solid #B0B0B0;
        padding: 1px;
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
    """,
    "MENU_BAR_STYLE": """
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
    """,
    "SLIDER_STYLE": """
    QSlider::groove:horizontal {
        border: 1px solid #B0B0B0;
        background: #5A5A5A;
        height: 8px;
        border-radius: 4px;
    }

    QSlider::handle:horizontal {
        background: #3A3A3A;
        border: 2px solid #B0B0B0;
        width: 16px;
        height: 16px;
        border-radius: 8px;
        margin: -4px 0;
    }

    QSlider::handle:horizontal:hover {
        background: #2A2A2A;
        border: 2px solid #2A2A2A;
    }

    QSlider::handle:horizontal:pressed {
        background: #1A1A1A;
        border: 2px solid #1A1A1A;
    }

    QSlider::sub-page:horizontal {
        background: #B0B0B0;
        border: 1px solid #B0B0B0;
        height: 8px;
        border-radius: 4px;
    }

    QSlider::add-page:horizontal {
        background: #5A5A5A;
        border: 1px solid #B0B0B0;
        height: 8px;
        border-radius: 4px;
    }

    QSlider::groove:horizontal:disabled {
        background: #4A4A4A;
        border: 1px solid #3A3A3A;
    }

    QSlider::handle:horizontal:disabled {
        background: #2A2A2A;
        border: 2px solid #3A3A3A;
    }

    QSlider::sub-page:horizontal:disabled {
        background: #3A3A3A;
        border: 1px solid #3A3A3A;
    }
    

    QSlider::add-page:horizontal:disabled {
        background: #4A4A4A;
        border: 1px solid #3A3A3A;
    }
    
    QSplitter {
        background-color: #535353;
        background: 1px solid #535353;
    }

    QSplitter::handle {
        background-color: #535353; 
    }

    QSplitter::handle:horizontal {
        width: 3px;
    }

    QSplitter::handle:vertical {
        height: 3px;
    }
    
    QMainWindow {
        background-color: #535353;
        border: 1px solid #535353;
    }
    
    QDialog {
        background-color: #535353;
        border: 1px solid #535353;
    }
    
    """, 
    "PALETTE": {
        "Window": (53, 53, 53),
        "WindowText": (255, 255, 255),
        "Base": (42, 42, 42),
        "AlternateBase": (66, 66, 66),
        "ToolTipBase": (255, 255, 255),
        "ToolTipText": (255, 255, 255),
        "Text": (255, 255, 255),
        "BrightText": (255, 0, 0),
        "Highlight": (142, 45, 197),
        "HighlightedText": (0, 0, 0),
    }
}
