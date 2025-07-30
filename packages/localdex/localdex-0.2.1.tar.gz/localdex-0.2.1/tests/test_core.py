"""
Tests for the core LocalDex functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
import os
from pathlib import Path

from localdex.core import LocalDex
from localdex.exceptions import (
    PokemonNotFoundError, MoveNotFoundError, AbilityNotFoundError, 
    ItemNotFoundError, DataLoadError
)

class TestLocalDex:
    """Test the main LocalDex class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        self.test_data_dir = Path(self.temp_dir) / "data"
        self.test_data_dir.mkdir(parents=True)
        
        # Create minimal test data structure
        (self.test_data_dir / "pokemon").mkdir()
        (self.test_data_dir / "moves").mkdir()
        (self.test_data_dir / "abilities").mkdir()
        (self.test_data_dir / "items").mkdir()
        
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_localdex_initialization(self):
        """Test LocalDex can be initialized."""
        dex = LocalDex(data_dir=str(self.test_data_dir))
        assert dex is not None
        assert dex.data_dir == str(self.test_data_dir)
    
    def test_localdex_default_initialization(self):
        """Test LocalDex initialization with default data directory."""
        dex = LocalDex()
        assert dex is not None
        # Should use default data directory
        assert hasattr(dex, 'data_dir')
    
    @patch('localdex.core.DataLoader.load_pokemon_by_name')
    def test_get_pokemon_not_found(self, mock_load):
        """Test getting a Pokemon that doesn't exist."""
        mock_load.return_value = None
        dex = LocalDex(data_dir=str(self.test_data_dir))
        
        with pytest.raises(PokemonNotFoundError):
            dex.get_pokemon("nonexistent")
    
    @patch('localdex.core.DataLoader.load_pokemon_by_id')
    def test_get_pokemon_by_id_not_found(self, mock_load):
        """Test getting a Pokemon by ID that doesn't exist."""
        mock_load.return_value = None
        dex = LocalDex(data_dir=str(self.test_data_dir))
        
        with pytest.raises(PokemonNotFoundError):
            dex.get_pokemon_by_id(99999)
    
    @patch('localdex.core.DataLoader.load_move')
    def test_get_move_not_found(self, mock_load):
        """Test getting a move that doesn't exist."""
        mock_load.return_value = None
        dex = LocalDex(data_dir=str(self.test_data_dir))
        
        with pytest.raises(MoveNotFoundError):
            dex.get_move("nonexistent")
    
    @patch('localdex.core.DataLoader.load_ability')
    def test_get_ability_not_found(self, mock_load):
        """Test getting an ability that doesn't exist."""
        mock_load.return_value = None
        dex = LocalDex(data_dir=str(self.test_data_dir))
        
        with pytest.raises(AbilityNotFoundError):
            dex.get_ability("nonexistent")
    
    @patch('localdex.core.DataLoader.load_item')
    def test_get_item_not_found(self, mock_load):
        """Test getting an item that doesn't exist."""
        mock_load.return_value = None
        dex = LocalDex(data_dir=str(self.test_data_dir))
        
        with pytest.raises(ItemNotFoundError):
            dex.get_item("nonexistent")
    
    def test_search_pokemon_empty_result(self):
        """Test searching Pokemon with no results."""
        dex = LocalDex(data_dir=str(self.test_data_dir))
        results = dex.search_pokemon(type="nonexistent")
        assert results == []
    
    def test_get_all_pokemon_empty(self):
        """Test getting all Pokemon when none exist."""
        dex = LocalDex(data_dir=str(self.test_data_dir))
        results = dex.get_all_pokemon()
        assert results == []
    
    def test_get_all_moves_empty(self):
        """Test getting all moves when none exist."""
        dex = LocalDex(data_dir=str(self.test_data_dir))
        results = dex.get_all_moves()
        assert results == []
    
    def test_get_all_abilities_empty(self):
        """Test getting all abilities when none exist."""
        dex = LocalDex(data_dir=str(self.test_data_dir))
        results = dex.get_all_abilities()
        assert results == []
    
    def test_get_all_items_empty(self):
        """Test getting all items when none exist."""
        dex = LocalDex(data_dir=str(self.test_data_dir))
        results = dex.get_all_items()
        assert results == []



class TestDataLoader:
    """Test the data loading functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_data_dir = Path(self.temp_dir) / "data"
        self.test_data_dir.mkdir(parents=True)
        
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_load_nonexistent_data_directory(self):
        """Test loading data from a directory that doesn't exist."""
        # Disable sprite downloader to avoid directory creation issues
        dex = LocalDex(data_dir="/nonexistent/path")
        # Should not raise an error, just return empty results
        assert dex.get_all_pokemon() == []
        assert dex.get_all_moves() == []
        assert dex.get_all_abilities() == []
        assert dex.get_all_items() == [] 