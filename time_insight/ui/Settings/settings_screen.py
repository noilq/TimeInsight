from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QStackedWidget, QSlider, QComboBox, QRadioButton, QCheckBox, QLineEdit, QSizePolicy
)
from PyQt5.QtCore import Qt

from time_insight.settings import get_setting, set_setting
from time_insight.logging.logger import logger

class SettingsScreen(QWidget):
    update_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Settings")
        self.setFixedSize(600, 400)

        central_layout = QVBoxLayout(self)
        #kak to blat ne rabotaet ne cetralizuet kal
        
        main_layout = QHBoxLayout()
        
        self.sidebar = QVBoxLayout()
        self.sidebar.setSpacing(2)  #minimize space between buttons
        self.buttons = {}
        sections = ["Main", "UI", "Settings 3", "Settings 4", "About"]
        
        for section in sections:
            btn = QPushButton(section)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn.setFixedWidth(100)
            btn.clicked.connect(lambda checked, s=section: self.switch_section(s))
            self.sidebar.addWidget(btn)
            self.buttons[section] = btn
        
        main_layout.addLayout(self.sidebar)
        
        self.stacked_widget = QStackedWidget()
        self.pages = {}
        self.curr_section = None

        for section in sections:
            page = self.create_settings_page(section)
            self.stacked_widget.addWidget(page)
            self.pages[section] = page
        
        main_layout.addWidget(self.stacked_widget)
        
        footer_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button = QPushButton("Cancel")
        self.save_button.setFixedWidth(100)
        self.cancel_button.setFixedWidth(100)
        footer_layout.addWidget(self.save_button)
        footer_layout.addWidget(self.cancel_button)
        footer_layout.setAlignment(Qt.AlignRight)
        
        container_layout = QVBoxLayout()
        container_layout.addLayout(main_layout)
        container_layout.addStretch()
        container_layout.addLayout(footer_layout)
        
        central_layout.addLayout(container_layout)
        self.setLayout(central_layout)
        
        self.switch_section("Main")
    
    def create_settings_page(self, section):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(QLabel(f"Settings for {section}"))
        
        if section == "Main":
            layout.addWidget(QLabel("Setting"))
            layout.addWidget(QLineEdit("10"))
            layout.addWidget(QLabel("Super slider"))
            layout.addWidget(QSlider())
        elif section == "UI":
            #color theme dropbox
            layout.addWidget(QLabel("Color theme"))
            self.theme_combo_box = QComboBox()
            self.theme_combo_box.addItems(["Light", "Dark", "Custom"])    #custom not implemented yet
            self.theme_combo_box.setCurrentText(get_setting("theme"))
            layout.addWidget(self.theme_combo_box)
        elif section == "Settings 3":
            layout.addWidget(QLabel("Sosal"))
            layout.addWidget(QRadioButton("Da"))
            layout.addWidget(QRadioButton("Vtoroe da"))
        elif section == "Settings 4":
            layout.addWidget(QLabel("Enable coookies"))
            layout.addWidget(QCheckBox("Enable malware"))
        
        page.setLayout(layout)
        return page
    
    def switch_section(self, section):
        self.stacked_widget.setCurrentWidget(self.pages[section])
        self.curr_section = section
        
    def save_settings(self):

        if self.curr_section == "Main":
            blabla = None
            self.update_signal.emit("var")
        elif self.curr_section == "UI":
            selected_theme = self.theme_combo_box.currentText()
            if selected_theme == "Light":
                set_setting("theme", selected_theme)
                set_setting("theme_main_color", "#ffffff")
                set_setting("theme_secondary_color", "#f0f0f0")
                set_setting("theme_third_color", "#cccccc")
                set_setting("theme_text_color", "#000000")
                logger.info("Theme changed to Light.")
                self.update_signal.emit("theme")
            elif selected_theme == "Dark":
                set_setting("theme", selected_theme)
                set_setting("theme_main_color", "#2b2b2b")
                set_setting("theme_secondary_color", "#3c3c3c")
                set_setting("theme_third_color", "#5c5c5c")
                set_setting("theme_text_color", "#ffffff")
                logger.info("Theme changed to Dark.")
                self.update_signal.emit("theme")