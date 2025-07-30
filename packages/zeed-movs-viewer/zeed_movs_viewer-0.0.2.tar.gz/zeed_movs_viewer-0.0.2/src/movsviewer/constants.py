from pathlib import Path
from typing import Final


def _resource(filename: str) -> Path:
    return Path(__file__).with_name('resources') / filename


MAINUI_UI_PATH: Final = _resource('mainui.ui')
SETTINGSUI_UI_PATH: Final = _resource('settingsui.ui')

GECKODRIVER_PATH: Final = _resource('geckodriver.exe')

SETTINGS_USERNAME: Final = 'username'
SETTINGS_PASSWORD: Final = 'password'  # noqa:S105
SETTINGS_DATA_PATHS: Final = 'dataPaths'
