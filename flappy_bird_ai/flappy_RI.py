import pygame
import random
import time
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


class FlappyBirdEnv:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Flappy Bird')

        self.BACKGROUND = pygame.image.load('assets/sprites/background-day.png').convert()
        self.BACKGROUND = pygame.transform.scale(self.BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.wing_sound = pygame.mixer.Sound(wing)  #Preload sound
        self.hit_sound = pygame.mixer.Sound(hit)

        self.score_font = pygame.font.Font(None, 32)
        self.clock = pygame.time.Clock()

        self.score = 0
        self.bird_group = pygame.sprite.Group()
        self.bird = Bird()
        self.ground_group = pygame.sprite.Group()
        self.pipe_group = pygame.sprite.Group()

    def reset(self):
        self.score = 0
        self.bird_group.remove()
        self.pipe_group.remove()
        self.ground_group.remove()

        self.bird_group = pygame.sprite.Group()
        self.bird = Bird()
        self.bird_group.add(self.bird)

        self.ground_group = pygame.sprite.Group()
        for i in range(2):
            ground = Ground(GROUND_WIDTH * i)
            self.ground_group.add(ground)

        self.pipe_group = pygame.sprite.Group()
        for i in range(2):
            pipes = get_random_pipes(SCREEN_WIDTH * i + 800)
            self.pipe_group.add(pipes[0])
            self.pipe_group.add(pipes[1])
        return self.get_observation()

    def step(self, action):
        self.clock.tick(50)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return False  #End the game
        
        if action == 1:
            self.bird.bump()
            self.wing_sound.play()

        self.screen.blit(self.BACKGROUND, (0, 0))

        if is_off_screen(self.ground_group.sprites()[0]):
            self.ground_group.remove(self.ground_group.sprites()[0])
            new_ground = Ground(GROUND_WIDTH - 20)
            self.ground_group.add(new_ground)

        if is_off_screen(self.pipe_group.sprites()[0]):
            self.pipe_group.remove(self.pipe_group.sprites()[0])
            self.pipe_group.remove(self.pipe_group.sprites()[0])
            self.score += 1
            pipes = get_random_pipes(SCREEN_WIDTH * 2)
            self.pipe_group.add(pipes[0])
            self.pipe_group.add(pipes[1])

        self.bird_group.update()
        self.ground_group.update()
        self.pipe_group.update()

        self.bird_group.draw(self.screen)
        self.pipe_group.draw(self.screen)
        self.ground_group.draw(self.screen)

        show_score(self.screen, self.score, self.score_font)

        pygame.display.update()
        
        if (pygame.sprite.groupcollide(self.bird_group, self.ground_group, False, False, pygame.sprite.collide_mask) or
                pygame.sprite.groupcollide(self.bird_group, self.pipe_group, False, False, pygame.sprite.collide_mask)):
            self.hit_sound.play()
            observation = self.get_observation(), -100, 1
            print(self.score)
            #self.reset()
            time.sleep(1)  #Pause briefly to display collision effects
            return observation
        return self.get_observation(), 0, 0

    def get_observation(self):
        return automatic_play(self.bird, self.pipe_group)

def automatic_play(bird, pipe_group):
    bird_height = bird.rect[1]
    if (pipe_group.sprites()[0].rect[0] < 0):
        pipe_x_pos = pipe_group.sprites()[2].rect[0]
        top_pipe_y_pos = pipe_group.sprites()[2].rect[1]
        bottom_pipe_y_pos = pipe_group.sprites()[3].rect[1]
    else:
        pipe_x_pos = pipe_group.sprites()[0].rect[0]
        top_pipe_y_pos = pipe_group.sprites()[0].rect[1]
        bottom_pipe_y_pos = pipe_group.sprites()[1].rect[1]
    return (bird_height, pipe_x_pos, top_pipe_y_pos, bottom_pipe_y_pos)

def is_off_screen(sprite):
    return sprite.rect[0] < -(sprite.rect[2])