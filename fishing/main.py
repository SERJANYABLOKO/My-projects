import pygame
import random

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
FONT_SIZE = 24
FONT_COLOR = BLACK
FISH_HEIGHT = 30  # Высота рыбы
MAX_FISH = 5 #Максимальное количество рыб на экране

# Настройка экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Рыбалка")
font = pygame.font.Font(None, FONT_SIZE)

# Данные о рыбах
fishs = {
    "Окунь": {"вес": (0.2, 1.5), "цена": 10, "шанс": 0.4, "описание": "Полосатый разбойник наших вод.", "цвет": GREEN},
    "Щука": {"вес": (1.0, 5.0), "цена": 30, "шанс": 0.2, "описание": "Водная торпеда, хищник.", "цвет": BLUE},
    "Лещ": {"вес": (0.5, 2.5), "цена": 15, "шанс": 0.3, "описание": "Мирная рыба, любит тихие заводи.", "цвет": (150, 75, 0)},  # Коричневый
    "Плотва": {"вес": (0.1, 0.5), "цена": 5, "шанс": 0.1, "описание": "Мелкая серебристая рыбка.", "цвет": (192, 192, 192)},  # Серый
    "Сом": {"вес": (3.0, 10.0), "цена": 50, "шанс": 0.05, "описание": "Крупный донный хищник.", "цвет": (101, 67, 33)}, # Добавили Сома
    "Карп": {"вес": (2.0, 7.0), "цена": 40, "шанс": 0.15, "описание": "Всеядная рыба, часто разводится в прудах.", "цвет": (205, 133, 63)} # Добавили Карпа
}

def draw_text(text, x, y, color=FONT_COLOR):
    """Отображает текст на экране."""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)

def draw_fishing_scene():
    """Рисует базовую сцену рыбалки (вода, берег)."""
    pygame.draw.rect(screen, BLUE, (0, HEIGHT // 2, WIDTH, HEIGHT // 2))  # Вода
    pygame.draw.rect(screen, GREEN, (0, HEIGHT // 2 - 50, WIDTH, 50))  # Берег

def catch_fish():
    """Определяет, какая рыба поймана."""
    available_fish = list(fishs.keys())
    weights = [fishs[fish]["шанс"] for fish in available_fish]
    catch = random.choices(available_fish, weights=weights, k=1)[0]
    return catch

def generate_fish_data():
    """Генерирует данные для одной рыбы (тип, вес, позиция)."""
    catch = catch_fish()
    min_weight, max_weight = fishs[catch]["вес"]
    weight = round(random.uniform(min_weight, max_weight), 2)
    color = fishs[catch]["цвет"]
    fish_width = int(weight * 20)
    fish_x = random.randint(0, WIDTH - fish_width)
    fish_y = random.randint(HEIGHT // 2, HEIGHT - FISH_HEIGHT)
    return catch, weight, color, fish_x, fish_y, fish_width


def main():
    """Основной игровой цикл."""
    running = True
    fish_list = [] # Список рыб на экране (каждая рыба - кортеж (тип, вес, цвет, x, y, ширина))
    description = ""
    price = 0
    show_prompt = False

    total_fish_caught = 0  # Счетчик пойманных рыб
    total_price = 0       # Общая стоимость пойманной рыбы

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y and show_prompt:
                    #Сбрасываем игру, не трогаем счетчики
                    fish_list = [] # Очищаем список рыб, чтобы начать заново
                    show_prompt = False
                elif event.key == pygame.K_n and show_prompt:
                    running = False
                elif not show_prompt: # Ловим рыбу, если не показывается подсказка
                    if len(fish_list) < MAX_FISH:
                        fish_type, fish_weight, fish_color, fish_x, fish_y, fish_width = generate_fish_data()
                        fish_list.append((fish_type, fish_weight, fish_color, fish_x, fish_y, fish_width)) # Добавляем новую рыбу

                        # Обновляем счетчики
                        total_fish_caught += 1
                        total_price += fishs[fish_type]["цена"]


        # Отрисовка сцены
        screen.fill(WHITE)
        draw_fishing_scene()

        # Рисуем всех рыб
        for fish_type, fish_weight, fish_color, fish_x, fish_y, fish_width in fish_list:
            pygame.draw.rect(screen, fish_color, (fish_x, fish_y, fish_width, FISH_HEIGHT))

        #Если есть рыбы, показываем инфо о первой
        if fish_list:
            first_fish_type, first_fish_weight, first_fish_color, _, _, _ = fish_list[0]
            description = fishs[first_fish_type]["описание"]
            price = fishs[first_fish_type]["цена"]

            draw_text(f"Поймано рыб на экране: {len(fish_list)}", 50, 50)
            draw_text(f"Первая рыба: {first_fish_type}, Вес: {first_fish_weight} кг, Цена: {price} у.е.", 50, 80)
            draw_text(f"Описание: {description}", 50, 110)

            show_prompt = True
            draw_text("Попробовать еще раз? (y/n)", 50, HEIGHT - 50)
        else:
             draw_text("Нажмите любую клавишу, чтобы начать рыбалку!", 50, 50)


        # Выводим общую статистику
        draw_text(f"Всего поймано рыб: {total_fish_caught}", 50, 140)
        draw_text(f"Общая стоимость улова: {total_price} у.е.", 50, 170)

        pygame.display.flip()

    pygame.quit()

# Запуск игры
main()