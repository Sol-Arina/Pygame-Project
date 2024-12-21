import pygame
import random
import json
from sound import FarmerSound, BaseSound
from plants import Inventory, Plant


class Farmer:
    FRAME_SIZE = (48, 48)
    DOWN = 0
    UP = 1
    LEFT = 2
    RIGHT = 3

    WALK_ANIMATION = [0, 1, 2, 3]  # Индексы кадров для анимации ходьбы

    def __init__(self, screen, tilemap):
        self.screen = screen
        self.tilemap = tilemap
        self.spritesheet = pygame.image.load("farmer.png").convert_alpha()
        self.pos_x, self.pos_y = 560, 360
        self.direction = self.DOWN
        self.animation_index = 0
        self.frame_counter = 0
        self.speed = 3
        self.screen_rect = pygame.Rect(self.pos_x, self.pos_y, self.FRAME_SIZE[0], self.FRAME_SIZE[1])
        self.interaction_text = ""
        self.font = pygame.font.Font(None, 36)
        self.menu = []
        self.next_frame()
        self.voice = FarmerSound()
        self.inventory = Inventory()
        self.selected_tile = None
        self.selection_color = (144, 238, 144)
        self.planting_menu_open = False
        self.planting_menu = None
        self.current_tile_coords = None
        self.plants = {}
        self.inventory = Inventory()

        
        # Флаг для звука шагов
        self.playing_step_sound = False

        # Время для одного шага
        self.step_duration = 200  # длительность одного шага в миллисекундах (например 200 мс)

        # Время начала проигрывания звука
        self.step_sound_start_time = None
        
        self.is_interacting = False 


    def next_frame(self):
        row = self.direction
        col = self.animation_index
        self.frame_rect = pygame.Rect(
            col * self.FRAME_SIZE[0],
            row * self.FRAME_SIZE[1],
            self.FRAME_SIZE[0],
            self.FRAME_SIZE[1]
        )

    def update_animation(self):
        self.frame_counter += 1
        if self.frame_counter >= 10:  # Менять кадр каждые 10 кадров
            self.frame_counter = 0
            self.animation_index = (self.animation_index + 1) % len(self.WALK_ANIMATION)
            self.next_frame()

    def move(self, direction):
        """Двигает фермера в заданном направлении, если тайл проходим."""

        # Сохраняем текущую позицию для проверки
        new_x, new_y = self.pos_x, self.pos_y
        new_x_next, new_y_next = self.pos_x, self.pos_y
        if direction == self.DOWN:
            new_y += self.speed
            new_y_next += (self.speed + 1)
        elif direction == self.UP:
            new_y -= self.speed
            new_y_next -= (self.speed + 1)
        elif direction == self.LEFT:
            new_x -= self.speed
            new_x_next -= (self.speed + 1)
        elif direction == self.RIGHT:
            new_x += self.speed
            new_x_next += (self.speed + 1)

        # Определяем тайловые координаты
        tile_x = new_x // self.tilemap.tile_size
        tile_y = new_y // self.tilemap.tile_size

        tile_x_next = new_x_next // self.tilemap.tile_size
        tile_y_next = new_y_next // self.tilemap.tile_size

        if 0 <= tile_x < len(self.tilemap.map_data[0]) and 0 <= tile_y < len(self.tilemap.map_data):
            # Проверяем, является ли тайл проходимым
            if not self.tilemap.isitwater(tile_x, tile_y) and not self.tilemap.isitcollidable(tile_x, tile_y):
                # Если тайл проходим, обновляем позицию
                self.pos_x, self.pos_y = new_x, new_y
                self.screen_rect.topleft = (self.pos_x, self.pos_y)  # Обновляем экранный прямоугольник

                self.is_interacting = False
                
                # Если звук шагов не проигрывается, воспроизводим его
                if not self.playing_step_sound:
                    self.voice.play('steps')  # Проигрываем звук шагов
                    self.playing_step_sound = True  # Устанавливаем флаг
                    self.step_sound_start_time = pygame.time.get_ticks()  # Записываем время начала звука

            else:
                # Если не можем сделать шаг, играем звук "no"
                if self.playing_step_sound:
                    self.voice.play('no')  # Проигрываем звук "no"
                    self.playing_step_sound = False  # Сбрасываем флаг

            if self.tilemap.canifarmhere(tile_x_next, tile_y_next):
                if (tile_x_next, tile_y_next) not in self.plants:
                    self.selected_tile = (tile_x_next * self.tilemap.tile_size, tile_y_next * self.tilemap.tile_size)
                    self.current_tile_coords = (tile_x_next, tile_y_next)
                else:
                    self.selected_tile = None
                    self.current_tile_coords = None
            else:
                self.selected_tile = None
                self.current_tile_coords = None


        else:
            # Если выходим за пределы карты
            if not self.playing_step_sound:
                self.voice.play('no')  # Проигрываем звук "no"
                self.playing_step_sound = True  # Устанавливаем флаг

    def draw(self):
        self.screen.blit(self.spritesheet, self.screen_rect, self.frame_rect)
        if self.selected_tile:
            pygame.draw.rect(self.screen, self.selection_color, (*self.selected_tile, self.tilemap.tile_size, self.tilemap.tile_size), 2)


    def update(self):
        self.update_animation()

        if self.planting_menu_open and self.planting_menu:
            self.planting_menu.draw()

        # Проверяем, если звук шагов проигрывается слишком долго, останавливаем его
        if self.playing_step_sound and self.step_sound_start_time:
            if pygame.time.get_ticks() - self.step_sound_start_time >= self.step_duration:
                self.voice.stop('steps')  # Останавливаем звук шагов после истечения времени шага
                self.playing_step_sound = False

    def handle_input(self, events):
        """Обрабатывает ввод с клавиатуры."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.move(Farmer.LEFT)
        elif keys[pygame.K_RIGHT]:
            self.move(Farmer.RIGHT)
        elif keys[pygame.K_UP]:
            self.move(Farmer.UP)
        elif keys[pygame.K_DOWN]:
            self.move(Farmer.DOWN)

        if keys[pygame.K_RETURN] and self.selected_tile and not self.planting_menu_open:
            return "open_planting_menu"

    def open_planting_menu(self):
        self.planting_menu_open = True
        self.planting_menu = PlantingMenu(self.screen, self)
        self.planting_menu.visible = True

    def check_interaction(self, animals_group, plants_group=None):
        """Проверяет взаимодействие с животными или растениями."""
        if self.is_interacting:  # Если уже было взаимодействие, не повторяем
           return None, None
    
        if plants_group:
            for plant in plants_group: 
                if self.screen_rect.colliderect(plant.rect):
                    self.is_interacting = True
                    return "plant", plant  # Возвращаем тип объекта и сам объект
        for animal in animals_group:
            if self.screen_rect.colliderect(animal.rect):
                self.is_interacting = True
                return "animal", animal  # Возвращаем тип объекта и сам объект
        return None, None  # Если взаимодействия нет
    
    def plant_seed(self, seed_name):
        if self.current_tile_coords and seed_name in self.inventory.items and self.inventory.items[seed_name] > 0:
            x, y = self.current_tile_coords
            stages = self.get_growth_stages(seed_name)
            plant = Plant(name=seed_name, growth_stages=stages, x=x * self.tilemap.tile_size, y=y * self.tilemap.tile_size)
            self.plants[(x, y)] = plant
            self.inventory.remove_item(seed_name, 1)
            self.selected_tile = None
            self.current_tile_coords = None
            self.planting_menu_open = False

    def get_growth_stages(self, seed_name):
        if seed_name == 'Wheat Seeds':
            return [pygame.image.load(f'assets/plant stages/wheat{i}.png') for i in range(1, 5)]
        elif seed_name == 'Tomato Seeds':
            return [pygame.image.load(f'assets/plant stages/tomato{i}.png') for i in range(1, 5)]
        elif seed_name == 'Strawberry Seeds':
            return [pygame.image.load(f'assets/plant stages/strawberry{i}.png') for i in range(1, 3)]
        elif seed_name == 'Apple Seeds':
            return [pygame.image.load(f'assets/plant stages/apple{i}.png') for i in range(1, 3)]

    def update_volume(self):
        """Обновляет громкость звуков фермера согласно глобальной громкости."""
        self.voice.update_volume()

    def feed(self):
        self.voice.play('okay')


class InteractionMenu:
    def __init__(self, screen):
        self.screen = screen
        self.options = []  # Список действий
        self.selected_index = 0  # Выбранный пункт меню
        self.font = pygame.font.Font('assets/fonts/pixelFont-7-8x14-sproutLands.ttf', 20)
        self.visible = False  # Видимость меню
        

    def draw(self):
        """Отрисовка меню на экране."""
        if not self.visible:
            return

        menu_width = 200
        menu_height = 40 * len(self.options)
        menu_x = self.screen.get_width() // 2 - menu_width // 2
        menu_y = self.screen.get_height() // 2 - menu_height // 2
        pygame.draw.rect(self.screen, (255, 229, 204), (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(self.screen, (255, 178, 102), (menu_x, menu_y, menu_width, menu_height), 2)

        for i, option in enumerate(self.options):
            color = (51, 0, 0) if i == self.selected_index else (102, 51, 0)
            text_surface = self.font.render(option, True, color)
            self.screen.blit(text_surface, (menu_x + 20, menu_y + 10 + i * 30))

    def handle_input(self, event):
        """Обработка ввода для управления меню."""
        if not self.visible:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:  # Перемещение вверх
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:  # Перемещение вниз
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:  # Выбор пункта меню
                return self.options[self.selected_index]
            elif event.key == pygame.K_ESCAPE:  # Закрытие меню
                self.visible = False

        return None



class AnimalMenu(InteractionMenu):
    def __init__(self, screen, animal, farmer):
        super().__init__(screen)
        self.options = ['feed', 'close']
        self.farmer = farmer
        self.animal = animal

    def feed(self):
        """Кормит животное."""
        self.farmer.feed()
        self.animal.feed()  # Добавьте действия для животного, если нужно
        #self.farmer.is_interacting = False

    def handle_input(self, event):
        """Обрабатывает ввод для AnimalMenu."""
        selected_action = super().handle_input(event)
        if selected_action:
            if selected_action == 'feed':
                self.feed()
            elif selected_action == 'close':
                self.visible = False
            self.visible = False
            return selected_action
        return None
    


class PlantMenu(InteractionMenu):
    def __init__(self, screen, plant, farmer):
        super().__init__(screen)
        self.options = ['water', 'close']
        self.farmer = farmer
        self.plant = plant

    def water(self):
        """Кормит животное."""
        self.farmer.feed()
        # self.plant.eat()  # Добавьте действия для животного, если нужно
        #self.farmer.is_interacting = False

    def handle_input(self, event):
        """Обрабатывает ввод для PlantMenu."""
        selected_action = super().handle_input(event)
        if selected_action:
            if selected_action == 'water':
                self.water()
            elif selected_action == 'close':
                self.visible = False
            self.visible = False
            return selected_action
        return None
    

class PlantingMenu(InteractionMenu):
    def __init__(self, screen, farmer):
        super().__init__(screen)
        self.farmer = farmer
        self.options = [f"{seed} ({count})" for seed, count in self.farmer.inventory.items.items() if count > 0]



    def handle_input(self, event):
        selected_action = super().handle_input(event)
        if selected_action:
            seed_name = selected_action.split(' (')[0]  # Извлекаем имя семян
            self.farmer.plant_seed(seed_name)
            self.visible = False
            return seed_name
        return False

    def draw(self):
        super().draw()  # Используем метод отрисовки из InteractionMenu