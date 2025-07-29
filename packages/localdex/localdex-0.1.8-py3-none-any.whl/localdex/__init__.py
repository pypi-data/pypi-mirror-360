"""
LocalDex - A fast, offline-first Python library for Pokemon data access.

This package provides comprehensive Pokemon information without requiring
network requests, making it perfect for applications that need reliable,
fast access to Pokemon data.
"""

__version__ = "0.1.0"
__author__ = "LocalDex Team"
__email__ = "localdex@example.com"

from .core import LocalDex
from .models import Pokemon, Move, Ability, Item, BaseStats
from .exceptions import PokemonNotFoundError, MoveNotFoundError, AbilityNotFoundError, ItemNotFoundError

__all__ = [
    "LocalDex",
    "Pokemon",
    "Move", 
    "Ability",
    "Item",
    "BaseStats",
    "PokemonNotFoundError",
    "MoveNotFoundError", 
    "AbilityNotFoundError",
    "ItemNotFoundError",
] 