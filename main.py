import sys
import time
import json
import pygame
import pygame_menu
from tiles import *
from spritesheet import Spritesheet # type: ignore
from animals import Animal, Cow, Chicken, load_animal_frames
from farmer import Farmer, InteractionMenu
from sound import BackgroundSound, BaseSound, AnimalSound, FarmerSound
from actionmenu import ActionMenu
from plants import Plant
from plants import Inventory
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

# ACTION MENU
# загрузка изображений и шрифта
font_path = 'assets/fonts/pixelFont-7-8x14-sproutLands.ttf'
item_images = {
    'wheat': 'assets/action_menu/wheat.png',
    'tomato': 'assets/action_menu/tomato.png',
    'strawberrybush': 'assets/action_menu/strawberrybush.png',
    'appletree': 'assets/action_menu/appletree.png',
    'chicken': 'assets/action_menu/chicken.png',
    'cow': 'assets/action_menu/cow.png',
    'coin': 'assets/action_menu/coin.png',
}

background_image = pygame.image.load('assets/action_menu/background.png')

# загрузка иконки для открытия меню
menu_icon = pygame.image.load('assets/action_menu/menu_icon.png')  
menu_icon_rect = menu_icon.get_rect()
menu_icon_rect.topleft = (SCREEN_WIDTH - 60, 20)  # правый верхний угол

action_menu = ActionMenu(screen, font_path, item_images)
#menu_act = action_menu.create_menu() 


"""        ЖИВОТНЫЕ        """
# загрузка фреймов для анимации животных
cow_frames_data = load_animal_frames('cow_sprite_sheet.json')
chicken_frames_data = load_animal_frames('chicken_sprite_sheet.json')

# загрузка спрайтов животных
cow_spritesheet = Spritesheet('cow_sprite_sheet.png')
chicken_spritesheet = Spritesheet('chicken_sprite_sheet.png')

# создание группы для животных
animals_group = pygame.sprite.Group()

# список кадров для анимации коровы
cow_frame_names = [
    'cow_eye_closed.png',
    'cow_static.png',
    'cow_tail_up.png',
    'cow_walking.png',
    'cow_walking1.png'
]

# список кадров для анимации курицы
chicken_frame_names = [
    'chicken_eyes_closed.png',
    'chicken_static.png',
    'chicken_static1.png',
    'chicken_walking.png',
    'chicken_walking1.png',
    'chicken_walking3.png'
]

# создание животных
cow = Cow(350, 200, cow_spritesheet, cow_frames_data, cow_frame_names, (32, 32), tilemap=tile_map)
chicken = Chicken(800, 240, chicken_spritesheet, chicken_frames_data, chicken_frame_names, (16, 16), tilemap=tile_map)

# добавление животных в группу
animals_group.add(cow, chicken)

# ------- РАСТЕНИЯ --------
# создание группы для растений
plants_group = pygame.sprite.Group()

inventory = Inventory()
pos = (21,23) # FOR TESTING PLANTS
pos1 = (24, 23)
pos2 = (26, 23)
pos3 = (28, 23)
# добавление растений в группу  
wheat = Plant('Wheat', growth_stages=[pygame.image.load('assets/plant stages/wheat1.png'), pygame.image.load('assets/plant stages/wheat2.png'), pygame.image.load('assets/plant stages/wheat3.png'), pygame.image.load('assets/plant stages/wheat4.png')], tile_map=tile_map, screen=screen, inventory=inventory, pos=pos)
tomato = Plant('Tomato', growth_stages=[pygame.image.load('assets/plant stages/tomato1.png'), pygame.image.load('assets/plant stages/tomato2.png'), pygame.image.load('assets/plant stages/tomato3.png'), pygame.image.load('assets/plant stages/tomato4.png')], tile_map=tile_map, screen=screen, inventory=inventory, pos=pos1)
apple = Plant('Apple', growth_stages=[pygame.image.load('assets/plant stages/apple1.png'), pygame.image.load('assets/plant stages/apple2.png')], tile_map=tile_map, screen=screen, inventory=inventory, pos=pos2)
strawberry = Plant ('Strawberry', growth_stages=[pygame.image.load('assets/plant stages/strawberry1.png'), pygame.image.load('assets/plant stages/strawberry2.png')], tile_map=tile_map, screen=screen, inventory=inventory, pos=pos3)
plants_group.add(wheat, tomato, apple, strawberry) 


'''ОГОРОДНИК'''
farmer = Farmer(screen, tile_map)
##################################################################################

'''МЕНЮ ВЗАИМОДЕЙСТВИЯ С ОБЪЕКТАМИ'''
menu = InteractionMenu(screen, []) #класс меню в farmer.py
animal_menu_options = ["Покормить", "Собрать продукты", "Назад"]
plant_menu_options = ["Полить", "Собрать урожай", "Назад"]


'''Фоновая музыка'''
bs = BackgroundSound('music.mp3') #сюда можно ввести название любого звукового файла, который хотим поставить на фон
bs.play()

# GAME LOOP
running = True
menu_open = False  # отслеживание, открыто ли меню
while running:
    dt = clock.tick(60)  # Ограничиваем FPS до 60
    events = pygame.event.get()
    
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        # ACTION меню условие
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if menu_icon_rect.collidepoint(mouse_pos):
                menu_open = not menu_open
                if menu_open:
                    action_menu.switch_to_main()
                else:
                    action_menu.menu.disable()
                    action_menu.shop_menu.disable()
                    action_menu.inventory_menu.disable()
      

            # Регулировка громкости
        BaseSound.adjust_volume(event)

        # Обновляем громкость у всех звуков через их владельцев
        bs.update_volume()
        farmer.update_volume()  # Обновление громкости фермера

    # Проверка взаимодействий
    interaction_type, target_object = farmer.check_interaction(animals_group, plants_group)
    
    for animal in animals_group:
        animal.update_volume()  # Обновление громкости животных

        # Обработка меню
        if menu.visible:
            action = menu.handle_input(event)
            if action:
                if action == "Назад":
                    menu.visible = False
                elif action == "Покормить":
                    target_object.feed()
                    print("Животное покормлено!")
                    menu.visible = False
                elif action == 'Собрать продукты':
                    pass
                elif action == "Полить":
                    print("Растение полито!")

    # Обновление фермера
    if not menu.visible:  # Если меню не активно
        farmer.handle_input()
        farmer.update()
    
    # # Проверка взаимодействий
    # interaction_type, target_object = farmer.check_interaction(animals_group, plants_group)
    if interaction_type == "animal" and not menu.visible:
        menu.visible = True
        menu.options = animal_menu_options
    elif interaction_type == "plant" and not menu.visible:
        menu.visible = True
        menu.options = plant_menu_options

    # Отрисовка объектов
    if menu_open:
            if action_menu.current_menu and action_menu.current_menu.is_enabled():
                action_menu.current_menu.update(events)
                action_menu.current_menu.draw(screen)
    else:
        screen.fill(BACKGROUND_TEAL)
        tile_map.draw_map(screen)
        farmer.draw()
        animals_group.update(dt)
        animals_group.draw(screen)
         # Обновляем и рисуем растения
        for plant in plants_group:
            plant.update()
            plant.draw()
        menu.draw()
        screen.blit(menu_icon, menu_icon_rect)
    
    pygame.display.flip()

pygame.quit()