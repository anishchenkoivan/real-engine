import pygame
from pygame.locals import *
from graphics import Renderer
import config
import platform
import os


class Engine:
    def __init__(self, resolution=(1920, 1080)):
        self.resolution = resolution
        if platform.system() == "Linux":
            os.environ["SDL_VIDEO_X11_FORCE_EGL"] = "1"
        pygame.init()
        pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
        pygame.display.set_caption('Real Engine')
        icon = pygame.image.load(config.ICON_PATH)
        pygame.display.set_icon(icon)

    def handle_pygame_events(self, event):
        pass

    def run(self, renderer: Renderer):
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                else:
                    self.handle_pygame_events(event)

            renderer.render()
            pygame.display.flip()
            clock.tick(config.FPS)
