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
        self.animal_type = animal_type # для выбора звука: cow/chicken
        self.spritesheet = spritesheet
        self.frames_data = frames_data
        self.frame_names = frame_names
        self.frame_size = frame_size
        self.radius = radius
        self.speed = speed
        self.tilemap = tilemap

        self.pos = pygame.Vector2(x, y) # позиция животного
        self.current_frame = 0 # для анимации
        self.elapsed_time = 0
        self.frame_time = 700
        self.image = self.load_frame(self.frame_names[self.current_frame])
        self.rect = self.image.get_rect(center=(x, y))

        self.movement_time = random.randint(1000, 3000)
        self.last_move_time = pygame.time.get_ticks()

        self.hunger = 0
        self.energy = 100
        self.hunger_rate = 0.5 # скорость увеличения голода (в секунду?)
        self.energy_rate = 0.5 # скорость уменьшения энергии (в секунду?)
        self.last_status_update = pygame.time.get_ticks() # для обновления уровня голода и энергии

    def load_frame(self, frame_name):
        """загрузка кадра по имени"""
        frame = self.frames_data[frame_name]['frame']
        x, y, w, h = frame['x'], frame['y'], frame['w'], frame['h']
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
    
    def update_status(self):
        """для обновления уровня голода и энергии"""
        now = pygame.time.get_ticks()
        elapsed_time = (now - self.last_status_update) / 1000 # время последнего обновления в секундах
        self.last_status_update = now

        self.hunger = min(self.hunger + self.hunger_rate * elapsed_time, 100)
        self.energy = max(self.energy - self.energy_rate * elapsed_time, 0)

        # if self.hunger >= 65 or self.energy <= 30:
        #     self.play.sound()

    
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
    
    def feed(self):
        pass
    
    def update(self, dt):
        self.update_status()
        self.move()
        self.animate(dt)


class Cow(Animal):
    def __init__(self, x, y, spritesheet, frames_data, frame_names, frame_size, tilemap=None, radius=5, speed=1):
        super().__init__(x, y, 'cow', spritesheet, frames_data, frame_names, frame_size, tilemap, radius, speed)

        self.voice = AnimalSound("cow", {
            'moo': 'moo.wav',
            'hungry': 'hungry_cow.wav',
            'fed': 'cow_bells.wav',
            'milk': 'cow_milk.wav'
        })

        # Параметры для молока
        self.feed_count = 0  # Количество кормлений
        self.milk_ready = False  # Доступность молока
        self.last_moo_time = pygame.time.get_ticks()  # Для контроля периодичности мычания

    def update_status(self):
        """Обновление уровня голода, энергии и звуков."""
        super().update_status()

        now = pygame.time.get_ticks()

        # Мычание с периодичностью
        if now - self.last_moo_time > 15000:  # 15 секунд
            self.voice.play('moo')
            self.last_moo_time = now

        # Проверка на голод или усталость
        if self.hunger >= 65 or self.energy <= 30:
            if not self.voice.sounds['hungry'].get_num_channels():  # Звук голода не должен перекрываться
                self.voice.play('hungry')

        # Проверяем, готово ли молоко
        self.milk_ready = self.feed_count >= 3 and self.energy >= 70

    def feed(self):
        """Кормление коровы."""
        super().feed()
        self.feed_count += 1
        self.voice.play('fed')

        # # Проверка на готовность молока
        # if self.milk_ready:
        #     print("Молоко готово! Вы можете собрать молоко.")

    def milk(self):
        """Собираем молоко, если доступно."""
        if self.milk_ready:
            self.voice.play('milk')
            self.feed_count = 0  # Сбрасываем счетчик кормлений
            self.milk_ready = False
        #     print("Вы взяли молоко!")
        # else:
        #     print("Молоко еще не готово.")

    def update_volume(self):
        """Обновляет громкость звуков животного на основе глобальной громкости."""
        self.voice.update_volume()


class Chicken(Animal):
    def __init__(self, x, y, spritesheet, frames_data, frame_names, frame_size, tilemap=None, radius=5, speed=1):
        super().__init__(x, y, 'chicken', spritesheet, frames_data, frame_names, frame_size, tilemap, radius, speed)
        # Звуки курицы
        self.voice = AnimalSound('chicken', {
            'squeak': 'chickens.wav',
            'hungry': 'hungry_chickens.wav',
        })

        self.feed_count = 0
        self.egg_ready = False
        self.last_squeak_time = pygame.time.get_ticks() 

    def update_status(self):
        """Обновление уровня голода, энергии и звуков."""
        super().update_status()

        now = pygame.time.get_ticks()

        # писк цыпленка с периодичностью
        if now - self.last_squeak_time > 20000:  # 20 секунд
            self.voice.play('squeak')
            self.last_squeak_time = now

        # Проверка на голод или усталость
        if self.hunger >= 65 or self.energy <= 30:
            if not self.voice.sounds['hungry'].get_num_channels():  # Звук голода не должен перекрываться
                self.voice.play('hungry')

        self.egg_ready = self.feed_count >= 3 and self.energy >= 70

    def feed(self):
        super().feed()
        self.feed_count += 1

        # # Проверка на готовность молока
        # if self.egg_ready:
        #     print("Молоко готово! Вы можете собрать молоко.")

    def egg(self):
        if self.egg_ready:
            self.feed_count = 0  # Сбрасываем счетчик кормлений
            self.egg_ready = False
        #     print("Вы взяли молоко!")
        # else:
        #     print("Молоко еще не готово.")

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