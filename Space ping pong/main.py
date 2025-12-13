import time
import pygame
pygame.init()
from PIL import Image
from config import *
import random
import math


WIDTH = 1200
HEIGHT = 1000


score_1 = 0
score_2 = 0


clock = pygame.time.Clock()


window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Ping - Pong')



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

class Player1(GameSprite):
    def __init__(self, player_image, player_x, player_y, width, height, speed_x, speed_y, speed, speed_max):
        super().__init__(player_image, player_x, player_y, width, height)
        self.health = 1
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.speed = speed
        self.speed_max = speed_max

    def update(self):
        keys_pressed = pygame.key.get_pressed()

        if keys_pressed[pygame.K_a]:
            self.speed_x -= self.speed
        if keys_pressed[pygame.K_d]:
            self.speed_x += self.speed

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

class Player2(GameSprite):
    def __init__(self, player_image, player_x, player_y, width, height, speed_x, speed_y, speed, speed_max):
        super().__init__(player_image, player_x, player_y, width, height)
        self.health = 1
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.speed = speed
        self.speed_max = speed_max

    def update(self):
        keys_pressed = pygame.key.get_pressed()

        if keys_pressed[pygame.K_LEFT]:
            self.speed_x -= self.speed
        if keys_pressed[pygame.K_RIGHT]:
            self.speed_x += self.speed
        # if keys_pressed[pygame.K_UP]:
        #     self.speed_y -= self.speed * 0.7
        # if keys_pressed[pygame.K_DOWN]:
        #     self.speed_y += self.speed


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

class Ball(GameSprite):
    def __init__(self, player_image, player_x, player_y, width, height, speed_x, speed_y):
        super().__init__(player_image, player_x, player_y, width, height)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.speed = 2

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.x < 0:
            self.speed_x += self.speed * 1.2
        if self.rect.x > WIDTH - self.rect.width:
            self.speed_x -= self.speed * 1.2

        if self.rect.y < 0:
            self.speed_y += self.speed * 1.2
        if self.rect.y > HEIGHT - self.rect.height:
            self.speed_y -= self.speed * 1.2


        if pygame.sprite.collide_rect(player_1, ball):
            ball.speed_y = -ball.speed_y
        if pygame.sprite.collide_rect(player_2, ball):
            ball.speed_y = -ball.speed_y



background = GameSprite(random.choice(backgrounds_images), 0, 0, WIDTH, HEIGHT)

player_1 = Player1(player_images[0], WIDTH / 2 - 60, HEIGHT -20, 90, 90, 5, 5, 10, 12)
player_2 = Player2(player_images[0], WIDTH / 2 - 60, HEIGHT -980, 90, 90, 5, 5, 10, 12)

player_2.rotate()
player_2.rotate()

players = [player_1, [player_2]]

ball = Ball('Images/balls/img.png', WIDTH/2-60, HEIGHT/2-60, 100, 100, 5, 5)

game = True
while game:
    background.draw()

    player_1.draw()
    player_1.update()

    player_2.draw()
    player_2.update()

    ball.draw()
    ball.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            x_go, y_go = event.pos
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game = False

    pygame.display.update()
    clock.tick(60)