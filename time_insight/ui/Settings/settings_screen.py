from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QStackedWidget, QSlider, QComboBox, QRadioButton, QCheckBox, QLineEdit, QSizePolicy, QFileDialog, QColorDialog
)
from PyQt5.QtCore import Qt
from time_insight.tracker.tracker import set_interval

from sqlalchemy.orm import Session
from time_insight.data.database import engine
from time_insight.data.models import ApplicationActivity, Application, UserSession, UserSessionType
import pandas as pd

from time_insight.settings import get_setting, set_setting
from time_insight.logging.logger import logger

import shutil
import os
from time_insight.config import DB_PATH, DATA_DIR

from time_insight.ui.language_manager import language_manager 
from time_insight.translations import t

class SettingsScreen(QWidget):
    update_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle(t("settings"))
        self.setFixedSize(600, 400)

        central_layout = QVBoxLayout(self)
        #kak to blat ne rabotaet ne cetralizuet kal
        
        main_layout = QHBoxLayout()
        
        self.sidebar = QVBoxLayout()
        self.sidebar.setSpacing(2)  #minimize space between buttons
        self.buttons = {}
        sections = [t("general"), t("ui"), t("data"), t("reports"), t("about")]
        
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
        self.save_button = QPushButton(t("save"))
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button = QPushButton(t("cancel"))
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
        
        self.switch_section(t("general"))

        language_manager.language_changed.connect(self.retranslate_ui)
        self.retranslate_ui()
        self.switch_section(self.curr_section)

    def retranslate_ui(self):
        self.setWindowTitle(t("settings"))
        self.save_button.setText(t("save"))
        self.cancel_button.setText(t("cancel"))
        self.frequency_label.setText(t("frequency_of_checking_active_window"))

        self.language_label.setText(t("language"))
        
        self.color_theme_label.setText(t("color_theme"))
        self.graphs_label.setText(t("graphs"))
        
        self.theme_combo_box.setItemText(0, t("theme_light"))
        self.theme_combo_box.setItemText(1, t("theme_dark"))
        self.theme_combo_box.setItemText(2, t("theme_custom"))
        
        self.graphs_type_combo_box.setItemText(0, t("graphs_bar"))
        self.graphs_type_combo_box.setItemText(1, t("graphs_line"))
        
        self.export_programs_data_button.setText(t("export_programs_data"))
        self.export_sessions_data_button.setText(t("export_sessions_data"))
        self.export_database_button.setText(t("export_database"))
        self.import_database_button.setText(t("import_database"))
        
        self.daily_checkbox.setText(t("daily_report"))
        self.weekly_checkbox.setText(t("weekly_report"))
        self.monthly_checkbox.setText(t("monthly_report"))

        sections = [t("general"), t("ui"), t("data"), t("reports"), t("about")]

        for i, (section, btn) in enumerate(self.buttons.items()):   
            btn.setText(sections[i])

        if self.curr_section:
            self.switch_section(self.curr_section)
    
    def create_settings_page(self, section):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(QLabel(section))
        
        if section == t("general"):
            self.frequency_label = QLabel(t("frequency_of_checking_active_window"))
            layout.addWidget(self.frequency_label)

            self.interval_combo_box = QComboBox()
            self.interval_combo_box.addItems(["1", "2", "3", "4", "5", "10", "15", "30"])
            self.interval_combo_box.setCurrentText(get_setting("window_cheking_interval"))
            layout.addWidget(self.interval_combo_box)

            self.language_label = QLabel(t("language"))
            layout.addWidget(self.language_label)

            self.language_combo_box = QComboBox()
            self.language_combo_box.addItems(["English", "Czech"])
            self.language_combo_box.setCurrentText(get_setting("language"))
            layout.addWidget(self.language_combo_box)
        elif section == t("ui"):
            #color theme dropbox
            self.color_theme_label = QLabel(t("color_theme"))
            layout.addWidget(self.color_theme_label)

            self.theme_combo_box = QComboBox()
            self.theme_combo_box.addItems([t("theme_light"), t("theme_dark"), t("theme_custom")])
            self.theme_combo_box.currentTextChanged.connect(self.on_theme_changed)  #if set to custom
            self.theme_combo_box.setCurrentText(get_setting("theme"))
            layout.addWidget(self.theme_combo_box)

            self.graphs_label = QLabel(t("graphs"))
            layout.addWidget(self.graphs_label)

            self.graphs_type_combo_box = QComboBox()
            self.graphs_type_combo_box.addItems([t("graphs_bar"), t("graphs_line")])
            self.graphs_type_combo_box.setCurrentText(get_setting("graphs"))
            layout.addWidget(self.graphs_type_combo_box)
        elif section == t("data"):
            self.export_programs_data_button = QPushButton(t("export_programs_data"))
            self.export_programs_data_button.clicked.connect(self.export_programs_data)
            layout.addWidget(self.export_programs_data_button)
            self.export_sessions_data_button = QPushButton(t("export_sessions_data"))
            self.export_sessions_data_button.clicked.connect(self.export_sessions_data)
            layout.addWidget(self.export_sessions_data_button)
            self.export_database_button = QPushButton(t("export_database"))
            self.export_database_button.clicked.connect(self.export_database)
            layout.addWidget(self.export_database_button)
            self.import_database_button = QPushButton(t("import_database"))
            self.import_database_button.clicked.connect(self.import_database)
            layout.addWidget(self.import_database_button)
        elif section == t("reports"):
            layout.addWidget(QLabel("Enable reports"))
            self.daily_checkbox = QCheckBox(t("daily_report"))
            self.daily_checkbox.setChecked(get_setting("daily_report"))
            self.weekly_checkbox = QCheckBox(t("weekly_report"))
            self.weekly_checkbox.setChecked(get_setting("weekly_report"))
            self.monthly_checkbox = QCheckBox(t("monthly_report"))
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
        print(self.curr_section)
        if self.curr_section == t("general"):
            window_cheking_interval = self.interval_combo_box.currentText()
            set_setting("window_cheking_interval", window_cheking_interval)
            set_interval(window_cheking_interval)     #set new window checking interval
            logger.info("Window checking interval changed to " + window_cheking_interval)
            self.update_signal.emit("var")

            selected_language = self.language_combo_box.currentText()
            print(selected_language)
            set_setting("language", selected_language)
            logger.info("Language changed to " + selected_language)

            language_manager.change_language(selected_language)
            self.retranslate_ui()
            self.switch_section(self.curr_section)

        elif self.curr_section == t("ui"):
            selected_theme = self.theme_combo_box.currentText()
            if selected_theme == t("theme_light"):
                set_setting("theme", selected_theme)
                set_setting("theme_main_color", "#ffffff")
                set_setting("theme_secondary_color", "#f0f0f0")
                set_setting("theme_third_color", "#cccccc")
                set_setting("theme_text_color", "#000000")
                logger.info("Theme changed to Light.")
                self.update_signal.emit("theme")
            elif selected_theme == t("theme_dark"):
                set_setting("theme", selected_theme)
                set_setting("theme_main_color", "#2b2b2b")
                set_setting("theme_secondary_color", "#3c3c3c")
                set_setting("theme_third_color", "#5c5c5c")
                set_setting("theme_text_color", "#ffffff")
                logger.info("Theme changed to Dark.")
                self.update_signal.emit("theme")
            elif selected_theme == t("theme_custom"):
                set_setting("theme", selected_theme)
                set_setting("theme_main_color", self.main_hex_color)
                set_setting("theme_secondary_color", self.secondary_hex_color)
                set_setting("theme_third_color", self.highlight_hex_color)
                set_setting("theme_text_color", self.text_hex_color)
                logger.info("Theme changed to Custom.")
                self.update_signal.emit("theme")

            selected_theme = self.graphs_type_combo_box.currentText()
            if selected_theme == t("graphs_bar"):
                set_setting("graphs", "Bar")
            elif selected_theme == t("graphs_line"):
                set_setting("graphs", "Line")

        elif self.curr_section == "Reports":
            daily = self.daily_checkbox.isChecked()
            weekly = self.weekly_checkbox.isChecked()
            monthly = self.monthly_checkbox.isChecked()
            set_setting("daily_report", daily)
            set_setting("weekly_report", weekly)
            set_setting("monthly_report", monthly)

    def export_programs_data(self):
        logger.info("Starting export...")
        with Session(engine) as session:
            activities = session.query(
                ApplicationActivity.id.label("Activity ID"),
                ApplicationActivity.application_id.label("Application ID"),
                ApplicationActivity.window_name.label("Window Name"),
                ApplicationActivity.additional_info.label("Additional Info"),
                ApplicationActivity.session_start.label("Start Time"),
                ApplicationActivity.session_end.label("End Time"),
                ApplicationActivity.duration.label("Duration"),
                Application.name.label("Program Name"),
                Application.desc.label("Program Description"),
                Application.enrollment_date.label("Enrollment Date"),
                Application.path.label("Program Path")
            ).join(
                Application, Application.id == ApplicationActivity.application_id
            ).all()

        df = pd.DataFrame(activities)

        dest, _ = QFileDialog.getSaveFileName(self, "Save Programs Data", "", "CSV Files (*.csv)")
        if dest:
            df.to_csv(dest, index=False, encoding="utf-8")
            logger.info(f"Programs data exported to {dest}")

    def export_sessions_data(self):
        logger.info("Starting export...")
        with Session(engine) as session:
            user_sessions = session.query(UserSession, UserSessionType.name).join(
                UserSessionType, UserSession.user_session_type_id == UserSessionType.id
            ).all()

        df = pd.DataFrame(user_sessions)

        dest, _ = QFileDialog.getSaveFileName(self, "Save Sessions Data", "", "CSV Files (*.csv)")
        if dest:
            df.to_csv(dest, index=False, encoding="utf-8")
            logger.info(f"Sessions data exported to {dest}")

    def export_database(self):
        logger.info("Starting export...")
        dest, _ = QFileDialog.getSaveFileName(self, "Save Database", "", "Database Files (*.db)")
        if dest:
            shutil.copy(DB_PATH, dest)
            logger.info(f"Database exported to {dest}")

    def import_database(self):
        logger.info("Starting import...")
        src, _ = QFileDialog.getOpenFileName(self, "Import Database", "", "Database Files (*.db)")
        if src:
            dest = os.path.join(DATA_DIR, 'time_insight.db')
            shutil.copy(src, DB_PATH)
            logger.info(f"Database imported from {src}")

    def on_theme_changed(self, text):
        if text == "Custom":
            main_color = QColorDialog.getColor(title="Choose main color")
            if main_color.isValid():
                self.main_hex_color = main_color.name()
            secondary_color = QColorDialog.getColor(title="Choose secondary color")
            if secondary_color.isValid():
                self.secondary_hex_color = secondary_color.name()
            highlight_color = QColorDialog.getColor(title="Choose highlight color")
            if highlight_color.isValid():
                self.highlight_hex_color = highlight_color.name()
            text_color = QColorDialog.getColor(title="Choose text color")
            if text_color.isValid():
                self.text_hex_color = text_color.name()