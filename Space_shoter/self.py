import time

import pygame

pygame.init()
from PIL import Image
from config import *
import random
import math

WIDTH = 1200
HEIGHT = 1000

clock = pygame.time.Clock()

max_enemies = 1

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Space Shoter')

enemies = []


def get_cropped(path: str):
    # Открываем изображение
    img = Image.open(path)
    img = img.convert("RGBA")
    alpha = img.split()[-1]
    bbox = alpha.getbbox()
    if bbox:
        cropped_img = img.crop(bbox)
        cropped_img.save(path)


def smooth_sine(t, t_max=600, amplitude=3, cycles=1):
    B = 2 * math.pi * cycles / t_max
    return amplitude * math.sin(B * t)


class GameSprite(pygame.sprite.Sprite):
    cache = {}

    def __init__(self, player_image, player_x, player_y, width, height):
        super().__init__()
        if player_image not in GameSprite.cache:
            get_cropped(player_image)
            GameSprite.cache[player_image] = pygame.transform.scale(pygame.image.load(player_image), (width, height))
            print(f'Картинка {player_image} прогружена!')
        self.original_image = GameSprite.cache[player_image]
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def draw(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

    def rotate(self, angle):
        """Поворачивает картинку на заданный угол"""
        self.image = pygame.transform.rotate(self.original_image, angle)
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center


class Player(GameSprite):
    def __init__(self, player_image, player_x, player_y, width, height, speed_x, speed_y, speed, speed_max, kd):
        super().__init__(player_image, player_x, player_y, width, height)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.speed = speed
        self.health = 5
        self.speed_max = speed_max
        self.kd = kd
        self.last_shoot_time = 0
        self.angle = 0 # Угол поворота игрока
        self.last_direction = (0, -1)  # Направление движения по умолчанию (вверх)

    def update(self):
        keys_pressed = pygame.key.get_pressed()

        # Сохраняем предыдущее состояние движения
        prev_speed_x = self.speed_x
        prev_speed_y = self.speed_y

        if keys_pressed[pygame.K_LEFT]:
            self.speed_x -= self.speed
        if keys_pressed[pygame.K_RIGHT]:
            self.speed_x += self.speed
        if keys_pressed[pygame.K_UP]:
            self.speed_y -= self.speed * 0.7
        if keys_pressed[pygame.K_DOWN]:
            self.speed_y += self.speed
        if keys_pressed[pygame.K_SPACE]:
            if time.time() - self.last_shoot_time > self.kd:
                # Создаем пулю в центре игрока
                bullet = Bullet(random.choice(lasers_images),
                                self.rect.centerx,
                                self.rect.centery,
                                60, 90)

                # Направляем пулю в текущем направлении движения игрока
                direction_x, direction_y = self.last_direction

                # Если игрок стоит на месте, стреляем в последнем направлении движения
                # Если последнего направления нет, стреляем вверх
                if direction_x == 0 and direction_y == 0:
                    direction_x, direction_y = 0, -1

                # Нормализуем вектор направления
                length = math.sqrt(direction_x ** 2 + direction_y ** 2)
                if length > 0:
                    direction_x /= length
                    direction_y /= length

                # Устанавливаем скорость пули в зависимости от направления
                bullet.speed_x = direction_x * 15
                bullet.speed_y = direction_y * 15

                # Поворачиваем пулю в направлении движения
                bullet_angle = math.degrees(math.atan2(direction_y, direction_x))
                bullet.rotate(bullet_angle)

                Bullet.bullets.append(bullet)
                self.last_shoot_time = time.time()

        # Обновляем направление движения на основе скорости
        current_speed_x = self.speed_x
        current_speed_y = self.speed_y

        # Если есть движение, обновляем последнее направление
        if abs(current_speed_x) > 0.1 or abs(current_speed_y) > 0.1:
            self.last_direction = (current_speed_x, current_speed_y)
            # Вычисляем угол поворота на основе направления движения
            self.angle = math.degrees(math.atan2(current_speed_y, current_speed_x)) +90
            self.rotate(self.angle)

        if self.speed_x > self.speed_max:
            self.speed_x -= self.speed
        if self.speed_x < -self.speed_max:
            self.speed_x += self.speed

        if self.speed_y > self.speed_max:
            self.speed_y -= self.speed
        if self.speed_y < -self.speed_max:
            self.speed_y += self.speed

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.speed_x > 0:
            self.speed_x -= self.speed * 0.8
            if self.speed_x < 0:
                self.speed_x = 0
        if self.speed_x < 0:
            self.speed_x += self.speed * 0.8
            if self.speed_x > 0:
                self.speed_x = 0

        if self.speed_y > 0:
            self.speed_y -= self.speed * 0.8
            if self.speed_y < 0:
                self.speed_y = 0
        if self.speed_y < 0:
            self.speed_y += self.speed * 0.8
            if self.speed_y > 0:
                self.speed_y = 0

        if self.rect.x < 0:
            self.speed_x += self.speed * 1.2
        if self.rect.x > WIDTH - self.rect.width:
            self.speed_x -= self.speed * 1.2

        if self.rect.y < 0:
            self.speed_y += self.speed * 1.2
        if self.rect.y > HEIGHT - self.rect.height:
            self.speed_y -= self.speed * 1.2


class Enemy(GameSprite):
    def __init__(self, player_image, player_x, player_y, width, height, speed_x, speed_y):
        super().__init__(player_image, player_x, player_y, width, height)
        self.speed_x = speed_x
        self.speed_y = speed_y

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.x > WIDTH:
            enemies.remove(self)
            global max_enemies
            max_enemies += 1


class Bullet(GameSprite):
    bullets = []

    def __init__(self, player_image, player_x, player_y, width, height):
        super().__init__(player_image, player_x, player_y, width, height)
        self.speed_x = 0
        self.speed_y = -15  # Значение по умолчанию

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Удаляем пулю, если она вышла за пределы экрана
        if (self.rect.y < -50 or self.rect.y > HEIGHT + 50 or
                self.rect.x < -50 or self.rect.x > WIDTH + 50):
            if self in Bullet.bullets:
                Bullet.bullets.remove(self)


class Area:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.fill_color = color

    def color(self, new_color):
        self.fill_color = new_color

    def fill(self):
        pygame.draw.rect(window, self.fill_color, self.rect)

    def outline(self, frame_color, thickness):
        pygame.draw.rect(window, frame_color, self.rect, thickness)

    def collidepoint(self, x, y):
        return self.rect.collidepoint(x, y)


class Label(Area):
    def set_text(self, text, fsize=12, text_color=(0, 0, 0)):
        self.image = pygame.font.SysFont("verdana", fsize).render(text, True, text_color)

    def draw(self, shift_x=0, shift_y=0):
        self.fill()
        window.blit(self.image, (self.rect.x + shift_x, self.rect.y + shift_y))


background = GameSprite(random.choice(backgrounds_images), 0, 0, WIDTH, HEIGHT)
player = Player(random.choice(player_images), WIDTH / 2 - 60, HEIGHT, 90, 90, 5, 5, 10, 12, 1)

score = 0

score_text = Label(10, 10, 0, 0, (0, 0, 0))
kd_text = Label(500, 500, 30, 0, (0, 250, 250))

game = True

while game:
    background.draw()

    score_text.set_text(f'Очки: {score}', fsize=20, text_color=(0, 250, 250))
    score_text.draw()
    if player.kd > 0:
        kd_text.set_text(f'Задержка: {player.kd}', fsize=20, text_color=(0, 250, 250))
        kd_text.draw()

    player.draw()
    player.update()

    if len(enemies) < max_enemies:
        size_kf = random.uniform(1, 1.8)
        enemy = Enemy(player_image=random.choice(en_images),
                      player_x=random.randint(-10, WIDTH),
                      player_y=random.uniform(-100, -50),
                      width=35 * size_kf,
                      height=35 * size_kf,
                      speed_x=random.uniform(0.2, 0.5),
                      speed_y=random.uniform(4, 7), )
        enemies.append(enemy)
        max_enemies += 1

    for enemy in enemies:
        enemy.update()
        enemy.draw()

    try:
        for bullet in Bullet.bullets:
            for enemy in enemies:
                if pygame.sprite.collide_rect(bullet, enemy):
                    enemies.remove(enemy)
                    Bullet.bullets.remove(bullet)
                    player.kd -= 0.1
                    score += 1
    except:
        print('Ошибка удаления')

    for bullet in Bullet.bullets:
        bullet.update()
        bullet.draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            x_go, y_go = event.pos
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game = False
            if event.key == pygame.K_q:
                score += 500

    pygame.display.update()
    clock.tick(60)