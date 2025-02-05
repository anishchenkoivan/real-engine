import pygame
from pygame.locals import *
from graphics import Renderer
import config


class Engine:
    def __init__(self, renderer: Renderer, resolution=(1920, 1080)):
        self.renderer = renderer
        self.resolution = resolution

    def handle_pygame_events(self, event):
        pass

    def run(self):
        pygame.init()
        pygame.display.set_caption('Real Engine')
        icon = pygame.image.load(config.ICON_PATH)
        pygame.display.set_icon(icon)
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                else:
                    self.handle_pygame_events(event)

            self.renderer.render()
            pygame.display.flip()
            clock.tick()
