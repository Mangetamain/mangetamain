"""
Index principal pour faciliter les imports des modules MangeTaMain
"""

# Imports des classes principales
from .core.app import MangeTaMainApp
from .managers.data_manager import DataManager
from .engines.recommendation_engine import RecommendationEngine
from .ui.components import UIComponents
from .utils.styles import StyleManager

# Configuration
from .utils.config import (
    DATA_PATHS,
    CACHE_CONFIG,
    RECOMMENDATION_CONFIG,
    UI_CONFIG,
    MESSAGES
)

# Version
__version__ = "2.0.0"

# Exports pour faciliter les imports
__all__ = [
    'MangeTaMainApp',
    'DataManager',
    'RecommendationEngine', 
    'UIComponents',
    'StyleManager',
    'DATA_PATHS',
    'CACHE_CONFIG',
    'RECOMMENDATION_CONFIG',
    'UI_CONFIG',
    'MESSAGES'
]