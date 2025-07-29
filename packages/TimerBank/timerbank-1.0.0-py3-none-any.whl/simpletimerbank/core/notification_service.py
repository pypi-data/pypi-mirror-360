"""Notification service module.

This module provides a service for sending desktop notifications to the user.
It also includes functionality to play a notification sound.
"""

from __future__ import annotations

import os
import sys
import threading
from typing import TYPE_CHECKING

from plyer import notification
from playsound import playsound

if sys.version_info < (3, 9):
    import importlib_resources
else:
    from importlib import resources as importlib_resources

if TYPE_CHECKING:
    # Add type hints for static analysis tools
    pass


def _get_asset_path(filename: str) -> str:
    """Gets the absolute path to a resource file.

    This function handles path resolution for both normal execution
    and for when the app is bundled with PyInstaller.

    Parameters
    ----------
    filename : str
        The name of the file in the assets directory.

    Returns
    -------
    str
        The absolute path to the asset.
    """
    if getattr(sys, 'frozen', False):
        # Path when running from a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Path when running from source. Go up three levels from core -> simpletimerbank -> src -> project root.
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    
    return os.path.join(base_path, 'assets', filename)


class NotificationService:
    """Service for sending desktop notifications and playing sounds.
    
    This class handles sending various notifications and playing an alert sound.
    To use a custom sound, replace the `notification.wav` file in the
    `assets/sounds/` directory.
    """
    
    def __init__(self, app_name: str = "SimpleTimerBank"):
        """Initialize the NotificationService."""
        self._app_name = app_name

    def _play_notification_sound(self):
        """Plays the notification sound in a separate thread."""
        try:
            sound_ref = importlib_resources.files('simpletimerbank.assets.sounds').joinpath('notification.wav')
            with importlib_resources.as_file(sound_ref) as sound_path:
                playsound(str(sound_path), block=False)
        except Exception as e:
            # Log the error or handle it silently
            print(f"Error playing sound: {e}")

    def notify(self, title: str, message: str):
        """Send a notification and play a sound."""
        # Run sound playback in a separate thread to not block notifications
        sound_thread = threading.Thread(target=self._play_notification_sound)
        sound_thread.daemon = True
        sound_thread.start()

        notification.notify(
            title=f"{self._app_name} - {title}",
            message=message,
            app_name=self._app_name,
            timeout=10,
        )

    def notify_timer_completed(self) -> None:
        """Send a notification that the timer has completed its initial countdown.
        
        This notification is sent when the timer reaches zero and transitions
        to overdraft mode.
        """
        self.notify("Timer Completed", "Your timer has completed its initial countdown and is now withdrawing from your bank balance.")
    
    def notify_overdraft_started(self) -> None:
        """Send a notification that overdraft mode has started.
        
        This is similar to notify_timer_completed but with a focus on
        the fact that the bank is now being depleted.
        """
        self.notify("Overdraft Mode Started", "Your timer is now withdrawing time from your bank balance. Stop the timer to prevent further depletion.")
    
    def notify_bank_depleted(self) -> None:
        """Send a notification that the bank balance has been depleted.
        
        This notification is sent when the timer is in overdraft mode and
        the bank balance reaches zero.
        """
        self.notify("Bank Balance Depleted", "Your bank balance has been depleted. The timer has been stopped.") 