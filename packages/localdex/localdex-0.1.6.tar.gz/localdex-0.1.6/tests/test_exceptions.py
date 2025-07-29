"""
Tests for the custom exceptions.
"""

import pytest
from localdex.exceptions import (
    LocalDexError,
    PokemonNotFoundError,
    MoveNotFoundError,
    AbilityNotFoundError,
    ItemNotFoundError,
    DataLoadError,
    ValidationError,
    SearchError,
    InvalidDataError
)


class TestExceptions:
    """Test the custom exceptions."""
    
    def test_localdex_error(self):
        """Test LocalDexError base exception."""
        error = LocalDexError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)
    
    def test_pokemon_not_found_error(self):
        """Test PokemonNotFoundError."""
        error = PokemonNotFoundError("pikachu")
        assert "pikachu" in str(error)
        assert isinstance(error, LocalDexError)
        assert isinstance(error, Exception)
    
    def test_pokemon_not_found_error_with_id(self):
        """Test PokemonNotFoundError with ID."""
        error = PokemonNotFoundError(25)
        assert "25" in str(error)
    
    def test_move_not_found_error(self):
        """Test MoveNotFoundError."""
        error = MoveNotFoundError("thunderbolt")
        assert "thunderbolt" in str(error)
        assert isinstance(error, LocalDexError)
    
    def test_ability_not_found_error(self):
        """Test AbilityNotFoundError."""
        error = AbilityNotFoundError("static")
        assert "static" in str(error)
        assert isinstance(error, LocalDexError)
    
    def test_item_not_found_error(self):
        """Test ItemNotFoundError."""
        error = ItemNotFoundError("master-ball")
        assert "master-ball" in str(error)
        assert isinstance(error, LocalDexError)
    
    def test_data_load_error(self):
        """Test DataLoadError."""
        error = DataLoadError("Failed to load data from file")
        assert "Failed to load data from file" in str(error)
        assert isinstance(error, LocalDexError)
    
    def test_invalid_data_error(self):
        """Test InvalidDataError."""
        error = InvalidDataError("Invalid JSON format")
        assert "Invalid JSON format" in str(error)
        assert isinstance(error, LocalDexError)
    
    def test_exception_inheritance(self):
        """Test that all exceptions inherit from LocalDexError."""
        exceptions = [
            PokemonNotFoundError,
            MoveNotFoundError,
            AbilityNotFoundError,
            ItemNotFoundError,
            DataLoadError,
            InvalidDataError
        ]
        
        for exception_class in exceptions:
            # Test that each exception can be instantiated
            error = exception_class("test")
            assert isinstance(error, LocalDexError)
            assert isinstance(error, Exception)
    
    def test_exception_messages(self):
        """Test that exceptions have meaningful messages."""
        # Test PokemonNotFoundError
        pokemon_error = PokemonNotFoundError("charizard")
        assert "charizard" in str(pokemon_error)
        assert "not found" in str(pokemon_error).lower()
        
        # Test MoveNotFoundError
        move_error = MoveNotFoundError("fire-blast")
        assert "fire-blast" in str(move_error)
        assert "not found" in str(move_error).lower()
        
        # Test AbilityNotFoundError
        ability_error = AbilityNotFoundError("blaze")
        assert "blaze" in str(ability_error)
        assert "not found" in str(ability_error).lower()
        
        # Test ItemNotFoundError
        item_error = ItemNotFoundError("ultra-ball")
        assert "ultra-ball" in str(item_error)
        assert "not found" in str(item_error).lower()
    
    def test_exception_with_custom_message(self):
        """Test exceptions with custom error messages."""
        custom_message = "Custom error message for testing"
        
        pokemon_error = PokemonNotFoundError("test", custom_message)
        assert custom_message in str(pokemon_error)
        
        move_error = MoveNotFoundError("test", custom_message)
        assert custom_message in str(move_error)
        
        ability_error = AbilityNotFoundError("test", custom_message)
        assert custom_message in str(ability_error)
        
        item_error = ItemNotFoundError("test", custom_message)
        assert custom_message in str(item_error) 