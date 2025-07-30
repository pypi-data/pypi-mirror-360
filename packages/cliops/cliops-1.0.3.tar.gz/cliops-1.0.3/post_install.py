import os
import sys
from pathlib import Path

def add_to_path():
    """Add Python Scripts directory to PATH if not already present"""
    scripts_dir = Path(sys.executable).parent / "Scripts"
    current_path = os.environ.get('PATH', '')
    
    if str(scripts_dir) not in current_path:
        print(f"Add this to your PATH: {scripts_dir}")
        print("Or run: setx PATH \"%PATH%;{}\"".format(scripts_dir))

if __name__ == "__main__":
    add_to_path()