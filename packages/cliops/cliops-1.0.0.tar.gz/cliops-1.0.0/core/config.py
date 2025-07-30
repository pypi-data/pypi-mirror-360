import os
from pathlib import Path

class Config:
    """Manages application configuration, including state file path and pattern definitions."""
    APP_NAME = "cliops"
    STATE_FILE_NAME = "cliops_state.json"
    PATTERNS_FILE_NAME = "patterns.json"

    @staticmethod
    def get_app_data_dir():
        """Returns the appropriate application data directory for the OS."""
        if os.name == 'nt':  # Windows
            return Path(os.environ.get('APPDATA', Path.home() / Config.APP_NAME)) / Config.APP_NAME
        elif os.name == 'posix':  # Linux, macOS, etc.
            xdg_data_home = os.environ.get('XDG_DATA_HOME')
            if xdg_data_home:
                return Path(xdg_data_home) / Config.APP_NAME
            return Path.home() / ".local" / "share" / Config.APP_NAME
        else:
            return Path.home() / f".{Config.APP_NAME}"

    @staticmethod
    def get_state_file_path():
        """Returns the full path to the CLI state file."""
        data_dir = Config.get_app_data_dir()
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir / Config.STATE_FILE_NAME

    @staticmethod
    def get_patterns_file_path():
        """Returns the full path to the user-defined patterns file."""
        data_dir = Config.get_app_data_dir()
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir / Config.PATTERNS_FILE_NAME