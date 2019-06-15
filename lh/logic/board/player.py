from lh.config.configuration import P_NAME_IDX, d_a_type, A_TYPE_IDX, PL_ENERGY_W2_IDX, PL_ENERGY_W1_IDX, \
    PL_SCORE_W1_IDX, PL_SCORE_W2_IDX, LH_KEY_IDX, ISLAND_IDX
from lh.config.gameconfig import MoveError


class Player(object):
    def __init__(self, pose, turn=0):
        self.turn = 1 if turn % 2 == 0 else -1
        self._pos = pose
        self._score = 0
        self._energy = 0
        self._keys = set()

    def has_key(self, lh_pose):
        return lh_pose in self._keys

    @property
    def score(self):
        return self._score

    def turn_to_board(self, pieces, turn=None):
        if turn is not None:
            self.turn = turn
        pieces[self._pos[1], self._pos[0], P_NAME_IDX] = self.turn

    def score_to_board(self, pieces, pose, score=-1):
        if score >= 0:
            self._score = score
        if self.turn == 1:
            pieces[pose[1], pose[0], PL_SCORE_W1_IDX] = self._score
        else:
            pieces[pose[1], pose[0], PL_SCORE_W2_IDX] = self._score

    def energy_to_board(self, pieces, pose, energy=-1):
        if energy >= 0:
            self._energy = energy
        if self.turn == 1:
            pieces[pose[1], pose[0], PL_ENERGY_W1_IDX] = self._energy
        else:
            pieces[pose[1], pose[0], PL_ENERGY_W2_IDX] = self._energy

    def keys_to_board(self, pieces):
        for key in self._keys:
            actor_type = pieces[key[1], key[0], A_TYPE_IDX]
            if actor_type == d_a_type["Lighthouse"]:
                lh_key_owner = pieces[key[1], key[0], LH_KEY_IDX]
                if lh_key_owner == 0:
                    pieces[key[1], key[0], LH_KEY_IDX] = self.turn
                else:
                    if lh_key_owner == 1 and self.turn == -1:
                        pieces[key[1], key[0], LH_KEY_IDX] = 3
                    elif lh_key_owner == -1 and self.turn == 1:
                        pieces[key[1], key[0], LH_KEY_IDX] = 3

    @staticmethod
    def from_array(pieces):
        player_list = list()
        dim_x, dim_y, enc = pieces.shape
        for x in range(dim_x):
            for y in range(dim_y):
                p_pose = (y, x)
                p_turn = pieces[x][y][P_NAME_IDX]
                if pieces[x][y][P_NAME_IDX] != 0:
                    player = Player(p_pose, p_turn)
                    player.board_to_energy(pieces)
                    player.board_to_score(pieces)
                    player.board_to_keys(pieces)
                    player_list.append(player)

        return player_list

    def board_to_turn(self, pieces):
        self.turn = pieces[self._pos[1], self._pos[0], P_NAME_IDX]

    def board_to_score(self, pieces):
        if self.turn == 1:
            self._score = pieces[self._pos[1], self._pos[0], PL_SCORE_W1_IDX]
        else:
            self._score = pieces[self._pos[1], self._pos[0], PL_SCORE_W2_IDX]

    def board_to_energy(self, pieces):
        if self.turn == 1:
            self._energy = pieces[self._pos[1], self._pos[0], PL_ENERGY_W1_IDX]
        else:
            self._energy = pieces[self._pos[1], self._pos[0], PL_ENERGY_W2_IDX]

    def board_to_keys(self, pieces):
        lighthouse_list = [lh for lh in pieces[:, :, A_TYPE_IDX] if lh == d_a_type["Lighthouse"]]
        for lh in lighthouse_list:
            lh_key_owner = pieces[lh[1], lh[0], LH_KEY_IDX]
            if lh_key_owner == self.turn:
                self._keys.add(lh)

    @staticmethod
    def _set_actor_type(new_actor, previous_actor):
        # actor_type == 1 work
        # actor_type == 2 lighthouse
        # actor_type == 3 work/lighthouse
        if new_actor == 0:
            return 0

        if new_actor == 3 or previous_actor == 3:
            return 3

        if new_actor != previous_actor:
            return new_actor if previous_actor == 0 else 3

        return new_actor

    def move(self, delta, pieces):
        dx, dy = delta
        if dx not in (0, 1, -1) or dy not in (0, 1, -1):
            raise MoveError("Delta must be 1 cell away")
        x, y = self._pos[0] + dx, self._pos[1] + dy
        if not pieces[x, y, ISLAND_IDX]:
            raise MoveError("Target pos is not in island")
        self._pos = (x, y)
