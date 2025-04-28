#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for the LectorCode application.
This module initializes the PyQt5 application and main window.
"""

import sys
import logging
from pathlib import Path

# Ensure the src directory is in the Python path
sys.path.insert(0, str(Path(__file__).parent))

# PyQt5 imports
from PyQt5 import QtWidgets
    
# Application imports
from src.ui.main_window import MainWindow


def setup_logging():
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Initialize and run the application."""
    # Setup logging
    setup_logging()
    
    # Suprimir warnings de fuentes no encontradas
    import os
    os.environ["QT_LOGGING_RULES"] = "qt.qpa.fonts=false"
    
    # Create application
    app = QtWidgets.QApplication(sys.argv)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())