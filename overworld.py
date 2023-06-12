import pygame
from game_data import levels
from support import import_folder

class Node(pygame.sprite.Sprite):
    def __init__(self, pos, status, icon_speed, path):
        super().__init__()
        self.frames = import_folder(path)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        if status == 'available':
            self.status = 'available'
        else:
            self.status = 'ты кто такой?'
        self.rect = self.image.get_rect(center=pos)

        self.zone = pygame.Rect(self.rect.centerx - icon_speed / 2, self.rect.centery - icon_speed / 2, icon_speed, icon_speed)

    def animate(self):
        self.frame_index += 0.15
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self):
        if self.status == 'available':
            self.animate()
        else:
            tint_surf = self.image.copy()
            tint_surf.fill('black', None, pygame.BLEND_RGBA_MULT)
            self.image.blit(tint_surf, (0, 0))

class Icon(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.image = pygame.image.load('../Gleb_Runner/images/overworld/gleb_head.png')
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        self.rect.center = self.pos

class Overworld:
    def __init__(self, start_level, last_level, surface, create_level):

        self.display_surface = surface
        self.last_level = last_level
        self.current_level = start_level
        self.create_level = create_level

        self.moving = False
        self.move_direction = pygame.math.Vector2(0, 0)
        self.speed = 10

        #спрайты
        self.setup_nodes()
        self.setup_icon()

        self.start_time = pygame.time.get_ticks()
        self.permission = False
        self.delay = 500

    def setup_nodes(self):
        self.nodes = pygame.sprite.Group()
        # цикл в котором мы получаем позицию где распологается иконка уровня и показываем только те уровни у которых
        # индекс <= значению last_level
        for index, nodes_data in enumerate(levels.values()):
            if index <= self.last_level:
                node_sprite = Node(nodes_data['node_pos'], 'available', self.speed, nodes_data['node_graphics'])
            else:
                node_sprite = Node(nodes_data['node_pos'], 'locked', self.speed, nodes_data['node_graphics'])
            self.nodes.add(node_sprite)

    def draw_paths(self):
        if self.last_level > 0:
            points = [node['node_pos'] for index, node in enumerate(levels.values()) if index <= self.last_level]
            pygame.draw.lines(self.display_surface, 'purple', False, points, 6)

    def setup_icon(self):
        self.icon = pygame.sprite.GroupSingle()
        # передаем позицию иконки игрока с помощью записанных ранее позиций уровней выбирая их центр
        # и отбирая из них тот который является текущим
        icon_sprite = Icon(self.nodes.sprites()[self.current_level].rect.center)
        self.icon.add(icon_sprite)

    def input(self):
        keys = pygame.key.get_pressed()
        if not self.moving and self.permission:
            if keys[pygame.K_d] and self.current_level < self.last_level and self.last_level!=4:
                self.move_direction = self.get_movement_data('next')
                self.current_level += 1
                self.moving = True
            elif keys[pygame.K_a] and self.current_level > 0:
                self.move_direction = self.get_movement_data('я русский')
                self.current_level -= 1
                self.moving = True
            elif keys[pygame.K_SPACE]:
                self.create_level(self.current_level)

    def get_movement_data(self, target):
        start = pygame.math.Vector2(self.nodes.sprites()[self.current_level].rect.center)

        if target == 'next':
            end = pygame.math.Vector2(self.nodes.sprites()[self.current_level + 1].rect.center)
        else:
            end = pygame.math.Vector2(self.nodes.sprites()[self.current_level - 1].rect.center)
        # переводит вектор в единичный формат
        return (end - start).normalize()

    def update_icon_pos(self):
        # нашу иконку мы перемещаем на соответствующий квадрат который равен нашему текущему уровню
        # так как пайгейм округляет до целого все числа с плавающей точкой, наша иконка никогда не достигнет центра прямоугольника
        # поэтому мы ввели переменную pos которая не будет превращаться в int
        if self.moving and self.move_direction:
            self.icon.sprite.pos += self.move_direction * self.speed
            target_node = self.nodes.sprites()[self.current_level]
            if target_node.zone.collidepoint(self.icon.sprite.pos):
                self.moving = False
                self.move_direction = pygame.math.Vector2(0, 0)

    def timer(self):
        if not self.permission:
            current_time = pygame.time.get_ticks()
            if current_time - self.start_time >= self.delay:
                self.permission = True

    def run(self):
        self.timer()
        self.input()
        self.update_icon_pos()
        self.icon.update()
        self.nodes.update()

        self.draw_paths()
        self.nodes.draw(self.display_surface)
        self.icon.draw(self.display_surface)
