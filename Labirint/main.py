import pygame
from random import *

# Initialize pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 800
BLOCK_SIZE = 50
WIDTH_BLOCK_COUNT = WIDTH // BLOCK_SIZE
HEIGHT_BLOCK_COUNT = HEIGHT // BLOCK_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)

# Create window
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Enhanced Maze Game')
clock = pygame.time.Clock()

# Font for score display
font = pygame.font.SysFont('Arial', 24)


class GameSprite(pygame.sprite.Sprite):
    def __init__(self, color, player_x, player_y, size_x, size_y):
        super().__init__()
        self.image = pygame.Surface((size_x, size_y))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def draw(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


class Player(GameSprite):
    def __init__(self, x, y):
        super().__init__((0, 100, 200), x, y, BLOCK_SIZE - 10, BLOCK_SIZE - 10)
        self.speed = 5
        self.score = 0

    def update(self, walls):
        keys = pygame.key.get_pressed()
        new_x, new_y = self.rect.x, self.rect.y

        if keys[pygame.K_LEFT]:
            new_x -= self.speed
        if keys[pygame.K_RIGHT]:
            new_x += self.speed
        if keys[pygame.K_UP]:
            new_y -= self.speed
        if keys[pygame.K_DOWN]:
            new_y += self.speed

        # Create a temporary rect for collision detection
        temp_rect = self.rect.copy()
        temp_rect.x = new_x
        temp_rect.y = new_y

        # Check for collisions with walls
        collision = False
        for wall in walls:
            if temp_rect.colliderect(wall.rect):
                collision = True
                break

        # Only update position if no collision
        if not collision:
            self.rect.x = new_x
            self.rect.y = new_y

        # Keep player within screen bounds
        self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, HEIGHT - self.rect.height))


class Coin(GameSprite):
    def __init__(self, x, y):
        super().__init__(GOLD, x, y, 15, 15)
        self.collected = False


# Create the game matrix
matrix = []
for x in range(WIDTH_BLOCK_COUNT):
    matrix.append([])
    for y in range(HEIGHT_BLOCK_COUNT):
        matrix[x].append(0)

# Create terrain
for x in range(WIDTH_BLOCK_COUNT):
    for y in range(HEIGHT_BLOCK_COUNT):
        matrix[x][y] = GameSprite(GREEN, 0 + BLOCK_SIZE * x, 0 + BLOCK_SIZE * y, BLOCK_SIZE, BLOCK_SIZE)

# Create ground
for x in range(WIDTH_BLOCK_COUNT):
    matrix[x][HEIGHT_BLOCK_COUNT - 1] = GameSprite(BROWN, 0 + BLOCK_SIZE * x, 0 + BLOCK_SIZE * (HEIGHT_BLOCK_COUNT - 1),
                                                   BLOCK_SIZE, BLOCK_SIZE)
    matrix[x][HEIGHT_BLOCK_COUNT - 2] = GameSprite((210, 180, 140), 0 + BLOCK_SIZE * x,
                                                   0 + BLOCK_SIZE * (HEIGHT_BLOCK_COUNT - 2), BLOCK_SIZE, BLOCK_SIZE)

# Create walls
walls = []
# Border walls
for x in range(WIDTH_BLOCK_COUNT):
    walls.append(GameSprite(BLACK, x * BLOCK_SIZE, 0, BLOCK_SIZE, BLOCK_SIZE))
    walls.append(GameSprite(BLACK, x * BLOCK_SIZE, HEIGHT - BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
for y in range(HEIGHT_BLOCK_COUNT):
    walls.append(GameSprite(BLACK, 0, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    walls.append(GameSprite(BLACK, WIDTH - BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

# Random interior walls
for _ in range(50):
    x = randint(1, WIDTH_BLOCK_COUNT - 2)
    y = randint(1, HEIGHT_BLOCK_COUNT - 2)
    walls.append(GameSprite(BLACK, x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

# Create player
player = Player(BLOCK_SIZE, BLOCK_SIZE)

# Create coins
coins = []
for _ in range(20):
    valid_position = False
    while not valid_position:
        x = randint(1, WIDTH_BLOCK_COUNT - 2) * BLOCK_SIZE + BLOCK_SIZE // 2 - 7
        y = randint(1, HEIGHT_BLOCK_COUNT - 2) * BLOCK_SIZE + BLOCK_SIZE // 2 - 7

        # Check if coin position doesn't collide with walls
        coin_rect = pygame.Rect(x, y, 15, 15)
        collision = False
        for wall in walls:
            if coin_rect.colliderect(wall.rect):
                collision = True
                break

        if not collision:
            valid_position = True
            coins.append(Coin(x, y))

# Game loop
game = True
while game:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game = False

    # Update
    player.update(walls)

    # Check for coin collection
    for coin in coins:
        if not coin.collected and player.rect.colliderect(coin.rect):
            coin.collected = True
            player.score += 10

    # Draw everything
    window.fill(WHITE)

    # Draw terrain
    for y in range(HEIGHT_BLOCK_COUNT):
        for x in range(WIDTH_BLOCK_COUNT):
            matrix[x][y].draw()

    # Draw walls
    for wall in walls:
        wall.draw()

    # Draw coins
    for coin in coins:
        if not coin.collected:
            coin.draw()

    # Draw player
    player.draw()

    # Draw score
    score_text = font.render(f'Score: {player.score}', True, BLACK)
    window.blit(score_text, (10, 10))

    # Check if all coins are collected
    if all(coin.collected for coin in coins):
        win_text = font.render('You Win! All coins collected!', True, BLACK)
        window.blit(win_text, (WIDTH // 2 - 150, HEIGHT // 2))

    pygame.display.update()
    clock.tick(60)

pygame.quit()