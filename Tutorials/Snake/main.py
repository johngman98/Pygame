from turtle import Vec2D
import pygame
import sys
import random
from pygame.math import Vector2

class Fruit:
    def __init__(self):
        self.randomize()
        self.apple = pygame.image.load('Snake/images/apple.png').convert_alpha() # faster !? maybe

    def draw(self):
        fruit_rect = pygame.Rect(int(self.pos.x * cell_size), int(self.pos.y * cell_size), cell_size, cell_size)
        screen.blit(self.apple, fruit_rect)
        #pygame.draw.rect(screen, (126, 166, 114), fruit_rect)
    
    def randomize(self):
        self.x = random.randint(0, cell_number - 1)
        self.y = random.randint(0, cell_number - 1)
        self.pos = Vector2(self.x, self.y)

class Snake:
    def __init__(self):
        self.body = [Vector2(5, 10), Vector2(4, 10), Vector2(3, 10)]
        self.direction = Vector2(0, 0)
        self.new_block = False

        # textures for snake
        self.head_up =  pygame.image.load('Snake/images/head_up.png').convert_alpha()
        self.head_down =  pygame.image.load('Snake/images/head_down.png').convert_alpha()
        self.head_right =  pygame.image.load('Snake/images/head_right.png').convert_alpha()
        self.head_left =  pygame.image.load('Snake/images/head_left.png').convert_alpha()
        
        self.tail_up =  pygame.image.load('Snake/images/tail_up.png').convert_alpha()
        self.tail_down =  pygame.image.load('Snake/images/tail_down.png').convert_alpha()
        self.tail_right =  pygame.image.load('Snake/images/tail_right.png').convert_alpha()
        self.tail_left =  pygame.image.load('Snake/images/tail_left.png').convert_alpha()

        self.body_horizontal =  pygame.image.load('Snake/images/body_horizontal.png').convert_alpha()
        self.body_vertical =  pygame.image.load('Snake/images/body_vertical.png').convert_alpha()

        self.body_tr =  pygame.image.load('Snake/images/body_tr.png').convert_alpha()
        self.body_tl =  pygame.image.load('Snake/images/body_tl.png').convert_alpha()
        self.body_br =  pygame.image.load('Snake/images/body_br.png').convert_alpha()
        self.body_bl =  pygame.image.load('Snake/images/body_bl.png').convert_alpha()
        
        # sound
        self.crunch_sound = pygame.mixer.Sound('Snake/sounds/Sound_crunch.wav')
    def draw(self):
        for index, block in enumerate(self.body):
            # Rect for positioning
            x_pos = int(block.x * cell_size)
            y_pos = int(block.y * cell_size)
            block_rect = pygame.Rect(x_pos, y_pos, cell_size, cell_size)
            
            # Figure out directions of snake's parts
            # head
            if index == 0:
                head = self.head_right # emoty surface
                if self.direction.x == 1:
                    head = self.head_right
                elif self.direction.x == -1:
                    head = self.head_left 
                elif self.direction.y == 1:
                    head = self.head_down
                elif self.direction.y == -1:
                    head = self.head_up
                screen.blit(head, block_rect)
            # tail
            elif index == len(self.body) - 1:
                tail = None
                tail_vect = self.body[-1] - self.body[-2] # tail vector
                if tail_vect.x == 1:
                    tail = self.tail_right
                elif tail_vect.x == -1:
                    tail = self.tail_left
                if tail_vect.y == 1:
                    tail = self.tail_down
                elif tail_vect.y == -1:
                    tail = self.tail_up
                screen.blit(tail, block_rect)
            # the rest of the body
            else:
                block_sur = None
                # vector from prev block (smaller index, close to head) to curr block
                prev_vect = block - self.body[index - 1]
                # vector from curr to next block(bigger index, close to tail)
                next_vect = self.body[index + 1] - block
                # horizontal
                if prev_vect.x == next_vect.x == 0:
                    block_sur = self.body_vertical
                # vertical
                elif prev_vect.y == next_vect.y == 0:
                    block_sur = self.body_horizontal
                # top left
                #   *
                # * *  
                # go from left to right then up or top to bottom then right
                elif (prev_vect.y == 1 and next_vect.x == -1) or (prev_vect.x == 1 and next_vect.y == -1):
                    block_sur = self.body_tl
                # bottom right
                # * *
                # *
                elif (prev_vect.x == -1 and next_vect.y == 1) or (prev_vect.y == -1 and next_vect.x == 1):
                    block_sur = self.body_br
                # top right
                # *
                # * *
                elif (prev_vect.y == 1 and next_vect.x == 1) or (prev_vect.x == -1 and next_vect.y == -1):
                    block_sur = self.body_tr
                # bottom left
                # * *
                #   *
                elif (prev_vect.x == 1 and next_vect.y == 1) or (prev_vect.y == -1 and next_vect.x == -1):
                    block_sur = self.body_bl
                
                screen.blit(block_sur, block_rect)

        # no texture just one-colored block
        # for block in self.body:
        #     x_pos = int(block.x * cell_size)
        #     y_pos = int(block.y * cell_size)
        #     block_rect = pygame.Rect(x_pos, y_pos, cell_size, cell_size)
        #     pygame.draw.rect(screen, (183, 111, 122), block_rect)
    
    def move(self):
        if self.new_block == True:
            # copy the whole body
            body_copy = self.body[:]
            self.new_block = False
        else:
            body_copy = self.body[:-1]

        body_copy.insert(0, self.body[0] + self.direction)
        self.body = body_copy[:] # deep-ish copy

    def add_block(self):
        self.new_block = True
    
    def play_crunch_sound(self):
        self.crunch_sound.play()

    def reset(self):
        self.body = [Vector2(5, 10), Vector2(4, 10), Vector2(3, 10)]
        self.direction = Vector2(0, 0)

class Main:
    def __init__(self):
        self.snake = Snake()
        self.fruit = Fruit()
    
    def update(self):
        # update movement every 150ms
        self.snake.move()
        self.check_collision()
        self.check_fail()
    
    def draw(self): 
        # draw every 1/60 s
        self.draw_grass()
        self.snake.draw()
        self.fruit.draw()
        self.draw_score()

    def check_collision(self):
        if self.fruit.pos == self.snake.body[0]:
            # reposition the fruit
            self.fruit.randomize()
            # increase the length of the snake
            self.snake.add_block()
            self.snake.play_crunch_sound()

        # check case where fruit spawn inside the snake
        for block in self.snake.body[1:]:
            if block == self.fruit.pos:
                self.fruit.randomize()

    def check_fail(self):
        # Check bounds
        if (not 0 <= self.snake.body[0].x < cell_number*2) or (not 0 <= self.snake.body[0].y < cell_number):
            self.game_over()
        
        # Check if snake hits itself, only need to check if the other parts collide the head or not
        for block in self.snake.body[1:]:
            if block == self.snake.body[0]:
                self.game_over()

    def game_over(self):
        self.snake.reset()

    def draw_grass(self):
        grass_color = (167, 209, 61)
        for row in range(cell_number):
            for col in range(cell_number * 2):
                # only draw if both of row and col are odd or even
                if not row%2 ^ col%2: # or (x%2 == 0 and y%2 == 0) or (x%2 == 1 and y%2==1)
                    grass_rect = pygame.Rect(col * cell_size, row*cell_size, cell_size, cell_size)
                    pygame.draw.rect(screen, grass_color, grass_rect)
    
    def draw_score(self):
        score_str = str(len(self.snake.body) - 3)
        score_surface = game_font.render(score_str, True, (56, 74, 12))
        score_x = int(cell_size * cell_number * 2 - 60)
        score_y = int(cell_size * cell_number - 40)
        score_rect = score_surface.get_rect(center = (score_x, score_y))
        apple_rect = self.fruit.apple.get_rect(midright = (score_rect.midleft))
        bg_rect = pygame.Rect(apple_rect.left, apple_rect.top, 
        apple_rect.width + score_rect.width + 10, apple_rect.height)
        
        pygame.draw.rect(screen, (167, 100, 61), bg_rect)
        screen.blit(score_surface, score_rect)
        screen.blit(self.fruit.apple, apple_rect)
        pygame.draw.rect(screen, (56, 74, 12), bg_rect, width=2) #bbox
        
         
pygame.init()
cell_size = 40
cell_number = 15
screen = pygame.display.set_mode((cell_size * cell_number * 2, cell_size * cell_number))
clock = pygame.time.Clock()
game_font = pygame.font.Font('Snake/font/PoetsenOne-Regular.ttf', 25)

main_game = Main()

# Timer
SCREEN_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SCREEN_UPDATE, 150) # event is broadcast every 150ms

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit() # somtimes doesnt close everything
            sys.exit()
        if event.type == SCREEN_UPDATE:
            main_game.update()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and main_game.snake.direction.y != 1:
                main_game.snake.direction = Vector2(0, -1)
            if event.key == pygame.K_DOWN and main_game.snake.direction.y != -1:
                main_game.snake.direction = Vector2(0, 1)
            if event.key == pygame.K_RIGHT and main_game.snake.direction.x != -1:
                main_game.snake.direction = Vector2(1, 0)
            if event.key == pygame.K_LEFT and main_game.snake.direction.x != 1:
                main_game.snake.direction = Vector2(-1, 0)
            
    screen.fill((175, 215, 70))
    main_game.draw()
    pygame.display.update()
    clock.tick(60)
    
   