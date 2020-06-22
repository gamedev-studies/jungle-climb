import base64
import io
import os
import platform
import sys
import json

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'True'

from pygame import gfxdraw, K_w, K_a, K_d, K_UP, K_LEFT, K_RIGHT, K_ESCAPE, K_F4, K_p, K_RALT, K_LALT, K_SPACE, \
    MOUSEBUTTONDOWN, QUIT, KEYUP, KEYDOWN, K_TAB, K_v, K_h, K_BACKSPACE, K_q, K_m, K_r
import pygame


VERSION = '1.11'
# CONSTANTS
WHITE = 255, 255, 255
BLACK = 0, 0, 0
# GREEN = 50, 205, 50
GREEN = 40, 175, 99
RED = 255, 0, 0
YELLOW = 250, 237, 39
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
config = {'DEBUG': False, 'jump_sound': True, 'background_music': True, 'show_fps': False, 'show_score': True,
          'high_scores': [0, 0, 0, 0, 0, 0, 0, 0, 0]}
music_playing = False


def save_config():
    with open(CONFIG_FILE, 'w') as fp:
        json.dump(config, fp, indent=4)


try:
    with open(CONFIG_FILE) as f:
        _config = json.load(f)
except FileNotFoundError: _config = {}
save_file = False
for k, v in config.items():
    try: config[k] = _config[k]
    except KeyError: save_file = True
if save_file: save_config()
DEBUG = config['DEBUG']

def text_objects(text, font, colour=BLACK):
    text_surface = font.render(text, True, colour)
    return text_surface, text_surface.get_rect()


def create_hud_text(text, color):
    text_surf, text_rect = text_objects(text, HUD_TEXT, color)
    text_rect.topleft = -2, -5
    bg_w, text_bg_h = text_surf.get_size()
    bg_w += 10
    bg = pygame.Surface((bg_w, text_bg_h), pygame.SRCALPHA, 32)
    bg.fill((50, 50, 50, 160))
    bg.blit(text_surf, (5, 0))
    return bg, text_rect


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
    else: pygame.draw.rect(SCREEN, inactive_colour, (x, y, w, h))

    text_surf, text_rect = text_objects(text, SMALL_TEXT, colour=text_colour)
    text_rect.center = (x + w / 2, y + h / 2)
    SCREEN.blit(text_surf, text_rect)
    return return_value


def draw_circle(surface, x, y, radius, color):
    gfxdraw.aacircle(surface, x, y, radius, color)
    gfxdraw.filled_circle(surface, x, y, radius, color)


def toggle_btn(text, x, y, w, h, click, text_colour=BLACK, enabled=True, draw_toggle=True, blit_text=True, enabled_color=LIGHT_BLUE, disabled_color=GREY):
    mouse = pygame.mouse.get_pos()
    # draw_toggle and blit_text are used to reduce redundant drawing and blitting (improves quality)
    if enabled and draw_toggle:
        pygame.draw.rect(SCREEN, WHITE, (x + TOGGLE_WIDTH - h // 4, y, TOGGLE_ADJ + h, h // 2))
        pygame.draw.rect(SCREEN, enabled_color, (x + TOGGLE_WIDTH, y, TOGGLE_ADJ, h // 2))
        draw_circle(SCREEN, int(x + TOGGLE_WIDTH), y + h // 4, h // 4, enabled_color)
        draw_circle(SCREEN, int(x + TOGGLE_WIDTH + TOGGLE_ADJ), y + h // 4, h // 4, enabled_color)
        draw_circle(SCREEN, int(x + TOGGLE_WIDTH + TOGGLE_ADJ), y + h // 4, h // 5, WHITE)  # small inner circle
    elif draw_toggle:
        pygame.draw.rect(SCREEN, WHITE, (x + TOGGLE_WIDTH - h // 4, y, TOGGLE_ADJ + h, h // 2))
        pygame.draw.rect(SCREEN, disabled_color, (x + TOGGLE_WIDTH, y, TOGGLE_ADJ, h // 2))
        draw_circle(SCREEN, int(x + TOGGLE_WIDTH), y + h // 4, h // 4, disabled_color)
        draw_circle(SCREEN, int(x + TOGGLE_WIDTH + TOGGLE_ADJ), y + h // 4, h // 4, disabled_color)
        draw_circle(SCREEN, int(x + TOGGLE_WIDTH), y + h // 4, h // 5, WHITE)  # small inner circle
    if blit_text:
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
                    ((SCREEN_WIDTH - BUTTON_WIDTH) // 2, SCREEN_HEIGHT * 7 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                    ((SCREEN_WIDTH - BUTTON_WIDTH) // 2, SCREEN_HEIGHT * 8 // 13, BUTTON_WIDTH, BUTTON_HEIGHT)]
    first_run = draw_bg_toggle = draw_jump_toggle = draw_show_fps = True
    while True:
        click = False
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            alt_f4 = (event.type == KEYDOWN and (event.key == K_F4 and (pressed_keys[K_LALT] or pressed_keys[K_RALT])
                      or event.key == K_q))
            if event.type == QUIT or alt_f4: sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE: return
            elif event.type == MOUSEBUTTONDOWN: click = True
        if toggle_btn('Background Music', *button_rects[0], click, enabled=config['background_music'],
                      draw_toggle=draw_bg_toggle, blit_text=first_run):
            config['background_music'] = not config['background_music']
            save_config()
            draw_bg_toggle = True
        elif toggle_btn('Jump Sound', *button_rects[1], click, enabled=config['jump_sound'],
                        draw_toggle=draw_jump_toggle, blit_text=first_run):
            config['jump_sound'] = not config['jump_sound']
            save_config()
            draw_jump_toggle = True
        elif toggle_btn('Show FPS', *button_rects[2], click, enabled=config['show_fps'],
                        draw_toggle=draw_show_fps, blit_text=first_run):
            config['show_fps'] = not config['show_fps']
            save_config()
            draw_show_fps = True
        elif button('B A C K', *button_rects[3], BLUE, LIGHT_BLUE, click, text_colour=WHITE): return
        else: draw_bg_toggle = draw_jump_toggle = draw_show_fps = False
        first_run = False
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
    button_rects = [((SCREEN_WIDTH - BUTTON_WIDTH) / 2, SCREEN_HEIGHT * 5 / 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                    ((SCREEN_WIDTH - BUTTON_WIDTH) / 2, SCREEN_HEIGHT * 6 / 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                    ((SCREEN_WIDTH - BUTTON_WIDTH) / 2, SCREEN_HEIGHT * 7 / 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                    ((SCREEN_WIDTH - BUTTON_WIDTH) / 2, SCREEN_HEIGHT * 8 / 13, BUTTON_WIDTH, BUTTON_HEIGHT)]
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
        elif button('M A I N  M E N U', *button_rects[1], BLUE, LIGHT_BLUE, click, text_colour=WHITE):
            return 'Main Menu'
        elif button('S E T T I N G S', *button_rects[2], BLUE, LIGHT_BLUE, click, text_colour=WHITE):
            settings_menu()
            pause_menu_setup(background)
        elif button('Q U I T  G A M E', *button_rects[3], BLUE, LIGHT_BLUE, click, text_colour=WHITE):
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

        SCREEN.fill(BACKGROUND)
        player_union_rect = player_new_rect.union(player_old_rect)
        # pygame.draw.rect(SCREEN, BACKGROUND, player_old_rect)
        dirty_rects.append(player_union_rect)
        player_sprite_group.draw(SCREEN)
        world.draw(SCREEN)
        if DEBUG:
            custom_text = f'Platform Sprites: {len(world.platform_list.sprites())}'
            custom_bg, custom_rect = create_hud_text(custom_text, RED)
            custom_rect.topleft = 50, -5
            SCREEN.blit(custom_bg, custom_rect)
        if config['show_fps']:
            fps_bg, fps_rect = create_hud_text(str(round(clock.get_fps())), YELLOW)
            fps_rect.topleft = -2, -5
            SCREEN.blit(fps_bg, fps_rect)
        if config['show_score']:
            score_bg, score_rect = create_hud_text(str(score), WHITE)
            score_rect.topright = SCORE_ANCHOR
            SCREEN.blit(score_bg, score_rect)
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
    TOGGLE_WIDTH = BUTTON_WIDTH * 0.875
    TOGGLE_ADJ = BUTTON_WIDTH * 0.075
    SCORE_ANCHOR = SCREEN_WIDTH - 8, -5

    window_icon = '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'
    window_icon = pygame.image.load(io.BytesIO(base64.b64decode(window_icon)))
    pygame.display.set_icon(window_icon)
    MENU_TEXT, LARGE_TEXT = pygame.font.Font(FONT_LIGHT, int(110 / 1080 * SCREEN_HEIGHT)), pygame.font.Font(FONT_REG, int(40 / 1080 * SCREEN_HEIGHT))
    MEDIUM_TEXT = pygame.font.Font(FONT_LIGHT, int(35 / 1440 * SCREEN_HEIGHT))
    SMALL_TEXT, HUD_TEXT = pygame.font.Font(FONT_BOLD, int(25 / 1440 * SCREEN_HEIGHT)), pygame.font.Font(FONT_REG, int(40 / 1440 * SCREEN_HEIGHT))
    MUSIC_SOUND = pygame.mixer.Sound('assets/audio/background_music.ogg')
    pygame.display.set_caption('Jungle Climb')
    music_playing = False
    clock = pygame.time.Clock()
    ticks = 0
    from objects import *
    main_menu()
