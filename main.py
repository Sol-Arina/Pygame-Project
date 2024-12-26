import pygame
import json
from tiles import *
from spritesheet import Spritesheet # type: ignore
from animals import Animal, Cow, Chicken, load_animal_frames
from farmer import Farmer, InteractionMenu, AnimalMenu, PlantMenu, PlantingMenu
from sound import BackgroundSound, BaseSound, AnimalSound, FarmerSound
from actionmenu import ActionMenu
from plants import Plant
# sys.dont_write_bytecode = True
# from lib.core import Core

def save_game(file_path, farmer, animals_group, plants_group, action_menu):
    """сохранение состояния игры в файл"""
    game_state = {
        "farmer": {
            "position" : [farmer.pos_x, farmer.pos_y],
            "inventory": {
                "items": farmer.inventory.items,
                "products": farmer.inventory.products,
                "harvest": farmer.inventory.harvest,
            },
            "money" : farmer.money
        },
        "animals": [
            {
                "type": animal.animal_type,
                "position": [animal.pos.x, animal.pos.y],
                "hunger": animal.hunger,
                "energy": animal.energy,
                "milk_ready": getattr(animal, "milk_ready", False),
                "egg_ready": getattr(animal, "egg_ready", False),
            } for animal in animals_group
        ],
        "plants": [
            {
                "name": plant.name,
                "position": [plant.rect.x, plant.rect.y],
                "current_stage": plant.current_stage,
                "growth_time": plant.growth_time,
            } for plant in plants_group
        ],
        "action_menu": {
            "shop_items": action_menu.shop_items,
            "sell_items": action_menu.sell_items,
            "total_cost": action_menu.total_cost,
            "current_menu": (
                "shop" if action_menu.current_menu == action_menu.shop_menu else
                "inventory" if action_menu.current_menu == action_menu.inventory_menu else
                "main"
            ),
        },
    }
    
    with open(file_path, "w") as f:
        json.dump(game_state, f, indent=4)


def load_game(file_path, farmer, animals_group, plants_group, action_menu):
    """загрузка состояния игры из файла"""
    try:
        with open(file_path, "r") as f:
            game_state = json.load(f)
        
        # Восстанавливаем состояние фермера
        farmer.pos_x, farmer.pos_y = game_state["farmer"]["position"]
        farmer.inventory.items = game_state["farmer"]["inventory"]["items"]
        farmer.inventory.products = game_state["farmer"]["inventory"]["products"]
        farmer.inventory.harvest = game_state["farmer"]["inventory"]["harvest"]
        farmer.money = game_state["farmer"]["money"]

        # Восстанавливаем животных
        animals_group.empty()
        for animal_data in game_state["animals"]:
            if animal_data["type"] == "cow":
                animal = Cow(
                    animal_data["position"][0],
                    animal_data["position"][1],
                    cow_spritesheet,
                    cow_frames_data,
                    cow_frame_names,
                    (32, 32),
                    tilemap=tile_map,
                )
            elif animal_data["type"] == "chicken":
                animal = Chicken(
                    animal_data["position"][0],
                    animal_data["position"][1],
                    chicken_spritesheet,
                    chicken_frames_data,
                    chicken_frame_names,
                    (16, 16),
                    tilemap=tile_map,
                )
            animal.hunger = animal_data["hunger"]
            animal.energy = animal_data["energy"]
            if "milk_ready" in animal_data:
                animal.milk_ready = animal_data["milk_ready"]
            if "egg_ready" in animal_data:
                animal.egg_ready = animal_data["egg_ready"]
            animals_group.add(animal)

        # Восстанавливаем растения
        plants_group.empty()
        for plant_data in game_state["plants"]:
            growth_stages = farmer.get_growth_stages(plant_data["name"])
            if not growth_stages:
                print(f"Skipping plant {plant_data['name']} due to missing growth stages.")
                continue

            plant = Plant(
                name=plant_data["name"],
                growth_stages=growth_stages,
                growth_time=plant_data["growth_time"],
                x=plant_data["position"][0],
                y=plant_data["position"][1],
            )
            plant.current_stage = plant_data["current_stage"]
            plants_group.add(plant)

            # Восстанавливаем состояние Action Menu
        action_menu.shop_items = game_state["action_menu"]["shop_items"]
        action_menu.sell_items = game_state["action_menu"]["sell_items"]
        action_menu.total_cost = game_state["action_menu"]["total_cost"]

        current_menu = game_state["action_menu"]["current_menu"]
        if current_menu == "shop":
            action_menu.current_menu = action_menu.shop_menu
        elif current_menu == "inventory":
            action_menu.current_menu = action_menu.inventory_menu
        else:
            action_menu.current_menu = action_menu.menu

        action_menu.update_money_display()

    except FileNotFoundError:
        print("Сохраненный файл не найден. Начинаем новую игру.")


def prompt_for_choice(file_path):
    """Запрашивает выбор: новая игра или продолжение."""
    while True:
        choice = input("Введите 'n' для новой игры или 'c' для продолжения: ").strip().lower()
        if choice == 'n':
            if os.path.exists(file_path):
                os.remove(file_path)  # Удаляем файл сохранения
            print("Начинаем новую игру...")
            return False  # Не загружать сохранение
        elif choice == 'c':
            if os.path.exists(file_path):
                print("Продолжаем сохраненную игру...")
                return True  # Загружать сохранение
            else:
                print("Файл сохранения не найден. Начинаем новую игру...")
                return False  # Не загружать сохранение
        else:
            print("Неверный ввод. Введите 'n' или 'c'.")

# Основной код
file_path = "game_save.json"

# Спрашиваем выбор перед началом игры
load_saved_game = prompt_for_choice(file_path)


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
tile_map = TileMap(TILE_SIZE, 'assets/environment/ground_tiles_environment.csv', 'assets/environment/ground_tiles_overlay_decor_biom.csv')

# загрузка тайлов для основного слоя
# ID тайла с грядкой - 504  (карта = ground_tiles_environment.csv, файлы = environmentsprites.png', environmentsprites.json') 
tile_map.add_tiles_from_image('assets/environment/environmentsprites.png', starting_index=0)

# загрузка тайлов для второго слоя, здесь деревья без урожая, цветы, камни, забор, дорожки, домик, грибы
tile_map.add_overlay_tiles_from_image('assets/environment/2ndlayer.png', starting_index=0)

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
#menu_act = action_menu.create_menu() 


#"""        ЖИВОТНЫЕ        """
# загрузка фреймов для анимации животных
cow_frames_data = load_animal_frames('assets/animals/cow_sprite_sheet.json')
chicken_frames_data = load_animal_frames('assets/animals/chicken_sprite_sheet.json')

# загрузка спрайтов животных
cow_spritesheet = Spritesheet('assets/animals/cow_sprite_sheet.png')
chicken_spritesheet = Spritesheet('assets/animals/chicken_sprite_sheet.png')

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

# # создание тестовых животных
# cow = Cow(350, 200, cow_spritesheet, cow_frames_data, cow_frame_names, (32, 32), tilemap=tile_map)
# chicken = Chicken(800, 240, chicken_spritesheet, chicken_frames_data, chicken_frame_names, (16, 16), tilemap=tile_map)

# # добавление животных в группу
# #animals_group.add(cow, chicken)

##################################################################################

'''МЕНЮ ВЗАИМОДЕЙСТВИЯ С ОБЪЕКТАМИ'''
menu = InteractionMenu(screen) #класс меню в farmer.py

# '''Растения тест'''
# plant_growth_stages = [
#     pygame.image.load('assets/plant stages/wheat1.png'),
#     pygame.image.load('assets/plant stages/wheat2.png'),
#     pygame.image.load('assets/plant stages/wheat3.png'),
#     pygame.image.load('assets/plant stages/wheat4.png')
# ]
# test_plant = Plant(name="Test Plant", growth_stages=plant_growth_stages, growth_time=5, x=400, y=350)


plants_group = pygame.sprite.Group()
#plants_group.add(test_plant)

'''ОГОРОДНИК'''
farmer = Farmer(screen, tile_map, plants_group, animals_group)

'''Фоновая музыка'''
bs = BackgroundSound('sound/environment/music.mp3') #сюда можно ввести название любого звукового файла, который хотим поставить на фон
bs.play()

animal_menu = None
plant_menu = None
planting_menu = None

action_menu = ActionMenu(screen, font_path, item_images, farmer=farmer)

file_path = "game_save.json"
if load_saved_game:
    load_game("save_file.json", farmer, animals_group, plants_group, action_menu)
# Game loop
running = True
menu_open = False 
while running:
    dt = clock.tick(60)
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            # Сохраняем игру и выходим
            save_game("save_file.json", farmer, animals_group, plants_group, action_menu)
            running = False
            break

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
        
        BaseSound.adjust_volume(event)
        bs.update_volume()
        farmer.update_volume()
        for animal in animals_group:
            animal.update_volume()

        # Handle menus
        if animal_menu and animal_menu.visible:
            action = animal_menu.handle_input(event)
            if action:
                animal_menu = None  

        if plant_menu and plant_menu.visible:
            action = plant_menu.handle_input(event)
            if action:
                plant_menu = None

        if planting_menu and planting_menu.visible:
            if planting_menu.handle_input(event):
                planting_menu = None


    if not (animal_menu and animal_menu.visible) \
        and not (plant_menu and plant_menu.visible) \
        and not (planting_menu and planting_menu.visible):

        command = farmer.handle_input(events)
        farmer.update()
        if command == "open_planting_menu":
            planting_menu = PlantingMenu(screen, farmer)
            planting_menu.visible = True
    

    interaction_type, target_object = farmer.check_interaction(animals_group)
    if interaction_type == "animal" and not (animal_menu and animal_menu.visible):
        animal_menu = AnimalMenu(screen, target_object, farmer, action_menu)
        animal_menu.visible = True
    elif interaction_type == "plant" and not (plant_menu and plant_menu.visible):
        plant_menu = PlantMenu(screen, target_object, farmer, action_menu)
        plant_menu.visible = True

    #plants_group.update()

    if menu_open:
            if action_menu.current_menu and action_menu.current_menu.is_enabled():
                action_menu.current_menu.update(events)
                action_menu.current_menu.draw(screen)
                pygame.display.flip()
    else:
        screen.fill(BACKGROUND_TEAL)
        tile_map.draw_map(screen)
        farmer.draw()
        animals_group.update(dt)
        animals_group.draw(screen)
        farmer.animals_group.update(dt)
        farmer.animals_group.draw(screen)
        plants_group.update()
        plants_group.draw(screen)

        for plant in plants_group:
            screen.blit(plant.get_image(), (plant.rect.x, plant.rect.y))
            plant.draw_status(screen)

        for animal in animals_group:
            animal.draw_status(screen)

        if planting_menu and planting_menu.visible:
            planting_menu.draw()

        if animal_menu:
            animal_menu.draw()
        if plant_menu:
            plant_menu.draw()
        
        menu.draw()
        screen.blit(menu_icon, menu_icon_rect)
        pygame.display.flip()

pygame.quit()
