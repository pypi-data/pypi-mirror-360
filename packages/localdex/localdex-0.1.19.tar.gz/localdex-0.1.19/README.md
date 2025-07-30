# LocalDex

A fast, offline-first Python library for Pokemon data access. LocalDex provides comprehensive Pokemon information without requiring network requests, making it perfect for applications that need reliable, fast access to Pokemon data.

[![PyPI version](https://badge.fury.io/py/localdex.svg)](https://badge.fury.io/py/localdex)
[![Python versions](https://img.shields.io/pypi/pyversions/localdex.svg)](https://pypi.org/project/localdex/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/colefoster/localdex/actions/workflows/release.yml/badge.svg)](https://github.com/colefoster/localdex/actions/workflows/release.yml)

## Features

- **100% Offline**: All data is stored locally - no network requests required
- **Fast Access**: Optimized for quick lookups and searches
- **Comprehensive Data**: Pokemon, moves, abilities, items, and more
- **Flexible Installation**: Choose which data sets to include
- **Type Hints**: Full type support for better development experience
- **Multiple Generations**: Support for all Pokemon generations
- **Competitive Data**: Includes battle sets and competitive information
- **Random Battle Sets**: Download and access Pokemon Showdown's random battle data

## Installation

### Basic Installation

```bash
pip install localdex
```

### Selective Data Installation

Install only the data you need to minimize package size:

```bash
# Core Pokemon data only
pip install localdex[core]

# Specific generation
pip install localdex[gen1]  # Generation 1 only
pip install localdex[gen9]  # Generation 9 only

# Additional data sets
pip install localdex[sprites]      # Pokemon sprites
pip install localdex[competitive]  # Competitive battle data
pip install localdex[learnsets]    # Detailed move learnsets
pip install localdex[items]        # Item data
pip install localdex[abilities]    # Ability data

# Full installation with everything
pip install localdex[full]
```


## Quick Start

```python
from localdex import LocalDex

# Initialize the dex
dex = LocalDex()

# Get Pokemon by name
pikachu = dex.get_pokemon("pikachu")
print(f"{pikachu.name} - {pikachu.types}")

# Get Pokemon by ID
charizard = dex.get_pokemon_by_id(6)
print(f"{charizard.name} - HP: {charizard.base_stats.hp}")

# Get Pokemon stats
bulbasaur = dex.get_pokemon("bulbasaur")
print(f"{bulbasaur.name} - Attack: {bulbasaur.base_stats.attack}, Speed: {bulbasaur.base_stats.speed}")

# Get moves
thunderbolt = dex.get_move("thunderbolt")
print(f"{thunderbolt.name} - Power: {thunderbolt.base_power}, Type: {thunderbolt.type}")

# Get abilities (note: use dashes in names like "lightning-rod")
lightning_rod = dex.get_ability("lightning-rod")
print(f"{lightning_rod.name} - {lightning_rod.description}")

# Search Pokemon by type (case-insensitive)
fire_types = dex.search_pokemon(type="fire")
print(f"Fire type Pokemon: {[p.name for p in fire_types[:5]]}")

# Search Pokemon by stat
fast_pokemon = dex.search_pokemon(min_speed=120)
print(f"Very fast Pokemon: {[p.name for p in fast_pokemon[:5]]}")

# Get all moves of a specific type (case-insensitive)
all_moves = dex.get_all_moves()
electric_moves = [m for m in all_moves if m.type.lower() == "electric"]
print(f"Electric moves count: {len(electric_moves)}")
print(f"First 5 Electric moves: {[m.name for m in electric_moves[:5]]}")

# Random Battle Sets (requires internet for initial download)
# Get random battle sets for a Pokemon
venusaur_sets = dex.get_random_battle_sets("venusaur", generation=9)
if venusaur_sets:
    print(f"Venusaur Gen 9 Level: {venusaur_sets.get('level')}")
    for set_data in venusaur_sets.get('sets', []):
        print(f"  Role: {set_data.get('role')}")
        print(f"  Moves: {', '.join(set_data.get('movepool', []))}")

# Search Pokemon by move in random battles
giga_drain_users = dex.search_random_battle_pokemon_by_move("Giga Drain", generation=9)
print(f"Pokemon with Giga Drain in Gen 9: {giga_drain_users[:5]}")

## API Reference

### LocalDex Class

The main class for accessing Pokemon data.

#### Methods

- `get_pokemon(name_or_id: Union[str, int]) -> Pokemon`: Get Pokemon by name or ID
- `get_pokemon_by_id(id: int) -> Pokemon`: Get Pokemon by ID
- `get_pokemon_by_name(name: str) -> Pokemon`: Get Pokemon by name
- `search_pokemon(**filters) -> List[Pokemon]`: Search Pokemon with filters
- `get_move(name: str) -> Move`: Get move by name
- `get_ability(name: str) -> Ability`: Get ability by name
- `get_item(name: str) -> Item`: Get item by name
- `get_all_pokemon() -> List[Pokemon]`: Get all Pokemon
- `get_all_moves() -> List[Move]`: Get all moves
- `get_all_abilities() -> List[Ability]`: Get all abilities
- `get_all_items() -> List[Item]`: Get all items

#### Random Battle Sets Methods

- `get_random_battle_sets(pokemon_name: str, generation: int = 9) -> Optional[Dict]`: Get random battle sets for a Pokemon
- `get_all_random_battle_sets(generation: int = 9) -> Dict`: Get all random battle sets for a generation
- `search_random_battle_pokemon_by_move(move_name: str, generation: int = 9) -> List[str]`: Search Pokemon by move in random battles
- `search_random_battle_pokemon_by_ability(ability_name: str, generation: int = 9) -> List[str]`: Search Pokemon by ability in random battles
- `get_available_random_battle_generations() -> List[int]`: Get available generations for random battles
- `get_random_battle_formats(generation: int) -> List[str]`: Get available formats for a generation

#### Search Filters

```python
# Search by type
fire_pokemon = dex.search_pokemon(type="Fire")

# Search by generation
gen1_pokemon = dex.search_pokemon(generation=1)

# Search by multiple criteria
legendary_fire = dex.search_pokemon(type="Fire", is_legendary=True)

# Search by base stat range
strong_pokemon = dex.search_pokemon(min_attack=100)
```

### Data Models

#### Pokemon

```python
class Pokemon:
    id: int
    name: str
    types: List[str]
    base_stats: BaseStats
    abilities: Dict[str, Ability]
    moves: List[Move]
    height: float
    weight: float
    description: str
    # ... and more
```

#### Move

```python
class Move:
    name: str
    type: str
    category: str
    base_power: int
    accuracy: int
    pp: int
    description: str
    # ... and more
```

#### Ability

```python
class Ability:
    name: str
    description: str
    short_description: str
    # ... and more
```

## Data Sets

LocalDex organizes data into logical sets that can be installed independently:

### Core Data (`core`)
- Basic Pokemon information (name, types, base stats)
- Essential for most applications

### Generation Data (`gen1`-`gen9`)
- Pokemon data for specific generations
- Useful for generation-specific applications

### Additional Data Sets
- **Sprites** (`sprites`): Pokemon images and sprites
- **Competitive** (`competitive`): Battle sets and competitive data
- **Learnsets** (`learnsets`): Detailed move learning information
- **Items** (`items`): Item data and effects
- **Abilities** (`abilities`): Detailed ability information

## Random Battle Sets

LocalDex can download and access Pokemon Showdown's random battle sets from different generations. This feature requires an internet connection for the initial download, but then works offline.

### Features

- **Multiple Generations**: Support for Gen 8 and Gen 9 random battles
- **Multiple Formats**: Standard sets, factory sets, doubles sets, and more
- **Search Capabilities**: Find Pokemon by moves or abilities in their random battle sets
- **Caching**: Downloaded data is cached for offline use
- **Optional**: Can be disabled to save memory and avoid downloads

### Usage

```python
from localdex import LocalDex

# Initialize with random battles enabled (default)
dex = LocalDex(enable_random_battles=True)

# Get random battle sets for a specific Pokemon
venusaur_sets = dex.get_random_battle_sets("venusaur", generation=9)
if venusaur_sets:
    print(f"Level: {venusaur_sets['level']}")
    for set_data in venusaur_sets['sets']:
        print(f"Role: {set_data['role']}")
        print(f"Moves: {', '.join(set_data['movepool'])}")
        print(f"Abilities: {', '.join(set_data['abilities'])}")
        print(f"Tera Types: {', '.join(set_data['teraTypes'])}")

# Search for Pokemon with specific moves
giga_drain_users = dex.search_random_battle_pokemon_by_move("Giga Drain", generation=9)
print(f"Pokemon with Giga Drain: {giga_drain_users}")

# Search for Pokemon with specific abilities
chlorophyll_users = dex.search_random_battle_pokemon_by_ability("Chlorophyll", generation=9)
print(f"Pokemon with Chlorophyll: {chlorophyll_users}")

# Get all random battle sets for a generation
all_gen9_sets = dex.get_all_random_battle_sets(generation=9)
print(f"Total Pokemon in Gen 9: {len(all_gen9_sets)}")

# Get available generations and formats
generations = dex.get_available_random_battle_generations()
formats = dex.get_random_battle_formats(9)
print(f"Available generations: {generations}")
print(f"Gen 9 formats: {formats}")

# Disable random battles to save memory
dex_lightweight = LocalDex(enable_random_battles=False)
```

### Data Structure

#### Generation 9 Sets
```json
{
  "venusaur": {
    "level": 84,
    "sets": [
      {
        "role": "Bulky Support",
        "movepool": ["Giga Drain", "Leech Seed", "Sleep Powder"],
        "abilities": ["Chlorophyll", "Overgrow"],
        "teraTypes": ["Steel", "Water"]
      }
    ]
  }
}
```

#### Generation 8 Data
```json
{
  "venusaur": {
    "level": 84,
    "moves": ["gigadrain", "leechseed", "sleeppowder"],
    "doublesMoves": ["earthpower", "energyball", "leechseed"],
    "doublesLevel": 80
  }
}
```

## CLI Usage

LocalDex includes a command-line interface for quick data access:

```bash
# Get Pokemon information
localdex pokemon pikachu

# Search Pokemon
localdex search --type Fire --generation 1

# Get move information
localdex move thunderbolt

# Get ability information
localdex ability lightningrod

# List all Pokemon
localdex list-pokemon

# Export data to JSON
localdex export --format json --output pokemon_data.json
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Data Sources

LocalDex uses data from:
- [Pokemon Showdown](https://github.com/smogon/pokemon-showdown)
- [PokeAPI](https://pokeapi.co/) (for initial data collection)

## Sprite Downloading and Usage

LocalDex can download and manage Pokémon and item sprites directly from Pokémon Showdown. This feature allows you to access local sprite images for use in your applications. The sprite extraction process uses parallel processing for significantly improved performance.

### Downloading Sprites

```python
from localdex import LocalDex

# Initialize with default parallel processing (8 workers)
dex = LocalDex()

# Download and extract all Pokémon and item sprites (requires internet for first run)
dex.download_all_sprites()

# Or customize the number of worker threads for parallel processing
dex_fast = LocalDex(sprite_max_workers=16)  # More workers for faster processing
dex_lightweight = LocalDex(sprite_max_workers=4)  # Fewer workers for lower resource usage
```

### Accessing Sprite Paths

```python
# Get the local file path to a Pokémon sprite
sprite_path = dex.get_pokemon_sprite_path("Pikachu")
print(sprite_path)  # e.g., /path/to/data/sprites/pokemon/pikachu.png

# Get the local file path to an item sprite
item_sprite_path = dex.get_item_sprite_path("Leftovers")
print(item_sprite_path)  # e.g., /path/to/data/sprites/items/leftovers.png
```

### Listing Available Sprites

```python
# List all available Pokémon sprites
pokemon_sprites = dex.list_available_sprites("pokemon")
print(pokemon_sprites)

# List all available item sprites
item_sprites = dex.list_available_sprites("items")
print(item_sprites)
```

### Accessing Sprite Metadata

```python
# Get metadata for all Pokémon sprites
pokemon_meta = dex.get_sprite_metadata("pokemon")
print(pokemon_meta["Pikachu"])

# Get metadata for all item sprites
item_meta = dex.get_sprite_metadata("items")
print(item_meta["Leftovers"])
```


