from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QStackedWidget, QSlider, QComboBox, QRadioButton, QCheckBox, QLineEdit, QSizePolicy
)
from PyQt5.QtCore import Qt
from time_insight.tracker.tracker import set_interval

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
        sections = ["General", "UI", "Settings 3", "Reports", "About"]
        
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
        
        self.switch_section("General")
    
    def create_settings_page(self, section):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(QLabel(section))
        
        if section == "General":
            layout.addWidget(QLabel("Frequency of checking active window"))
            self.interval_combo_box = QComboBox()
            self.interval_combo_box.addItems(["1", "2", "3", "4", "5", "10", "15", "30"])
            self.interval_combo_box.setCurrentText(get_setting("window_cheking_interval"))
            layout.addWidget(self.interval_combo_box)
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
        elif section == "Reports":
            layout.addWidget(QLabel("Enable reports"))
            self.daily_checkbox = QCheckBox("Daily")
            self.daily_checkbox.setChecked(get_setting("daily_report"))
            self.weekly_checkbox = QCheckBox("Weekly")
            self.weekly_checkbox.setChecked(get_setting("weekly_report"))
            self.monthly_checkbox = QCheckBox("Monthly")
            self.monthly_checkbox.setChecked(get_setting("monthly_report"))
            layout.addWidget(self.daily_checkbox)
            layout.addWidget(self.weekly_checkbox)
            layout.addWidget(self.monthly_checkbox)
        
        page.setLayout(layout)
        return page
    
    def switch_section(self, section):
        self.stacked_widget.setCurrentWidget(self.pages[section])
        self.curr_section = section
        
    def save_settings(self):

        if self.curr_section == "General":
            window_cheking_interval = self.interval_combo_box.currentText()
            set_setting("window_cheking_interval", window_cheking_interval)
            set_interval(window_cheking_interval)     #set new window checking interval
            logger.info("Window checking interval changed to " + window_cheking_interval)
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
        elif self.curr_section == "Reports":
            daily = self.daily_checkbox.isChecked()
            weekly = self.weekly_checkbox.isChecked()
            monthly = self.monthly_checkbox.isChecked()
            set_setting("daily_report", daily)
            set_setting("weekly_report", weekly)
            set_setting("monthly_report", monthly)