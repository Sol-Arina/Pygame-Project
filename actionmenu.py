import pygame
import pygame_menu
#import uuid

pygame.init()

# Цвета для текста и кнопок
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND_TEAL = (155, 212, 195)

SCREEN_WIDTH = 1120 # 16 умножить на 70 
SCREEN_HEIGHT = 720 # 16 умножить на 45 

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

class ActionMenu:
    '''класс для меню действий - магазина и инвентаря'''
    def __init__(self, screen, font_path, item_images, farmer):
        self.screen = screen
        self.font = font_path  # нащ шрифт
        self.farmer = farmer
        self.money_display = farmer.money
        #self.farmer.money = self.farmer.money  # деньги игрока
        self.message = ''
        self.menu_open = False  #  контроль состояния меню
        self.total_cost = 0
        #self.background = pygame.image.load(background)
        #self.theme = theme
        
        # товары магазина 
        self.shop_items = [
            {'name': 'Wheat Seeds', 'price': 5, 'quantity': 0},
            {'name': 'Tomato Seeds', 'price': 5, 'quantity': 0},
            {'name': 'Strawberry Seeds', 'price': 10, 'quantity': 0},
            {'name': 'Apple Seeds', 'price': 10, 'quantity': 0},
            {'name': 'Chicken', 'price': 15, 'quantity': 0},
            {'name': 'Cow', 'price': 25, 'quantity': 0},
        ]
        self.sell_items = [
            {'name': 'wheat', 'price': 6, 'quantity': 0},
            {'name': 'tomato', 'price': 6, 'quantity': 0},
            {'name': 'apple', 'price': 11, 'quantity': 0},
            {'name': 'strawberry', 'price': 11, 'quantity': 0},
            {'name': 'eggs', 'price': 3, 'quantity': 0},
            {'name': 'milk', 'price': 5, 'quantity': 0},
        ]
        self.inventory = farmer.inventory
        self.theme = pygame_menu.themes.THEME_SOLARIZED.copy()
        self.theme.title_font = pygame.font.Font(self.font, 30)
        self.theme.widget_font = pygame.font.Font(self.font, 20)

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

        # инициализация меню
        self.menu = self.create_menu() # это главное окно
         # подменю для магазина и инвентаря
        self.shop_menu = self.create_shop_menu()
        self.inventory_menu = self.create_inventory_menu(farmer)

        self.current_menu = self.menu # ПО ДЕФОЛТУ В ЭТОМ ОКНЕ ВСЁ   

    def create_menu(self):
        '''создает главное меню (объект pygame_menu.Menu)'''
        menu = pygame_menu.Menu('Action Menu', 900, 521, theme=self.theme)

        # кнопки для переключения вкладок
        menu.add.button('Shop', self.switch_to_shop).set_alignment(pygame_menu.locals.ALIGN_LEFT).set_margin(20, 60)
        menu.add.button('Inventory', self.switch_to_inventory).set_alignment(pygame_menu.locals.ALIGN_LEFT).set_margin(20, 60)
        
        # Отображение денег игрока ПЕРЕНЕСЕНО ВО ВКЛАДКУ МАГАЗИН
        #menu.add.label(f"Money: ${self.farmer.money}").set_alignment(pygame_menu.locals.ALIGN_LEFT).set_margin(20, 60)
        return menu
 
    def create_shop_menu(self):
        '''ЭТА ФУНКЦИЯ ОТОБРАЖАЕТ МАГАЗ'''
        shop_menu = pygame_menu.Menu('Shop', 500, 521, theme=self.theme)
        #  шоп меню 
        shop_menu.add.label('you can buy:')
        for item in self.shop_items:
            name, price, quantity = item['name'], item['price'], item['quantity']
            # отображаем товар и кнопки +/-
            shop_menu.add.label(f'{name}: {quantity} x ${price}').set_alignment(pygame_menu.locals.ALIGN_LEFT)#.set_margin(20, 20)
            shop_menu.add.button('+', lambda item=item: self.increase_quantity(item))#.set_alignment(pygame_menu.locals.ALIGN_LEFT)#.set_margin(20, 20)
            shop_menu.add.button('-', lambda item=item: self.decrease_quantity(item))#.set_alignment(pygame_menu.locals.ALIGN_LEFT)#.set_margin(20, 20)
        # you can sell
        shop_menu.add.label('you can sell:')    
        for item in self.sell_items:
            name, price, quantity = item['name'], item['price'], item['quantity']
            # отображаем товар и кнопки +/-
            shop_menu.add.label(f'{name}: {quantity} x ${price}').set_alignment(pygame_menu.locals.ALIGN_LEFT)#.set_margin(20, 20)
            shop_menu.add.button('+', lambda item=item: self.increase_quantity(item))#.set_alignment(pygame_menu.locals.ALIGN_LEFT)#.set_margin(20, 20)
            shop_menu.add.button('-', lambda item=item: self.decrease_quantity(item))#.set_alignment(pygame_menu.locals.ALIGN_LEFT)#.set_margin(20, 20)
  
        # отображаем общую сумму покупки
        shop_menu.add.label(f'Total: ${self.total_cost}').set_alignment(pygame_menu.locals.ALIGN_RIGHT)#.set_margin(20, 20)
        shop_menu.add.label(f'Money: ${self.farmer.money}').set_alignment(pygame_menu.locals.ALIGN_LEFT)#.set_margin(20, 60)
        # нопки купить и продать
        shop_menu.add.button('Buy', self.handle_buy).set_alignment(pygame_menu.locals.ALIGN_RIGHT)#.set_margin(20, 20)
        shop_menu.add.button('Sell', self.handle_sell).set_alignment(pygame_menu.locals.ALIGN_RIGHT)#.set_margin(20, 20)
        # Кнопка Назад
        shop_menu.add.button('Back', self.switch_to_main)
        return shop_menu

    def create_inventory_menu(self, farmer):
        '''ЭТА ФУНКЦИЯ ОТОБРАЖАЕТ ИНВЕНТАРЬ'''
        inventory_menu = pygame_menu.Menu('Inventory', 500, 521, theme=self.theme)
        self.inventory = farmer.inventory
        # семена
        #inventory_menu.add.label('Inventory Items')
        for item, quantity in self.inventory.items.items():
            inventory_menu.add.label(f'{item}: {quantity}').set_alignment(pygame_menu.locals.ALIGN_LEFT).set_margin(60, 20)
        # молоко и яйца    
        for product, quantity in self.inventory.products.items():
            inventory_menu.add.label(f'{product}: {quantity}').set_alignment(pygame_menu.locals.ALIGN_LEFT).set_margin(60, 20)
        # урожай: пшеница, помидоры, яблоки, клубника    
        for harvest, quantity in self.inventory.harvest.items():
            inventory_menu.add.label(f'{harvest}: {quantity}').set_alignment(pygame_menu.locals.ALIGN_LEFT).set_margin(60, 20)  
        # Кнопка НАЗАД
        inventory_menu.add.button('Back', self.switch_to_main)
        return inventory_menu

    def switch_to_main(self):
        '''back to actiom menu main tab'''
        if self.current_menu:  # отключаем текущее активное меню
            self.current_menu.disable()
            self.current_menu = self.menu  # переключаемся на главное меню
            self.current_menu.enable()

    def switch_to_shop(self):
        """Переключение на вкладку 'shop'"""  
        if self.current_menu:  # отключаем текущее меню
            self.current_menu.disable()
            self.current_menu = self.shop_menu  # на главное меню
            self.current_menu.enable()

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
        self.menu.add.label(f'Total: ${self.total_cost}').set_alignment(pygame_menu.locals.ALIGN_RIGHT).set_margin(20, 60)
        # Кнопки купить и продать
        self.menu.add.button('Buy', self.handle_buy).set_alignment(pygame_menu.locals.ALIGN_RIGHT).set_margin(20, 60)
        self.menu.add.button('Sell', self.handle_sell).set_alignment(pygame_menu.locals.ALIGN_RIGHT).set_margin(20, 60)

    def handle_buy(self):
        '''Обработка покупки'''
        for item in self.shop_items:  # это раздел you can buy
            if item['quantity'] > 0:
                total_price = item['price'] * item['quantity']
                if self.farmer.money >= total_price:
                    print(f"Покупка {item['quantity']} {item['name']} за {total_price}$. Денег осталось: {self.farmer.money - total_price}$")

                    if item['name'] == 'Cow':
                        for _ in range(item['quantity']):
                            self.farmer.buy_animal('Cow')
                    elif item['name'] == 'Chicken':
                        for _ in range(item['quantity']):
                            self.farmer.buy_animal('Chicken')
                    else:
                        self.farmer.inventory.add_item(item['name'], item['quantity'])

                    self.farmer.money -= total_price
                else:
                    print(f"Недостаточно денег для покупки {item['name']}. Необходимо {total_price}$, доступно {self.farmer.money}$")

                item['quantity'] = 0

        self.total_cost = 0
        self.update_shop_menu()

    def handle_sell(self):
        '''Обработка продажи'''
        for item in self.sell_items:  # это раздел you can sell
            # обработка для товаров из harvest
            inv_item_quantity = self.farmer.inventory.harvest.get(item['name'].lower(), 0)
            if inv_item_quantity >= item['quantity'] > 0:
                # выводим сообщение о продаже
                total_price = item['price'] * item['quantity']
                print(f"Продажа {item['quantity']} {item['name']} за {total_price}$. Денег стало: {self.farmer.money + total_price}$")
                # увеличиваем деньги игрока
                self.farmer.money += total_price
                # уменьшаем количество проданного товара в инвентаре
                self.farmer.inventory.harvest[item['name'].lower()] -= item['quantity']
            elif inv_item_quantity > 0:
                # нет достаточного количества товара для продажи из harvest
                print(f"Недостаточно товара {item['name']} для продажи из урожая. В наличии: {inv_item_quantity}, требуется: {item['quantity']}")

            # обработка для товаров из products
            inv_product_quantity = self.farmer.inventory.products.get(item['name'].lower(), 0)
            if inv_product_quantity >= item['quantity'] > 0:
                total_price = item['price'] * item['quantity']
                print(f"Продажа {item['quantity']} {item['name']} за {total_price}$. Денег стало: {self.farmer.money + total_price}$")
                self.farmer.money += total_price
                self.farmer.inventory.products[item['name'].lower()] -= item['quantity']
            elif inv_product_quantity > 0:
                # нет товара для продажи из продуктов
                print(f"Недостаточно товара {item['name']} для продажи из продуктов. В наличии: {inv_product_quantity}, требуется: {item['quantity']}")

            # обнуление товара после обработки
            item['quantity'] = 0

        self.total_cost = 0
        self.update_shop_menu()

    def switch_to_inventory(self):
        """Переключение на вкладку 'inventory'"""
        if self.current_menu: 
            self.current_menu.disable()

            # пересоздаем меню инвентаря каждый раз при его открытии чтобы цифры обновлялись!!
            self.inventory_menu = self.create_inventory_menu(self.farmer)

            self.current_menu = self.inventory_menu  # переключаемся на меню инвентаря
            self.current_menu.enable()

    def close_menu(self):
        '''закрыть меню'''
        self.menu.disable()  # jтключаем существующее меню
        self.menu_open = False  # обновляем маркер

    def increase_quantity(self, item):
        '''Увеличение количества товара'''
        item['quantity'] += 1
        self.total_cost += item['price']
        self.update_shop_menu()

    def decrease_quantity(self, item):
        '''Уменьшение количества товара'''
        if item['quantity'] > 0:
            item['quantity'] -= 1
            self.total_cost -= item['price']
            self.update_shop_menu()

    def update_shop_menu(self):
        '''Обновление вкладки магазина при изменении данных'''
        self.shop_menu.clear()
        self.shop_menu.add.label('you can buy:')

        for item in self.shop_items:
            name, price, quantity = item['name'], item['price'], item['quantity']
            self.shop_menu.add.label(f'{name}: {quantity} x ${price}').set_alignment(pygame_menu.locals.ALIGN_LEFT)
            self.shop_menu.add.button('+', lambda item=item: self.increase_quantity(item))
            self.shop_menu.add.button('-', lambda item=item: self.decrease_quantity(item))

        self.shop_menu.add.label('you can sell:')
        for item in self.sell_items:
            name, price = item['name'], item['price']
            # Получение количества из инвентаря
            quantity = self.farmer.inventory.harvest.get(name.lower(), 0) + self.farmer.inventory.products.get(name.lower(), 0)
            item['quantity'] = quantity  # Обновляем количество для продажи
            self.shop_menu.add.label(f'{name}: {item["quantity"]} x ${price}').set_alignment(pygame_menu.locals.ALIGN_LEFT)
            self.shop_menu.add.button('+', lambda item=item: self.increase_quantity(item))
            self.shop_menu.add.button('-', lambda item=item: self.decrease_quantity(item))

        self.shop_menu.add.label(f'Total: ${self.total_cost}').set_alignment(pygame_menu.locals.ALIGN_RIGHT)
        self.shop_menu.add.label(f'Money: ${self.farmer.money}').set_alignment(pygame_menu.locals.ALIGN_LEFT)
        self.shop_menu.add.button('Buy', self.handle_buy).set_alignment(pygame_menu.locals.ALIGN_RIGHT)
        self.shop_menu.add.button('Sell', self.handle_sell).set_alignment(pygame_menu.locals.ALIGN_RIGHT)
        self.shop_menu.add.button('Back', self.switch_to_main)

    def update_money_display(self):
        """После запуска сохраненной игры отображается оставшееся кол-во денег"""
        self.money_display = self.farmer.money