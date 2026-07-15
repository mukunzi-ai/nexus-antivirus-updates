from gui.dashboard import start_dashboard
import sys
import os

if __name__ == "__main__":
    # Check for --minimized flag (start minimized to tray)
    if "--minimized" in sys.argv:
        # Start with tray only
        start_dashboard()
    else:
        start_dashboard()