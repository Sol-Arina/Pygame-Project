import pygame
import random
import json

# группа для всех животных
animals_group = pygame.sprite.Group()

class Animal(pygame.sprite.Sprite):
    def __init__(self, x, y, spritesheet, anim_frames, radius=50, speed=1):
        super().__init__()
        self.spritesheet = spritesheet
        self.frames = anim_frames
        self.direction = 'down' # ...
        self.current_frame = 0
        self.image = self.spritesheet.parse_sprite(self.frames[self.direction][self.current_frame])
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.radius = radius
        self.speed = speed
        self.elapsed_time = 0
        self.frame_time = 200 # интервал между кадрами анимации
        self.movement_time = random.randint(1000, 3000)
        self.last_move_time = pygame.time.get_ticks()
    
    def animate(self, dt):
        """для обновления кадра анимации"""
        self.elapsed_time += dt
        if self.elapsed_time >= self.frame_time:
            self.elapsed_time = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames[self.direction])
            self.image = self.spritesheet.parse_sprite(self.frames[self.direction][self.current_frame])
    
    def move(self):
        """случайное движение в пределах радиуса"""
        now = pygame.time.get_ticks()
        if now - self.last_move_time >= self.movement_time:
            self.last_move_time = now
            angle = random.uniform(0, 2 * 3.14)
            offset = pygame.Vector2(self.radius, 0).rotate_rad(angle) # ...
            self.pos += offset

            # определяем направление
            dx, dy = offset.x, offset.y
            if abs(dx) > abs(dy):
                self.direction = 'right' if dx > 0 else 'left'
            else:
                self.direction = 'down' if dy > 0 else 'up'
        
        # обновление позиции
        self.rect.center = self.pos
    
    def update(self, dt):
        self.move()
        self.animate(dt)

 
def load_animal_frames(filename):
    """загружаем фреймы животных из JSON-файла"""
    with open(filename, 'r') as f:
        return json.load(f)