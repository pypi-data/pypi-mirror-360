"""Time display widget for SimpleTimerBank.

This module provides a widget to display the time balance in a visually
appealing, read-only digital clock format.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout


class TimeDisplayWidget(QWidget):
    """A widget to display a time value using a large, digital-style label.
    
    This widget is used for displaying the main bank balance and is designed
    to be a clear, non-editable read-out of a time value formatted as HH:MM:SS.
    It supports a normal and an "overdraft" style to provide visual feedback.
    """
    
    def __init__(self, parent: QWidget = None, font_family: str = "Courier New") -> None:
        """Initialize the TimeDisplayWidget.
        
        Parameters
        ----------
        parent : QWidget, optional
            The parent widget of this component. Defaults to None.
        font_family : str
            The name of the font family to use for the digital display.
            Defaults to "Courier New".
        """
        super().__init__(parent)
        
        # Create the main layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create the time display label
        self._time_label = QLabel("00:00:00", self)
        font = QFont(font_family, 48, QFont.Weight.Bold)  # Reduced font size
        self._time_label.setFont(font)
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Define styles
        self._normal_style = """
            color: #FFD700;
            background-color: #1E1E1E;
            border: 2px solid #4A4A4A;
            border-radius: 10px;
            padding: 10px;
        """
        
        self._overdraft_style = """
            color: #FFFFFF;
            background-color: #8B0000;
            border: 2px solid #FF4500;
            border-radius: 10px;
            padding: 10px;
        """
        
        # Set initial style
        self._time_label.setStyleSheet(self._normal_style)
        
        # Add widgets to layout
        layout.addWidget(self._time_label)
        self.setLayout(layout)
        
        # Track overdraft state
        self._is_overdraft_mode = False
    
    def update_time(self, formatted_time: str) -> None:
        """Update the time displayed on the widget.
        
        Parameters
        ----------
        formatted_time : str
            The time string to display, formatted as HH:MM:SS.
        """
        self._time_label.setText(formatted_time)
    
    def set_overdraft_mode(self, is_overdraft: bool) -> None:
        """Set the visual style of the display to indicate overdraft status.
        
        In overdraft mode, the display uses a different color scheme (e.g., red)
        to visually indicate that the associated value is in a special state.
        
        Parameters
        ----------
        is_overdraft : bool
            True to switch to overdraft style, False for normal style.
        """
        if is_overdraft == self._is_overdraft_mode:
            return  # No change needed
            
        self._is_overdraft_mode = is_overdraft
        
        if is_overdraft:
            self._time_label.setStyleSheet(self._overdraft_style)
        else:
            self._time_label.setStyleSheet(self._normal_style) 