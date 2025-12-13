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

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Space Shoter')