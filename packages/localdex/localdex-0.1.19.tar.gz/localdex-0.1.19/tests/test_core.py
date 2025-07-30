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
from localdex.sprite_downloader import SpriteDownloader


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

    def test_sprite_downloader_integration(self):
        """Test that sprite downloader is integrated and exposes expected methods."""
        dex = LocalDex(data_dir=str(self.test_data_dir), enable_sprite_downloader=True)
        assert hasattr(dex, 'sprite_downloader')
        assert hasattr(dex, 'download_all_sprites')
        assert hasattr(dex, 'get_pokemon_sprite_path')
        assert hasattr(dex, 'get_item_sprite_path')
        assert hasattr(dex, 'get_sprite_metadata')
        assert hasattr(dex, 'list_available_sprites')

    def test_sprite_downloader_parallel_processing(self):
        """Test that sprite downloader can be configured with custom worker count."""
        # Test default workers
        dex_default = LocalDex(data_dir=str(self.test_data_dir), enable_sprite_downloader=True)
        assert dex_default.sprite_downloader.max_workers == 8
        
        # Test custom workers
        dex_custom = LocalDex(data_dir=str(self.test_data_dir), enable_sprite_downloader=True, sprite_max_workers=16)
        assert dex_custom.sprite_downloader.max_workers == 16
        
        # Test disabled sprite downloader
        dex_disabled = LocalDex(data_dir=str(self.test_data_dir), enable_sprite_downloader=False)
        assert dex_disabled.sprite_downloader is None

    @patch('localdex.sprite_downloader.SpriteDownloader.download_all_sprites')
    def test_download_all_sprites(self, mock_download):
        """Test download_all_sprites method calls SpriteDownloader."""
        dex = LocalDex(data_dir=str(self.test_data_dir), enable_sprite_downloader=True)
        mock_download.return_value = {'pokemon': 'mock_pokemon_dir', 'items': 'mock_item_dir'}
        result = dex.download_all_sprites()
        assert 'pokemon' in result and 'items' in result
        mock_download.assert_called_once()

    @patch('localdex.sprite_downloader.SpriteDownloader.get_pokemon_sprite_path')
    def test_get_pokemon_sprite_path(self, mock_get_path):
        """Test get_pokemon_sprite_path returns correct path."""
        dex = LocalDex(data_dir=str(self.test_data_dir), enable_sprite_downloader=True)
        mock_get_path.return_value = Path('/mock/path/pikachu.png')
        path = dex.get_pokemon_sprite_path('Pikachu')
        assert str(path).endswith('pikachu.png')
        mock_get_path.assert_called_with('Pikachu')

    @patch('localdex.sprite_downloader.SpriteDownloader.get_item_sprite_path')
    def test_get_item_sprite_path(self, mock_get_path):
        """Test get_item_sprite_path returns correct path."""
        dex = LocalDex(data_dir=str(self.test_data_dir), enable_sprite_downloader=True)
        mock_get_path.return_value = Path('/mock/path/leftovers.png')
        path = dex.get_item_sprite_path('Leftovers')
        assert str(path).endswith('leftovers.png')
        mock_get_path.assert_called_with('Leftovers')

    @patch('localdex.sprite_downloader.SpriteDownloader.get_sprite_metadata')
    def test_get_sprite_metadata(self, mock_metadata):
        """Test get_sprite_metadata returns metadata dict."""
        dex = LocalDex(data_dir=str(self.test_data_dir), enable_sprite_downloader=True)
        mock_metadata.return_value = {'Pikachu': {'filename': 'pikachu.png'}}
        meta = dex.get_sprite_metadata('pokemon')
        assert 'Pikachu' in meta
        mock_metadata.assert_called_with('pokemon')

    @patch('localdex.sprite_downloader.SpriteDownloader.list_available_sprites')
    def test_list_available_sprites(self, mock_list):
        """Test list_available_sprites returns list of sprite names."""
        dex = LocalDex(data_dir=str(self.test_data_dir), enable_sprite_downloader=True)
        mock_list.return_value = ['pikachu', 'bulbasaur']
        names = dex.list_available_sprites('pokemon')
        assert 'pikachu' in names
        mock_list.assert_called_with('pokemon')


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
        dex = LocalDex(data_dir="/nonexistent/path", enable_sprite_downloader=False)
        # Should not raise an error, just return empty results
        assert dex.get_all_pokemon() == []
        assert dex.get_all_moves() == []
        assert dex.get_all_abilities() == []
        assert dex.get_all_items() == [] 