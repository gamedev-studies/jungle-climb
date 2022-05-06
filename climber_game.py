import base64
import io
import os
import platform
import sys
import json
import numpy as np
import datetime

# CONSTANTS
VERSION = '1.17'
WHITE = 255, 255, 255
BLACK = 0, 0, 0
MATTE_BLACK = 20, 20, 20
GREEN = 40, 175, 99
RED = 255, 0, 0
YELLOW = 250, 237, 39
DARK_GREEN = 0, 128, 0
LIGHT_BLUE = 0, 191, 255
GREY = 204, 204, 204
BLUE = 33, 150, 243
BACKGROUND = 174, 222, 203
WORLD_SHIFT_SPEED_PERCENT = 0.00135
FONT_BOLD = 'assets/fonts/OpenSans-SemiBold.ttf'
FONT_REG = 'assets/fonts/OpenSans-Regular.ttf'
FONT_LIGHT = 'assets/fonts/OpenSans-Light.ttf'
CONFIG_FILE = 'config.json'

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'True'

from pygame import gfxdraw, K_w, K_a, K_d, K_UP, K_LEFT, K_RIGHT, K_ESCAPE, K_F4, K_p, K_RALT, K_LALT, K_SPACE, \
    MOUSEBUTTONDOWN, QUIT, KEYUP, KEYDOWN, K_TAB, K_v, K_h, K_BACKSPACE, K_q, K_m, K_r
import pygame

class Event():
    def __init__(self, player_x, player_y, gap_x1, gap_x2, alive, on_ground, facing_side, score, time_elapsed):
        self.player_x = player_x
        self.player_y = player_y
        self.gap_x1 = gap_x1
        self.gap_x2 = gap_x2
        self.alive = alive
        self.on_ground = on_ground
        self.facing_side = facing_side
        self.score = score
        self.time_elapsed = time_elapsed

class Observer():
    def __init__(self):
        self.event = None

    def update(self, event: Event):
        self.event = event

class ClimberGame():

    def __init__(self):
        self._observers = []

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self,observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self, event: Event) -> None:
        for observer in self._observers:
            observer.update(event)

    def save_config(self):
        with open(CONFIG_FILE, 'w') as fp:
            json.dump(self.config, fp, indent=4)

    def text_objects(self, text, font, colour=BLACK):
        text_surface = font.render(text, True, colour)
        return text_surface, text_surface.get_rect()

    def create_hud_text(self, text, color):
        text_surf, text_rect = self.text_objects(text, self.HUD_TEXT, color)
        text_rect.topleft = -2, -5
        bg_w, text_bg_h = text_surf.get_size()
        bg_w += 10
        bg = pygame.Surface((bg_w, text_bg_h), pygame.SRCALPHA, 32)
        bg.fill((50, 50, 50, 160))
        bg.blit(text_surf, (5, 0))
        return bg, text_rect

    def save_score(self, user_score: int) -> bool:
        """
        Takes a score and saves to file if it is a top 10 score else it returns False
        :param user_score: the score of the user
        :return: boolean indicating whether the score was a top 10 score
        """
        scores = self.config['high_scores']
        placement = None
        for i, score in enumerate(scores):
            if user_score > score:
                placement = i
                break
        if placement is not None:
            scores.insert(placement, user_score)
            scores.pop()
            self.save_config()
            return True
        return False


    def button(self, text, x, y, w, h, click, inactive_colour=BLUE, active_colour=LIGHT_BLUE, text_colour=WHITE):
        mouse = pygame.mouse.get_pos()
        return_value = False
        if x < mouse[0] < x + w and y < mouse[1] < y + h:  # if mouse is hovering the button
            pygame.draw.rect(self.SCREEN, active_colour, (x, y, w, h))
            if click and pygame.time.get_ticks() > 100: return_value = True
        else: pygame.draw.rect(self.SCREEN, inactive_colour, (x, y, w, h))

        text_surf, text_rect = self.text_objects(text, self.SMALL_TEXT, colour=text_colour)
        text_rect.center = (int(x + w / 2), int(y + h / 2))
        self.SCREEN.blit(text_surf, text_rect)
        return return_value


    def draw_circle(surface, x, y, radius, color):
        gfxdraw.aacircle(surface, x, y, radius, color)
        gfxdraw.filled_circle(surface, x, y, radius, color)


    def toggle_btn(self, text, x, y, w, h, click, text_colour=BLACK, enabled=True, draw_toggle=True, blit_text=True,
                enabled_color=LIGHT_BLUE, disabled_color=GREY):
        mouse = pygame.mouse.get_pos()
        # draw_toggle and blit_text are used to reduce redundant drawing and blitting (improves quality)
        rect_height = h // 2
        if rect_height % 2 == 0: rect_height += 1
        if enabled and draw_toggle:
            pygame.draw.rect(self.SCREEN, WHITE, (x + self.TOGGLE_WIDTH - h // 4, y, self.TOGGLE_ADJ + h, rect_height))
            pygame.draw.rect(self.SCREEN, enabled_color, (x + self.TOGGLE_WIDTH, y, self.TOGGLE_ADJ, rect_height))
            self.draw_circle(self.SCREEN, int(x + self.TOGGLE_WIDTH), y + h // 4, h // 4, enabled_color)
            self.draw_circle(self.SCREEN, int(x + self.TOGGLE_WIDTH + self.TOGGLE_ADJ), y + h // 4, h // 4, enabled_color)
            self.draw_circle(self.SCREEN, int(x + self.TOGGLE_WIDTH + self.TOGGLE_ADJ), y + h // 4, h // 5, WHITE)  # small inner circle
        elif draw_toggle:
            pygame.draw.rect(self.SCREEN, WHITE, (x + self.TOGGLE_WIDTH - h // 4, y, self.TOGGLE_ADJ + h, rect_height))
            pygame.draw.rect(self.SCREEN, disabled_color, (x + self.TOGGLE_WIDTH, y, self.TOGGLE_ADJ, rect_height))
            self.draw_circle(self.SCREEN, int(x + self.TOGGLE_WIDTH), y + h // 4, h // 4, disabled_color)
            self.draw_circle(self.SCREEN, int(x + self.TOGGLE_WIDTH + self.TOGGLE_ADJ), y + h // 4, h // 4, disabled_color)
            self.draw_circle(self.SCREEN, int(x + self.TOGGLE_WIDTH), y + h // 4, h // 5, WHITE)  # small inner circle
        if blit_text:
            text_surf, text_rect = self.text_objects(text, self.MEDIUM_TEXT, colour=text_colour)
            text_rect.topleft = (x, y)
            self.SCREEN.blit(text_surf, text_rect)
        return x < mouse[0] < x + w and y < mouse[1] < y + h and click and pygame.time.get_ticks() > 100


    def view_high_scores(self):
        self.SCREEN.fill(WHITE)
        text_surf, text_rect = self.text_objects('High Scores', self.MENU_TEXT)
        text_rect.center = ((self.SCREEN_WIDTH // 2), (self.SCREEN_HEIGHT // 6))
        self.SCREEN.blit(text_surf, text_rect)
        for i, score in enumerate(self.config['high_scores']):
            text_surf, text_rect = self.text_objects(str(score), self.LARGE_TEXT)
            text_rect.center = (self.SCREEN_WIDTH // 2, int(self.SCREEN_HEIGHT * (i / 1.5 + 3) // 11))
            self.SCREEN.blit(text_surf, text_rect)
        on_high_scores = True
        pygame.display.update()
        back_button_rect = ((self.SCREEN_WIDTH - self.BUTTON_WIDTH) // 2, self.SCREEN_HEIGHT * 4 // 5, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        while on_high_scores:
            click = False
            pressed_keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                alt_f4 = (event.type == KEYDOWN and event.key == pygame.K_F4
                        and (pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]))
                if event.type == QUIT or alt_f4: sys.exit()
                elif event.type == KEYDOWN and (event.key == K_ESCAPE or event.key == K_BACKSPACE): on_high_scores = False
                elif event.type == MOUSEBUTTONDOWN: click = True
            if self.button('B A C K', *back_button_rect, click): break
            pygame.display.update([back_button_rect])
            self.clock.tick(60)


    def hide_mouse(self):
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(False)


    def show_mouse(self):
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(True)


    def main_menu_setup(self):
        self.show_mouse()
        self.SCREEN.fill(WHITE)
        text_surf, text_rect = self.text_objects('Jungle Climb', self.MENU_TEXT)
        text_rect.center = (int(self.SCREEN_WIDTH / 2), int(self.SCREEN_HEIGHT / 4))
        self.SCREEN.blit(text_surf, text_rect)
        text_surf, text_rect = self.text_objects(f'v{VERSION}', self.SMALL_TEXT)
        text_rect.center = (int(self.SCREEN_WIDTH * 0.98), int(self.SCREEN_HEIGHT * 0.98))
        self.SCREEN.blit(text_surf, text_rect)
        text_surf, text_rect = self.text_objects('Created by Elijah Lopez', self.LARGE_TEXT)
        text_rect.center = (int(self.SCREEN_WIDTH / 2), int(self.SCREEN_HEIGHT * 0.84))
        self.SCREEN.blit(text_surf, text_rect)
        pygame.display.update()


    def main_menu(self):
        global ticks
        self.main_menu_setup()
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

            if self.button('S T A R T  G A M E', *self.button_layout_4[0], click): start_game = True
            elif self.button('V I E W  H I G H S C O R E S', *self.button_layout_4[1], click) or view_hs:
                self.view_high_scores()
                view_hs = False
                self.main_menu_setup()
            elif self.button('S E T T I N G S', *self.button_layout_4[2], click):
                self.settings_menu()
                self.main_menu_setup()
            elif self.button('Q U I T  G A M E', *self.button_layout_4[3], click): sys.exit()
            if start_game:
                #while start_game: start_game = self.game() == 'Restart'
                self.main_menu_setup()
            pygame.display.update(self.button_layout_4)
            self.clock.tick(60)

    def settings_menu(self):
        self.SCREEN.fill(WHITE)
        text_surf, text_rect = self.text_objects('Settings', self.MENU_TEXT)
        text_rect.center = ((self.SCREEN_WIDTH // 2), (self.SCREEN_HEIGHT // 4))
        self.SCREEN.blit(text_surf, text_rect)
        pygame.display.update()
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
            if self.toggle_btn('Background Music', *self.button_layout_4[0], click, enabled=self.config['background_music'],
                        draw_toggle=draw_bg_toggle, blit_text=first_run):
                self.config['background_music'] = not self.config['background_music']
                self.save_config()
                draw_bg_toggle = True
            elif self.toggle_btn('Jump Sound', *self.button_layout_4[1], click, enabled=self.config['jump_sound'],
                            draw_toggle=draw_jump_toggle, blit_text=first_run):
                self.config['jump_sound'] = not self.config['jump_sound']
                self.save_config()
                draw_jump_toggle = True
            elif self.toggle_btn('Show FPS', *self.button_layout_4[2], click, enabled=self.config['show_fps'],
                            draw_toggle=draw_show_fps, blit_text=first_run):
                self.config['show_fps'] = not self.config['show_fps']
                self.save_config()
                draw_show_fps = True
            elif self.button('B A C K', *self.button_layout_4[3], click): return
            else: draw_bg_toggle = draw_jump_toggle = draw_show_fps = False
            first_run = False
            pygame.display.update(self.button_layout_4)
            self.clock.tick(60)


    def pause_menu_setup(self, background):
        self.SCREEN.blit(background, (0, 0))
        background = self.SCREEN.copy()
        text_surf, text_rect = self.text_objects('Paused', self.MENU_TEXT, colour=WHITE)
        text_rect.center = ((self.SCREEN_WIDTH // 2), (self.SCREEN_HEIGHT // 4))
        self.SCREEN.blit(text_surf, text_rect)
        pygame.display.update()
        return background


    def pause_menu(self, player):
        self.show_mouse()
        paused = True
        facing_left = player.facing_right  # store the pre-pause value in case player doesn't hold a right/left key down
        background = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA, 32)
        background.fill((*MATTE_BLACK, 160))
        background = self.pause_menu_setup(background)
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
                        player.facing_right = facing_left
            if self.button('R E S U M E', *self.button_layout_4[0], click): return 'Resume'
            if self.button('M A I N  M E N U', *self.button_layout_4[1], click): return 'Main Menu'
            if self.button('S E T T I N G S', *self.button_layout_4[2], click):
                self.settings_menu()
                self.pause_menu_setup(background)
            elif self.button('Q U I T  G A M E', *self.button_layout_4[3], click): sys.exit()
            pygame.display.update(self.button_layout_4)
            self.clock.tick(60)
        return 'Resume'


    def end_game_setup(self, score, surface_copy=None):
        if surface_copy is not None:
            self.SCREEN.blit(surface_copy, (0, 0))
        else:
            background = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA, 32)
            background.fill((255, 255, 255, 160))
            self.SCREEN.blit(background, (0, 0))
            text_surf, text_rect = self.text_objects('Game Over', self.MENU_TEXT)
            text_rect.center = ((self.SCREEN_WIDTH // 2), (self.SCREEN_HEIGHT // 4))
            self.SCREEN.blit(text_surf, text_rect)
            text_surf, text_rect = self.text_objects(f'You scored {score}', self.LARGE_TEXT)
            text_rect.center = ((self.SCREEN_WIDTH // 2), (self.SCREEN_HEIGHT * 8 // 21))
            self.SCREEN.blit(text_surf, text_rect)
            surface_copy = pygame.display.get_surface().copy()
        pygame.display.update()
        return surface_copy


    def end_game(self, score):
        self.show_mouse()
        view_hs = False
        end_screen_copy = self.end_game_setup(score)
        if self.save_score(score): pass  # Show "You got a high score!"
        button_layout_3 = [(self.button_x_start, self.SCREEN_HEIGHT * 6 // 13, self.BUTTON_WIDTH, self.BUTTON_HEIGHT),
                        (self.button_x_start, self.SCREEN_HEIGHT * 7 // 13, self.BUTTON_WIDTH, self.BUTTON_HEIGHT),
                        (self.button_x_start, self.SCREEN_HEIGHT * 8 // 13, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)]
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
            if self.button('R E S T A R T', *button_layout_3[0], click): return 'Restart'
            if self.button('M A I N  M E N U', *button_layout_3[1], click): return 'Main Menu'
            elif self.button('V I E W  H I G H S C O R E S', *button_layout_3[2], click) or view_hs:
                self.view_high_scores()
                view_hs = False
                self.end_game_setup(score, end_screen_copy)
            pygame.display.update(button_layout_3)
            self.clock.tick(60)

    
    def get_gap_position(self):
        gap_x1 = self.SCREEN_WIDTH/2
        gap_x2 = self.SCREEN_WIDTH/2
        height_above = 80

        # get blocks directly above player
        all_blocks = self.world.platform_list.sprites()
        
        if self.player.on_ground or len(self.blocks_above_1) == 0 or len(self.blocks_above_2) == 0:
            self.blocks_above_1 = np.array([])
            self.blocks_above_2 = np.array([])
            for block in all_blocks:
                if block.rect.left == 0 or block.rect.left == 750:
                    continue
                if block.rect.top > self.player.rect.top - height_above and block.rect.top < self.player.rect.top:
                    self.blocks_above_1 = np.append(self.blocks_above_1, block.rect.left)
                if block.rect.top > self.player.rect.top - (height_above * 3) and block.rect.top < self.player.rect.top - height_above:
                    self.blocks_above_2 = np.append(self.blocks_above_2, block.rect.left)

        size = len(self.blocks_above_1)
        for i, block in enumerate(self.blocks_above_1):
            if i != size - 1:
                dif = self.blocks_above_1[i+1] - block
                if dif > 47:
                    # start of the block + 47 to get to actual gap
                    gap_x1 = block + 47
                            
        size = len(self.blocks_above_2)
        for i, block in enumerate(self.blocks_above_2):
            if i != size - 1:
                dif = self.blocks_above_2[i+1] - block
                if dif > 47:
                    # start of the block + 47 to get to actual gap
                    gap_x2 = block + 47
                    break
      
        return gap_x1, gap_x2

    def draw_gap(self, gap_x, y_dist):
        marker = pygame.draw.rect(self.SCREEN, (255,0,0), pygame.Rect(gap_x, self.player.rect.top - y_dist, 100, 30))
        pygame.display.update(marker)

    def run_logic(self, action):
        # TODO: make background with vines
        if not pygame.mouse.get_focused():
            if self.music_playing:
                pygame.mixer.Channel(0).pause()
                self.music_playing = False
            if self.config['background_music']:
                if pygame.mixer.Channel(0).get_busy():
                    pygame.mixer.Channel(0).unpause()
                else:
                    pygame.mixer.Channel(0).play(self.MUSIC_SOUND, loops=-1)
                    pygame.mixer.Channel(0).set_volume(0)
                self.music_playing = True
        for event in pygame.event.get():
            pressed_keys = pygame.key.get_pressed()
            alt_f4 = (event.type == KEYDOWN and event.key == K_F4
                    and (pressed_keys[K_LALT] or pressed_keys[K_RALT]))
            if event.type == QUIT or alt_f4: sys.exit()
            if event.type == KEYDOWN and action == -1:
                right_key = event.key == K_RIGHT and not pressed_keys[K_d] or event.key == K_d and not pressed_keys[K_RIGHT]
                left_key = event.key == K_LEFT and not pressed_keys[K_a] or event.key == K_a and not pressed_keys[K_LEFT]
                if right_key: self.player.go_right()
                elif left_key: self.player.go_left()
                elif event.key in (K_UP, K_w, K_SPACE): self.player.jump(self.config['jump_sound'])
                if event.key == K_ESCAPE and not pressed_keys[K_p] or event.key == K_p and not pressed_keys[K_ESCAPE]:
                    pygame.mixer.Channel(0).pause()
                    self.music_playing = False
                    if self.pause_menu(self.player) == 'Main Menu': return 'Main Menu'
                    else: self.hide_mouse()
                    if self.config['background_music']:
                        pygame.mixer.Channel(0).unpause()
                        self.music_playing = True
                elif self.DEBUG:
                    if event.key == pygame.K_EQUALS: self.world.shift_world(shift_x=1)
                    elif event.key == pygame.K_MINUS: self.world.shift_world(shift_x=-1)
                    elif event.key == K_TAB: print(self.player.rect)
            if event.type == KEYUP:
                if event.key in (K_LEFT, K_a, K_RIGHT, K_d):
                    self.player.stop(pressed_keys)
                    
        # react to commands from agent
        has_jumped = False
        if action == 0:
            self.player.go_right()
        elif action == 1:
            self.player.go_left()
        elif action == 2:
            self.player.jump(self.config['jump_sound'])
            has_jumped = True
        self.player.update(self.delta_time)
        #print(action, '=>', self.player.rect.left)

        gap_x1, gap_x2 = self.get_gap_position() 
        self.draw_gap(gap_x1, 100)
        self.draw_gap(gap_x2, 200)
        #print("gaps 1 and 2: ", gap_x1, gap_x2)

        self.current_time = datetime.datetime.now()
        time_elapsed = (self.current_time - self.time_game_started).total_seconds()

        if self.player.rect.top > self.SCREEN_HEIGHT + self.player.rect.height // 2:
            if self.music_playing:
                pygame.mixer.Channel(0).stop()
                self.music_playing = False
            event = Event(self.player.rect.left, self.player.rect.top, gap_x1, gap_x2,  self.music_playing, self.player.is_on_ground(), self.player.get_facing_side(), self.score, time_elapsed)
            self.notify(event)
            return self.score
        self.delta_time = self.clock.tick(60) / 1000  # milliseconds -> seconds
        event = Event(self.player.rect.left, self.player.rect.top, gap_x1, gap_x2,  self.music_playing, self.player.is_on_ground(), self.player.get_facing_side(), self.score, time_elapsed)
        self.notify(event)

        return -1

    def render(self):
        self.player.update(self.delta_time)
        if self.world_shift_speed:
            for _ in range(self.world_shift_speed):
                self.world.shift_world(1)
                self.SCREEN.fill(BACKGROUND)
                self.player.draw(self.SCREEN)
                self.world.draw(self.SCREEN)  # some grass appears in front of player
            self.score += 1
            if self.score > 1000 * self.world_shift_speed + (self.world_shift_speed - 1) * 1000:
                self.world_shift_speed = min(self.world_shift_speed + self.speed_increment, self.MAX_SPEED)
        else:
            self.SCREEN.fill(BACKGROUND)
            self.player.draw(self.SCREEN)
            self.world.draw(self.SCREEN)  # some grass appears in front of player
            if self.player.rect.top < self.shift_threshold: self.world_shift_speed = self.speed_increment
        if self.DEBUG:
            custom_text = f'Platform Sprites: {len(self.world.platform_list)}'
            custom_bg, custom_rect = self.create_hud_text(custom_text, RED)
            custom_rect.topleft = 50, -5
            self.SCREEN.blit(custom_bg, custom_rect)
        if self.config['show_fps']:
            fps_bg, fps_rect = self.create_hud_text(str(round(self.clock.get_fps())), YELLOW)
            fps_rect.topleft = -2, -5
            self.SCREEN.blit(fps_bg, fps_rect)
        if self.config['show_score']:
            score_bg, score_rect = self.create_hud_text(str(self.score), WHITE)
            score_rect.topright = self.SCORE_ANCHOR
            self.SCREEN.blit(score_bg, score_rect)
        pygame.display.update()
    
    def main(self):
        self.config = {'DEBUG': False, 'jump_sound': True, 'background_music': True, 'show_fps': False, 'show_score': True,
                'high_scores': [0, 0, 0, 0, 0, 0, 0, 0, 0]}
        self.music_playing = False
        self.delta_time = 0
        self.blocks_above_1 = np.array([])

        try:
            with open(CONFIG_FILE) as f:
                _config = json.load(f)
        except FileNotFoundError: _config = {}
        save_file = False
        for k, v in self.config.items():
            try: self.config[k] = _config[k]
            except KeyError: save_file = True
        if save_file: self.save_config()
        self.DEBUG = self.config['DEBUG']

        # Initialization
        if platform.system() == 'Windows':
            from ctypes import windll
            windll.user32.SetProcessDPIAware()
        os.environ['SDL_VIDEO_CENTERED'] = '1'  # center display
        pygame.mixer.init(frequency=44100, buffer=512)
        self.MUSIC_SOUND = pygame.mixer.Sound('assets/audio/background_music.ogg')
        pygame.init()

        self.SCREEN_WIDTH, self.SCREEN_HEIGHT =  800, 600
        self.SCREEN = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.BUTTON_WIDTH = int(self.SCREEN_WIDTH * 0.625 // 3)
        self.BUTTON_HEIGHT = int(self.SCREEN_HEIGHT * 5 // 81)
        self.button_x_start = (self.SCREEN_WIDTH - self.BUTTON_WIDTH) // 2
        self.button_layout_4 = [(self.button_x_start, self.SCREEN_HEIGHT * 5 // 13, self.BUTTON_WIDTH, self.BUTTON_HEIGHT),
                        (self.button_x_start, self.SCREEN_HEIGHT * 6 // 13, self.BUTTON_WIDTH, self.BUTTON_HEIGHT),
                        (self.button_x_start, self.SCREEN_HEIGHT * 7 // 13, self.BUTTON_WIDTH, self.BUTTON_HEIGHT),
                        (self.button_x_start, self.SCREEN_HEIGHT * 8 // 13, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)]
        self.TOGGLE_WIDTH = int(self.BUTTON_WIDTH * 0.875)
        self.TOGGLE_ADJ = int(self.BUTTON_WIDTH * 0.075)
        self.SCORE_ANCHOR = self.SCREEN_WIDTH - 8, -5
        self.MENU_TEXT = pygame.font.Font(FONT_LIGHT, int(110 / 1080 * self.SCREEN_HEIGHT))
        self.LARGE_TEXT = pygame.font.Font(FONT_REG, int(40 / 1080 * self.SCREEN_HEIGHT))
        self.MEDIUM_TEXT = pygame.font.Font(FONT_LIGHT, int(35 / 1440 * self.SCREEN_HEIGHT))
        self.SMALL_TEXT = pygame.font.Font(FONT_BOLD, int(25 / 1440 * self.SCREEN_HEIGHT))
        self.HUD_TEXT = pygame.font.Font(FONT_REG, int(40 / 1440 * self.SCREEN_HEIGHT))

        ICON = 'iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAIAAABMXPacAAAuJElEQVR4AWySiZHbUAxDCX7JqSFtZO7039PuWp9ACCrOuTRHJ4wHY4yv377rKimwcj1WL44VEdqsa/NZ9SxuhhiBPDLPNbIjz4zMqJZVfez6KFZZs4AzcyWAsFEEZsMeKrLYx3luQysXwmKJPoiyGrbKYzWoj7ChXxr3vpvITRuf6TC9C+rpt86860nRFCQakZO5j010kmLL2qSPItGzmpI35fcY6VjaE5uy4cJkXlhWTGAfojeMs9VpkHcZxxeuV0VkC3J9OVp2xJ9zm3CYu3iRV6ls7zrSvvfiTIy1fmcNpNNbMPgAEH8NexCQgtBk7b37jbRWNDc2VZQ/CDsCS5CEPhj5aea7qLpYVyd/tY+465idinMq+6PhSD9cI2jxP6nVW6AC1O+f6XK9ANRTYpGv2DAXMmhQf/rhT2sHPhCwRAxKpGocKV7lLUpypOWa5u/vYy6Hll6OABKYcH77sBju1O4yzDhsYVT399z+bfv4KVZZS4Uo5+ktKqENIhDpsj0I4HaFxWQBDP6gslzQG4lBGIyw73/gnTHaDyEnzaTNkxoJfkhfEfN+2Xf1pRmfMSpXAi07W8m+steK1GeWzcvBj9N0U6ednTee1szCyK5TeFHZsQGrHt3UqYohovY9WjZe52C5n1FSueDqCyJvDETwK2haivRWmQ5dhPhT0FJTQyesPhwdP+2sZHoEo+z/LSCygz1UyDCm1TcodTDqkO/h6edWsqf6KVWG+w/IHI1YE9BoO2amilOsosTL7qXteiSZTBZzK3ocqwfx6HDn0BPLJo+WQdUWuahvXzQyyqfnFqft+Tuk/OskMuMDHVIVchiDjfbg2fdHzUhkBG6Yjwp524MleMZ51dPZknSnFQhEBadbp+4Alep0IfXPNg13H1yqIpmwhZUxziy7rzq9zU6v4uKxYd1N5BfrXAhq3WfF8Q4f8nOnquPEPvsE+hd7MhlSWCNLT8IcLdtYTetHXwV1C0SulmBhGT6nzAJV+vlKr3ecEFBad7oYea11Rg4WiHqqjlYMlcsQMkbgEBoBcp4PFpl5R3ZB1TeGNX9ka0BS+qFrjgF1lYj5d1T9txtAyh3jBvC0al+dEQpARZUGseoMqdiSq8s6fR43yyZsCoAjVcccJJvKvs9Rae6oO7hsvzhP6SkbdnK8oBk2O5P4SOW6E5qeA39dv6L8FGygw3jIqovOKPoMpWSkAJfs3GnupNn3ESM7s+9ntRFhUyXN+odK6BzjnzLlrXiCYSIh8RnIFVCit+9d19umkX0pMQjbO4ESvvCfDDPR1hwEYTDazvs/7yzKHPKZ0p7bM8td+itCCIknC0XZZgUDBBwBw1oHfniUBp/t/pXoWRrm/nM+wsJJ9s/r8euCVdlISIwxagQhb/SxFaKXUFdlyxIzzLAWHE7rdFSgZemwtEvR1JFAoA7sw5apvMOZ1IyUkf0YfB3zF5JUk0PdEWynWqoSe6d5ZWX9IWoCm6MKECIfT62jW+FT05w7goWJA9WVoD/Egk37sY39PobLzGvPIhGT/UVMHlktdnzyiiY3yYxna6ny4kZyh8P48bSkQdFHFG3uuGqm0HZ0tWeV/lj7m7vd/cJNsiiI0cFaW/kAKaljnqB7IpAqDPxxVy/H0eMwJrN0xXJfU36+8uElezVnKGbkNRlxKk/wgkwcutC0G6/8gozaZ28hIufOPbrq7sHkMKVik/6IU3nkWRVAemhtmSyC5Q/gK0AoueITXpizlpojLdhNifwRBOMQ4k8Jr7BLsi2aLFskuwXzLLtz+xRgTKqX4Xwrg/GatDO39l20vzemDAYRHg0Y8pE4SQKJVZsH+3FqPCf6lSf5a4nNp4ZeBPkH4bxAXTUiVSGwX2NWMj80GEbmWDu9heNWEv4RtgCx6hWMEn/MPKIdjSt79ZjwW6/pPgacNM3YMqUKvF2RXhfpjh3JWVCJipnhdBtE/MEQtXkbH+7hJE2OmPjXC0JaoWzrDsPiAeyL36RQ3wXoh9LqK2y2D2PpRgAxlRQcnE5SvRwDmMFuZjpt4LHZgMhsXciiKwoxf8i+Wlae5vEHMV8968ckowUldao7I18K1agFaNIFgOaSpKwhLNS3v02yT7c867DKEmsjDIgyMq7uToYVmkfkY+aRwWEL0PTJvm2hJWnK2ugwjQIH1difYJ+iJnlpJwRr8ZMOiSsKusyP4c8dhrPfQxEboQH3lZL2lf+qcRXzBa03DfXz+GfnAWuy8lZB+mbDZ+gaMEPkm3Nz9UYjb42I6QLtZHpTIet9CTWOgSq/ugA+vCzDSiYedzVSeNNFPUfAueFvyf51H2NoDoxv0ILnhvq/Nyt+sOhclsmmuGXt48TMNO4TcgQ1U+gSNjm4p5MwDTnNlx6bEMABzV0VfbB+c55xmelQRI1qk76Op0beqeSq6B40Yt4csZtnN1PXN0gqsD1Rm6ZauKEkvrQHpKKvAR5hTvC4ImwVJ+ObVqh5kF+bcKKKixqrPDpjv9Dmn3xh/nGg8ZrVClqVQ4kExFaaohanoZHIsuWDmMk+rltspQ7wMT4N3+0p1MylwjtNbyokjsjghcb+7OtrOozsP1YvMQqMdN/3lgHGQ1/CG7XRalKclRGyz1LuJ/jfMkyVG5gUjgBT87in56gA9PVGjsvT9A3SODUW77GPAddhC4sjFXak3PUhUvF++Oq0madZqmbAk32v3vRMYdFw0+lI49E0h91Y7nqslpKl1DNdsGkuKrpe5TTtSlDxILUHW0FHjUrXsq+kqHzwbndAnGthFmkSix+XjyqGzZAQ49k+2cVR2wCh8eDh5j61WuCQbdFDF3zmMaeaSuqJW+MloklceFFAejCNEfvxls5+jxr8xXkZj9P3wEZr78Ix6BWZHR0DYTIDRiFK12DocQ36SoodyaBv7vghcBlRuPkRNo8MjbcIss/63DyO22LTyGt3CZvB1ojPDpvyMwB69lLOdnPWvjdhKe6NVxbLL1iMyFioFeTwlp6iAF9FsuKk7NrVXBG8RoH3cuqTuwSD9NWNmmYsqg1ZHCltvw1JnnKSlyfsycqjodIJ9bXEoqP1IoKwp4sbiBvZnawPVermRiP3GzZjbGzhpmtfxXWqfQuwK+CqMpDBx/flH3rZasyDiMzTDV5oSFyz8QD7zv7D1F0ttzBdH4HK1ppt44VK3gz6ox+jjeFtOta98T8bKFL/jLufYf9b4pPFtx5X8xJU80Bt0BsMCRifMY62fmDha3V31T9G/9c8z6f8aQKomG8o3xeTSDES+vb6NP58QMRfrhwO9c8Y+1HodZi6opl2Q/w180iPpynyPznn0RxJshzhzyMTYtTTWp34D6j5/4/U6kZ9ffqtRFeGcwedUWkNYhvsmdXrBkML27KujWpEuHt4zdregFjsy9VkhHkAY3sprLG2p557rt5+8Y34xYuwkEShvjcth5TxX78f//1OTrJw1XUVP3vGz24SYBnvU6mQ2LHs6yh+DHfmX9/V3SBDQNo2E67fNsCJU5DdOelUua+LjUV9L46b+mixm/a216N2rXG0RY9kqy3x4tX3ffxJl4kUxcwkgHWSbElIknWigPYRV/8bcwk85avEcbF1Fb94GX/1bRLAPIIIgfifD9XmZj9o7ec3489fjjQnUMn9R2DBH4b+/S7usDz9V8nsMCUM6yt4N4lv97D/b/VBsRi3ir1KqwrV0IvzAppkUa0mfiUhqufuXBOW0N+DEWBI16Be0+XEEQGWbZnjbrv3+2ybuT2Ndt3ojSBxmnOIaDdqvYyAkKU0ySnMGQiySrxUvZFO2LFNlXobh0lAuu9V4tg9kDRTBxYfmNvUta5b6mxq9+nKqS1fSOWn1V53zCGZs4HOn16lL6EDrEjA9PLsnfKrVOg87e2ob9mt6YoN0EJhbM5CTVGL7mXlvwnWNPI+ippACIPStvNQTsFh8qg+NfqqPtHiGLZpq/ULYaPqvC5xX55PCi1/Me00a7pM9/TEGuq7KtEk0WUa1/qsPGGQWLpEFdq4q//AIDS7ZT/mXBxCyVOQtOh52oI0b4Q85Phw2ZRCamJ5onjkapgjATX1cTe8+v4SzWXPiZAoppQ4155rTH2/VvmZ1pZINgo9cIewFSHNjbm6dqFUo6hOsawbEkLhGZYZI5V4eEy+kBik4u9TQBVFSZ7CnOTVZRLy1gjMZTDHNNjsBzuXK1MEszuyzln96NHzbsuq4Kz+9Ws+sGJMUo2+rIGRWQqWTNtAF9eynBoEJnVQGDxybOnjV1UoptkyR8W0i8lhT4WZV9tgZNoAAYFE2JHJZkGO7FvamUJNERHXcX07V/DTnhM34kk0+3rbmgTYpN2GQFwI28eysEt6rfarlG1vzupOajqa0H1Wn8oBXu+6WZKYMPhUhZd3ZgQJv7jVHz2TMRpifID+9sP2Qc39GTEKARIPsO9wxmFcbfknt3kjIAyioITkiA7XJ0O59/z5D7nqiQwDAK7k5BwMP9MIbUvxyj9RN53LMWNxoLJpPOMEkkoDLZdsEpw+6aCkouTL+UsDqPr+I8tSl8bRVdOzwCc1HZkqHl2b+BV1EgPDiTberPSNeBY8AbHDcBW87Fw1wBTM0+jwDITr/Oi8OSSdOG0UnUN450WKtsh3jx5Is/vvAU0nEqxm6PFwwz5Jd6CIkBRreaz6LXG6L6tt6pZDiuFlHW8lHWMeby7AWmFcDrNg3hzqEfaal+ucUFD1nKWenqjp7aYvoSE80ikKEiv/tJVpPGy7KjuzbGoGn55QC6DmtkdSaQkkpTPEbuLZQDSFGgwwXypIatetBRhXy8W7NlrhsN07ctrO3m474HTthrzPVRbvX4ocswAC5gfkwxO6ac3Czk0oE2YsaWQCY9kOSIo4nmgLicGXDqLd9NYgnQcS7NwTKGvpUr19T13e/wUURc0cpHeTchmfYCbK0Ra2pHVFUUCu5kNc90BOR0tiWPiAc1JihCxrz/age/2hJg7YnId95p0LYDDg05eXQ+i1cmp4S8xU+zPqugIPiOq3nnZ09OZaASpFwMCG3G3yMhcFCliBToyN0h75qybFFaH5MeabHxxeJdNGTzvTsnVijtw03V5BZDQUFtGTzhOI4Fsve4tVtRa0EBfC5sVt/ODbXUyY1+/YXAwRPULYuCXljiq0W2qKgFoFZCjToisgK69ih3fOeZJ/nn6Z6hqO9IZH2vYA5a/UfqMWrR2jelfpn//m931L9LEExvDNK755i20YMH+ZJ9BC3/1mu+p6+7+A57fx4pRy2bwhAqUcAk6z06AJjI/1bMYN053G7Av0xaMYHqAp2PYACNjDOoxECYxceR4sY7wsO3EGZrdKL4O9fr89bD4Z5MxYYGyYP6YmKErMvmJBktQ9DCsumlKYmreJpjHX9i5msuat8Ur0uT6bhrHE1ww5MgcemZlz1FGJni0JRS0QZlVli55bKrSTpIDM+dISmq69ar3ldBB4Xef08PD9rzTzzdGEzacA18PnCz18ftzm2tvwoZi6bcIxchPSnqPd85YQ3VvS93QN3v3rhV3tzlfIahGnJyJn2BopCNxaYB4ghMSCCWEeojedt8N6F+JTQiYn+VKD6E0scJfcGUkU3t0Y0yUrf36/0Wqr4YajB2qKOlbuOTKEQ5ItwPg0Dugj0kPEuia0CETV6nv4+xiMB3dDUrcfTrxrvboRZof0SPV//oOr3sXHYFXkU4DEb9/ZfvW7cXq970+pPjHEv7yjv38v2uzJ9sjtkO9+mGWh5xJMJkeyCA1IjkYJrO4tsyohyxTWbjZzkyJhdSoCEZIJkBp05/U2/PGjzRCiC4tzEL3rqsl8PhjJYbN0ruPdJX/Y1AMlTufmcbdcd9KIZSTbHoZMATTJiyTRM1OVTypfaJlKtr0BCcMmdrcOEWKSfqBrG2yD8zBPw59zh9ejL8UCO8s3nh6lZ/VHhRnWktUjff+7DgZUSRBKBtt4rqvwMtKmjLJPPzuo7WP1IqKJrxeMNXdTtcKrMMNccyI5MwWHdDo9wEWDHC2AjrS2H1IAkn1yV9SknpJCGZKMDF5CXkL6ehU/SecxSbWqDxHrxnyhHMKMYTKd5CFZ8SQU6hFKC9vJXJ6hPY5w4i/vlF/IBjFhIyf22f7uJU3eXhlJPAn74qPEA6xyhRaXm7cBi7nrPqwIt65mHlktgAAPK9LITuzcUIzU1F5dRwdjuNI4lZ5YCQkpIu5/75EFEGKH4Tr8zVv5bG//zsv2nZfBI7jM1cl8zVVGIh7FcnWe38ZFRwHvfpDSw5H7t7/XyAqKS//zAT6Q1Jo3E1DU3S8zZhFOO+DB3U3pHEYJSOpx1Rxy5J7/qgSV8XRTVxLfJXqNvdJKNtc9/x8X4LXz5bf2Bkb6I6Z42Hz+Wn70WS+ehf3wqIv+tgQfJH/zO9790Hk3PBIRr0GayTipHe/KIwfI8gPObWNY3oHUo4dDDh3t6D3gbyztq8uZ7PWW6ZkowiBABAYffz+9tMLmLSHV7zMwuuCocxCEHRhITOIcYxle06w8TYOHXdW3lwSQ1+2rKaBHC4cTqJRnzgX6jOS3suGmFjNZDUoClWlhvqow5JgOPmatY6nc+LoPpUULRRCQEjL49Bqg3USzTFeIXVWvRXyF467biuWOUm+uES0iYMkB85XEXMfaabuSk7JCirKKZxp8lkLIGCEewU4yDZ2FPepeCctKmStkY5bPug6QNP+JLOt8ImEdchnhsW0WBDmzpta5oxjpTPuioyBESBQEgqzb4qrx1qZ3Vb9FlyL+t7236pPsWNa744nMVV0NMxoGvVt0pMPnbHzNzPYHMF/70vRJjHeGOzMzsw8zg9CCIw1jU62V8bh3Z6zMrJp2VdeMNs1Rqn/iXl0dkSsh4ol/NCb2sWxaAtHMD4co0tpcTjDRlpDCVE6Rfv2S4v8Y0IUZ04MDEjXKtjVZLKXZPbCb94YTDipLrX/1wgtHX8K5TfjV68mMsvQctDUNR89f67sU8hOfPPrJTx6C9TDSJ84aNIXLVEOR48VQy48Wa40clERpR03RKCKTVZdGDRSSefWvWTBp1ngUOpkfvPLX4aEVB2Sh3Ga3+AbuHdjuvi05qJw4JY+s/4U3Xl5UOeO06/da3xUV7/zkh29+sqfk8fWKNpDDOPdVkEcodSg6Sgi1LO6FqMLBBZZFz1BWmRF0hWh9ylo+BA0Uy2clhbbcpTYiVeBPGS9Riv96AKt/1YVwNE577ZwLhzyjBmjJMJFcKiGJzNpLryNjjb3UqsdSe+uhHfoZqRL3ina2BHLRArciog2mIo7qiqo6yh20CPZLTV8pmwZU0NTrilcTPgfDaQBiZoPfvOr2KICWIjif+BDQaRBNEVxTeyttej0PRZHFRxus1P9DcVIFpJClkHp0pq/+Xtfg3nouBo9pAOL33oa7iXqOBGohm2TQYD750LVVZcdGiZ2S/jQICnqxC9FFn+5ehUJ8NqNyl4aRJFKCHuMSlou8ZKSzPLsbFjEeHH/cp3SelPmxoBYGQKP1ljfhtt6kDiekEDScrHd32yMAIeR/XWhNebgPgkYhLQmZlKpRBEFLxSshdOt7yNs1/nk61OpRQhQStQbjAk5whqoExYIR2tgAKarYnnaKqh/qU7r9YJfPfIFWxdntqc67cu+w3z/s2034YP8gpj6gnQ5ICJQmQ5UEXEDYVGZTvUiV1KnXWeYdZc79cdRV+1xTBTWgdaazmQo6lvBET4OvA7Y7ubKDFnQTsHgwP7cTj/Q80oz7j9K7vzaTOnhma+MP/sHvPPozRwnQf/zRX/5b/+ZHg+IZtSfnz2z+xT/2e8+f2Sq+DKr//aff/Dc/+AshNNndw/QdaZBmDAjvdxcHhFq9TCNYaV7NjcbPL4VzEwAR5roVGUaqCURcrxYFEDPXraiK17wju3oUWVCswgCy1S0pBvPV7fjPQcEVgirpIuawUjKf/yOTyXRjsj3doDDbqE9258HjoPrs4h8zyvw4mv53Hs49HED3BKZNFY1Q2SGBJbyQTVk4kwQ0VknoKHMTWiDFEgWOY5ABsRIixj+PIAcWYHJ+bilokQKjzCtVgkMoP62EIBtoDuutRZ5p8MQHrHw4x6gxqGLWogNEi9iNkMTBPzTdEx7GZz7Ix1GxruakzcFsoRwBYL3IDQ2BWUU0aCAGscHGuirLyAsoCDE1CfK8Dg0KA+lyT1TMLpz10YsxiUk7geqACw8JyFCAtKSlWJaCkmTOasNaVhfUU8wUUwic1uQR7TTuCBuCuPSmg/FPWO8yOwJr+FRRax++xs5VzTuUa+HhCtHFD86sABFIYRblsnoFSCIxP9YGk4YJ6VBrPx9CgxAqyMH/jIliLKXobEDNduwADjnFTD32XtWmi1ifMkEB4oUIB4IHXJEPCI9NZFiaflocFL5+9cIf/sLruv4mvH/QHxz0ZSXZ2uhufnTn0e2H7XJ/cdL94S++rqjih1942P/Co5lS/A9jIkxQTjoFgFK0mijSWMCr5jyrCCWogHgpkShVfQMhDcYIHWMNTsbiyNKhGNGoHxDajZ+etzHSsgP4wMAVx/uUBiPXSNIa5fWr569MwvpbAO7d3717f7e9It746PbCnLh4Yfs7vvBGeQMC8ODD3f/90eNAqSfAfrDZIIn0IzjGQnOf3Y4v74IALkIpOC5TBEhQLYEkoYVMuQzCrIooUJack6+IUQHR7lYa83UvCMs5NbtutTHZ3CVPP8pkWncTBryGoWU2nPiQuTgTshHo4ewczznGx1giFuT1bMszstQHprA0HmGMNCpVAWpVvTW8eanwbv/zeK4qN3AfldcUpBNhkUkkEcCJ/M/BKFjezFEcUq0yF2fqOSHDFBBlpWvGQDWBSC4QTSZJ1MrZVEhU7ac4Hi2OyTaZAw/pScdKwF8jqnbN4VoE4PNi/0pldhRAJb6LBD8SZE2KmCAC6gHOuq3nLcE8MiQYL0sF5dDU0UeOVOcS5i4wRyHn1wzPtEHhuHxKHuyTCHmS0+ZbjWBVlWjziMX62/W0FFwN6liEI0vhQPUJGWRZgslFMZndU9TdVImK6HrOEm+WFqSap3Q+hC0cTsloI08eI9pMCh0xiaC5oBUDO8xGpAGX7WzEK5tdu8PakNjanDJRoyRpxuQYHDtXtLURF2x92A/3dw8ArIjzbE1V0XpeVVeeUw+OHr53QNYQ1v5Bn/qEEYBWqqvb8LAXetJ/dMadsnVpQ5H34tBwwuT0EqXCoi16LgPceeRY2G5MkDKyw+D2HZL9kd/9PX/uD36+TI40DHfe/yj1gwiKjX7g597/wZ99v5jJyO+8fvaLL19o3Ra7sNnFJrKCH3v743/1Az8XFGvFeQAcDJ/cuftoyeaUH/5zH99qj6EfhjOCnYyYduQI6umhlSaydN3J5GoVzt+wG34jkMqdft4BLioqpZRBs9GR4OiWlC8HeakHAvIQ1I4NIdnOzvTcxTOSzB3QD7y/mfq+CQTp1mRRlTWJYWca2xBNiIsnzoPjN2BJLIhkiAFBQwzVAYpVb0B5vQ4bB3B/Y2rBmKocf4457s+vSHHznC5BLS9KWYcKIDE/ykG65ZUyxtIiJut/RMFUuZFORxLJFygVFSmIJddZ52+HYm7dZR7tae/kfAG5AhYAWan99cvn0+Us24fDD9UegNEAp4U9Ce8uiKyc53d4t0qFd2MeFQcAWkhV4205ZuFbIQH7k/MoGhimMTFEzbWP0DHuwco8ei4Gj4eqLDCS3Zq1fc0YrBxIJJopg8aSKZtPoaOBLjupyp0XQ2N9aKXwsfWB5zUTih7Ran2XR5Gem0G3F2JoHFBwaSJCB+FBaJLx9ci2KR1WmpVQWg1LeaC6xjBqxau6AKJt21C8LWLmcamUV7TSYkEg+cp34lx6MtMIWTMYZxyGxMAlm/AwWL1OrjEr/OHlXAAKJz73gyujWqYgxLzfolerp5olNIoaoToikkgRokq4JKhkT4xaN4VEf79w4vIJVmj7eAcR8eaLTSV4yj2dmoGgZy5dyBtU2YRl48aDAwtByy9/uEqrbLQvff6Ns5+7plh2A9jc6K69/tLWRsfm6jC9/VgogmXW//Ln3/j87/wimnPRf/jlW//prbvHxLY6L5tdxiFYLjwZu/ZFxYsXN7tO0fSr2dra2t7eHhu/AYre+NaNOwNrLifW5buKimTcQOlVfShxJL9cEHPqPb95N0NVdy5dWMyHbWw+OGAIbBzgLl5ioy9+/o3f+dKLq+YzF2F7qhvvfJzJAEu8e/Tw7/vdX5Hy4YPe/Mc/9J/f+9HagKzofVhEorUasmY3A165vDWdBNbFW65cuXw06I4TQB4f9O/fedDPZmIe/I8Fr+oj0fwWVu5wUBQYaV086s8x8Ymw6m560hJ0ukqXlIT89AkEvn4lMWsTZ8G3ylquTCPZpsc5hg8Uwdvl5TViPgPh31fXN9Lx0XDpYwS0dKaqP8Dda7kYFeGkcw5q+xt5fpTRBTpdkNeV+VsiEy7fUGIMBmgXBGtMDktu7VhSzW793B+m9yWlUeK1bTzmqYAwDJDnZYy93+o53ud+ixWuTe/cAaHTNexf+2VZZNu8r0JcvUKm4fs5DrKVaPtpjJLvFxJ0uSaCgBlL2ia55vJk+Tzbe9r6o/6eqziHT97LSufPyhsu0z8HJwLGvi+j18LJd8XFEBbG92kkuEaa9wywfqHdo59e/av9eSasxU6SuyH/0Juf/OV/8eM26icC5OzeoRrbj/Lo9r0/+H1XABRDf9vlrQXVrYZw5vrlbmNSNteNsztPs8CRV1+5/oXf9WUolnjo6P9Z3C1KbNlanXPTt1Fxfrs7vz1pBZkeR55/zN7u3s2bN9s1e3+WhllvfWrh3TZymJ0EzGx+73hVr4KqEIVbxcTMmHwDCEF/8O1PfuDtT3yx6kJHeenWw5iMzXnmyPp/6PuupOaobgshbBJBz1y7MtmeNjZ/qpeAvPLKtSuvXl/5vy04ADWO5uVyjTbHC5LObXcvn9sguTz2sbe3t7u72zrgMLE/HGxWjrCMpcWTS3lZwZat9YG2JSOtrokm2V8xVOyooiND0CB1ZIBpbii62ijPXsxXjPv0aRmWbiWlxz18L8QpHw1g8cH9HKU+ppkzuDm4KVE693eKGMrqRt+sZe4sbFkpDS+wQZtS/pYcpHdgsqFaCgEaPJLjXLynLVCwoVpfg8bcMiPfKVxwMXF4dwkQtc13XDLkPnNqPXMJsRPQxYvzq37vtIsJvwmOsxwszQahpBbfHjB2pFN3wPqAb8CfX7qHaKcx9dX6yNbP8O58Fm6OnqSV/lmpbagCHfkFtWcAjL0IgWLUJELVGENaWpEUYhA8Fb1/WHVZA44fvurpKWE2qIgkA82Dc0KlHX9BCDFLaV5fk5vhzI88sefTD8lG6+ctNta+K6G2Li/dmVvCQ9uwpb40QBEUIVlpOJzI9xAE9UY4JP7uM9tXP3dlWLo6hUkXQlh37U5DuvPmu2k2CP7frp3Ei9/+WuiiLB1nI1/aHGLmMlAzlf/hw0e2bzjwY8/h1vT21uacnk71woUXWh8A8mt39t+/taeZ42kuh+4H09qdRKPARaZlwSk6reYwXi8Kpf8ArbbG9oMp0Cbuep+a/jVQqBq6wLTUATE83cp9jO+fCfCMpEUFO8xdacy8GYqwaLi/OlbWnw3JDg4HdwBrm/7aOkQRQ6dN9++x9TltPiJdp38+GNTrGGvlia9BNfeG9neGecT8azWwTBu2Vm+S1TSJ0z2rFjVpo0oFoJV8cowublZqDmaL8Z4S8ykd5KpixQ3MWn2ppYlPCaSocbBcRvXra0BEodp0MRVUFydaYgzTLl86ONDM2EAR3NmND+aZB4V7UBJvuXmtn1+LA9CbIalRfp15wCd7ieVAx0YvYy8SYwyTIBRLMCbkyd0UCKJBjPiqEgAW6bBro8t/1UKYiMHPr8ny66/GkJtf1+FCvyVp8jVuwiTJtQPUCyjNoKI6v8agfDdQ11ss1qSUZnot88FloKFTncTRIJRBzIxZFaFRaYRkWSmPv1D7tiI/OGObKsnPu32asXwgovSuxNgazNvAHP85kj/x8cO//gPv5itCvlr8xlcu/IaXz7c+YLJHn9zUENpY0MbZ7eU+yAEMS2nJKUhDWIzXKH725z/4qZ+vUiVV/YlffPfg7n5QVO9DphuThQ1md3e/fTpC6Pd2RAPNOHiY4d7jvugNG4MYTBEIgxjiHKCDKj7GlhZZixIw5vJR16vBjORJXEc0mJDilTgJP/HJwx95/97YHokD5c8Bv+mV88YWAJwef3yrcQhf+Nz1lfE4DWHn+uW1szTAkfX/9t//gRAqhnZvdnh4eIDqSWoMZ14+FzotXXGPrL+7u4e2ti3GO3uDKa1P6XAYDgbrB7/WLBwBskuoPi8beLciFlhiVktanlwLLf+Z1GAUwdjKm2Tb35FW23CM7QVFEaJkOr7kug6IhKDLAyhcAwvBp6tdza0X23+zCF1AfXy7BC3ecY2eGSUhnAMDmdG0VV1oVEJEEZlYYB0CVVBktCCR38qMrsGoviJGo3Ok8+ZX37w7ARSClvIKiLjzjJq8lFkdhfdcDLeyFwf4QaaeHgGkmlVUUQERBBYtGdqTOwTmyWhm5+vY91GBXGYdBFSdC96YlLKQ3veiwvvO5heybW0LyHM2bGBibQDo5aRJDOY7tGeushEAEMywjiK9OxV5DKUTloiHVky8elKGUqFDZRBSYxAAJaTRXt3gayNW32W+NgUgznw43UqGet4rh6IyOOLrKyGlgFcH88Wt2q4el45xNaPaEHISvNtGRZCWah8XZkFq6lq7CNUSZdVOJ1sTx6hFzTK64XCYaQ8NFiONBhxquJNkWJY2xMH+sPdgv7WLCrdBrI+geDSwfU4I2J/104m2W9FBDz7hbVv4iOTi7gVwSGkQ9t6MvCwPIK3xeJazS15AsgOyzUM+BZdZBxQyAnoIkvOJdbxWKwReQk7y3KsvXnj9pSJO6TbiK99/rZvG6kzIrffvH321ZQo/PQlvfqLL37fHv/LB47u/2NC0cQb2p7vHZ2Fc5076YODffO/wwWDtDv8dm/zKd5y3Rpj1yx/a/d09AVrr7378sPXk5Nz03Lkz0oyBeLhL6y1DXB1hW3dvs1qABIHndj0hU5A4Wu9cAAqvjomjNztFEAQVzccpkRzUsBCnk25rWurbu2ncOrd95IbWBhs7h3G6D5UyDikHacUq8WB/ePBgXxoHnIM9nuyGNR3wuOfHd/fvzQjUa+DnrkymL0wSqwOi6oo3gARF50O2ajKmjs1tAIFbTbyUEZKEPhvp/O2YdQOQlJcolMYLaPIwrOTvXPBXIv3wT40n5OmyoE+HVNaCNAOroymlwLpQp9aGFzjh1BMcdQCgrDtORkTSV54SdHtSC2Rgu/moQGJBsHDIRxsrQrDSPxxGGpi8GsSvaw0r5LMxlpiidC2csw5HdSPNRIDkDWVUosZQVnwzUwEpLemsNuUGmFlFYgJrJ4Pfvxa4SAsBE5QJ/Clw3rDmY1xdPv80ntxoguUtLQOLMstFiZojbAOqpI6sHQjpmVonYA21wjuGjVAbBhjNxtB/kSaqV4VrAOAu3NjZhNagKI2TzclkI5IspV5Dn5683nbT2C4dKUsxllpfg8YuSrsEiT0SXfnyZcBasdHDgRPIZrMEGSXqoi68C7o1/yEp0seOUod1XZ8NOjqjN488l2qOiiFOlGQiLDHMQqAHgJd+y+9sYYsl6N+29kcWaiMrBtJ0Z/O3/Zk/sPnCVo1OU7SL2iSzhj599Mu3Wx+QvPji2Qsvnm3fj1sf5HMRlraHWlD+gsOw997HHIblc35299Hs3qMSUZ9AvnsLk3ls7KUz8dLOnHH7ZMP8oXPWdT/30huz2JWPfefN9++++UF59ZF1f0FzQ+aid7ba/NqYKpEbWkvtci9J5kYE2fq5QBAQ0UKGVQ1KinhRMY+sv3W+jVC6b8tHzD6YHfRt0Wx+A+qsVISgsmrogugRSCKPRBOXfy8Ok8x6k7HebVNlAmzq3HyPT/g+I7ilGaHrwvamdpPy21mIh7Pkywi8IFBLRU1Qz9T2yCGKcmJBASIl58pF7YIYTdy4+Uvoap/gLdw0L1As31xicEvYeIsRq0+pe+9YuABZMRZQjnjix/J0uw4XNF7wHsiiAi3FX5ohrkWa5iZKhoX0Bhwvmkf08I6gvTZA54OgoY0HkvLZoLCKl6uEUFXaqu6TTwu16h2QvCBwPoumqjh2qa9oRSNvKWWl/MrZW9bHli1S7nnrJbe5sN3C5dy2NMsMmtGaF48i5fVuLyu2mM04fcY9S8edMICobYF8YRqeLLMcQ5SRZsIK79CYizQrkOjyt1279NoVS6T5JhEnXbc5oSxXl+jll86ltEjW/OSdu3NhhnsHK35fyvb5zZ3zU+Hctnz2wmT58UkUs1/4P7P9RzJqzbc6/fwr20d/ptQxnehGF1qr3t/tj76Wc9l3rl2EU4M8A0izxzdu2ZDKLcr7Bvt5kidkrIJAEa03KEYSF/2qraP+Hbj02tXv+r3fb4nAnAmEK3bOyy+fm3f5V63/8Tt359fDlfbnkfWvvXZhcQ7hkiwdCDrbezR75z1RlM61n3/1zNY0LpwdFuflJ3v3H/ey1APbVy/sXLvQdvYbDmf7d+/lIKgn3JNLCDnU1pJjdTuy/zK82zQ6M1c7LxX2mm5XFNGn/7NiagvGF+uvt8I14d2+ALSrrl9FV2fu1+5p4IsMqojNYSvJivVlMUeLGDQi2pAyjB4K5KwwOXIgiujns3HKjFiuJ6DfpQZ6QVmJ/7eF852GqJHJqEJAXKFYcSscaR+fjZWDIseVFiZkKeRzQ4YMIUJ9J5uXIOZKBBGrCTPFHO7G+A2eWetTKgsElVz/OcJ2HcIpliXHlB0OR18Cl9VCtWEIef3vSEuqbnB2tI36BoUv/c06+nXtkZTLdNs6shD0VHDRvf25uaLo0tBNoyhGbOWp0IucdHZmqw1oWuxEsdJrX3XAbMDx8P4updqStMGkh4nNTYoR3k0mgzFLVsiyqNE3kK/jCF149fuvxUmFwIaoXCX8P7L+wd/9r3zU5G0o3311+t2/6aqxunbaBa5y5OF3v/bgxZfR3Hv7WbJfuiOztMz+ObA4S1DVCA0evxkRcAakgoUWYASjMwq8x6Fg5MS53Hx8a+zrLaeMkziZxvUcbzyyPh/sCppI56W4Nd2m8fSxD4jYpEtntrRlrx0Oq0QcKIXWCAINTkjpyjW2rmTmLVVzYD/FtjtVTcKUsGjmvn29x1O9dlhQqDP/ic9e3UeusQfVnbbI0EtcmR6iGsNEyRjHRartTm9MUmggp/jxnw0KBBWtIpWd0yLUYj5nwvyEajTGqjYv6/5AJpbC1c/sf8rpnwU4JSnMxFLfWjwkyqwjMaaRlqKgwrEBxzYXSHaAh6btm9IDqvO/PUix5trI0726IDEfwcPTzrhcpJ7jj0xmvQhEOQYeNHsGREuEs1iTpcnCtHv9t39XtzkpWQGKXPmO6/wm8wEP++En3zz6M0oeMQ1HZ554Kbbr9tULGxQut/6t8xdunztfFwry9vkLWH8F0hgvvPFSmvWkyJid37/74ODeQ8f+iZYaOg2ak58iEstVg8bQxe/8vZ/furBTPlCJ7X1zve2Hff8Dv1DOPKR003h04tyaLibpyBXb9pH1f/HV15XWBNYE5PrTP5x/7f+bEzEqbv/iu7s37gURQgigJRePCqTIJnk/ws6M3/wLv2KuuEVRAm3rDbJddvCp9MjyikVvygfNckIjUc/C+R8U/xexI8AObM8dyQAAAABJRU5ErkJggg==' 
        ICON = pygame.image.load(io.BytesIO(base64.b64decode(ICON)))
        pygame.display.set_icon(ICON)
        pygame.display.set_caption('Jungle Climb')
        self.clock = pygame.time.Clock()
        self.ticks = 0
        import objects 

        from objects import World
        from objects import Player
        self.hide_mouse()
        if not self.music_playing and self.config['background_music']:
            pygame.mixer.Channel(0).play(self.MUSIC_SOUND, loops=-1)
            pygame.mixer.Channel(0).set_volume(0)
            self.music_playing = True
        self.world = World()
        self.player = Player(self.world)
        self.player.force_stop()
        self.world.set_player(self.player)
        self.world_shift_speed = 0
        self.speed_increment = round(WORLD_SHIFT_SPEED_PERCENT * self.SCREEN_HEIGHT)
        self.MAX_SPEED = self.speed_increment * 4
        self.score = 0
        self.prev_score = 0
        self.time_game_started = datetime.datetime.now()
        self.shift_threshold = 0.75 * self.SCREEN_HEIGHT
        gap_x1, gap_x2 = self.get_gap_position()
        event = Event(self.player.rect.left, self.player.rect.top, gap_x1, gap_x2, self.music_playing, self.player.is_on_ground(), self.player.get_facing_side(), self.score, 0)
        self.notify(event)
