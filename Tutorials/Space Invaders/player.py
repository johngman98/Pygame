import pygame
from laser import Laser

''' Requirements:
1. Show an image of player
2. Move the player
3. Constraint player in the game window
4. Shoot a laser and recharge (timer)
'''

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, x_constraint, speed):
        super().__init__()
        self.image = pygame.image.load('Space Invaders/images/player.png').convert_alpha()
        self.rect = self.image.get_rect(midbottom = pos)
        self.speed = speed
        self.x_constraint = x_constraint
        self.ready_to_shoot = True
        self.laser_time = 0 # to store the moment the laser is shot, or time stamp the previous shot
        self.laser_cooldown = 400 # 600ms
        self.lasers = pygame.sprite.Group()
        self.laser_sound = pygame.mixer.Sound('Space Invaders/audio/laser.wav')
        self.laser_sound.set_volume(0.15)
    
    def update(self, screen):
        self.get_input(screen)
        self.check_constraint()
        self.recharge()
        self.lasers.update()
    
    def get_input(self, screen):
        keys = pygame.key.get_pressed()
        
        # movemonet
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        elif keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        
        # shooting
        if keys[pygame.K_SPACE] and self.ready_to_shoot:
            self.shoot_laser()
            self.ready_to_shoot = False
            self.laser_time = pygame.time.get_ticks() 
            self.laser_sound.play()

    def check_constraint(self):
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= self.x_constraint:
            self.rect.right = self.x_constraint

    def shoot_laser(self):
        self.lasers.add(Laser(self.rect.center, 8, self.rect.bottom)) # player bottom is always at the bottom of the screen

    def recharge(self):
        # to reset the self.ready_to_shoot state to true
        if not self.ready_to_shoot:
            curr_time = pygame.time.get_ticks()
            if curr_time - self.laser_time >= self.laser_cooldown:
                self.ready_to_shoot = True

    
