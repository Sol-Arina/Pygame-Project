import sys
import time
import json
import pygame
from tiles import *
from spritesheet import Spritesheet # type: ignore
from animals import Animal, load_animal_frames
from farmer import Farmer, InteractionMenu
from sound import BackgroundSound, BaseSound, AnimalSound, FarmerSound
# sys.dont_write_bytecode = True
# from lib.core import Core


# инициализация pygame
pygame.mixer.pre_init(44100, -16, 1, 512) 
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
animals_group = pygame.sprite.Group() #нужно будет создать plants_group, чтобы появлялось меню взаимодействия с растениями

cow = Animal(300, 300, cow_spritesheet, animal_frames['cow'], 'cow')
chicken = Animal(500, 500, chicken_spritesheet, animal_frames['chicken'], 'chicken')

animals_group.add(cow, chicken)


'''ОГОРОДНИК'''
farmer = Farmer(screen, tile_map)
##################################################################################

'''МЕНЮ ВЗАИМОДЕЙСТВИЯ С ОБЪЕКТАМИ'''
menu = InteractionMenu(screen, []) #класс меню в farmer.py
animal_menu_options = ["Покормить", "Назад"]
plant_menu_options = ["Полить", "Собрать урожай", "Назад"]


'''Фоновая музыка'''
bs = BackgroundSound('music.mp3') #сюда можно ввести название любого звукового файла, который хотим поставить на фон
bs.play()

# GAME LOOP
running = True
while running:
    dt = clock.tick(60)  # Ограничиваем FPS до 60
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
       # Регулировка громкости
    BaseSound.adjust_volume(event)

    # Обновляем громкость у всех звуков через их владельцев
    bs.update_volume()
    farmer.update_volume()  # Обновление громкости фермера
    for animal in animals_group:
        animal.update_volume()  # Обновление громкости животных

        # Обработка меню
        if menu.visible:
            action = menu.handle_input(event)
            if action:
                if action == "Назад":
                    menu.visible = False
                elif action == "Покормить":
                    print("Животное покормлено!")
                elif action == "Полить":
                    print("Растение полито!")
    
    # Обновление фермера
    if not menu.visible:  # Если меню не активно
        farmer.handle_input()
    farmer.update()
    
    # Проверка взаимодействий
    interaction_type, target_object = farmer.check_interaction(animals_group)
    if interaction_type == "animal" and not menu.visible:
        menu.visible = True
        menu.options = animal_menu_options
    elif interaction_type == "plant" and not menu.visible:
        menu.visible = True
        menu.options = plant_menu_options

    # Отрисовка объектов
    screen.fill(BACKGROUND_TEAL)
    tile_map.draw_map(screen)
    farmer.draw()
    animals_group.update(dt)
    animals_group.draw(screen)
    menu.draw()

    
    
    pygame.display.flip()

pygame.quit()