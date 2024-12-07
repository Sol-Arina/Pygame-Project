import pygame
import csv
import os


class TileMap:
    '''класс для карты тайлов'''
    def __init__(self, tile_size, map_file, overlay_map_file=None):
        self.tile_size = tile_size  # 16 на 16 пикселей
        self.tile_images = {}  # cловарь для хранения тайлов основного слоя
        self.overlay_tile_images = {}  # cловарь для хранения тайлов второго слоя
        
        # загружаем основную карту
        self.map_data = self.load_map(map_file)
        
        self.farmable_tiles = {504} # ЗДЕСЬ МОЖНО САЖАТЬ
        self.water = {9}  # вода= нельзя идти

         # непроходимые тайлы - заборы, постройки, деревья
        self.secondlayer_collision = {1, 2, 3, 17, 18, 19, 33, 34, 35, 4, 5, 6, 7, 20, 21, 22, 23, 36, 37, 38, 39, 52, 53, 54 , 55, 69, 70, 71, 85, 87, 101, 102, 103, 104, 156, 124, 136, 152, 231, 232, 208, 224, 209, 210, 225, 226} 

        # если указан файл для второго слоя, загружаем его
        if overlay_map_file:
            self.overlay_map_data = self.load_map(overlay_map_file)
        else:
            self.overlay_map_data = None  # если нет второго слоя, оставляем None ПОТОМ МОЖНО СЮДА ДОБАВИТЬ ЕЩЁ СЛОЁВ

    def isitwater(self, x, y):
        '''checking if a tile is water первый слой'''
        return self.map_data[y][x] in self.water        

    def canifarmhere(self, x, y):
        '''проверка, грядка или нет'''
        return self.map_data[y][x] in self.farmable_tiles

    def isitcollidable(self, x, y):
        '''проверяет тайлы второго слоя на проходимость'''
        return self.overlay_map_data[y][x] in self.secondlayer_collision


    def load_tile_set(self, filename, tile_width, tile_height):
        '''функция для загрузки изображения с несколькими тайлами'''
        image = pygame.image.load(filename)
        image_width, image_height = image.get_size()
        tile_set = []
        
        # разделение изображения на тайлы по сетке
        for y in range(0, image_height, tile_height):
            for x in range(0, image_width, tile_width):
                tile = image.subsurface((x, y, tile_width, tile_height))
                tile_set.append(tile)  
        return tile_set

    def add_tiles_from_image(self, filename, starting_index=1):
        '''добавление тайлов в словарь первого ground слоя'''       
        tile_set = self.load_tile_set(filename, self.tile_size, self.tile_size)
        for i, tile in enumerate(tile_set):
            self.tile_images[starting_index + i] = tile

    def add_overlay_tiles_from_image(self, filename, starting_index=1):
        '''добавление тайлов в словарь второго слоя'''
        tile_set = self.load_tile_set(filename, self.tile_size, self.tile_size)
        for i, tile in enumerate(tile_set):
            self.overlay_tile_images[starting_index + i] = tile

    def load_map(self, filename):
        '''функция для загрузки карты из CSV файла'''
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            map_data = []
            for row in reader:
                map_data.append([int(tile) for tile in row])
        return map_data

    def draw_map(self, screen):
        '''функция для отрисовки карты на экране'''
        # основной ground слой
        for y, row in enumerate(self.map_data):
            for x, tile in enumerate(row):
                if tile in self.tile_images:
                    screen.blit(self.tile_images[tile], (x * self.tile_size, y * self.tile_size))

        # если есть второй слой, рисуем его на карте
        if self.overlay_map_data:
            for y, row in enumerate(self.overlay_map_data):
                for x, tile in enumerate(row):
                    if tile in self.overlay_tile_images:
                        screen.blit(self.overlay_tile_images[tile], (x * self.tile_size, y * self.tile_size))
