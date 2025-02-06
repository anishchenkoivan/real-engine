import sys

import pygame
from OpenGL.raw.GL.VERSION.GL_2_0 import glUniform2f
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
        self.mouse_event_handler = None
        self.keyboard_event_handler = None

    def handle_pygame_events(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.mouse_event_handler is not None:
                if pygame.mouse.get_pressed(3)[0]:
                    self.mouse_event_handler.handle_event(pygame.mouse.get_rel())
                else:
                    pygame.mouse.get_rel()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                print("g")

    def run(self, renderer: Renderer):
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                else:
                    self.handle_pygame_events(event)

            renderer.render()
            pygame.display.flip()
            clock.tick(config.FPS)
