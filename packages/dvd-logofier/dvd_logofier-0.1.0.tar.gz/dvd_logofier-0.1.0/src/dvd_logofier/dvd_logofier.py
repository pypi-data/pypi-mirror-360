import typer
from typing_extensions import Annotated
from typing import List, Optional
import pygame
import math
import sys
import warnings

imageTest = "~/dev/dvd-logofier/DVD_logo.png"

image1 = "test.png"
image2 = "test2.png"
image3 = "test3.png"
image4 = "test4.png"
image5 = "test5.png"

images = [image1, image2, image3, image4, image5]

def dvd_logofier(
    image_filename: Annotated[Optional[List[str]], typer.Argument(help="The filename of the image which should bounce; multiple filenames can be given. When there are multiple filenames, the next in the series will be selected any time a wall is hit.")],
    initial_position_x: Annotated[int, typer.Option(help="The initial x-position of the center of the image on the screen. Defaults to 360. Y defaults to 240.")] = 360,
    initial_position_y: Annotated[int, typer.Option(help="The initial y-position of the center of the image on the screen. Defaults to 240. X defaults to 360.")] = 240,
    vector_x: Annotated[int, typer.Option(help="The initial x-vector, i.e. the x-direction, of the image, given as an integer. The whole vector defaults to (1, 1), the right lower corner. Note, that the vector is normalized before being applied, to change the speed use the velocity parameter.")] = 1,
    vector_y: Annotated[int, typer.Option(help="The initial y-vector, i.e. the y-direction, of the image, given as an integer. The whole vector defaults to (1, 1), the right lower corner. Note, that the vector is normalized before being applied, to change the speed use the velocity parameter.")] = 1,
    velocity: Annotated[int, typer.Option(help="The velocity of the bouncing image, given in pixel per frame (60 FPS). Default to 1.")] = 1,
    screen_width: Annotated[int, typer.Option(help="The width of the window in which the bouncing is simulated, given as an integer in pixels. The whole screen size defaults to (720, 480).")] = 720,
    screen_height: Annotated[int, typer.Option(help="The height of the window in which the bouncing is simulated, given as an integer in pixels. The whole screen size defaults to (720, 480).")] = 480,
    background_color: Annotated[str, typer.Option(help="The background color of the screen, given as a hex value. Defaults to black '#000000'")] = '#000000'
    ):

    def get_image_dict(image_filename):
        image = pygame.image.load(image_filename)
        image_dimensions = image.get_size()
        return {
            "image": image,
            "image_dimensions": image_dimensions
        }

    def wrong_position_error():
        raise ValueError("initial_position can't lay outside the screen. Note, that initial_position describes the position of the image's center.")

    def hex_to_rgb(value):
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

    initial_position = (initial_position_x, initial_position_y)
    vector = (vector_x, vector_y)
    screen_size = (screen_width, screen_height)
    background_color = hex_to_rgb(background_color)
    

    pygame.init()
    pygame.display.set_caption("DVD-Logofier")
    screen = pygame.display.set_mode(screen_size)
    clock = pygame.time.Clock()

    vector = pygame.math.Vector2(vector[0], vector[1])
    vector.normalize()

    velocity = int(math.sqrt(velocity*velocity))

    last_wall = -1

    images = []
    image_index = 0
    if type(image_filename) == str:
        images.append(get_image_dict(image_filename))
    elif type(image_filename) == list:
        for filename in image_filename:
             images.append(get_image_dict(filename))
        image_dimensions = images[image_index]["image_dimensions"]
        for i, image in enumerate(images):
            if not image["image_dimensions"][0] > 0 or not image["image_dimensions"][1] > 0:
                raise ValueError("The image dimensions can't be negative.")
            if image["image_dimensions"][0] > screen_size[0] or image["image_dimensions"][1] > screen_size[1]:
                raise ValueError("The image dimensions can't be greater than the screen_size.")
            if image["image_dimensions"] != image_dimensions:
                warnings.warn(f"It's not recommended to have alternating image sizes. The image at index {i} has differing dimensions to the first image in the list.", stacklevel = 2)
    else:
        raise TypeError("image_filename must be of type str or list.")

    position = (initial_position[0] - (images[image_index]["image_dimensions"][0] / 2), initial_position[1] - (images[image_index]["image_dimensions"][1] / 2))
    left_edge = position[0]
    right_edge = position[0] + images[image_index]["image_dimensions"][0]
    upper_edge = position[1]
    lower_edge = position[1] + images[image_index]["image_dimensions"][1]

    if lower_edge >= screen_size[1]:
        wrong_position_error()
    elif upper_edge <= 0:
        wrong_position_error()
    elif right_edge >= screen_size[0]:
        wrong_position_error()
    elif left_edge <= 0:
        wrong_position_error()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(background_color)

        screen.blit(images[image_index]["image"], position)

        for _ in range(velocity):
            position = (position[0] + vector.x, position[1] + vector.y)
            left_edge = position[0]
            right_edge = position[0] + images[image_index]["image_dimensions"][0]
            upper_edge = position[1]
            lower_edge = position[1] + images[image_index]["image_dimensions"][1]

            if lower_edge >= screen_size[1] and last_wall != 'S':
                position = (position[0] - vector.x, position[1] - vector.y)
                vector.y = vector.y * -1
                last_wall = 'S'
                image_index += 1
                if image_index >= (len(images)):
                    image_index = 0
            elif upper_edge <= 0 and last_wall != 'N':
                position = (position[0] - vector.x, position[1] - vector.y)
                vector.y = vector.y * -1
                last_wall = 'N'

                image_index += 1
                if image_index >= (len(images)):
                    image_index = 0
            elif right_edge >= screen_size[0] and last_wall != 'E':
                position = (position[0] - vector.x, position[1] - vector.y)
                vector.x = vector.x * -1
                last_wall = 'E'

                image_index += 1
                if image_index >= (len(images)):
                    image_index = 0
            elif left_edge <= 0 and last_wall != 'W':
                position = (position[0] - vector.x, position[1] - vector.y)
                vector.x = vector.x * -1
                last_wall = 'W'

                image_index += 1
                if image_index >= (len(images)):
                    image_index = 0
                
 
        pygame.display.update()
        clock.tick(60)

