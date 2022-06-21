from xml.sax.handler import DTDHandler
from xmlrpc.client import Boolean
import pygame
from constants import *
from random import choice, randint

class Background(pygame.sprite.Sprite):
    def __init__(self, groups, ): # this sprite is added to the groups not the other way around
        super().__init__(groups)
        self.sprite_type = 'back_ground'

        day_or_night = choice(['day', 'night'])
        bg_image = pygame.image.load(f'Flappy Bird/images/background-{day_or_night}.png').convert() # doesnt need alpha/transparency
        
        # Aspect ratio of image = 9/16, window = 2/3 => almost the same
        bg_image = pygame.transform.scale(bg_image, (WINDOW_WIDTH, WINDOW_HEIGHT))

        # Surface with 3 times the image_width, and draw the same image twice
        self.image = pygame.Surface((2*WINDOW_WIDTH, WINDOW_HEIGHT))
        self.image.blit(bg_image, (0, 0))
        self.image.blit(bg_image, (WINDOW_WIDTH, 0))

        self.rect = self.image.get_rect(topleft = (0, 0))

        # Use a float variable to store postion, since rect's attribs only use integers -> rounding error
        self.pos = pygame.math.Vector2(self.rect.topleft)

    def update(self, dt):
        self.pos.x -= 150 * dt

        # Reset if center is out of screen
        if self.rect.centerx <= 0:
            self.pos.x = 0

        self.rect.x = round(self.pos.x) # round is better than int() since int() == floor()

class Ground(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.sprite_type = 'ground'

        # Image
        ground_image = pygame.image.load('Flappy Bird/images/base.png').convert_alpha()
        ground_image = pygame.transform.scale(ground_image, (WINDOW_WIDTH, ground_image.get_height()))
        self.image = pygame.Surface((WINDOW_WIDTH*2, ground_image.get_height()))
        self.image.blit(ground_image, (0, 0))
        self.image.blit(ground_image, (WINDOW_WIDTH, 0))
        # Rect
        self.rect = self.image.get_rect(bottomleft = (0, WINDOW_HEIGHT))
        self.pos = pygame.math.Vector2(self.rect.topleft)

    def update(self, dt):
        self.pos.x -= 200 * dt
        if self.rect.centerx <= 0:
            self.pos.x = 0
        
        self.rect.x = round(self.pos.x)

class Bird(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        
        self.sprite_type = 'bird'

        # Images, animation
        self.color = choice(['red', 'yellow', 'blue'])
        self.frames = self.import_frames()
        self.frame_index = 0
        self.image = self.frames[self.frame_index]

        # Rect
        self.rect = self.image.get_rect(midleft = (WINDOW_WIDTH//20, WINDOW_HEIGHT//2))
        self.pos = pygame.math.Vector2(self.rect.topleft)

        # Movement
        self.gravity = 600
        self.vy = 0 # velocity in y direction

        # Rotation
        self.rotation = 0

        # Mask for better collision
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.apply_gravity(dt)
        self.animate(dt)
        self.rotate(dt)

    def apply_gravity(self, dt):
        # free fall equation
        self.vy += self.gravity*dt
        # cap the falling velocity
        if self.vy >= UPPER_SPEED_LIMIT:
           self.vy = UPPER_SPEED_LIMIT
        falling_distance = self.vy*dt + self.gravity*0.5*dt*dt
        self.pos.y += falling_distance
        self.rect.y = round(self.pos.y)
    
    def animate(self, dt):
        # Increase the frame index by certain amount/speed of animation
        self.frame_index += 4 * dt
        self.image = self.frames[int(self.frame_index)%3]

    def rotate(self, dt):
        # Minus because the bird is falling, it should rotate clockwise
        # Possible bug: if falling too fast, can rotate in full circle
        self.image = pygame.transform.rotozoom(self.image, -self.vy*10*dt, 1)
        # need to update mask after rotatiing
        self.mask = pygame.mask.from_surface(self.image)

    def jump(self):
        # velocity will be decreased over time -> jump up some amount -> jump up a bit less ->..->start falling
        self.vy -= 400
        if self.vy <= LOWER_SPEED_LIMIT: # cap the velocity
            self.vy = LOWER_SPEED_LIMIT

    def import_frames(self):
        up_flap = pygame.image.load(f'Flappy Bird/images/{self.color}bird-upflap.png')
        mid_flap = pygame.image.load(f'Flappy Bird/images/{self.color}bird-midflap.png')
        down_flap = pygame.image.load(f'Flappy Bird/images/{self.color}bird-downflap.png')
        return [up_flap, mid_flap, down_flap]

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, groups, topleft, color: str, flip: Boolean):
        super().__init__(groups)

        self.sprite_type = 'obstacle'

        # Image
        pipe_image = pygame.image.load(f'Flappy Bird/images/pipe-{color}.png').convert_alpha() # up
        pipe_image = pygame.transform.scale(pipe_image, (pipe_image.get_width(), WINDOW_HEIGHT//2))
        if flip:
            pipe_image = pygame.transform.flip(pipe_image, False, True)
        self.image = pipe_image
        
        # Rect
        self.rect = self.image.get_rect(topleft = topleft)
          
        self.pos = pygame.math.Vector2(self.rect.topleft)


    
    def update(self, dt):
        self.pos.x -= PIPE_SPEED*dt
        self.rect.x = round(self.pos.x)
        # need to kill
        if self.rect.right <= 0:
            self.kill()
        
class ScoreBox(pygame.sprite.Sprite):
    def __init__(self, groups, show=False):
        super().__init__(groups)

        self.sprite_type = 'score_box'

        # Just for reference not rendering
        pipe_up_image = pygame.image.load('Flappy Bird/images/pipe-green.png').convert_alpha()
        width = pipe_up_image.get_width()

        # Surface
        self.image = pygame.Surface((width, WINDOW_HEIGHT), pygame.SRCALPHA).convert_alpha()
        if show:
            pygame.draw.rect(self.image, 'RED', (0, 0, self.image.get_width(), self.image.get_height()), 5)

        # Rect
        self.rect = self.image.get_rect(topleft = (WINDOW_WIDTH + width, 0)) # spawn right next to the right of the pipe pair
        self.pos = pygame.math.Vector2(self.rect.topleft)
        
    
    def update(self, dt):
        self.pos.x -= PIPE_SPEED*dt
        self.rect.x = round(self.pos.x)
        
        # Kill if pass the right of the window
        if self.rect.right <= 0:
            self.kill()

class GameoverMenu(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)

        self.sprite_type = 'gameover_menu'

        # Image
        self.image = pygame.image.load('Flappy Bird/images/gameover.png').convert_alpha()  

        # Rect
        self.rect = self.image.get_rect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2))