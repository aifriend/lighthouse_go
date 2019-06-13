from typing import List

import numpy as np


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
        self.P_NAME_IDX_INC_OH = 2  # playerName 2 bit - 00(neutral), 01(1) or 10(-1) or 11(both)
        self.ENERGY_W1_IDX_INC_OH = 12  # work1 energy
        self.ENERGY_W2_IDX_INC_OH = 12  # work2 energy
        self.LH_ENERGY_IDX_INC_OH = 12  # lighthouse energy
        self.LH_OWNER_IDX_INC_OH = 2  # carrying
        self.LH_KEY_IDX_INC_OH = 2  # player has lighthouse key
        self.LH_CONN_IDX_INC_OH = 5  # lighthouse laser connections witho other lhs
        self.LH_TRI_IDX_INC_OH = 3  # poligon areas between three lasers
        self.REMAIN_IDX_INC_OH = 11  # 2^11 2048(za total annihilation)

        # builds indexes for character encoding
        self.ISLAND_IDX_OH = 0
        self.ISLAND_IDX_MAX_OH = self.ISLAND_IDX_INC_OH

        self.P_NAME_IDX_OH = self.ISLAND_IDX_MAX_OH
        self.P_NAME_IDX_MAX_OH = self.P_NAME_IDX_OH + self.P_NAME_IDX_INC_OH

        self.ENERGY_W1_IDX_OH = self.P_NAME_IDX_MAX_OH
        self.ENERGY_W1_IDX_MAX_OH = self.ENERGY_W1_IDX_OH + self.ENERGY_W1_IDX_INC_OH

        self.ENERGY_W2_IDX_OH = self.ENERGY_W1_IDX_MAX_OH
        self.ENERGY_W2_IDX_MAX_OH = self.ENERGY_W2_IDX_OH + self.ENERGY_W2_IDX_INC_OH

        self.LH_ENERGY_IDX_OH = self.ENERGY_W2_IDX_MAX_OH
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
            return [int(i) for i in '{0:01b}'.format(num)]
        if length == 2:
            return [int(i) for i in '{0:02b}'.format(num)]
        if length == 3:
            return [int(i) for i in '{0:03b}'.format(num)]
        if length == 4:
            return [int(i) for i in '{0:04b}'.format(num)]
        if length == 5:
            return [int(i) for i in '{0:05b}'.format(num)]
        if length == 8:
            return [int(i) for i in '{0:08b}'.format(num)]
        if length == 11:
            return [int(i) for i in '{0:011b}'.format(num)]
        raise TypeError("Length not supported:", length)

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
        """
        lighthouses = []
        for lh in self.board.lighthouses.values():
            connections = [next(l for l in c if l is not lh.pos)
                           for c in self.board.conns if lh.pos in c]
            lighthouses.append({
                "position": lh.pos,
                "owner": lh.owner,
                "energy": lh.energy,
                "connections": connections,
                "have_key": lh.pos in player.keys,
            })
        state = {
            "position": player.pos,
            "score": player.score,
            "energy": player.energy,
            "view": self.board.island.get_view(player.pos),
            "lighthouses": lighthouses,
        }
        """
        from lh.config.configuration import ISLAND_IDX, P_NAME_IDX, ENERGY_W1_IDX, ENERGY_W2_IDX, \
            LH_ENERGY_IDX, LH_OWNER_IDX, LH_KEY_IDX, LH_CONN_IDX, LH_TRI_IDX, TIME_IDX

        n = board.shape[0]

        b = np.zeros((n, n, self.NUM_ENCODERS))
        for y in range(n):
            for x in range(n):
                # switch player from -1 to 2
                player = 0
                if board[x, y, P_NAME_IDX] == 1:
                    player = 1
                elif board[x, y, P_NAME_IDX] == -1:
                    player = 2

                # switch lighthouse key from -1 to 2 or 3
                lh_key = 0
                if board[x, y, LH_KEY_IDX] == 1:
                    lh_key = 1
                elif board[x, y, LH_KEY_IDX] == -1:
                    lh_key = 2
                elif board[x, y, LH_KEY_IDX] == 3:
                    lh_key = 3

                b[x, y][self.ISLAND_IDX_OH:self.ISLAND_IDX_MAX_OH] = \
                    self.itb(board[x, y, ISLAND_IDX], self.ISLAND_IDX_INC_OH)
                b[x, y][self.P_NAME_IDX_OH:self.P_NAME_IDX_MAX_OH] = \
                    self.itb(player, self.P_NAME_IDX_INC_OH)
                b[x, y][self.ENERGY_W1_IDX_OH:self.ENERGY_W1_IDX_MAX_OH] = \
                    self.itb(board[x, y, ENERGY_W1_IDX], self.ENERGY_W1_IDX_INC_OH)
                b[x, y][self.ENERGY_W2_IDX_OH:self.ENERGY_W2_IDX_MAX_OH] = \
                    self.itb(board[x, y, ENERGY_W2_IDX], self.ENERGY_W2_IDX_INC_OH)
                b[x, y][self.LH_ENERGY_IDX_OH:self.LH_ENERGY_IDX_MAX_OH] = \
                    self.itb(board[x, y, LH_ENERGY_IDX], self.LH_ENERGY_IDX_INC_OH)
                b[x, y][self.LH_OWNER_IDX_OH:self.LH_OWNER_IDX_MAX_OH] = \
                    self.itb(board[x, y, LH_OWNER_IDX], self.LH_OWNER_IDX_INC_OH)
                b[x, y][self.LH_KEY_IDX_OH:self.LH_KEY_IDX_MAX_OH] = \
                    self.itb(lh_key, self.LH_KEY_IDX_INC_OH)
                b[x, y][self.LH_CONN_IDX_OH:self.LH_CONN_IDX_MAX_OH] = \
                    self.itb(board[x, y, LH_CONN_IDX], self.LH_CONN_IDX_INC_OH)
                b[x, y][self.LH_TRI_IDX_OH:self.LH_TRI_IDX_MAX_OH] = \
                    self.itb(board[x, y, LH_TRI_IDX], self.LH_TRI_IDX_INC_OH)
                b[x, y][self.REMAIN_IDX_OH:self.REMAIN_IDX_MAX_OH] = \
                    self.itb(board[x, y, TIME_IDX], self.REMAIN_IDX_INC_OH)
        return b
