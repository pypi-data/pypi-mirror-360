"""Unit tests for PersistenceService class.

This module contains comprehensive unit tests for the PersistenceService class,
following the pytest protocol with pure unit testing and mocked file I/O.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
from simpletimerbank.core.persistence import PersistenceService


class TestPersistenceService:
    """Test suite for PersistenceService class."""
    
    def test_init_with_custom_file_path(self) -> None:
        """Test PersistenceService initializes with custom file path."""
        custom_path = Path("custom_data.json")
        service = PersistenceService(custom_path)
        # Should not raise any errors
    
    def test_init_with_default_file_path(self) -> None:
        """Test PersistenceService initializes with default file path."""
        service = PersistenceService()
        # Should not raise any errors
    
    @patch('pathlib.Path.exists')
    def test_data_file_exists_returns_true_when_file_exists(self, mock_exists: Mock) -> None:
        """Test data_file_exists returns True when file exists."""
        mock_exists.return_value = True
        service = PersistenceService()
        assert service.data_file_exists() is True
    
    @patch('pathlib.Path.exists')
    def test_data_file_exists_returns_false_when_file_missing(self, mock_exists: Mock) -> None:
        """Test data_file_exists returns False when file is missing."""
        mock_exists.return_value = False
        service = PersistenceService()
        assert service.data_file_exists() is False
    
    def test_get_default_data_path_returns_correct_path(self) -> None:
        """Test get_default_data_path returns expected path."""
        service = PersistenceService()
        result = service.get_default_data_path()
        assert isinstance(result, Path)
        assert result.name == "simpletimerbank_data.json"
    
    @patch('builtins.open', new_callable=mock_open, read_data='{"balance": 300}')
    @patch('pathlib.Path.exists')
    def test_load_data_successful(self, mock_exists: Mock, mock_file: Mock) -> None:
        """Test loading data successfully from existing file."""
        mock_exists.return_value = True
        service = PersistenceService()
        
        result = service.load_data()
        
        expected = {"balance": 300}
        assert result == expected
        mock_file.assert_called_once()
    
    @patch('pathlib.Path.exists')
    def test_load_data_returns_empty_dict_when_file_missing(self, mock_exists: Mock) -> None:
        """Test loading data returns empty dict when file doesn't exist."""
        mock_exists.return_value = False
        service = PersistenceService()
        
        result = service.load_data()
        
        assert result == {}
    
    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    @patch('pathlib.Path.exists')
    def test_load_data_handles_json_decode_error(self, mock_exists: Mock, mock_file: Mock) -> None:
        """Test loading data handles JSON decode errors gracefully."""
        mock_exists.return_value = True
        service = PersistenceService()
        
        result = service.load_data()
        
        assert result == {}  # Should return empty dict on JSON error
    
    @patch('builtins.open', side_effect=OSError("Permission denied"))
    @patch('pathlib.Path.exists')
    def test_load_data_handles_file_read_error(self, mock_exists: Mock, mock_file: Mock) -> None:
        """Test loading data handles file read errors gracefully."""
        mock_exists.return_value = True
        service = PersistenceService()
        
        result = service.load_data()
        
        assert result == {}  # Should return empty dict on read error
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.parent')
    def test_save_data_successful(self, mock_parent: Mock, mock_file: Mock) -> None:
        """Test saving data successfully."""
        service = PersistenceService()
        data = {"balance": 450}
        
        result = service.save_data(data)
        
        assert result is True
        mock_file.assert_called_once()
    
    @patch('builtins.open', side_effect=OSError("Disk full"))
    def test_save_data_handles_file_write_error(self, mock_file: Mock) -> None:
        """Test saving data handles file write errors gracefully."""
        service = PersistenceService()
        data = {"balance": 450}
        
        result = service.save_data(data)
        
        assert result is False
    
    def test_save_data_validates_input_type(self) -> None:
        """Test save_data validates that input is a dictionary."""
        service = PersistenceService()
        
        # Test with non-dict input
        result = service.save_data("not a dict")  # type: ignore
        assert result is False
        
        result = service.save_data(123)  # type: ignore
        assert result is False
        
        result = service.save_data(None)  # type: ignore
        assert result is False
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.parent')
    def test_save_empty_dictionary(self, mock_parent: Mock, mock_file: Mock) -> None:
        """Test saving empty dictionary works correctly."""
        service = PersistenceService()
        data = {}
        
        result = service.save_data(data)
        
        assert result is True
        mock_file.assert_called_once()
    
    @patch('builtins.open', side_effect=json.JSONEncoder().encode)
    def test_save_data_handles_json_encode_error(self, mock_file: Mock) -> None:
        """Test saving data handles JSON encoding errors gracefully."""
        service = PersistenceService()
        # Create data that can't be JSON serialized
        data = {"balance": set([1, 2, 3])}  # Sets aren't JSON serializable
        
        result = service.save_data(data)
        
        assert result is False
    
    @patch('builtins.open', new_callable=mock_open)
    def test_save_data_creates_parent_directories(self, mock_file: Mock) -> None:
        """Test save_data creates parent directories if they don't exist."""
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.mkdir') as mock_mkdir:
            
            # Mock parent directory doesn't exist
            mock_exists.return_value = False
            
            service = PersistenceService()
            data = {"balance": 100}
            
            result = service.save_data(data)
            
            assert result is True
            # Directory creation should be called
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    

    
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.parent')
    def test_save_complex_data_structure(self, mock_parent: Mock, mock_file: Mock) -> None:
        """Test saving complex nested data structure."""
        service = PersistenceService()
        data = {
            "balance": 1500,
            "settings": {
                "theme": "dark",
                "notifications": True,
                "intervals": [60, 300, 900]
            },
            "history": [
                {"date": "2023-01-01", "time_used": 3600},
                {"date": "2023-01-02", "time_used": 1800}
            ]
        }
        
        result = service.save_data(data)
        
        assert result is True
        written_content = "".join(call.args[0] for call in mock_file().write.call_args_list)
        loaded_data = json.loads(written_content)
        assert loaded_data == data
    
    @patch('builtins.open', new_callable=mock_open, read_data='{"balance": 600}')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.parent')
    def test_load_save_roundtrip(self, mock_parent: Mock, mock_exists: Mock, mock_file: Mock) -> None:
        """Test that loading and saving data maintains consistency."""
        mock_exists.return_value = True
        service = PersistenceService()
        
        # Load data
        loaded_data = service.load_data()
        assert loaded_data == {"balance": 600}
        
        # Modify and save
        loaded_data["balance"] = 700
        loaded_data["new_field"] = "test"
        
        result = service.save_data(loaded_data)
        assert result is True 