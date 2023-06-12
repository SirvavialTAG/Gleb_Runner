import pygame
from support import import_folder


class ParticleEffect(pygame.sprite.Sprite):
    def __init__(self, pos, type):
        super().__init__()
        self.frame_index = 0
        self.frame_speed = 0.5
        if type == 'explosion':
            self.frames = import_folder('../Gleb_Runner/images/enemy/explosion')
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)

    def animate(self):
        # когда заканчиваются файлы мы уничтожаем спрайт
        self.frame_index += self.frame_speed
        if self.frame_index >= len(self.frames):
            # удаляет спрайт со всех групп
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]

    def update(self, x_shift):
        self.animate()
        self.rect.x += x_shift
