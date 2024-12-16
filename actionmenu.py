import pygame
import pygame_menu
import uuid

pygame.init()

# Цвета для текста и кнопок
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND_TEAL = (155, 212, 195)

SCREEN_WIDTH = 1120 # 16 умножить на 70 
SCREEN_HEIGHT = 720 # 16 умножить на 45 

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

class ActionMenu:
    def __init__(self, screen, font_path, item_images, money=1000):
        self.screen = screen
        self.font = font_path  # нащ шрифт
        self.money = money  # деньги игрока
        #self.current_tab = 'shop'
        #self.current_tab = 'main'  # указатель на текущее меню
        
        self.message = ''
        self.menu_open = False  #  контроль состояния меню
        self.total_cost = 0
        #self.background = pygame.image.load(background)
        #self.theme = theme
        
        # ьовары магазина 
        self.shop_items = [
            {'name': 'Wheat Seeds', 'price': 5, 'quantity': 0},
            {'name': 'Tomato Seeds', 'price': 5, 'quantity': 0},
            {'name': 'Strawberry Bush', 'price': 10, 'quantity': 0},
            {'name': 'Apple Tree', 'price': 10, 'quantity': 0},
            {'name': 'Chicken', 'price': 15, 'quantity': 0},
            {'name': 'Cow', 'price': 25, 'quantity': 0},
        ]
        self.sell_items = [
            {'name': 'Wheat', 'price': 6, 'quantity': 0},
            {'name': 'Tomato', 'price': 8, 'quantity': 0},
            {'name': 'Apple', 'price': 15, 'quantity': 0},
            {'name': 'Strawberries', 'price': 20, 'quantity': 0},
            {'name': 'Egg', 'price': 5, 'quantity': 0},
            {'name': 'Milk', 'price': 10, 'quantity': 0},
        ]
        
        self.inventory = {
            'Wheat Seeds': 0,
            'Tomato Seeds': 0,
            'Strawberry Bush': 0,
            'Apple Tree': 0,
            'Chicken': 0,
            'Cow': 0,
            'Egg': 0,
            'Milk': 0,
            'Wheat': 0,
            'Tomato': 0,
            'Apple': 0,
            'Strawberries': 0,
        }

        #self.background = pygame_menu.baseimage.load('assets/action_menu/background.png')

        self.theme = pygame_menu.themes.THEME_SOLARIZED.copy()
        self.theme.title_font = pygame.font.Font(self.font, 30)
        self.theme.widget_font = pygame.font.Font(self.font, 20)
        #self.theme.background_color = self.set_background

        # Создаем словарь для изображений товаров
        self.item_images = {
            'Wheat Seeds': pygame.image.load(item_images['wheat']),
            'Tomato Seeds': pygame.image.load(item_images['tomato']),
            'Strawberry Bush': pygame.image.load(item_images['strawberrybush']),
            'Apple Tree': pygame.image.load(item_images['appletree']),
            'Chicken': pygame.image.load(item_images['chicken']),
            'Cow': pygame.image.load(item_images['cow']),
            'Coin': pygame.image.load(item_images['coin'])
        }

        # Инициализация меню
        self.menu = self.create_menu() # это главное окно
         # Добавляем подменю для магазина и инвентаря
        self.shop_menu = self.create_shop_menu()
        self.inventory_menu = self.create_inventory_menu()

        self.current_menu = self.menu # ПО ДЕФОЛТУ В ЭТОМ ОКНЕ ВСЁ

    #def set_background(self, surface):
    #    surface.blit(self.background, (0, 0))    

    def create_menu(self):
        """Создает и возвращает объект меню pygame_menu.Menu"""
        #my_theme = pygame_menu.themes.THEME_DARK.copy()  # Копируем существующую тему
        #my_theme.background_color = surface.blit(self.background, (0, 0))
        menu = pygame_menu.Menu('Action Menu', 1000, 521, theme=self.theme)

        # добавляем кнопки для переключения вкладок
        menu.add.button('Shop', self.switch_to_shop).set_alignment(pygame_menu.locals.ALIGN_LEFT).set_margin(20, 60)
        menu.add.button('Inventory', self.switch_to_inventory).set_alignment(pygame_menu.locals.ALIGN_LEFT).set_margin(20, 60)
        
        # жобавляем кнопку закрытия меню, используя функцию close_menu
        #menu.add.button('Close Menu', self.close_menu)

        # Отображение денег игрока
        menu.add.label(f"Money: ${self.money}").set_alignment(pygame_menu.locals.ALIGN_LEFT).set_margin(20, 60)

        return menu
 
    def create_shop_menu(self):
        '''ЭТА ФУНКЦИЯ ОТОБРАЖАЕТ МАГАЗ'''
        shop_menu = pygame_menu.Menu('Shop', 500, 521, theme=self.theme)
        # Конфигурируем шоп меню
        shop_menu.add.label('Shop Items')
        for item in self.shop_items:
            name, price, quantity = item['name'], item['price'], item['quantity']
            # Отображаем товар и кнопки +/-
            shop_menu.add.label(f'{name}: {quantity} x ${price}')#.set_alignment(pygame_menu.locals.ALIGN_RIGHT).set_margin(20, 60)
            shop_menu.add.button('+', lambda item=item: self.increase_quantity(item))#.set_alignment(pygame_menu.locals.ALIGN_RIGHT).set_margin(20, 60)
            shop_menu.add.button('-', lambda item=item: self.decrease_quantity(item))#.set_alignment(pygame_menu.locals.ALIGN_RIGHT).set_margin(20, 60)
        # Отображаем общую сумму покупки
        shop_menu.add.label(f'Total Cost: ${self.total_cost}')#.set_alignment(pygame_menu.locals.ALIGN_RIGHT).set_margin(20, 60)
        # Кнопки купить и продать
        shop_menu.add.button('Buy', self.handle_buy) #.set_alignment(pygame_menu.locals.ALIGN_RIGHT).set_margin(20, 60)
        shop_menu.add.button('Sell', self.handle_sell) #.set_alignment(pygame_menu.locals.ALIGN_RIGHT).set_margin(20, 60)
        # Кнопка Назад
        shop_menu.add.button('Back', self.switch_to_main)
        #for item in self.shop_items:
        #    shop_menu.add.button(f"Buy {item['name']}", lambda i=item: self.handle_buy(i))
        # Кнопка Назад
        #shop_menu.add.button('Back', self.switch_to_main)
        return shop_menu

    def create_inventory_menu(self):
        '''ЭТА ФУНКЦИЯ ОТОБРАЖАЕТ ИНВЕНТАРЬ'''
        inventory_menu = pygame_menu.Menu('Inventory', 500, 521, theme=self.theme)
        #  меню инвентаря
        inventory_menu.add.label('Inventory Items')
        for item, quantity in self.inventory.items():
            inventory_menu.add.label(f'{item}: {quantity}')
        # Кнопка НАЗАД
        inventory_menu.add.button('Back', self.switch_to_main)
        return inventory_menu

    def switch_to_main(self):
        '''back to actiom menu main tab'''
        if self.current_menu:  # Отключаем текущее активное меню
            self.current_menu.disable()
            self.current_menu = self.menu  # Переключаемся на главное меню
            self.current_menu.enable()
        #self.current_menu = self.menu
        #self.current_menu.enable()
        #self.current_tab = 'main'
        #self.menu.enable() 
        #self.shop_menu.disable()
        #self.inventory_menu.disable()  


    def switch_to_shop(self):
        """Переключение на вкладку 'shop'"""  
        if self.current_menu:  # Отключаем текущее активное меню
            self.current_menu.disable()
            self.current_menu = self.shop_menu  # Переключаемся на главное меню
            self.current_menu.enable()
        
        #self.current_menu = self.shop_menu

        #self.current_tab = 'shop'
        #self.main_menu.disable()
        #self.shop_menu.enable()
        #self.inventory_menu.disable()

    def draw_shop_tab(self):
        """эта функция ничего не делает и не используется, но я кое-что отсюда копирую в create_shop_tab"""
        self.menu.clear()
        self.menu.add.label('Shop')
        for item in self.shop_items:
            name, price, quantity = item['name'], item['price'], item['quantity']
            # Отображаем товар и кнопки +/-
            self.menu.add.label(f'{name}: {quantity} x ${price}').set_alignment(pygame_menu.locals.ALIGN_RIGHT).set_margin(20, 60)
            self.menu.add.button('+', lambda item=item: self.increase_quantity(item)).set_alignment(pygame_menu.locals.ALIGN_RIGHT).set_margin(20, 60)
            self.menu.add.button('-', lambda item=item: self.decrease_quantity(item)).set_alignment(pygame_menu.locals.ALIGN_RIGHT).set_margin(20, 60)
        # Отображаем общую сумму покупки
        self.menu.add.label(f'Total Cost: ${self.total_cost}').set_alignment(pygame_menu.locals.ALIGN_RIGHT).set_margin(20, 60)
        # Кнопки купить и продать
        self.menu.add.button('Buy', self.handle_buy).set_alignment(pygame_menu.locals.ALIGN_RIGHT).set_margin(20, 60)
        self.menu.add.button('Sell', self.handle_sell).set_alignment(pygame_menu.locals.ALIGN_RIGHT).set_margin(20, 60)

    def handle_buy(self):
        """Обработка покупки"""
        for item in self.shop_items:
            if item['quantity'] > 0:
                self.inventory[item['name']] += item['quantity']
                self.money -= item['price'] * item['quantity']
                item['quantity'] = 0
        self.total_cost = 0
        #self.draw_shop_tab()

    def handle_sell(self):
        """Обработка продажи"""
        for item in self.shop_items:
            inv_item = self.inventory.get(item['name'])
            if inv_item and inv_item >= item['quantity']:
                self.money += item['price'] * item['quantity']
                self.inventory[item['name']] -= item['quantity']
                item['quantity'] = 0
        self.total_cost = 0
        #self.draw_shop_tab()      

    def switch_to_inventory(self):
        """Переключение на вкладку 'inventory'."""
        if self.current_menu:  # Отключаем текущее активное меню
            self.current_menu.disable()
            self.current_menu = self.inventory_menu  # Переключаемся на главное меню
            self.current_menu.enable()

        #self.current_menu = self.inventory_menu

        #self.current_tab = 'inventory'
        #self.menu.disable()
        #self.shop_menu.disable()
        #self.inventory_menu.enable()

        #self.menu.clear()
        #self.draw_inventory_tab()
        #self.menu.enable()

    def draw_inventory_tab(self):
        """Отрисовка вкладки инвентаря."""
        self.menu.clear()
        self.menu.add.label("Inventory").set_alignment(pygame_menu.locals.ALIGN_RIGHT).set_margin(20, 60)
        for item, quantity in self.inventory.items():
            self.menu.add.label(f'{item}: {quantity}').set_alignment(pygame_menu.locals.ALIGN_RIGHT).set_margin(20, 60)  

    def close_menu(self):
        '''закрыть меню'''
        self.menu.disable()  # Отключаем существующее меню
        self.menu_open = False  # Обновляем флаг

    def increase_quantity(self, item):
        """Увеличение количества товара."""
        item['quantity'] += 1
        self.total_cost += item['price']
        #self.update_shop_menu()

    def decrease_quantity(self, item):
        """Уменьшение количества товара."""
        if item['quantity'] > 0:
            item['quantity'] -= 1
            self.total_cost -= item['price']
            #self.update_shop_menu()

    #def update_shop_menu(self):
    #    """Перерисовка пунктов меню и обновление отображаемых значений."""
    #    if self.shop_menu.is_enabled():
    #        for item in self.shop_items:
    #            label = self.shop_menu.get_widget(item['name'])
    #            label.set_title(f'{item["name"]}: {item["quantity"]} x ${item["price"]}')
    #        total_label = self.shop_menu.get_widget("total_cost")
    #        total_label.set_title(f'Total Cost: ${self.total_cost}')
    #        money_label = self.menu.get_widgets()[2]  # Индекс может быть перестроен
    #        money_label.set_title(f"Money: ${self.money}")
    #        #self.shop_menu.update(events)        

    #def increase_quantity(self, item):
    #    """Увеличение количества товара."""
    #    item['quantity'] += 1
    #    self.total_cost += item['price']
    #    self.draw_shop_tab()

    #def decrease_quantity(self, item):
    #    """Уменьшение количества товара."""
    #    if item['quantity'] > 0:
    #        item['quantity'] -= 1
    #        self.total_cost -= item['price']
    #    self.draw_shop_tab()'''

    '''def main_loop(self):
        """Основной цикл меню с отрисовкой фона."""
        events = pygame.event.get()
        self.menu.update(events)  # Обновляем меню
        self.menu.draw(self.screen)  # Отрисовываем меню с фоном
        pygame.display.update()'''

    '''def draw_background(self, surface: pygame.Surface):
        """Отрисовка фонового изображения."""
        screen.fill(BACKGROUND_TEAL)
        surface.blit(self.background, (0, 0))
        pygame.display.update()'''    



