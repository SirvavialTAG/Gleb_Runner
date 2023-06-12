import pygame
from tiles import Tile, StaticTile, Object
from settings import tile_size, screen_width, screen_height
from particles import ParticleEffect
from support import import_csv_layout, import_cut_graphics
from enemies import Enemy
from player import Player
from game_data import levels


class Level:
    # передаем данные об уровне и поверхность
    def __init__(self, current_level, surface, create_overworld, change_bitcoins, change_health):
        super().__init__()

        # Общая настройка
        self.display_surface = surface
        self.world_shift = 0
        self.current_x = None
        self.bg = pygame.image.load('../Gleb_Runner/images/background_1.png').convert()
        self.bg = pygame.transform.scale(self.bg, (3080, 920))

        # связь с выбором уровня
        self.create_overworld = create_overworld
        self.current_level = current_level
        level_data = levels[self.current_level]
        self.new_last_level = level_data['unlock']

        # Настройка игрока
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout, change_health)

        # Интерфейс
        self.change_bitcoins = change_bitcoins

        # Настройка местности игры
        building_layout = import_csv_layout(level_data['building'])
        self.building_sprites = self.create_tile_group(building_layout, 'building')

        # Настройка объектов
        object_layout = import_csv_layout((level_data['objects']))
        self.object_sprites = self.create_tile_group(object_layout, 'objects')

        # Настройка монет
        bitcoin_layout = import_csv_layout((level_data['bitcoin']))
        self.bitcoin_sprites = self.create_tile_group(bitcoin_layout, 'bitcoin')

        # Настройка заднего плана
        background_layout = import_csv_layout((level_data['background']))
        self.background_sprites = self.create_tile_group(background_layout, 'background')

        # Настройка врагов
        enemy_layout = import_csv_layout((level_data['enemy']))
        self.enemy_sprites = self.create_tile_group(enemy_layout, 'enemy')

        # Настройка ограничения для передвижения врагов
        constraint_layout = import_csv_layout((level_data['constrains']))
        self.constraints_sprites = self.create_tile_group(constraint_layout, 'constrains')

        self.current_x = 0

        # частицы
        self.particles_sprite = pygame.sprite.GroupSingle()
        self.player_on_floor = False

        # Взрыв врага
        self.explosion_sprites = pygame.sprite.GroupSingle()

    # Создаём группу плиток для уровня и находим расположение плитки на карте
    def create_tile_group(self, layout, type):
        global sprite
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == 'building':
                        building_tile_list = import_cut_graphics('../Gleb_Runner/images/building.png')
                        tile_surface = building_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'objects':
                        sprite = Object(tile_size, x, y)

                    if type == 'bitcoin':
                        coins_tile_list = import_cut_graphics('../Gleb_Runner/images/bitcoin.png')
                        tile_surface = coins_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'enemy':
                        sprite = Enemy(tile_size, x, y)

                    if type == 'constrains':
                        sprite = Tile(tile_size, x, y)

                    sprite_group.add(sprite)

        return sprite_group

    def player_setup(self, layout, change_health):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == '0':
                    sprite = Player((x, y), self.display_surface, change_health)
                    self.player.add(sprite)
                if val == '1':
                    car_surface = pygame.image.load('../Gleb_Runner/images/car.png').convert_alpha()
                    sprite = StaticTile(tile_size, x-40, y-65, car_surface)
                    self.goal.add(sprite)

    def enemy_collision_reverse(self):
        for enemy in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.constraints_sprites, False):
                enemy.reverse()

    def cheak_death(self):
        if self.player.sprite.rect.top > screen_height:
            self.create_overworld(self.current_level, 0)

    def check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite, self.goal, False):
            self.create_overworld(self.current_level, self.new_last_level)

    # создаём функцию в которой проверяем дошел ли игрок до конца карты, если да, то мы проверяем в какую сторону он движется
    # и с учетом этого обнуляем скорость и двигаем картинку в сторону дваижения игрока
    def world_scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        movement_x = player.movement.x
        # если расположение прямоугольника с игроком меньше 200 и его движение направлено влево, то переменная с скролом мира
        # принимает значение равное скорости
        if player_x < screen_width / 3 and movement_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > screen_width - (screen_width / 3) and movement_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8

    # функция которая удерживает нашего игрока на поверхности
    def horizontal_move_collision(self):
        player = self.player.sprite
        player.rect.x += player.movement.x * player.speed

        # смотрим столкнулись ли два прямоугольника. Если да и игрок движется вправо, тогда правая часть прямоугольника
        # принимает положение левой части квадрата и наоборот
        # мы ввели перменную current_x чтобы исправить баг с подниманием на стену, теперь мы проверяем положение х игрока
        # и как только мы его получаем мы делаем так чтобы игрок не могу казаться этой стены с другой стороны
        collidable_sprites = self.building_sprites.sprites() + self.object_sprites.sprites() #+ self.foreground_sprites.sprites()'''
        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.movement.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right
                elif player.movement.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left

        # доп проверка если игрок справа и положение его право части меньше текущего х или он двигается влево тогда он не справа
        if player.on_right and (player.rect.right > self.current_x or player.movement.y <= 0):
            player.on_right = False
        if player.on_left and (player.rect.left < self.current_x or player.movement.y >= 0):
            player.on_left = False

    # смотрим столкнулись ли два прямоугольника, если да, то если мы падали (у > 0) нижняя часть столкнувшегося прямоугольнка
    # становится нашим верхом и обнуляем гравитацию, т.к. если мы будем стоять на месте то она просто увеличится

    def vertical_movement_coll(self):
        player = self.player.sprite
        player.gravitty_mov()

        collidable_sprites = self.building_sprites.sprites() + self.object_sprites.sprites() #'+ self.foreground_sprites.sprites()
        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.movement.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.movement.y = 0
                    player.on_floor = True
                elif player.movement.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.movement.y = 0
                    player.ceiling = True

        # проверяем не в прыжке ли находится игрок и не в падении
        if player.on_floor and player.movement.y < 0 or player.movement.y > 1:
            player.on_floor = False
        if player.ceiling and player.movement.y > 0:
            player.ceiling = False

    # Функция для проверки столкновения игрока с монетой и её последующего сбора
    def check_bitcoin_collision(self):
        collided_bitcoins = pygame.sprite.spritecollide(self.player.sprite, self.bitcoin_sprites, True)
        if collided_bitcoins:
            for bitcoin in collided_bitcoins:
                self.change_bitcoins(1)

    # Функция, проверяющая столкновение игрока с врагом
    def check_enemy_collision(self):
        enemy_collisions = pygame.sprite.spritecollide(self.player.sprite, self.enemy_sprites, False)
        if enemy_collisions:
            for enemy in enemy_collisions:
                enemy_center = enemy.rect.centery
                enemy_top = enemy.rect.top
                player_bottom = self.player.sprite.rect.bottom

                if (enemy_center > player_bottom) and (enemy_top < player_bottom) and (self.player.sprite.movement.y >= 0):
                    self.player.sprite.movement.y = -15
                    explosion_sprite = ParticleEffect(enemy.rect.center, 'explosion')
                    self.explosion_sprites.add(explosion_sprite)
                    enemy.kill()
                else:
                    self.player.sprite.get_damage()

    def run(self):
        # частицы
        self.particles_sprite.update(self.world_shift)
        self.particles_sprite.draw(self.display_surface)
        self.world_scroll_x()
        # передвижение экрана за игроком

        # Задний план
        self.display_surface.blit(self.bg, (0, 0))

        # Местность
        self.building_sprites.update(self.world_shift)
        self.building_sprites.draw(self.display_surface)

        # Враг
        self.enemy_sprites.update(self.world_shift)
        self.constraints_sprites.update(self.world_shift)
        self.enemy_collision_reverse()
        self.enemy_sprites.draw(self.display_surface)
        self.explosion_sprites.update(self.world_shift)
        self.explosion_sprites.draw(self.display_surface)


        # Объекты
        self.object_sprites.update(self.world_shift)
        self.object_sprites.draw(self.display_surface)

        # Монеты
        self.bitcoin_sprites.update(self.world_shift)
        self.bitcoin_sprites.draw(self.display_surface)


        # Спрайты игрока
        self.player.update()
        self.horizontal_move_collision()
        self.vertical_movement_coll()
        self.player.draw(self.display_surface)
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)
        self.cheak_death()
        self.check_win()
        self.check_bitcoin_collision()
        self.check_enemy_collision()