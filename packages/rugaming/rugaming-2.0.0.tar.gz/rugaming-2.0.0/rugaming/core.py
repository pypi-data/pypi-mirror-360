import pygame
from typing import Dict, List, Optional
from rugaming.objects import GameObject
from rugaming.render import Renderer2D, Renderer3D

class Scene:
    def __init__(self, name: str):
        self.name = name
        self.objects: List[GameObject] = []
        self._lights: List[GameObject] = []
        self._main_camera: Optional[GameObject] = None

    def add_light(self, light: GameObject):
        if "Light" in light.name:
            self._lights.append(light)

    def set_main_camera(self, camera: GameObject):
        if "Camera" in camera.name:
            self._main_camera = camera

class GameEngine:
    def __init__(self, title: str, width: int = 800, height: int = 600, mode: str = "2d"):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(f"{title} | RuGaming 2.0")
        self.clock = pygame.time.Clock()
        self.scenes: Dict[str, Scene] = {}
        self.current_scene: Optional[Scene] = None
        self._renderer = Renderer3D(self.screen) if mode == "3d" else Renderer2D(self.screen)
        self._running = False

    def add_scene(self, scene: Scene):
        self.scenes[scene.name] = scene

    def _process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False

    def _update(self, delta_time: float):
        if not self.current_scene:
            return
            
        for obj in self.current_scene.objects:
            obj.update(delta_time)

    def _render(self):
        if not self.current_scene:
            return

        self.screen.fill((0, 0, 0))  # Очистка экрана
        
        for obj in self.current_scene.objects:
            if obj.visible:
                self._renderer.render(obj)

        pygame.display.flip()

    def run(self, target_fps: int = 60):
        self._running = True
        last_time = pygame.time.get_ticks()

        while self._running:
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - last_time) / 1000.0
            last_time = current_time

            self._process_input()
            self._update(delta_time)
            self._render()
            self.clock.tick(target_fps)

        pygame.quit()