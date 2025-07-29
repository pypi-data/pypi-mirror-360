"""
Configuration management for QUIZR
"""

import os
import sys
from typing import Dict, Any
from pathlib import Path


class Config:
    """Configuration settings for QUIZR"""
    
    # Default configuration values
    DEFAULT_CONFIG = {
        'fuzzy_threshold': 90,  # Percentage for fuzzy matching
        'images_dir': 'images',  # Directory for images
        'exercises_dir': 'Exercises',  # Directory for exercise files
        'progress_file': 'progress.yaml',  # Progress tracking file
        'quick_mode_count': 10,  # Number of questions in quick mode
    }
    
    def __init__(self, base_dir: str = None):
        """Initialize configuration
        
        Args:
            base_dir: Base directory for quiz data (defaults to package directory)
        """
        if base_dir:
            self.base_dir = base_dir
        else:
            # Get the directory where the package is installed
            package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.base_dir = package_dir
            
        self.config = self.DEFAULT_CONFIG.copy()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value
    
    def get_images_dir(self) -> str:
        """Get full path to images directory"""
        return os.path.join(self.base_dir, self.get('images_dir'))
    
    def get_exercises_dir(self) -> str:
        """Get full path to exercises directory"""
        return os.path.join(self.base_dir, self.get('exercises_dir'))
    
    def get_progress_file(self) -> str:
        """Get full path to progress file"""
        return os.path.join(self.base_dir, self.get('progress_file'))
    
    def validate_directories(self) -> Dict[str, bool]:
        """Validate that required directories exist
        
        Returns:
            Dict mapping directory names to whether they exist
        """
        results = {}
        
        # Check if images directory exists
        images_dir = self.get_images_dir()
        results['images'] = os.path.exists(images_dir)
        
        # Check if exercises directory exists
        exercises_dir = self.get_exercises_dir()
        results['exercises'] = os.path.exists(exercises_dir)
        
        # Check if base directory is writable
        results['base_writable'] = os.access(self.base_dir, os.W_OK)
        
        return results
    
    def create_missing_directories(self) -> None:
        """Create missing directories"""
        images_dir = self.get_images_dir()
        if not os.path.exists(images_dir):
            os.makedirs(images_dir, exist_ok=True)
            
        exercises_dir = self.get_exercises_dir()
        if not os.path.exists(exercises_dir):
            os.makedirs(exercises_dir, exist_ok=True) 