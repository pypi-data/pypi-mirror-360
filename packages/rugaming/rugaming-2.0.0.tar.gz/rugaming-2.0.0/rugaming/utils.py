import pygame
import os
from typing import Tuple, Optional, List
import json

class ResourceManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._textures = {}
            cls._sounds = {}
            cls._fonts = {}
        return cls._instance

    @classmethod
    def load_texture(cls, path: str) -> Optional[pygame.Surface]:
        if path in cls._textures:
            return cls._textures[path]
        
        try:
            texture = pygame.image.load(path).convert_alpha()
            cls._textures[path] = texture
            return texture
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading texture {path}: {e}")
            return None

    @classmethod
    def load_sound(cls, path: str) -> Optional[pygame.mixer.Sound]:
        # Аналогичная реализация для звуков
        pass

class InputHandler:
    @staticmethod
    def get_mouse_position() -> Tuple[int, int]:
        return pygame.mouse.get_pos()

    @staticmethod
    def is_key_pressed(key: int) -> bool:
        return pygame.key.get_pressed()[key]

class GameTimer:
    def __init__(self):
        self._timers = {}
    
    def add_timer(self, name: str, duration: float):
        self._timers[name] = {
            "duration": duration,
            "elapsed": 0.0,
            "running": False
        }
    
    def update(self, delta_time: float):
        for timer in self._timers.values():
            if timer["running"]:
                timer["elapsed"] += delta_time
    
    def start(self, name: str):
        if name in self._timers:
            self._timers[name]["running"] = True
            self._timers[name]["elapsed"] = 0.0
    
    def is_expired(self, name: str) -> bool:
        return (name in self._timers and 
                self._timers[name]["running"] and 
                self._timers[name]["elapsed"] >= self._timers[name]["duration"])