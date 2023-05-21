import pygame
from support import import_folder


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, surface, create_jump_particles):
        super().__init__()
        # отрисовываем игрока и передаем ему позицию
        self.import_character_ass()
        # путь к изображениям частиц при беге
        self.import_run_particles()
        self.particles_frame_index = 0
        self.particles_frame_speed = 0.15


        # индекс фрейма анимации и скорость с которой идет анимация
        self.frame_index = 0
        self.frame_speed = 0.15
        self.display_surface = surface
        self.create_jump_particles = create_jump_particles
        self.image = self.animations['straight'][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        # перемещение игрока осуществлем с помощью направления вектора, поэтому он изначально нулевой
        self.movement = pygame.math.Vector2(0, 0)
        # значение скорости перемещения игрока, значение гравитации и высоты прыжка
        self.speed = 8
        self.gravity = 0.98
        self.jump_speed = -20

        # статус игрока, куда он смотрит находится ли он на полу и т.д.
        self.status = 'straight'
        self.look_right = True
        self.on_floor = False
        self.ceiling = False
        self.on_left = False
        self.on_right = False

    # функция импортирующая полный путь до нужной нам папки анимации
    def import_character_ass(self):
        character_path = 'anim/pers/'
        self.animations = {'straight': [], 'run': [], 'jump': [], 'fall': []}

        for animate in self.animations.keys():
            full_path = character_path + animate
            self.animations[animate] = import_folder(full_path)

    # функция которая перебирает картинки из нужной нам папки и когда доходит до конца списка обнуляется и начинает по новой
    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.frame_speed
        if self.frame_index > len(animation):
            self.frame_index = 0
        image = animation[int(self.frame_index)]

        if self.look_right:
            self.image = image
        else:
            # функция которая переворачивает изображение по оси х, т.к. стоит тру первым и не трогает ось у
            flipped_image = pygame.transform.flip(image, True, False)
            self.image = flipped_image

        # делает так чтобы картинка всегда была на земле и не парила в воздухе
        if self.on_floor and self.on_right:
            self.rect = self.image.get_rect(bottomright=self.rect.bottomright)
        elif self.on_floor and self.on_left:
            self.rect = self.image.get_rect(bottomleft=self.rect.bottomleft)
        elif self.ceiling and self.on_right:
            self.rect = self.image.get_rect(topright=self.rect.topright)
        elif self.ceiling and self.on_left:
            self.rect = self.image.get_rect(topleft=self.rect.topleft)
        elif self.ceiling:
            self.rect = self.image.get_rect(midtop=self.rect.midtop)

    # импортируем частицы при беге
    def import_run_particles(self):
        self.run_particles = import_folder('../Gleb_Runner/anim/dust_particles/run')

    # анимация частичек при беге, если статус игрока в беге и игрок стоит на земле тогда анимируем бег
    def run_particles_animate(self):
        if self.status == 'run' and self.on_floor:
            self.particles_frame_index += self.particles_frame_speed
            if self.particles_frame_index >= len(self.run_particles):
                self.particles_frame_index = 0

            particles = self.run_particles[int(self.particles_frame_index)]

            # если смотрит на право то заполняем поверхность картинкой частички и передаем ее позицию (снизу слева)
            if self.look_right:
                # так как нижняя левая часть игрока находится слишком низко, то мы вычитаем вектор так чтобы
                # поднять её на нужное нам расстояние
                pos = self.rect.bottomleft - pygame.math.Vector2(12, 11)
                self.display_surface.blit(particles, pos)
            else:
                flipped_particles = pygame.transform.flip(particles, True, False)
                pos = self.rect.bottomright - pygame.math.Vector2(-1, 11)
                self.display_surface.blit(flipped_particles, pos)


    # определяет название нужной нам папки
    def get_status(self):
        if self.movement.y < 0:
            self.status = 'jump'
        elif self.movement.y > 1:
            self.status = 'fall'
        else:
            if self.movement.x == 0:
                self.status = 'straight'
            else:
                self.status = 'run'

    # функция которая считывает клавиатуру и в зависимости от нажатой клавиши направляет вектор вправо или влево или вверх
    def key_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_d]:
            self.movement.x = 1
            self.look_right = True
        elif keys[pygame.K_a]:
            self.movement.x = -1
            self.look_right = False
        else:
            self.movement.x = 0

        if keys[pygame.K_w] and self.on_floor:
            self.jump()
            self.create_jump_particles(self.rect.midbottom)

    # добавляет гравитацию
    def gravitty_mov(self):
        self.movement.y += self.gravity
        self.rect.y += self.movement.y

    # функция которая изменяет направление вектора при прыжке
    def jump(self):
        self.movement.y = self.jump_speed


    # функция которая используя значения из функции key_input направляет игрока в указанную сторону
    def update(self):
        self.key_input()
        self.get_status()
        self.animate()
        self.run_particles_animate()
