import math

import numpy as np

from lh.config.config import CONFIG
from lh.config.configuration import ISLAND_IDX, ACTS_REV, NUM_ACTS, LH_CONN_IDX, LH_TRI_IDX, ENERGY_IDX
from lh.config.gameconfig import MoveError, GameConfig
from lh.logic.board.island import Island
from lh.logic.board.lighthouse import Lighthouse
from lh.logic.board.player import Player
from lh.logic.utils.geom import colinear, intersect, render, distt


class Connection:
    def __init__(self):
        self._conns = set()

    @property
    def conns(self):
        return self._conns

    def conns_to_board(self, pieces, conns=None):
        if conns is not None:
            self._conns = conns
        pieces[0, 0, LH_CONN_IDX] = self._conns

    def board_to_conns(self, pieces):
        self._conns = pieces[0, 0, LH_CONN_IDX]

    @staticmethod
    def encode_conns(pieces) -> None:
        connection = 0
        player_lh = Lighthouse.owned_by(pieces, player=1)
        conns = pieces[0][0][LH_CONN_IDX]
        for pair in conns:
            if next(iter(pair)) in player_lh:
                connection += 1
        pieces[0][0][LH_CONN_IDX] = connection

    def close_conn(self, pos):
        self._conns = set(i for i in self._conns if pos not in i)


class Triangle:
    def __init__(self):
        self._tris = dict()

    @property
    def tris(self):
        return self._tris

    def tris_to_board(self, pieces, tris=None):
        if tris is not None:
            self._tris = tris
        pieces[0, 0, LH_TRI_IDX] = self._tris

    def board_to_tris(self, pieces):
        self._tris = pieces[0, 0, LH_TRI_IDX]

    @staticmethod
    def encode_tris(pieces) -> None:
        cell = 0
        player_lh = Lighthouse.owned_by(pieces, player=1)
        polygons = pieces[0][0][LH_TRI_IDX]
        for key, tris in polygons.items():
            if next(iter(key)) in player_lh:
                cell += len(tris)
        pieces[0, 0, LH_TRI_IDX] = cell

    def close_tri(self, pos):
        self._tris = dict(i for i in self._tris.items() if pos not in i[0])


class Board(object):
    RDIST = 5

    def __init__(self):
        self.size = dict()
        self._island = None
        self._players = list()
        self._lighthouses = dict()
        self._connection = None
        self._triangle = None

    def from_file(self, cfg_file, num_player=None):
        # board from file
        cfg = GameConfig(cfg_file)
        self.size = dict(height=cfg.height, width=cfg.width)

        # island
        self._island = Island(cfg.island)

        # players
        if num_player is None:
            num_player = len(cfg.players)
        assert num_player <= len(cfg.players)
        for i, (c, pos) in enumerate(cfg.players[:num_player]):
            self._players.append(Player(pos, i))

        # lighthouses
        self._lighthouses = dict((pos, Lighthouse(self, pos)) for pos in enumerate(cfg.lighthouses))

        # connections
        self._connection = Connection()
        self._triangle = Triangle()

    def from_array(self, board):
        # island
        self._island = Island.from_array(board)

        # players
        self._players = Player.from_array(board)

        # lighthouses
        self._lighthouses = Lighthouse.from_array(board)

        # conns & tris
        self._connection.board_to_conns(board)
        self._triangle.board_to_tris(board)

    def to_array(self, board) -> np.array:
        pieces = np.copy(board)

        # island
        pieces[:, :, ISLAND_IDX] = self._island.map

        # energy
        pieces[:, :, ENERGY_IDX] = self._island.energy

        # players
        for player in self._players:
            player.turn_to_board(pieces)
            player.keys_to_board(pieces)
            player.score_to_board(pieces)

        # lighthouses
        for lighthouse in self._lighthouses.values():
            lighthouse.lh_to_board(pieces)
            lighthouse.energy_to_board(pieces)
            lighthouse.owner_to_board(pieces)

        # conns & tris
        self._connection.conns_to_board(pieces)
        self._triangle.tris_to_board(pieces)

        return pieces

    def close_conn(self, pos):
        self._connection.close_conn(pos)
        self._triangle.close_tri(pos)

    def pre_round(self):
        # Update island energy
        for pos in self._lighthouses:
            for y in range(pos[1] - self.RDIST + 1, pos[1] + self.RDIST):
                for x in range(pos[0] - self.RDIST + 1, pos[0] + self.RDIST):
                    dist = distt(pos, (x, y))
                    delta = int(math.floor(self.RDIST - dist))
                    if delta > 0:
                        self._island.energy[x, y] += delta

        # Player get lh keys
        player_posmap = dict()
        for player in self._players:
            if player.pos in player_posmap:
                player_posmap[player.pos].append(player)
            else:
                player_posmap[player.pos] = [player]
            if player.pos in self._lighthouses:
                player.keys.add(player.pos)

        # Update player energy
        for pos, players in player_posmap.items():
            energy = self._island.energy[pos] // len(players)
            for player in players:
                player.energy += energy
            self._island.energy[pos] = 0

        # Decay lighthouse energy
        for lh in self._lighthouses.values():
            lh.decay(10)

    def connect(self, player, dest_pos):
        if player.pos not in self._lighthouses:
            raise MoveError("Player must be located at the origin lighthouse")
        if dest_pos not in self._lighthouses:
            raise MoveError("Destination must be an existing lighthouse")
        orig = self._lighthouses[player.pos]
        dest = self._lighthouses[dest_pos]
        if orig.owner != player.num or dest.owner != player.num:
            raise MoveError("Both lighthouses must be player-owned")
        if dest.pos not in player.keys:
            raise MoveError("Player does not have the destination key")
        if orig is dest:
            raise MoveError("Cannot connect lighthouse to itself")
        assert orig.energy and dest.energy
        pair = frozenset((orig.pos, dest.pos))
        if pair in self._connection.conns:
            raise MoveError("Connection already exists")
        x0, x1 = sorted((orig.pos[0], dest.pos[0]))
        y0, y1 = sorted((orig.pos[1], dest.pos[1]))
        for lh in self._lighthouses:
            if (x0 <= lh[0] <= x1 and y0 <= lh[1] <= y1 and
                    lh not in (orig.pos, dest.pos) and
                    colinear(orig.pos, dest.pos, lh)):
                raise MoveError("Connection cannot intersect a lighthouse")
        new_tris = set()
        for c in self._connection.conns:
            if intersect(tuple(c), (orig.pos, dest.pos)):
                raise MoveError("Connection cannot intersect another connection")
            if orig.pos in c:
                third = next(l for l in c if l != orig.pos)
                if frozenset((third, dest.pos)) in self._connection.conns:
                    new_tris.add((orig.pos, dest.pos, third))

        player.keys.remove(dest.pos)
        self._connection.conns.add(pair)
        for i in new_tris:
            self._triangle.tris[i] = [j for j in render(i) if self._island[j]]

    def post_round(self):
        # Evaluate board player score: lighthouses owned
        for lh in self._lighthouses.values():
            if lh.owner is not None:
                self._players[lh.owner].score += 2

        # Evaluate board player score: lighthouses linked
        for pair in self._connection.conns:
            self._players[self._lighthouses[next(iter(pair))].owner].score += 2

        # Evaluate board player score: lighthouses closed
        for tri, cells in self._triangle.tris.items():
            self._players[self._lighthouses[tri[0]].owner].score += len(cells)

    def get_available_worker_moves(self, player, valid_moves, valid_actions):
        # All possible movements: (row, col)
        possible_moves = {1: (0, -1),  # up
                          2: (0, 1),  # down
                          3: (1, 0),  # right
                          4: (-1, 0),  # left
                          5: (1, -1),  # upright
                          6: (-1, -1),  # upleft
                          7: (1, 1),  # downright
                          8: (-1, 1)}  # downleft

        # Get possible movements
        cx, cy = player.pos
        directions = [tuple()] * len(possible_moves)
        for key, mov in possible_moves:
            if self._island.map[cy + mov[1]][cx + mov[0]]:
                directions[key] = mov
                valid_moves[key] = 1

        valid_actions.append(directions)

    def get_available_attack(self, player, valid_moves, valid_actions):
        # All possible attacks
        possible_attack = {9: 0.1,  # attack 10%
                           10: 0.3,  # attack 30%
                           11: 0.6,  # attack 60%
                           12: 0.8,  # attack 80%
                           13: 1.0}  # attack 100%

        attacks = [-1] * len(possible_attack)
        if player.pos in self._lighthouses:
            lh_energy = self._lighthouses[player.pos].energy
            if player.energy >= lh_energy * possible_attack[9]:
                attacks[9] = int(round(player.energy * possible_attack[9]))
                valid_moves[9] = 1
            if player.energy >= lh_energy * possible_attack[10]:
                attacks[10] = int(round(player.energy * possible_attack[10]))
                valid_moves[10] = 1
            if player.energy >= lh_energy * possible_attack[11]:
                attacks[11] = int(round(player.energy * possible_attack[11]))
                valid_moves[11] = 1
            if player.energy >= lh_energy * possible_attack[12]:
                attacks[12] = int(round(player.energy * possible_attack[12]))
                valid_moves[12] = 1
            if player.energy >= lh_energy * possible_attack[13]:
                attacks[13] = int(round(player.energy * possible_attack[13]))
                valid_moves[13] = 1

        valid_actions.append(attacks)

    def get_available_lh_connections(self, player, valid_moves, valid_actions):
        # All possible connections
        possible_lh_connections = {14: "connect0",
                                   15: "connect1",
                                   16: "connect2",
                                   17: "connect3",
                                   18: "connect4"}

        connections = [tuple()] * len(possible_lh_connections)
        if player.pos in self._lighthouses:
            orig = self._lighthouses[player.pos].pos
            if orig.owner == player:  # own lighthouse
                for dest in self._lighthouses.values():
                    # Do not connect with self
                    # Do not connect if we have not the key
                    if dest != orig and player.has_key(dest.pos):
                        dest_connections = [next(l for l in c if l is not dest.pos)
                                            for c in self._connection.conns if dest.pos in c]
                        # Do not connect if it is already connected
                        # Do not connect if we do not own destiny
                        # Do not connect if intersects
                        if (list(orig) not in dest_connections and
                                dest.owner == player and
                                not self._lh_colinear(orig, dest) and
                                not self._lh_intersect(orig, dest)):
                            try:
                                key, _ = possible_lh_connections.popitem()
                                connections[key] = dest
                                valid_moves[key] = 1
                            except KeyError:
                                break

        valid_actions.append(connections)

    @staticmethod
    def get_score(player) -> int:
        """
        Define elo rating for specified player. This one takes into account only total current health of units.
        Players with more units, which have more health should win.

        :param player: player that requires to know sum of health for his units
        :return: sum of health for specified player
        """
        return player.score

    def _lh_colinear(self, orig, dest):
        x0, x1 = sorted((orig[0], dest[0]))
        y0, y1 = sorted((orig[1], dest[1]))
        for lh in self._lighthouses.values():
            if (x0 <= lh[0] <= x1 and y0 <= lh[1] <= y1 and
                    lh not in (orig, dest) and
                    self._colinear(orig, dest, lh)):
                return True

        return False

    def _lh_intersect(self, orig, dest):
        for lh in self._lighthouses.values():
            connections = [next(l for l in c if l is not lh.pos)
                           for c in self._connection.conns if lh.pos in c]
            for c in connections:
                if self._intersect((lh.pos, tuple(c)), (orig, dest)):
                    return True

        return False

    def _colinear(self, a, b, c):
        return self._orient2d(a, b, c) == 0

    @staticmethod
    def _orient2d(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])

    def _intersect(self, j, k):
        j1, j2 = j
        k1, k2 = k
        return (
                self._orient2d(k1, k2, j1) *
                self._orient2d(k1, k2, j2) < 0 and
                self._orient2d(j1, j2, k1) *
                self._orient2d(j1, j2, k2) < 0
        )


class LHLogic:
    """
    Defines game rules (action checking, end-game conditions)
    can_execute_move is checking if move can be executed and execute_move is applying this move to new board
    """
    ACTIONS = list()

    def __init__(self, cfg_file) -> None:
        self.config_file = cfg_file
        self.board = None

    def initialize(self):
        self.board = Board()
        self.board.from_file(self.config_file, 2)

    def get_next_state(self, player, action_index):
        """
        Player 1 trigger pre_round pre-processing
        Player -1 trigger post_round post-processing
        """
        if player == 1:
            config = CONFIG.player1_config
        else:
            config = CONFIG.player2_config

        # Execute move
        act = ACTS_REV[action_index]
        act_value = self.ACTIONS[action_index]

        if act == "pass":
            pass

        # Game player move
        elif act == "move":
            if not act_value:
                raise MoveError("Move command requires x, y")
            player.move((act_value[0], act_value[1]))

        # Game LH update
        elif act == "attack":
            if not act_value or not isinstance(act_value, int):
                raise MoveError("Attack command requires integer energy")
            if player.pos not in self.board.lighthouses:
                raise MoveError("Player must be located at target lighthouse")
            self.board.lighthouses[player.pos].attack(player, act_value)

        # Game connection
        elif act == "connect":
            if not act_value or not isinstance(act_value, tuple):
                raise MoveError("Connect command requires destination")
            try:
                dest = act_value
                hash(dest)
            except Exception:
                raise MoveError("Destination must be a coordinate pair")
            self.board.connect(player, dest)

        else:
            raise MoveError("Invalid command %r with param %r" % (act, act_value))

    def get_valid_moves(self, player, config):
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
        if player.turn == 0:
            return None

        # get valid moves
        moves = [0] * NUM_ACTS
        actions = list()

        # AVAILABLE ACTION - WK - MOVE
        self.board.get_available_worker_moves(player, moves, actions)

        # AVAILABLE ACTION - WK - ATTACK
        self.board.get_available_attack(player, moves, actions)

        # AVAILABLE ACTION - LH - CONN
        self.board.get_available_lh_connections(player, moves, actions)

        self.ACTIONS = actions

        # return the generated move list
        return moves
