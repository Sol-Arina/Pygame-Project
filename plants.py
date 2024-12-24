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

        self.products = {'milk' : 0, 'eggs' : 0}
        self.harvest = {'wheat': 0, 'tomato': 0, 'apple': 0, 'strawberry': 0}  # урожай, который собран 

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
    '''Класс растений: пшеница, помидоры, яблоки, клубника'''
    def __init__(self, name, growth_stages, growth_time=60, x=0, y=0):
        super().__init__()
        self.name = name
        self.growth_stages = growth_stages
        self.current_stage = 0  # текущая фаза роста
        self.growth_time = growth_time  # время на каждую фазу роста (в секундах)
        self.last_growth_time = time.time()  # время последнего обновления фазы
        self.readytoharvest = False  # растение не достигло полной зрелости или да
        #self.inventory = inventory
        #self.pos = pos  # координаты растения на грядке
        self.drop = None  # здесь будет храниться изображение дропа
        self.wateredtimes = 0

        self.image = self.growth_stages[self.current_stage]
        self.rect = self.image.get_rect(topleft=(x, y))


    def get_image(self):
        '''Возвращаем изображение растения в зависимости от его текущей фазы.'''
        return self.growth_stages[self.current_stage] if self.current_stage < len(self.growth_stages) else self.growth_stages[-1]      

    def grow(self):
        '''обновление фазы роста'''
        if time.time() - self.last_growth_time > self.growth_time:
            self.current_stage += 1
            if self.current_stage >= len(self.growth_stages):
                self.readytoharvest = True  # Растение дало плоды ДРУГОЕ НАЗВАНИЕ МАРКЕРА
                #self.drop = pygame.image.load(f'assets/drops/{self.name.lower()}_drop.png')  # добавляем дроп
            else:
                self.image = self.growth_stages[self.current_stage]  # переход на следующую фазу роста
            self.last_growth_time = time.time()

##################################################################################################################

    def iswatered(self):
        '''полито + 1, если 3 полива -> урожай'''
        self.wateredtimes += 1
        print('полили растение')
        if self.wateredtimes == 3:
            print('------- растение полито 3 раза -------') # отладка
            self.readytoharvest = True
            print('----------собирайте урожай-------') # отладка 

    def harvestcheck(self):
        '''проверка на урожай, сбор, обнуление фазы роста'''
        if self.readytoharvest:
            self.current_stage = 0
            self.wateredtimes = 0
            self.readytoharvest = False
            print('''вы собрали урожай''') # отладка 
        else:
            print('''урожая ещё нет''') # отладка 

##################################################################################################################

    def update(self):
        '''обновление состояния растения'''
        self.grow()

    def draw(self):
        '''отрисовка растений'''
        self.screen.blit(self.image, self.rect.topleft)
        # если растение полностью созрело, отрисовываем дроп рядом с ним
        if self.readytoharvest and self.drop:
            drop_rect = self.drop.get_rect(topleft=(self.rect.x + 20, self.rect.y + 20))  # дроп рисуем рядом с растением
            self.screen.blit(self.drop, drop_rect.topleft)
