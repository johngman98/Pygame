import enum
from math import gamma
from os import system
from random import choice, randint
import pygame
import sys
from player import Player
import obstacle
from alien import Alien, ExtraAlien
from laser import Laser

class Game:
    def __init__(self):
        # PLayer setup
        player_sprite = Player((screen_width//2, screen_height), screen_width, 5)
        self.player = pygame.sprite.GroupSingle(player_sprite)

        # Obstacle setup
        self.ostacle_shape = obstacle.shape
        self.block_size = 6
        self.blocks = pygame.sprite.Group()
        self.num_obstacles = 4 # maximum number of obstables fit the screen: screen_width / (block_size * 11), 11 block is the length of ostacle
        self.create_multiple_obstacles(self.cal_obstacle_x_offsets(), x_start=0, y_start=480)

        # Alien setup
        self.aliens = pygame.sprite.Group()
        self.aliens_setup(6, 8)
        self.aliens_direction = 1 # all aliens move at the same direction
        self.aliens_lasers = pygame.sprite.Group()
        self.aliens_shoot_last_time = pygame.time.get_ticks()
        self.aliens_shoot_interval = 800 # 800ms

        # Extra alien
        self.extra_alien = pygame.sprite.GroupSingle()
        self.extra_alien.add(ExtraAlien(choice(['left', 'right']), screen_width))
        self.extra_alien_spawn_time = randint(400, 800) # unit is frames

        # Lives
        self.lives = 3
        self.lives_surface = pygame.image.load('Space Invaders/images/player.png').convert_alpha()
        self.lives_surface = pygame.transform.scale(self.lives_surface, (self.lives_surface.get_width()*0.75, 
                                                                        self.lives_surface.get_height()*0.75))
        
        # Score
        self.score = 0
        self.font = pygame.font.Font('Space Invaders/font/Pixeled.ttf', 20)

        # CRT screen overlay
        self.crt = pygame.image.load('Space Invaders/images/tv.png').convert_alpha()
        # make sure overlay always same size as screen
        self.crt = pygame.transform.scale(self.crt, (screen_width, screen_height))

        # Audio
        # back ground music
        music = pygame.mixer.Sound('Space Invaders/audio/music.wav')
        music.set_volume(0.1)
        music.play(loops=-1)
        # laser and explosion sound
        self.laser_sound = pygame.mixer.Sound('Space Invaders/audio/laser.wav')
        self.laser_sound.set_volume(0.15)
        self.explosion_sound = pygame.mixer.Sound('Space Invaders/audio/explosion.wav')
        self.explosion_sound.set_volume(0.3)


    def run(self):
        # Update all sprite groups
        self.player.update(screen)
        self.aliens.update(self.aliens_direction)
    
         # Check statuses if need to, other stuff go here too
        self.check_aliens_position()
        self.alien_shoot()
        self.aliens_lasers.update()

        # Extra alien
        self.extra_alien_timer()
        self.extra_alien.update()

        # Collisions
        self.check_collisions()

        # Draw all sprite groups, should be LAST
        self.player.sprite.lasers.draw(screen) # call sprite property from player (groupd single) player_sprite is not a member
        self.player.draw(screen)
        self.blocks.draw(screen)
        self.aliens.draw(screen)
        self.aliens_lasers.draw(screen)
        self.extra_alien.draw(screen)
        self.display_lives()
        self.display_score()
        self.enable_crt()

        # win
        self.check_win()
     
    def create_obstacle(self, x_start, y_start):
        for row_index, row in enumerate(self.ostacle_shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    x = x_start + self.block_size * col_index
                    y = y_start + self.block_size * row_index
                    block = obstacle.Block(self.block_size, (241, 79, 90), x, y)
                    self.blocks.add(block)

    def create_multiple_obstacles(self, offsets, x_start, y_start):
        # All obstacles have the same y, but diff x values
        for x in offsets:
            self.create_obstacle(x_start + x, y_start)
    
    
    def cal_obstacle_x_offsets(self):
        obstacle_width = self.block_size * 11 # 11 blocks -> see obstacle
        offsets =  [x * (screen_width/self.num_obstacles) for x in range(self.num_obstacles)]
        # make everything in the middle, everything + distance of the right side of the last obstacle
        return [x + (screen_width - offsets[-1] - obstacle_width)/2 for x in offsets]

    def aliens_setup(self, rows, cols, x_distance = 60, y_distance = 48, x_offset = 70, y_offset = 100):
        for row in range(rows):
            for col in range(cols):
                x = col * x_distance + x_offset
                y = row * y_distance + y_offset
                
                color = ''
                if row == 0: color = 'yellow'
                elif 1 <= row <= 2: color = 'green'
                else: color = 'red'

                alien_sprite = Alien(color, x, y)
                self.aliens.add(alien_sprite)
    
    def check_aliens_position(self):
        all_aliens = self.aliens.sprites()

        # Should check all the sprites cause u can destroy aliens
        for alien in all_aliens:
            if alien.rect.right >= screen_width:
                self.aliens_direction = -1
                # Move down, can have problem if there are no aliens left
                self.move_aliens_down(2)
                
            elif alien.rect.left <= 0:
                self.aliens_direction = 1
                self.move_aliens_down(2)

    def move_aliens_down(self, distance):
        for alien in self.aliens.sprites(): # already cover empty case
            alien.rect.y += distance

    def alien_shoot(self):
        # Only one random alien shoot
        all_aliens = self.aliens.sprites()
        # check timer
        curr = pygame.time.get_ticks()
        if all_aliens and curr - self.aliens_shoot_last_time >= self.aliens_shoot_interval: # deal with empty case
            random_alien = choice(all_aliens)
            laser_sprite = Laser(random_alien.rect.center, -6, screen_height, color = 'red')
            self.aliens_lasers.add(laser_sprite)
            self.aliens_shoot_last_time = curr
            # sound
            self.laser_sound.play()
        
        
    def extra_alien_timer(self):
        self.extra_alien_spawn_time -= 1 # decrease every frame => 400 frames * 3 = 1200 units
        if self.extra_alien_spawn_time <= 0:
            self.extra_alien.add(ExtraAlien(choice(['left', 'right']), screen_width))
            self.extra_alien_spawn_time = randint(400, 800)
    
    def check_collisions(self):
        # call between after updates positons and before drawing

        # Collsions between player's laser and other
        for laser in self.player.sprite.lasers:
            # obstacles
            if pygame.sprite.spritecollide(laser, self.blocks, True):
                laser.kill()
            # alien
            aliens_hit_list = pygame.sprite.spritecollide(laser, self.aliens, True)
            if aliens_hit_list:
                laser.kill()
                self.score += aliens_hit_list[0].value # the laser can only hit one alien anyway
                self.explosion_sound.play()
            # extra alien
            if pygame.sprite.spritecollide(laser, self.extra_alien, True):
                laser.kill()
                self.score += 500
                self.explosion_sound.play()
                
            
        # Collision between aliens' lasers and others
        for laser in self.aliens_lasers:
            # obstacles
            if pygame.sprite.spritecollide(laser, self.blocks, True):
                laser.kill()
            # player, DONOT kill the player sprite
            if pygame.sprite.spritecollide(laser, self.player, False):
                laser.kill()
                self.lives -= 1
                if self.lives <= 0:
                    print('Game Over')
                    pygame.quit()
                    sys.exit()

        # Collision between aliens and other
        for alien in self.aliens:
            # Obstacles
            if pygame.sprite.spritecollide(alien, self.blocks, True):
                pass
            # Player, DONOT kill the player sprite
            if pygame.sprite.spritecollide(alien, self.player, False):
                print('Game Over')
                pygame.quit()
                sys.exit()

    def display_lives(self):
        for live in range(self.lives - 1):
        # only display 2 lives, player can have 0 live -> last one 
            x = screen_width - (live + 1) * (self.lives_surface.get_width() + 10)
            screen.blit(self.lives_surface, (x, 8)) # y is just some arbitrary number

    def display_score(self):
        score_font = self.font.render(f'Score: {self.score}', True, 'white')
        screen.blit(score_font, (0, -20))

    def enable_crt(self):
        # flickering effect
        self.crt.set_alpha(randint(75, 90)) 
        # lines effect
        line_height = 3
        line_amount = screen_width//line_height
        for line in range(line_amount):
            y = line * line_height
            # actually line is 1 unit thick and black that is inside a 3 units rectangle
            pygame.draw.line(self.crt, 'black', (0, y), (screen_width, y), 1)
        screen.blit(self.crt, (0, 0))

    def check_win(self):
        if not self.aliens.sprites():
            victory_msg = self.font.render('You won', False, 'white')
            victory_msg_rect = victory_msg.get_rect(center = (screen_width/2, screen_height/2))
            screen.blit(victory_msg, victory_msg_rect)

if __name__ == '__main__':
    pygame.init()
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Space Invaders')

    clock = pygame.time.Clock()
    game = Game()
    # overlay to look like crt tv
 

    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        screen.fill((30, 30, 30))
        game.run()
        pygame.display.flip()
        clock.tick(60)