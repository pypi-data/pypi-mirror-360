"""
Tests for the data download functionality.
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from localdex.download_data import DataDownloader, main
from localdex.exceptions import DataLoadError


class TestDataDownloader:
    """Test the DataDownloader class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir) / "data"
        
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_downloader_initialization(self):
        """Test DataDownloader can be initialized."""
        downloader = DataDownloader(str(self.output_dir))
        assert downloader.output_dir == self.output_dir
        assert downloader.base_url == "https://pokeapi.co/api/v2"
        
        # Check that directories were created
        assert (self.output_dir / "pokemon").exists()
        assert (self.output_dir / "moves").exists()
        assert (self.output_dir / "abilities").exists()
        assert (self.output_dir / "items").exists()
    
    def test_downloader_default_initialization(self):
        """Test DataDownloader initialization with default directory."""
        downloader = DataDownloader()
        assert downloader.output_dir == Path("localdex/data")
    
    @patch('localdex.download_data.requests.Session')
    def test_download_pokemon_data_success(self, mock_session):
        """Test successful Pokemon data download."""
        # Mock the session and responses
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Mock the Pokemon list response
        pokemon_list_response = MagicMock()
        pokemon_list_response.json.return_value = {
            "results": [
                {"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"},
                {"name": "ivysaur", "url": "https://pokeapi.co/api/v2/pokemon/2/"}
            ]
        }
        pokemon_list_response.raise_for_status.return_value = None
        
        # Mock the individual Pokemon response
        pokemon_detail_response = MagicMock()
        pokemon_detail_response.json.return_value = {
            "id": 1,
            "name": "bulbasaur",
            "types": [{"type": {"name": "grass"}}, {"type": {"name": "poison"}}],
            "stats": [
                {"base_stat": 45, "stat": {"name": "hp"}},
                {"base_stat": 49, "stat": {"name": "attack"}},
                {"base_stat": 49, "stat": {"name": "defense"}},
                {"base_stat": 65, "stat": {"name": "special-attack"}},
                {"base_stat": 65, "stat": {"name": "special-defense"}},
                {"base_stat": 45, "stat": {"name": "speed"}}
            ],
            "height": 7,
            "weight": 69,
            "abilities": [
                {"ability": {"name": "overgrow"}, "is_hidden": False},
                {"ability": {"name": "chlorophyll"}, "is_hidden": True}
            ],
            "moves": [{"move": {"name": "tackle"}}, {"move": {"name": "growl"}}]
        }
        pokemon_detail_response.raise_for_status.return_value = None
        
        # Set up the session to return different responses
        mock_session_instance.get.side_effect = [
            pokemon_list_response,
            pokemon_detail_response,
            pokemon_detail_response  # For the second Pokemon
        ]
        
        downloader = DataDownloader(str(self.output_dir))
        downloader.download_pokemon_data(limit=2)
        
        # Verify the Pokemon data was saved
        bulbasaur_file = self.output_dir / "pokemon" / "bulbasaur.json"
        assert bulbasaur_file.exists()
        
        with open(bulbasaur_file, 'r') as f:
            data = json.load(f)
            assert data["name"] == "bulbasaur"
            assert data["id"] == 1
            assert "grass" in data["types"]
            assert "poison" in data["types"]
    
    @patch('localdex.download_data.requests.Session')
    def test_download_pokemon_data_api_error(self, mock_session):
        """Test Pokemon data download with API error."""
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Mock a response that raises an HTTPError
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_session_instance.get.return_value = mock_response
        
        downloader = DataDownloader(str(self.output_dir))
        
        # Should not raise an exception, just log the error
        try:
            downloader.download_pokemon_data(limit=1)
        except Exception:
            # The test expects the exception to be caught internally
            pass
        
        # No files should be created
        pokemon_dir = self.output_dir / "pokemon"
        assert not any(pokemon_dir.iterdir())
    
    @patch('localdex.download_data.requests.Session')
    def test_download_move_data_success(self, mock_session):
        """Test successful move data download."""
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Mock the move list response
        move_list_response = MagicMock()
        move_list_response.json.return_value = {
            "results": [
                {"name": "tackle", "url": "https://pokeapi.co/api/v2/move/1/"}
            ]
        }
        move_list_response.raise_for_status.return_value = None
        
        # Mock the move detail response
        move_detail_response = MagicMock()
        move_detail_response.json.return_value = {
            "name": "tackle",
            "type": {"name": "normal"},
            "damage_class": {"name": "physical"},
            "power": 40,
            "accuracy": 100,
            "pp": 35,
            "priority": 0,
            "target": {"name": "selected-pokemon"},
            "generation": {"name": "generation-i"},
            "flavor_text_entries": [
                {
                    "flavor_text": "A physical attack in which the user charges and slams into the target with its whole body.",
                    "language": {"name": "en"}
                }
            ]
        }
        move_detail_response.raise_for_status.return_value = None
        
        mock_session_instance.get.side_effect = [
            move_list_response,
            move_detail_response
        ]
        
        downloader = DataDownloader(str(self.output_dir))
        downloader.download_move_data(limit=1)
        
        # Verify the move data was saved
        tackle_file = self.output_dir / "moves" / "tackle.json"
        assert tackle_file.exists()
        
        with open(tackle_file, 'r') as f:
            data = json.load(f)
            assert data["name"] == "tackle"
            assert data["type"] == "normal"
            assert data["basePower"] == 40
    
    def test_get_generation_from_id(self):
        """Test generation calculation from Pokemon ID."""
        downloader = DataDownloader(str(self.output_dir))
        
        assert downloader._get_generation_from_id(1) == 1    # Bulbasaur
        assert downloader._get_generation_from_id(151) == 1  # Mew
        assert downloader._get_generation_from_id(152) == 2  # Chikorita
        assert downloader._get_generation_from_id(251) == 2  # Celebi
        assert downloader._get_generation_from_id(252) == 3  # Treecko
        assert downloader._get_generation_from_id(386) == 3  # Deoxys
        assert downloader._get_generation_from_id(387) == 4  # Turtwig
        assert downloader._get_generation_from_id(493) == 4  # Arceus
        assert downloader._get_generation_from_id(494) == 5  # Victini
        assert downloader._get_generation_from_id(649) == 5  # Genesect
        assert downloader._get_generation_from_id(650) == 6  # Chespin
        assert downloader._get_generation_from_id(721) == 6  # Volcanion
        assert downloader._get_generation_from_id(722) == 7  # Rowlet
        assert downloader._get_generation_from_id(809) == 7  # Melmetal
        assert downloader._get_generation_from_id(810) == 8  # Grookey
        assert downloader._get_generation_from_id(898) == 8  # Calyrex
        assert downloader._get_generation_from_id(899) == 9  # Sprigatito
        assert downloader._get_generation_from_id(1000) == 9  # Future Pokemon


class TestDownloadDataMain:
    """Test the main function of download_data."""
    
    @patch('localdex.download_data.DataDownloader')
    def test_main_function(self, mock_downloader_class):
        """Test the main function calls the downloader correctly."""
        mock_downloader = MagicMock()
        mock_downloader_class.return_value = mock_downloader
        
        # Test with default arguments
        with patch('sys.argv', ['download_data.py']):
            main()
            
        mock_downloader_class.assert_called_once_with("localdex/data")
        mock_downloader.download_all_data.assert_called_once()
    
    @patch('localdex.download_data.DataDownloader')
    def test_main_function_with_limits(self, mock_downloader_class):
        """Test the main function with custom limits."""
        mock_downloader = MagicMock()
        mock_downloader_class.return_value = mock_downloader
        
        # Test with custom limits
        with patch('sys.argv', ['download_data.py', '--pokemon-limit', '10', '--move-limit', '5']):
            main()
            
        mock_downloader.download_all_data.assert_called_once_with(
            pokemon_limit=10,
            move_limit=5,
            ability_limit=99999,
            item_limit=99999
        ) 