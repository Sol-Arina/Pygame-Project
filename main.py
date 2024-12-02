import sys
import time
import json
import pygame
from tiles import *
from spritesheet import Spritesheet # type: ignore
from animals import Animal, load_animal_frames
# sys.dont_write_bytecode = True
# from lib.core import Core


# инициализация pygame
pygame.init()

# настройка экрана
SCREEN_WIDTH = 1120 # 16 умножить на 70 
SCREEN_HEIGHT = 720 # 16 умножить на 45 
TILE_SIZE = 16
BACKGROUND_TEAL = (155, 212, 195)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
canvas = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption('Farm :)')  # надо придумать название

clock = pygame.time.Clock()

#################################################################################

# cоздаем объект TileMap (см. tiles.py) с основной картой и картой второго слоя 
tile_map = TileMap(TILE_SIZE, 'ground_tiles_environment.csv', 'ground_tiles_overlay_decor_biom.csv')

# загрузка тайлов для основного слоя
# ID тайла с грядкой - 504  (карта = ground_tiles_environment.csv, файлы = environmentsprites.png', environmentsprites.json') 
tile_map.add_tiles_from_image('environmentsprites.png', starting_index=0)

# загрузка тайлов для второго слоя, здесь деревья без урожая, цветы, камни, забор, дорожки, домик, грибы
tile_map.add_overlay_tiles_from_image('2ndlayer.png', starting_index=0)


"""        ЖИВОТНЫЕ        """
# загрузка спрайтов животных
cow_spritesheet = Spritesheet('cowspritesheet.png')
chicken_spritesheet = Spritesheet('chickenspritesheet.png')

# загрузка фреймов для анимации животных
animal_frames = load_animal_frames('animal_frames.json')

# создание животных
animals_group = pygame.sprite.Group()

cow = Animal(300, 300, cow_spritesheet, animal_frames['cow'])
chicken = Animal(500, 500, chicken_spritesheet, animal_frames['chicken'])

animals_group.add(cow, chicken)

##################################################################################


# GAME LOOP
running = True
while running:
    dt = clock.tick(60)  # дельта времени для кадров
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # очистка экрана
    screen.fill((0, 0, 0))

     # заливка экрана цветом воды (чтобы заполнилось пространство между водой и травой)
    screen.fill(BACKGROUND_TEAL)

    # отрисовка карты с основным и вторым слоями
    tile_map.draw_map(screen)

    # отрисовка животных
    animals_group.update(dt)
    animals_group.draw(screen)

    # обновление экрана
    pygame.display.flip()

# закрытие программы
pygame.quit()