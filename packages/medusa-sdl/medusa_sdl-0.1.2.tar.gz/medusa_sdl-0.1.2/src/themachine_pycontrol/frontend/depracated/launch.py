import os
import webbrowser
from pathlib import Path

def launch_editor():
    """Launches the Medusa graph editor in a web browser."""
    frontend_dir = Path(__file__).parent
    html_file = frontend_dir / 'index.html'
    if html_file.exists():
        webbrowser.open_new_tab(f'file://{html_file.resolve()}')
    else:
        print(f"Error: index.html not found at {html_file}")

if __name__ == '__main__':
    launch_editor()