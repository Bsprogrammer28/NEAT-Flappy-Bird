import pygame
import random
import sys
from pygame.locals import *

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

game_images = {}
groundHeight = screen_size["height"] * 0.8
FPS = 32
window = pygame.display.set_mode((screen_size["width"], screen_size["height"]))


def render_pipe():
    offset = screen_size["height"] / 3
    pipe_height = game_images["pipes"][0].get_height()
    base_height = game_images["base"].get_height()

    pipeX = screen_size["width"] + 10

    # Calculate a random y position for the bottom pipe and derive the top pipe position
    pipe2_y = offset + random.randrange(0, int(screen_size["height"] - base_height - 1.2 * offset))
    pipe1_y = pipe2_y - pipe_height - offset

    # Top pipe (upside down) and bottom pipe coordinates
    pipe_cords = [
        {"x": pipeX, "y": pipe1_y},  # Upper pipe
        {"x": pipeX, "y": pipe2_y},  # Lower pipe
    ]
    return pipe_cords



def game_over(horizontal, vertical, up_pipes, down_pipes):
    bird_width = game_images["bird"][0].get_width()
    bird_height = game_images["bird"][0].get_height()

    # Check for collision with upper pipes
    for pipe in up_pipes:
        pipe_height = game_images["pipes"][0].get_height()
        if vertical < pipe["y"] + pipe_height:
            if abs(horizontal - pipe["x"]) < bird_width:
                return True

    # Check for collision with lower pipes
    for pipe in down_pipes:
        if vertical + bird_height > pipe["y"]:
            if abs(horizontal - pipe["x"]) < bird_width:
                return True

    # Check for collision with the ground
    if vertical + bird_height >= groundHeight:
        return True

    return False



def game_logic():
    score = 0
    horizontal = int(screen_size["width"]/5) 
    vertical = int(screen_size["height"]/2) 
    ground = 0
    mytempHeight = 100
    first_pipe = render_pipe()
    second_pipe = render_pipe()

    down_pipes = [
        {
            "x": screen_size["width"] + 300 - mytempHeight,
            "y": first_pipe[1]["y"]
        },
        {
            "x": screen_size["width"] + 300 - mytempHeight + (screen_size["width"] / 2),
            "y": second_pipe[1]["y"]
        }
    ]

    up_pipes = [
        {
            "x": screen_size["width"] + 300 - mytempHeight,
            "y": first_pipe[0]["y"]
        },
        {
            "x": screen_size["width"] + 300 - mytempHeight + (screen_size["width"] / 2),
            "y": second_pipe[0]["y"]
        }
    ]

    pipeVel = -4
    birdVelY = -9
    birdMaxVelY = 10
    birdMinVelY = -8
    birdAccY = 1

    birdFlapVel = -8    
    birdFlapped = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if vertical > 0:
                    birdVelY = birdFlapVel
                    birdFlapped = True

        if game_over(horizontal, vertical, up_pipes, down_pipes):
            return
        
        # Check for Score
        playerMidPos = horizontal + game_images["bird"][0].get_width() / 2

        # Increment the Score
        for pipe in up_pipes:
            pipeMidPos = pipe["x"] + game_images["pipes"][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                # pygame.mixer.Sound.play(audio["point"])

        # Increase velocity of the bird
        if birdVelY < birdMaxVelY and not birdFlapped:
            birdVelY += birdAccY

        if birdFlapped:
            birdFlapped = False
        playerHeight = game_images["bird"][0].get_height()
        vertical = vertical + min(birdVelY, groundHeight - vertical - playerHeight)

        # Move pipes to left
        for upperPipe, lowerPipe in zip(up_pipes, down_pipes):
            upperPipe["x"] += pipeVel
            lowerPipe["x"] += pipeVel

        # Add new pipe
        if 0 < up_pipes[0]["x"] < 5:
            newpipe = render_pipe()
            up_pipes.append(newpipe[0])
            down_pipes.append(newpipe[1])
        
        # Remove old pipe
        if up_pipes[0]["x"] < -game_images["pipes"][0].get_width():
            up_pipes.pop(0)
            down_pipes.pop(0)
        
        # Draw game elements
        window.blit(game_images["background"], (0, 0))
        for upperPipe, lowerPipe in zip(up_pipes, down_pipes):
            window.blit(game_images["pipes"][0], (upperPipe["x"], upperPipe["y"]))
            window.blit(game_images["pipes"][1], (lowerPipe["x"], lowerPipe["y"]))

        window.blit(game_images["base"], (ground, groundHeight))
        window.blit(game_images["bird"][0], (horizontal, vertical))

        myDigits = [int(x) for x in list(str(score))]
        width = 0
        for digit in myDigits:
            width += game_images["scores"][digit].get_width()
        Xoffset = (screen_size["width"] - width) / 2

        for digit in myDigits:
            window.blit(game_images["scores"][digit], (Xoffset, screen_size["height"] * 0.12))
            Xoffset += game_images["scores"][digit].get_width()

        pygame.display.update()
        clock.tick(FPS)



if __name__ == "__main__":
    #NEAT options
    generation = 0 #note that the first generation of the birds is 0 because index starts from zero. XD
    max_gen = 50 #the maximum number of generation to run
    prob_threshold_to_jump = 0.8 #the probability threshold to activate the bird to jump
    failed_punishment = 10 #the amount of fitness decrease after collision

    #Assets
    pygame.init()
    pygame.display.set_caption("Flappy Bird")

    game_images["background"] = pygame.image.load(
        assets["background"]).convert_alpha()
    game_images["base"] = pygame.image.load(assets["base"]).convert_alpha()
    game_images["gameover"] = pygame.image.load(
        assets["gameover"]).convert_alpha()
    game_images["message"] = pygame.image.load(
        assets["message"]).convert_alpha()
    game_images["bird"] = [pygame.image.load(
        assets["bird"][i]).convert_alpha() for i in range(len(assets["bird"]))]
    game_images["scores"] = [
        pygame.image.load(assets["score"][0]).convert_alpha(),
        pygame.image.load(assets["score"][1]).convert_alpha(),
        pygame.image.load(assets["score"][2]).convert_alpha(),
        pygame.image.load(assets["score"][3]).convert_alpha(),
        pygame.image.load(assets["score"][4]).convert_alpha(),
        pygame.image.load(assets["score"][5]).convert_alpha(),
        pygame.image.load(assets["score"][6]).convert_alpha(),
        pygame.image.load(assets["score"][7]).convert_alpha(),
        pygame.image.load(assets["score"][8]).convert_alpha(),
        pygame.image.load(assets["score"][9]).convert_alpha(),
    ]
    game_images["pipes"] = [
        pygame.transform.flip(pygame.image.load(
            assets["pipe"]).convert_alpha(), False, True),
        pygame.image.load(assets["pipe"]).convert_alpha()
    ]
    clock = pygame.time.Clock()

    horizontal = int(screen_size["width"]/5)
    vertical = int(
        (screen_size["height"] - game_images['bird'][1].get_height())/2)

    ground = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_logic()
            else:
                window.blit(game_images["background"], (0, 0))
                window.blit(game_images["base"], (0, 475))
                window.blit(game_images["message"], ((screen_size["width"] - game_images["message"].get_width(
                ))/2, (screen_size["height"] - game_images["message"].get_height())/2 - 50))
                pygame.display.update()
                clock.tick(FPS)

        clock.tick(FPS)
