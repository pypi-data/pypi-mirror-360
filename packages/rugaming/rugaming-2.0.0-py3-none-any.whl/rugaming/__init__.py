"""
RuGaming - Русскоязычный игровой движок для Python
"""

__version__ = "2.0.0"
__all__ = ['GameEngine', 'GameObject', 'Scene']  # и другие экспортируемые классы

from .core import GameEngine, Scene
from .objects import GameObject
from .render import Renderer2D, Renderer3D
from .ai import SimpleAI, PathfindingAI

__all__ = [
    'GameEngine',
    'Scene',
    'GameObject',
    'Light',
    'Camera',
    'Renderer2D',
    'Renderer3D',
    'SimpleAI',
    'PathfindingAI'
]