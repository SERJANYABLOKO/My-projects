import pygame
import PIL
from PIL import Image
from pygame import Surface

pygame.init()

WIDTH = 800
HEIGHT = 800
PLAYER_WIDTH = 160
PLAYER_HEIGHT = 65

clock = pygame.time.Clock()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('ЧЕРЕПАШКА ИГРА')

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

        rect = pygame.Rect(self.rect.x + self.speed_x, self.rect.y + self.speed_y, self.rect.width, self.rect.height)
        # pygame.draw.rect(window, (255, 0, 0), rect)
        is_collide = False
        for wall in walls:
            if rect.colliderect(wall):
                is_collide = True
                break

        if not is_collide:
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

class Enemy(GameSprite):
    def __init__(self, player_image, player_x, player_y, width, height, speed_x, speed_y):
        super().__init__(player_image, player_x, player_y, width, height)
        self.speed_x = speed_x
        self.speed_y = speed_y
    def draw(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Wall(pygame.sprite.Sprite):
    def __init__(self, color, wall_x, wall_y, wall_width, wall_height):
        super().__init__()
        self.color = color
        self.width = wall_width
        self.height = wall_height
        self.image = Surface((self.width, self.height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = wall_x
        self.rect.y = wall_y
    def draw_wall(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


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

game = True

player = Player('Images/car.png', 100, 100, 100, 50, 5, 5, 5, 10)
enemy = Enemy(  'Images/img.png', 300, 300, 100, 50, 5, 5)

lose_text = Label(200, 200, 800, 400, (200, 0, 0))
lose_text.set_text('Вы проиграли', 80, )

walls = [
    Wall((200, 0, 255), 400, 400, 10, 200),
    Wall((200, 0, 0), 400, 500, 200, 10),
    Wall((200, 0, 0), 200, 100, 200, 15),
    Wall((200, 0, 0), 150, 300, 140, 10),
    Wall((200, 0, 0), 600, 350, 270, 10),
    Wall((200, 0, 0), 800, 450, 200, 10),
    Wall((200, 0, 0), 100, 600, 200, 10)
]




while game:
    window.fill('gray')
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game = False
        if event.type == pygame.K_ESCAPE:
            game = False
    if pygame.sprite.collide_rect(player, enemy):
        lose_text.draw()
        player.speed = 0
        player.speed_y = 0
        player.speed_x = 0

    enemy.draw()
    player.draw()
    player.update()
    for wall in walls:
        wall.draw_wall()

    pygame.display.update()
    clock.tick(60)
