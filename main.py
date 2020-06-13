import base64
import io
import os
import pathlib
import platform
import sys
import time
import math
import json

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'True'

from pygame import K_w, K_a, K_d, K_UP, K_LEFT, K_RIGHT, K_ESCAPE, K_F4, K_p, K_RALT, K_LALT, K_SPACE, \
    MOUSEBUTTONDOWN, QUIT, KEYUP, KEYDOWN, K_TAB, K_v, K_h, K_BACKSPACE, K_q, K_m, K_r
import pygame


VERSION = '1.9'
if os.path.exists('.env'):
    with open('.env') as f:
        for line in f.read().splitlines():
            key, value = line.split('=')
            os.environ[key] = value


def save_config():
    with open(CONFIG_FILE, 'w') as fp:
        json.dump(config, fp)


# CONSTANTS
DEBUG = os.getenv('DEBUG', False)
WHITE = 255, 255, 255
BLACK = 0, 0, 0
# GREEN = 50, 205, 50
GREEN = 40, 175, 99
DARK_GREEN = 0, 128, 0
LIGHT_BLUE = 0, 191, 255
GREY = 204, 204, 204
BLUE = 33, 150, 243
BACKGROUND = 174, 222, 203
WORLD_SHIFT_SPEED_PERCENT = 0.00135
FONT_BOLD ='assets/fonts/OpenSans-SemiBold.ttf'
FONT_REG = 'assets/fonts/OpenSans-Regular.ttf'
FONT_LIGHT ='assets/fonts/OpenSans-Light.ttf'
CONFIG_FILE = 'config.json'
config = { 'jump_sound': True, 'background_music': True, 'high_scores': [0, 0, 0, 0, 0, 0, 0, 0, 0,] }
music_playing = False

try:
    with open(CONFIG_FILE) as fp:
        config = json.load(fp)
except FileNotFoundError:
    save_config()


def text_objects(text, font, colour=BLACK):
    text_surface = font.render(text, True, colour)
    return text_surface, text_surface.get_rect()


def save_score(user_score: int) -> bool:
    """
    Takes a score and saves to file if it is a top 10 score else it returns False
    :param user_score: the score of the user
    :param path: high score text file location
    :return: boolean indicating whether the score was a top 10 score
    """
    scores = config['high_scores']
    placement = None
    for i, score in enumerate(scores):
        if user_score > score:
            placement = i
            break
    if placement is not None:
        scores.insert(placement, user_score)
        scores.pop()
        save_config()
        return True
    return False


def button(text, x, y, w, h, inactive_colour, active_colour, click, text_colour=BLACK):
    mouse = pygame.mouse.get_pos()
    # focus = pygame.mouse.get_focused()
    return_value = False
    if x < mouse[0] < x + w and y < mouse[1] < y + h:  # if mouse is hovering the button
        pygame.draw.rect(SCREEN, active_colour, (x, y, w, h))
        if click and pygame.time.get_ticks() > 100: return_value = True
        # if click and action is not None and pygame.time.get_ticks() - ticks > 100: action()
    else: pygame.draw.rect(SCREEN, inactive_colour, (x, y, w, h))

    text_surf, text_rect = text_objects(text, SMALL_TEXT, colour=text_colour)
    text_rect.center = (x + w / 2, y + h / 2)
    SCREEN.blit(text_surf, text_rect)
    return return_value


def toggle_btn(text, x, y, w, h, click, text_colour=BLACK, enabled=True):
    mouse = pygame.mouse.get_pos()
    # focus = pygame.mouse.get_focused()
    if enabled:
        # pygame.draw.rect(SCREEN, on_colour, (x, y, w, h))
        pygame.draw.rect(SCREEN, LIGHT_BLUE, (x + 350, y, 30, h // 2 - 1))
        pygame.draw.circle(SCREEN, LIGHT_BLUE, (int(x + 350), y + h // 4), h // 4)
        pygame.draw.circle(SCREEN, LIGHT_BLUE, (int(x + 380), y + h // 4), h // 4)
        pygame.draw.circle(SCREEN, WHITE, (int(x + 380), y + h // 4), h // 5)
        # if click and action is not None and pygame.time.get_ticks() - ticks > 100: action()
    else:
        pygame.draw.rect(SCREEN, GREY, (x + 350, y, 30, h // 2 - 1))
        pygame.draw.circle(SCREEN, GREY, (int(x + 350), y + h // 4), h // 4)
        pygame.draw.circle(SCREEN, GREY, (int(x + 380), y + h // 4), h // 4)
        pygame.draw.circle(SCREEN, WHITE, (int(x + 350), y + h // 4), h // 5)
    text_surf, text_rect = text_objects(text, MEDIUM_TEXT, colour=text_colour)
    text_rect.topleft = (x, y)
    SCREEN.blit(text_surf, text_rect)
    return x < mouse[0] < x + w and y < mouse[1] < y + h and click and pygame.time.get_ticks() > 100



def view_high_scores():
    SCREEN.fill(WHITE)
    text_surf, text_rect = text_objects('High Scores', MENU_TEXT)
    text_rect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 6))
    SCREEN.blit(text_surf, text_rect)
    for i, score in enumerate(config['high_scores']):
        text_surf, text_rect = text_objects(str(score), LARGE_TEXT)
        text_rect.center = ((SCREEN_WIDTH / 2), ((i/1.5 + 3) * SCREEN_HEIGHT / 11))
        SCREEN.blit(text_surf, text_rect)
    on_high_scores = True
    pygame.display.update()
    button_rects = [((SCREEN_WIDTH - BUTTON_WIDTH) / 2, SCREEN_HEIGHT * 4 / 5, BUTTON_WIDTH, BUTTON_HEIGHT)]
    while on_high_scores:
        click = False
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            alt_f4 = (event.type == KEYDOWN and event.key == pygame.K_F4
                      and (pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]))
            if event.type == QUIT or alt_f4: sys.exit()
            elif event.type == KEYDOWN and (event.key == K_ESCAPE or event.key == K_BACKSPACE): on_high_scores = False
            elif event.type == MOUSEBUTTONDOWN: click = True
        if button('B A C K', *button_rects[0], BLUE, LIGHT_BLUE, click, text_colour=WHITE): break
        pygame.display.update(button_rects)
        clock.tick(60)


def main_menu_setup():
    SCREEN.fill(WHITE)
    text_surf, text_rect = text_objects('Jungle Climb', MENU_TEXT)
    text_rect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 4))
    SCREEN.blit(text_surf, text_rect)
    text_surf, text_rect = text_objects(f'v{VERSION}', SMALL_TEXT)
    text_rect.center = ((SCREEN_WIDTH * 0.98), (SCREEN_HEIGHT * 0.98))
    SCREEN.blit(text_surf, text_rect)
    text_surf, text_rect = text_objects('Created by Elijah Lopez', LARGE_TEXT)
    text_rect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT * 0.84))
    SCREEN.blit(text_surf, text_rect)
    pygame.display.update()


def main_menu():
    global ticks
    main_menu_setup()
    ticks = pygame.time.get_ticks()
    start_game = view_hs = False
    button_rects = [((SCREEN_WIDTH - BUTTON_WIDTH) / 2, SCREEN_HEIGHT * 5 / 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                    ((SCREEN_WIDTH - BUTTON_WIDTH) / 2, SCREEN_HEIGHT * 6 / 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                    ((SCREEN_WIDTH - BUTTON_WIDTH) / 2, SCREEN_HEIGHT * 7 / 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                    ((SCREEN_WIDTH - BUTTON_WIDTH) / 2, SCREEN_HEIGHT * 8 / 13, BUTTON_WIDTH, BUTTON_HEIGHT)]
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

        if button('S T A R T  G A M E', *button_rects[0], BLUE, LIGHT_BLUE, click, text_colour=WHITE): start_game = True
        elif button('V I E W  H I G H S C O R E S', *button_rects[1], BLUE, LIGHT_BLUE, click, text_colour=WHITE) or view_hs:
            view_high_scores()
            view_hs = False
            main_menu_setup()
        elif button('S E T T I N G S', *button_rects[2], BLUE, LIGHT_BLUE, click, text_colour=WHITE):
            settings_menu()
            main_menu_setup()
        elif button('Q U I T  G A M E', *button_rects[3], BLUE, LIGHT_BLUE, click, text_colour=WHITE): sys.exit()
        if start_game:
            while start_game: start_game = game() == 'Restart'
            main_menu_setup()
        pygame.display.update(button_rects)
        clock.tick(60)


def settings_menu():
    SCREEN.fill(WHITE)
    text_surf, text_rect = text_objects('Settings', MENU_TEXT)
    text_rect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 4))
    SCREEN.blit(text_surf, text_rect)
    pygame.display.update()
    button_rects = [((SCREEN_WIDTH - BUTTON_WIDTH) // 2, SCREEN_HEIGHT * 5 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                    ((SCREEN_WIDTH - BUTTON_WIDTH) // 2, SCREEN_HEIGHT * 6 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                    ((SCREEN_WIDTH - BUTTON_WIDTH) // 2, SCREEN_HEIGHT * 7 // 13, BUTTON_WIDTH, BUTTON_HEIGHT)]
    while True:
        click = False
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            alt_f4 = (event.type == KEYDOWN and (event.key == K_F4 and (pressed_keys[K_LALT] or pressed_keys[K_RALT])
                      or event.key == K_q))
            if event.type == QUIT or alt_f4: sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE: return
            elif event.type == KEYDOWN and event.key == K_SPACE: start_game = True
            elif event.type == KEYDOWN and (event.key == K_v or event.key == K_h): view_hs = True
            elif event.type == MOUSEBUTTONDOWN: click = True
        # if toggle_btn('Jump Sound', *button_rects[0], BLUE, LIGHT_BLUE, click, enabled=config['background_music']):
        if toggle_btn('Background Music', *button_rects[0], click, enabled=config['background_music']):
            config['background_music'] = not config['background_music']
            save_config()
        elif toggle_btn('Jump Sound', *button_rects[1], click, enabled=config['jump_sound']):
            config['jump_sound'] = not config['jump_sound'];
            save_config()
        elif button('B A C K', *button_rects[2], BLUE, LIGHT_BLUE, click, text_colour=WHITE): return
        pygame.display.update(button_rects)
        clock.tick(60)


def pause_menu_setup(background):
    SCREEN.blit(background, (0, 0))
    background = SCREEN.copy()
    text_surf, text_rect = text_objects('Pause Menu', MENU_TEXT)
    text_rect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 4))
    SCREEN.blit(text_surf, text_rect)
    pygame.display.update()
    return background


def pause_menu(player):
    paused = True
    facing_left = player.facing_left  # store the pre-pause value in case player doesn't hold a right/left key down
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA, 32)
    background.fill((255, 255, 255, 160))
    background = pause_menu_setup(background)
    # SCREEN.blit(background, (0, 0))
    # text_surf, text_rect = text_objects('Pause Menu', MENU_TEXT)
    # text_rect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 4))
    # SCREEN.blit(text_surf, text_rect)
    # pygame.display.update()
    button_rects = [((SCREEN_WIDTH - BUTTON_WIDTH) / 2, SCREEN_HEIGHT * 5 / 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                    ((SCREEN_WIDTH - BUTTON_WIDTH) / 2, SCREEN_HEIGHT * 6 / 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                    ((SCREEN_WIDTH - BUTTON_WIDTH) / 2, SCREEN_HEIGHT * 7 / 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                    ((SCREEN_WIDTH - BUTTON_WIDTH) / 2, SCREEN_HEIGHT * 8 / 13, BUTTON_WIDTH, BUTTON_HEIGHT)]
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

        if button('R E S U M E', *button_rects[0], BLUE, LIGHT_BLUE, click, text_colour=WHITE):
            return 'Resume'
        if button('M A I N  M E N U', *button_rects[1], BLUE, LIGHT_BLUE, click, text_colour=WHITE):
            return 'Main Menu'
        if button('S E T T I N G S', *button_rects[2], BLUE, LIGHT_BLUE, click, text_colour=WHITE):
            settings_menu()
            pause_menu_setup(background)
        if button('Q U I T  G A M E', *button_rects[3], BLUE, LIGHT_BLUE, click, text_colour=WHITE):
            sys.exit()
        pygame.display.update(button_rects)
        clock.tick(60)
    return 'Resume'


def end_game_setup(score, surface_copy=None):
    if surface_copy is not None:
        SCREEN.blit(surface_copy, (0, 0))
    else:
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA, 32)
        background.fill((255, 255, 255, 160))
        SCREEN.blit(background, (0, 0))
        text_surf, text_rect = text_objects('Game Over', MENU_TEXT)
        text_rect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 4))
        SCREEN.blit(text_surf, text_rect)
        text_surf, text_rect = text_objects(f'You scored {score}', LARGE_TEXT)
        text_rect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT * 8 / 21))
        SCREEN.blit(text_surf, text_rect)
        surface_copy = pygame.display.get_surface().copy()
    pygame.display.update()
    return surface_copy


def end_game(score):
    view_hs = False
    end_screen_copy = end_game_setup(score)
    button_width, button_height = SCREEN_WIDTH * 0.21, SCREEN_HEIGHT * 0.062
    if save_score(score): pass  # Show "You got a high score!"
    button_rects = [((SCREEN_WIDTH - BUTTON_WIDTH) / 2, SCREEN_HEIGHT * 6 / 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                    ((SCREEN_WIDTH - BUTTON_WIDTH) / 2, SCREEN_HEIGHT * 7 / 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                    ((SCREEN_WIDTH - BUTTON_WIDTH) / 2, SCREEN_HEIGHT * 8 / 13, BUTTON_WIDTH, BUTTON_HEIGHT)]
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
        if button('R E S T A R T', *button_rects[0], BLUE, LIGHT_BLUE, click, text_colour=WHITE):
            return 'Restart'
        elif button('M A I N  M E N U', *button_rects[1], BLUE, LIGHT_BLUE, click, text_colour=WHITE):
            main_menu()
            return 'Main Menu'
        elif button('V I E W  H I G H S C O R E S', *button_rects[2], BLUE, LIGHT_BLUE, click, text_colour=WHITE) or view_hs:
            view_high_scores()
            view_hs = False
            end_game_setup(score, end_screen_copy)
        pygame.display.update(button_rects)
        clock.tick(60)


def game():
    global music_playing
    restart, game_over, start_shifting = False, False, False
    if not music_playing and config['background_music']:
        pygame.mixer.Channel(0).play(MUSIC_SOUND, loops=-1)
        music_playing = True
    world = World()
    player = Player(world)
    player.force_stop()
    player_sprite_group = pygame.sprite.Group(player)
    world.player = player
    world_shift_speed = round(WORLD_SHIFT_SPEED_PERCENT * SCREEN_HEIGHT)  # NOTE: percent of screen
    speed_increment = world_shift_speed
    MAX_SPEED = speed_increment * 4
    speed_level, score = 1, 0
    shift_thresh = 0.75 * SCREEN_HEIGHT
    SCREEN.fill(BACKGROUND)
    world.draw(SCREEN)
    pygame.display.update()
    while True:
        # TODO: make background with vines
        if not pygame.mouse.get_focused():
            if music_playing:
                pygame.mixer.Channel(0).pause()
                music_playing = False
            if pause_menu(player) == 'Main Menu': return 'Main Menu'
            if config['background_music']:
                pygame.mixer.Channel(0).unpause()
                music_playing = True
        player_old_rect = player.rect.copy()
        dirty_rects = []
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
                elif event.key in (K_UP, K_w, K_SPACE): player.jump(config['jump_sound'])
                elif event.key == K_ESCAPE and not pressed_keys[K_p] or event.key == K_p and not pressed_keys[K_ESCAPE]:
                    pygame.mixer.Channel(0).pause()
                    music_playing = False
                    if pause_menu(player) == 'Main Menu': return 'Main Menu'
                    if config['background_music']:
                        pygame.mixer.Channel(0).unpause()
                        music_playing = True
                elif DEBUG:
                    if event.key == pygame.K_EQUALS: world.shift_world(shift_x=30)
                    elif event.key == pygame.K_MINUS: world.shift_world(shift_x=-30)
                    elif event.key == K_TAB: print(player.rect)
            if event.type == KEYUP:
                if event.key in (K_LEFT, K_a, K_RIGHT, K_d):
                    player.stop(pressed_keys)

        player_new_rect = player.update()

        if start_shifting:
            # if pygame.time.get_ticks() % 2 == 0:
            world.shift_world(world_shift_speed)
            score += 1
            # if score > 1000 * speed_level:
            #     world_shift_speed = min(world_shift_speed + speed_increment, MAX_SPEED)
            #     speed_level += 1
            if score > 1000 * world_shift_speed + (world_shift_speed - 1) * 1000:
                world_shift_speed = min(world_shift_speed * 2, MAX_SPEED)
        elif player.rect.top < shift_thresh: start_shifting = True

        if DEBUG:
            custom_text = f'FPS: {round(clock.get_fps())}'
            # custom_text = f'Platform Sprites: {len(world.platform_list.sprites())}'
            text_surf, score_rect = text_objects(custom_text, SCORE_TEXT, WHITE)
        else: text_surf, score_rect = text_objects(str(score), SCORE_TEXT, WHITE)
        score_rect.topright = SCORE_ANCHOR
        score_bg_w, text_bg_h = text_surf.get_size()
        score_bg_w += 15
        score_bg = pygame.Surface((score_bg_w, text_bg_h), pygame.SRCALPHA, 32)
        score_bg.fill((50, 50, 50, 160))
        score_bg.blit(text_surf, (5, 0))
        SCREEN.fill(BACKGROUND)
        player_union_rect = player_new_rect.union(player_old_rect)
        # pygame.draw.rect(SCREEN, BACKGROUND, player_old_rect)
        dirty_rects.append(player_union_rect)
        player_sprite_group.draw(SCREEN)
        world.draw(SCREEN)
        SCREEN.blit(score_bg, score_rect)
        # a = [SCORE_ANCHOR[0] - score_bg_w * 0.8, SCORE_ANCHOR[1], score_bg_w, text_bg_h]
        # dirty_rects.append(a)
        # pygame.display.update(dirty_rects)
        pygame.display.update()
        clock.tick(60)
        if player.rect.top > SCREEN_HEIGHT + player.rect.height // 2:
            game_over = True
            if music_playing:
                pygame.mixer.Channel(0).stop()
                music_playing = False
            break
    if game_over: return end_game(score)  # always runs


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
        SCREEN = pygame.display.set_mode(SIZE, pygame.FULLSCREEN)
    else:
        SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = int(0.75 * SCREEN_WIDTH), int(0.75 * SCREEN_HEIGHT)
        SCREEN = pygame.display.set_mode(SIZE)

    BUTTON_WIDTH = SCREEN_WIDTH * 0.625 // 3
    BUTTON_HEIGHT = SCREEN_HEIGHT * 5 // 81
    SCORE_ANCHOR = SCREEN_WIDTH - 8, -5

    window_icon = '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'
    window_icon = pygame.image.load(io.BytesIO(base64.b64decode(window_icon)))
    pygame.display.set_icon(window_icon)
    MENU_TEXT, LARGE_TEXT = pygame.font.Font(FONT_LIGHT, int(110 / 1080 * SCREEN_HEIGHT)), pygame.font.Font(FONT_REG, int(40 / 1080 * SCREEN_HEIGHT))
    MEDIUM_TEXT = pygame.font.Font(FONT_LIGHT, int(35 / 1440 * SCREEN_HEIGHT))
    SMALL_TEXT, SCORE_TEXT = pygame.font.Font(FONT_BOLD, int(25 / 1440 * SCREEN_HEIGHT)), pygame.font.Font(FONT_REG, int(40 / 1440 * SCREEN_HEIGHT))
    MUSIC_SOUND = pygame.mixer.Sound('assets/audio/background_music.ogg')
    pygame.display.set_caption('Jungle Climb')
    music_playing = False
    clock = pygame.time.Clock()
    ticks = 0
    from objects import *
    main_menu()
