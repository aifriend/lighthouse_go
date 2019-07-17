from typing import List

import numpy as np

from lh.config.configuration import Configuration


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
        self.ENERGY_IDX_INC_OH = 7  # island energy to be played 7 bit - 00(not energy), 1100100(100 energy units)
        self.P_NAME_IDX_INC_OH = 2  # playerName 2 bit - 00(neutral), 01(1) or 10(-1) or 11(both)
        self.A_TYPE_IDX_INC_OH = 2  # either work or lighthouse - 00(work), 01(lighthouse) or 11(both)
        self.PL_ENERGY_W_IDX_INC_OH = 13  # player1 energy
        self.LH_ENERGY_IDX_INC_OH = 13  # lighthouse energy
        self.LH_OWNER_IDX_INC_OH = 2  # lighthouse owner 2 bit - 00(neutral), 01(1) or 10(-1)
        self.LH_KEY_IDX_INC_OH = 2  # player has lighthouse key
        self.LH_CONN_IDX_INC_OH = 5  # lighthouse laser connections with other lhs
        self.LH_TRI_IDX_INC_OH = 1  # polygon cell between three lasers

        # builds indexes for character encoding
        self.ENERGY_IDX_OH = 0
        self.ENERGY_IDX_MAX_OH = self.ENERGY_IDX_OH + self.ENERGY_IDX_INC_OH

        self.P_NAME_IDX_OH = self.ENERGY_IDX_MAX_OH
        self.P_NAME_IDX_MAX_OH = self.P_NAME_IDX_OH + self.P_NAME_IDX_INC_OH

        self.A_TYPE_IDX_OH = self.P_NAME_IDX_MAX_OH
        self.A_TYPE_IDX_MAX_OH = self.A_TYPE_IDX_OH + self.A_TYPE_IDX_INC_OH

        self.PL_ENERGY_W_IDX_OH = self.A_TYPE_IDX_MAX_OH
        self.PL_ENERGY_W_IDX_MAX_OH = self.PL_ENERGY_W_IDX_OH + self.PL_ENERGY_W_IDX_INC_OH

        self.LH_ENERGY_IDX_OH = self.PL_ENERGY_W_IDX_MAX_OH
        self.LH_ENERGY_IDX_MAX_OH = self.LH_ENERGY_IDX_OH + self.LH_ENERGY_IDX_INC_OH

        self.LH_OWNER_IDX_OH = self.LH_ENERGY_IDX_MAX_OH
        self.LH_OWNER_IDX_MAX_OH = self.LH_OWNER_IDX_OH + self.LH_OWNER_IDX_INC_OH

        self.LH_KEY_IDX_OH = self.LH_OWNER_IDX_MAX_OH
        self.LH_KEY_IDX_MAX_OH = self.LH_KEY_IDX_OH + self.LH_KEY_IDX_INC_OH

        self.LH_CONN_IDX_OH = self.LH_KEY_IDX_MAX_OH
        self.LH_CONN_IDX_MAX_OH = self.LH_CONN_IDX_OH + self.LH_CONN_IDX_INC_OH

        self.LH_TRI_IDX_OH = self.LH_CONN_IDX_MAX_OH
        self.LH_TRI_IDX_MAX_OH = self.LH_TRI_IDX_OH + self.LH_TRI_IDX_INC_OH

        self.NUM_ENCODERS = self.LH_TRI_IDX_MAX_OH

    def encode_multiple(self, boards: np.ndarray) -> np.ndarray:
        """
        Encodes and returns multiple boards using onehot encoder

        :param boards: array of boards to encode
        :return: new boards, encoded using onehot encoder
        """
        new_boards = list()
        for board in boards:
            new_boards.append(self.encode(board))
        return np.asarray(new_boards)

    def encode(self, board) -> np.ndarray:
        """
        Encode single board using onehot encoder

        :param board: normal board
        :return: new encoded board
        """
        pieces = np.copy(board)

        row, col, enc = pieces.shape

        # filter energy encoded layer
        self._energy_encoder_filter(pieces)  # window energy view

        # filter lighthouse connections and polygons
        self._lh_encoder_filter(pieces)  # max lh conns/tris only for player 1 (blind play)

        # filter player
        self._player_encoder_filter(pieces, 1)  # only player 1 (blind play)

        b = np.zeros((row, col, self.NUM_ENCODERS))
        for y in range(col):
            for x in range(row):
                # switch lighthouse key from -1 to 2 or 3(both)
                lh_key = 0
                if pieces[x, y, Configuration.LH_KEY_IDX] == 1:
                    lh_key = 1
                elif pieces[x, y, Configuration.LH_KEY_IDX] == -1:
                    lh_key = 2

                # lighthouse owner from -1 to 2
                lh_owner = 0
                if pieces[x, y, Configuration.LH_OWNER_IDX] == 1:
                    lh_owner = 1
                elif pieces[x, y, Configuration.LH_OWNER_IDX] == -1:
                    lh_owner = 2

                b[x, y][self.ENERGY_IDX_OH:self.ENERGY_IDX_MAX_OH] = \
                    self.itb(pieces[x, y, Configuration.ENERGY_IDX], self.ENERGY_IDX_INC_OH)
                b[x, y][self.P_NAME_IDX_OH:self.P_NAME_IDX_MAX_OH] = \
                    self.itb(pieces[x, y, Configuration.P_NAME_IDX], self.P_NAME_IDX_INC_OH)
                b[x, y][self.A_TYPE_IDX_OH:self.A_TYPE_IDX_MAX_OH] = \
                    self.itb(pieces[x, y, Configuration.A_TYPE_IDX], self.A_TYPE_IDX_INC_OH)
                b[x, y][self.PL_ENERGY_W_IDX_OH:self.PL_ENERGY_W_IDX_MAX_OH] = \
                    self.itb(pieces[x, y, Configuration.PL_ENERGY_W1_IDX], self.PL_ENERGY_W_IDX_INC_OH)
                b[x, y][self.LH_ENERGY_IDX_OH:self.LH_ENERGY_IDX_MAX_OH] = \
                    self.itb(pieces[x, y, Configuration.LH_ENERGY_IDX], self.LH_ENERGY_IDX_INC_OH)
                b[x, y][self.LH_OWNER_IDX_OH:self.LH_OWNER_IDX_MAX_OH] = \
                    self.itb(lh_owner, self.LH_OWNER_IDX_INC_OH)
                b[x, y][self.LH_KEY_IDX_OH:self.LH_KEY_IDX_MAX_OH] = \
                    self.itb(lh_key, self.LH_KEY_IDX_INC_OH)
                b[x, y][self.LH_CONN_IDX_OH:self.LH_CONN_IDX_MAX_OH] = \
                    self.itb(pieces[x, y, Configuration.LH_CONN_IDX], self.LH_CONN_IDX_INC_OH)
                b[x, y][self.LH_TRI_IDX_OH:self.LH_TRI_IDX_MAX_OH] = \
                    self.itb(pieces[x, y, Configuration.LH_TRI_IDX], self.LH_TRI_IDX_INC_OH)

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
        if length == 5:
            return [int(i) for i in list('{0:05b}'.format(num))]
        if length == 7:
            return [int(i) for i in list('{0:07b}'.format(num))]
        if length == 8:
            return [int(i) for i in list('{0:08b}'.format(num))]
        if length == 9:
            return [int(i) for i in list('{0:09b}'.format(num))]
        if length == 10:
            return [int(i) for i in list('{0:010b}'.format(num))]
        if length == 13:
            return [int(i) for i in list('{0:013b}'.format(num))]
        raise TypeError("Length not supported:", length)

    @staticmethod
    def _energy_encoder_filter(pieces) -> None:
        from lh.logic.board.island import Island

        # narrow island energy window
        row, col, enc = pieces.shape
        for y in range(col):
            for x in range(row):
                if pieces[x][y][Configuration.P_NAME_IDX] == 1:  # only view for player 1
                    Island.encode_view(pieces, (y, x))

    @staticmethod
    def _lh_encoder_filter(pieces) -> None:
        from lh.logic.board.board import Connection, Polygon
        Connection.encode_conns(pieces, 1)
        Polygon.encode_tris(pieces, 1)

    @staticmethod
    def _player_encoder_filter(pieces, player_id):
        row, col, enc = pieces.shape
        for y in range(col):
            for x in range(row):
                # remove opponent
                if pieces[x][y][Configuration.P_NAME_IDX] == -player_id:
                    pieces[x][y][:] = 0
                # encode worker type
                if pieces[x][y][Configuration.P_NAME_IDX] == player_id:
                    pieces[x][y][Configuration.A_TYPE_IDX] = Configuration.d_a_type["Worker"]
