from typing import Tuple

import numpy as np

from lh.LHLogic import LHLogic
from lh.config.config import CONFIG
from lh.config.configuration import NUM_ENCODERS, NUM_ACTS, P_NAME_IDX, A_TYPE_IDX, TIME_IDX
from lib.Game import Game


class LHGame(Game):
    def __init__(self) -> None:
        super().__init__()

        self.initial_board_config = CONFIG.initial_board_config

        self.logic = LHLogic()

    def getInitBoard(self) -> np.ndarray:
        """
        :return: Returns new board from initial_board_config. That config can be dynamically changed as game progresses.
        """
        remaining_time = None  # when setting initial board, remaining time might be different
        for e in self.initial_board_config:
            self.logic.pieces[e.x, e.y] = [e.player, e.a_type, e.health, e.carry, e.gold, e.timeout]
            remaining_time = e.timeout

        # remaining time is stored in all squares
        self.logic.pieces[:, :, TIME_IDX] = remaining_time

        return np.array(self.logic.pieces)

    def getBoardSize(self) -> Tuple[int, int, int]:
        # (a,b) tuple
        return self.n, self.n, NUM_ENCODERS

    def getNextState(self, board: np.ndarray, player: int, action: int) -> Tuple[np.ndarray, int]:
        """
        Gets next state for board. It also updates tick for board as game tick iterations are transfered
        within board as the last encoded parameter

        :param board: current board
        :param player: player executing action
        :param action: action to apply to new board
        :return: new board with applied action
        """
        self.logic.pieces = np.copy(board)

        y, x, action_index = np.unravel_index(action, [NUM_ACTS])
        move = (x, y, action_index)

        # first execute move, then run time function to destroy any actors if needed
        self.logic.execute_move(move, player)

        # get config for timeout
        # update timer on every tile:
        self.logic.pieces[:, :, TIME_IDX] -= 1

        return self.logic.pieces, -player

    def getActionSize(self) -> int:
        return NUM_ACTS

    def getValidMoves(self, board: np.ndarray, player: int) -> np.ndarray:
        valids = [0] * NUM_ACTS
        self.logic.pieces = np.copy(board)

        if player == 1:
            config = CONFIG.player1_config
        else:
            config = CONFIG.player2_config

        for y in range(self.n):
            for x in range(self.n):
                if self.logic[x][y][P_NAME_IDX] == player and \
                        self.logic[x][y][A_TYPE_IDX] == 1:  # for this player and only worker type
                    valids = self.logic.get_moves_for_square(x, y, config=config)

        return np.array(valids)

    def getGameEnded(self, board: np.ndarray, player) -> float:
        """
        Ok, this function is where it gets complicated...
        See, its  hard to decide when to finish real time strategy game, as players might not have enough time to execute wanted
        actions, but in the other hand, if players are left to play for too long, games become very long, or even
        'infinitely' long.
        Using timeout. Timeout just cuts game and evaluates winner using one of 3 elo functions. We've found this one
        to be more useful, as it can be applied in 3d real time strategy games easier and more sensibly.

        :param board: current game state
        :param player: current player
        :return: real number on interval [-1,1] - return 0 if not ended, 1 if player 1 won, -1 if player 1 lost, 0.001 if tie
        """
        n = board.shape[0]

        # detect timeout
        if board[0, 0, TIME_IDX] < 1:
            score_player1 = self.getScore(board, player)
            score_player2 = self.getScore(board, -player)
            if score_player1 == score_player2:
                return 0.001
            better_player = 1 if score_player1 > score_player2 else -1
            return better_player

        # detect win condition
        sum_p1 = 0
        sum_p2 = 0
        for y in range(n):
            for x in range(n):
                if board[x][y][P_NAME_IDX] == 1:
                    sum_p1 += 1
                if board[x][y][P_NAME_IDX] == -1:
                    sum_p2 += 1

        if sum_p1 < 2:  # SUM IS 1 WHEN PLAYER ONLY HAS MINERALS LEFT
            return -1
        if sum_p2 < 2:  # SUM IS 1 WHEN PLAYER ONLY HAS MINERALS LEFT
            return +1

        # detect no valid actions -
        # possible tie by overpopulating on non-attacking units and buildings -
        # all fields are full or one player is surrounded:
        if sum(self.getValidMoves(board, 1)) == 0:
            return -1

        if sum(self.getValidMoves(board, -1)) == 0:
            return 1

        # continue game
        return 0

    def getCanonicalForm(self, board: np.ndarray, player: int) -> np.ndarray:
        b = np.copy(board)
        b[:, :, P_NAME_IDX] = b[:, :, P_NAME_IDX] * player
        return b

    def getSymmetries(self, board: np.ndarray, pi):
        # mirror, rotational
        assert (len(pi) == self.n * self.n * NUM_ACTS)
        pi_board = np.reshape(pi[:-1], (self.n, self.n, NUM_ACTS))
        return_list = []
        for i in range(1, 5):
            for j in [True, False]:
                newB = np.rot90(board, i)
                newPi = np.rot90(pi_board, i)
                if j:
                    newB = np.fliplr(newB)
                    newPi = np.fliplr(newPi)
                return_list += [(newB, list(newPi.ravel()))]

        return return_list

    def stringRepresentation(self, board: np.ndarray) -> bytes:
        return board.tostring()

    def getScore(self, board: np.array, player: int) -> int:
        """
        Uses one of 3 elo functions that determine better player

        :param board: game state
        :param player: current player
        :return: elo for current player on this board
        """
        self.logic.pieces = np.copy(board)

        # can use different score functions for each player
        if player == 1:
            score_function = CONFIG.player1_config.score_function
        else:
            score_function = CONFIG.player2_config.score_function

        if score_function == 1:
            return self.logic.get_health_score(player)
        elif score_function == 2:
            return self.logic.get_money_score(player)
        else:
            return self.logic.get_combined_score(player)
