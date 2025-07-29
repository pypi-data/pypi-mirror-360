"""SimpleTimerBank Desktop Application Entry Point.

This module serves as the main entry point for the SimpleTimerBank desktop application.
It initializes the PySide6 application and manages the application lifecycle.
"""

import sys
from typing import Optional

from PySide6.QtWidgets import QApplication
from simpletimerbank.core.app_state import AppStateManager
from simpletimerbank.gui.main_window import MainWindow


def main(argv: Optional[list[str]] = None) -> int:
    """Main application entry point.
    
    Initializes and runs the SimpleTimerBank desktop application.
    
    Parameters
    ----------
    argv : list[str], optional
        Command line arguments. If None, uses sys.argv.
        
    Returns
    -------
    int
        Application exit code (0 for success, non-zero for error).
        
    Examples
    --------
    >>> # To run the application (will open the GUI)
    >>> # if __name__ == "__main__":
    >>> #     sys.exit(main())
    """
    if argv is None:
        argv = sys.argv
    
    # Create the Qt application
    app = QApplication(argv)
    app.setApplicationName("SimpleTimerBank")
    app.setApplicationVersion("0.0.1")
    app.setOrganizationName("supersheepbear")
    
    # Initialize the core application logic manager
    app_manager = AppStateManager()
    app_manager.initialize()
    
    # Create and show the main window
    main_window = MainWindow(app_manager)
    main_window.show()
    
    # Start the application event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main()) 