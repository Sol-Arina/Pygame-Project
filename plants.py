import pygame
import time
from tiles import *
from spritesheet import Spritesheet


class Inventory:
    def __init__(self):
        self.items = {
            'Wheat Seeds': 5,
            'Tomato Seeds': 5,
            'Strawberry Seeds': 5,
            'Apple Seeds': 5
        }
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

class Plant(pygame.sprite.Sprite): # ОСТАНОВИЛАСЬ ЗДЕСЬ!!!!!!!!!!!!!!!!!!!!!!!!!!
    '''Класс растений: пшеница, помидоры, яблоки, клубника'''
    def __init__(self, name, growth_stages, tile_map, screen, inventory, pos, growth_time=60):
        super().__init__()
        self.name = name
        self.growth_stages = growth_stages
        self.current_stage = 0  # текущая фаза роста
        self.growth_time = growth_time  # время на каждую фазу роста (в секундах)
        self.last_growth_time = time.time()  # время последнего обновления фазы
        self.harvested = False  # растение не достигло полной зрелости или да
        self.tile_map = tile_map
        self.screen = screen
        self.inventory = inventory
        self.pos = pos  # координаты растения на грядке
        self.drop = None  # здесь будет храниться изображение дропа
        self.wateredtimes = 0

        # устанавливаем начальное изображение и rect
        self.image = self.growth_stages[self.current_stage]
        self.rect = self.image.get_rect(topleft=(pos[0] * tile_map.tile_size, pos[1] * tile_map.tile_size))

    '''@staticmethod
    def create_plant(self, plant_name, pos, tile_map, screen, inventory):
        x, y = pos[0] // tile_map.tile_size, pos[1] // tile_map.tile_size

        if tile_map.canifarmhere(x, y):
            plant = Plant(plant_name, self.growth_stages[plant_name], tile_map, screen, inventory, (x, y))
            inventory.remove_item(f'{plant_name} Seeds', 1)  #
            return plant
        else:
            print('Нельзя сажать на этом тайле!')
            return None '''

    def iswatered(self):
        self.wateredtimes += 1   

    def grow(self):
        '''обновление фазы роста'''
        if time.time() - self.last_growth_time > self.growth_time:
            self.current_stage += 1
            if self.current_stage >= len(self.growth_stages):
                self.harvested = True  # Растение дало плоды
                #self.drop = pygame.image.load(f'assets/drops/{self.name.lower()}_drop.png')  # добавляем дроп
            else:
                self.image = self.growth_stages[self.current_stage]  # переход на следующую фазу роста
            self.last_growth_time = time.time()

    def update(self):
        '''обновление состояния растения'''
        self.grow()

    def plant(self, pos, plant_name):
        '''посадка растения с проверкой на грядку'''
        x, y = pos[0] // self.tile_map.tile_size, pos[1] // self.tile_map.tile_size
        if self.tile_map.canifarmhere(x, y):  # проверяем, можно ли сажать
            self.pos = (x, y)
            self.rect.topleft = (x * self.tile_map.tile_size, y * self.tile_map.tile_size)
            self.inventory.remove_item(plant_name, 1)  # уменьшаем количество семян
        else:
            print('Нельзя сажать на этом тайле!')

    def draw(self):
        '''отрисовка растений'''
        self.screen.blit(self.image, self.rect.topleft)
        # если растение полностью созрело, отрисовываем дроп рядом с ним
        if self.harvested and self.drop:
            drop_rect = self.drop.get_rect(topleft=(self.rect.x + 20, self.rect.y + 20))  # дроп рисуем рядом с растением
            self.screen.blit(self.drop, drop_rect.topleft)

    def collect(self):
        '''сбор урожая'''
        if self.harvested:
            self.inventory.add_harvest(self.name.split()[0], 1)
            print(f'Собрано: {self.name}')
            return True  # урожай можно собрать
        return False