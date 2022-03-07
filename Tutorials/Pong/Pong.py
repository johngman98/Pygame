from itertools import count
from turtle import speed
import pygame
import sys
import random

# Classes
class Block(pygame.sprite.Sprite):
    # Use to read an image and make a rect out of it
    def __init__(self, path, x_pos, y_pos):
        super().__init__() # to call Sprite().__init__() and avoid using the inheriting class (base class) explicitly 
        self.image = pygame.image.load(path) # return a surface
        self.rect = self.image.get_rect(center = (x_pos, y_pos))

class Player(Block):
    def __init__(self, path, x_pos, y_pos, speed):
        super().__init__(path, x_pos, y_pos)
        self.speed = speed
        self.movement = 0

    def screen_constrain(self):
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
    
    def update(self, ball_group):
        self.rect.y += self.movement
        self.screen_constrain()

class Ball(Block):
    def __init__(self, path, x_pos, y_pos, speed_x, speed_y, paddles):
        super().__init__(path, x_pos, y_pos)
        self.speed_x = speed_x * random.choice((1, -1))
        self.speed_y = speed_y * random.choice((1, -1))
        self.paddles = paddles
        self.active = False
        self.score_time = 0

    def update(self):
        if self.active:
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
            self.collisions()
        else:
            self.restart_counter()

    def collisions(self):
        # Top and botoom collisions 
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            pygame.mixer.Sound.play(plob_sound)
            self.speed_y *= -1
        
        # Paddles collisions
        if pygame.sprite.spritecollide(self, self.paddles, False):
            pygame.mixer.Sound.play(plob_sound)
            # whichever paddle is collided, since only one can be collided at a time, it should be index 0
            collision_paddle = pygame.sprite.spritecollide(self, self.paddles, False)[0].rect 
            # only change dir if the distance between them less than 10 and ball's moving right
            if abs(self.rect.right - collision_paddle.left) < 10  and self.speed_x > 0:
                self.rect.right = collision_paddle.left
                self.speed_x *= -1
            # ball's moving left, and colliding with opponent
            if abs(self.rect.left - collision_paddle.right) < 10 and self.speed_x < 0:
                self.rect.left = collision_paddle.right
                self.speed_x *= -1
            # paddle's bottom collision
            if abs(self.rect.top - collision_paddle.bottom) < 10 and self.speed_y < 0:
                self.rect.top = collision_paddle.bottom
                self.speed_y *= -1
            # paddke's top collision
            if abs(self.rect.bottom - collision_paddle.top) < 10 and self.speed_y > 0:
                self.rect.bottom = collision_paddle.top
                self.speed_y *= -1
    def reset_ball(self):
        # Called once when the ball hit either left or right borders
        self.active = False
        self.speed_x *= random.choice((1, -1))
        self.speed_y *= random.choice((1, -1))
        self.score_time = pygame.time.get_ticks()
        self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        pygame.mixer.Sound.play(score_sound)
    
    def restart_counter(self):
        # Called everyframe if self.active is false
        current_time = pygame.time.get_ticks()
        countdown_number = 3

        if current_time - self.score_time <= 700:
            countdown_number = 3
        elif current_time - self.score_time <= 1400:
            countdown_number = 2
        elif current_time - self.score_time <= 2100:
            countdown_number = 1
        else: # > 2100ms
            self.active = True
        
        # Draw timer
        time_counter = basic_font.render(str(countdown_number), True, accent_color)
        time_counter_rect = time_counter.get_rect(center = (SCREEN_WIDTH/2 ,SCREEN_HEIGHT/2 - 50))
        pygame.draw.rect(screen, bg_color, time_counter_rect)
        screen.blit(time_counter, time_counter_rect)

class Opponent(Block):
    def __init__(self, path, x_pos, y_pos, speed):
        super().__init__(path, x_pos, y_pos)
        self.speed = speed
    def update(self, ball_group):
        if self.rect.top < ball_group.sprite.rect.y:
            self.rect.y += self.speed
        if self.rect.bottom > ball_group.sprite.rect.y:
            self.rect.y -= self.speed
        self.constraint()
    def constraint(self):
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

class GameManager:
    def __init__(self, ball_group, paddle_group):
        self.player_score = 0
        self.opponent_score = 0
        self.ball_group = ball_group
        self.paddle_group = paddle_group
    
    def run_game(self):
        # Drawing game object
        self.paddle_group.draw(screen)
        self.ball_group.draw(screen)

        # Updating the game objects
        self.paddle_group.update(self.ball_group)
        self.ball_group.update()
        self.reset_ball()
        self.draw_score()

    def reset_ball(self):
        if self.ball_group.sprite.rect.right >= SCREEN_WIDTH:
            self.opponent_score += 1
            self.ball_group.sprite.reset_ball()
        if self.ball_group.sprite.rect.left <= 0:
            self.player_score += 1
            self.ball_group.sprite.reset_ball()
    
    def draw_score(self):
        player_score = basic_font.render(str(self.player_score), True, accent_color)
        opponent_score = basic_font.render(str(self.opponent_score), True, accent_color)

        player_score_rect = player_score.get_rect(midleft = (SCREEN_WIDTH/ 2 + 40, SCREEN_HEIGHT /2))
        opponent_score_rect = opponent_score.get_rect(midleft = (SCREEN_WIDTH/ 2 - 40, SCREEN_HEIGHT /2))

        screen.blit(player_score, player_score_rect)
        screen.blit(opponent_score, opponent_score_rect)

# General setup
#pygame.mixer.pre_init() # no need, all default arguments are properly set
pygame.init()
clock = pygame.time.Clock()

# Setting up the main window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Pong')

# Game rectangle
middle_strip = pygame.Rect(SCREEN_WIDTH/2 - 2, 0, 4, SCREEN_HEIGHT)

# Colors
bg_color = pygame.Color('#2F373F') # pygame color object
accent_color = (27, 35, 43) # user-defined color values

# Everything text
player_score = 0
opponent_score = 0
basic_font = pygame.font.Font('freesansbold.ttf', 32)


# Movement's attrib
player_speed = 0
opponent_speed = 7
score_time = 1 # Start with 1 or True so the countdown start

# Sound
plob_sound = pygame.mixer.Sound('sound/pong.ogg')
score_sound = pygame.mixer.Sound('sound/score.ogg')

# Instancing
player = Player('images/Paddle.png', SCREEN_WIDTH - 20, SCREEN_HEIGHT/2, 5)
opponent = Opponent('images/Paddle.png',  20, SCREEN_HEIGHT/2, 5)
paddle_group = pygame.sprite.Group()
paddle_group.add(player)
paddle_group.add(opponent)

ball = Ball('images/Ball.png', SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 4, 4, paddle_group)
ball_sprite = pygame.sprite.GroupSingle()
ball_sprite.add(ball)

game_manager = GameManager(ball_sprite, paddle_group)

while True:
    # Handling input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                player.movement += player.speed
            if event.key == pygame.K_UP:
                player.movement -= player.speed
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                player.movement -= player.speed
            if event.key == pygame.K_UP:
                player.movement += player.speed



    # Visuals
    screen.fill(bg_color)
    pygame.draw.rect(screen, accent_color, middle_strip)
    
    game_manager.run_game()

    # Update the window
    pygame.display.flip() # same as using update() with not arguments
    # Wait until this frame take 1/60s -> 60 FPS
    clock.tick(60)