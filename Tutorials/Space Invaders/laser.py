import imp


import pygame

class Laser(pygame.sprite.Sprite):
    def __init__(self, pos, speed, y_constraint, color = 'white'):
        super().__init__()
        self.image = pygame.Surface((4, 20))
        self.image.fill(color)
        self.rect = self.image.get_rect(center = pos)
        self.speed = speed
        self.y_constraint = y_constraint
        self.test = 2

    def update(self):
        self.rect.y -= self.speed
        self.destroy()
    
    def destroy(self):
        if self.rect.bottom <= 0 or self.rect.top >= self.y_constraint:
            self.kill()