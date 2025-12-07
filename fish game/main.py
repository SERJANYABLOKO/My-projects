import pygame
pygame.init()
from pprint import pprint
import time, random
import config
import math

pygame.mixer.init()

WIDTH = 800
HEIGHT = 800

clock = pygame.time.Clock()

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Лабиринт')

music = pygame.mixer.Sound('music/music.mp3')

score = 0

def smooth_sine(t, t_max=600, amplitude=3, cycles=1):
    B = 2 * math.pi * cycles / t_max
    return amplitude * math.sin(B * t)

from PIL import Image

def get_cropped(path: str):
    # Открываем изображение
    img = Image.open(path)

    img = img.convert("RGBA")
    alpha = img.split()[-1]

    # Получаем координаты всех пикселей с alpha > 0
    bbox = alpha.getbbox()  # по умолчанию учитывает все >0

    if bbox:
        cropped_img = img.crop(bbox)
        cropped_img.save(path)

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


class Player(GameSprite):
    def __init__(self, player_image, player_x, player_y, width, height, speed_x, speed_y, speed, speed_max):
        super().__init__(player_image, player_x, player_y, width, height)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.speed = speed
        self.health = 5
        self.speed_max = speed_max
        self.facing_right = True  # Направление взгляда (True - вправо, False - влево)

    def update(self):
        keys_pressed = pygame.key.get_pressed()

        if keys_pressed[pygame.K_LEFT]:
            self.speed_x -= self.speed
            self.facing_right = False  # Двигаемся влево
        if keys_pressed[pygame.K_RIGHT]:
            self.speed_x += self.speed
            self.facing_right = True  # Двигаемся вправо
        if keys_pressed[pygame.K_UP]:
            self.speed_y -= self.speed
        if keys_pressed[pygame.K_DOWN]:
            self.speed_y += self.speed
            

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
        if self.rect.y > HEIGHT - self.rect.height * 3:
            self.speed_y -= self.speed * 1.2

        # Зеркальное отражение изображения в зависимости от направления
        if self.facing_right:
            self.image = self.original_image
        else:
            self.image = pygame.transform.flip(self.original_image, True, False)

        if random.randint(0, 10) == 0:
                    bubble = Bubble(
                        images=['Images/bubble_b.png', 'Images/bubble_a.png', 'Images/bubble_c.png'],
                        bubble_x=self.rect.x,
                        bubble_y=self.rect.y,
                        width=15,
                        height=15,
                        speed_y=1,
                    )
                    Bubble.bubbles.append(bubble)

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

class Bubble(GameSprite):
    bubbles = []
    def __init__(self, images : list, bubble_x, bubble_y, width, height, speed_y):
        super().__init__(images[0], bubble_x, bubble_y, width, height)

        self.frames = []
        for img in images:
            if img not in GameSprite.cache:
                get_cropped(img)
                GameSprite.cache[img] = pygame.transform.scale(
                    pygame.image.load(img), (width, height)
                )
                print(f'Картинка {img} прогружена (для пузырей)!')
            self.frames.append(GameSprite.cache[img])

        self.frame_index = 0
        self.start_time = time.time()

        self.speed_y = speed_y

    def update(self):
        self.rect.y -= self.speed_y
        if time.time() - self.start_time > 1:
            self.start_time = time.time()
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                Bubble.bubbles.remove(self)
                return

            self.image = self.frames[self.frame_index]

class Enemy(GameSprite):
    def __init__(self, player_image, player_x, player_y, width, height, speed_x, speed_y):
        super().__init__(player_image, player_x, player_y, width, height)
        self.speed_x = speed_x
        self.speed_y = speed_y

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += smooth_sine(self.rect.x, amplitude=1, t_max=300)
        if self.rect.x > WIDTH:
            enemies.remove(self)
            global  max_enemies
            max_enemies += 1



matrix = []
player = Player('Images/fish_pink.png', WIDTH / 2, HEIGHT / 2, 50, 40, 0, 0, 3, 20)

BLOCK_SIZE = 50
WIDTH_BLOCK_COUNT = WIDTH // BLOCK_SIZE
HEIGHT_BLOCK_COUNT = HEIGHT // BLOCK_SIZE

# Инициализация матрицы правильными размерами
for y in range(HEIGHT_BLOCK_COUNT):
    matrix.append([])
    for x in range(WIDTH_BLOCK_COUNT):
        matrix[y].append('Images/background_terrain.png')

# Заполнение нижних строк - ПРАВИЛЬНЫЕ ИНДЕКСЫ
for x in range(WIDTH_BLOCK_COUNT):
    matrix[HEIGHT_BLOCK_COUNT - 1][x] = 'Images/terrain_dirt_a.png'

for x in range(WIDTH_BLOCK_COUNT):
    matrix[HEIGHT_BLOCK_COUNT - 2][x] = 'Images/terrain_sand_a.png'

print(f"Width: {WIDTH_BLOCK_COUNT}, Height: {HEIGHT_BLOCK_COUNT}")
pprint(matrix)

# Создание спрайтов - ПРАВИЛЬНЫЙ ПОРЯДОК ИНДЕКСОВ
sprite_matrix = []
for y in range(HEIGHT_BLOCK_COUNT):
    sprite_matrix.append([])
    for x in range(WIDTH_BLOCK_COUNT):
        sprite_matrix[y].append(GameSprite(
            player_image=matrix[y][x],
            player_x=BLOCK_SIZE * x,
            player_y=BLOCK_SIZE * y,
            width=BLOCK_SIZE,
            height=BLOCK_SIZE
        ))

bubble = Bubble(
    images=['Images/bubble_b.png', 'Images/bubble_a.png', 'Images/bubble_c.png'],
    bubble_x=WIDTH/2,
    bubble_y=HEIGHT/2,
    width=5,
    height=5,
    speed_y=1,
)
Bubble.bubbles.append(bubble)
max_enemies = 5
enemies = []

score_text = Label(5, 5, 0, 0, (0, 0, 0))
time_text = Label(WIDTH - 100, 5, 0, 0, (0, 0, 0))

score_text.set_text(f'Очки: {score}', fsize=12, text_color=(0, 0, 0))

game = True

x_go = 0
y_go = 0
start_time=time.time()
music.play()

while game:
    end_time = time.time()
    # window.blit(bc, (0, 0))

    if random.randint(0, 10) == 0:
        bubble = Bubble(
            images=['Images/bubble_b.png', 'Images/bubble_a.png', 'Images/bubble_c.png'],
            bubble_x=random.randint(0, WIDTH),
            bubble_y=random.randint(0, HEIGHT),
            width=random.uniform(0.5,1),
            height=random.uniform(0.5,1),
            speed_y=random.uniform(1,5),

        )
        Bubble.bubbles.append(bubble)
    if len(enemies) < max_enemies:
        size_kf = random.uniform(0.6, 1.2)
        enemy = Enemy(player_image=random.choice(config.enemies_images),
                      player_x=random.randint(-100, -50),
                      player_y=random.uniform(0, HEIGHT * 0.8),
                      width=35 * size_kf,
                      height=35 * size_kf,
                      speed_x=random.uniform(1,5),
                      speed_y=random.uniform(1,3),)

        enemies.append(enemy)

    # Отрисовка спрайтов
    for y in range(HEIGHT_BLOCK_COUNT):
        for x in range(WIDTH_BLOCK_COUNT):
            sprite_matrix[y][x].draw()

    player.draw()
    player.update()

    for bubble in Bubble.bubbles:
        bubble.draw()
        bubble.update()
    for enemy in enemies:
        enemy.draw()
        enemy.update()
        if pygame.sprite.collide_rect(player, enemy):
            enemies.remove(enemy)
            score += 1
            score_text.set_text(f'Очки: {score}', fsize=min(12 + score, 75), text_color=(0, 0, 0))

    time_text.set_text(f'Время: {round(end_time - start_time, 2)}', fsize=12, text_color=(0, 0, 0))

    if x_go != 0:
        if player.rect.x + player.rect.width/2 > x_go or player.rect.x + player.rect.width/2 < x_go:
           pass
        else:
            x_go = 0
        if player.rect.x + player.rect.width/2 > x_go:
            player.speed_x -= player.speed
            player.facing_right = False
        if player.rect.x + player.rect.width/2 < x_go:
            player.speed_x += player.speed
            player.facing_right = True
    if y_go != 0:
        if player.rect.y + player.rect.height / 2 > y_go or player.rect.y + player.rect.height / 2 < y_go:
            pass
        else:
            y_go = 0

        if player.rect.y + player.rect.height/2 > y_go:
            player.speed_y -= player.speed
        if player.rect.y + player.rect.height/2 < y_go:
            player.speed_y += player.speed

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            x_go, y_go = event.pos
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game = False

    score_text.draw()
    time_text.draw()

    pygame.display.update()
    clock.tick(60)
    