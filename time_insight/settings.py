import json
import os

from time_insight.logging.logger import logger

SETTINGS_FILE = 'settings.json'

DEFAULT_SETTINGS = {
    "theme": "Light",
    "theme_main_color": "#ffffff",
    "theme_secondary_color": "#f0f0f0",
    "theme_third_color": "#cccccc",
    "theme_text_color": "#000000",
    "language": "en",
    "autostart": True,
    "sosal": False
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
            return settings
        except Exception as e:
            logger.error(e)
            return DEFAULT_SETTINGS
    else:
        return DEFAULT_SETTINGS

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        logger.error(e)

def reset_settings():
    save_settings(DEFAULT_SETTINGS)

def get_setting(key, default=None):
    settings = load_settings()
    return settings.get(key, default)

def set_setting(key, value):
    settings = load_settings()
    settings[key] = value
    save_settings(settings)