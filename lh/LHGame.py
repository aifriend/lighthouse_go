from typing import Tuple

import numpy as np

from lh.LHLogic import LHLogic
from lh.config.config import CONFIG
from lh.config.configuration import NUM_ENCODERS, NUM_ACTS, P_NAME_IDX, TIME_IDX
from lib.Game import Game


class LHGame(Game):
    def __init__(self) -> None:
        super().__init__()

        self.logic = LHLogic(CONFIG.board_file_path)

    def getInitBoard(self) -> np.ndarray:
        """
        :return: Returns new board from initial_board_config. That config can be dynamically changed as game progresses.
        """
        self.logic.initialize()

        pieces = np.zeros((self.logic.board.size["height"], self.logic.board.size["width"], NUM_ENCODERS))

        # remaining time is stored in all squares
        pieces[:, :, TIME_IDX] = CONFIG.timeout

        # get pieces from actual board state
        pieces = self.logic.board.to_array(pieces)

        return pieces

    def getBoardSize(self) -> Tuple[int, int, int]:
        """
        Get board size

        :return:
        """
        return self.logic.board.size["width"], self.logic.board.size["height"], NUM_ENCODERS

    def getNextState(self, board: np.ndarray, player: int, action: int) -> Tuple[np.ndarray, int]:
        """
        Gets next state for board. It also updates tick for board as game tick iterations are transfered
        within board as the last encoded parameter

        :param board: current board
        :param player: player executing action
        :param action: action to apply to new board
        :return: new board with applied action
        """
        # update board status
        self.logic.board.from_array(board)

        # first execute move, then run time function to destroy any actors if needed
        self.logic.get_next_state(action, player)

        # get pieces from actual board state
        pieces = self.logic.board.to_array(board)

        # get config for timeout
        # update timer on every tile:
        pieces[:, :, TIME_IDX] -= 1

        return pieces, -player

    def getActionSize(self) -> int:
        return NUM_ACTS

    def getValidMoves(self, board: np.ndarray, player: int) -> np.ndarray:
        """
        Returns all valid actions for specific tile

        :param board:
        :param player:
        :return:
        """
        # update board status
        self.logic.board.from_array(board)

        # apply config and prepare board for player turn
        if player == 1:
            config = CONFIG.player1_config
            self.logic.board.pre_round()
        else:
            config = CONFIG.player2_config
            self.logic.board.post_round()

        # select valid moves
        valid = self.logic.get_valid_moves(player, config=config)

        return np.array(valid)

    def getGameEnded(self, board: np.ndarray, player) -> float:
        """
        It is hard to decide when to finish real time strategy game, as players might not have enough time
        to execute wanted actions, but in the other hand, if players are left to play for too long, games become
        very long, or even 'infinitely' long.
        Using timeout. Timeout just cuts game and evaluates winner using one of 3 elo functions. We've found this one
        to be more useful, as it can be applied in 3d real time strategy games easier and more sensibly.

        :param board: current game state
        :param player: current player
        :return: real number on interval [-1,1] - return 0 if not ended, 1 if player 1 won, -1 if player 1 lost, 0.001 if tie
        """
        # update board status
        self.logic.board.from_array(board)

        # detect timeout
        if board[0, 0, TIME_IDX] < 1:
            score_player1 = self.getScore(board, player)
            score_player2 = self.getScore(board, -player)
            if score_player1 == score_player2:
                return 0.001
            better_player = 1 if score_player1 > score_player2 else -1
            return better_player

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
        """

        :param board:
        :param player:
        :return:
        """
        b = np.copy(board)
        b[:, :, P_NAME_IDX] = b[:, :, P_NAME_IDX] * player
        return b

    def getSymmetries(self, board: np.ndarray, pi):
        """

        :param board:
        :param pi:
        :return:
        """
        # mirror, rotational
        assert (len(pi) == self.logic.board.size["width"] * self.logic.board.size["height"] * NUM_ACTS)
        pi_board = np.reshape(pi[:-1], (self.logic.board.size["width"], self.logic.board.size["height"], NUM_ACTS))
        return_list = []
        for i in range(1, 5):
            for j in [True, False]:
                new_b = np.rot90(board, i)
                new_pi = np.rot90(pi_board, i)
                if j:
                    new_b = np.fliplr(new_b)
                    new_pi = np.fliplr(new_pi)
                return_list += [(new_b, list(new_pi.ravel()))]

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
        # update board status
        self.logic.board.from_array(board)

        return self.logic.board.get_score(player)
