import sys

import pygame
from pygame.locals import *
from graphics import Renderer
import config
import platform
import os


class Engine:
    def __init__(self):
        self.resolution = config.RESOLUTION
        if platform.system() == "Linux":
            os.environ["SDL_VIDEO_X11_FORCE_EGL"] = "1"
        pygame.init()
        pygame.display.set_mode(config.RESOLUTION, DOUBLEBUF | OPENGL)
        pygame.display.set_caption('Real Engine')
        icon = pygame.image.load(config.ICON_PATH)
        pygame.display.set_icon(icon)
        pygame.key.set_repeat(int(1000 / config.FPS))
        self.movement_event_handler = None

    def handle_pygame_events(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.movement_event_handler is not None:
                if pygame.mouse.get_pressed(3)[0]:
                    self.movement_event_handler.handle_mouse_event(pygame.mouse.get_rel())
                else:
                    pygame.mouse.get_rel()
        if event.type == pygame.KEYDOWN:
            if self.movement_event_handler is not None:
                self.movement_event_handler.handle_keydown_event()

    def run(self, renderer: Renderer):
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                else:
                    self.handle_pygame_events(event)
            if self.movement_event_handler is not None and any(pygame.key.get_pressed()):
                self.movement_event_handler.handle_keydown_event()

            renderer.render()
            pygame.display.flip()
            clock.tick(config.FPS)
