import math
import sys

from lh.config.gameconfig import CommError, MoveError
from lh.logic.board.island import Island
from lh.logic.board.lighthouse import Lighthouse
from lh.logic.board.player import Player
from lh.logic.utils.geom import colinear, intersect, render, distt
from lh.logic.utils.process import Process


class Board(object):
    RDIST = 5

    def __init__(self, cfg, num_player=None):
        # players
        if num_player is None:
            num_player = len(cfg.players)
        assert num_player <= len(cfg.players)
        self.players = [Player(self, i, pos) for i, pos in enumerate(cfg.players[:num_player])]

        # island
        self.island = Island(cfg.island)

        # lighthouses
        self.lighthouses = dict((pos, Lighthouse(self, pos)) for pos in cfg.lighthouses)

        # connections
        self.conns = set()
        self.tris = dict()

    def pre_round(self):
        # Update board energy
        for pos in self.lighthouses:
            for y in range(pos[1] - self.RDIST + 1, pos[1] + self.RDIST):
                for x in range(pos[0] - self.RDIST + 1, pos[0] + self.RDIST):
                    dist = distt(pos, (x, y))
                    delta = int(math.floor(self.RDIST - dist))
                    if delta > 0:
                        self.island.energy[x, y] += delta

        # Get board player keys
        player_posmap = dict()
        for player in self.players:
            if player.pos in player_posmap:
                player_posmap[player.pos].append(player)
            else:
                player_posmap[player.pos] = [player]
            if player.pos in self.lighthouses:
                player.keys.add(player.pos)

        # Update board player/island energy
        for pos, players in player_posmap.items():
            energy = self.island.energy[pos] // len(players)
            for player in players:
                player.energy += energy
            self.island.energy[pos] = 0

        # Decay lighthouse energy
        for lh in self.lighthouses.values():
            lh.decay(10)

    def connect(self, player, dest_pos):
        if player.pos not in self.lighthouses:
            raise MoveError("Player must be located at the origin lighthouse")
        if dest_pos not in self.lighthouses:
            raise MoveError("Destination must be an existing lighthouse")
        orig = self.lighthouses[player.pos]
        dest = self.lighthouses[dest_pos]
        if orig.owner != player.num or dest.owner != player.num:
            raise MoveError("Both lighthouses must be player-owned")
        if dest.pos not in player.keys:
            raise MoveError("Player does not have the destination key")
        if orig is dest:
            raise MoveError("Cannot connect lighthouse to itself")
        assert orig.energy and dest.energy
        pair = frozenset((orig.pos, dest.pos))
        if pair in self.conns:
            raise MoveError("Connection already exists")
        x0, x1 = sorted((orig.pos[0], dest.pos[0]))
        y0, y1 = sorted((orig.pos[1], dest.pos[1]))
        for lh in self.lighthouses:
            if (x0 <= lh[0] <= x1 and y0 <= lh[1] <= y1 and
                    lh not in (orig.pos, dest.pos) and
                    colinear(orig.pos, dest.pos, lh)):
                raise MoveError("Connection cannot intersect a lighthouse")
        new_tris = set()
        for c in self.conns:
            if intersect(tuple(c), (orig.pos, dest.pos)):
                raise MoveError("Connection cannot intersect another connection")
            if orig.pos in c:
                third = next(l for l in c if l != orig.pos)
                if frozenset((third, dest.pos)) in self.conns:
                    new_tris.add((orig.pos, dest.pos, third))

        player.keys.remove(dest.pos)
        self.conns.add(pair)
        for i in new_tris:
            self.tris[i] = [j for j in render(i) if self.island[j]]

    def post_round(self):
        # Evaluate board player score: on lighthouses owned
        for lh in self.lighthouses.values():
            if lh.owner is not None:
                self.players[lh.owner].score += 2

        # Evaluate board player score: on lighthouses linked
        for pair in self.conns:
            self.players[self.lighthouses[next(iter(pair))].owner].score += 2

        # Evaluate board player score: on lighthouses closed
        for tri, cells in self.tris.items():
            self.players[self.lighthouses[tri[0]].owner].score += len(cells)


class BotPlayer(object):
    INIT_TIMEOUT = 2.0
    MOVE_TIMEOUT = 0.1
    MOVE_HARDTIMEOUT = 0.5

    def __init__(self, board, playernum, logic, debug=False):
        self.alive = True
        self.board = board
        self.player = board.players[playernum]
        self.player_logic = logic
        self.debug = debug

    def init_player(self):
        """
        El motor envía el siguiente mensaje (ejemplo):
        {
            "player_num": 0,
            "player_count": 2,
            "position": [1, 2],
            "map": [
                [0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0],
                [0, 1, 1, 0, 0],
                [0, 1, 1, 0, 0],
                [0, 0, 0, 0, 0]],
            "lighthouses": [
                [1, 1], [3, 1], [2, 3], [1, 3]
            ]
        }
        """
        if not self.alive:
            return

        state = {
            "player_num": self.player.num,
            "player_count": len(self.board.players),
            "position": self.player.pos,
            "map": self.board.island.map,
            "lighthouses": list(self.board.lighthouses.keys()),
        }
        self.player_logic.initialize(state)
        self.player.name = self.player_logic.NAME

    def turn_by_player(self):
        if not self.alive:
            return

        # Game pre-process
        self.board.pre_round()

        # Request action from all players
        move = self._get_player_move()
        self._apply_move(move)  # Move player on board

        # Game post-process
        self.board.post_round()

    def _get_player_move(self):
        lighthouses = []
        for lh in self.board.lighthouses.values():
            connections = [next(l for l in c if l is not lh.pos)
                           for c in self.board.conns if lh.pos in c]
            lighthouses.append({
                "position": lh.pos,
                "owner": lh.owner,
                "energy": lh.energy,
                "connections": connections,
                "have_key": lh.pos in self.player.keys,
            })
        state = {
            "position": self.player.pos,
            "score": self.player.score,
            "energy": self.player.energy,
            "view": self.board.island.get_view(self.player.pos),
            "lighthouses": lighthouses,
        }
        move = self.player_logic.play(Process.fake_link(state))

        return move

    def _apply_move(self, move):
        if not isinstance(move, dict) or "command" not in move:
            raise CommError("Invalid command structure")

        try:
            if move["command"] == "pass":
                pass

            # Game player move
            elif move["command"] == "move":
                if "x" not in move or "y" not in move:
                    raise MoveError("Move command requires x, y")
                self.player.move((move["x"], move["y"]))

            # Game LH update
            elif move["command"] == "attack":
                if "energy" not in move or not isinstance(move["energy"], int):
                    raise MoveError("Attack command requires integer energy")
                if self.player.pos not in self.board.lighthouses:
                    raise MoveError("Player must be located at target lighthouse")
                self.board.lighthouses[self.player.pos].attack(self.player, move["energy"])

            # Game connection
            elif move["command"] == "connect":
                if "destination" not in move:
                    raise MoveError("Connect command requires destination")
                try:
                    dest = tuple(move["destination"])
                    hash(dest)
                except Exception as exc:
                    raise MoveError("Destination must be a coordinate pair")
                self.board.connect(self.player, dest)

            else:
                raise MoveError("Invalid command %r" % move["command"])

            # Player feedback on success
            self.player_logic.success()

        # Player feedback on failure
        except MoveError as e:
            # sys.stderr.write("Bot %r move error: %s\n" % (self.player.name, e.message))
            self.player_logic.error(e, move)

    def close(self):
        if self.alive:
            sys.stderr.write("Bot %r exit\n" % self.player.name)
            self.alive = False

    def __del__(self):
        self.close()
