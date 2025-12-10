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

