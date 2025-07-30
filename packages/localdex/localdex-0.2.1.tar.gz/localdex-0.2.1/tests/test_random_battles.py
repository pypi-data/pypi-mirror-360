"""
Tests for Random Battle Sets functionality.

This module tests the RandomBattleSets class and its integration with LocalDex.
"""

import pytest
import tempfile
import os
import shutil
import json
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from localdex.random_battles import RandomBattleSets
from localdex.core import LocalDex
from localdex.exceptions import DataLoadError


class TestRandomBattleSets:
    """Test cases for RandomBattleSets class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.random_battles = RandomBattleSets(cache_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_init_with_custom_cache_dir(self):
        """Test initialization with custom cache directory."""
        custom_dir = os.path.join(self.temp_dir, "custom_cache")
        rb = RandomBattleSets(cache_dir=custom_dir)
        assert rb.cache_dir == custom_dir
        assert os.path.exists(custom_dir)
    
    def test_init_with_default_cache_dir(self):
        """Test initialization with default cache directory."""
        rb = RandomBattleSets()
        assert "localdex_random_battles" in rb.cache_dir
        assert os.path.exists(rb.cache_dir)
    
    @patch('urllib.request.urlopen')
    def test_download_json_data_success(self, mock_urlopen):
        """Test successful download of JSON data."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"test": "data"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        cache_file = os.path.join(self.temp_dir, "test.json")
        result = self.random_battles._download_json_data("https://pkmn.github.io/randbats/data/gen9randombattle.json", cache_file)
        
        assert result is not None
        assert os.path.exists(cache_file)
    
    @patch('urllib.request.urlopen')
    def test_download_json_data_failure(self, mock_urlopen):
        """Test failed download of JSON data."""
        mock_urlopen.side_effect = Exception("Download failed")
        
        cache_file = os.path.join(self.temp_dir, "test.json")
        with pytest.raises(DataLoadError):
            self.random_battles._download_json_data("https://test.com/data.json", cache_file)
    
    def test_download_json_data_cached(self):
        """Test download when data is already cached."""
        # Create a cache file
        cache_file = os.path.join(self.temp_dir, "test.json")
        with open(cache_file, 'w') as f:
            json.dump({"cached": "data"}, f)
        
        # Should return cached data without downloading
        result = self.random_battles._download_json_data("https://pkmn.github.io/randbats/data/gen9randombattle.json", cache_file)
        assert result == {"cached": "data"}
    
    def test_get_gen9_sets_not_downloaded(self):
        """Test getting Gen 9 sets when data is not downloaded."""
        with patch.object(self.random_battles, '_download_json_data', side_effect=DataLoadError("Download failed")):
            with pytest.raises(DataLoadError):
                self.random_battles.get_gen9_sets()
    
    def test_get_gen8_data_not_downloaded(self):
        """Test getting Gen 8 data when data is not downloaded."""
        with patch.object(self.random_battles, '_download_json_data', side_effect=DataLoadError("Download failed")):
            with pytest.raises(DataLoadError):
                self.random_battles.get_gen8_data()
    
    def test_get_pokemon_gen9_sets_not_found(self):
        """Test getting Gen 9 sets for non-existent Pokemon."""
        # Mock the data to return empty dict
        with patch.object(self.random_battles, 'get_gen9_sets', return_value={}):
            result = self.random_battles.get_pokemon_gen9_sets("nonexistent")
            assert result is None
    
    def test_get_pokemon_gen8_data_not_found(self):
        """Test getting Gen 8 data for non-existent Pokemon."""
        # Mock the data to return empty dict
        with patch.object(self.random_battles, 'get_gen8_data', return_value={}):
            result = self.random_battles.get_pokemon_gen8_data("nonexistent")
            assert result is None
    
    def test_search_pokemon_by_move_gen9(self):
        """Test searching Pokemon by move in Gen 9."""
        mock_data = {
            "venusaur": {
                "moves": ["Giga Drain", "Leech Seed", "Sleep Powder"]
            },
            "charizard": {
                "moves": ["Flamethrower", "Earthquake", "Focus Blast"]
            }
        }
        
        with patch.object(self.random_battles, 'get_gen9_sets', return_value=mock_data):
            results = self.random_battles.search_pokemon_by_move("Giga Drain", generation=9)
            assert "venusaur" in results
            assert "charizard" not in results
    
    def test_search_pokemon_by_move_gen8(self):
        """Test searching Pokemon by move in Gen 8."""
        mock_data = {
            "venusaur": {
                "moves": ["gigadrain", "leechseed", "sleeppowder"]
            },
            "charizard": {
                "moves": ["fireblast", "earthquake", "focusblast"]
            }
        }
        
        with patch.object(self.random_battles, 'get_gen8_data', return_value=mock_data):
            results = self.random_battles.search_pokemon_by_move("gigadrain", generation=8)
            assert "venusaur" in results
            assert "charizard" not in results
    
    def test_search_pokemon_by_ability_gen9(self):
        """Test searching Pokemon by ability in Gen 9."""
        mock_data = {
            "venusaur": {
                "abilities": ["Chlorophyll", "Overgrow"]
            },
            "charizard": {
                "abilities": ["Blaze"]
            }
        }
        
        with patch.object(self.random_battles, 'get_gen9_sets', return_value=mock_data):
            results = self.random_battles.search_pokemon_by_ability("Chlorophyll", generation=9)
            assert "venusaur" in results
            assert "charizard" not in results
    
    def test_search_pokemon_by_ability_gen8(self):
        """Test searching Pokemon by ability in Gen 8 (should return empty list)."""
        mock_data = {
            "venusaur": {
                "moves": ["gigadrain", "leechseed"]
            }
        }
        
        with patch.object(self.random_battles, 'get_gen8_data', return_value=mock_data):
            results = self.random_battles.search_pokemon_by_ability("Chlorophyll", generation=8)
            assert results == []
    
    def test_get_available_generations(self):
        """Test getting available generations."""
        generations = self.random_battles.get_available_generations()
        assert generations == [8, 9]
    
    def test_get_generation_formats(self):
        """Test getting generation formats."""
        formats = self.random_battles.get_generation_formats(9)
        assert formats == ["randombattle"]
        
        formats = self.random_battles.get_generation_formats(7)
        assert formats == []
    
    def test_clear_cache(self):
        """Test clearing cache."""
        # Set some cache values
        self.random_battles._gen9_sets_cache = {"test": "data"}
        self.random_battles._gen8_data_cache = {"test2": "data2"}
        
        self.random_battles.clear_cache()
        
        assert self.random_battles._gen9_sets_cache is None
        assert self.random_battles._gen8_data_cache is None
    
    def test_cleanup_downloads(self):
        """Test cleanup of downloads."""
        # Create cache files
        cache_files = [
            os.path.join(self.random_battles.cache_dir, "gen8_randombattle.json"),
            os.path.join(self.random_battles.cache_dir, "gen9_randombattle.json")
        ]
        
        for cache_file in cache_files:
            with open(cache_file, 'w') as f:
                f.write('{"test": "data"}')
        
        self.random_battles.cleanup_downloads()
        
        for cache_file in cache_files:
            assert not os.path.exists(cache_file)


class TestLocalDexRandomBattles:
    """Test cases for LocalDex random battle integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Don't create LocalDex in setup to avoid downloads
        pass
    
    def test_init_with_random_battles_enabled(self):
        """Test initialization with random battles enabled."""
        localdex = LocalDex(enable_random_battles=True)
        assert localdex.random_battles is not None
        assert isinstance(localdex.random_battles, RandomBattleSets)
    
    def test_init_with_random_battles_disabled(self):
        """Test initialization with random battles disabled."""
        localdex = LocalDex(enable_random_battles=False)
        assert localdex.random_battles is None
    
    def test_get_random_battle_sets_not_enabled(self):
        """Test getting random battle sets when not enabled."""
        localdex = LocalDex(enable_random_battles=False)
        
        with pytest.raises(ValueError, match="Random battle sets are not enabled"):
            localdex.get_random_battle_sets("venusaur")
    
    def test_get_random_battle_sets_invalid_generation(self):
        """Test getting random battle sets with invalid generation."""
        with patch('localdex.core.RandomBattleSets') as mock_rb_class:
            mock_rb_instance = MagicMock()
            mock_rb_class.return_value = mock_rb_instance
            localdex = LocalDex(enable_random_battles=True)
            
            with pytest.raises(ValueError, match="Generation 7 is not supported"):
                localdex.get_random_battle_sets("venusaur", generation=7)
    
    def test_get_all_random_battle_sets_not_enabled(self):
        """Test getting all random battle sets when not enabled."""
        localdex = LocalDex(enable_random_battles=False)
        
        with pytest.raises(ValueError, match="Random battle sets are not enabled"):
            localdex.get_all_random_battle_sets()
    
    def test_search_random_battle_pokemon_by_move_not_enabled(self):
        """Test searching by move when random battles not enabled."""
        localdex = LocalDex(enable_random_battles=False)
        
        with pytest.raises(ValueError, match="Random battle sets are not enabled"):
            localdex.search_random_battle_pokemon_by_move("Giga Drain")
    
    def test_search_random_battle_pokemon_by_ability_not_enabled(self):
        """Test searching by ability when random battles not enabled."""
        localdex = LocalDex(enable_random_battles=False)
        
        with pytest.raises(ValueError, match="Random battle sets are not enabled"):
            localdex.search_random_battle_pokemon_by_ability("Chlorophyll")
    
    def test_get_available_random_battle_generations_not_enabled(self):
        """Test getting available generations when random battles not enabled."""
        localdex = LocalDex(enable_random_battles=False)
        
        with pytest.raises(ValueError, match="Random battle sets are not enabled"):
            localdex.get_available_random_battle_generations()
    
    def test_get_random_battle_formats_not_enabled(self):
        """Test getting formats when random battles not enabled."""
        localdex = LocalDex(enable_random_battles=False)
        
        with pytest.raises(ValueError, match="Random battle sets are not enabled"):
            localdex.get_random_battle_formats(9)
    
    def test_clear_random_battle_cache_not_enabled(self):
        """Test clearing cache when random battles not enabled."""
        localdex = LocalDex(enable_random_battles=False)
        # Should not raise an error
        localdex.clear_random_battle_cache()
    
    def test_cleanup_random_battle_downloads_not_enabled(self):
        """Test cleanup when random battles not enabled."""
        localdex = LocalDex(enable_random_battles=False)
        # Should not raise an error
        localdex.cleanup_random_battle_downloads()
    
    def test_get_random_battle_sets_gen9(self):
        """Test getting Gen 9 random battle sets."""
        with patch('localdex.core.RandomBattleSets') as mock_rb_class:
            mock_rb_instance = MagicMock()
            mock_rb_class.return_value = mock_rb_instance
            localdex = LocalDex(enable_random_battles=True)
            
            mock_data = {
                "level": 84,
                "sets": [
                    {
                        "role": "Bulky Support",
                        "movepool": ["Giga Drain", "Leech Seed", "Sleep Powder"]
                    }
                ]
            }
            mock_rb_instance.get_pokemon_gen9_sets.return_value = mock_data
            
            result = localdex.get_random_battle_sets("venusaur", generation=9)
            
            assert result == mock_data
            mock_rb_instance.get_pokemon_gen9_sets.assert_called_once_with("venusaur", False)
    
    def test_get_random_battle_sets_gen8(self):
        """Test getting Gen 8 random battle data."""
        with patch('localdex.core.RandomBattleSets') as mock_rb_class:
            mock_rb_instance = MagicMock()
            mock_rb_class.return_value = mock_rb_instance
            localdex = LocalDex(enable_random_battles=True)
            
            mock_data = {
                "level": 84,
                "moves": ["gigadrain", "leechseed", "sleeppowder"]
            }
            mock_rb_instance.get_pokemon_gen8_data.return_value = mock_data
            
            result = localdex.get_random_battle_sets("venusaur", generation=8)
            
            assert result == mock_data
            mock_rb_instance.get_pokemon_gen8_data.assert_called_once_with("venusaur", False)
    
    def test_get_all_random_battle_sets_gen9(self):
        """Test getting all Gen 9 random battle sets."""
        with patch('localdex.core.RandomBattleSets') as mock_rb_class:
            mock_rb_instance = MagicMock()
            mock_rb_class.return_value = mock_rb_instance
            localdex = LocalDex(enable_random_battles=True)
            
            mock_data = {"venusaur": {"level": 84, "sets": []}}
            mock_rb_instance.get_gen9_sets.return_value = mock_data
            
            result = localdex.get_all_random_battle_sets(generation=9)
            
            assert result == mock_data
            mock_rb_instance.get_gen9_sets.assert_called_once_with(False)
    
    def test_get_all_random_battle_sets_gen8(self):
        """Test getting all Gen 8 random battle data."""
        with patch('localdex.core.RandomBattleSets') as mock_rb_class:
            mock_rb_instance = MagicMock()
            mock_rb_class.return_value = mock_rb_instance
            localdex = LocalDex(enable_random_battles=True)
            
            mock_data = {"venusaur": {"level": 84, "moves": []}}
            mock_rb_instance.get_gen8_data.return_value = mock_data
            
            result = localdex.get_all_random_battle_sets(generation=8)
            
            assert result == mock_data
            mock_rb_instance.get_gen8_data.assert_called_once_with(False)
    
    def test_search_random_battle_pokemon_by_move(self):
        """Test searching Pokemon by move in random battles."""
        with patch('localdex.core.RandomBattleSets') as mock_rb_class:
            mock_rb_instance = MagicMock()
            mock_rb_class.return_value = mock_rb_instance
            localdex = LocalDex(enable_random_battles=True)
            
            mock_rb_instance.search_pokemon_by_move.return_value = ["venusaur", "vileplume"]
            
            result = localdex.search_random_battle_pokemon_by_move("Giga Drain", generation=9)
            
            assert result == ["venusaur", "vileplume"]
            mock_rb_instance.search_pokemon_by_move.assert_called_once_with("Giga Drain", 9, False)
    
    def test_search_random_battle_pokemon_by_ability(self):
        """Test searching Pokemon by ability in random battles."""
        with patch('localdex.core.RandomBattleSets') as mock_rb_class:
            mock_rb_instance = MagicMock()
            mock_rb_class.return_value = mock_rb_instance
            localdex = LocalDex(enable_random_battles=True)
            
            mock_rb_instance.search_pokemon_by_ability.return_value = ["venusaur"]
            
            result = localdex.search_random_battle_pokemon_by_ability("Chlorophyll", generation=9)
            
            assert result == ["venusaur"]
            mock_rb_instance.search_pokemon_by_ability.assert_called_once_with("Chlorophyll", 9, False)
    
    def test_get_available_random_battle_generations(self):
        """Test getting available random battle generations."""
        with patch('localdex.core.RandomBattleSets') as mock_rb_class:
            mock_rb_instance = MagicMock()
            mock_rb_class.return_value = mock_rb_instance
            localdex = LocalDex(enable_random_battles=True)
            
            mock_rb_instance.get_available_generations.return_value = [8, 9]
            
            result = localdex.get_available_random_battle_generations()
            
            assert result == [8, 9]
            mock_rb_instance.get_available_generations.assert_called_once()
    
    def test_get_random_battle_formats(self):
        """Test getting random battle formats."""
        with patch('localdex.core.RandomBattleSets') as mock_rb_class:
            mock_rb_instance = MagicMock()
            mock_rb_class.return_value = mock_rb_instance
            localdex = LocalDex(enable_random_battles=True)
            
            mock_rb_instance.get_generation_formats.return_value = ["sets", "factory-sets", "doubles-sets"]
            
            result = localdex.get_random_battle_formats(9)
            
            assert result == ["sets", "factory-sets", "doubles-sets"]
            mock_rb_instance.get_generation_formats.assert_called_once_with(9)
    
    def test_clear_random_battle_cache(self):
        """Test clearing random battle cache."""
        with patch('localdex.core.RandomBattleSets') as mock_rb_class:
            mock_rb_instance = MagicMock()
            mock_rb_class.return_value = mock_rb_instance
            localdex = LocalDex(enable_random_battles=True)
            
            localdex.clear_random_battle_cache()
            mock_rb_instance.clear_cache.assert_called_once()
    
    def test_cleanup_random_battle_downloads(self):
        """Test cleaning up random battle downloads."""
        with patch('localdex.core.RandomBattleSets') as mock_rb_class:
            mock_rb_instance = MagicMock()
            mock_rb_class.return_value = mock_rb_instance
            localdex = LocalDex(enable_random_battles=True)
            
            localdex.cleanup_random_battle_downloads()
            mock_rb_instance.cleanup_downloads.assert_called_once()


if __name__ == "__main__":
    # Run tests with Textual UI if available
    try:
        from textual.app import App
        from textual.widgets import DataTable, Header, Footer
        from textual.containers import Container
        
        class TestRunnerApp(App):
            """Textual app for running tests."""
            
            CSS = """
            DataTable {
                height: 1fr;
            }
            """
            
            def compose(self):
                yield Header()
                yield Container(DataTable())
                yield Footer()
            
            def on_mount(self):
                table = self.query_one(DataTable)
                table.add_columns("Test", "Status", "Message")
                
                # Run tests and display results
                import subprocess
                result = subprocess.run([
                    sys.executable, "-m", "pytest", __file__, "-v"
                ], capture_output=True, text=True)
                
                # Parse test results and add to table
                lines = result.stdout.split('\n')
                for line in lines:
                    if '::' in line and ('PASSED' in line or 'FAILED' in line):
                        parts = line.split('::')
                        test_name = parts[-1].split()[0]
                        status = "PASSED" if "PASSED" in line else "FAILED"
                        message = line.split('[')[0] if '[' in line else line
                        table.add_row(test_name, status, message)
        
        app = TestRunnerApp()
        app.run()
        
    except ImportError:
        # Fallback to regular pytest if Textual is not available
        pytest.main([__file__, "-v"]) 