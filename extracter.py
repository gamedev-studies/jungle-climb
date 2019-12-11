# from PIL import Image
import pygame as pg


def extract_platforms(source_path='Assets/jungle tileset.png') -> list:  # each tile is 16x16
    """
    Extracts platform tiles from the tilesheet and returns them as a list

    :param source_path: the relative path to the tilesheet
    :return:list of images for each platform tile
    """

    # im = Image.open(source_path)
    sheet = pg.image.load(source_path).convert_alpha()
    images = [sheet.subsurface((0, 16, 27, 27)),
              sheet.subsurface((26, 16, 27, 27)),
              sheet.subsurface((53, 16, 27, 27))]
    # im.crop((0, 16, 80, 48)).show()
    # images = [im.crop((0, 16, 27, 43)).convert('RGBA'), im.crop((26, 16, 53, 43)).convert('RGBA'),
    #           im.crop((53, 16, 80, 43)).convert('RGBA')]
    # TODO: crop vines
    # [top_left, centre, top_right]
    return images


def extract_images(source_path: str, sprite_width: int) -> list:
    """
    Extracts images from a sprite sheet and returns them as a list

    :param source_path: relative path to sprite sheet
    :param sprite_width: width of a sprite in pixels
    :return: list of images of the sprite sheets
    """
    # im = Image.open(source_path)
    sheet = pg.image.load(source_path).convert_alpha()
    # width, height = im.size
    width, height = sheet.get_size()
    num_of_sprites = int(width / sprite_width)
    images = []
    for x in range(num_of_sprites):
        images.append(sheet.subsurface(x * sprite_width, 0, sprite_width, height))
        # images.append(im.crop((x * sprite_width, 0, (x + 1) *
        #                        sprite_width, height)).convert('RGBA'))
    return images


if __name__ == '__main__':
    # extract_images('Jungle Asset Pack/Character with outline/sprites/run outline.png', 23)
    extract_platforms()[1]
