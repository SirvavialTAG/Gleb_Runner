import pygame, sys
from settings import *
from level import Level
from overworld import Overworld
from interface import Interface

class Game:
    def __init__(self):
        # Игровые атрибуты
        self.last_level = 0
        self.max_health = 100
        self.current_health = 100
        self.bitcoins = 0

        self.overworld = Overworld(0, self.last_level, screen, self.create_level)
        self.status = 'overworld'

        # Интерфейс
        self.interface = Interface(screen)

    def create_level(self, current_level):
        self.level = Level(current_level, screen, self.create_overworld, self.change_bitcoins, self.change_health)
        self.status = 'level'

    def create_overworld(self, current_level, new_last_level):
        if new_last_level > self.last_level:
            self.last_level = new_last_level
        self.overworld = Overworld(current_level, self.last_level, screen, self.create_level)
        self.status = 'overworld'

    def change_bitcoins(self, amount):
        self.bitcoins += amount

    def change_health(self, amount):
        self.current_health += amount

    def game_over(self):
        if self.current_health <= 0:
            self.current_health = 100
            self.bitcoins = 0
            self.last_level = 0
            self.overworld = Overworld(0, self.last_level, screen, self.create_level)
            self.status = 'overworld'

    def run(self):
        if self.status == 'overworld':
            self.overworld.run()
        else:
            self.level.run()
            self.interface.show_health(self.current_health, self.max_health)
            self.interface.show_bitcoin(self.bitcoins)
            self.game_over()

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

# передаём Level значение level_map из файла settings.py и screen
game = Game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill('pink')
    game.run()

    pygame.display.update()
    clock.tick(60)