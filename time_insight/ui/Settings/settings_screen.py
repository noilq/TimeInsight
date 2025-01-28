from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QStackedWidget, QSlider, QComboBox, QRadioButton, QCheckBox, QLineEdit, QSizePolicy
)
from PyQt5.QtCore import Qt

class SettingsScreen(QWidget):
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
        
        for section in sections:
            page = self.create_settings_page(section)
            self.stacked_widget.addWidget(page)
            self.pages[section] = page
        
        main_layout.addWidget(self.stacked_widget)
        
        footer_layout = QHBoxLayout()
        self.ok_button = QPushButton("Apply")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.setFixedWidth(100)
        self.cancel_button.setFixedWidth(100)
        footer_layout.addWidget(self.ok_button)
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
            layout.addWidget(QLabel("Mega dropbox"))
            layout.addWidget(QComboBox())
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