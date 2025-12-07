import os

backgrounds = os.listdir('Images/Backgrounds')

backgrounds_images = []

for background in backgrounds:
    path = f'Images/Backgrounds/{background}'
    images = os.listdir(path)
    for image in images:
        backgrounds_images.append(f'Images/Backgrounds/{background}/{image}')

player_images = []

players = os.listdir('images/player_img')

for image in players:
    player_image = f'Images/Player_img/{image}'
    player_images.append(player_image)

lasers_images = []
lasers = os.listdir(f'Images/Laser Sprites')

for laser in lasers:
    laser_path = f'Images/Laser Sprites/{laser}'
    lasers_images.append(laser_path)

en_images = []

enemies_images = os.listdir('Images/Enemies img')

for enemy_img in enemies_images:
    enemy_path = f'Images/Enemies img/{enemy_img}'
    en_images.append(enemy_path)
print(en_images)