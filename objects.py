import random
from math import ceil

import pygame
from extracter import extract_images, extract_platforms, scale_image


CURRENT_W, CURRENT_H = pygame.display.Info().current_w, pygame.display.Info().current_h
JUMP_SOUND = pygame.mixer.Sound('assets/audio/jump.ogg')
JUMP_SOUND.set_volume(0.3)


class Player(pygame.sprite.Sprite):
    # INITIAL_SPEED = 3
    PERCENT_OF_SCREEN_HEIGHT = 0.1296296296296296
    CHANGE_ANIMATION = 4  # Todo: make this a dictionary

    facing_right = True
    on_ground = True
    idle_index = 1
    running_index = 0
    speed = [0, 0]

    animation_frame = 'idle'
    IDLE_PATH = 'assets/sprites/idle.png'
    JUMP_PATH = 'assets/sprites/jump.png'
    LANDING_PATH = 'assets/sprites/landing.png'
    MID_AIR_PATH = 'assets/sprites/mid air.png'
    RUN_PATH = 'assets/sprites/run.png'

    RUNNING_SPEED = round(CURRENT_W / 200)
    JUMP_SPEED = round(CURRENT_H / -40.5)
    GRAVITY_CONSTANT = -0.05 * JUMP_SPEED
    # NOTE: 35 is the idle height for outline, 34 is for no outline
    scale_factor = CURRENT_H * PERCENT_OF_SCREEN_HEIGHT / 34
    idle_images = [[], []]  # left, right
    for image in extract_images(IDLE_PATH, 19, scale_factor):  # 21 with outline, 19 without
        idle_images[0].append(pygame.transform.flip(image, True, False))
        idle_images[1].append(image)

    jump_image = pygame.image.load(JUMP_PATH).convert_alpha()
    jump_image = scale_image(jump_image, scale_factor)
    jump_images = [pygame.transform.flip(jump_image, True, False), jump_image]

    landing_image = pygame.image.load(LANDING_PATH).convert_alpha()
    landing_image = scale_image(landing_image, scale_factor)
    landing_images = [pygame.transform.flip(landing_image, True, False), landing_image]

    mid_air_images = [[], []]  # left, right
    for image in extract_images(MID_AIR_PATH, 20, scale_factor):  # 22 with outline , 20 without
        # image = pygame.image.fromstring(image.tobytes(), image.size, image.mode).convert_alpha()
        mid_air_images[0].append(pygame.transform.flip(image, True, False))
        mid_air_images[1].append(image)

    run_images = [[], []]  # left, right
    for image in extract_images(RUN_PATH, 21, scale_factor):  # 23 with outline, 21 without
        run_images[0].append(pygame.transform.flip(image, True, False))
        run_images[1].append(image)

    # first percent is the grass percent of the tile (3/TILE_SIDELENGTH)
    # second percent is the percent of screen height for a tile
    GROUND_ADJUSTMENT = ceil(0.1111111111111111 * 0.07901234567901234 * CURRENT_H)

    def __init__(self, world, pos: tuple = None):
        """
        :param pos: (x, y) tuple where 0, 0 is the top left
        """
        super().__init__()

        self.world = world
        self.image: pygame.Surface = self.idle_images[1][0]
        # fixme: collision rect
        self.rect: pygame.Rect = self.image.get_rect()
        collide_width = self.rect.width - 8 * self.scale_factor
        self.collide_rect: pygame.Rect = pygame.rect.Rect((0, 0), (collide_width, self.rect.height))
        if pos is None:
            pos = (0.05 * CURRENT_W, 0.92098765432098766 * CURRENT_H + self.GROUND_ADJUSTMENT)
        self.rect.bottomleft = pos
        self.collide_rect.midbottom = self.rect.midbottom

    def get_image(self, images: list, index: int = None) -> pygame.image:
        """
        gets an image from a list of right images and left images according to direction player is facing
        :param images: list containing a right facing image(s) [0] and left facing image(s) [1]
        :param index: index of the image to return. if equal to None, images does not contain lists
        :return: the image of proper facing direction
        """
        if index is None: return images[self.facing_right]
        return images[self.facing_right][index]

    def update_idle(self):
        """
        Updates the idle animation
        """
        if self.CHANGE_ANIMATION <= 0:
            self.image = self.get_image(self.idle_images, self.idle_index)
            self.idle_index += 1
            self.CHANGE_ANIMATION = 4
            if self.idle_index >= len(self.idle_images[0]): self.idle_index = 0
        else:
            self.CHANGE_ANIMATION -= 1

    def update_running(self):
        """
        Updates the running animations
        """
        if self.CHANGE_ANIMATION <= 0:
            self.image = self.get_image(self.run_images, self.running_index)
            self.running_index += 1
            self.CHANGE_ANIMATION = 4
            if self.running_index >= len(self.run_images[0]): self.running_index = 0
        else:
            self.CHANGE_ANIMATION -= 1

    def gravity(self):
        self.on_ground = False
        for platform in pygame.sprite.spritecollide(self, self.world.platform_list, False):
            if self.rect.bottom == platform.rect.top + self.GROUND_ADJUSTMENT:
                self.on_ground = True
                break
        if not self.on_ground:
            # TODO: add landing image if statement
            self.speed[1] += self.GRAVITY_CONSTANT
            if self.speed[1] > 0 and self.animation_frame != f'mid-air down {self.facing_right}':
                self.image = self.get_image(self.mid_air_images, False)
                self.animation_frame = f'mid-air down {self.facing_right}'
            elif 0 > self.speed[1] >= -12 and self.animation_frame != f'mid-air up {self.facing_right}':
                self.image = self.get_image(self.mid_air_images, True)
                self.animation_frame = f'mid-air up {self.facing_right}'

    def update(self):
        self.gravity()
        self.rect.y += self.speed[1]

        platform_hit_list = pygame.sprite.spritecollide(self, self.world.platform_list, False)  # detect collisions

        for platform in platform_hit_list:
            if self.speed[1] > 0 and self.rect.bottom > platform.rect.top + self.GROUND_ADJUSTMENT:  # going down
                self.rect.bottom = platform.rect.top + self.GROUND_ADJUSTMENT
                self.speed[1] = 0
            elif self.speed[1] < 0 and platform.rect.top < self.rect.top < platform.rect.bottom:  # going up
                self.rect.top = platform.rect.bottom
                self.speed[1] = 0

        self.rect.x += self.speed[0]
        platform_hit_list = pygame.sprite.spritecollide(self, self.world.platform_list, False)  # detect collisions
        for platform in platform_hit_list:
            if (self.speed[0] > 0 and
                    platform.rect.left < self.rect.right and
                    platform.rect.top + self.GROUND_ADJUSTMENT < self.rect.bottom):
                self.rect.right = platform.rect.left  # going right
            elif (self.speed[0] < 0 and
                  platform.rect.right > self.rect.left and
                  platform.rect.top + self.GROUND_ADJUSTMENT < self.rect.bottom):
                self.rect.left = platform.rect.right  # going left
        # if self.speed == [0, 0] and will_land and self.ON_GROUND:  # if standing still
        if self.speed == [0, 0]:  # if standing still
            self.update_idle()
            self.animation_frame = 'idle'
            # if self.animation_frame != 'idle':
            #     self.animation_frame = 'idle'
            #     self.update_rect()
        elif self.speed[0] != 0 and self.on_ground:  # animate only if running on the ground
            self.update_running()
            self.animation_frame = 'running'
            # if self.animation_frame != 'running':
            #     self.animation_frame = 'running'
            #     self.update_rect()
        return self.rect

    def stop(self, pressed_keys):

        if self.speed[0] == 0:
            # if right keys are still pressed
            if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]: self.speed[0] += self.RUNNING_SPEED
            # if left keys are still pressed
            if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]: self.speed[0] -= self.RUNNING_SPEED
            if self.speed[0] > 0: self.facing_right = True
            elif self.speed[0] < 0: self.facing_right = False

        elif (pressed_keys[pygame.K_LEFT] + pressed_keys[pygame.K_a] +
              pressed_keys[pygame.K_RIGHT] + pressed_keys[pygame.K_d] == 0):
            if self.on_ground: self.image = self.get_image(self.idle_images, True)
            self.speed[0] = 0

    def force_stop(self):
        self.speed = [0, 0]

    def go_left(self):
        if self.speed[0] > -self.RUNNING_SPEED: self.speed[0] -= self.RUNNING_SPEED
        self.facing_right = False

    def go_right(self):
        if self.speed[0] < self.RUNNING_SPEED: self.speed[0] += self.RUNNING_SPEED
        self.facing_right = True

    def jump(self, play_jump_sound: bool):
        """ Called when user hits 'jump' button. """
        #  player can jump to a height of two platforms
        if self.on_ground:
            if play_jump_sound: pygame.mixer.Channel(1).play(JUMP_SOUND)
            self.image = self.get_image(self.jump_images)
            # self.image = pygame.transform.flip(self.jump_frame, self.FACING_LEFT, False)
            self.speed[1] = self.JUMP_SPEED
            self.on_ground = False
            self.animation_frame = 'jump'

    def update_rect(self):
        pos = self.rect.bottomleft
        self.rect: pygame.Rect = self.image.get_rect()
        collide_width = self.rect.width - 8 * self.scale_factor
        self.collide_rect: pygame.Rect = pygame.rect.Rect((0, 0), (collide_width, self.rect.height))
        # if pos is None:
        #     pos = (0.05 * current_w, 0.92098765432098766 * current_h + self.GROUND_ADJUSTMENT)
        self.rect.bottomleft = pos
        self.collide_rect.midbottom = self.rect.midbottom


class Platform(pygame.sprite.Sprite):
    PERCENT_OF_SCREEN_HEIGHT = 0.07901234567901234
    GROUND_ADJUSTMENT = ceil(0.1111111111111111 * 0.07901234567901234 * CURRENT_H)
    TILESET_SIDELENGTH = 27
    scale_factor = PERCENT_OF_SCREEN_HEIGHT * CURRENT_H / TILESET_SIDELENGTH
    images = extract_platforms(scale_factor=scale_factor)
    images = {'left': images[0], 'centre': images[1], 'right': images[2]}

    def __init__(self, x, y, platform_type='centre'):
        super().__init__()
        # 16 is the height of the sprite in pixels
        self.image = self.images[platform_type.lower()]
        self.rect = self.image.get_rect()
        w, h = self.image.get_size()
        w -= self.GROUND_ADJUSTMENT * 2
        h -= self.GROUND_ADJUSTMENT
        self.collide_rect = pygame.rect.Rect((0, 0), (w, h))
        self.rect.topleft = (x, y)
        self.collide_rect.midbottom = self.rect.midbottom


class World(object):
    P_PLATFORM = 0.8  # probability of platforms
    difficulty = 1

    def __init__(self):
        TILESET_SIDELENGTH = Platform.TILESET_SIDELENGTH
        self.platform_list = pygame.sprite.Group()
        self.player = None
        self.screen_width, self.screen_height = CURRENT_W, CURRENT_H
        self.scale_factor = 0.07901234567901234 * CURRENT_H / TILESET_SIDELENGTH
        self.tileset_new_sidelength = int(TILESET_SIDELENGTH * self.scale_factor)
        self.number_of_spots = self.screen_width // self.tileset_new_sidelength
        pos_y = self.screen_height - self.tileset_new_sidelength
        for x in range(ceil(self.screen_width / self.tileset_new_sidelength)):
            pos_x = x * self.tileset_new_sidelength
            platform = Platform(pos_x, pos_y)
            self.platform_list.add(platform)
        for x in range(1, ceil(self.screen_height / self.tileset_new_sidelength / 3)):
            # platforms are every 3 "rows"
            self.create_platforms(self.screen_height - self.tileset_new_sidelength * (1 + 3 * x))

    def draw(self, screen):
        self.platform_list.draw(screen)

    def create_platforms(self, pos_y):
        # Note: player can jump to a height of two platforms
        safe_spaces = 1.75, 2, 2.5, 3, 3.5, 4
        starting_pos = int(random.choice([-1, 0, 1, 1.5]) * self.tileset_new_sidelength)
        safety = starting_pos - 1
        for x in range(starting_pos, self.screen_width, int(self.tileset_new_sidelength * 0.25)):
            if x > safety:
                max_tiles = max(((self.screen_width - x) // self.tileset_new_sidelength), 2)
                num_of_tiles = min(random.randint(3, 10), max_tiles)
                safety = x + num_of_tiles * self.tileset_new_sidelength + random.choice(
                    safe_spaces) * self.tileset_new_sidelength
                for tile_number in range(num_of_tiles):
                    if tile_number == 0: platform_type = 'left'
                    elif tile_number == num_of_tiles - 1:  platform_type = 'right'
                    else: platform_type = 'centre'
                    platform = Platform(x + tile_number * self.tileset_new_sidelength, pos_y, platform_type)
                    self.platform_list.add(platform)

    def shift_world(self, shift_y=0, shift_x=0):
        """For automated scrolling"""
        platforms_to_remove = []
        farthest_y = self.screen_height
        # Go through all the sprite lists and shift
        self.player.rect.y += shift_y
        self.player.rect.x += shift_x
        self.player.collide_rect.y += shift_y
        self.player.collide_rect.x += shift_x
        for platform in self.platform_list:
            platform.rect.y += shift_y
            platform.collide_rect.y += shift_y
            platform.rect.x += shift_x
            platform.collide_rect.x += shift_x
            if platform.rect.y < farthest_y:
                farthest_y = platform.rect.y
            if platform.rect.top > self.screen_height + self.player.rect.height:
                platforms_to_remove.append(platform)
        if farthest_y > 0:
            self.create_platforms(farthest_y - self.tileset_new_sidelength * 3)
        if platforms_to_remove:
            self.platform_list.remove(platforms_to_remove)
            platforms_to_remove.clear()

    def update(self):
        self.platform_list.update()
