from lh.config.configuration import LH_ENERGY_IDX, LH_OWNER_IDX, A_TYPE_IDX
from lh.config.gameconfig import MoveError


class Lighthouse(object):

    def __init__(self, game, pos):
        self._id = pos[1] + pos[0]
        self._game = game
        self._pos = pos
        self._owner = 0
        self._energy = 0

    @property
    def id(self):
        return self._id

    @property
    def pos(self):
        return self._pos

    def lh_to_board(self, pieces):
        pieces[self._pos[1], self._pos[0], A_TYPE_IDX] = self._id

    def energy_to_board(self, pieces, energy=-1, add=-1):
        if energy >= 0:
            self._energy = energy
        if add >= 0:
            self._energy += add
        pieces[self._pos[1], self._pos[0], LH_ENERGY_IDX] = self._energy

    def owner_to_board(self, pieces, owner=None):
        if owner is not None:
            self._owner = owner
        pieces[self._pos[1], self._pos[0], LH_OWNER_IDX] = self._owner

    @staticmethod
    def from_array(game, pieces):
        lh_list = dict()
        dim_x, dim_y, enc = pieces.shape
        for x in range(dim_x):
            for y in range(dim_y):
                lh_pose = (y, x)
                if pieces[x][y][A_TYPE_IDX] != 0:
                    lighthouse = Lighthouse(game, lh_pose)
                    lighthouse.board_to_lh(pieces)
                    lighthouse.board_to_energy(pieces)
                    lighthouse.board_to_owner(pieces)
                    lh_list[lh_pose] = lighthouse

        return lh_list

    def board_to_lh(self, pieces):
        self._id = pieces[self._pos[1], self._pos[0], A_TYPE_IDX]

    def board_to_energy(self, pieces):
        self._energy = pieces[self._pos[1], self._pos[0], LH_ENERGY_IDX]

    def board_to_owner(self, pieces):
        self._owner = pieces[self._pos[1], self._pos[0], LH_OWNER_IDX]

    def attack(self, player, strength):
        if not isinstance(strength, int):
            raise MoveError("Strength must be an int")
        if strength < 0:
            raise MoveError("Strength must be positive")
        if strength > player.energy:
            strength = player.energy
        player.energy -= strength
        if self._owner is not None and self._owner != player.turn:
            d = min(self._energy, strength)
            self.decay(d)
            strength -= d
        if strength:
            self._owner = player.turn
            self._energy = strength

    def decay(self, by):
        self._energy -= by
        if self._energy <= 0:
            self._energy = 0
            self._owner = 0
            self._game.close_conn(self._pos)

    @staticmethod
    def owned_by(pieces, player=1):
        """
        Lighthouses owned by given player

        :param pieces:
        :param player:
        :return:
        """
        lh_owned = []
        row, col = pieces.shape
        for y in range(col):
            for x in range(row):
                if pieces[x][y][LH_OWNER_IDX] == player:
                    lh_owned.append((y, x))

        return lh_owned
