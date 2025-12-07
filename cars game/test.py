import pygame
from pygame import K_DOWN, K_UP, K_LEFT, K_RIGHT, K_ESCAPE

pygame.init()

WIDTH = 800
HEIGHT = 800
PLAYER_WIDTH = 100
PLAYER_HEIGHT = 1

clock = pygame.time.Clock()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('ЧЕРЕПАШКА ИГРА')

class Player:
    def __init__(self, image_path, x, y, speed):
        self.image = pygame.transform.scale(
            pygame.image.load(image_path),
            (PLAYER_WIDTH, PLAYER_HEIGHT)
        )
        self.x = x
        self.y = y
        self.speed = speed

    def update(self):
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[K_RIGHT]:
            self.x += self.speed
        if keys_pressed[K_LEFT]:
            self.x -= self.speed
        if keys_pressed[K_UP]:
            self.y -= self.speed  # Исправлено: вверх — уменьшение Y
        if keys_pressed[K_DOWN]:
            self.y += self.speed  # Исправлено: вниз — увеличение Y

    def draw(self):
        window.blit(self.image, (self.x, self.y))

# Укажите корректный путь к изображению
player = Player('Images/car.png', 100, 100, 3)

game = True

while game:
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game = False
        if event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
            game = False

    # Правильный порядок: сначала заливка, потом отрисовка
    player.draw()
    player.update()
    window.fill('green')


    pygame.display.update()
    clock.tick(60)

pygame.quit()