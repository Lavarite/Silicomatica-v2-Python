import pygame

from classes.inventory import Inventory


class Player:
    def __init__(self, x, y, id=0):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.inventory = Inventory()
        self.color = (100, 100, 200)
        self.id = id
