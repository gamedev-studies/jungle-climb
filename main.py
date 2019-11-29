import pathlib
import sys
import os
from ctypes import windll
import time

from pygame import K_w, K_a, K_d, K_UP, K_LEFT, K_RIGHT, K_ESCAPE, K_F4, K_p, K_RALT, K_LALT, K_SPACE, \
    MOUSEBUTTONDOWN, QUIT, KEYUP, KEYDOWN, K_TAB, K_v, K_h, K_BACKSPACE, K_q, K_m, K_r
import pygame

# CONSTANTS
WHITE = 255, 255, 255
BLACK = 0, 0, 0
# GREEN = 50, 205, 50
GREEN = 40, 175, 99
DARK_GREEN = 0, 128, 0
LIGHT_BLUE = 0, 191, 255
BLUE = 33, 150, 243
BACKGROUND = 174, 222, 203
WORLD_SHIFT_SPEED_PERCENT = 0.00135
game_folder = os.path.expanduser(r'~\Documents\Jungle Climb')

windll.shcore.SetProcessDpiAwareness(1)
os.environ['SDL_VIDEO_CENTERED'] = '1'  # center display
pygame.init()  # initialize pygame
current_w, current_h = pygame.display.Info().current_w, pygame.display.Info().current_h

FULLSCREEN = True
if FULLSCREEN:
    SCREEN_WIDTH, SCREEN_HEIGHT = current_w, current_h
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
else:
    SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = int(0.75 * current_w), int(0.75 * current_h)
    screen = pygame.display.set_mode(SIZE)

LARGE_TEXT, MEDIUM_TEXT = pygame.font.Font('Fonts/Verdana.ttf', int(110 / 1080 * current_h)), pygame.font.Font('Fonts/Verdana.ttf', int(40 / 1080 * current_h))
SMALL_TEXT, SCORE_TEXT = pygame.font.Font('Fonts/Verdana.ttf', int(25 / 1440 * current_h)), pygame.font.Font('Fonts/Verdana.ttf', int(40 / 1440 * current_h))

pygame.display.set_caption('Jungle Climb')
clock = pygame.time.Clock()
ticks = 0

if getattr(sys, 'frozen', False): os.chdir(sys._MEIPASS)
from objects import *


def text_objects(text, font, colour=BLACK):
    text_surface = font.render(text, True, colour)
    return text_surface, text_surface.get_rect()


def save_score(user_score: int, path: str = game_folder + '/High Scores.txt') -> bool:
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


def button(text, x, y, w, h, inactive_colour, active_colour, click, text_colour=BLACK):
    mouse = pygame.mouse.get_pos()
    # focus = pygame.mouse.get_focused()
    return_value = False
    if x < mouse[0] < x + w and y < mouse[1] < y + h:  # if mouse is hovering the button
        pygame.draw.rect(screen, active_colour, (x, y, w, h))
        if click and pygame.time.get_ticks() > 100: return_value = True
        # if click and action is not None and pygame.time.get_ticks() - ticks > 100: action()
    else: pygame.draw.rect(screen, inactive_colour, (x, y, w, h))

    text_surf, text_rect = text_objects(text, SMALL_TEXT, colour=text_colour)
    text_rect.center = (x + w / 2, y + h / 2)
    screen.blit(text_surf, text_rect)
    return return_value


def view_high_scores():
    screen.fill(WHITE)
    text_surf, text_rect = text_objects('High Scores', LARGE_TEXT)
    text_rect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 6))
    screen.blit(text_surf, text_rect)
    button_width = SCREEN_WIDTH * 0.625 / 3
    button_height = SCREEN_HEIGHT * 5 / 81
    for i, score in enumerate(get_scores()):
        text_surf, text_rect = text_objects(score, MEDIUM_TEXT)
        text_rect.center = ((SCREEN_WIDTH / 2), ((i/1.5 + 3) * SCREEN_HEIGHT / 11))
        screen.blit(text_surf, text_rect)
    on_high_scores = True
    while on_high_scores:
        click = False
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            alt_f4 = (event.type == KEYDOWN and event.key == pygame.K_F4
                      and (pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]))
            if event.type == QUIT or alt_f4: sys.exit()
            elif event.type == KEYDOWN and (event.key == K_ESCAPE or event.key == K_BACKSPACE): on_high_scores = False
            elif event.type == MOUSEBUTTONDOWN: click = True
        if button('B A C K', (SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT * 4 / 5,
                  button_width, button_height, BLUE, LIGHT_BLUE, click, text_colour=WHITE): break
        pygame.display.update()
        # clock.tick(60)


def main_menu_setup():
    screen.fill(WHITE)
    text_surf, text_rect = text_objects('Jungle Climb', LARGE_TEXT)
    text_rect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 4))
    screen.blit(text_surf, text_rect)


def main_menu():
    global ticks
    main_menu_setup()
    button_width = SCREEN_WIDTH * 0.20833333333333334
    button_height = SCREEN_HEIGHT * 0.06172839506172839
    ticks = pygame.time.get_ticks()
    start_game = view_hs = False
    while True:
        click = False
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            alt_f4 = (event.type == KEYDOWN and (event.key == K_F4
                      and (pressed_keys[K_LALT] or pressed_keys[K_RALT])
                      or event.key == K_q or event.key == K_ESCAPE))
            if event.type == QUIT or alt_f4: sys.exit()
            elif event.type == KEYDOWN and event.key == K_SPACE: start_game = True
            elif event.type == KEYDOWN and (event.key == K_v or event.key == K_h): view_hs = True
            elif event.type == MOUSEBUTTONDOWN: click = True

        if button('S T A R T  G A M E', (SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT * 5 / 13,
                  button_width, button_height, BLUE, LIGHT_BLUE, click, text_colour=WHITE): start_game = True            
        elif button('V I E W  H I G H S C O R E S', (SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT * 6 / 13,
                  button_width, button_height, BLUE, LIGHT_BLUE, click, text_colour=WHITE) or view_hs:
            view_high_scores()
            view_hs = False
            main_menu_setup()
        elif button('Q U I T  G A M E', (SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT * 7 / 13,
                  button_width, button_height, BLUE, LIGHT_BLUE, click, text_colour=WHITE): sys.exit()
        if start_game:
            while start_game: start_game = game() == 'Restart'
            main_menu_setup()
        pygame.display.update()
        clock.tick(60)


def pause_menu(player):
    paused = True
    facing_left = player.facing_left  # store the pre-pause value in case player doesn't hold a right/left key down
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA, 32)
    background.fill((255, 255, 255, 160))
    screen.blit(background, (0, 0))

    text_surf, text_rect = text_objects('Pause Menu', LARGE_TEXT)
    text_rect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 4))
    screen.blit(text_surf, text_rect)

    button_width = SCREEN_WIDTH * 0.20833333333333334
    button_height = SCREEN_HEIGHT * 0.06172839506172839
    while paused:
        click = False
        pks = pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            alt_f4 = (event.type == KEYDOWN and event.key == K_F4
                      and (pressed_keys[K_LALT] or pressed_keys[K_RALT]))
            if event.type == QUIT or alt_f4: sys.exit()
            elif event.type == KEYDOWN:
                right_key = event.key == K_RIGHT and not pks[K_d] or event.key == K_d and not pks[K_RIGHT]
                left_key = event.key == K_LEFT and not pks[K_a] or event.key == K_a and not pks[K_LEFT]
                if right_key: player.go_right()
                elif left_key: player.go_left()
                elif event.key in (pygame.K_ESCAPE, pygame.K_p): paused = False
                elif event.key == K_m: return 'Main Menu'
                elif event.key == K_SPACE: return 'Resume'
            elif event.type == MOUSEBUTTONDOWN: click = True
            elif event.type == KEYUP:
                if event.key in (K_d, K_RIGHT, K_a, K_LEFT):
                    player.stop(pygame.key.get_pressed())
                    player.facing_left = facing_left

        if button('R E S U M E', (SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT * 5 / 13,
                  button_width, button_height, BLUE, LIGHT_BLUE, click, text_colour=WHITE):
            return 'Resume'

        if button('M A I N  M E N U', (SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT * 6 / 13,
                  button_width, button_height, BLUE, LIGHT_BLUE, click, text_colour=WHITE):
            return 'Main Menu'

        if button('Q U I T  G A M E', (SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT * 7 / 13,
                  button_width, button_height, BLUE, LIGHT_BLUE, click, text_colour=WHITE):
            sys.exit()
        pygame.display.update()
        # clock.tick(60)
    return 'Resume'


def end_game_setup(score, from_copy=None):
    if from_copy is not None:
        screen.blit(from_copy, (0, 0))
        return from_copy
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA, 32)
    background.fill((255, 255, 255, 160))
    screen.blit(background, (0, 0))
    text_surf, text_rect = text_objects('Game Over', LARGE_TEXT)
    text_rect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 4))
    screen.blit(text_surf, text_rect)
    text_surf, text_rect = text_objects(f'You scored {score}', MEDIUM_TEXT)
    text_rect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT * 8 / 21))
    screen.blit(text_surf, text_rect)
    return pygame.display.get_surface().copy()


def end_game(score):
    view_hs = False
    end_screen_copy = end_game_setup(score)
    button_width, button_height = SCREEN_WIDTH * 0.21, SCREEN_HEIGHT * 0.062
    if save_score(score): pass  # Show "You got a high score!"
    while True:
        click, pressed_keys = False, pygame.key.get_pressed()
        for event in pygame.event.get():
            alt_f4 = (event.type == KEYDOWN and event.key == pygame.K_F4
                      and (pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]))
            if event.type == QUIT or alt_f4: sys.exit()
            elif event.type == KEYDOWN and (event.key == K_ESCAPE or event.key == K_m): return 'Main Menu'
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_r): return 'Restart'
            elif event.type == KEYDOWN and (event.key == K_v or event.key == K_h): view_hs = True
            elif event.type == MOUSEBUTTONDOWN: click = True
        if button('R E S T A R T', (SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT * 6 / 13,
                  button_width, button_height, BLUE, LIGHT_BLUE, click, text_colour=WHITE):
            # game()
            return 'Restart'
        elif button('M A I N  M E N U', (SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT * 7 / 13,
                    button_width, button_height, BLUE, LIGHT_BLUE, click, text_colour=WHITE):
            main_menu()
            return 'Main Menu'
        elif button('V I E W  H I G H S C O R E S', (SCREEN_WIDTH - button_width) / 2, SCREEN_HEIGHT * 8 / 13,
                    button_width, button_height, BLUE, LIGHT_BLUE, click, text_colour=WHITE) or view_hs:
            view_high_scores()
            view_hs = False
            end_game_setup(score, end_screen_copy)
        pygame.display.update()
        # clock.tick(60)


 
def game():
    restart, game_over, start_shifting = False, False, False
    world = World()
    player = Player(world)
    player.force_stop()
    all_sprites_list = pygame.sprite.Group(player)
    world.player = player
    world_shift_speed = round(WORLD_SHIFT_SPEED_PERCENT * SCREEN_HEIGHT)  # NOTE: percent of screen
    score = 0
    text_anchor = round(0.997 * SCREEN_WIDTH), 0
    start = time.time()
    while True:
        delta = time.time() - start
        # print(delta)  # somehow reduces lag
        start = time.time()
        # TODO: make background with vines
        if not pygame.mouse.get_focused():
            if pause_menu(player) == 'Main Menu': return 'Main Menu'
            # TODO: return something
            # continue ?
        for event in pygame.event.get():
            pressed_keys = pygame.key.get_pressed()
            alt_f4 = (event.type == KEYDOWN and event.key == K_F4
                      and (pressed_keys[K_LALT] or pressed_keys[K_RALT]))
            if event.type == QUIT or alt_f4: sys.exit()
            if event.type == KEYDOWN:
                right_key: bool = event.key == K_RIGHT and not pressed_keys[
                    pygame.K_d] or event.key == K_d and not pressed_keys[K_RIGHT]
                left_key: bool = event.key == K_LEFT and not pressed_keys[
                    pygame.K_a] or event.key == K_a and not pressed_keys[K_LEFT]
                if right_key: player.go_right()
                elif left_key: player.go_left()
                elif event.key in (K_UP, K_w, K_SPACE): player.jump()
                elif event.key == K_ESCAPE and not pressed_keys[K_p] or event.key == K_p and not pressed_keys[K_ESCAPE]:
                    if pause_menu(player) == 'Main Menu': return 'Main Menu'
                # elif event.key == K_TAB: print('test')
            if event.type == KEYUP:
                if event.key in (K_LEFT, K_a, K_RIGHT, K_d):
                    player.stop(pressed_keys)
        player.update()
        if start_shifting:
            # if pygame.time.get_ticks() % 2 == 0:
            world.shift_world(world_shift_speed)
            score += 1
            if score > 1000 * world_shift_speed + (world_shift_speed - 1) * 1000:
                world_shift_speed = min(world_shift_speed * 2, round(WORLD_SHIFT_SPEED_PERCENT * SCREEN_HEIGHT) * 4)
        elif player.rect.top < 0.75 * SCREEN_HEIGHT: start_shifting = True

        if player.rect.top > SCREEN_HEIGHT + player.rect.height:
            game_over = True
            break
        screen.fill(BACKGROUND)
        all_sprites_list.draw(screen)
        world.draw(screen)
        text_surf, text_rect = text_objects(str(score), SCORE_TEXT, WHITE)
        text_rect.topright = text_anchor
        # screen.blit(text_surf, text_rect)
        text_bg_w, text_bg_h = text_surf.get_size()
        text_bg_w *= 1.25
        text_bg = pygame.Surface((text_bg_w, text_bg_h), pygame.SRCALPHA, 32)
        text_bg.fill((50, 50, 50, 160))
        text_bg.blit(text_surf, (text_bg_w // 15, 0))
        screen.blit(text_bg, text_rect)
        pygame.display.update()
        clock.tick(60)
    if game_over: return end_game(score) # always runs


main_menu()
