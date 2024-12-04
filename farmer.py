import pygame
import random
import json



class Farmer:
    FRAME_SIZE = (48, 48)
    DOWN = 0
    UP = 1
    LEFT = 2
    RIGHT = 3

    WALK_ANIMATION = [0, 1, 2, 3]  # Индексы кадров для анимации ходьбы

    def __init__(self, screen):
        self.screen = screen
        self.spritesheet = pygame.image.load("farmer.png").convert_alpha()
        self.pos_x, self.pos_y = 100, 100
        self.direction = self.DOWN
        self.animation_index = 0
        self.frame_counter = 0
        self.speed = 3
        self.screen_rect = pygame.Rect(self.pos_x, self.pos_y, self.FRAME_SIZE[0], self.FRAME_SIZE[1])
        self.interaction_text = ""
        self.font = pygame.font.Font(None, 36)
        self.menu = []
        self.next_frame()

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
        self.direction = direction
        if direction == self.DOWN:
            self.pos_y += self.speed
        elif direction == self.UP:
            self.pos_y -= self.speed
        elif direction == self.LEFT:
            self.pos_x -= self.speed
        elif direction == self.RIGHT:
            self.pos_x += self.speed
        self.screen_rect.topleft = (self.pos_x, self.pos_y)

    def draw(self):
        self.screen.blit(self.spritesheet, self.screen_rect, self.frame_rect)

    # Отрисовка текста, если есть взаимодействие
        if self.interaction_text:
            text_surface = self.font.render(self.interaction_text, True, (255, 255, 255))
            self.screen.blit(text_surface, (self.pos_x, self.pos_y - 20))  # Надпись над фермером

    def update(self):
        self.update_animation()

    def handle_input(self):
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

    def check_interaction(self, animals_group, plants_group=None):
       """Проверяет взаимодействие с животными или растениями."""       
       if plants_group:
           for plant in plants_group: 
               if self.screen_rect.colliderect(plant.rect):
                   return "plant", plant  # Возвращаем тип объекта и сам объект
       for animal in animals_group:
           if self.screen_rect.colliderect(animal.rect):
               return "animal", animal  # Возвращаем тип объекта и сам объект
       return None, None  # Если взаимодействия нет




class InteractionMenu:
    def __init__(self, screen, options):
        self.screen = screen
        self.options = options  # Список действий
        self.selected_index = 0  # Выбранный пункт меню
        self.font = pygame.font.Font(None, 36)
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
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.options[self.selected_index]  # Возвращаем выбранное действие
            elif event.key == pygame.K_ESCAPE:
                self.visible = False  # Закрываем меню

        return None