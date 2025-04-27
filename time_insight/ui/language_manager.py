from PyQt5.QtCore import QObject, pyqtSignal
from time_insight.translations import set_language
from time_insight.logging.logger import logger

class LanguageManager(QObject):
    language_changed = pyqtSignal()

    def __init__(self):
        super().__init__()

    def change_language(self, language):
        set_language(language)         #change lang globaly
        logger.info(f"Language changed to {language}")
        self.language_changed.emit()
        
language_manager = LanguageManager()
