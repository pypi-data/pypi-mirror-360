"""
Core LocalDex functionality.

This module contains the main LocalDex class that provides access to
Pokemon data with caching, search capabilities, and data loading.
"""

import json
import os
import glob
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Set
from functools import lru_cache

from .models import Pokemon, Move, Ability, Item, BaseStats
from .exceptions import (
    PokemonNotFoundError, MoveNotFoundError, AbilityNotFoundError, 
    ItemNotFoundError, DataLoadError, SearchError
)
from .data_loader import DataLoader
from .random_battles import RandomBattleSets


class LocalDex:
    """
    Main class for accessing Pokemon data.
    
    This class provides fast, offline access to Pokemon data including
    Pokemon, moves, abilities, and items. It includes caching for
    performance and comprehensive search capabilities.
    """
    
    def __init__(self, data_path: Optional[str] = None, data_dir: Optional[str] = None, enable_caching: bool = True, enable_random_battles: bool = True):
        """
        Initialize the LocalDex.
        
        Args:
            data_path: Optional path to data directory. If None, uses package data.
            data_dir: Alias for data_path for backward compatibility.
            enable_caching: Whether to enable caching for better performance.
            enable_random_battles: Whether to enable random battle sets functionality.

        """
        # Use data_dir if provided, otherwise use data_path
        final_data_path = data_dir if data_dir is not None else data_path
        self.data_loader = DataLoader(final_data_path)
        self.data_dir = final_data_path  # Store for backward compatibility
        self.enable_caching = enable_caching

        
        # Initialize random battle sets
        self.random_battles = RandomBattleSets() if enable_random_battles else None
        
        # Initialize caches
        self._pokemon_cache: Dict[str, Pokemon] = {}
        self._pokemon_id_cache: Dict[int, Pokemon] = {}
        self._move_cache: Dict[str, Move] = {}
        self._ability_cache: Dict[str, Ability] = {}
        self._item_cache: Dict[str, Item] = {}
        
        # Search indexes
        self._pokemon_by_type: Dict[str, Set[str]] = {}
        self._pokemon_by_generation: Dict[int, Set[str]] = {}
        self._moves_by_type: Dict[str, Set[str]] = {}
        self._moves_by_category: Dict[str, Set[str]] = {}
        
        # Load data if caching is enabled
        if self.enable_caching:
            self._build_indexes()
    
    def _build_indexes(self) -> None:
        """Build search indexes for faster lookups."""
        try:
            # Build Pokemon indexes
            all_pokemon = self.get_all_pokemon()
            
            for pokemon in all_pokemon:
                # Index by type
                for pokemon_type in pokemon.types:
                    if pokemon_type not in self._pokemon_by_type:
                        self._pokemon_by_type[pokemon_type] = set()
                    self._pokemon_by_type[pokemon_type].add(pokemon.name.lower())
                
                # Index by generation
                if pokemon.generation:
                    if pokemon.generation not in self._pokemon_by_generation:
                        self._pokemon_by_generation[pokemon.generation] = set()
                    self._pokemon_by_generation[pokemon.generation].add(pokemon.name.lower())
            
            # Build move indexes
            all_moves = self.get_all_moves()
            
            for move in all_moves:
                # Index by type
                if move.type not in self._moves_by_type:
                    self._moves_by_type[move.type] = set()
                self._moves_by_type[move.type].add(move.name.lower())
                
                # Index by category
                if move.category not in self._moves_by_category:
                    self._moves_by_category[move.category] = set()
                self._moves_by_category[move.category].add(move.name.lower())
                
        except Exception as e:
            # If indexing fails, continue without indexes
            pass
    
    def get_pokemon(self, name_or_id: Union[str, int]) -> Pokemon:
        """
        Get a Pokemon by name or ID.
        
        Args:
            name_or_id: Pokemon name (case-insensitive) or ID number
            
        Returns:
            Pokemon object
            
        Raises:
            PokemonNotFoundError: If Pokemon is not found
        """
        if isinstance(name_or_id, int):
            return self.get_pokemon_by_id(name_or_id)
        else:
            return self.get_pokemon_by_name(name_or_id)
    
    def get_pokemon_by_id(self, pokemon_id: int) -> Pokemon:
        """
        Get a Pokemon by ID.
        
        Args:
            pokemon_id: Pokemon ID number
            
        Returns:
            Pokemon object
            
        Raises:
            PokemonNotFoundError: If Pokemon is not found
        """
        # Check cache first
        if self.enable_caching and pokemon_id in self._pokemon_id_cache:
            return self._pokemon_id_cache[pokemon_id]
        
        # Load from data
        pokemon_data = self.data_loader.load_pokemon_by_id(pokemon_id)
        if not pokemon_data:
            raise PokemonNotFoundError(str(pokemon_id))
        
        pokemon = self._create_pokemon_from_data(pokemon_data)
        
        # Cache the result
        if self.enable_caching:
            self._pokemon_id_cache[pokemon_id] = pokemon
            self._pokemon_cache[pokemon.name.lower()] = pokemon
        
        return pokemon
    
    def get_pokemon_by_name(self, name: str) -> Pokemon:
        """
        Get a Pokemon by name.
        
        Args:
            name: Pokemon name (case-insensitive)
            
        Returns:
            Pokemon object
            
        Raises:
            PokemonNotFoundError: If Pokemon is not found
        """
        name_lower = name.lower()
        
        # Check cache first
        if self.enable_caching and name_lower in self._pokemon_cache:
            return self._pokemon_cache[name_lower]
        
        # Load from data
        pokemon_data = self.data_loader.load_pokemon_by_name(name)
        if not pokemon_data:
            raise PokemonNotFoundError(name)
        
        pokemon = self._create_pokemon_from_data(pokemon_data)
        
        # Cache the result
        if self.enable_caching:
            self._pokemon_cache[name_lower] = pokemon
            self._pokemon_id_cache[pokemon.id] = pokemon
        
        return pokemon
    
    def get_move(self, name: str) -> Move:
        """
        Get a move by name.
        
        Args:
            name: Move name (case-insensitive)
            
        Returns:
            Move object
            
        Raises:
            MoveNotFoundError: If move is not found
        """
        name_lower = name.lower()
        
        # Check cache first
        if self.enable_caching and name_lower in self._move_cache:
            return self._move_cache[name_lower]
        
        # Load from data
        move_data = self.data_loader.load_move(name)
        if not move_data:
            raise MoveNotFoundError(name)
        
        move = self._create_move_from_data(move_data)
        
        # Cache the result
        if self.enable_caching:
            self._move_cache[name_lower] = move
        
        return move
    
    def get_ability(self, name: str) -> Ability:
        """
        Get an ability by name.
        
        Args:
            name: Ability name (case-insensitive)
            
        Returns:
            Ability object
            
        Raises:
            AbilityNotFoundError: If ability is not found
        """
        name_lower = name.lower()
        
        # Check cache first
        if self.enable_caching and name_lower in self._ability_cache:
            return self._ability_cache[name_lower]
        
        # Load from data
        ability_data = self.data_loader.load_ability(name)
        if not ability_data:
            raise AbilityNotFoundError(name)
        
        ability = self._create_ability_from_data(ability_data)
        
        # Cache the result
        if self.enable_caching:
            self._ability_cache[name_lower] = ability
        
        return ability
    
    def get_item(self, name: str) -> Item:
        """
        Get an item by name.
        
        Args:
            name: Item name (case-insensitive)
            
        Returns:
            Item object
            
        Raises:
            ItemNotFoundError: If item is not found
        """
        name_lower = name.lower()
        
        # Check cache first
        if self.enable_caching and name_lower in self._item_cache:
            return self._item_cache[name_lower]
        
        # Load from data
        item_data = self.data_loader.load_item(name)
        if not item_data:
            raise ItemNotFoundError(name)
        
        item = self._create_item_from_data(item_data)
        
        # Cache the result
        if self.enable_caching:
            self._item_cache[name_lower] = item
        
        return item
    
    def search_pokemon(self, **filters) -> List[Pokemon]:
        """
        Search for Pokemon using various filters.
        
        Args:
            **filters: Search filters including:
                - type: Pokemon type (e.g., "Fire", "Water")
                - generation: Generation number (1-9)
                - min_attack: Minimum attack stat
                - max_attack: Maximum attack stat
                - min_special_attack: Minimum special attack stat
                - max_special_attack: Maximum special attack stat
                - min_speed: Minimum speed stat
                - max_speed: Maximum speed stat
                - min_hp: Minimum HP stat
                - max_hp: Maximum HP stat
                - is_legendary: Whether Pokemon is legendary
                - is_mythical: Whether Pokemon is mythical
                - name_contains: Partial name match
                
        Returns:
            List of Pokemon matching the filters
        """
        try:
            # Use indexes for faster search if available
            if self.enable_caching and self._pokemon_by_type and self._pokemon_by_generation:
                return self._search_pokemon_with_indexes(**filters)
            else:
                return self._search_pokemon_full_scan(**filters)
        except Exception as e:
            raise SearchError(f"Error during Pokemon search: {e}")
    
    def _search_pokemon_with_indexes(self, **filters) -> List[Pokemon]:
        """Search Pokemon using pre-built indexes."""
        candidate_names = set()
        
        # Filter by type
        if "type" in filters:
            pokemon_type = filters["type"].lower()
            if pokemon_type in self._pokemon_by_type:
                if not candidate_names:
                    candidate_names = self._pokemon_by_type[pokemon_type].copy()
                else:
                    candidate_names &= self._pokemon_by_type[pokemon_type]
        
        # Filter by generation
        if "generation" in filters:
            generation = filters["generation"]
            if generation in self._pokemon_by_generation:
                if not candidate_names:
                    candidate_names = self._pokemon_by_generation[generation].copy()
                else:
                    candidate_names &= self._pokemon_by_generation[generation]
        
        # If no candidates from indexes, do full scan
        if not candidate_names:
            return self._search_pokemon_full_scan(**filters)
        
        # Load and filter candidates
        results = []
        for name in candidate_names:
            try:
                pokemon = self.get_pokemon_by_name(name)
                if self._pokemon_matches_filters(pokemon, filters):
                    results.append(pokemon)
            except PokemonNotFoundError:
                continue
        
        return results
    
    def _search_pokemon_full_scan(self, **filters) -> List[Pokemon]:
        """Search Pokemon by scanning all data."""
        results = []
        all_pokemon = self.get_all_pokemon()
        
        for pokemon in all_pokemon:
            if self._pokemon_matches_filters(pokemon, filters):
                results.append(pokemon)
        
        return results
    
    def _pokemon_matches_filters(self, pokemon: Pokemon, filters: Dict[str, Any]) -> bool:
        """Check if a Pokemon matches the given filters."""
        # Type filter
        if "type" in filters:
            if filters["type"].lower() not in [t.lower() for t in pokemon.types]:
                return False
        
        # Generation filter
        if "generation" in filters:
            if pokemon.generation != filters["generation"]:
                return False
        
        # Stat filters
        if "min_attack" in filters and pokemon.base_stats.attack < filters["min_attack"]:
            return False
        if "max_attack" in filters and pokemon.base_stats.attack > filters["max_attack"]:
            return False
        if "min_special_attack" in filters and pokemon.base_stats.special_attack < filters["min_special_attack"]:
            return False
        if "max_special_attack" in filters and pokemon.base_stats.special_attack > filters["max_special_attack"]:
            return False
        if "min_speed" in filters and pokemon.base_stats.speed < filters["min_speed"]:
            return False
        if "max_speed" in filters and pokemon.base_stats.speed > filters["max_speed"]:
            return False
        if "min_hp" in filters and pokemon.base_stats.hp < filters["min_hp"]:
            return False
        if "max_hp" in filters and pokemon.base_stats.hp > filters["max_hp"]:
            return False
        
        # Legendary/Mythical filters
        if "is_legendary" in filters and pokemon.is_legendary != filters["is_legendary"]:
            return False
        if "is_mythical" in filters and pokemon.is_mythical != filters["is_mythical"]:
            return False
        
        # Name contains filter
        if "name_contains" in filters:
            if filters["name_contains"].lower() not in pokemon.name.lower():
                return False
        
        return True
    
    def get_all_pokemon(self) -> List[Pokemon]:
        """Get all Pokemon."""
        pokemon_data_list = self.data_loader.load_all_pokemon()
        return [self._create_pokemon_from_data(data) for data in pokemon_data_list]
    
    def get_all_moves(self) -> List[Move]:
        """Get all moves."""
        move_data_list = self.data_loader.load_all_moves()
        return [self._create_move_from_data(data) for data in move_data_list]
    
    def get_all_abilities(self) -> List[Ability]:
        """Get all abilities."""
        ability_data_list = self.data_loader.load_all_abilities()
        return [self._create_ability_from_data(data) for data in ability_data_list]
    
    def get_all_items(self) -> List[Item]:
        """Get all items."""
        item_data_list = self.data_loader.load_all_items()
        return [self._create_item_from_data(data) for data in item_data_list]
    
    def _create_pokemon_from_data(self, data: Dict[str, Any]) -> Pokemon:
        """Create a Pokemon object from raw data."""
        # Create base stats
        base_stats_data = data.get("baseStats", {})
        base_stats = BaseStats(
            hp=base_stats_data.get("hp", 0),
            attack=base_stats_data.get("attack", base_stats_data.get("atk", 0)),
            defense=base_stats_data.get("defense", base_stats_data.get("def", 0)),
            special_attack=base_stats_data.get("special_attack", base_stats_data.get("spa", 0)),
            special_defense=base_stats_data.get("special_defense", base_stats_data.get("spd", 0)),
            speed=base_stats_data.get("speed", base_stats_data.get("spe", 0))
        )
        
        # Create Pokemon object
        pokemon = Pokemon(
            id=data.get("id", 0),
            name=data.get("name", ""),
            types=data.get("types", []),
            base_stats=base_stats,
            height=data.get("height"),
            weight=data.get("weight"),
            color=data.get("color"),
            evolutions=data.get("evolutions"),
            prevo=data.get("prevo"),
            evo_level=data.get("evoLevel"),
            evo_type=data.get("evoType"),
            evo_condition=data.get("evoCondition"),
            evo_item=data.get("evoItem"),
            egg_groups=data.get("eggGroups"),
            gender_ratio=data.get("genderRatio"),
            generation=data.get("generation"),
            description=data.get("description"),
            is_legendary=data.get("isLegendary", False),
            is_mythical=data.get("isMythical", False),
            is_ultra_beast=data.get("isUltraBeast", False),
            random_battle_sets=data.get("randomBattleSets"),
            metadata=data
        )
        
        # Add abilities
        abilities_data = data.get("abilities", {})
        for slot, ability_data in abilities_data.items():
            if isinstance(ability_data, dict) and "data" in ability_data:
                ability = self._create_ability_from_data(ability_data["data"])
                pokemon.abilities[slot] = ability
        
        # Add moves
        moves_data = data.get("moves", [])
        for move_data in moves_data:
            if isinstance(move_data, dict):
                move = self._create_move_from_data(move_data)
                pokemon.moves.append(move)
        
        return pokemon
    
    def _create_move_from_data(self, data: Dict[str, Any]) -> Move:
        """Create a Move object from raw data."""
        return Move(
            name=data.get("name", ""),
            type=data.get("type", "Normal"),
            category=data.get("category", "Status"),
            base_power=data.get("basePower", 0),
            accuracy=data.get("accuracy", 100),
            pp=data.get("pp", 10),
            priority=data.get("priority", 0),
            target=data.get("target", "normal"),
            description=data.get("desc"),
            short_description=data.get("shortDesc"),
            contest_type=data.get("contestType"),
            crit_ratio=data.get("critRatio", 1),
            secondary_effects=data.get("secondary"),
            flags=data.get("flags", {}),
            drain=data.get("drain"),
            z_move=data.get("isZ"),
            z_move_type=data.get("zMoveType"),
            z_move_from=data.get("zMoveFrom"),
            generation=data.get("num"),
            is_nonstandard=data.get("isNonstandard"),
            metadata=data
        )
    
    def _create_ability_from_data(self, data: Dict[str, Any]) -> Ability:
        """Create an Ability object from raw data."""
        return Ability(
            name=data.get("name", ""),
            description=data.get("description", data.get("desc", "")),
            short_description=data.get("short_description", data.get("shortDesc", "")),
            generation=data.get("generation", data.get("gen")),
            rating=data.get("rating"),
            num=data.get("num"),
            effect=data.get("effect"),
            effect_entries=data.get("effect_entries"),
            metadata=data
        )
    
    def _create_item_from_data(self, data: Dict[str, Any]) -> Item:
        """Create an Item object from raw data."""
        return Item(
            name=data.get("name", ""),
            description=data.get("desc"),
            short_description=data.get("shortDesc"),
            generation=data.get("gen"),
            num=data.get("num"),
            spritenum=data.get("spritenum"),
            fling=data.get("fling"),
            mega_stone=data.get("megaStone"),
            mega_evolves=data.get("megaEvolves"),
            z_move=data.get("zMove"),
            z_move_type=data.get("zMoveType"),
            z_move_from=data.get("zMoveFrom"),
            item_user=data.get("itemUser"),
            on_plate=data.get("onPlate"),
            on_drive=data.get("onDrive"),
            on_memory=data.get("onMemory"),
            forced_forme=data.get("forcedForme"),
            is_nonstandard=data.get("isNonstandard"),
            category=data.get("category"),
            metadata=data
        )
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        self._pokemon_cache.clear()
        self._pokemon_id_cache.clear()
        self._move_cache.clear()
        self._ability_cache.clear()
        self._item_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            "pokemon_by_name": len(self._pokemon_cache),
            "pokemon_by_id": len(self._pokemon_id_cache),
            "moves": len(self._move_cache),
            "abilities": len(self._ability_cache),
            "items": len(self._item_cache)
        }
    
    # Random Battle Sets Methods
    
    def get_random_battle_sets(self, pokemon_name: str, generation: int = 9, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get random battle sets for a specific Pokemon.
        
        Args:
            pokemon_name: Name of the Pokemon (case-insensitive)
            generation: Generation to get sets from (8 or 9)
            force_refresh: If True, re-download data
            
        Returns:
            Pokemon's random battle sets or None if not found
            
        Raises:
            ValueError: If random battles are not enabled
        """
        if self.random_battles is None:
            raise ValueError("Random battle sets are not enabled. Set enable_random_battles=True when initializing LocalDex.")
        
        if generation == 9:
            return self.random_battles.get_pokemon_gen9_sets(pokemon_name, force_refresh)
        elif generation == 8:
            return self.random_battles.get_pokemon_gen8_data(pokemon_name, force_refresh)
        else:
            raise ValueError(f"Generation {generation} is not supported. Use 8 or 9.")
    
    def get_all_random_battle_sets(self, generation: int = 9, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get all random battle sets for a generation.
        
        Args:
            generation: Generation to get sets from (8 or 9)
            force_refresh: If True, re-download data
            
        Returns:
            Dictionary containing all random battle sets for the generation
            
        Raises:
            ValueError: If random battles are not enabled
        """
        if self.random_battles is None:
            raise ValueError("Random battle sets are not enabled. Set enable_random_battles=True when initializing LocalDex.")
        
        if generation == 9:
            return self.random_battles.get_gen9_sets(force_refresh)
        elif generation == 8:
            return self.random_battles.get_gen8_data(force_refresh)
        else:
            raise ValueError(f"Generation {generation} is not supported. Use 8 or 9.")
    
    def search_random_battle_pokemon_by_move(self, move_name: str, generation: int = 9, force_refresh: bool = False) -> List[str]:
        """
        Search for Pokemon that have a specific move in their random battle sets.
        
        Args:
            move_name: Name of the move to search for (case-insensitive)
            generation: Generation to search in (8 or 9)
            force_refresh: If True, re-download data
            
        Returns:
            List of Pokemon names that have the move
            
        Raises:
            ValueError: If random battles are not enabled
        """
        if self.random_battles is None:
            raise ValueError("Random battle sets are not enabled. Set enable_random_battles=True when initializing LocalDex.")
        
        return self.random_battles.search_pokemon_by_move(move_name, generation, force_refresh)
    
    def search_random_battle_pokemon_by_ability(self, ability_name: str, generation: int = 9, force_refresh: bool = False) -> List[str]:
        """
        Search for Pokemon that have a specific ability in their random battle sets.
        
        Args:
            ability_name: Name of the ability to search for (case-insensitive)
            generation: Generation to search in (8 or 9)
            force_refresh: If True, re-download data
            
        Returns:
            List of Pokemon names that have the ability
            
        Raises:
            ValueError: If random battles are not enabled
        """
        if self.random_battles is None:
            raise ValueError("Random battle sets are not enabled. Set enable_random_battles=True when initializing LocalDex.")
        
        return self.random_battles.search_pokemon_by_ability(ability_name, generation, force_refresh)
    
    def get_available_random_battle_generations(self) -> List[int]:
        """
        Get list of available generations for random battles.
        
        Returns:
            List of generation numbers
            
        Raises:
            ValueError: If random battles are not enabled
        """
        if self.random_battles is None:
            raise ValueError("Random battle sets are not enabled. Set enable_random_battles=True when initializing LocalDex.")
        
        return self.random_battles.get_available_generations()
    
    def get_random_battle_formats(self, generation: int) -> List[str]:
        """
        Get available formats for a specific generation.
        
        Args:
            generation: Generation number
            
        Returns:
            List of available format names
            
        Raises:
            ValueError: If random battles are not enabled
        """
        if self.random_battles is None:
            raise ValueError("Random battle sets are not enabled. Set enable_random_battles=True when initializing LocalDex.")
        
        return self.random_battles.get_generation_formats(generation)
    
    def clear_random_battle_cache(self) -> None:
        """Clear random battle cache."""
        if self.random_battles is not None:
            self.random_battles.clear_cache()
    
    def cleanup_random_battle_downloads(self) -> None:
        """Remove downloaded Pokemon Showdown repository."""
        if self.random_battles is not None:
            self.random_battles.cleanup_downloads()
    
    