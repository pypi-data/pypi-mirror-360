"""
Sprite downloader for LocalDex.

This module handles downloading and managing Pokemon and item sprites
from Pokemon Showdown and other sources.
"""

import os
import sys
import re
import json
import glob
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile
import concurrent.futures
import threading
import requests
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional, Set, Union
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .exceptions import DataLoadError


class SpriteDownloader:
    """
    Downloads and manages Pokemon and item sprites.
    
    This class handles downloading spritesheets from Pokemon Showdown,
    extracting individual sprites, and managing sprite metadata.
    """
    
    def __init__(self, data_dir: Optional[str] = None, enable_progress_output: bool = False, max_workers: int = 8):
        """
        Initialize the sprite downloader.
        
        Args:
            data_dir: Directory to save sprites and metadata. If None, uses package data.
            enable_progress_output: Whether to output progress messages.
            max_workers: Maximum number of worker threads for parallel processing.
        """
        if data_dir is None:
            # Use package data directory
            package_dir = Path(__file__).parent
            self.data_dir = package_dir / "data"
        else:
            self.data_dir = Path(data_dir)
        
        # Create sprite directories
        self.sprites_dir = self.data_dir / "sprites"
        self.spritesheet_dir = self.data_dir / "spritesheets"
        self.pokemon_sprites_dir = self.sprites_dir / "pokemon"
        self.item_sprites_dir = self.sprites_dir / "items"
        
        for directory in [self.sprites_dir, self.spritesheet_dir, 
                         self.pokemon_sprites_dir, self.item_sprites_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.enable_progress_output = enable_progress_output
        self.max_workers = max_workers
        
        # Metadata files
        self.pokemon_coords_file = self.spritesheet_dir / "pokemon_sprite_coords.json"
        self.item_coords_file = self.spritesheet_dir / "item_sprite_coords.json"
        self.pokemon_metadata_file = self.spritesheet_dir / "pokemon_sprite_metadata.json"
        self.item_metadata_file = self.spritesheet_dir / "item_sprite_metadata.json"
    
    def _update_progress(self, progress: float, message: str = ""):
        """Update progress output."""
        if self.enable_progress_output:
            print(f"PROGRESS:{progress}:{message}", flush=True)
        else:
            print(f"Progress: {progress*100:.1f}% - {message}")
    
    def _update_status(self, message: str):
        """Update status output."""
        if self.enable_progress_output:
            print(f"STATUS:{message}", flush=True)
        else:
            print(f"Status: {message}")
    
    def _run_command(self, command: str) -> Tuple[int, str, str]:
        """
        Run a shell command and return the exit code, stdout, and stderr.
        
        Args:
            command (str): Command to run.
            
        Returns:
            Tuple[int, str, str]: Exit code, stdout, and stderr.
        """
        # Use a different approach on Windows to avoid shell issues
        if sys.platform == 'win32':
            try:
                # Split the command into parts for better Windows compatibility
                if isinstance(command, str):
                    command_parts = command.split()
                else:
                    command_parts = command
                    
                # Run the command with shell=False for better Windows compatibility
                process = subprocess.Popen(
                    command_parts,
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate()
                return process.returncode, stdout, stderr
            except Exception as e:
                # If there's an error with the non-shell approach, fall back to shell=True
                self._update_status(f"Warning: Non-shell command execution failed, falling back to shell: {e}")
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate()
                return process.returncode, stdout, stderr
        else:
            # On Unix-like systems, use the original approach
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            return process.returncode, stdout, stderr
    
    def download_pokemon_spritesheet(self) -> Path:
        """
        Download the Pokemon spritesheet from Pokemon Showdown.
        
        Returns:
            Path to the downloaded spritesheet
        """
        self._update_status("Checking for existing Pokemon spritesheet...")
        self._update_progress(0.0, "Starting Pokemon spritesheet check...")
        
        # URL of the Pokemon spritesheet
        spritesheet_url = "https://play.pokemonshowdown.com/sprites/pokemonicons-sheet.png"
        spritesheet_path = self.spritesheet_dir / "pokemonicons-sheet.png"
        
        # Check if the spritesheet already exists
        if spritesheet_path.exists():
            self._update_status(f"Using existing spritesheet from {spritesheet_path}")
            self._update_progress(1.0, "Using existing Pokemon spritesheet")
            
            # Verify the existing image
            try:
                img = Image.open(spritesheet_path)
                self._update_status(f"Spritesheet dimensions: {img.width}x{img.height}")
            except Exception as e:
                self._update_status(f"Warning: Could not verify existing spritesheet image: {e}")
                self._update_status("Will download a fresh copy...")
                # If verification fails, we'll download a fresh copy
            else:
                return spritesheet_path
        
        # Download the spritesheet if it doesn't exist or verification failed
        self._update_status("Downloading Pokemon spritesheet...")
        try:
            response = requests.get(spritesheet_url, stream=True)
            if response.status_code != 200:
                raise Exception(f"Failed to download spritesheet, status code: {response.status_code}")
            
            with open(spritesheet_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self._update_status(f"Spritesheet downloaded successfully to {spritesheet_path}")
            self._update_progress(1.0, "Pokemon spritesheet download complete")
            
            # Verify the downloaded image
            try:
                img = Image.open(spritesheet_path)
                self._update_status(f"Spritesheet dimensions: {img.width}x{img.height}")
            except Exception as e:
                self._update_status(f"Warning: Could not verify spritesheet image: {e}")
            
            return spritesheet_path
        except Exception as e:
            self._update_status(f"Error downloading Pokemon spritesheet: {str(e)}")
            raise
    
    def download_item_spritesheet(self) -> Path:
        """
        Download the item spritesheet from Pokemon Showdown.
        
        Returns:
            Path to the downloaded spritesheet
        """
        self._update_status("Checking for existing item spritesheet...")
        self._update_progress(0.0, "Starting item spritesheet check...")
        
        # URL of the item spritesheet
        spritesheet_url = "https://play.pokemonshowdown.com/sprites/itemicons-sheet.png"
        spritesheet_path = self.spritesheet_dir / "itemicons-sheet.png"
        
        # Check if the spritesheet already exists
        if spritesheet_path.exists():
            self._update_status(f"Using existing spritesheet from {spritesheet_path}")
            self._update_progress(1.0, "Using existing item spritesheet")
            
            # Verify the existing image
            try:
                img = Image.open(spritesheet_path)
                self._update_status(f"Spritesheet dimensions: {img.width}x{img.height}")
            except Exception as e:
                self._update_status(f"Warning: Could not verify existing spritesheet image: {e}")
                self._update_status("Will download a fresh copy...")
                # If verification fails, we'll download a fresh copy
            else:
                return spritesheet_path
        
        # Download the spritesheet if it doesn't exist or verification failed
        self._update_status("Downloading item spritesheet...")
        try:
            response = requests.get(spritesheet_url, stream=True)
            if response.status_code != 200:
                raise Exception(f"Failed to download spritesheet, status code: {response.status_code}")
            
            with open(spritesheet_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self._update_status(f"Spritesheet downloaded successfully to {spritesheet_path}")
            self._update_progress(1.0, "Item spritesheet download complete")
            
            # Verify the downloaded image
            try:
                img = Image.open(spritesheet_path)
                self._update_status(f"Spritesheet dimensions: {img.width}x{img.height}")
            except Exception as e:
                self._update_status(f"Warning: Could not verify spritesheet image: {e}")
            
            return spritesheet_path
        except Exception as e:
            self._update_status(f"Error downloading item spritesheet: {str(e)}")
            raise
    
    def parse_pokemon_sprite_coordinates(self) -> Dict[str, Dict[str, int]]:
        """
        Parse Pokemon sprite coordinates from the gallery test page.
        
        Returns:
            Dictionary mapping Pokemon names to their sprite coordinates
        """
        self._update_status("Checking for existing Pokemon sprite coordinates...")
        self._update_progress(0.0, "Starting coordinate check...")
        
        # Check if the coordinates JSON already exists
        if self.pokemon_coords_file.exists():
            self._update_status(f"Using existing coordinates from {self.pokemon_coords_file}")
            try:
                with open(self.pokemon_coords_file, 'r') as f:
                    pokemon_coords = json.load(f)
                
                self._update_status(f"Loaded coordinates for {len(pokemon_coords)} Pokemon")
                self._update_progress(1.0, "Using existing coordinates")
                return pokemon_coords
            except Exception as e:
                self._update_status(f"Error loading existing coordinates: {str(e)}")
                self._update_status("Will parse fresh coordinates...")
                # If loading fails, we'll parse fresh coordinates
        
        # URL of the gallery test page
        gallery_url = "https://play.pokemonshowdown.com/sprites/gallery-test.html"
        
        # Create a dictionary to store the Pokemon sprite coordinates
        pokemon_coords = {}
        
        # Add MissingNo. to the coordinates dictionary
        pokemon_coords["MissingNo."] = {
            "x": 0,
            "y": 0
        }

        # Set up Chrome options for headless browsing
        self._update_status("Setting up headless browser...")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        
        try:
            # Initialize the Chrome driver
            driver = webdriver.Chrome(options=chrome_options)
            
            # Navigate to the gallery page
            self._update_status(f"Navigating to {gallery_url}...")
            driver.get(gallery_url)
            
            # Wait for the page to load (wait for the table to be rendered)
            self._update_status("Waiting for page to load...")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            
            # Give the JavaScript some time to fully render the page
            time.sleep(2)
            
            # Find the navigation buttons to determine how many pages there are
            nav_buttons = driver.find_elements(By.CSS_SELECTOR, "ul li button")
            total_pages = len(nav_buttons)
            
            self._update_status(f"Found {total_pages} pages of Pokemon data")
            
            # Process each page
            total_pokemon = 0
            for page in range(total_pages):
                self._update_status(f"Processing page {page+1}/{total_pages}...")
                
                # If not on the first page, click the navigation button to go to the page
                if page > 0:
                    # Find the navigation buttons again (they might have been refreshed)
                    nav_buttons = driver.find_elements(By.CSS_SELECTOR, "ul li button")
                    nav_buttons[page].click()
                    
                    # Wait for the page to load
                    time.sleep(1)
                
                # Find all table rows (skip the header row)
                rows = driver.find_elements(By.CSS_SELECTOR, "table tr:not(:first-child)")
                
                page_rows = len(rows)
                self._update_status(f"Found {page_rows} Pokemon entries on page {page+1}")
                total_pokemon += page_rows
                
                # Process each row to extract the Pokemon name and sprite coordinates
                for i, row in enumerate(rows):
                    try:
                        # Get the cells in the row
                        cells = row.find_elements(By.TAG_NAME, "td")
                        
                        if len(cells) >= 2:
                            # First cell contains the icon with style attribute containing coordinates
                            icon_cell = cells[0]
                            icon_spans = icon_cell.find_elements(By.CLASS_NAME, "picon")
                            
                            if icon_spans:
                                # Get the style attribute which contains the coordinates
                                style = icon_spans[0].get_attribute("style")
                                
                                # Extract the coordinates using regex
                                # The format is: background: transparent url("...") Xpx Ypx no-repeat;
                                coords_match = re.search(r'(-?\d+)px (-?\d+)px', style)
                                
                                if coords_match:
                                    x_coord = int(coords_match.group(1))
                                    y_coord = int(coords_match.group(2))
                                    
                                    # Second cell contains the Pokemon name
                                    pokemon_name = cells[1].text.strip()
                                    
                                    # Store the coordinates
                                    pokemon_coords[pokemon_name] = {
                                        "x": x_coord,
                                        "y": y_coord
                                    }
                        
                    except Exception as e:
                        self._update_status(f"Error processing row {i} on page {page+1}: {str(e)}")
                
                # Update progress after each page
                progress = (page + 1) / total_pages
                self._update_progress(progress, f"Processed page {page+1}/{total_pages}")
            
            # Close the browser
            driver.quit()
            
            # Save the coordinates to a JSON file
            self._update_status(f"Saving coordinates for {len(pokemon_coords)} Pokemon to {self.pokemon_coords_file}...")
            with open(self.pokemon_coords_file, 'w') as f:
                json.dump(pokemon_coords, f, indent=2)
            
            self._update_status(f"Coordinates saved successfully to {self.pokemon_coords_file}")
            self._update_progress(1.0, "Coordinate parsing complete")
            
            return pokemon_coords
        
        except Exception as e:
            self._update_status(f"Error parsing Pokemon sprite coordinates: {str(e)}")
            if 'driver' in locals():
                driver.quit()
            raise
    
    def parse_item_sprite_coordinates(self) -> Dict[str, Dict[str, Any]]:
        """
        Parse item sprite coordinates from the items.js data file.
        
        Returns:
            Dictionary mapping item names to their sprite coordinates
        """
        self._update_status("Checking for existing item sprite coordinates...")
        self._update_progress(0.0, "Starting coordinate check...")
        
        # Check if the coordinates JSON already exists
        if self.item_coords_file.exists():
            self._update_status(f"Using existing coordinates from {self.item_coords_file}")
            try:
                with open(self.item_coords_file, 'r') as f:
                    item_coords = json.load(f)
                
                self._update_status(f"Loaded coordinates for {len(item_coords)} items")
                self._update_progress(1.0, "Using existing coordinates")
                return item_coords
            except Exception as e:
                self._update_status(f"Error loading existing coordinates: {str(e)}")
                self._update_status("Will parse fresh coordinates...")
                # If loading fails, we'll parse fresh coordinates
        
        # Create a dictionary to store the item sprite coordinates
        item_coords = {}
        
        try:
            # Download the items.js file to get item data
            self._update_status("Downloading item data from Pokemon Showdown...")
            items_url = "https://play.pokemonshowdown.com/data/items.js"
            response = requests.get(items_url)
            
            if response.status_code != 200:
                raise Exception(f"Failed to download items data, status code: {response.status_code}")
            
            self._update_progress(0.3, "Item data downloaded, parsing...")
            
            # Parse the JavaScript content to extract item information
            content = response.text
            
            # Extract item entries with names and sprite numbers
            # Pattern matches: itemid:{...name:"Item Name"...spritenum:123...}
            item_pattern = r'(\w+):\s*{[^}]*name:\s*"([^"]+)"[^}]*spritenum:\s*(\d+)[^}]*}'
            item_matches = re.findall(item_pattern, content)
            
            self._update_status(f"Found {len(item_matches)} items in data file")
            self._update_progress(0.6, "Calculating sprite coordinates...")
            
            # Calculate spritesheet grid layout
            # The spritesheet is 384x1152 with 24x24 sprites
            sprite_width = 24
            sprite_height = 24
            cols = 384 // sprite_width  # 16 columns
            
            # Process each item to calculate coordinates
            for i, (item_id, item_name, spritenum_str) in enumerate(item_matches):
                try:
                    spritenum = int(spritenum_str)
                    
                    # Calculate grid position from sprite number
                    row = spritenum // cols
                    col = spritenum % cols
                    
                    # Calculate pixel coordinates (top-left corner)
                    x = col * sprite_width
                    y = row * sprite_height
                    
                    # Store the coordinates
                    item_coords[item_name] = {
                        "x": x,
                        "y": y,
                        "spritenum": spritenum,
                        "item_id": item_id
                    }
                    
                    # Update progress periodically
                    if i % 50 == 0 or i == len(item_matches) - 1:
                        progress = 0.6 + (0.3 * (i + 1) / len(item_matches))
                        self._update_progress(progress, f"Processed {i+1}/{len(item_matches)} items")
                        
                except Exception as e:
                    self._update_status(f"Error processing item {item_name}: {str(e)}")
            
            # Save the coordinates to a JSON file
            self._update_status(f"Saving coordinates for {len(item_coords)} items to {self.item_coords_file}...")
            with open(self.item_coords_file, 'w') as f:
                json.dump(item_coords, f, indent=2)
            
            self._update_status(f"Coordinates saved successfully to {self.item_coords_file}")
            self._update_progress(1.0, "Coordinate parsing complete")
            
            return item_coords
        
        except Exception as e:
            self._update_status(f"Error parsing item sprite coordinates: {str(e)}")
            raise
    
    def _extract_single_pokemon_sprite(self, args: Tuple[str, Dict[str, int], Image.Image, Path, int, int]) -> Tuple[str, Dict[str, Any]]:
        """
        Extract a single Pokemon sprite from the spritesheet.
        
        Args:
            args: Tuple containing (pokemon_name, coords, spritesheet, output_dir, sprite_width, sprite_height)
            
        Returns:
            Tuple of (pokemon_name, metadata_dict)
        """
        pokemon_name, coords, spritesheet, output_dir, sprite_width, sprite_height = args
        
        try:
            # Get the coordinates
            x = abs(coords["x"])
            y = abs(coords["y"])
            
            # Extract the sprite from the spritesheet
            sprite = spritesheet.crop((x, y, x + sprite_width, y + sprite_height))
            
            # Create a safe filename (replace spaces and special characters)
            safe_name = re.sub(r'[^\w\-_]', '_', pokemon_name)
            safe_name = safe_name.replace(' ', '').replace('.','').replace('-','').replace('_','').lower()
            sprite_path = output_dir / f"{safe_name}.png"
            
            # Save the sprite with transparency
            sprite.save(sprite_path, 'PNG')
            
            # Create metadata
            metadata = {
                "filename": f"{safe_name}.png",
                "path": str(sprite_path),
                "coordinates": {
                    "x": x,
                    "y": y,
                    "width": sprite_width,
                    "height": sprite_height
                },
                "extracted_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return pokemon_name, metadata
            
        except Exception as e:
            self._update_status(f"Error extracting sprite for {pokemon_name}: {str(e)}")
            return pokemon_name, None
    
    def extract_pokemon_sprites(self, spritesheet_path: Path, pokemon_coords: Dict[str, Dict[str, int]]) -> Path:
        """
        Extract individual Pokemon sprites from the spritesheet using parallel processing.
        
        Args:
            spritesheet_path: Path to the spritesheet image
            pokemon_coords: Dictionary mapping Pokemon names to their sprite coordinates
            
        Returns:
            Path to the directory containing the extracted sprites
        """
        self._update_status("Checking for existing Pokemon sprite metadata...")
        self._update_progress(0.0, "Starting sprite extraction check...")
        
        # Check if the metadata JSON already exists
        if self.pokemon_metadata_file.exists():
            self._update_status(f"Using existing sprite metadata from {self.pokemon_metadata_file}")
            try:
                with open(self.pokemon_metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                # Verify that the sprites directory exists and has files
                if self.pokemon_sprites_dir.exists() and len(list(self.pokemon_sprites_dir.glob("*.png"))) > 0:
                    self._update_status(f"Found existing sprites in {self.pokemon_sprites_dir}")
                    self._update_progress(1.0, "Using existing sprites")
                    return self.pokemon_sprites_dir
                else:
                    self._update_status("Sprite directory empty or missing, will extract sprites...")
            except Exception as e:
                self._update_status(f"Error loading existing metadata: {str(e)}")
                self._update_status("Will extract sprites...")
                # If loading fails, we'll extract sprites
        
        self._update_status("Extracting Pokemon sprites from spritesheet using parallel processing...")
        self._update_progress(0.1, "Starting parallel sprite extraction...")
        
        # Create a metadata file to store information about the sprites
        metadata = {}
        
        try:
            # Load the spritesheet image
            spritesheet = Image.open(spritesheet_path)
            self._update_status(f"Loaded spritesheet with dimensions: {spritesheet.width}x{spritesheet.height}")
            
            # Convert to RGBA to preserve transparency
            if spritesheet.mode != 'RGBA':
                spritesheet = spritesheet.convert('RGBA')
            
            # Define the size of each sprite (40x30 pixels)
            sprite_width = 40
            sprite_height = 30
            
            # Prepare arguments for parallel processing
            total_pokemon = len(pokemon_coords)
            self._update_status(f"Starting parallel extraction of {total_pokemon} Pokemon sprites with {self.max_workers} workers...")
            
            # Create arguments for each sprite extraction
            extraction_args = []
            for pokemon_name, coords in pokemon_coords.items():
                args = (pokemon_name, coords, spritesheet, self.pokemon_sprites_dir, sprite_width, sprite_height)
                extraction_args.append(args)
            
            # Thread-safe counter for progress tracking
            completed_count = 0
            lock = threading.Lock()
            
            def update_progress():
                nonlocal completed_count
                with lock:
                    completed_count += 1
                    progress = 0.1 + (0.8 * completed_count / total_pokemon)
                    if completed_count % 10 == 0 or completed_count == total_pokemon:
                        self._update_progress(progress, f"Extracted {completed_count}/{total_pokemon} sprites")
            
            # Process sprites in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all extraction tasks
                future_to_pokemon = {
                    executor.submit(self._extract_single_pokemon_sprite, args): args[0] 
                    for args in extraction_args
                }
                
                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_pokemon):
                    pokemon_name, sprite_metadata = future.result()
                    if sprite_metadata:
                        metadata[pokemon_name] = sprite_metadata
                    update_progress()
            
            # Save the metadata
            with open(self.pokemon_metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self._update_status(f"Extracted {len(metadata)} Pokemon sprites to {self.pokemon_sprites_dir}")
            self._update_status(f"Metadata saved to {self.pokemon_metadata_file}")
            self._update_progress(1.0, "Parallel sprite extraction complete")
            
            return self.pokemon_sprites_dir
        
        except Exception as e:
            self._update_status(f"Error extracting Pokemon sprites: {str(e)}")
            raise
    
    def _extract_single_item_sprite(self, args: Tuple[str, Dict[str, Any], Image.Image, Path, int, int]) -> Tuple[str, Dict[str, Any]]:
        """
        Extract a single item sprite from the spritesheet.
        
        Args:
            args: Tuple containing (item_name, coords, spritesheet, output_dir, sprite_width, sprite_height)
            
        Returns:
            Tuple of (item_name, metadata_dict)
        """
        item_name, coords, spritesheet, output_dir, sprite_width, sprite_height = args
        
        try:
            # Get the coordinates
            x = abs(coords["x"])
            y = abs(coords["y"])
            
            # Extract the sprite from the spritesheet
            sprite = spritesheet.crop((x, y, x + sprite_width, y + sprite_height))
            
            # Create a safe filename (replace spaces and special characters)
            safe_name = re.sub(r'[^\w\-_]', '_', item_name)
            safe_name = safe_name.replace(' ', '').replace('.','').replace('-','').replace('_','').lower()
            sprite_path = output_dir / f"{safe_name}.png"
            
            # Save the sprite with transparency
            sprite.save(sprite_path, 'PNG')
            
            # Create metadata
            metadata = {
                "filename": f"{safe_name}.png",
                "path": str(sprite_path),
                "coordinates": {
                    "x": x,
                    "y": y,
                    "width": sprite_width,
                    "height": sprite_height
                },
                "extracted_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return item_name, metadata
            
        except Exception as e:
            self._update_status(f"Error extracting sprite for {item_name}: {str(e)}")
            return item_name, None
    
    def extract_item_sprites(self, spritesheet_path: Path, item_coords: Dict[str, Dict[str, Any]]) -> Path:
        """
        Extract individual item sprites from the spritesheet using parallel processing.
        
        Args:
            spritesheet_path: Path to the spritesheet image
            item_coords: Dictionary mapping item names to their sprite coordinates
            
        Returns:
            Path to the directory containing the extracted sprites
        """
        self._update_status("Checking for existing item sprite metadata...")
        self._update_progress(0.0, "Starting sprite extraction check...")
        
        # Check if the metadata JSON already exists
        if self.item_metadata_file.exists():
            self._update_status(f"Using existing sprite metadata from {self.item_metadata_file}")
            try:
                with open(self.item_metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                # Verify that the sprites directory exists and has files
                if self.item_sprites_dir.exists() and len(list(self.item_sprites_dir.glob("*.png"))) > 0:
                    self._update_status(f"Found existing sprites in {self.item_sprites_dir}")
                    self._update_progress(1.0, "Using existing sprites")
                    return self.item_sprites_dir
                else:
                    self._update_status("Sprite directory empty or missing, will extract sprites...")
            except Exception as e:
                self._update_status(f"Error loading existing metadata: {str(e)}")
                self._update_status("Will extract sprites...")
                # If loading fails, we'll extract sprites
        
        self._update_status("Extracting item sprites from spritesheet using parallel processing...")
        self._update_progress(0.1, "Starting parallel sprite extraction...")
        
        # Create a metadata file to store information about the sprites
        metadata = {}
        
        try:
            # Load the spritesheet image
            spritesheet = Image.open(spritesheet_path)
            self._update_status(f"Loaded spritesheet with dimensions: {spritesheet.width}x{spritesheet.height}")
            
            # Convert to RGBA to preserve transparency
            if spritesheet.mode != 'RGBA':
                spritesheet = spritesheet.convert('RGBA')
            
            # Define the size of each sprite (24x24 pixels for items)
            sprite_width = 24
            sprite_height = 24
            
            # Prepare arguments for parallel processing
            total_items = len(item_coords)
            self._update_status(f"Starting parallel extraction of {total_items} item sprites with {self.max_workers} workers...")
            
            # Create arguments for each sprite extraction
            extraction_args = []
            for item_name, coords in item_coords.items():
                args = (item_name, coords, spritesheet, self.item_sprites_dir, sprite_width, sprite_height)
                extraction_args.append(args)
            
            # Thread-safe counter for progress tracking
            completed_count = 0
            lock = threading.Lock()
            
            def update_progress():
                nonlocal completed_count
                with lock:
                    completed_count += 1
                    progress = 0.1 + (0.8 * completed_count / total_items)
                    if completed_count % 10 == 0 or completed_count == total_items:
                        self._update_progress(progress, f"Extracted {completed_count}/{total_items} sprites")
            
            # Process sprites in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all extraction tasks
                future_to_item = {
                    executor.submit(self._extract_single_item_sprite, args): args[0] 
                    for args in extraction_args
                }
                
                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_item):
                    item_name, sprite_metadata = future.result()
                    if sprite_metadata:
                        metadata[item_name] = sprite_metadata
                    update_progress()
            
            # Save the metadata
            with open(self.item_metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self._update_status(f"Extracted {len(metadata)} item sprites to {self.item_sprites_dir}")
            self._update_status(f"Metadata saved to {self.item_metadata_file}")
            self._update_progress(1.0, "Parallel sprite extraction complete")
            
            return self.item_sprites_dir
        
        except Exception as e:
            self._update_status(f"Error extracting item sprites: {str(e)}")
            raise
    
    def download_all_sprites(self) -> Dict[str, Path]:
        """
        Download and extract all sprites (Pokemon and items).
        
        Returns:
            Dictionary with paths to the extracted sprite directories
        """
        self._update_status("Starting sprite download process...")
        self._update_progress(0.0, "Starting sprite download...")
        
        try:
            # Download Pokemon spritesheet
            pokemon_spritesheet = self.download_pokemon_spritesheet()
            self._update_status(f"Pokemon spritesheet ready at: {pokemon_spritesheet}")
            self._update_progress(0.2, "Pokemon spritesheet downloaded")
            
            # Download item spritesheet
            item_spritesheet = self.download_item_spritesheet()
            self._update_status(f"Item spritesheet ready at: {item_spritesheet}")
            self._update_progress(0.4, "Item spritesheet downloaded")
            
            # Parse Pokemon sprite coordinates
            pokemon_coords = self.parse_pokemon_sprite_coordinates()
            self._update_status(f"Pokemon sprite coordinates parsed")
            self._update_status(f"Found coordinates for {len(pokemon_coords)} Pokemon")
            self._update_progress(0.6, "Pokemon coordinates parsed")
            
            # Parse item sprite coordinates
            item_coords = self.parse_item_sprite_coordinates()
            self._update_status(f"Item sprite coordinates parsed")
            self._update_status(f"Found coordinates for {len(item_coords)} items")
            self._update_progress(0.7, "Item coordinates parsed")
            
            # Extract Pokemon sprites
            pokemon_sprites_dir = self.extract_pokemon_sprites(pokemon_spritesheet, pokemon_coords)
            self._update_status(f"Pokemon sprites extracted to: {pokemon_sprites_dir}")
            self._update_progress(0.85, "Pokemon sprites extracted")
            
            # Extract item sprites
            item_sprites_dir = self.extract_item_sprites(item_spritesheet, item_coords)
            self._update_status(f"Item sprites extracted to: {item_sprites_dir}")
            self._update_progress(1.0, "All sprites downloaded and extracted")
            
            return {
                "pokemon": pokemon_sprites_dir,
                "items": item_sprites_dir
            }
            
        except Exception as e:
            self._update_status(f"Error in sprite download process: {str(e)}")
            raise
    
    def get_pokemon_sprite_path(self, pokemon_name: str) -> Optional[Path]:
        """
        Get the path to a Pokemon sprite.
        
        Args:
            pokemon_name: Name of the Pokemon
            
        Returns:
            Path to the sprite file, or None if not found
        """
        # Create safe filename
        safe_name = re.sub(r'[^\w\-_]', '_', pokemon_name)
        safe_name = safe_name.replace(' ', '').replace('.','').replace('-','').replace('_','').lower()
        sprite_path = self.pokemon_sprites_dir / f"{safe_name}.png"
        
        if sprite_path.exists():
            return sprite_path
        return None
    
    def get_item_sprite_path(self, item_name: str) -> Optional[Path]:
        """
        Get the path to an item sprite.
        
        Args:
            item_name: Name of the item
            
        Returns:
            Path to the sprite file, or None if not found
        """
        # Create safe filename
        safe_name = re.sub(r'[^\w\-_]', '_', item_name)
        safe_name = safe_name.replace(' ', '').replace('.','').replace('-','').replace('_','').lower()
        sprite_path = self.item_sprites_dir / f"{safe_name}.png"
        
        if sprite_path.exists():
            return sprite_path
        return None
    
    def get_sprite_metadata(self, sprite_type: str = "pokemon") -> Dict[str, Any]:
        """
        Get sprite metadata.
        
        Args:
            sprite_type: Type of sprites ("pokemon" or "items")
            
        Returns:
            Dictionary containing sprite metadata
        """
        if sprite_type == "pokemon":
            metadata_file = self.pokemon_metadata_file
        elif sprite_type == "items":
            metadata_file = self.item_metadata_file
        else:
            raise ValueError("sprite_type must be 'pokemon' or 'items'")
        
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def list_available_sprites(self, sprite_type: str = "pokemon") -> List[str]:
        """
        List all available sprites of a given type.
        
        Args:
            sprite_type: Type of sprites ("pokemon" or "items")
            
        Returns:
            List of sprite names
        """
        if sprite_type == "pokemon":
            sprite_dir = self.pokemon_sprites_dir
        elif sprite_type == "items":
            sprite_dir = self.item_sprites_dir
        else:
            raise ValueError("sprite_type must be 'pokemon' or 'items'")
        
        if sprite_dir.exists():
            return [f.stem for f in sprite_dir.glob("*.png")]
        return [] 