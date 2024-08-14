# import packages to build the game
from __future__ import print_function
import neat.config
import pygame
import neat
import random

screen_size = {
    "width": 400,
    "height": 600
}

assets = {
    "background": "Flappy Bird/assets/Game Objects/background.png",
    "base": "Flappy Bird/assets/Game Objects/base.png",
    "bird": ["Flappy Bird/assets/Game Objects/yellowbird-upflap.png", "Flappy Bird/assets/Game Objects/yellowbird-midflap.png", "Flappy Bird/assets/Game Objects/yellowbird-downflap.png"],
    "pipe": "Flappy Bird/assets/Game Objects/pipe.png",
    "gameover": "Flappy Bird/assets/UI/gameover.png",
    "message": "Flappy Bird/assets/UI/message.png",
    "score": [
        "Flappy Bird/assets/UI/Numbers/0.png",
        "Flappy Bird/assets/UI/Numbers/1.png",
        "Flappy Bird/assets/UI/Numbers/2.png",
        "Flappy Bird/assets/UI/Numbers/3.png",
        "Flappy Bird/assets/UI/Numbers/4.png",
        "Flappy Bird/assets/UI/Numbers/5.png",
        "Flappy Bird/assets/UI/Numbers/6.png",
        "Flappy Bird/assets/UI/Numbers/7.png",
        "Flappy Bird/assets/UI/Numbers/8.png",
        "Flappy Bird/assets/UI/Numbers/9.png",
    ]
}

audio = {
    "hit": "Flappy Bird/assets/Sound Efects/hit.wav",
    "point": "Flappy Bird/assets/Sound Efects/point.wav",
    "swoosh": "Flappy Bird/assets/Sound Efects/swoosh.wav",
    "wing": "Flappy Bird/assets/Sound Efects/wing.wav",
    "die": "Flappy Bird/assets/Sound Efects/die.wav",
}

# initialize pygame
pygame.init()
SCREEN = pygame.display.set_mode((screen_size['width'], screen_size['height']))

# set up the font
FONT = pygame.font.SysFont('comicsansms', 20)
FONT_COLOR = (255, 255, 255)  # white font

# load the required images
BIRD_IMGS = [pygame.image.load(assets['bird'][0]),
             pygame.image.load(assets['bird'][1]),
             pygame.image.load(assets['bird'][2]),
             ]

BOTTOM_PIPE_IMG = pygame.image.load(assets['pipe'])
# flip the image of the bottom pipe to get the image for the pipe on the top
TOP_PIPE_IMG = pygame.transform.flip(BOTTOM_PIPE_IMG, False, True)

FLOOR_IMG = pygame.image.load(assets['base'])

BG_IMG = pygame.transform.scale(pygame.image.load(
    assets['background']), (screen_size['width'], screen_size['height']))

# set the game options
FPS = 30  # run the game at rate FPS, the speed at which images are shown
max_score = 5000  # the maximum score of the game before we break the loop

# floor options
# the horizontal moving velocity of the floor, this should equal to pipe_velocity
floor_velocity = 5
floor_starting_y_position = 500  # the starting y position of the floor

# pipe options
pipe_max_num = 5000  # the maximum number of pipes in this game\

# the gap between the top pipe and the bottom pipe, the smaller the number, the harder the game
pipe_vertical_gap = 50 # This random ranging from 75 to 200
pipe_vertical_gap_min = 65
pipe_vertical_gap_max = 125

pipe_horizontal_gap = 200  # the gap between two sets of pipes
# the horizontal moving velocity of the pipes, this should equal to floor_velocity
pipe_velocity = 5
# the minimum height of the top pipe (carefully set this number)
top_pipe_min_height = 100
# the maximum height of the top pipe (carefully set this number)
top_pipe_max_height = 300
pipe_starting_x_position = 500  # the starting x position of the first pipe

# bird options
bird_max_upward_angle = 35  # the maximum upward angle when flying up
bird_max_downward_angle = -90  # the maximum downward angle when flying down
# the minimum incremental angle when tilting up or down
bird_min_incremental_angle = 5
bird_angular_acceleration = 0.3  # the acceleration of bird's flying angle
bird_jump_velocity = -12  # the vertical jump up velocity
bird_acceleration = 12  # the gravity for the bird in the game
bird_max_displacement = 20  # the maximum displacement per frame
bird_starting_x_position = 150  # the starting x position of the bird
bird_starting_y_position = 250  # the starting y position of the bird


class Bird:
    # Bird's attributes
    IMGS = BIRD_IMGS
    MAX_UPWARD_ANGLE = bird_max_upward_angle
    MAX_DOWNWARD_ANGLE = bird_max_downward_angle

    # initialize the Object
    def __init__(self, x_position, y_position):
        # use the first image as the initial image
        self.bird_img = self.IMGS[0]
        self.x = x_position  # starting x position
        self.y = y_position  # starting y position
        self.fly_angle = 0  # starting flying angle, initialized to be 0
        self.time = 0  # starting time set to calculate displacement, initialized to be 0
        self.velocity = 0  # starting vertical velocity, initialized to be 0
        self.index = 0  # used to change bird images, initialized to be 0

    # defien a function to move the bird
    def move(self):
        self.time += 1  # count the time

        # for a body with a nonzero speed v and a constant acceleration a
        # the displacement d of this body after time t is d = vt + 1/2at^2
        # calculate the displacement when going downward
        displacement = self.velocity * self.time + \
            (1/2) * bird_acceleration * self.time ** 2

        # we don't want the bird going donw too fast
        # so we need to set a displacement limit per frame
        if displacement > bird_max_displacement:
            displacement = bird_max_displacement

        self.y = self.y + displacement  # update the bird y position after the displacement

        if displacement < 0:  # when the bird is going up
            if self.fly_angle < self.MAX_UPWARD_ANGLE:  # if the flying angle is less than the maximum upward angle
                self.fly_angle += max(bird_angular_acceleration*(self.MAX_UPWARD_ANGLE -
                                      self.fly_angle), bird_min_incremental_angle)  # accelerate the angle up
            elif self.fly_angle >= self.MAX_UPWARD_ANGLE:
                self.fly_angle = self.MAX_UPWARD_ANGLE

        else:  # when the bird is going down
            if self.fly_angle > self.MAX_DOWNWARD_ANGLE:  # if the flying angle is less than the maximum downward angle
                self.fly_angle -= abs(min(bird_angular_acceleration*(self.MAX_DOWNWARD_ANGLE -
                                      self.fly_angle), -bird_min_incremental_angle))  # accelerate the angle down
            elif self.fly_angle <= self.MAX_DOWNWARD_ANGLE:
                self.fly_angle = self.MAX_DOWNWARD_ANGLE

    # defien a function to jump the bird
    def jump(self):
        self.velocity = bird_jump_velocity  # jump up by bird_jump_velocity
        self.time = 0  # when we jump, we reset the time to 0

    # define a function to get the rotated image and rotated rectangle for draw function
    def update(self):
        # if the bird is diving, then it shouldn't flap its wings
        if self.fly_angle < -45:
            self.bird_img = self.IMGS[0]
            self.index = 0  # reset the index

        # if the bird is not diving, then it should flap its wings
        # keep looping the 3 bird images to mimic flapping its wings
        elif self.index >= len(self.IMGS):
            self.index = 0

        self.bird_img = self.IMGS[self.index]
        self.index += 1

        # https://stackoverflow.com/questions/4183208/how-do-i-rotate-an-image-around-its-center-using-pygame
        # rotate the bird image for degree at self.tilt
        rotated_image = pygame.transform.rotate(self.bird_img, self.fly_angle)
        # store the center of the source image rectangle
        origin_img_center = self.bird_img.get_rect(
            topleft=(self.x, self.y)).center
        # update the center of the rotated image rectangle
        rotated_rect = rotated_image.get_rect(center=origin_img_center)
        # get the rotated bird image and the rotated rectangle
        return rotated_image, rotated_rect

# build the class Pipe


class Pipe:
    # Pipe's attributes
    VERTICAL_GAP = pipe_vertical_gap  # the gap between the top and bottom pipes
    VELOCITY = pipe_velocity  # the moving velocity of the pipes
    IMG_WIDTH = TOP_PIPE_IMG.get_width()  # the width of the pipe
    IMG_LENGTH = TOP_PIPE_IMG.get_height()  # the length of the pipe

    # initialize the Object
    def __init__(self, x_position):
        self.top_pipe_img = TOP_PIPE_IMG  # get the image for the pipe on the top
        # get the image for the pipe on the bottom
        self.bottom_pipe_img = BOTTOM_PIPE_IMG
        self.x = x_position  # starting x position of the first set of pipes
        self.top_pipe_height = 0  # the height of the top pipe, initialized to be 0
        self.top_pipe_topleft = 0  # the topleft position of the top pipe, initialized to be 0
        # the topleft position of the bottom pipe, initialized to be 0
        self.bottom_pipe_topleft = 0
        # set the height of the pipes randomly as well as the starting topleft position for top and bottom pipes
        self.random_height()

    # define a function to move the pipe
    def move(self):
        self.x -= self.VELOCITY

    # define a function to randomize pipe gaps
    def random_height(self):
        # the range is between top_pipe_min_height and top_pipe_max_height
        self.top_pipe_height = random.randrange(
            top_pipe_min_height, top_pipe_max_height)
        # the topleft position of the top pipe should be the random height - the length of the pipe
        self.top_pipe_topleft = self.top_pipe_height - self.IMG_LENGTH
        # the topleft position of the bottom pipe should be the random height + the GAP
        self.VERTICAL_GAP = random.randrange(
            pipe_vertical_gap_min, pipe_vertical_gap_max)
        self.bottom_pipe_topleft = self.top_pipe_height + self.VERTICAL_GAP


# build the class Floor
class Floor:
    # Floor's attributes
    # we need 3 floor images to set up the moving floor
    IMGS = [FLOOR_IMG, FLOOR_IMG, FLOOR_IMG]
    VELOCITY = floor_velocity  # the moving velocity of the floor
    IMG_WIDTH = FLOOR_IMG.get_width()  # the width of the floor

    # initialize the Object
    def __init__(self, y_position):
        # these 3 images have different starting position but have the same y position
        self.x1 = 0  # the starting x position of the first floor image
        self.x2 = self.IMG_WIDTH  # the starting x position of the second floor image
        self.x3 = self.IMG_WIDTH * 2  # the starting x position of the third floor image
        self.y = y_position  # the y position of the floor image

    # define a function to move the floor
    def move(self):
        self.x1 -= self.VELOCITY  # move to the left with the velocity of VELOCITY
        self.x2 -= self.VELOCITY  # move to the left with the velocity of VELOCITY
        self.x3 -= self.VELOCITY  # move to the left with the velocity of VELOCITY

        if self.x1 + self.IMG_WIDTH < 0:  # if the first floor image moves out of the screen
            # then move the first floor image to to the right of the third floor image
            self.x1 = self.x3 + self.IMG_WIDTH
        if self.x2 + self.IMG_WIDTH < 0:  # if the second floor image moves out of the screen
            # then move the second floor image to to the right of the first floor image
            self.x2 = self.x1 + self.IMG_WIDTH
        if self.x3 + self.IMG_WIDTH < 0:  # if the third floor image moves out of the screen
            # then move the third floor image to to the right of the second floor image
            self.x3 = self.x2 + self.IMG_WIDTH

# define a function to check collision


def collide(bird, pipe, floor, screen):

    # Creates a Mask object from the given surface by setting all the opaque pixels and not setting the transparent pixels
    bird_mask = pygame.mask.from_surface(
        bird.bird_img)  # get the mask of the bird
    top_pipe_mask = pygame.mask.from_surface(
        pipe.top_pipe_img)  # get the mask of the pipe on the top
    bottom_pipe_mask = pygame.mask.from_surface(
        pipe.bottom_pipe_img)  # get the mask of the pipe on the bottom

    sky_height = 0  # the sky height is the upper limit
    floor_height = floor.y  # the floor height is the lower limit
    # the y position of the lower end of the bird image
    bird_lower_end = bird.y + bird.bird_img.get_height()

    # in order to check whether the bird hit the pipe, we need to find the point of intersection of the bird and the pipes
    # if overlap, then mask.overlap(othermask, offset) return (x, y)
    # if not overlap, then mask.overlap(othermask, offset) return None
    # more information regarding offset, https://www.pygame.org/docs/ref/mask.html#mask-offset-label
    top_pipe_offset = (round(pipe.x - bird.x),
                       round(pipe.top_pipe_topleft - bird.y))
    bottom_pipe_offset = (round(pipe.x - bird.x),
                          round(pipe.bottom_pipe_topleft - bird.y))

    # Returns the first point of intersection encountered between bird's mask and pipe's masks
    top_pipe_intersection_point = bird_mask.overlap(
        top_pipe_mask, top_pipe_offset)
    bottom_pipe_intersection_point = bird_mask.overlap(
        bottom_pipe_mask, bottom_pipe_offset)

    if top_pipe_intersection_point is not None or bottom_pipe_intersection_point is not None or bird_lower_end > floor_height or bird.y < sky_height:
        return True
    else:
        return False

# define a function to draw the screen to display the game


def draw_game(screen, birds, pipes, floor, score, generation, game_time):

    # draw the background
    screen.blit(BG_IMG, (0, 0))

    # draw the moving pipes
    for pipe in pipes:
        # draw the pipe on the top
        screen.blit(pipe.top_pipe_img, (pipe.x, pipe.top_pipe_topleft))
        # draw the pipe on the bottom
        screen.blit(pipe.bottom_pipe_img, (pipe.x, pipe.bottom_pipe_topleft))
    # draw the moving floor
    # draw the first floor image
    screen.blit(floor.IMGS[0], (floor.x1, floor.y))
    # draw the second floor image
    screen.blit(floor.IMGS[1], (floor.x2, floor.y))
    # draw the third floor image
    screen.blit(floor.IMGS[2], (floor.x3, floor.y))


    # draw the animated birds
    for bird in birds:
        rotated_image, rotated_rect = bird.update()
        screen.blit(rotated_image, rotated_rect)

    # add additional information
    # set up the text to show the scores
    score_text = FONT.render('Score: ' + str(score), 1, FONT_COLOR)
    # draw the scores
    screen.blit(
        score_text, (screen_size["width"] - 15 - score_text.get_width(), 15))

    # set up the text to show the progress
    game_time_text = FONT.render(
        'Timer: ' + str(game_time) + ' s', 1, FONT_COLOR)
    screen.blit(game_time_text, (screen_size["width"] - 15 - game_time_text.get_width(
    ), 15 + score_text.get_height()))  # draw the progress

    # set up the text to show the number of generation
    generation_text = FONT.render(
        'Generation: ' + str(generation - 1), 1, FONT_COLOR)
    screen.blit(generation_text, (15, 15))  # draw the generation

    # set up the text to show the number of birds alive
    bird_text = FONT.render('Birds Alive: ' + str(len(birds)), 1, FONT_COLOR)
    # draw the number of birds alive
    screen.blit(bird_text, (15, 15 + generation_text.get_height()))

    # set up the text to show the progress
    progress_text = FONT.render(
        'Pipes Remained: ' + str(len(pipes) - score), 1, FONT_COLOR)
    screen.blit(progress_text, (15, 15 + generation_text.get_height() +
                bird_text.get_height()))  # draw the progress

    pygame.display.update()  # show the surface


# NEAT options
generation = 0  # note that the first generation of the birds is 0 because index starts from zero. XD
max_gen = 500  # the maximum number of generation to run
prob_threshold_to_jump = 0.8  # the probability threshold to activate the bird to jump
failed_punishment = 10  # the amount of fitness decrease after collision

# define a function to get the input index of the pipes


def get_index(pipes, birds):
    # get the birds' x position
    bird_x = birds[0].x
    # calculate the x distance between birds and each pipes
    list_distance = [pipe.x + pipe.IMG_WIDTH - bird_x for pipe in pipes]
    # get the index of the pipe that has the minimum non negative distance(the closest pipe in front of the bird)
    index = list_distance.index(min(i for i in list_distance if i >= 0))
    return index


def main(genomes, config):

    global generation, SCREEN
    screen = SCREEN

    generation += 1

    score = 0
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()

    floor = Floor(floor_starting_y_position)  # set up the floor
    # set up the pipe list
    pipes_list = []
    for i in range(pipe_max_num):
        global pipe_vertical_gap
        pipe_vertical_gap = random.randrange(pipe_vertical_gap_min, pipe_vertical_gap_max)
        pipe = Pipe(pipe_starting_x_position + i * pipe_horizontal_gap)
        pipes_list.append(pipe)

    models_list = []
    genomes_list = []
    birds_list = []

#     initialize the neural network
    for geneome_id, genome in genomes:
        birds_list.append(
            Bird(bird_starting_x_position, bird_starting_y_position))
        genome.fitness = 0
        genomes_list.append(genome)
        model = neat.nn.FeedForwardNetwork.create(genome, config)
        models_list.append(model)

    run = True

    while run is True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        if score >= max_score or len(birds_list) == 0:
            run = False
            break

        game_time = round((pygame.time.get_ticks() - start_time) / 1000, 2)
        clock.tick(FPS)
        floor.move()

        pipe_input_index = get_index(pipes_list, birds_list)

        passes_pipes = []
        for pipe in pipes_list:
            pipe.move()
            if pipe.x + pipe.IMG_WIDTH < birds_list[0].x:
                passes_pipes.append(pipe)

        score = len(passes_pipes)

        for index, bird in enumerate(birds_list):
            bird.move()
            delta_x = pipes_list[pipe_input_index].x - bird.x
            delta_y_top = bird.y - pipes_list[pipe_input_index].top_pipe_height
            delta_y_bottom = bird.y - \
                pipes_list[pipe_input_index].bottom_pipe_topleft

            net_input = (delta_x, delta_y_top, delta_y_bottom)

            output = models_list[index].activate(net_input)

            if output[0] > prob_threshold_to_jump:
                bird.jump()

            bird_failed = True if collide(
                bird, pipes_list[pipe_input_index], floor, screen) is True else False

            genomes_list[index].fitness = game_time + \
                score - bird_failed*failed_punishment

            if bird_failed is True:
                birds_list.pop(index)
                models_list.pop(index)
                genomes_list.pop(index)

        draw_game(screen, birds_list, pipes_list, floor, score, generation, game_time)


def run_Neat(config_path):

    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    
    neat_pop = neat.Population(config)

    # add the stats reporter
    neat_pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    neat_pop.add_reporter(stats)

    neat_pop.run(main, max_gen)

    winner = stats.best_genome()

    # Visualization
    node_name = {-1: 'delta_x', -2 : 'delta_y_top', -3 : 'delta_y_bottom', 0 : 'jump or not'}
    neat.visualize.draw_net(config, winner, True, node_name=node_name)
    neat.visualize.plot_stats(stats, ylog = False, view = True)
    neat.visualize.plot_species(stats, view = True)

    print('Best genome:\n{!s}'.format(winner))

config_path = "D:\Work\Programming\Learning New Things\Genetic Algo\Flappy Bird\config.txt"

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                run_Neat(config_path)  
    pygame.display.update()

