from pickle import FALSE
from random import randint, choice
import pygame
import sys
import time
from constants import *
from sprites import Background, Ground, Bird, Obstacle, ScoreBox, GameoverMenu

class Game:
    '''
        Tasks:
            1. Initialize and setup everything that needed
            2. Update states of objects
            3. Render/draw everyhing
    '''

    def __init__(self):
        # Init pygame
        pygame.init()

        # Screen/display/Window
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Flappy Bird')

        # Clock
        self.clock = pygame.time.Clock()

        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.score_boxes = pygame.sprite.Group()

        # Sprite setup
        Background(self.all_sprites)
        Ground([self.all_sprites, self.collision_sprites])
        self.bird = Bird(self.all_sprites)

        # Obstacles spawn event
        self.obstacle_spawn_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.obstacle_spawn_event, 1000 + randint(-100, 200)) # 1200ms

        # Text
        self.font = pygame.font.Font('Flappy Bird/fonts/BD_Cartoon_Shout.ttf', 30)
        self.score = 0

        # Game states
        self.active = True

    def run(self):
        last_time = time.time()
        while True:

            # Delta time
            curr_time = time.time()
            dt = curr_time - last_time
            last_time = curr_time
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if self.active:
                        self.bird.jump()
                    else:
                        self.reset()

                if event.type == self.obstacle_spawn_event and self.active:
                    self.spawn_obstacles()

            # Update and check collision if gamestate is active
            if self.active:
                self.all_sprites.update(dt)
                self.check_collision()

            # Draw
            self.display_surface.fill('black')
            self.all_sprites.draw(self.display_surface)
            self.display_score()

            # Update the screen/display and its frame rate
            pygame.display.update()
            self.clock.tick(FRAMERATE)
    
    def spawn_obstacles(self):
        gap = 100 + randint(0, 25)
        gap_up = randint(0, gap) # from middle window to pipe up
        gap_down = gap - gap_up

        color = choice(['green', 'red'])

        Obstacle([self.all_sprites, self.collision_sprites], 
                            topleft=(WINDOW_WIDTH, WINDOW_HEIGHT/2 + gap_up), 
                            color=color,
                            flip=False)
        Obstacle([self.all_sprites, self.collision_sprites], 
                            topleft=(WINDOW_WIDTH, 0 - gap_down),
                            color=color,
                            flip=True)
        
        # score box
        ScoreBox([self.all_sprites, self.score_boxes], show = False) # show True if want to see score box
        #print(len(self.all_sprites.sprites())) #-> shouldnt spawn more if state is not active

    def check_collision(self):
        if pygame.sprite.spritecollide(self.bird, self.collision_sprites, False, pygame.sprite.collide_mask)\
        or self.bird.rect.top <= 0:
            self.active = False
            GameoverMenu(self.all_sprites)

        if pygame.sprite.spritecollide(self.bird, self.score_boxes, True): # shouldnt use collide_mask for insible rect
            self.score += 1

    def display_score(self):
        score_str = str(self.score)
        x = WINDOW_WIDTH/2
        y = WINDOW_HEIGHT//10
        if  not self.active:
            y = WINDOW_HEIGHT/2 + 50
            score_str = 'SCORE: ' + score_str

            reset_surf = self.font.render(str('Press SPACE to RESET'), True, 'black')
            reset_rect = reset_surf.get_rect(midtop = (x, y + 50))
            self.display_surface.blit(reset_surf, reset_rect)


        score_surf = self.font.render(str(score_str), True, 'black')
        score_rect = score_surf.get_rect(midtop = (x, y))
        self.display_surface.blit(score_surf, score_rect)

        
    def reset(self):
        self.active = True

        # Kill everything, for some reason use .remove() doesnt work
        for sprite in self.all_sprites.sprites():
            sprite.kill()

        #`print(len(self.all_sprites.sprites()))
          
        # New background
        Background(self.all_sprites)
        # Ground
        Ground([self.all_sprites, self.collision_sprites])
        # New bird
        self.bird = Bird(self.all_sprites)
        # Reset score
        self.score = 0



if __name__ == '__main__':
    game = Game()
    game.run()