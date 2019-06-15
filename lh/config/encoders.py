from typing import List

import numpy as np

from lh.config.configuration import ISLAND_IDX, ENERGY_IDX, P_NAME_IDX, A_TYPE_IDX, PL_ENERGY_W1_IDX, PL_ENERGY_W2_IDX, \
    LH_ENERGY_IDX, LH_OWNER_IDX, LH_KEY_IDX, LH_CONN_IDX, LH_TRI_IDX, TIME_IDX, PL_SCORE_W1_IDX, PL_SCORE_W2_IDX


class Encoder:
    """
    Defines one-hot encoder

    One-hot encoder uses binary representation of integer numbers, with exception of player name, which is processed separately
    """

    def __init__(self):
        self.NUM_ENCODERS = None

    def encode(self, board) -> np.ndarray:
        pass

    def encode_multiple(self, boards: np.ndarray) -> np.ndarray:
        pass

    @property
    def num_encoders(self):
        return self.NUM_ENCODERS


class OneHotEncoder(Encoder):
    def __init__(self) -> None:
        super().__init__()
        self._build_indexes()

    def _build_indexes(self):
        """
        Defines encoding indexes - you may change them as you would like, but do not reduce them below their actual encoders.
        """
        self.ISLAND_IDX_INC_OH = 2  # island to be played 2 bit - 00(not playable), 01(island playable) or 10(lh)
        self.ENERGY_IDX_INC_OH = 7  # island energy to be played 7 bit - 00(not energy), 1100100(100 energy units)
        self.P_NAME_IDX_INC_OH = 2  # playerName 2 bit - 00(neutral), 01(1) or 10(-1) or 11(both)
        self.A_TYPE_IDX_INC_OH = 2  # either work or lighthouse - 00(work), 01(lighthouse) or 11(both)
        self.PL_SCORE_W1_IDX_INC_OH = 20  # player1 score 20 bit - inf?
        self.PL_SCORE_W2_IDX_INC_OH = 20  # player2 score 20 bit - inf?
        self.PL_ENERGY_W1_IDX_INC_OH = 12  # player1 energy 12 bit
        self.PL_ENERGY_W2_IDX_INC_OH = 12  # player2 energy 12 bit
        self.LH_ENERGY_IDX_INC_OH = 12  # lighthouse energy
        self.LH_OWNER_IDX_INC_OH = 2  # lighthouse owner 2 bit - 00(neutral), 01(1) or 10(-1)
        self.LH_KEY_IDX_INC_OH = 2  # player has lighthouse key
        self.LH_CONN_IDX_INC_OH = 5  # lighthouse laser connections with other lhs
        self.LH_TRI_IDX_INC_OH = 3  # polygon areas between three lasers
        self.REMAIN_IDX_INC_OH = 11  # 2^11 2048(za total annihilation)

        # builds indexes for character encoding
        self.ISLAND_IDX_OH = 0
        self.ISLAND_IDX_MAX_OH = self.ISLAND_IDX_INC_OH

        self.ENERGY_IDX_OH = self.ISLAND_IDX_MAX_OH
        self.ENERGY_IDX_MAX_OH = self.ENERGY_IDX_OH + self.ENERGY_IDX_INC_OH

        self.P_NAME_IDX_OH = self.ENERGY_IDX_MAX_OH
        self.P_NAME_IDX_MAX_OH = self.P_NAME_IDX_OH + self.P_NAME_IDX_INC_OH

        self.A_TYPE_IDX_OH = self.P_NAME_IDX_MAX_OH
        self.A_TYPE_IDX_MAX_OH = self.A_TYPE_IDX_OH + self.A_TYPE_IDX_INC_OH

        self.PL_SCORE_W1_IDX_OH = self.A_TYPE_IDX_MAX_OH
        self.PL_SCORE_W1_IDX_MAX_OH = self.PL_SCORE_W1_IDX_OH + self.PL_SCORE_W1_IDX_INC_OH

        self.PL_SCORE_W2_IDX_OH = self.PL_SCORE_W1_IDX_MAX_OH
        self.PL_SCORE_W2_IDX_MAX_OH = self.PL_SCORE_W2_IDX_OH + self.PL_SCORE_W2_IDX_INC_OH

        self.PL_ENERGY_W1_IDX_OH = self.PL_SCORE_W2_IDX_MAX_OH
        self.PL_ENERGY_W1_IDX_MAX_OH = self.PL_ENERGY_W1_IDX_OH + self.PL_ENERGY_W1_IDX_INC_OH

        self.PL_ENERGY_W2_IDX_OH = self.PL_ENERGY_W1_IDX_MAX_OH
        self.PL_ENERGY_W2_IDX_MAX_OH = self.PL_ENERGY_W2_IDX_OH + self.PL_ENERGY_W2_IDX_INC_OH

        self.LH_ENERGY_IDX_OH = self.PL_ENERGY_W2_IDX_MAX_OH
        self.LH_ENERGY_IDX_MAX_OH = self.LH_ENERGY_IDX_OH + self.LH_ENERGY_IDX_INC_OH

        self.LH_OWNER_IDX_OH = self.LH_ENERGY_IDX_MAX_OH
        self.LH_OWNER_IDX_MAX_OH = self.LH_OWNER_IDX_OH + self.LH_OWNER_IDX_INC_OH

        self.LH_KEY_IDX_OH = self.LH_OWNER_IDX_MAX_OH
        self.LH_KEY_IDX_MAX_OH = self.LH_KEY_IDX_OH + self.LH_KEY_IDX_INC_OH

        self.LH_CONN_IDX_OH = self.LH_KEY_IDX_MAX_OH
        self.LH_CONN_IDX_MAX_OH = self.LH_CONN_IDX_OH + self.LH_CONN_IDX_INC_OH

        self.LH_TRI_IDX_OH = self.LH_CONN_IDX_MAX_OH
        self.LH_TRI_IDX_MAX_OH = self.LH_TRI_IDX_OH + self.LH_TRI_IDX_INC_OH

        self.REMAIN_IDX_OH = self.LH_TRI_IDX_MAX_OH
        self.REMAIN_IDX_MAX_OH = self.REMAIN_IDX_OH + self.REMAIN_IDX_INC_OH

        self.NUM_ENCODERS = self.REMAIN_IDX_MAX_OH

    def encode_multiple(self, boards: np.ndarray) -> np.ndarray:
        """
        Encodes and returns multiple boards using onehot encoder

        :param boards: array of boards to encode
        :return: new boards, encoded using onehot encoder
        """
        new_boards = []
        for board in boards:
            new_boards.append(self.encode(board))
        return np.asarray(new_boards)

    def encode(self, board) -> np.ndarray:
        """
        Encode single board using onehot encoder

        :param board: normal board
        :return: new encoded board
        """
        row, col = board.shape

        # filter energy encoded layer
        self._energy_filter(board)  # window energy view

        # filter lighthouse connections and polygons
        self._lh_filter(board)  # max lh conns/tris

        b = np.zeros((row, col, self.NUM_ENCODERS))
        for y in range(col):
            for x in range(row):
                # switch player from -1 to 2
                player = 0
                if board[x, y, P_NAME_IDX] == 1:
                    player = 1
                elif board[x, y, P_NAME_IDX] == -1:
                    # remove opposite player (blind play)
                    board[x, y, self.ISLAND_IDX_INC_OH:-self.REMAIN_IDX_INC_OH] = 0
                    continue

                # switch lighthouse key from -1 to 2 or 3(both)
                lh_key = 0
                if board[x, y, LH_KEY_IDX] == 1:
                    lh_key = 1
                elif board[x, y, LH_KEY_IDX] == -1:
                    lh_key = 2
                elif board[x, y, LH_KEY_IDX] == 3:
                    lh_key = 3

                # lighthouse owner from -1 to 2
                lh_owner = 0
                if board[x, y, LH_OWNER_IDX] == 1:
                    lh_owner = 1
                elif board[x, y, LH_OWNER_IDX] == -1:
                    lh_owner = 2

                b[x, y][self.ISLAND_IDX_OH:self.ISLAND_IDX_MAX_OH] = \
                    self.itb(board[x, y, ISLAND_IDX], self.ISLAND_IDX_INC_OH)
                b[x, y][self.ENERGY_IDX_OH:self.ENERGY_IDX_MAX_OH] = \
                    self.itb(board[x, y, ENERGY_IDX], self.ENERGY_IDX_INC_OH)
                b[x, y][self.P_NAME_IDX_OH:self.P_NAME_IDX_MAX_OH] = \
                    self.itb(player, self.P_NAME_IDX_INC_OH)
                b[x, y][self.A_TYPE_IDX_OH:self.A_TYPE_IDX_MAX_OH] = \
                    self.itb(board[x, y, A_TYPE_IDX], self.A_TYPE_IDX_INC_OH)
                b[x, y][self.PL_SCORE_W1_IDX_OH:self.PL_SCORE_W1_IDX_MAX_OH] = \
                    self.itb(board[x, y, PL_SCORE_W1_IDX], self.PL_SCORE_W1_IDX_INC_OH)
                b[x, y][self.PL_SCORE_W2_IDX_OH:self.PL_SCORE_W2_IDX_MAX_OH] = \
                    self.itb(board[x, y, PL_SCORE_W2_IDX], self.PL_SCORE_W2_IDX_INC_OH)
                b[x, y][self.PL_ENERGY_W1_IDX_OH:self.PL_ENERGY_W1_IDX_MAX_OH] = \
                    self.itb(board[x, y, PL_ENERGY_W1_IDX], self.PL_ENERGY_W1_IDX_INC_OH)
                b[x, y][self.PL_ENERGY_W2_IDX_OH:self.PL_ENERGY_W2_IDX_MAX_OH] = \
                    self.itb(board[x, y, PL_ENERGY_W2_IDX], self.PL_ENERGY_W2_IDX_INC_OH)
                b[x, y][self.LH_ENERGY_IDX_OH:self.LH_ENERGY_IDX_MAX_OH] = \
                    self.itb(board[x, y, LH_ENERGY_IDX], self.LH_ENERGY_IDX_INC_OH)
                b[x, y][self.LH_OWNER_IDX_OH:self.LH_OWNER_IDX_MAX_OH] = \
                    self.itb(lh_owner, self.LH_OWNER_IDX_INC_OH)
                b[x, y][self.LH_KEY_IDX_OH:self.LH_KEY_IDX_MAX_OH] = \
                    self.itb(lh_key, self.LH_KEY_IDX_INC_OH)
                b[x, y][self.LH_CONN_IDX_OH:self.LH_CONN_IDX_MAX_OH] = \
                    self.itb(board[x, y, LH_CONN_IDX], self.LH_CONN_IDX_INC_OH)
                b[x, y][self.LH_TRI_IDX_OH:self.LH_TRI_IDX_MAX_OH] = \
                    self.itb(board[x, y, LH_TRI_IDX], self.LH_TRI_IDX_INC_OH)
                b[x, y][self.REMAIN_IDX_OH:self.REMAIN_IDX_MAX_OH] = \
                    self.itb(board[x, y, TIME_IDX], self.REMAIN_IDX_INC_OH)

        return b

    @staticmethod
    def itb(num: int, length: int) -> List[int]:
        """
        Converts integer to bit array
        Someone fix this please :D - it's horrible
        :param num: number to convert to bits
        :param length: length of bits to convert to
        :return: bit array
        """
        num = int(num)
        if length == 1:
            return [int(i) for i in list('{0:01b}'.format(num))]
        if length == 2:
            return [int(i) for i in list('{0:02b}'.format(num))]
        if length == 3:
            return [int(i) for i in list('{0:03b}'.format(num))]
        if length == 4:
            return [int(i) for i in list('{0:04b}'.format(num))]
        if length == 5:
            return [int(i) for i in list('{0:05b}'.format(num))]
        if length == 7:
            return [int(i) for i in list('{0:07b}'.format(num))]
        if length == 8:
            return [int(i) for i in list('{0:08b}'.format(num))]
        if length == 11:
            return [int(i) for i in list('{0:011b}'.format(num))]
        if length == 12:
            return [int(i) for i in list('{0:012b}'.format(num))]
        if length == 20:
            return [int(i) for i in list('{0:020b}'.format(num))]
        raise TypeError("Length not supported:", length)

    @staticmethod
    def _energy_filter(pieces) -> None:
        from lh.logic.board.island import Island

        # narrow island energy window
        row, col = pieces.shape
        for y in range(col):
            for x in range(row):
                if pieces[x][y][P_NAME_IDX] != 0:
                    Island.encode_view(pieces, (y, x))

    @staticmethod
    def _lh_filter(pieces) -> None:
        from lh.LHLogic import Connection, Triangle

        row, col = pieces.shape
        for y in range(col):
            for x in range(row):
                Connection.encode_conns(pieces)
                Triangle.encode_tris(pieces)
