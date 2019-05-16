"""
Used for displaying Gama visualization using Pygame

"""

from typing import Any, Tuple, Optional

import numpy as np
import pygame

from rts.config.configuration import P_NAME_IDX, A_TYPE_IDX, d_a_color, d_type_rev, MONEY_IDX, TIME_IDX, CARRY_IDX, \
    HEALTH_IDX

SCREEN_SIZE = 1200


def message_display(game_display, text, position, text_size, color=(0, 0, 0)) -> None:
    """
    Display text on pygame window.
    :param game_display: Which canvas text will be rendered upon
    :param text: string text
    :param position: coordinates on canvas where text will be displayed
    :param text_size: ...
    :param color: (r,g,b) color
    """

    large_text = pygame.font.SysFont('arial', text_size)
    text_surf = large_text.render(text, True, color)
    text_rect = text_surf.get_rect()
    text_rect.center = position
    game_display.blit(text_surf, text_rect)


def init_visuals(world_width: int, world_height: int, verbose=True) -> Optional[Tuple[Any, Any, Any]]:
    """
    Creates canvas to draw upon and creates tick
    :param world_width: ...
    :param world_height: ...
    :param verbose: if verbose is set to false, game will not be initialized
    :return: game_display, clock
    """
    if verbose:
        pygame.init()

        # square canvas
        canvas_scale = int(SCREEN_SIZE * (2 / 3) / world_height)  # for drawing - it takes 2 thirds of screen height
        display_width, display_height = world_width * canvas_scale, world_height * canvas_scale  # for example 800

        # screen
        screen = pygame.display.set_mode((display_width, display_height))
        pygame.display.set_caption('RTS visualization Python game')

        # surface
        arena = pygame.Surface((display_width, display_height), 0, screen)

        # clock
        clock = pygame.time.Clock()

        return arena, screen, clock


def update_graphics(board: np.ndarray, arena, screen, clock, fps: int = 1) -> bool:
    """
    Executes game tick on canvas, redrawing whole game state. Values here are somewhat hardcoded, which can be changed to display game in some nicer config.
    RTSLogic size 8x8 is working best with this config, 6x6 might work as well, but other might not.
    :param board: game state that will be drawn
    :param game_display: canvas to draw game state upon
    :param clock: game tick
    :param fps: how many fps should pygame draw. if value is set to higher number than your pc can handle, it will draw at max possible.
    """
    n = board.shape[0]

    # square canvas
    canvas_scale = int(SCREEN_SIZE * (16 / 30) / n)  # for drawing - it takes 2 thirds of screen height

    # arena.fill((0, 0, 0))

    # clear display
    screen.fill((255, 255, 255))
    # self.display_img(game_display, x,y)

    # title
    # message_display(screen, u"" + ' ' + str(gold_p1), (int((n / 8) * canvas_scale), (n+1) * canvas_scale + int(int(canvas_scale / 12) + canvas_scale * (0 / 4) + int(canvas_scale * (1 / 8)))), int(canvas_scale / 6))

    # draw grid:
    for y in range(canvas_scale, (n + 2) * canvas_scale, canvas_scale):
        pygame.draw.line(screen, (0, 0, 0), [y, canvas_scale], [y, (n + 1) * canvas_scale])
        for x in range(canvas_scale, (n + 2) * canvas_scale, canvas_scale):
            pygame.draw.line(screen, (0, 0, 0), [canvas_scale, x], [(n + 1) * canvas_scale, x])
            if x < (n + 1) * canvas_scale and y < (n + 1) * canvas_scale:
                message_display(screen, u"" + str(x / canvas_scale - 1) + ", " + str(y / canvas_scale - 1),
                                ((x + canvas_scale / 4), (y + canvas_scale / 10)), int(canvas_scale / 8))

    # gold for each player:
    gold_p1 = board[int(n / 2) - 1][int(n / 2)][MONEY_IDX]
    gold_p2 = board[int(n / 2)][int(n / 2) - 1][MONEY_IDX]
    message_display(screen, u"" + 'Gold Player +1: ' + str(gold_p1), (int((n / 8) * canvas_scale),
                                                                      (n + 1) * canvas_scale + int(
                                                                          int(canvas_scale / 12) + canvas_scale * (
                                                                                      0 / 4) + int(
                                                                              canvas_scale * (1 / 8)))),
                    int(canvas_scale / 6))
    message_display(screen, u"" + 'Gold Player -1: ' + str(gold_p2), (int((n / 8) * canvas_scale),
                                                                      (n + 1) * canvas_scale + int(
                                                                          int(canvas_scale / 12) + canvas_scale * (
                                                                                      1 / 4) + int(
                                                                              canvas_scale * (1 / 8)))),
                    int(canvas_scale / 6))

    # timing remaining:
    time_remaining = board[0][0][TIME_IDX]
    message_display(screen, u"" + 'Remaining ' + str(time_remaining), (int((n / 8) * canvas_scale),
                                                                       (n + 1) * canvas_scale + int(
                                                                           int(canvas_scale / 12) + canvas_scale * (
                                                                                       2 / 4) + int(
                                                                               canvas_scale * (1 / 8)))),
                    int(canvas_scale / 6))

    # board
    for y in range(n):
        for x in range(n):
            a_player = board[x][y][P_NAME_IDX]

            if a_player == 1 or a_player == -1:

                a_type = board[x][y][A_TYPE_IDX]
                actor_color = d_a_color[a_type]

                actor_location = (int(x * canvas_scale + canvas_scale / 2 + canvas_scale),
                                  int(y * canvas_scale + canvas_scale / 2) + canvas_scale)
                actor_x, actor_y = actor_location

                actor_size = int(canvas_scale / 3)
                actor_short_name = d_type_rev[a_type]

                actor_carry = board[x][y][CARRY_IDX]
                actor_health = board[x][y][HEALTH_IDX]

                pygame.draw.circle(screen, actor_color, actor_location, actor_size)

                player_color = (0, 0, 0)
                if a_player == 1:
                    player_color = (0, 255, 0)
                if a_player == -1:
                    player_color = (255, 0, 0)

                pygame.draw.circle(screen, player_color, actor_location, actor_size, int(actor_size / 10))
                message_display(screen, u"" + actor_short_name, actor_location, int(actor_size * 0.7))

                if a_type != 1:  # if not gold
                    message_display(screen, u"hp: " + str(actor_health),
                                    (actor_x, actor_y + canvas_scale * (2 / 10)), int(actor_size * 0.5))

                if a_type == 2:  # if npc
                    message_display(screen, u"carry: " + str(actor_carry),
                                    (actor_x, actor_y + canvas_scale * (4 / 10)), int(actor_size * 0.5))

    pygame.display.flip()

    clock.tick(fps)

    return not _close_event_graphics()


def _close_event_graphics() -> bool:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # This would be a quit event.
            return True  # So the user can close the program
    return False
