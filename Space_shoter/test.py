import time

import pygame
pygame.init()
from PIL import Image
from config import *
import random
import math

WIDTH = 1200
HEIGHT = 1000

score = 0

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

    def rotate(self):
        """Поворачивает картинку на 90 градусов по часовой стрелке"""
        self.image = pygame.transform.rotate(self.image, 90)


        old_center = self.rect.center


        self.rect = self.image.get_rect()
        self.rect.center = old_center

def show_screen(txt):
    text = Label(WIDTH / 2, HEIGHT / 3, 0, 0, (0, 0, 0))
    text.set_text(txt, 50, (0, 0, 0))
    while True:
        background.draw()

        text.draw()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
            if event.type == pygame.MOUSEBUTTONDOWN:
                x_go, y_go = event.pos
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    break


        pygame.display.update()
        clock.tick(60)


class Player(GameSprite):
    def __init__(self, player_image, player_x, player_y, width, height, speed_x, speed_y, speed, speed_max, kd):
        super().__init__(player_image, player_x, player_y, width, height)
        self.health = 1
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.speed = speed
        self.speed_max = speed_max
        self.kd = kd
        self.last_shoot_time = 0

    def update(self):
        keys_pressed = pygame.key.get_pressed()

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
                bullet = Bullet(random.choice(lasers_images), self.rect.x + self.rect.width / 7, self.rect.y, 60, 90)
                bullet.rect.x += random.uniform(-16, 18)
                bullet.rotate()
                Bullet.bullets.append(bullet)
                self.last_shoot_time = time.time()

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
        if self.rect.x > player.rect.x:
            self.rect.x -= player.speed * 0.1
        if self.rect.x < player.rect.x:
            self.rect.x += player.speed * 0.1
        if self.rect.y > WIDTH:
            enemies.remove(self)
            global max_enemies
            global score
            score -= 1



class Bullet(GameSprite):
    bullets = []
    def update(self):
        self.rect.y -= 15

        if self.rect.y < -50:
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
player = Player(player_images[0], WIDTH / 2 - 60, HEIGHT, 90, 90, 5, 5, 10, 12, 1)



score_text = Label(10, 10, 0, 0 , (0, 0, 0))
kd_text = Label(500, 500,  30, 0, (0, 250, 250))

game = True

health = 0

while game:
    background.draw()
    if score >= 1000:
        show_screen('Победа!')
        exit()
    if score <= -100:
        show_screen('Поражение!')
        exit()

    score_text.set_text(f'Очки: {score}', fsize=20, text_color=(0, 250, 250))
    score_text.draw()
    if player.kd > 0:
        kd_text.set_text(f'Задержка: {player.kd}', fsize=20, text_color=(0, 250, 250))
        kd_text.draw()

    player.draw()
    player.update()

    while len(enemies) < max_enemies:
        size_kf = random.uniform(1, 1.8)
        enemy = Enemy(player_image=random.choice(en_images),
                      player_x=random.randint(-10, WIDTH),
                      player_y=random.uniform(-100, -50),
                      width=35 * size_kf,
                      height=35 * size_kf,
                      speed_x=random.uniform(0.2,0.5),
                      speed_y=random.uniform(4,7),)
        enemies.append(enemy)




    for enemy in enemies:
        enemy.update()
        enemy.draw()
        if pygame.sprite.collide_rect(player, enemy):
            health += 1
            max_enemies //= 2
            if health > len(player_images) - 1:
                health = len(player_images) - 1
                show_screen('Вы проиграли')
            while len(enemies) > 0:
                enemies.pop(0)
            player = Player(player_images[health], player.rect.x, player.rect.y, 90, 90, 5, 5, 10, 12, player.kd)
            break
    try:
        for bullet in Bullet.bullets:
            bullet.update()
            bullet.draw()
            for enemy in enemies:
                if pygame.sprite.collide_rect(bullet, enemy):
                    enemies.remove(enemy)
                    Bullet.bullets.remove(bullet)
                    max_enemies += 1
                    player.kd -= 0.1
                    score += 1
    except:
        print('Ошибка удаления')

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