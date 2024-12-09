import pygame
import random
import json
from sound import AnimalSound, BaseSound
from spritesheet import Spritesheet
from tiles import TileMap

# группа для всех животных
animals_group = pygame.sprite.Group()

class Animal(pygame.sprite.Sprite):
    def __init__(self, x, y, animal_type, spritesheet, frames_data, frame_names, frame_size, tilemap, radius=5, speed=1):
        """
        - x, y: начальные координаты
        - animal_type: тип животного
        - spritesheet: объект Spritesheet для загрузки спрайтов
        - frames_data: данные JSON о фреймах
        - frame_names: список имен кадров (["cow_static.png", ...])
        - frame_size: размер кадра (ширина, высота)
        - tilemap: объект TileMap для проверки движения
        - radius: радиус движения
        - speed: скорость движения
        """
        super().__init__()
        self.animal_type = animal_type
        self.spritesheet = spritesheet
        self.frames_data = frames_data
        self.frame_names = frame_names
        self.frame_size = frame_size
        self.radius = radius
        self.speed = speed
        self.tilemap = tilemap

        self.pos = pygame.Vector2(x, y)
        self.current_frame = 0
        self.elapsed_time = 0
        self.frame_time = 700
        self.image = self.load_frame(self.frame_names[self.current_frame])
        self.rect = self.image.get_rect(center=(x, y))

        self.movement_time = random.randint(1000, 3000)
        self.last_move_time = pygame.time.get_ticks()

        self.animal_type = animal_type  #для выбора звука: cow/chicken
        self.voice = AnimalSound(self.animal_type)

    def load_frame(self, frame_name):
        """загрузка кадра по имени"""
        frame = self.frames_data[frame_name]['frame']
        x, y, w, h = frame["x"], frame["y"], frame["w"], frame["h"]
        sprite = self.spritesheet.get_sprite(x, y, w, h)
        return pygame.transform.scale(sprite, self.frame_size)

    def is_tile_walkable(self, x, y):
        """Проверяет, можно ли двигаться на указанный тайл."""
        # Проверяем границы карты
        if x < 0 or y < 0 or y >= len(self.tilemap.map_data) or x >= len(self.tilemap.map_data[0]):
            return False

        # Проверяем проходимость тайла
        if self.tilemap.isitwater(x, y) or self.tilemap.isitcollidable(x, y):
            return False
        
        return True
    
    def animate(self, dt):
        """для обновления кадра анимации"""
        self.elapsed_time += dt
        if self.elapsed_time >= self.frame_time:
            self.elapsed_time = 0
            self.current_frame = (self.current_frame + 1) % len(self.frame_names)
            self.image = self.load_frame(self.frame_names[self.current_frame])
    
    def move(self):
        """Случайное движение в пределах радиуса от исходной позиции."""
        now = pygame.time.get_ticks()
        if now - self.last_move_time >= self.movement_time:
            self.last_move_time = now
            angle = random.uniform(0, 2 * 3.14)
            offset = pygame.Vector2(self.radius, 0).rotate_rad(angle)
            new_pos = self.pos + offset

            # Определяем тайловые координаты
            tile_x = int(new_pos.x // self.tilemap.tile_size)
            tile_y = int(new_pos.y // self.tilemap.tile_size)

            if self.is_tile_walkable(tile_x, tile_y):
                self.pos = new_pos              

            # # Проверка на выход за границы экрана или слишком далекое движение
            # screen_width, screen_height = 800, 600  # Размер экрана
            # if 0 <= new_pos.x <= screen_width and 0 <= new_pos.y <= screen_height:
            #     self.pos = new_pos

        # Обновление позиции прямоугольника
        self.rect.center = self.pos
    
    def update(self, dt):
        self.move()
        self.animate(dt)

    def update_volume(self):
        """Обновляет громкость звуков животного на основе глобальной громкости."""
        self.voice.update_volume()

 
def load_animal_frames(filename):
    """
    Загрузка данных фреймов животных из JSON-файла.
    - filename: путь к JSON-файлу с данными о фреймах
    Возвращает: словарь с данными фреймов
    """
    with open(filename, 'r') as f:
        data = json.load(f)
    return data['frames']