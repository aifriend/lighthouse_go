from lib.View import View
from rts.config.config import CONFIG
from rts.config.configuration import P_NAME_IDX, A_TYPE_IDX, FPS
from rts.visualization.rts_pygame import init_visuals, update_graphics


class RTSView(View):
    def __init__(self, game):
        self.game = game
        self.screen = None
        self.clock = None
        self.arena = None

    def initView(self, board):
        if not CONFIG.visibility:
            return

        n = board.shape[0]
        if CONFIG.visibility > 3:
            self.arena, self.screen, self.clock = init_visuals(n, n, CONFIG.visibility)
        else:
            self._show(n, self.game.board)

    def display(self, board):
        """
        Console presentation of board

        :param board: game state
        :return: /
        """
        if not CONFIG.visibility:
            return

        if CONFIG.visibility > 3 and not (self.arena is None) and not (self.screen is None) and not (
                self.clock is None):
            is_view_updated = update_graphics(board, self.arena, self.screen, self.clock, FPS)
            if not is_view_updated:
                self._show(board.shape[0], board)
                exit(1)

    @staticmethod
    def _show(n, board):
        for y in range(n):
            print('-' * (n * 8 + 1))
            for x in range(n):
                a_player = board[x][y][P_NAME_IDX]
                if a_player == 1:
                    a_player = '+1'
                if a_player == -1:
                    a_player = '-1'
                if a_player == 0:
                    a_player = ' 0'
                print("|" + a_player + " " + str(board[x][y][A_TYPE_IDX]) + " ", end="")
            print("|")
        print('-' * (n * 8 + 1))
