import pygame
import random
import time
import csv
import os
from pygame.locals import *

# VARIABLES
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 10
GRAVITY = 1
GAME_SPEED = 10

GROUND_WIDTH = 2 * SCREEN_WIDTH
GROUND_HEIGHT = 100

PIPE_WIDTH = 80
PIPE_HEIGHT = 500
PIPE_GAP = 200

wing = 'assets/audio/wing.wav'
hit = 'assets/audio/hit.wav'

def show_score(screen, score, font):
    score_surface = font.render(f'Score: {score}', True, (255, 255, 255))
    screen.blit(score_surface, (SCREEN_WIDTH - score_surface.get_width() - 10, 10))

def update_training_data(data):
    file_name = 'training_data.csv'

    # Write the data to the CSV file
    if os.path.exists(file_name):
        with open(file_name, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
            writer.writerow([])
    else:
        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
            writer.writerow([])

def automatic_play(bird, wing_sound, pipe_group, game_restart_tick, score):
    bird.bump()
    wing_sound.play()
    time_of_jump = pygame.time.get_ticks() - game_restart_tick # from when game restarts
    bird_height = bird.rect[1]
    # print(len(pipe_group.sprites())) 
    # Always 4 pipes existing, pipes continue to exist in pipe_group a little white 
    # after going off screen before getting removed
    if (pipe_group.sprites()[0].rect[0] < 0):
        pipe_x_pos = pipe_group.sprites()[2].rect[0]
        top_pipe_y_pos = pipe_group.sprites()[2].rect[1]
        bottom_pipe_y_pos = pipe_group.sprites()[3].rect[1]
    else:
        pipe_x_pos = pipe_group.sprites()[0].rect[0]
        top_pipe_y_pos = pipe_group.sprites()[0].rect[1]
        bottom_pipe_y_pos = pipe_group.sprites()[1].rect[1]
    return (time_of_jump, bird_height, pipe_x_pos, top_pipe_y_pos, bottom_pipe_y_pos, score)

def game_over_screen(screen, score, score_font):
    """
    Show a game-over screen with the final score and a message to restart.
    """
   #Prompt information for rendering scores and restarting
    score_text = score_font.render(f'Final Score: {score}', True, (255, 255, 255))
    restart_text = score_font.render('Press Space to Restart', True, (255, 255, 255))

   #Display score and prompt information in the center
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50))

    screen.blit(score_text, score_rect)
    screen.blit(restart_text, restart_rect)

    #Update screen display
    pygame.display.update()

    #Waiting for player response
    waiting = True 
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return False  #End the game
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    return True  #Restart the game
        return True # just so agent does not need to wait for keypress to restart the game

def get_random_pipes(xpos):
    size = random.randint(100, 300)
    pipe = Pipe(False, xpos, size)
    pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)
    return pipe, pipe_inverted

class Bird(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.images =  [pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha(),
                        pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha(),
                        pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha()]

        self.speed = SPEED

        self.current_image = 0
        self.image = pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = SCREEN_WIDTH / 6
        self.rect[1] = SCREEN_HEIGHT / 2

    def update(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        self.speed += GRAVITY

        #UPDATE HEIGHT
        self.rect[1] += self.speed

    def bump(self):
        self.speed = -SPEED

    def begin(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]




class Pipe(pygame.sprite.Sprite):

    def __init__(self, inverted, xpos, ysize):
        pygame.sprite.Sprite.__init__(self)

        self. image = pygame.image.load('assets/sprites/pipe-green.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDTH, PIPE_HEIGHT))


        self.rect = self.image.get_rect()
        self.rect[0] = xpos

        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = - (self.rect[3] - ysize)
        else:
            self.rect[1] = SCREEN_HEIGHT - ysize


        self.mask = pygame.mask.from_surface(self.image)


    def update(self):
        self.rect[0] -= GAME_SPEED

        

class Ground(pygame.sprite.Sprite):
    
    def __init__(self, xpos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/sprites/base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDTH, GROUND_HEIGHT))

        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT
    def update(self):
        self.rect[0] -= GAME_SPEED

def is_off_screen(sprite):
    return sprite.rect[0] < -(sprite.rect[2]) # modified to instantly remove when off screen

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Flappy Bird')

    BACKGROUND = pygame.image.load('assets/sprites/background-day.png').convert()
    BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))

    wing_sound = pygame.mixer.Sound(wing)  #Preload sound
    hit_sound = pygame.mixer.Sound(hit)

    score_font = pygame.font.Font(None, 32)
    clock = pygame.time.Clock()

    game_restart_tick = 0

    running = True
    while running:  #Main loop
        score = 0
        jump_data_list = []
        bird_group = pygame.sprite.Group()
        bird = Bird()
        bird_group.add(bird)

        ground_group = pygame.sprite.Group()
        for i in range(2):
            ground = Ground(GROUND_WIDTH * i)
            ground_group.add(ground)

        pipe_group = pygame.sprite.Group()
        for i in range(2):
            pipes = get_random_pipes(SCREEN_WIDTH * i + 800)
            pipe_group.add(pipes[0])
            pipe_group.add(pipes[1])

        game_over = False
        while not game_over:  #Game Run Cycle
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return
                if event.type == KEYDOWN:
                    if event.key == K_SPACE or event.key == K_UP:
                        bird.bump()
                        wing_sound.play()
            if random.randint(0, 20) > 18:
                jump_data_list.append(automatic_play(bird, wing_sound, pipe_group, game_restart_tick, score))

            screen.blit(BACKGROUND, (0, 0))

            if is_off_screen(ground_group.sprites()[0]):
                ground_group.remove(ground_group.sprites()[0])
                new_ground = Ground(GROUND_WIDTH - 20)
                ground_group.add(new_ground)

            if is_off_screen(pipe_group.sprites()[0]):
                pipe_group.remove(pipe_group.sprites()[0])
                pipe_group.remove(pipe_group.sprites()[0])
                score += 1
                pipes = get_random_pipes(SCREEN_WIDTH * 2)
                pipe_group.add(pipes[0])
                pipe_group.add(pipes[1])

            bird_group.update()
            ground_group.update()
            pipe_group.update()

            bird_group.draw(screen)
            pipe_group.draw(screen)
            ground_group.draw(screen)

            show_score(screen, score, score_font)

            pygame.display.update()

            if (pygame.sprite.groupcollide(bird_group, ground_group, False, False, pygame.sprite.collide_mask) or
                    pygame.sprite.groupcollide(bird_group, pipe_group, False, False, pygame.sprite.collide_mask)):
                hit_sound.play()
                time.sleep(1)  #Pause briefly to display collision effects
                update_training_data(jump_data_list)
                game_over = True  #End internal loop

        #Show game end screen
        if not game_over_screen(screen, score, score_font):
            break  #If the function returns False, exit the main loop and end the game
        else:
            game_restart_tick = pygame.time.get_ticks()

if __name__ == '__main__':
    main()
