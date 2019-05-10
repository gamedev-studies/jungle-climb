import pathlib
import sys
import os
from ctypes import windll

from pygame import K_w, K_a, K_d, K_UP, K_LEFT, K_RIGHT, K_ESCAPE, K_F4, K_p, K_RALT, K_LALT, K_SPACE
import pygame

# TODO: fix pygame lag when platforms are spawning

# constants
WHITE = 255, 255, 255
BLACK = 0, 0, 0
GREEN = 50, 205, 50
DARK_GREEN = 0, 128, 0

LIGHT_BLUE = 0, 191, 255
BLUE = 33, 150, 243

BACKGROUND = 174, 222, 203
game_folder = os.path.expanduser(r'~\Documents\Jungle Climb')

windll.user32.SetProcessDPIAware()  # overrides windows "Change the size of Apps"
os.environ['SDL_VIDEO_CENTERED'] = '1'  # center display
pygame.init()  # initialize pygame
infoObject = pygame.display.Info()  # infoObject holds information about the screen resolution

# SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = int(0.75 * infoObject.current_w), int(0.75 * infoObject.current_h)
# screen = pygame.display.set_mode(SIZE)

# FOR FULL SCREEN
SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = infoObject.current_w, infoObject.current_h
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

pygame.display.set_caption('Jungle Climb')
clock = pygame.time.Clock()

paused = False
from objects import *


def text_objects(text, font, colour=BLACK):
    text_surface = font.render(text, True, colour)
    return text_surface, text_surface.get_rect()


def save_score(user_score: int, path: str = game_folder + r'\high scores.txt') -> bool:
    """
    Takes a score and saves to file if it is a top 10 score else it returns False
    :param user_score: the score of the user
    :param path: high score text file location
    :return: boolean indicating whether the score was a top 10 score
    """

    try:
        with open(path) as f:
            scores = f.readlines()
        placement = None
        for i, score in enumerate(scores):
            if user_score > int(score[:-1]):
                placement = i
                break
        if placement is not None:
            scores.insert(placement, str(user_score) + '\n')
            with open(path, 'w') as f:
                f.writelines(scores[:-1])
            return True
        return False

    except FileNotFoundError:
        pathlib.Path(game_folder).mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            f.writelines([str(user_score) + '\n'] + ['0\n'] * 9)
        return True


def get_scores(path: str = game_folder + r'\high scores.txt') -> list:
    """
    Gets the list of top 10 scores
    :param path: path to the scores
    :return: list of the scores
    """

    try:
        with open(path) as f:
            return f.read().splitlines()
    except FileNotFoundError:
        pathlib.Path('/my/directory').mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            f.writelines(['0\n'] * 10)
        return [0] * 10


def aa_filled_rounded_rect(rect, color, radius=0.4):
    """
    aa_filled_rounded_rect(surface,rect,color,radius=0.4)

    surface : destination
    rect    : rectangle
    color   : rgb or rgba
    radius  : 0 <= radius <= 1
    """

    rect = pygame.Rect(rect)
    color = pygame.Color(*color)
    alpha = color.a
    color.a = 0
    pos = rect.topleft
    rect.topleft = 0, 0
    rectangle = pygame.Surface(rect.size, pygame.SRCALPHA)

    circle = pygame.Surface([min(rect.size) * 3] * 2, pygame.SRCALPHA)
    pygame.draw.ellipse(circle, (0, 0, 0), circle.get_rect(), 0)
    circle = pygame.transform.smoothscale(circle, [int(min(rect.size) * radius)] * 2)

    radius = rectangle.blit(circle, (0, 0))
    radius.bottomright = rect.bottomright
    rectangle.blit(circle, radius)
    radius.topright = rect.topright
    rectangle.blit(circle, radius)
    radius.bottomleft = rect.bottomleft
    rectangle.blit(circle, radius)

    rectangle.fill((0, 0, 0), rect.inflate(-radius.w, 0))
    rectangle.fill((0, 0, 0), rect.inflate(0, -radius.h))

    rectangle.fill(color, special_flags=pygame.BLEND_RGBA_MAX)
    rectangle.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MIN)

    return screen.blit(rectangle, pos)


def button(text, x, y, w, h, inactive_colour, active_colour, action=None, text_colour=BLACK):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    # focus = pygame.mouse.get_focused()

    if x < mouse[0] < x + w and y < mouse[1] < y + h:  # if mouse is hovering the button
        pygame.draw.rect(screen, active_colour, (x, y, w, h))
        if click[0] == 1 and action is not None and pygame.time.get_ticks() - ticks > 100: action()
    else:
        pygame.draw.rect(screen, inactive_colour, (x, y, w, h))

    small_text = pygame.font.Font('freesansbold.ttf', 20)
    text_surf, text_rect = text_objects(text, small_text, colour=text_colour)
    text_rect.center = (x + w / 2, y + h / 2)
    screen.blit(text_surf, text_rect)


def view_high_scores():
    screen.fill(WHITE)
    large_text = pygame.font.Font('freesansbold.ttf', 115)
    text_surf, text_rect = text_objects('High Scores', large_text)
    text_rect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 4))
    screen.blit(text_surf, text_rect)
    button_width = SCREEN_WIDTH * 0.20833333333333334
    button_height = SCREEN_HEIGHT * 0.06172839506172839
    # for score in get_scores():
    #     # todo: DISPLAY THESE SCORES
    #     pass
    while True:
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            alt_f4 = (event.type == pygame.KEYDOWN and event.key == pygame.K_F4
                      and (pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]))
            if event.type == pygame.QUIT or alt_f4: sys.exit()

        button('M A I N  M E N U', (SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT * 2 / 5,
               button_width, button_height, BLUE, LIGHT_BLUE, action=main_menu, text_colour=BLACK)
        # aa_filled_rounded_rect(((SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT * 2 / 5,
        #                         button_width, button_height), BLUE, 0.9)
        pygame.display.update()
        # clock.tick(60)


def main_menu():
    global ticks, on_main_menu
    on_main_menu = True
    # todo: change font colour
    # todo: fix  menu flows (stop spawning them)
    screen.fill(WHITE)
    large_text = pygame.font.Font('freesansbold.ttf', 115)
    text_surf, text_rect = text_objects('Jungle Climb', large_text)
    text_rect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 4))
    screen.blit(text_surf, text_rect)
    button_width = SCREEN_WIDTH * 0.20833333333333334
    button_height = SCREEN_HEIGHT * 0.06172839506172839
    ticks = pygame.time.get_ticks()
    while on_main_menu:
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            alt_f4 = (event.type == pygame.KEYDOWN and event.key == pygame.K_F4
                      and (pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]))
            if event.type == pygame.QUIT or alt_f4: sys.exit()
        button('S T A R T  G A M E', (SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT * 5 / 13,
               button_width, button_height, BLUE, LIGHT_BLUE, action=game, text_colour=BLACK)
        button('V I E W  H I G H S C O R E S', (SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT * 6 / 13,
               button_width, button_height, BLUE, LIGHT_BLUE, action=view_high_scores, text_colour=BLACK)
        button('Q U I T  G A M E', (SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT * 7 / 13,
               button_width, button_height, BLUE, LIGHT_BLUE, action=quit, text_colour=BLACK)
        # aa_filled_rounded_rect(((SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT * 2 / 5,
        #                         button_width, button_height), BLUE, 0.9)
        pygame.display.update()
        # clock.tick(60)


def resume():
    global paused
    paused = False


def pause_menu(player):
    global paused
    paused = True
    facing_left = player.facing_left  # store the pre-pause value in case player doesn't hold a right/left key down

    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA, 32)
    background.fill((255, 255, 255, 160))
    screen.blit(background, (0, 0))

    large_text = pygame.font.Font('freesansbold.ttf', 115)
    text_surf, text_rect = text_objects('Pause Menu', large_text)
    text_rect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 4))
    screen.blit(text_surf, text_rect)

    button_width = SCREEN_WIDTH * 0.20833333333333334
    button_height = SCREEN_HEIGHT * 0.06172839506172839
    while paused:
        for event in pygame.event.get():
            pressed_keys = pygame.key.get_pressed()
            alt_f4 = (event.type == pygame.KEYDOWN and event.key == K_F4
                      and (pressed_keys[K_LALT] or pressed_keys[K_RALT]))
            if event.type == pygame.QUIT or alt_f4: sys.exit()
            if event.type == pygame.KEYDOWN:
                right_key: bool = event.key == pygame.K_RIGHT and not pressed_keys[
                    pygame.K_d] or event.key == pygame.K_d and not pressed_keys[pygame.K_RIGHT]
                left_key: bool = event.key == pygame.K_LEFT and not pressed_keys[
                    pygame.K_a] or event.key == pygame.K_a and not pressed_keys[pygame.K_LEFT]
                if right_key:
                    player.go_right()
                elif left_key:
                    player.go_left()
                elif event.key in (pygame.K_ESCAPE, pygame.K_p):
                    paused = False
                    break
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_d, pygame.K_RIGHT, pygame.K_a, pygame.K_LEFT):
                    player.stop(pressed_keys)
                    player.facing_left = facing_left

        button('R E S U M E', (SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT * 5 / 13,
               button_width, button_height, BLUE, LIGHT_BLUE, action=resume, text_colour=BLACK)

        button('M A I N  M E N U', (SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT * 6 / 13,
               button_width, button_height, BLUE, LIGHT_BLUE, action=resume, text_colour=BLACK)

        button('Q U I T  G A M E', (SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT * 7 / 13,
               button_width, button_height, BLUE, LIGHT_BLUE, action=quit, text_colour=BLACK)
        # todo: update this UI LATER
        pygame.display.update()
        # clock.tick(60)


def leave_end_game():
    global on_end_game
    on_end_game = False


def end_game(score):
    # todo: change font colour
    global on_end_game
    on_end_game = True
    screen.fill(WHITE)
    large_text = pygame.font.Font('freesansbold.ttf', 115)
    text_surf, text_rect = text_objects('Game Over', large_text)
    text_rect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 4))
    screen.blit(text_surf, text_rect)

    large_text = pygame.font.Font('freesansbold.ttf', 50)
    text_surf, text_rect = text_objects(f'You scored {score}', large_text)
    text_rect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT * 2 / 5))
    screen.blit(text_surf, text_rect)
    button_width = SCREEN_WIDTH * 0.20833333333333334
    button_height = SCREEN_HEIGHT * 0.06172839506172839
    if save_score(score):
        # put a you got a top score!!
        pass
    while on_end_game:
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            alt_f4 = (event.type == pygame.KEYDOWN and event.key == pygame.K_F4
                      and (pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]))
            if event.type == pygame.QUIT or alt_f4: sys.exit()

        button('R E S T A R T', (SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT * 6 / 13,
               button_width, button_height, BLUE, LIGHT_BLUE, action=game, text_colour=BLACK)
        button('M A I N  M E N U', (SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT * 7 / 13,
               button_width, button_height, BLUE, LIGHT_BLUE, action=main_menu, text_colour=BLACK)
        button('V I E W  H I G H S C O R E S', (SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT * 8 / 13,
               button_width, button_height, BLUE, LIGHT_BLUE, action=view_high_scores, text_colour=BLACK)
        pygame.display.update()

        # clock.tick(60)


def game():
    global on_main_menu, paused
    on_main_menu = False
    world = World()
    player = Player(world)
    player.force_stop()
    all_sprites_list = pygame.sprite.Group(player)
    world.player = player
    # world_shift_speeds = [round(-0.000694444444*SCREEN_WIDTH * 2 ** x) for x in range(5)]
    world_shift_speed_percent = 0.0012345679
    world_shift_speed = round(world_shift_speed_percent * SCREEN_HEIGHT)  # note: percent of screen
    start_shifting = False
    score = 0
    text_topleft = round(0.00694 * SCREEN_WIDTH), round(0.0123 * SCREEN_HEIGHT)
    while True:
        # todo: made background with vines
        # todo: make the game faster every 5 ^ x world shifts

        for event in pygame.event.get():
            pressed_keys = pygame.key.get_pressed()
            alt_f4 = (event.type == pygame.KEYDOWN and event.key == K_F4
                      and (pressed_keys[K_LALT] or pressed_keys[K_RALT]))
            if event.type == pygame.QUIT or alt_f4: sys.exit()
            if event.type == pygame.KEYDOWN:
                right_key: bool = event.key == K_RIGHT and not pressed_keys[
                    pygame.K_d] or event.key == K_d and not pressed_keys[K_RIGHT]
                left_key: bool = event.key == K_LEFT and not pressed_keys[
                    pygame.K_a] or event.key == K_a and not pressed_keys[K_LEFT]
                if right_key:
                    player.go_right()
                elif left_key:
                    player.go_left()
                elif event.key in (K_UP, K_w, K_SPACE):
                    player.jump()
                elif event.key == K_ESCAPE and not pressed_keys[K_p] or event.key == K_p and not pressed_keys[K_ESCAPE]:
                    pause_menu(player)
            if event.type == pygame.KEYUP:
                if event.key in (K_LEFT, K_a, K_RIGHT, K_d):
                    player.stop(pressed_keys)

        player.update()
        if start_shifting:
            # if pygame.time.get_ticks() % 2 == 0:
            world.shift_world(world_shift_speed)
            score += 1
            if score > 1000 * world_shift_speed + (world_shift_speed - 1) * 1000:
                world_shift_speed = min(world_shift_speed * 2, round(world_shift_speed_percent * SCREEN_HEIGHT) * 3)

        elif player.rect.top < 0.75 * SCREEN_HEIGHT:
            start_shifting = True

        # todo: world.shift_world(world_shift_speed)  # world should shift up
        if player.rect.top > SCREEN_HEIGHT + player.rect.height:
            end_game(score)
            return
        large_text = pygame.font.Font('freesansbold.ttf', 40)
        text_surf, text_rect = text_objects(str(score), large_text)
        text_rect.topleft = text_topleft

        screen.fill(BACKGROUND)
        world.draw(screen)
        all_sprites_list.draw(screen)
        screen.blit(text_surf, text_rect)

        pygame.display.update()
        clock.tick(60)




main_menu()
    # end_game(100)
