"""
TASKMAN - A secure task management and note-taking application
"""

import pkg_resources
import requests
from colorama import Fore, Style

from .interface import main_interface
from .taskman_backend import TaskmanBackend, setup_backend

__version__ = "0.7.7"

def check_for_updates():
    """Check for new version of taskman-sv on PyPI"""
    try:
        response = requests.get("https://pypi.org/pypi/taskman-sv/json", timeout=2)
        if response.status_code == 200:
            latest_version = response.json()["info"]["version"]
            current_version = pkg_resources.get_distribution("taskman-sv").version
            
            if latest_version > current_version:
                print(f"{Fore.YELLOW}New version available: {latest_version} "
                      f"(you have {current_version})")
                print(f"Run 'pip install --upgrade taskman-sv' to update{Style.RESET_ALL}")
    except Exception:
        # Silently fail if unable to check for updates
        pass



__all__ = [
    'main_interface',
    'TaskmanBackend',
    'setup_backend',
    'add_task',
    'edit_task',
    'start_task',
    'resume_task',
    'notes_interface',
    'fast_notes_interface',
    'generate_daily_report'
]