"""Notification service module.

This module provides a service for sending desktop notifications to the user.
It also includes functionality to play a notification sound.
"""

from plyer import notification
from playsound import playsound
import os
import sys
import threading


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
    
    def __init__(self) -> None:
        """Initialize the NotificationService."""
        self._app_name = "SimpleTimerBank"
        self._sound_file = _get_asset_path('sounds/notification.wav')

    def _play_sound(self) -> None:
        """Plays the notification sound in a separate thread to avoid blocking."""
        try:
            if os.path.exists(self._sound_file):
                # Run playsound in a new thread to avoid blocking the GUI
                sound_thread = threading.Thread(target=playsound, args=(self._sound_file,))
                sound_thread.daemon = True  # Allows main program to exit even if thread is running
                sound_thread.start()
        except Exception as e:
            # Silently fail if sound cannot be played
            print(f"Could not play notification sound: {e}")

    def notify_timer_completed(self) -> None:
        """Send a notification that the timer has completed its initial countdown.
        
        This notification is sent when the timer reaches zero and transitions
        to overdraft mode.
        """
        self._play_sound()
        notification.notify(
            title=f"{self._app_name} - Timer Completed",
            message="Your timer has completed its initial countdown and is now withdrawing from your bank balance.",
            app_name=self._app_name,
            timeout=10
        )
    
    def notify_overdraft_started(self) -> None:
        """Send a notification that overdraft mode has started.
        
        This is similar to notify_timer_completed but with a focus on
        the fact that the bank is now being depleted.
        """
        self._play_sound()
        notification.notify(
            title=f"{self._app_name} - Overdraft Mode Started",
            message="Your timer is now withdrawing time from your bank balance. Stop the timer to prevent further depletion.",
            app_name=self._app_name,
            timeout=10
        )
    
    def notify_bank_depleted(self) -> None:
        """Send a notification that the bank balance has been depleted.
        
        This notification is sent when the timer is in overdraft mode and
        the bank balance reaches zero.
        """
        self._play_sound()
        notification.notify(
            title=f"{self._app_name} - Bank Balance Depleted",
            message="Your bank balance has been depleted. The timer has been stopped.",
            app_name=self._app_name,
            timeout=10
        ) 