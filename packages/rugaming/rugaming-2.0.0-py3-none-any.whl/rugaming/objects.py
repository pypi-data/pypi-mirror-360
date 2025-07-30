from typing import Tuple, Optional
from dataclasses import dataclass
import math

@dataclass
class Transform:
    """Компонент трансформации"""
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)

class GameObject:
    """Базовый игровой объект"""
    def __init__(self, name: str = "Object"):
        self.name = name
        self.transform = Transform()
        self.components = []
        self.visible = True
    
    def update(self) -> None:
        """Обновление состояния объекта"""
        for component in self.components:
            if hasattr(component, 'update'):
                component.update()
    
    def add_component(self, component) -> None:
        """Добавление компонента"""
        self.components.append(component)
        component.game_object = self

class Camera(GameObject):
    """Камера"""
    def __init__(self, name: str = "Camera", fov: float = 60.0):
        super().__init__(name)
        self.fov = fov
        self.clip_near = 0.1
        self.clip_far = 1000.0

class Light(GameObject):
    """Источник света"""
    def __init__(self, name: str = "Light", 
                 color: Tuple[int, int, int] = (255, 255, 255),
                 intensity: float = 1.0):
        super().__init__(name)
        self.color = color
        self.intensity = intensity