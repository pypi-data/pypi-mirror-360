"""Command-line interface for TASKMAN"""
import sys
import argparse
from . import __version__, check_for_updates
from .interface import (
    add_task,
    edit_task,
    start_task,
    resume_task,
    notes_interface,
    fast_notes_interface,
    generate_daily_report,
    main_interface
)

def main():
    check_for_updates()
    try:
        main_interface()
    except Exception as e:
        print(f"\033[91mError: {str(e)}\033[0m")
        return 1
    return 0

if __name__ == "__main__":
    main()