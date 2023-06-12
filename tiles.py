import pygame
from support import import_folder


# создаем класс который наследует спрайт
class Tile(pygame.sprite.Sprite):
    def __init__(self, size, x, y):
        super().__init__()
        #создаём квадратную поверхность, заполняем ее зеленым цветом и рисуем на ней квадрат в указанной позиции
        self.image = pygame.Surface((size, size))
        self.rect = self.image.get_rect(topleft=(x, y))

    # создаем функцию которая будет обновлять положение х в зависимости от игрока
    def update(self, shift):
        self.rect.x += shift


# создаём класс статичной плитки
class StaticTile(Tile):
    def __init__(self, size, x, y, surface):
        super().__init__(size, x, y)
        self.image = surface


# Создаём класс для объектов (фонарь)
class Object(StaticTile):
    def __init__(self, size, x, y):
        super().__init__(size, x, y, pygame.image.load('../Gleb_Runner/images/building/фонарь.png').convert_alpha())
        offset_y = y + size
        self.rect = self.image.get_rect(bottomleft=(x, offset_y))


# Создаём класс для анимированных объектов
class AnimatedTile(Tile):
    def __init__(self, size, x, y, path):
        super().__init__(size, x, y)
        self.frames = import_folder(path)
        self.frames_index = 0
        self.image = self.frames[self.frames_index]

    def animate(self):
        self.frames_index += 0.15
        if self.frames_index >= len(self.frames):
            self.frames_index = 0
        self.image = self.frames[int(self.frames_index)]

    def update(self, shift):
        self.animate()
        self.rect.x += shift