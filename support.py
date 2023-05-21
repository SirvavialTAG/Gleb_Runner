from os import walk
from csv import reader
from settings import tile_size
import pygame


# функция которая добавляет в список картинку с нужной нам анимацией
def import_folder(path):
    surface_list = []

    # img_files список с названием всех картинок в папке
    for _, __, img_files in walk(path):
        # пробегаемся по списку, чтобы знать названия наших картинок
        for img in img_files:
            # узнаем полный путь к именно нужной нам картинке
            full_path = path + '/' + img
            # загружаем нашу картинку и конвертируем, чтобы пайгему было легче с ней работать
            img_surface = pygame.image.load(full_path).convert_alpha()
            # добавляем картинку в список
            surface_list.append(img_surface)

    return surface_list


# Функция, которая импортирует файлы формата csv из программы Tiled
def import_csv_layout(path):
    terrain_map = []
    with open(path) as map:
        level = reader(map, delimiter=',')
        for row in level:
            terrain_map.append(list(row))
        return terrain_map


def import_cut_graphics(path):
    # Загружаем изображение поверхности и конвертируем его для ускорения отрисовки поверхности
    surface = pygame.image.load(path).convert_alpha()

    # Получаем ширину и высоту поверхности в пикселях
    tile_num_x = int(surface.get_size()[0] / tile_size)
    tile_num_y = int(surface.get_size()[1] / tile_size)

    cut_tiles = []
    for row in range(tile_num_y):
        for col in range(tile_num_x):
            x = col * tile_size
            y = row * tile_size
            new_surface = pygame.Surface((tile_size, tile_size), flags=pygame.SRCALPHA)

            # Накладываем поверхность new_surface на поверхность surface и добавляем её в пустой список
            new_surface.blit(surface, (0, 0), pygame.Rect(x, y, tile_size, tile_size))
            cut_tiles.append(new_surface)

    return cut_tiles
