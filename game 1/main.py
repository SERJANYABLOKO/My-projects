import pygame
import sys
import math
import os
from collections import deque

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 1000, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)
GREEN = (100, 255, 150)
RED = (255, 100, 100)
PURPLE = (200, 100, 255)
YELLOW = (255, 255, 100)
ORANGE = (255, 150, 50)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Загружаем изображение игрока
        try:
            self.original_image = pygame.image.load("img.png").convert_alpha()
            # Масштабируем до нужного размера
            self.original_image = pygame.transform.scale(self.original_image, (40, 60))
        except:
            # Если файл не найден, создаем временное изображение
            print("Файл img.png не найден! Создаю временное изображение...")
            self.original_image = pygame.Surface((40, 60), pygame.SRCALPHA)
            # Рисуем простого человечка
            pygame.draw.rect(self.original_image, BLUE, (10, 0, 20, 30))  # Тело
            pygame.draw.circle(self.original_image, (255, 200, 150), (20, 35), 12)  # Голова
            pygame.draw.rect(self.original_image, BLUE, (5, 30, 10, 25))  # Левая нога
            pygame.draw.rect(self.original_image, BLUE, (25, 30, 10, 25))  # Правая нога
            pygame.draw.rect(self.original_image, BLUE, (0, 10, 10, 15))  # Левая рука
            pygame.draw.rect(self.original_image, BLUE, (30, 10, 10, 15))  # Правая рука

        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.jump_power = -14
        self.gravity = 0.7
        self.on_ground = False
        self.facing_right = True
        self.lives = 3

        # Для записи истории движений
        self.history = deque(maxlen=180)  # 3 секунды при 60 FPS
        self.is_recording = True

    def record_state(self):
        """Записываем текущее состояние игрока"""
        if self.is_recording:
            state = {
                'pos': (self.rect.centerx, self.rect.centery),
                'facing_right': self.facing_right,
                'on_ground': self.on_ground
            }
            self.history.append(state)

    def get_past_state(self, frames_ago):
        """Получаем состояние игрока frames_ago кадров назад"""
        if frames_ago < len(self.history):
            return list(self.history)[-(frames_ago + 1)]
        return None

    def update(self, platforms, traps, level_end):
        # Движение по горизонтали
        keys = pygame.key.get_pressed()
        self.vel_x = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vel_x = -self.speed
            self.facing_right = False
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vel_x = self.speed
            self.facing_right = True

        # Прыжок
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False

        # Применяем гравитацию
        self.vel_y += self.gravity

        # Ограничиваем падение
        if self.vel_y > 20:
            self.vel_y = 20

        # Двигаем по X
        self.rect.x += self.vel_x

        # Проверяем столкновения по X
        self.check_collision(platforms, self.vel_x, 0)

        # Проверка на выход за пределы экрана
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

        # Двигаем по Y
        self.rect.y += self.vel_y
        self.on_ground = False

        # Проверяем столкновения по Y
        self.check_collision(platforms, 0, self.vel_y)

        # Проверка падения в пропасть
        if self.rect.top > HEIGHT:
            self.lives -= 1
            return "fall"

        # Проверка столкновения с ловушками
        for trap in traps:
            if self.rect.colliderect(trap.rect):
                self.lives -= 1
                return "trap"

        # Проверка достижения конца уровня
        if level_end and self.rect.colliderect(level_end.rect):
            return "level_complete"

        # Записываем состояние
        self.record_state()

        # Поворачиваем изображение при движении влево
        if not self.facing_right:
            self.image = pygame.transform.flip(self.original_image, True, False)
        else:
            self.image = self.original_image.copy()

        return "alive"

    def check_collision(self, platforms, vel_x, vel_y):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if vel_x > 0:  # Движение вправо
                    self.rect.right = platform.rect.left
                if vel_x < 0:  # Движение влево
                    self.rect.left = platform.rect.right
                if vel_y > 0:  # Падение вниз
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                    self.vel_y = 0
                if vel_y < 0:  # Движение вверх
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0


class Echo(pygame.sprite.Sprite):
    def __init__(self, player_history, start_frame, is_ghost=False):
        super().__init__()

        # Создаем изображение эха на основе игрока
        try:
            base_image = pygame.image.load("img.png").convert_alpha()
            base_image = pygame.transform.scale(base_image, (40, 60))
        except:
            base_image = pygame.Surface((40, 60), pygame.SRCALPHA)
            pygame.draw.rect(base_image, BLUE, (10, 0, 20, 30))
            pygame.draw.circle(base_image, (255, 200, 150), (20, 35), 12)
            pygame.draw.rect(base_image, BLUE, (5, 30, 10, 25))
            pygame.draw.rect(base_image, BLUE, (25, 30, 10, 25))
            pygame.draw.rect(base_image, BLUE, (0, 10, 10, 15))
            pygame.draw.rect(base_image, BLUE, (30, 10, 10, 15))

        self.image = base_image.copy()

        if is_ghost:
            # Призрак - фиолетовый и более прозрачный
            color_overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            color_overlay.fill((200, 100, 255, 120))  # Фиолетовый с прозрачностью
            self.image.blit(color_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.image.set_alpha(150)
        else:
            # Эхо - зеленый
            color_overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            color_overlay.fill((100, 255, 150, 150))  # Зеленый с прозрачностью
            self.image.blit(color_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.image.set_alpha(180)

        self.rect = self.image.get_rect()

        # Берем историю игрока
        self.history = list(player_history)[-start_frame:] if start_frame <= len(player_history) else list(
            player_history)
        self.current_frame = 0
        self.animation_speed = 1
        self.is_ghost = is_ghost
        self.original_for_flip = self.image.copy()

    def update(self):
        if self.current_frame < len(self.history):
            state = self.history[self.current_frame]
            self.rect.centerx, self.rect.centery = state['pos']

            # Поворачиваем в ту же сторону
            if not state.get('facing_right', True):
                self.image = pygame.transform.flip(self.original_for_flip, True, False)
            else:
                self.image = self.original_for_flip.copy()

            self.current_frame += self.animation_speed
        else:
            # Анимация закончилась - исчезаем
            self.kill()


class Crystal(pygame.sprite.Sprite):
    def __init__(self, x, y, crystal_type="green"):
        super().__init__()
        self.type = crystal_type

        # Цвета для кристаллов
        colors = {
            "green": (100, 255, 150),
            "blue": (100, 150, 255),
            "purple": (200, 100, 255)
        }

        # Создаем кристалл с эффектом свечения
        self.base_size = 20
        self.image = pygame.Surface((self.base_size * 2, self.base_size * 2), pygame.SRCALPHA)

        # Внешний слой (свечение)
        pygame.draw.polygon(self.image, (*colors[crystal_type][:3], 100), [
            (self.base_size, 0),
            (self.base_size * 1.7, self.base_size),
            (self.base_size, self.base_size * 2),
            (self.base_size * 0.3, self.base_size)
        ])

        # Внутренний слой
        inner_size = self.base_size * 0.6
        pygame.draw.polygon(self.image, colors[crystal_type], [
            (self.base_size, self.base_size - inner_size),
            (self.base_size + inner_size * 0.7, self.base_size),
            (self.base_size, self.base_size + inner_size),
            (self.base_size - inner_size * 0.7, self.base_size)
        ])

        self.rect = self.image.get_rect(center=(x, y))
        self.float_offset = 0
        self.collected = False

    def update(self):
        # Плавающая анимация
        if not self.collected:
            self.float_offset += 0.05
            self.rect.y += math.sin(self.float_offset) * 0.5


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=GRAY):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        # Добавляем текстуру
        for i in range(0, width, 4):
            pygame.draw.line(self.image, (color[0] - 20, color[1] - 20, color[2] - 20),
                             (i, 0), (i, height), 2)
        self.rect = self.image.get_rect(topleft=(x, y))


class MovingPlatform(Platform):
    def __init__(self, x, y, width, height, move_range, speed, vertical=True):
        super().__init__(x, y, width, height, color=(120, 120, 120))
        self.start_x = x
        self.start_y = y
        self.move_range = move_range
        self.speed = speed
        self.vertical = vertical
        self.direction = 1
        self.timer = 0

    def update(self):
        self.timer += 1
        if self.vertical:
            self.rect.y = self.start_y + math.sin(self.timer * self.speed / 100) * self.move_range
        else:
            self.rect.x = self.start_x + math.sin(self.timer * self.speed / 100) * self.move_range


class Trap(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(RED)
        # Рисуем шипы
        spike_height = height // 2
        for i in range(0, width, 20):
            points = [(i, height), (i + 10, height - spike_height), (i + 20, height)]
            pygame.draw.polygon(self.image, (150, 0, 0), points)
        self.rect = self.image.get_rect(topleft=(x, y))


class MovingTrap(Trap):
    def __init__(self, x, y, width, height, move_range, speed, horizontal=True):
        super().__init__(x, y, width, height)
        self.start_x = x
        self.start_y = y
        self.move_range = move_range
        self.speed = speed
        self.horizontal = horizontal
        self.timer = 0

    def update(self):
        self.timer += 1
        if self.horizontal:
            self.rect.x = self.start_x + math.sin(self.timer * self.speed / 100) * self.move_range
        else:
            self.rect.y = self.start_y + math.sin(self.timer * self.speed / 100) * self.move_range


class LevelEnd(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((60, 80))
        # Рисуем портал
        pygame.draw.ellipse(self.image, PURPLE, (0, 0, 60, 80))
        pygame.draw.ellipse(self.image, (150, 50, 200), (5, 5, 50, 70))
        # Анимированный центр портала
        center_size = 20 + math.sin(pygame.time.get_ticks() / 200) * 5
        pygame.draw.circle(self.image, YELLOW, (30, 40), int(center_size))
        self.rect = self.image.get_rect(center=(x, y))


class Level:
    def __init__(self, number):
        self.number = number
        self.platforms = pygame.sprite.Group()
        self.moving_platforms = pygame.sprite.Group()
        self.traps = pygame.sprite.Group()
        self.moving_traps = pygame.sprite.Group()
        self.crystals = pygame.sprite.Group()
        self.level_end = None
        self.player_start = (100, HEIGHT - 100)
        self.total_crystals = 0
        self.required_crystals = 0

        self.setup_level()

    def setup_level(self):
        if self.number == 1:
            self._setup_level_1()
        elif self.number == 2:
            self._setup_level_2()
        elif self.number == 3:
            self._setup_level_3()
        elif self.number == 4:
            self._setup_level_4()
        elif self.number == 5:
            self._setup_level_5()

    def _setup_level_1(self):
        """Первый уровень - обучение"""
        self.player_start = (100, HEIGHT - 100)
        self.required_crystals = 3

        # Платформы
        self.platforms.add(Platform(0, HEIGHT - 50, WIDTH, 50))
        self.platforms.add(Platform(200, HEIGHT - 150, 200, 20))
        self.platforms.add(Platform(500, HEIGHT - 200, 150, 20))
        self.platforms.add(Platform(800, HEIGHT - 250, 150, 20))

        # Кристаллы
        self.crystals.add(Crystal(300, HEIGHT - 200, "green"))
        self.crystals.add(Crystal(550, HEIGHT - 250, "green"))
        self.crystals.add(Crystal(850, HEIGHT - 300, "green"))

        # Выход
        self.level_end = LevelEnd(WIDTH - 100, HEIGHT - 300)

        self.total_crystals = len(self.crystals)

    def _setup_level_2(self):
        """Второй уровень - движущиеся платформы"""
        self.player_start = (100, HEIGHT - 100)
        self.required_crystals = 4

        # Основные платформы
        self.platforms.add(Platform(0, HEIGHT - 50, WIDTH, 50))
        self.platforms.add(Platform(100, HEIGHT - 200, 100, 20))
        self.platforms.add(Platform(400, HEIGHT - 300, 100, 20))
        self.platforms.add(Platform(700, HEIGHT - 200, 100, 20))

        # Движущиеся платформы
        self.moving_platforms.add(MovingPlatform(250, HEIGHT - 150, 80, 20, 100, 2))
        self.moving_platforms.add(MovingPlatform(550, HEIGHT - 250, 80, 20, 100, 1.5))

        # Кристаллы
        self.crystals.add(Crystal(150, HEIGHT - 250, "green"))
        self.crystals.add(Crystal(290, HEIGHT - 200, "blue"))
        self.crystals.add(Crystal(450, HEIGHT - 350, "green"))
        self.crystals.add(Crystal(590, HEIGHT - 300, "blue"))

        # Выход
        self.level_end = LevelEnd(WIDTH - 100, HEIGHT - 250)

        self.total_crystals = len(self.crystals)

    def _setup_level_3(self):
        """Третий уровень - ловушки"""
        self.player_start = (100, HEIGHT - 100)
        self.required_crystals = 5

        # Платформы
        self.platforms.add(Platform(0, HEIGHT - 50, WIDTH, 50))
        self.platforms.add(Platform(100, HEIGHT - 150, 100, 20))
        self.platforms.add(Platform(250, HEIGHT - 250, 100, 20))
        self.platforms.add(Platform(400, HEIGHT - 350, 100, 20))
        self.platforms.add(Platform(550, HEIGHT - 250, 100, 20))
        self.platforms.add(Platform(700, HEIGHT - 150, 100, 20))

        # Ловушки
        self.traps.add(Trap(220, HEIGHT - 170, 60, 20))
        self.traps.add(Trap(470, HEIGHT - 370, 60, 20))
        self.traps.add(Trap(720, HEIGHT - 170, 60, 20))

        # Движущиеся ловушки
        self.moving_traps.add(MovingTrap(370, HEIGHT - 380, 60, 20, 200, 1.5))

        # Кристаллы
        self.crystals.add(Crystal(150, HEIGHT - 200, "green"))
        self.crystals.add(Crystal(300, HEIGHT - 300, "blue"))
        self.crystals.add(Crystal(450, HEIGHT - 400, "purple"))
        self.crystals.add(Crystal(600, HEIGHT - 300, "blue"))
        self.crystals.add(Crystal(750, HEIGHT - 200, "green"))

        # Выход
        self.level_end = LevelEnd(WIDTH - 100, HEIGHT - 200)

        self.total_crystals = len(self.crystals)

    def _setup_level_4(self):
        """Четвертый уровень - сложная комбинация"""
        self.player_start = (100, HEIGHT - 100)
        self.required_crystals = 6

        # Платформы с пропусками
        self.platforms.add(Platform(0, HEIGHT - 50, 300, 20))
        self.platforms.add(Platform(400, HEIGHT - 50, 300, 20))
        self.platforms.add(Platform(800, HEIGHT - 50, 200, 20))

        self.platforms.add(Platform(150, HEIGHT - 200, 100, 20))
        self.platforms.add(Platform(350, HEIGHT - 300, 100, 20))
        self.platforms.add(Platform(600, HEIGHT - 250, 100, 20))

        # Движущиеся платформы
        self.moving_platforms.add(MovingPlatform(500, HEIGHT - 150, 80, 20, 150, 2, vertical=False))
        self.moving_platforms.add(MovingPlatform(200, HEIGHT - 350, 80, 20, 100, 1.8))

        # Ловушки
        self.traps.add(Trap(300, HEIGHT - 70, 100, 20))
        self.traps.add(Trap(700, HEIGHT - 70, 100, 20))

        # Кристаллы в труднодоступных местах
        self.crystals.add(Crystal(200, HEIGHT - 250, "green"))
        self.crystals.add(Crystal(400, HEIGHT - 350, "blue"))
        self.crystals.add(Crystal(650, HEIGHT - 300, "purple"))
        self.crystals.add(Crystal(850, HEIGHT - 100, "green"))
        self.crystals.add(Crystal(550, HEIGHT - 200, "blue"))
        self.crystals.add(Crystal(250, HEIGHT - 400, "purple"))

        # Выход
        self.level_end = LevelEnd(WIDTH - 100, HEIGHT - 100)

        self.total_crystals = len(self.crystals)

    def _setup_level_5(self):
        """Пятый уровень - финальный босс"""
        self.player_start = (100, HEIGHT - 100)
        self.required_crystals = 8

        # Сложная структура платформ
        self.platforms.add(Platform(0, HEIGHT - 50, 200, 20))
        self.platforms.add(Platform(300, HEIGHT - 50, 200, 20))
        self.platforms.add(Platform(600, HEIGHT - 50, 200, 20))

        # Башня из платформ
        for i in range(5):
            y_pos = HEIGHT - 150 - i * 80
            self.platforms.add(Platform(800, y_pos, 80, 20))

        # Движущиеся платформы по кругу
        for i in range(4):
            x_pos = 400 + math.cos(i * math.pi / 2) * 200
            y_pos = HEIGHT - 200 + math.sin(i * math.pi / 2) * 200
            mp = MovingPlatform(x_pos, y_pos, 60, 20, 50, 1.5 + i * 0.3)
            mp.vertical = (i % 2 == 0)
            self.moving_platforms.add(mp)

        # Много ловушек
        for i in range(3):
            self.traps.add(Trap(250 + i * 150, HEIGHT - 70, 80, 20))

        self.moving_traps.add(MovingTrap(500, HEIGHT - 300, 60, 20, 300, 2))

        # Много кристаллов разных типов
        crystal_positions = [
            (150, HEIGHT - 100, "green"),
            (400, HEIGHT - 100, "blue"),
            (650, HEIGHT - 100, "purple"),
            (850, HEIGHT - 200, "green"),
            (850, HEIGHT - 360, "blue"),
            (850, HEIGHT - 520, "purple"),
            (600, HEIGHT - 400, "green"),
            (300, HEIGHT - 400, "blue")
        ]

        for x, y, crystal_type in crystal_positions:
            self.crystals.add(Crystal(x, y, crystal_type))

        # Выход на вершине башни
        self.level_end = LevelEnd(830, HEIGHT - 600)

        self.total_crystals = len(self.crystals)

    def get_all_platforms(self):
        all_platforms = pygame.sprite.Group()
        all_platforms.add(self.platforms)
        all_platforms.add(self.moving_platforms)
        return all_platforms

    def get_all_traps(self):
        all_traps = pygame.sprite.Group()
        all_traps.add(self.traps)
        all_traps.add(self.moving_traps)
        return all_traps

    def get_all_sprites(self):
        all_sprites = pygame.sprite.Group()
        all_sprites.add(self.platforms)
        all_sprites.add(self.moving_platforms)
        all_sprites.add(self.traps)
        all_sprites.add(self.moving_traps)
        all_sprites.add(self.crystals)
        if self.level_end:
            all_sprites.add(self.level_end)
        return all_sprites


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Хроно-Сборщик - Система уровней")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 72)

        # Загружаем фон
        try:
            self.background = pygame.image.load("background.png").convert()
            self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))
        except:
            print("Файл background.png не найден! Создаю временный фон...")
            self.background = pygame.Surface((WIDTH, HEIGHT))
            # Создаем градиентный фон
            for y in range(HEIGHT):
                color_value = 20 + int(y / HEIGHT * 30)
                pygame.draw.line(self.background, (color_value, color_value + 10, color_value + 20),
                                 (0, y), (WIDTH, y))

            # Добавляем звезды на фон
            for _ in range(100):
                x = pygame.time.get_ticks() % WIDTH
                y = pygame.time.get_ticks() % HEIGHT
                size = (pygame.time.get_ticks() % 3) + 1
                brightness = 100 + (pygame.time.get_ticks() % 155)
                pygame.draw.circle(self.background, (brightness, brightness, brightness), (x, y), size)

        # Игровые переменные
        self.current_level = 1
        self.max_level = 5
        self.game_state = "menu"  # menu, playing, level_complete, game_over, game_complete
        self.reset_level()

    def reset_level(self):
        # Загружаем текущий уровень
        self.level = Level(self.current_level)

        # Группы спрайтов
        self.all_sprites = self.level.get_all_sprites()
        self.platforms = self.level.get_all_platforms()
        self.traps = self.level.get_all_traps()
        self.crystals = self.level.crystals
        self.echoes = pygame.sprite.Group()

        # Создаем игрока
        start_x, start_y = self.level.player_start
        self.player = Player(start_x, start_y)
        self.all_sprites.add(self.player)

        # Статистика уровня
        self.collected = 0
        self.total_crystals = self.level.total_crystals
        self.required_crystals = self.level.required_crystals
        self.echo_cooldown = 0
        self.ghost_cooldown = 0
        self.level_time = 0
        self.respawn_timer = 0

    def create_echo(self):
        """Создает эхо-копию игрока из 3-секундного прошлого"""
        if self.echo_cooldown <= 0:
            echo = Echo(self.player.history, 180, is_ghost=False)
            echo.rect.center = self.player.rect.center
            self.echoes.add(echo)
            self.all_sprites.add(echo)
            self.echo_cooldown = 60  # 1 секунда перезарядки
            return True
        return False

    def create_ghost(self):
        """Создает призрака из будущего"""
        if self.ghost_cooldown <= 0:
            ghost = Echo(self.player.history, 30, is_ghost=True)
            ghost.rect.center = self.player.rect.center
            self.echoes.add(ghost)
            self.all_sprites.add(ghost)
            self.ghost_cooldown = 90  # 1.5 секунды перезарядки
            return True
        return False

    def check_crystal_collision(self):
        """Проверяем сбор кристаллов эхом"""
        for crystal in self.crystals:
            if not hasattr(crystal, 'collected') or not crystal.collected:
                if pygame.sprite.spritecollide(crystal, self.echoes, False):
                    crystal.collected = True
                    self.collected += 1

                    # Эффект при сборе
                    for i in range(15):
                        particle = pygame.Rect(0, 0, 3, 3)
                        angle = i * (2 * math.pi / 15)
                        distance = 20
                        particle.center = (
                            crystal.rect.centerx + math.cos(angle) * distance,
                            crystal.rect.centery + math.sin(angle) * distance
                        )
                        pygame.draw.rect(self.screen, GREEN, particle)

    def handle_player_respawn(self):
        """Обработка респауна игрока после смерти"""
        if self.respawn_timer > 0:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                # Респавн игрока
                start_x, start_y = self.level.player_start
                self.player.rect.center = (start_x, start_y)
                self.player.vel_x = 0
                self.player.vel_y = 0
                self.player.on_ground = False
                return True
        return False

    def run(self):
        running = True

        while running:
            dt = self.clock.tick(FPS)

            # Обновление времени уровня
            if self.game_state == "playing":
                self.level_time += 1

            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if self.game_state == "menu":
                        if event.key == pygame.K_SPACE:
                            self.game_state = "playing"
                        elif event.key == pygame.K_ESCAPE:
                            running = False

                    elif self.game_state == "playing":
                        if event.key == pygame.K_q:
                            self.create_echo()
                        elif event.key == pygame.K_e:
                            self.create_ghost()
                        elif event.key == pygame.K_r:
                            self.reset_level()
                        elif event.key == pygame.K_ESCAPE:
                            self.game_state = "menu"

                    elif self.game_state in ["level_complete", "game_over", "game_complete"]:
                        if event.key == pygame.K_SPACE:
                            if self.game_state == "level_complete" and self.current_level < self.max_level:
                                self.current_level += 1
                                self.reset_level()
                                self.game_state = "playing"
                            elif self.game_state == "game_complete":
                                self.current_level = 1
                                self.reset_level()
                                self.game_state = "menu"
                            elif self.game_state == "game_over":
                                self.current_level = 1
                                self.reset_level()
                                self.game_state = "menu"
                        elif event.key == pygame.K_ESCAPE:
                            self.game_state = "menu"

            # Игровая логика
            if self.game_state == "playing":
                # Проверка респауна
                if self.respawn_timer > 0:
                    if self.handle_player_respawn():
                        continue

                # Обновление перезарядок
                if self.echo_cooldown > 0:
                    self.echo_cooldown -= 1
                if self.ghost_cooldown > 0:
                    self.ghost_cooldown -= 1

                # Обновление движущихся объектов
                self.level.moving_platforms.update()
                self.level.moving_traps.update()

                # Обновление игрока
                result = self.player.update(self.platforms, self.traps, self.level.level_end)

                # Обработка результатов обновления игрока
                if result == "level_complete":
                    if self.collected >= self.required_crystals:
                        if self.current_level == self.max_level:
                            self.game_state = "game_complete"
                        else:
                            self.game_state = "level_complete"
                    else:
                        # Игрок достиг выхода, но не собрал достаточно кристаллов
                        pass
                elif result in ["fall", "trap"]:
                    if self.player.lives > 0:
                        self.respawn_timer = 60  # 1 секунда до респауна
                    else:
                        self.game_state = "game_over"

                # Обновление эха
                self.echoes.update()

                # Обновление кристаллов
                self.crystals.update()

                # Проверка сбора кристаллов
                self.check_crystal_collision()

            # Отрисовка
            # Сначала рисуем фон
            self.screen.blit(self.background, (0, 0))

            if self.game_state == "menu":
                self.draw_menu()
            elif self.game_state == "playing":
                # Затем все спрайты
                self.all_sprites.draw(self.screen)

                # Рисуем UI поверх всего
                self.draw_ui()

                # Мигание при респауне
                if self.respawn_timer > 0 and self.respawn_timer % 10 < 5:
                    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    overlay.fill((255, 255, 255, 100))
                    self.screen.blit(overlay, (0, 0))

            elif self.game_state == "level_complete":
                self.draw_level_complete()
            elif self.game_state == "game_over":
                self.draw_game_over()
            elif self.game_state == "game_complete":
                self.draw_game_complete()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def draw_menu(self):
        # Затемнение фона
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Название игры
        title = self.title_font.render("ХРОНО-СБОРЩИК", True, YELLOW)
        title_shadow = self.title_font.render("ХРОНО-СБОРЩИК", True, (100, 100, 0))
        self.screen.blit(title_shadow, (WIDTH // 2 - title.get_width() // 2 + 3, HEIGHT // 4 - 50 + 3))
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4 - 50))

        # Описание игры
        desc_lines = [
            "Собирайте кристаллы времени с помощью ваших копий!",
            "Используйте Эхо (Q) и Призраков (E) для сбора кристаллов.",
            "Соберите достаточно кристаллов и достигните портала."
        ]

        for i, line in enumerate(desc_lines):
            desc_text = self.small_font.render(line, True, WHITE)
            self.screen.blit(desc_text, (WIDTH // 2 - desc_text.get_width() // 2, HEIGHT // 2 + i * 30))

        # Уровни
        level_text = self.font.render(f"Доступно уровней: {self.max_level}", True, GREEN)
        self.screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 2 + 120))

        # Кнопка начала игры
        start_bg = pygame.Surface((300, 60), pygame.SRCALPHA)
        start_bg.fill((0, 100, 0, 200))
        self.screen.blit(start_bg, (WIDTH // 2 - 150, HEIGHT // 2 + 180))

        start_text = self.font.render("НАЧАТЬ ИГРУ (SPACE)", True, WHITE)
        self.screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 + 195))

        # Управление
        controls = [
            "A/D или ←/→ - Движение",
            "SPACE/W/↑ - Прыжок",
            "Q - Создать Эхо (прошлое)",
            "E - Создать Призрака (будущее)",
            "ESC - Пауза/Меню"
        ]

        controls_bg = pygame.Surface((350, 160), pygame.SRCALPHA)
        controls_bg.fill((0, 0, 0, 150))
        self.screen.blit(controls_bg, (WIDTH // 2 - 175, HEIGHT - 200))

        for i, control in enumerate(controls):
            control_text = self.small_font.render(control, True, WHITE)
            self.screen.blit(control_text, (WIDTH // 2 - control_text.get_width() // 2, HEIGHT - 190 + i * 30))

    def draw_ui(self):
        # Верхняя панель информации
        top_panel = pygame.Surface((WIDTH, 50), pygame.SRCALPHA)
        top_panel.fill((0, 0, 0, 150))
        self.screen.blit(top_panel, (0, 0))

        # Уровень
        level_text = self.font.render(f"Уровень: {self.current_level}/{self.max_level}", True, YELLOW)
        self.screen.blit(level_text, (20, 10))

        # Кристаллы
        crystals_text = self.font.render(f"Кристаллы: {self.collected}/{self.required_crystals}",
                                         True, GREEN if self.collected >= self.required_crystals else WHITE)
        self.screen.blit(crystals_text, (WIDTH // 2 - crystals_text.get_width() // 2, 10))

        # Жизни
        lives_text = self.font.render(f"Жизни: {self.player.lives}",
                                      True,
                                      RED if self.player.lives == 1 else GREEN if self.player.lives > 1 else WHITE)
        self.screen.blit(lives_text, (WIDTH - 150, 10))

        # Иконки жизней
        for i in range(min(self.player.lives, 5)):
            heart_rect = pygame.Rect(WIDTH - 180 + i * 25, 45, 20, 20)
            pygame.draw.polygon(self.screen, RED, [
                (heart_rect.centerx, heart_rect.top),
                (heart_rect.right, heart_rect.centery - 5),
                (heart_rect.right, heart_rect.bottom),
                (heart_rect.centerx, heart_rect.bottom + 5),
                (heart_rect.left, heart_rect.bottom),
                (heart_rect.left, heart_rect.centery - 5)
            ])

        # Панель способностей внизу
        bottom_panel = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)
        bottom_panel.fill((0, 0, 0, 150))
        self.screen.blit(bottom_panel, (0, HEIGHT - 100))

        # Способность Эхо
        echo_bg = pygame.Surface((200, 40), pygame.SRCALPHA)
        echo_bg.fill((0, 50, 0, 200) if self.echo_cooldown > 0 else (0, 100, 0, 200))
        self.screen.blit(echo_bg, (50, HEIGHT - 90))

        echo_text = self.small_font.render("ЭХО (Q)", True, WHITE)
        self.screen.blit(echo_text, (60, HEIGHT - 85))

        if self.echo_cooldown > 0:
            cooldown_width = 180 * (1 - self.echo_cooldown / 60)
            pygame.draw.rect(self.screen, (50, 150, 50), (60, HEIGHT - 60, cooldown_width, 10))
            time_left = self.echo_cooldown / 60
            cooldown_text = self.small_font.render(f"{time_left:.1f} сек", True, WHITE)
            self.screen.blit(cooldown_text, (150, HEIGHT - 75))
        else:
            ready_text = self.small_font.render("ГОТОВО", True, YELLOW)
            self.screen.blit(ready_text, (150, HEIGHT - 75))

        # Способность Призрак
        ghost_bg = pygame.Surface((200, 40), pygame.SRCALPHA)
        ghost_bg.fill((50, 0, 50, 200) if self.ghost_cooldown > 0 else (100, 0, 100, 200))
        self.screen.blit(ghost_bg, (WIDTH - 250, HEIGHT - 90))

        ghost_text = self.small_font.render("ПРИЗРАК (E)", True, WHITE)
        self.screen.blit(ghost_text, (WIDTH - 240, HEIGHT - 85))

        if self.ghost_cooldown > 0:
            cooldown_width = 180 * (1 - self.ghost_cooldown / 90)
            pygame.draw.rect(self.screen, (150, 50, 150), (WIDTH - 240, HEIGHT - 60, cooldown_width, 10))
            time_left = self.ghost_cooldown / 60
            cooldown_text = self.small_font.render(f"{time_left:.1f} сек", True, WHITE)
            self.screen.blit(cooldown_text, (WIDTH - 150, HEIGHT - 75))
        else:
            ready_text = self.small_font.render("ГОТОВО", True, YELLOW)
            self.screen.blit(ready_text, (WIDTH - 150, HEIGHT - 75))

        # Подсказка в центре
        hint_bg = pygame.Surface((400, 30), pygame.SRCALPHA)
        hint_bg.fill((0, 0, 0, 150))
        self.screen.blit(hint_bg, (WIDTH // 2 - 200, HEIGHT - 50))

        if self.collected < self.required_crystals:
            hint = self.small_font.render(f"Соберите {self.required_crystals - self.collected} кристаллов для выхода!",
                                          True, YELLOW)
        else:
            hint = self.small_font.render("Достигните портала для завершения уровня!", True, GREEN)

        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 45))

    def draw_level_complete(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Поздравление
        congrats_text = self.title_font.render("УРОВЕНЬ ПРОЙДЕН!", True, YELLOW)
        self.screen.blit(congrats_text, (WIDTH // 2 - congrats_text.get_width() // 2, HEIGHT // 3 - 50))

        # Статистика
        stats_bg = pygame.Surface((500, 200), pygame.SRCALPHA)
        stats_bg.fill((0, 0, 50, 150))
        self.screen.blit(stats_bg, (WIDTH // 2 - 250, HEIGHT // 2 - 50))

        stats = [
            f"Кристаллы собраны: {self.collected}/{self.total_crystals}",
            f"Требовалось: {self.required_crystals}",
            f"Жизней осталось: {self.player.lives}",
            f"Время: {self.level_time // 60} сек"
        ]

        for i, stat in enumerate(stats):
            stat_text = self.font.render(stat, True, WHITE)
            self.screen.blit(stat_text, (WIDTH // 2 - stat_text.get_width() // 2, HEIGHT // 2 - 30 + i * 40))

        # Кнопка продолжения
        if self.current_level < self.max_level:
            next_bg = pygame.Surface((400, 60), pygame.SRCALPHA)
            next_bg.fill((0, 100, 0, 200))
            self.screen.blit(next_bg, (WIDTH // 2 - 200, HEIGHT - 200))

            next_text = self.font.render(f"СЛЕДУЮЩИЙ УРОВЕНЬ (SPACE)", True, WHITE)
            self.screen.blit(next_text, (WIDTH // 2 - next_text.get_width() // 2, HEIGHT - 185))

            level_preview = self.small_font.render(
                f"Уровень {self.current_level + 1}: {self._get_level_name(self.current_level + 1)}", True, YELLOW)
            self.screen.blit(level_preview, (WIDTH // 2 - level_preview.get_width() // 2, HEIGHT - 150))
        else:
            final_bg = pygame.Surface((400, 60), pygame.SRCALPHA)
            final_bg.fill((100, 0, 100, 200))
            self.screen.blit(final_bg, (WIDTH // 2 - 200, HEIGHT - 200))

            final_text = self.font.render("ФИНАЛЬНЫЙ УРОВЕНЬ ДАЛЕЕ!", True, WHITE)
            self.screen.blit(final_text, (WIDTH // 2 - final_text.get_width() // 2, HEIGHT - 185))

        # Кнопка меню
        menu_bg = pygame.Surface((300, 50), pygame.SRCALPHA)
        menu_bg.fill((100, 100, 100, 200))
        self.screen.blit(menu_bg, (WIDTH // 2 - 150, HEIGHT - 100))

        menu_text = self.font.render("МЕНЮ (ESC)", True, WHITE)
        self.screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT - 90))

    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Сообщение о поражении
        game_over_text = self.title_font.render("ИГРА ОКОНЧЕНА", True, RED)
        self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 3 - 50))

        # Статистика
        stats_bg = pygame.Surface((500, 150), pygame.SRCALPHA)
        stats_bg.fill((50, 0, 0, 150))
        self.screen.blit(stats_bg, (WIDTH // 2 - 250, HEIGHT // 2 - 50))

        stats = [
            f"Достигнут уровень: {self.current_level}",
            f"Кристаллов собрано: {self.collected}",
            f"Всего кристаллов: {self.total_crystals}"
        ]

        for i, stat in enumerate(stats):
            stat_text = self.font.render(stat, True, WHITE)
            self.screen.blit(stat_text, (WIDTH // 2 - stat_text.get_width() // 2, HEIGHT // 2 - 30 + i * 40))

        # Кнопка рестарта
        restart_bg = pygame.Surface((400, 60), pygame.SRCALPHA)
        restart_bg.fill((100, 0, 0, 200))
        self.screen.blit(restart_bg, (WIDTH // 2 - 200, HEIGHT - 200))

        restart_text = self.font.render("НАЧАТЬ ЗАНОВО (SPACE)", True, WHITE)
        self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT - 185))

        # Кнопка меню
        menu_bg = pygame.Surface((300, 50), pygame.SRCALPHA)
        menu_bg.fill((100, 100, 100, 200))
        self.screen.blit(menu_bg, (WIDTH // 2 - 150, HEIGHT - 100))

        menu_text = self.font.render("МЕНЮ (ESC)", True, WHITE)
        self.screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT - 90))

    def draw_game_complete(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Поздравление с победой
        victory_text = self.title_font.render("ВЫ ПОБЕДИЛИ!", True, YELLOW)
        self.screen.blit(victory_text, (WIDTH // 2 - victory_text.get_width() // 2, HEIGHT // 4 - 50))

        # Сообщение
        message = self.font.render("Вы собрали все кристаллы времени!", True, GREEN)
        self.screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT // 4 + 50))

        # Итоговая статистика
        stats_bg = pygame.Surface((600, 200), pygame.SRCALPHA)
        stats_bg.fill((0, 50, 0, 150))
        self.screen.blit(stats_bg, (WIDTH // 2 - 300, HEIGHT // 2 - 50))

        final_stats = [
            f"Все уровни пройдены: {self.max_level}/5",
            f"Жизней осталось: {self.player.lives}",
            f"Всего собрано кристаллов: {self.collected}",
            f"Общее время игры: {self.level_time // 60} сек"
        ]

        for i, stat in enumerate(final_stats):
            stat_text = self.font.render(stat, True, WHITE)
            self.screen.blit(stat_text, (WIDTH // 2 - stat_text.get_width() // 2, HEIGHT // 2 - 30 + i * 40))

        # Кнопка новой игры
        new_game_bg = pygame.Surface((400, 60), pygame.SRCALPHA)
        new_game_bg.fill((0, 100, 0, 200))
        self.screen.blit(new_game_bg, (WIDTH // 2 - 200, HEIGHT - 200))

        new_game_text = self.font.render("НОВАЯ ИГРА (SPACE)", True, WHITE)
        self.screen.blit(new_game_text, (WIDTH // 2 - new_game_text.get_width() // 2, HEIGHT - 185))

        # Кнопка меню
        menu_bg = pygame.Surface((300, 50), pygame.SRCALPHA)
        menu_bg.fill((100, 100, 100, 200))
        self.screen.blit(menu_bg, (WIDTH // 2 - 150, HEIGHT - 100))

        menu_text = self.font.render("МЕНЮ (ESC)", True, WHITE)
        self.screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT - 90))

    def _get_level_name(self, level_num):
        """Получаем название уровня по номеру"""
        names = {
            1: "Обучение",
            2: "Движущиеся платформы",
            3: "Ловушки",
            4: "Сложная комбинация",
            5: "Финальное испытание"
        }
        return names.get(level_num, f"Уровень {level_num}")


# Запуск игры
if __name__ == "__main__":
    game = Game()
    game.run()