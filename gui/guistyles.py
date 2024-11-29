
#App styles
styles = {
    "LIGHT_MODE_CHECKBOX_STYLE": """
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
    "LIGHT_MODE_BUTTON_STYLE": """
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
    "DARK_MODE_CHECKBOX_STYLE": """
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

    "DARK_MODE_BUTTON_STYLE": """
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
    
    "DARK_MODE_MENU_BAR_STYLE": """
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
    
    "LIGHT_MODE_MENU_BAR_STYLE": """
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
    
     "LIGHT_MODE_SLIDER_STYLE": """
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
    """,

"DARK_MODE_SLIDER_STYLE": """
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
    """

}