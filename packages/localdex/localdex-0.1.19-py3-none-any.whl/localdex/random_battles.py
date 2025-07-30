"""
Random Battle Sets functionality for LocalDex.

This module provides functionality to download and parse Pokemon Showdown's
random battle sets from different generations and formats.
"""

import json
import os
import tempfile
from typing import Dict, List, Optional, Any, Union
from urllib.request import urlopen

from .exceptions import DataLoadError


class RandomBattleSets:
    """
    Handles downloading and parsing Pokemon Showdown random battle sets.
    
    This class provides methods to download random battle data from the
    pkmn.github.io/randbats API and parse it into a usable format.
    """
    
    # URLs for random battle data
    GEN8_URL = "https://pkmn.github.io/randbats/data/gen8randombattle.json"
    GEN9_URL = "https://pkmn.github.io/randbats/data/gen9randombattle.json"
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the RandomBattleSets handler.
        
        Args:
            cache_dir: Directory to cache downloaded data. If None, uses temp directory.
        """
        self.cache_dir = cache_dir or os.path.join(tempfile.gettempdir(), "localdex_random_battles")
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Cache for loaded data
        self._gen9_sets_cache: Optional[Dict[str, Any]] = None
        self._gen8_data_cache: Optional[Dict[str, Any]] = None
    
    def _download_json_data(self, url: str, cache_file: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Download JSON data from URL and cache it locally.
        
        Args:
            url: URL to download from
            cache_file: Local cache file path
            force_refresh: If True, re-download even if already cached
            
        Returns:
            Downloaded data as dictionary
            
        Raises:
            DataLoadError: If download fails
        """
        # Check if we have cached data and don't need to refresh
        if os.path.exists(cache_file) and not force_refresh:
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # If cache is corrupted, remove it and re-download
                pass
        
        try:
            print(f"Downloading random battle data from {url}...")
            with urlopen(url) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            # Cache the data
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            print("Random battle data downloaded successfully!")
            return data
            
        except Exception as e:
            raise DataLoadError(f"Failed to download data from {url}: {e}")
    
    def get_gen9_sets(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get Generation 9 random battle sets.
        
        Args:
            force_refresh: If True, re-download data
            
        Returns:
            Dictionary containing Gen 9 random battle sets
        """
        if self._gen9_sets_cache is not None and not force_refresh:
            return self._gen9_sets_cache
        
        cache_file = os.path.join(self.cache_dir, "gen9_randombattle.json")
        data = self._download_json_data(self.GEN9_URL, cache_file, force_refresh)
        
        self._gen9_sets_cache = data
        return data
    
    def get_gen8_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get Generation 8 random battle data.
        
        Args:
            force_refresh: If True, re-download data
            
        Returns:
            Dictionary containing Gen 8 random battle data
        """
        if self._gen8_data_cache is not None and not force_refresh:
            return self._gen8_data_cache
        
        cache_file = os.path.join(self.cache_dir, "gen8_randombattle.json")
        data = self._download_json_data(self.GEN8_URL, cache_file, force_refresh)
        
        self._gen8_data_cache = data
        return data
    

    
    def get_pokemon_gen9_sets(self, pokemon_name: str, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get Generation 9 random battle sets for a specific Pokemon.
        
        Args:
            pokemon_name: Name of the Pokemon (case-insensitive)
            force_refresh: If True, re-download data
            
        Returns:
            Pokemon's Gen 9 sets or None if not found
        """
        data = self.get_gen9_sets(force_refresh)
        return data.get(pokemon_name.lower())
    
    def get_pokemon_gen8_data(self, pokemon_name: str, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get Generation 8 random battle data for a specific Pokemon.
        
        Args:
            pokemon_name: Name of the Pokemon (case-insensitive)
            force_refresh: If True, re-download data
            
        Returns:
            Pokemon's Gen 8 data or None if not found
        """
        data = self.get_gen8_data(force_refresh)
        return data.get(pokemon_name.lower())
    
    def search_pokemon_by_move(self, move_name: str, generation: int = 9, force_refresh: bool = False) -> List[str]:
        """
        Search for Pokemon that have a specific move in their random battle sets.
        
        Args:
            move_name: Name of the move to search for (case-insensitive)
            generation: Generation to search in (8 or 9)
            force_refresh: If True, re-download data
            
        Returns:
            List of Pokemon names that have the move
        """
        move_name_lower = move_name.lower()
        results = []
        
        if generation == 9:
            data = self.get_gen9_sets(force_refresh)
            for pokemon_name, pokemon_data in data.items():
                if 'moves' in pokemon_data:
                    if any(move.lower() == move_name_lower for move in pokemon_data['moves']):
                        results.append(pokemon_name)
        elif generation == 8:
            data = self.get_gen8_data(force_refresh)
            for pokemon_name, pokemon_data in data.items():
                if 'moves' in pokemon_data:
                    if any(move.lower() == move_name_lower for move in pokemon_data['moves']):
                        results.append(pokemon_name)
        
        return results
    
    def search_pokemon_by_ability(self, ability_name: str, generation: int = 9, force_refresh: bool = False) -> List[str]:
        """
        Search for Pokemon that have a specific ability in their random battle sets.
        
        Args:
            ability_name: Name of the ability to search for (case-insensitive)
            generation: Generation to search in (8 or 9)
            force_refresh: If True, re-download data
            
        Returns:
            List of Pokemon names that have the ability
        """
        ability_name_lower = ability_name.lower()
        results = []
        
        if generation == 9:
            data = self.get_gen9_sets(force_refresh)
            for pokemon_name, pokemon_data in data.items():
                if 'abilities' in pokemon_data:
                    if any(ability.lower() == ability_name_lower for ability in pokemon_data['abilities']):
                        results.append(pokemon_name)
        elif generation == 8:
            data = self.get_gen8_data(force_refresh)
            for pokemon_name, pokemon_data in data.items():
                if 'abilities' in pokemon_data:
                    if any(ability.lower() == ability_name_lower for ability in pokemon_data['abilities']):
                        results.append(pokemon_name)
        
        return results
    
    def get_available_generations(self) -> List[int]:
        """
        Get list of available generations in the downloaded data.
        
        Returns:
            List of generation numbers
        """
        return [8, 9]  # Only Gen 8 and 9 are available via the API
    
    def get_generation_formats(self, generation: int) -> List[str]:
        """
        Get available formats for a specific generation.
        
        Args:
            generation: Generation number
            
        Returns:
            List of available format names
        """
        if generation in [8, 9]:
            return ["randombattle"]  # Only random battle format is available via the API
        return []
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._gen9_sets_cache = None
        self._gen8_data_cache = None
    
    def cleanup_downloads(self) -> None:
        """Remove downloaded cache files."""
        cache_files = [
            os.path.join(self.cache_dir, "gen8_randombattle.json"),
            os.path.join(self.cache_dir, "gen9_randombattle.json")
        ]
        
        for cache_file in cache_files:
            if os.path.exists(cache_file):
                os.remove(cache_file)
        
        self.clear_cache() 