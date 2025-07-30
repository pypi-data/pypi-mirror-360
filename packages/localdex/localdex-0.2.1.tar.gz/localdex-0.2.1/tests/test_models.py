"""
Tests for the LocalDex data models.
"""

import pytest
from localdex.models.pokemon import Pokemon, BaseStats
from localdex.models.move import Move
from localdex.models.ability import Ability
from localdex.models.item import Item


class TestBaseStats:
    """Test the BaseStats model."""
    
    def test_base_stats_creation(self):
        """Test creating BaseStats with valid data."""
        stats = BaseStats(
            hp=100,
            attack=110,
            defense=90,
            special_attack=120,
            special_defense=95,
            speed=105
        )
        
        assert stats.hp == 100
        assert stats.attack == 110
        assert stats.defense == 90
        assert stats.special_attack == 120
        assert stats.special_defense == 95
        assert stats.speed == 105
    
    def test_base_stats_total(self):
        """Test calculating total base stats."""
        stats = BaseStats(
            hp=100,
            attack=110,
            defense=90,
            special_attack=120,
            special_defense=95,
            speed=105
        )
        
        assert stats.total == 620
    
    def test_base_stats_repr(self):
        """Test BaseStats string representation."""
        stats = BaseStats(
            hp=100,
            attack=110,
            defense=90,
            special_attack=120,
            special_defense=95,
            speed=105
        )
        
        assert "BaseStats" in repr(stats)
        assert "hp=100" in repr(stats)


class TestPokemon:
    """Test the Pokemon model."""
    
    def test_pokemon_creation(self):
        """Test creating a Pokemon with valid data."""
        stats = BaseStats(
            hp=100,
            attack=110,
            defense=90,
            special_attack=120,
            special_defense=95,
            speed=105
        )
        
        pokemon = Pokemon(
            id=25,
            name="pikachu",
            types=["Electric"],
            base_stats=stats,
            height=0.4,
            weight=6.0,
            abilities={"0": {"name": "Static"}, "H": {"name": "Lightning Rod"}},
            moves=["thunderbolt", "quick-attack", "thunder-wave"],
            generation=1
        )
        
        assert pokemon.id == 25
        assert pokemon.name == "pikachu"
        assert pokemon.types == ["Electric"]
        assert pokemon.base_stats == stats
        assert pokemon.height == 0.4
        assert pokemon.weight == 6.0
        assert len(pokemon.abilities) == 2
        assert len(pokemon.moves) == 3
        assert pokemon.generation == 1
    
    def test_pokemon_repr(self):
        """Test Pokemon string representation."""
        stats = BaseStats(hp=100, attack=110, defense=90, 
                         special_attack=120, special_defense=95, speed=105)
        
        pokemon = Pokemon(
            id=25,
            name="pikachu",
            types=["Electric"],
            base_stats=stats,
            height=0.4,
            weight=6.0,
            abilities={},
            moves=[],
            generation=1
        )
        
        assert "Pokemon" in repr(pokemon)
        assert "pikachu" in repr(pokemon)
        assert "id=25" in repr(pokemon)


class TestMove:
    """Test the Move model."""
    
    def test_move_creation(self):
        """Test creating a Move with valid data."""
        move = Move(
            name="thunderbolt",
            type="Electric",
            category="Special",
            base_power=90,
            accuracy=100,
            pp=15,
            priority=0,
            target="selected-pokemon",
            description="A strong electric blast is loosed at the target.",
            generation="1"
        )
        
        assert move.name == "thunderbolt"
        assert move.type == "Electric"
        assert move.category == "Special"
        assert move.base_power == 90
        assert move.accuracy == 100
        assert move.pp == 15
        assert move.priority == 0
        assert move.target == "selected-pokemon"
        assert "electric blast" in move.description.lower()
        assert move.generation == "1"
    
    def test_move_repr(self):
        """Test Move string representation."""
        move = Move(
            name="thunderbolt",
            type="Electric",
            category="Special",
            base_power=90,
            accuracy=100,
            pp=15,
            priority=0,
            target="selected-pokemon",
            description="A strong electric blast.",
            generation="1"
        )
        
        assert "Move" in repr(move)
        assert "thunderbolt" in repr(move)


class TestAbility:
    """Test the Ability model."""
    
    def test_ability_creation(self):
        """Test creating an Ability with valid data."""
        ability = Ability(
            name="static",
            description="This Pokemon's body is charged with static electricity, making contact with it have a 30% chance to cause paralysis.",
            short_description="30% chance to paralyze on contact.",
            generation="1"
        )
        
        assert ability.name == "static"
        assert "static electricity" in ability.description.lower()
        assert "30%" in ability.short_description
        assert ability.generation == "1"
    
    def test_ability_repr(self):
        """Test Ability string representation."""
        ability = Ability(
            name="static",
            description="Static electricity effect.",
            short_description="30% paralysis chance.",
            generation="1"
        )
        
        assert "Ability" in repr(ability)
        assert "static" in repr(ability)


class TestItem:
    """Test the Item model."""
    
    def test_item_creation(self):
        """Test creating an Item with valid data."""
        item = Item(
            name="master-ball",
            description="The best Ball with the ultimate level of performance. With it, you will catch any wild Pokemon without fail.",
            category="pokeballs",
            cost=0,
            fling={"basePower": 0}
        )
        
        assert item.name == "master-ball"
        assert "best Ball" in item.description
        assert item.category == "pokeballs"
        assert item.cost == 0
        assert item.fling_power == 0
    
    def test_item_repr(self):
        """Test Item string representation."""
        item = Item(
            name="master-ball",
            description="The best Ball.",
            category="pokeballs",
            cost=0,
            fling={"basePower": 0}
        )
        
        assert "Item" in repr(item)
        assert "master-ball" in repr(item) 