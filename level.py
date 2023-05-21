import pygame
from tiles import Tile, StaticTile, Object, Bitcoin, Flashlight
from settings import tile_size, screen_width, screen_height
from player import Player
from particles import ParticleEffect
from support import import_csv_layout, import_cut_graphics
from enemies import Enemy
from decoration import Night_city, Flight_car
from player import Player


class Level:
    # передаем данные об уровне и поверхность
    def __init__(self, level_data, surface):
        super().__init__()

        # Общая настройка
        self.display_surface = surface
        self.world_shift = 0
        self.current_x = None
        self.bg = pygame.image.load('../Gleb_Runner/images/background_1.png').convert()
        self.bg = pygame.transform.scale(self.bg, (1280, 1088))

        # Настройка игрока
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout)

        # Настройка местности игры
        building_layout = import_csv_layout(level_data['building'])
        self.building_sprites = self.create_tile_group(building_layout, 'building')

        # Настройка травы
        '''grass_layout = import_csv_layout((level_data['grass']))
        self.grass_sprites = self.create_tile_group(grass_layout, 'grass')'''

        # Настройка объектов
        object_layout = import_csv_layout((level_data['objects']))
        self.object_sprites = self.create_tile_group(object_layout, 'objects')

        # Настройка монет
        bitcoin_layout = import_csv_layout((level_data['bitcoin']))
        self.bitcoin_sprites = self.create_tile_group(bitcoin_layout, 'bitcoin')

        # Настройка ближнего плана
        '''foreground_layout = import_csv_layout((level_data['fg_palms']))
        self.foreground_sprites = self.create_tile_group(foreground_layout, 'fg_palms')'''

        # Настройка заднего плана
        background_layout = import_csv_layout((level_data['background']))
        self.background_sprites = self.create_tile_group(background_layout, 'background')

        # Настройка врагов
        enemy_layout = import_csv_layout((level_data['enemy']))
        self.enemy_sprites = self.create_tile_group(enemy_layout, 'enemy')

        # Настройка ограничения для передвижения врагов
        constraint_layout = import_csv_layout((level_data['constrains']))
        self.constraints_sprites = self.create_tile_group(constraint_layout, 'constrains')

        # Декорации
        '''self.sky = Night_city(8)'''
        '''level_width = len(building_layout[0]) * tile_size
        self.water = Water(screen_height - 20, level_width)
        self.flight_car = Flight_car(400, level_width, 20)'''

        self.current_x = 0

        # частицы
        self.particles_sprite = pygame.sprite.GroupSingle()
        self.player_on_floor = False

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

                    '''if type == 'grass':
                        grass_tile_list = import_cut_graphics('../Gleb_Runner/images/decoration/grass/grass.png')
                        tile_surface = grass_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)'''

                    if type == 'objects':
                        sprite = Object(tile_size, x, y)

                    if type == 'bitcoin':
                        coins_tile_list = import_cut_graphics('../Gleb_Runner/images/bitcoin.png')
                        tile_surface = coins_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    '''if type == 'fg_palms':
                        if val == '0': sprite = Flashlight(tile_size, x, y, '../Project/images/terrain/palm_small', 38)
                        if val == '1': sprite = Flashlight(tile_size, x, y, '../Project/images/terrain/palm_large', 64)'''

                    '''if type == 'bg_palms':
                        sprite = Flashlight(tile_size, x, y, '../Gleb_Runner/images/terrain/palm_bg', 0)'''

                    if type == 'enemy':
                        sprite = Enemy(tile_size, x, y)

                    if type == 'constrains':
                        sprite = Tile(tile_size, x, y)

                    sprite_group.add(sprite)

        return sprite_group

    def player_setup(self, layout):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == '0':
                    sprite = Player((x, y), self.display_surface, self.create_jump_particles)
                    self.player.add(sprite)
                if val == '1':
                    hat_surface = pygame.image.load('../Gleb_Runner/images/car.png').convert_alpha()
                    sprite = StaticTile(tile_size, x-120, y-60, hat_surface)
                    self.goal.add(sprite)

    def enemy_collision_reverse(self):
        for enemy in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.constraints_sprites, False):
                enemy.reverse()

    def create_jump_particles(self, pos):
        if self.player.sprite.look_right:
            pos -= pygame.math.Vector2(10, 5)
        else:
            pos += pygame.math.Vector2(10, -5)
        jump_particles_sprite = ParticleEffect(pos, 'jump')
        self.particles_sprite.add(jump_particles_sprite)

    def j_player_on_floor(self):
        if self.player.sprite.on_floor:
            self.player_on_floor = True
        else:
            self.player_on_floor = False

    def create_landing_dust(self):
        # если игрок тольео приземлился и в группе спрайтов нет ничего тогда воспроизводим частицы приземления
        if not self.player_on_floor and self.player.sprite.on_floor and not self.particles_sprite.sprites():
            if self.player.sprite.look_right:
                offset = pygame.math.Vector2(5, 17)
            else:
                offset = pygame.math.Vector2(-5, 17)
            fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset, 'land')
            self.particles_sprite.add(fall_dust_particle)

    # создаём функцию в которой проверяем дошел ли игрок до конца карты, если да, то мы проверяем в какую сторону он движется
    # и с учетом этого обнуляем скорость и двигаем картинку в сторону дваижения игрока
    def world_scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        movement_x = player.movement.x
        # если расположение прямоугольника с игроком меньше 200 и его движение направлено влево, то переменная с скролом мира
        # принимает значение равное скорости
        if player_x < screen_width / 6 and movement_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > screen_width - (screen_width / 6) and movement_x > 0:
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

    def run(self):
        # частицы
        self.particles_sprite.update(self.world_shift)
        self.particles_sprite.draw(self.display_surface)
        self.world_scroll_x()
        # передвижение экрана за игроком


        # Небо
        '''self.sky.draw(self.display_surface)'''
        '''self.flight_cars.draw(self.display_surface, self.world_shift)'''

        # Задний план
        self.display_surface.blit(self.bg,(0,0))

        # Местность
        self.building_sprites.update(self.world_shift)
        self.building_sprites.draw(self.display_surface)

        # Враг
        self.enemy_sprites.update(self.world_shift)
        self.constraints_sprites.update(self.world_shift)
        self.enemy_collision_reverse()
        self.enemy_sprites.draw(self.display_surface)
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)

        # Объекты
        self.object_sprites.update(self.world_shift)
        self.object_sprites.draw(self.display_surface)

        # Трава
        '''self.grass_sprites.update(self.world_shift)
        self.grass_sprites.draw(self.display_surface)'''

        # Монеты
        self.bitcoin_sprites.update(self.world_shift)
        self.bitcoin_sprites.draw(self.display_surface)

        # Ближний план
        '''self.foreground_sprites.update(self.world_shift)
        self.foreground_sprites.draw(self.display_surface)'''

        # Спрайты игрока
        self.player.update()
        self.horizontal_move_collision()
        self.vertical_movement_coll()
        self.j_player_on_floor()
        self.create_landing_dust()
        self.player.draw(self.display_surface)


        # Вода
        '''self.water.draw(self.display_surface, self.world_shift)'''
