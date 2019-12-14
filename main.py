import pathlib
import sys
import os
import time
import platform
import io
import base64

from pygame import K_w, K_a, K_d, K_UP, K_LEFT, K_RIGHT, K_ESCAPE, K_F4, K_p, K_RALT, K_LALT, K_SPACE, \
    MOUSEBUTTONDOWN, QUIT, KEYUP, KEYDOWN, K_TAB, K_v, K_h, K_BACKSPACE, K_q, K_m, K_r
import pygame


VERSION = '1.6'
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
VERDANA = 'Assets/Fonts/Verdana.ttf'


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
            f.writelines([str(user_score) + '\n'] + ['0\n'] * 8)
        return True


def get_scores(path: str = game_folder + r'\High Scores.txt') -> list:
    """
    Gets the list of top 10 scores
    :param path: path to the scores
    :return: list of the scores
    """

    try:
        with open(path) as f:
            return f.read().splitlines()
    except FileNotFoundError:
        temp_scores = ['0' for _ in range(9)]
        pathlib.Path(game_folder).mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            f.writelines(map(lambda x: x + '\n', temp_scores))
        return temp_scores


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
        clock.tick(60)


def main_menu_setup():
    screen.fill(WHITE)
    text_surf, text_rect = text_objects('Jungle Climb', LARGE_TEXT)
    text_rect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 4))
    screen.blit(text_surf, text_rect)
    text_surf, text_rect = text_objects(f'v{VERSION}', SMALL_TEXT)
    text_rect.center = ((SCREEN_WIDTH * 0.98), (SCREEN_HEIGHT * 0.98))
    screen.blit(text_surf, text_rect)
    text_surf, text_rect = text_objects('Created by Elijah Lopez', MEDIUM_TEXT)
    text_rect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT * 0.84))
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
    # TODO: stop music
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
                elif event.key == K_q: sys.exit()
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
        clock.tick(60)
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
        clock.tick(60)


def game():
    restart, game_over, start_shifting = False, False, False
    # if not music_playing: pygame.mixer.Channel(0).play(MUSIC_SOUND, loops=-1)
    world = World()
    player = Player(world)
    player.force_stop()
    all_sprites_list = pygame.sprite.Group(player)
    world.player = player
    world_shift_speed = round(WORLD_SHIFT_SPEED_PERCENT * SCREEN_HEIGHT)  # NOTE: percent of screen
    speed_increment = world_shift_speed
    MAX_SPEED = speed_increment * 4
    speed_level, score = 1, 0
    text_anchor = round(0.997 * SCREEN_WIDTH), 0
    start = time.time()
    while True:
        delta = time.time() - start
        # print(delta)  # somehow reduces lag
        start = time.time()
        # TODO: make background with vines
        if not pygame.mouse.get_focused():
            # pygame.mixer_music.Channel(0).pause()
            # music_playing = False
            if pause_menu(player) == 'Main Menu': return 'Main Menu'
            # pygame.mixer_music.Channel(0).resume()
            # music_playing = True
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
                    # pygame.mixer_music.Channel(0).pause()
                    # music_playing = False
                    if pause_menu(player) == 'Main Menu': return 'Main Menu'
                    # pygame.mixer_music.Channel(0).resume()
                    # music_playing = True
                # elif event.key == pygame.K_EQUALS: world.shift_world(shift_x=30)
                # elif event.key == pygame.K_MINUS: world.shift_world(shift_x=-30)
                # elif event.key == K_TAB: pass
            if event.type == KEYUP:
                if event.key in (K_LEFT, K_a, K_RIGHT, K_d):
                    player.stop(pressed_keys)
        player.update()
        if start_shifting:
            # if pygame.time.get_ticks() % 2 == 0:
            world.shift_world(world_shift_speed)
            score += 1
            # if score > 1000 * speed_level:
            #     world_shift_speed = min(world_shift_speed + speed_increment, MAX_SPEED)
            #     speed_level += 1
            if score > 1000 * world_shift_speed + (world_shift_speed - 1) * 1000:
                world_shift_speed = min(world_shift_speed * 2, MAX_SPEED)
        elif player.rect.top < 0.75 * SCREEN_HEIGHT: start_shifting = True
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
        if player.rect.top > SCREEN_HEIGHT + player.rect.height:
            game_over = True
            # pygame.mixer_music.Channel(0).stop()
            # music_playing = False
            break
        clock.tick(60)
    if game_over: return end_game(score) # always runs


if __name__ == '__main__':
    # Initialization
    if platform.system() == 'Windows':
        from ctypes import windll
        windll.user32.SetProcessDPIAware()
    os.environ['SDL_VIDEO_CENTERED'] = '1'  # center display
    pygame.mixer.init(frequency=44100, buffer=512)
    pygame.init()
    SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
    FULLSCREEN = True
    if FULLSCREEN:
        screen = pygame.display.set_mode(SIZE, pygame.FULLSCREEN)
    else:
        SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = int(0.75 * SCREEN_WIDTH), int(0.75 * SCREEN_HEIGHT)
        screen = pygame.display.set_mode(SIZE)

    window_icon = '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'
    window_icon = pygame.image.load(io.BytesIO(base64.b64decode(window_icon)))
    pygame.display.set_icon(window_icon)
    LARGE_TEXT, MEDIUM_TEXT = pygame.font.Font(VERDANA, int(110 / 1080 * SCREEN_HEIGHT)), pygame.font.Font(VERDANA, int(40 / 1080 * SCREEN_HEIGHT))
    SMALL_TEXT, SCORE_TEXT = pygame.font.Font(VERDANA, int(25 / 1440 * SCREEN_HEIGHT)), pygame.font.Font(VERDANA, int(40 / 1440 * SCREEN_HEIGHT))    
    MUSIC_SOUND = pygame.mixer.Sound('Assets/Audio/background_music.ogg')
    pygame.display.set_caption('Jungle Climb')
    music_playing = False
    clock = pygame.time.Clock()
    ticks = 0
    from objects import *
    main_menu()
