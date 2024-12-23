import pygame
import time
from tiles import *


class Inventory:
    def __init__(self):
        self.items = {
            'Wheat Seeds': 5,
            'Tomato Seeds': 5,
            'Strawberry Seeds': 5,
            'Apple Seeds': 5
        }
        self.products = {'milk' : 0, 'eggs' : 0}
        self.harvest = {}  # урожай, который собран (яблоки, пшеница..........)

    def add_item(self, item, quantity=1):
        if item in self.items:
            self.items[item] += quantity
        else:
            self.items[item] = quantity

    def remove_item(self, item, quantity=1):
        if item in self.items and self.items[item] >= quantity:
            self.items[item] -= quantity

    def add_harvest(self, crop, quantity=1):
        if crop in self.harvest:
            self.harvest[crop] += quantity
        else:
            self.harvest[crop] = quantity

class Plant(pygame.sprite.Sprite):
    '''Класс растений: пшеница, помидоры, яблоки, клубника.'''
    def __init__(self, name, growth_stages, growth_time=60, x=0, y=0):
        super().__init__()
        self.name = name
        self.growth_stages = growth_stages
        self.current_stage = 0  # Текущая фаза роста
        self.growth_time = growth_time  # Время на фазу роста (в секундах)
        self.last_growth_time = time.time()  # Время последнего обновления фазы
        self.harvested = False  # Флаг, что растение дало плоды
        self.image = self.growth_stages[self.current_stage]
        self.rect = self.image.get_rect(topleft=(x, y))

    def grow(self):
        '''Обновление фазы роста.'''
        if time.time() - self.last_growth_time > self.growth_time:
            self.current_stage += 1
            if self.current_stage >= len(self.growth_stages):
                self.harvested = True  # Растение дало плоды
                self.current_stage = len(self.growth_stages) - 1
            self.image = self.growth_stages[self.current_stage]
            self.last_growth_time = time.time()

    def update(self):
        self.grow()


    def get_image(self):
        '''Возвращаем изображение растения в зависимости от его текущей фазы.'''
        return self.growth_stages[self.current_stage] if self.current_stage < len(self.growth_stages) else self.growth_stages[-1]

class Farm:
    '''Класс для управления посадкой ЕГО СОЕДИНИТЬ С КЛАССОМ РАСТЕНИЕ'''
    def __init__(self, screen, tile_map, font_path):
        self.screen = screen
        self.tile_map = tile_map
        self.font = pygame.font.Font(font_path, 20)
        self.inventory = Inventory()
        self.plants = {}  # Растения на грядке, с координатами тайлов в качестве ключей
        self.selected_tile = None
        self.selection_color = (144, 238, 144)  # Нежно-зелёный цвет для обводки
        self.plant_selection_window_open = False  # Окно выбора растения
        self.drops = []

    def draw(self):
        '''Отрисовка растений'''
        # Рисуем все растения
        for (x, y), plant in self.plants.items():
            plant_image = plant.get_image()
            self.screen.blit(plant_image, (x * self.tile_map.tile_size, y * self.tile_map.tile_size))

            # Если растение созрело, добавляем дроп
            if plant.harvested:
                drop_image = pygame.image.load('assets/plant stages/wheatdrop.png')  # Здесь путь к изображению дропа
                self.drops.append({'pos': (x * self.tile_map.tile_size, y * self.tile_map.tile_size), 'image': drop_image})

        # Отрисовываем дропы
        for drop in self.drops:
            self.screen.blit(drop['image'], drop['pos'])

        # Если выбран тайл для посадки, обводим его
        if self.selected_tile:
            pygame.draw.rect(self.screen, self.selection_color, (*self.selected_tile, self.tile_map.tile_size, self.tile_map.tile_size), 2)

    def handle_click(self, pos):
        '''Обработка клика по ферме для посадки растения.'''
        x, y = pos[0] // self.tile_map.tile_size, pos[1] // self.tile_map.tile_size

        # Проверяем, можно ли сажать на этом тайле
        if self.tile_map.canifarmhere(x, y):
            self.selected_tile = (x * self.tile_map.tile_size, y * self.tile_map.tile_size)
            self.plant_selection_window_open = True  # Открываем окно выбора растения
        else:
            print('Тут нельзя сажать!')  # Вывод сообщения, если нельзя сажать

# Это у фермера щас !!!!!!!!!!!!!!!!!!!
    '''def draw_plant_selection_window(self):
        Отрисовка окошка выбора растения.
        if self.plant_selection_window_open:
            # Окно выбора с растениями
            pygame.draw.rect(self.screen, (200, 200, 200), (self.selected_tile[0], self.selected_tile[1] - 100, 150, 100))
            self.draw_text('Seed choice:', self.selected_tile[0] + 5, self.selected_tile[1] - 90)

            # Отрисовываем варианты растений, проверяем, есть ли семена
            y_offset = self.selected_tile[1] - 70
            for seed in self.inventory.items:
                if self.inventory.items[seed] > 0:
                    self.draw_text(f'{seed}', self.selected_tile[0] + 5, y_offset)
                    y_offset += 20'''

    def plant_plant(self, plant_name):
        '''Сажаем выбранное растение.'''
        if plant_name == 'Wheat Seeds':
            stages = [pygame.image.load('assets/plant stages/wheat1.png'), pygame.image.load('assets/plant stages/wheat2.png'), pygame.image.load('assets/plant stages/wheat3.png'), pygame.image.load('assets/plant stages/wheat4.png')]
        elif plant_name == 'Tomato Seeds':
            stages = [pygame.image.load('assets/plant stages/tomato1.png'), pygame.image.load('assets/plant stages/tomato2.png'), pygame.image.load('assets/plant stages/tomato3.png'), pygame.image.load('assets/plant stages/tomato4.png')]
        elif plant_name == 'Apple Seeds':
            stages = [pygame.image.load('assets/plant stages/apple1.png'), pygame.image.load('assets/plant stages/apple2.png')]
        elif plant_name == 'Srawberry Seeds':
            stages = [pygame.image.load('assets/plant stages/strawberry1.png'), pygame.image.load('assets/plant stages/strawberry2.png')]
       

        plant = Plant(name=plant_name, growth_stages=stages)
        x, y = self.selected_tile[0] // self.tile_map.tile_size, self.selected_tile[1] // self.tile_map.tile_size
        self.plants[(x, y)] = plant  # Сажаем растение на грядке
        self.inventory.remove_item(plant_name, 1)  # Уменьшаем количество семян
        self.plant_selection_window_open = False  # Закрываем окно выбора растения

    def update(self):
        '''Обновление фермы и проверка роста растений.'''
        for plant in self.plants.values():
            plant.grow()

    def handle_drop_click(self, pos):
        '''Обработка клика по дропу для сбора урожая.'''
        x, y = pos[0] // self.tile_map.tile_size, pos[1] // self.tile_map.tile_size
        for drop in self.drops:
            drop_pos = drop['pos']
            if drop_pos[0] <= x * self.tile_map.tile_size <= drop_pos[0] + self.tile_map.tile_size and \
               drop_pos[1] <= y * self.tile_map.tile_size <= drop_pos[1] + self.tile_map.tile_size:
                plant_name = self.plants[(x, y)].name
                self.inventory.add_harvest(plant_name.split()[0], 1)  # Добавляем в инвентарь урожай
                self.drops.remove(drop)  # Удаляем дроп
                del self.plants[(x, y)]  # Удаляем растение после сбора
                print(f'Собрано: {plant_name}')

    def draw_text(self, text, x, y, color=(0, 0, 0)):
        '''Функция для отрисовки текста.'''
        font = pygame.font.Font(None, 20)
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))