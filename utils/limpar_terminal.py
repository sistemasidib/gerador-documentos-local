import os
import sys # sys is useful for checking the operating system

def clear_terminal():
    """Clears the terminal screen."""
    if sys.platform.startswith('win'):
        # For Windows
        os.system('cls')
    else:
        # For Linux and macOS
        os.system('clear')

