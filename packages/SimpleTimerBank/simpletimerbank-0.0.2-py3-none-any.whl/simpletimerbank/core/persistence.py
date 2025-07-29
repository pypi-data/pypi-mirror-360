"""Data persistence service module.

This module contains the PersistenceService class responsible for saving
and loading application data to/from persistent storage.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class PersistenceService:
    """Manages data persistence for the SimpleTimerBank application.
    
    This class handles saving and loading application state (time balance,
    settings, etc.) to and from local storage files.
    """
    
    def __init__(self, data_file: Optional[Path] = None) -> None:
        """Initialize PersistenceService.
        
        Parameters
        ----------
        data_file : Path, optional
            Path to the data file. If None, uses default location.
        """
        if data_file is None:
            self._data_file = self.get_default_data_path()
        else:
            self._data_file = data_file
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """Save application data to persistent storage.
        
        Parameters
        ----------
        data : dict
            Dictionary containing application data to save.
            
        Returns
        -------
        bool
            True if save was successful, False otherwise.
        """
        # Validate input type
        if not isinstance(data, dict):
            return False
        
        try:
            # Ensure parent directory exists
            parent_dir = self._data_file.parent
            if not parent_dir.exists():
                parent_dir.mkdir(parents=True, exist_ok=True)
            
            # Write data to file as JSON
            with open(self._data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        
        except (OSError, TypeError, ValueError) as e:
            # Handle file I/O errors and JSON encoding errors
            return False
    
    def load_data(self) -> Dict[str, Any]:
        """Load application data from persistent storage.
        
        Returns
        -------
        dict
            Dictionary containing loaded application data.
            Returns empty dict if no data file exists.
        """
        # Return empty dict if file doesn't exist
        if not self.data_file_exists():
            return {}
        
        try:
            with open(self._data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        
        except (OSError, json.JSONDecodeError, ValueError) as e:
            # Handle file I/O errors and JSON decoding errors
            return {}
    
    def data_file_exists(self) -> bool:
        """Check if data file exists.
        
        Returns
        -------
        bool
            True if data file exists, False otherwise.
        """
        return self._data_file.exists()
    
    def get_default_data_path(self) -> Path:
        """Get the default data file path.
        
        Returns
        -------
        Path
            Default path for application data file.
        """
        return Path("simpletimerbank_data.json") 