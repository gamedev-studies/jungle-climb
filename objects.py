import random
from math import ceil

import pygame
from extracter import *


# Todo: comment code

def load_image(image):
    return pygame.image.fromstring(image.tobytes(), image.size, image.mode).convert_alpha()

def scale_image(image, new_width, new_height):
    return pygame.transform.scale(image, (new_width, new_height))


class Player(pygame.sprite.Sprite):
    # INITIAL_SPEED = 3
    # RUNNING_SPEED = 6
    # JUMP_SPEED = -20
    PERCENT_OF_SCREEN_HEIGHT = 0.1296296296296296
    CHANGE_ANIMATION = 4  # Todo: make this a dictionary

    facing_left = False
    on_ground = True
    idle_index = 1
    running_index = 0
    speed = [0, 0]

    animation_frame = 'idle'

    # sprite paths
    # idle_sprite_path = 'Jungle Asset Pack/Character with outline/sprites/idle outline.png'
    # jump_sprite_path = 'Jungle Asset Pack/Character with outline/sprites/jump outline.png'
    # landing_sprite_path = 'Jungle Asset Pack/Character with outline/sprites/landing outline.png'
    # mid_air_sprite_path = 'Jungle Asset Pack/Character with outline/sprites/mid air outline.png'
    # run_sprite_path = 'Jungle Asset Pack/Character with outline/sprites/run outline.png'

    idle_sprite_path = 'Jungle Asset Pack/Character/sprites/idle.png'
    jump_sprite_path = 'Jungle Asset Pack/Character/sprites/jump.png'
    landing_sprite_path = 'Jungle Asset Pack/Character/sprites/landing.png'
    mid_air_sprite_path = 'Jungle Asset Pack/Character/sprites/mid air.png'
    run_sprite_path = 'Jungle Asset Pack/Character/sprites/run.png'

    @staticmethod
    def scale_image(image: pygame.Surface, scale_factor) -> pygame.Surface:
        """
        Scales and returns the given image
        :param image: the original pygame.Surface
        :param scale_factor: how much to scale the image by
        :return: the scaled image
        """
        width, height = image.get_rect().size[0], image.get_rect().size[1]
        return pygame.transform.scale(image, (int(width * scale_factor), int(height * scale_factor)))

    def __init__(self, world, pos: tuple = None):
        """
        :param pos: (x, y) tuple where 0, 0 is the top left
        """
        super().__init__()

        self.world = world
        current_h = pygame.display.Info().current_h
        current_w = pygame.display.Info().current_w
        # if pos is None: pos = (0.05 * info_object.current_w, 0.07901234567901234 * info_object.current_h)

        # 35 is the height of the sprite in pixels
        # todo: set running speed and jump height based on screen width and height
        self.RUNNING_SPEED = round(current_w / 200)
        self.JUMP_SPEED = (round(current_h / -40.5))
        self.GRAVITY_CONSTANT = -0.05 * self.JUMP_SPEED
        # print(self.JUMP_SPEED)
        # print(self.GRAVITY_CONSTANT)
        # 35 is the idle height for outline, 34 is for no outline
        scale_factor = current_h * self.PERCENT_OF_SCREEN_HEIGHT / 34
        idle_images_right = []
        idle_images_left = []
        self.idle_images = [idle_images_right, idle_images_left]
        for image in extract_images(self.idle_sprite_path, 19):  # 21 with outline, 19 without
            image = pygame.image.fromstring(image.tobytes(), image.size, image.mode).convert_alpha()

            image = self.scale_image(image, scale_factor)
            idle_images_right.append(image)
            idle_images_left.append(pygame.transform.flip(image, True, False))

        jump_image = pygame.image.load(self.jump_sprite_path).convert_alpha()
        jump_image = self.scale_image(jump_image, scale_factor)
        self.jump_images = [jump_image, pygame.transform.flip(jump_image, True, False)]

        landing_image = pygame.image.load(self.landing_sprite_path).convert_alpha()
        landing_image = self.scale_image(landing_image, scale_factor)
        self.landing_images = [landing_image, pygame.transform.flip(landing_image, True, False)]

        mid_air_images_right = []
        mid_air_images_left = []
        self.mid_air_images = [mid_air_images_right, mid_air_images_left]
        for image in extract_images(self.mid_air_sprite_path, 20):  # 22 with outline , 20 without
            image = pygame.image.fromstring(image.tobytes(), image.size, image.mode).convert_alpha()
            image = self.scale_image(image, scale_factor)
            mid_air_images_right.append(image)
            mid_air_images_left.append(pygame.transform.flip(image, True, False))

        run_images_right = []
        run_images_left = []
        self.run_images = [run_images_right, run_images_left]
        for image in extract_images(self.run_sprite_path, 21):  # 23 with outline, 21 without
            image = pygame.image.fromstring(image.tobytes(), image.size, image.mode).convert_alpha()
            image = self.scale_image(image, scale_factor)
            run_images_right.append(image)
            run_images_left.append(pygame.transform.flip(image, True, False))

        # first percent is the grass percent of the tile (3/TILE_SIDELENGTH)
        # second percent is the percent of screen height for a tile
        self.GROUND_ADJUSTMENT = ceil(0.1111111111111111 * 0.07901234567901234 * current_h)

        self.image: pygame.Surface = idle_images_right[0]
        # fixme: collision rect
        self.rect: pygame.Rect = self.image.get_rect()
        collide_width = self.rect.width - 8 * scale_factor
        self.collide_rect: pygame.Rect = pygame.rect.Rect((0, 0), (collide_width, self.rect.height))
        if pos is None:
            pos = (0.05 * current_w, 0.92098765432098766 * current_h + self.GROUND_ADJUSTMENT)
        self.rect.bottomleft = pos
        self.collide_rect.midbottom = self.rect.midbottom

    def get_image(self, images: list, index: int = None) -> pygame.image:
        """
        gets an image from a list of right images and left images according to direction player is facing
        :param images: list containing a right facing image(s) [0] and left facing image(s) [1]
        :param index: index of the image to return. if equal to None, images does not contain lists
        :return: the image of proper facing direction
        """
        if index is None: return images[self.facing_left]
        return images[self.facing_left][index]

    def update_idle(self):
        """
        Updates the idle animation
        """
        if self.CHANGE_ANIMATION <= 0:
            self.image = self.get_image(self.idle_images, self.idle_index)
            # self.image = pygame.transform.flip(self.idle_images_right[self.idle_index], self.FACING_LEFT, False)
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
            # self.image = pygame.transform.flip(self.run_images_right[self.running_index], self.FACING_LEFT, False)
            self.running_index += 1
            self.CHANGE_ANIMATION = 4
            if self.running_index >= len(self.run_images[0]): self.running_index = 0
        else:
            self.CHANGE_ANIMATION -= 1

    def gravity(self):
        self.on_ground = False
        for platform in pygame.sprite.spritecollide(self, self.world.platform_list, False):
            if self.rect.bottom >= platform.rect.top + self.GROUND_ADJUSTMENT:
                self.on_ground = True
                break
        if not self.on_ground:
            # TODO: add landing image if statement
            self.speed[1] += self.GRAVITY_CONSTANT
            if self.speed[1] > 0 and self.animation_frame != f'mid-air down {self.facing_left}':
                self.image = self.get_image(self.mid_air_images, 1)
                # self.image = pygame.transform.flip(self.mid_air_images_right[1], self.FACING_LEFT, False)
                self.animation_frame = f'mid-air down {self.facing_left}'
            elif 0 > self.speed[1] >= -12 and self.animation_frame != f'mid-air up {self.facing_left}':
                self.image = self.get_image(self.mid_air_images, 0)
                # self.image = pygame.transform.flip(self.mid_air_images_right[0], self.FACING_LEFT, False)
                self.animation_frame = f'mid-air up {self.facing_left}'

    def update(self):
        self.gravity()
        self.rect.x += self.speed[0]
        platform_hit_list = pygame.sprite.spritecollide(self, self.world.platform_list, False)  # detect collisions
        for platform in platform_hit_list:
            if (self.speed[0] > 0 and
                    platform.rect.left < self.rect.right and
                    platform.rect.top + self.GROUND_ADJUSTMENT < self.rect.bottom):
                self.rect.x = platform.rect.left  # going right
            elif (self.speed[0] < 0 and
                  platform.rect.right > self.rect.left and
                  platform.rect.top + self.GROUND_ADJUSTMENT < self.rect.bottom):
                self.rect.x = platform.rect.right  # going left

        self.rect.y += self.speed[1]

        platform_hit_list = pygame.sprite.spritecollide(self, self.world.platform_list, False)  # detect collisions
        for platform in platform_hit_list:
            if self.speed[1] > 0 and self.rect.bottom > platform.rect.top + self.GROUND_ADJUSTMENT:  # going down
                # fixme
                self.rect.bottom = platform.rect.top + self.GROUND_ADJUSTMENT
                self.speed[1] = 0
            elif self.speed[1] < 0:  # going up
                # fixme
                self.rect.top = platform.rect.bottom
                self.speed[1] = 0
        # if self.speed == [0, 0] and will_land and self.ON_GROUND:  # if standing still
        if self.speed == [0, 0]:  # if standing still
            self.update_idle()
            self.animation_frame = 'idle'
        elif self.speed[0] != 0 and self.on_ground:  # animate only if running on the ground
            self.update_running()
            self.animation_frame = 'running'

    def stop(self, pressed_keys):
        if self.speed[0] == 0:

            # if right keys are still pressed
            if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]: self.speed[0] += self.RUNNING_SPEED

            # Left keys still pressed
            if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]: self.speed[0] -= self.RUNNING_SPEED

            if self.speed[0] > 0:
                self.facing_left = False
            elif self.speed[0] < 0:
                self.facing_left = True

        elif (pressed_keys[pygame.K_LEFT] + pressed_keys[pygame.K_a] +
              pressed_keys[pygame.K_RIGHT] + pressed_keys[pygame.K_d] == 0):
            if self.on_ground: self.image = self.get_image(self.idle_images, 0)
            self.speed[0] = 0

    def force_stop(self):
        self.speed = [0, 0]

    def go_left(self):
        if self.speed[0] > -self.RUNNING_SPEED:
            self.speed[0] -= self.RUNNING_SPEED
        self.facing_left = True

    def go_right(self):
        if self.speed[0] < self.RUNNING_SPEED:
            self.speed[0] += self.RUNNING_SPEED
        self.facing_left = False

    def jump(self):
        """ Called when user hits 'jump' button. """
        # note: player can jump to a height of two platforms
        if self.on_ground:
            self.image = self.get_image(self.jump_images)
            # self.image = pygame.transform.flip(self.jump_frame, self.FACING_LEFT, False)
            self.speed[1] = self.JUMP_SPEED
            self.on_ground = False
            self.animation_frame = 'jump'


class Platform(pygame.sprite.Sprite):
    PERCENT_OF_SCREEN_HEIGHT = 0.07901234567901234
    side_length = TILESET_SIDELENGTH = 27
    scale_factor = PERCENT_OF_SCREEN_HEIGHT * pygame.display.Info().current_h / TILESET_SIDELENGTH
    side_length = int(side_length * scale_factor)
    images = [load_image(image) for image in extract_platforms()]
    print(side_length)
    image_0 = pygame.transform.scale(images[0], (side_length, side_length))
    image_1 = pygame.transform.scale(images[1], (side_length, side_length))
    image_2 = pygame.transform.scale(images[2], (side_length, side_length))
    images = [image_0, image_1, image_2]
    # images = [scale_image(image, side_length, side_length) for image in images]
    images = {'left': images[0], 'centre': images[1], 'right': images[2]}
    
    # [platform_left, platform_centre, platform_right]

    def __init__(self, x, y, platform_type='centre'):
        super().__init__()
        # 16 is the height of the sprite in pixels
        # TODO: this isn't the right calculation
        self.image = self.images[platform_type.lower()]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class World(object):
    TILESET_SIDELENGTH = 27
    P_PLATFORM = 0.8  # probability of platforms
    difficulty = 1

    def __init__(self):
        TILESET_SIDELENGTH = 27
        self.platform_list = pygame.sprite.Group()
        self.player = None
        self.screen_width, self.screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
        self.scale_factor = 0.07901234567901234 * pygame.display.Info().current_h / TILESET_SIDELENGTH
        self.tileset_new_sidelength = int(TILESET_SIDELENGTH * self.scale_factor)
        self.number_of_spots = self.screen_width // self.tileset_new_sidelength
        pos_y = self.screen_height - self.tileset_new_sidelength
        for x in range(ceil(self.screen_width / self.tileset_new_sidelength)):
            pos_x = x * self.tileset_new_sidelength
            # print(pos_x, floor((x+1) * self.scale_factor * self.TILESET_SIDELENGTH))
            platform = Platform(pos_x, pos_y)
            self.platform_list.add(platform)
        for x in range(1, ceil(self.screen_height / self.tileset_new_sidelength / 3)):
            # platforms are every 3 heights
            self.create_platforms(self.screen_height - self.tileset_new_sidelength * (1 + 3 * x))
        # todo: randomly generate the rest of the world as player goes up

    def draw(self, screen):
        self.platform_list.draw(screen)

    def create_platforms(self, pos_y, difficulty=1):
        # note: player can jump to a height of two platforms
        safety = -1
        # self.number_of_spots = self.screen_width // self.tileset_new_sidelength
        # note: spaces should be at 1.5x to 3x a tileset_new_sidelength
        for x in range(self.screen_width):
            if random.random() <= self.P_PLATFORM and x > safety:
                if difficulty > 1:
                    num_of_platforms = random.randint(5, 13)
                else:
                    num_of_platforms = random.randint(3, 10)
                safety = x + num_of_platforms * self.tileset_new_sidelength + random.choice([1.5, 2, 2.5]) * self.tileset_new_sidelength
                for y in range(num_of_platforms):
                    if y == 0: platform_type = 'left'
                    elif y == num_of_platforms - 1:  platform_type = 'right'
                    else: platform_type = 'centre'
                    platform = Platform(x + y * self.tileset_new_sidelength, pos_y, platform_type)
                    self.platform_list.add(platform)
            elif x > safety:
                safety = x + 1.5 * self.tileset_new_sidelength

    def shift_world(self, shift_y):
        """For automated scrolling"""

        platforms_to_remove = []
        farthest_y = self.screen_height
        # Go through all the sprite lists and shift
        self.player.rect.y += shift_y
        for platform in self.platform_list:
            platform.rect.y += shift_y
            if platform.rect.y < farthest_y:
                farthest_y = platform.rect.y
            if platform.rect.top > self.screen_height + platform.rect.height:
                platforms_to_remove.append(platform)
        if platforms_to_remove:
            self.platform_list.remove(platforms_to_remove)
            self.create_platforms(farthest_y - self.tileset_new_sidelength * 3)

    def update(self):
        self.platform_list.update()

# class Button(pygame.sprite.Sprite):
#
#     def __init__(self, x, y, width, height, callback, text, text_color=(0, 0, 0), image_normal=None, imagae_hover=None,
#                  image_down=None):
#         super().__init__()
