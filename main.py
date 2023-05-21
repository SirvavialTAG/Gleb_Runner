import pygame, sys
from settings import *
from level import Level
from game_data import level_1

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

# передаём Level значение level_map из файла settings.py и screen
level = Level(level_1, screen)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill('grey')
    level.run()

    pygame.display.update()
    clock.tick(60)