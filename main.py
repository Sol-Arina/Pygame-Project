import sys
import time
import json
import pygame
# sys.dont_write_bytecode = True
# from lib.core import Core


# инициализация pygame
pygame.init()

# настройка экрана
SCREEN_WIDTH = 880
SCREEN_HEIGHT = 640
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Farm :)')

tilesets = {
    1: pygame.image.load(r'assets\tilemaps\Bitmask references 1.png'),
    2: pygame.image.load(r'assets\tilemaps\Doors.png'),
    3: pygame.image.load(r'assets\tilemaps\Fences.png'),
    4: pygame.image.load(r'assets\tilemaps\Grass.png'),
    5: pygame.image.load(r'assets\tilemaps\Hills.png'),
    6: pygame.image.load(r'assets\tilemaps\Tilled_Dirt.png'),
    7: pygame.image.load(r'assets\tilemaps\Water.png'),
    8: pygame.image.load(r'assets\tilemaps\Wooden_House_Roof_Tilset.png'),
    9: pygame.image.load(r'assets\tilemaps\Wooden_House_Walls_Tilset.png')
}

# размер 1 тайла
TILE_SIZE = 16

# Функция для отрисовки тайлов с учётом отражения (flip) и проверки границ
def render_tile(tileset, dest_x, dest_y, src_x, src_y, flip_h, flip_v):
    '''tile rendering'''
    # Проверяем, не выходит ли область за пределы тайлсета
    if (src_x + TILE_SIZE <= tileset.get_width()) and (src_y + TILE_SIZE <= tileset.get_height()):
        # Извлекаем часть изображения тайла
        tile = tileset.subsurface((src_x, src_y, TILE_SIZE, TILE_SIZE))

        # Применяем отражение, если нужно
        if flip_h or flip_v:
            tile = pygame.transform.flip(tile, flip_h, flip_v)

        # Отрисовываем тайл на экране
        screen.blit(tile, (dest_x, dest_y))
    else:
        print(f"Warning: Tile source out of bounds at ({src_x}, {src_y}) in tileset.")

# Функция для рендеринга карты
def render_map(level_data):
    '''map rendering'''
    for level in level_data['levels']:
        if 'layerInstances' in level:
            for layer in level['layerInstances']:
                tileset_id = layer.get('__tilesetDefUid')
                if tileset_id and tileset_id in tilesets:
                    tileset = tilesets[tileset_id]
                    for tile in layer['gridTiles']:
                        # Источник тайла в тайлсете
                        src_x, src_y = tile['src']
                        # Позиция тайла на экране
                        dest_x, dest_y = tile['px']
                        # Определяем, нужно ли отражение
                        flip_h = tile['f'] in (1, 3)  # 1 или 3 — горизонтальное отражение
                        flip_v = tile['f'] in (2, 3)  # 2 или 3 — вертикальное отражение
                        # Рендерим тайл с проверкой границ
                        render_tile(tileset, dest_x, dest_y, src_x, src_y, flip_h, flip_v)
                        

# Загрузка данных уровня из JSON
with open('new_farm_window.json', encoding='utf-8') as f:
    level_data = json.load(f)

# Основной игровой цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Очистка экрана
    screen.fill((0, 0, 0))

    # Рендеринг карты
    render_map(level_data)

    # Обновление экрана
    pygame.display.flip()

# Завершение Pygame
pygame.quit()