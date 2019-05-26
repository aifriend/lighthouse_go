import math
import sys
from typing import Any

import numpy as np

from lh.config.config import CONFIG
from lh.config.configuration \
    import NUM_ENCODERS, ACTS_REV, ISLAND_IDX, TIME_IDX, P_NAME_IDX, A_TYPE_IDX, NUM_ACTS, d_acts, d_a_type
from lh.config.gameconfig import CommError, MoveError, GameConfig
from lh.logic.board.island import Island
from lh.logic.board.lighthouse import Lighthouse
from lh.logic.board.player import Player
from lh.logic.utils.geom import colinear, intersect, render, distt
from lh.logic.utils.process import Process


class Board(object):
    RDIST = 5

    def __init__(self, cfg_file, num_player=None):
        # board from file
        cfg = GameConfig(cfg_file)

        # players
        if num_player is None:
            num_player = len(cfg.players)
        assert num_player <= len(cfg.players)
        self.players = [Player(self, i, pos) for i, pos in enumerate(cfg.players[:num_player])]

        # island -> tiles energy
        self.island = Island(cfg.island)

        # lighthouses
        self.lighthouses = dict((pos, Lighthouse(self, pos)) for pos in cfg.lighthouses)

        # connections
        self.conns = set()
        self.tris = dict()

        # nnet board representation
        self._pieces = np.zeros((cfg.width, cfg.height, NUM_ENCODERS))

    def pre_round(self):
        # Update board energy
        for pos in self.lighthouses:
            for y in range(pos[1] - self.RDIST + 1, pos[1] + self.RDIST):
                for x in range(pos[0] - self.RDIST + 1, pos[0] + self.RDIST):
                    dist = distt(pos, (x, y))
                    delta = int(math.floor(self.RDIST - dist))
                    if delta > 0:
                        self.island.energy[x, y] += delta

        # Player get lh keys
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
        # Evaluate board player score: lighthouses owned
        for lh in self.lighthouses.values():
            if lh.owner is not None:
                self.players[lh.owner].score += 2

        # Evaluate board player score: lighthouses linked
        for pair in self.conns:
            self.players[self.lighthouses[next(iter(pair))].owner].score += 2

        # Evaluate board player score: lighthouses closed
        for tri, cells in self.tris.items():
            self.players[self.lighthouses[tri[0]].owner].score += len(cells)

    def to_array(self):
        return self._pieces


class Bot(object):
    """Bot base. Este bot no hace nada (pasa todos los turnos)."""
    NAME = "NullBot"

    # ==========================================================================
    # Comportamiento del bot
    # Métodos a implementar / sobreescribir (opcionalmente)
    # ==========================================================================

    def __init__(self):
        self.player_num = -1
        self.player_count = 0
        self.init_pos = ()
        self.map = list()
        self.lighthouses = list()

    def initialize(self, init_state):
        """Inicializar el bot: llamado al comienzo del juego."""
        self.player_num = init_state["player_num"]
        self.player_count = init_state["player_count"]
        self.init_pos = init_state["position"]
        self.map = init_state["map"]
        self.lighthouses = map(tuple, init_state["lighthouses"])

    def play(self, state):
        """Jugar: llamado cada turno.
        Debe devolver una acción (jugada).

        state: estado actual del juego.
        """
        return self.nop()

    def success(self):
        """Éxito: llamado cuando la jugada previa es válida."""
        pass

    def error(self, message, last_move):
        """Error: llamado cuando la jugada previa no es válida."""
        self.log("Recibido error: %s", message)
        self.log("Jugada previa: %r", last_move)

    # ==========================================================================
    # Utilidades
    # No es necesario sobreescribir estos métodos.
    # ==========================================================================

    def log(self, message, *args):
        """Mostrar mensaje de registro por stderr"""
        print("[%s] %s" % (self.NAME, (message % args)), file=sys.stderr)

    # ==========================================================================
    # Jugadas posibles
    # No es necesario sobreescribir estos métodos.
    # ==========================================================================

    @staticmethod
    def nop():
        """Pasar el turno"""
        return {
            "command": "pass",
        }

    @staticmethod
    def move(x, y):
        """Mover a una casilla adyacente

        x: delta x (0, -1, 1)
        y: delta y (0, -1, 1)
        """
        return {
            "command": "move",
            "x": x,
            "y": y
        }

    @staticmethod
    def attack(energy):
        """Atacar a un faro

        energy: energía (entero positivo)
        """
        return {
            "command": "attack",
            "energy": energy
        }

    @staticmethod
    def connect(destination):
        """Conectar a un faro remoto

        destination: tupla o lista (x,y): coordenadas del faro remoto
        """
        return {
            "command": "connect",
            "destination": destination
        }


class BotLogic(Bot):
    """
    Lightgo player bot
    """
    NAME = "Lightgo"

    def __init__(self):
        super().__init__()

    def initialize(self, init_state):
        super().initialize(init_state)

    def _play(self):
        # Pass
        return self.nop()

    # Decide attack # Attack - AVAILABLE ACTION - LH - ATTACK
    def _decide_attack(self, state, lh_states):
        my_pos = tuple(state["position"])
        if state["energy"] >= lh_states[my_pos]["energy"]:  # 100
            return state["energy"]

        return 0

    # Decide LH destination # AVAILABLE ACTION - LH - CLOSE-TRI
    def _decide_dest_lh(self, state, lh_states):
        # Go to a interesting lighthouse
        for dest_lh in lh_states:
            lh_points = random.uniform(0.0, 1.0)
            lh_points -= lh_states[dest_lh]['cur_dist']
            if lh_states[dest_lh]["owner"] != self.player_num:
                possible_connections = self._get_possible_connections(lh_states, dest_lh)
                if len(possible_connections) > 1:
                    for orig_conn in possible_connections:
                        for dest_conn in lh_states[orig_conn]["connections"]:
                            if tuple(dest_conn) in possible_connections:
                                tri_size = self._closes_tri(lh_states, dest_conn, orig_conn, size=True)

    # Decide player moves # AVAILABLE ACTION - WK - MOVE + ENERGY
    def _decide_movement(self, state):
        possible_moves = self._get_available_moves(state["position"])  # AVAILABLE ACTION - WK - MOVE
        move, energy_gain = self._harvest_movement(state["view"],
                                                   possible_moves)  # AVAILABLE ACTION - WK - MOVE + ENERGY

        return self.move(move[0], move[1])

    # Get LH connections # AVAILABLE ACTIONS - LH - CONNECTIONS
    def _get_possible_connections(self, my_pos, lh_states, orig):
        possible_connections = []
        if lh_states[my_pos]["owner"] == self.player_num:  # LH - OWN
            for dest in lh_states:
                # Do not connect with self
                # Do not connect if we have not the key
                # Do not connect if it is already connected
                # Do not connect if we do not own destiny
                # Do not connect if intersects
                if (dest != orig and
                        lh_states[dest]["have_key"] and
                        list(orig) not in lh_states[dest]["connections"] and
                        lh_states[dest]["owner"] == self.player_num and
                        not self._has_lhs(orig, dest, lh_states) and
                        not self._has_connections(lh_states, orig, dest)):
                    possible_connections.append(dest)

        return possible_connections

    # Get player moves # AVAILABLE ACTION - WK - MOVE
    def _get_available_moves(self, pos):
        # All possible movements
        moves = ((-1, -1), (-1, 0), (-1, 1),
                 (0, -1), (0, 1),
                 (1, -1), (1, 0), (1, 1))

        # Get possible movements
        cx, cy = pos
        moves = [(x, y) for x, y in moves if self.map[cy + y][cx + x]]

        return moves

    # Get LH-distance map
    @staticmethod  # AVAILABLE ACTIONS - WK - MOVE
    def _get_possible_points(pos, lh_map):
        # Random movements
        moves = ((-1, -1), (-1, 0), (-1, 1),
                 (0, -1), (0, 1),
                 (1, -1), (1, 0), (1, 1))

        # Possible movements
        cx, cy = pos
        points = [(cx + x, cy + y)
                  for x, y in moves
                  if lh_map[cy + y][cx + x] == -1]

        return points

    # Has LH colinear # AVAILABLE ACTIONS - LH - CONN
    def _has_lhs(self, orig, dest, lh_states):
        x0, x1 = sorted((orig[0], dest[0]))
        y0, y1 = sorted((orig[1], dest[1]))
        for lh in lh_states:
            if (x0 <= lh[0] <= x1 and y0 <= lh[1] <= y1 and
                    lh not in (orig, dest) and
                    self._colinear(orig, dest, lh)):
                return True

        return False

    # Has LH connection # AVAILABLE ACTIONS - LH - CONN
    def _has_connections(self, lh_states, orig, dest):
        for lh in lh_states:
            for c in lh_states[lh]["connections"]:
                if self._intersect(
                        (lh_states[lh]["position"], tuple(c)),
                        (orig, dest)):
                    return True

        return False

    # Decide LH connection and destination # AVAILABLE ACTIONS - LH - TRI
    @staticmethod
    def _closes_tri(lh_states, orig, dest, size=False):
        for lh in lh_states:
            conns = lh_states[lh]["connections"]
            if list(orig) in conns and list(dest) in conns:
                if size:
                    min_0 = min(lh[0], orig[0], dest[0])
                    max_0 = max(lh[0], orig[0], dest[0])
                    min_1 = min(lh[1], orig[1], dest[1])
                    max_1 = max(lh[1], orig[1], dest[1])
                    return (max_0 - min_0) * (max_1 - min_1)
                return True

        if size:
            return 0

        return False

    # Decide player motion # AVAILABLE ACTION - WK - MOVE + ENERGY
    @staticmethod
    def _harvest_movement(view, possible_moves):
        view_center = (int(len(view) / 2), int(len(view[0]) / 2))

        energy_on_move = {}
        for move in possible_moves:
            c_x = move[1] + view_center[1]
            c_y = move[0] + view_center[0]
            new_center = \
                view[c_x][c_y] * 8 + \
                (view[c_x - 1][c_y - 1] + view[c_x - 1][c_y] + view[c_x - 1][c_y + 1] +
                 view[c_x + 1][c_y - 1] + view[c_x + 1][c_y] + view[c_x + 1][c_y + 1] +
                 view[c_x][c_y + 1] + view[c_x][c_y - 1]) * 1
            energy_on_move[move] = new_center + random.uniform(0.0, 0.1)

        move = max(energy_on_move, key=energy_on_move.get)

        return move, energy_on_move[move]

    @staticmethod
    def _orient2d(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])

    def _colinear(self, a, b, c):
        return self._orient2d(a, b, c) == 0

    def _intersect(self, j, k):
        j1, j2 = j
        k1, k2 = k
        return (
                self._orient2d(k1, k2, j1) *
                self._orient2d(k1, k2, j2) < 0 and
                self._orient2d(j1, j2, k1) *
                self._orient2d(j1, j2, k2) < 0
        )


class BotPlayer(object):
    def __init__(self, cfg_file, bot, debug=False):
        """
        Opponent player (-1) account for all players apart from player 1. Say, from opponent(-1) to N players [0..N]
        """
        self.board = Board(cfg_file, 1)
        self.player = self.board.players[0]
        self.bot = bot
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
        state = {
            "player_num": self.player.num,
            "player_count": len(self.board.players),
            "position": self.player.pos,
            "map": self.board.island.map,
            "lighthouses": list(self.board.lighthouses.keys()),
        }
        self.bot.initialize(state)
        self.player.name = self.bot.NAME

    def play(self, player):
        """
        Player 1 trigger pre_round pre-processing
        Player -1 trigger post_round post-processing
        """
        # Game pre-process: turn for player 1
        if player:
            self.board.pre_round()

        # Execute move
        move = self._get_player_move()
        self._apply_move(move)  # Move player on board

        # Game post-process: turn for player -1
        if not player:
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
        move = self.bot.play(Process.fake_link(state))

        return move

    def _apply_move(self, move):
        if not isinstance(move, dict) or "command" not in move:
            raise CommError("Invalid command structure")

        try:  # 11 total actions available
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
            self.bot.success()

        # Player feedback on failure
        except MoveError as e:
            # sys.stderr.write("Bot %r move error: %s\n" % (self.player.name, e.message))
            self.bot.error(e, move)


##################################################################################################
##################################################################################################
##################################################################################################


class LHLogic:
    """
    Defines game rules (action checking, end-game conditions)
    can_execute_move is checking if move can be executed and execute_move is applying this move to new board

    """
    def __init__(self, n) -> None:
        self.n = n
        self.pieces = np.zeros((self.n, self.n, NUM_ENCODERS))

    def __getitem__(self, index: int) -> np.array:
        return self.pieces[index]

    def execute_move(self, move, player) -> None:
        """
        Executes move on this board for specified player
        :param move: (x, y, action_index), that define which action should be executed on which tile
        :param player: int - player that is executing action
        :return: /
        """

        if player == 1:
            config = CONFIG.player1_config
        else:
            config = CONFIG.player2_config

        x, y, action_index = move
        act = ACTS_REV[action_index]
        if act == "idle":
            return
        if act == "up":
            new_x, new_y = x, y - 1
            self._move(x, y, new_x, new_y)
            return
        if act == "down":
            new_x, new_y = x, y + 1
            self._move(x, y, new_x, new_y)
            return
        if act == "right":
            new_x, new_y = x + 1, y
            self._move(x, y, new_x, new_y)
            return
        if act == "left":
            new_x, new_y = x - 1, y
            self._move(x, y, new_x, new_y)
            return
        if act == "mine_resources":
            self[x][y][CARRY_IDX] = 1
            return
        if act == "return_resources":
            self[x][y][CARRY_IDX] = 0
            self._update_money(player, config.MONEY_INC)
            return
        if act == "attack_up":
            self._attack(x, y, x, y - 1, config=config)
            return
        if act == "attack_down":
            self._attack(x, y, x, y + 1, config=config)
            return
        if act == "attack_left":
            self._attack(x, y, x - 1, y, config=config)
            return
        if act == "attack_right":
            self._attack(x, y, x + 1, y, config=config)
            return

        if act == "heal_up":
            self._heal(x, y, x, y - 1, config=config)
            return
        if act == "heal_down":
            self._heal(x, y, x, y + 1, config=config)
            return
        if act == "heal_left":
            self._heal(x, y, x - 1, y, config=config)
            return
        if act == "heal_right":
            self._heal(x, y, x + 1, y, config=config)
            return

        if act == "npc_up":
            self._update_money(player, -config.a_cost[2])
            self._spawn(x, y, x, y - 1, 2, config=config)
            return
        if act == "npc_down":
            self._update_money(player, -config.a_cost[2])
            self._spawn(x, y, x, y + 1, 2, config=config)
            return
        if act == "npc_left":
            self._update_money(player, -config.a_cost[2])
            self._spawn(x, y, x - 1, y, 2, config=config)
            return
        if act == "npc_right":
            self._update_money(player, -config.a_cost[2])
            self._spawn(x, y, x + 1, y, 2, config=config)
            return

        if act == "barracks_up":
            self._update_money(player, -config.a_cost[3])
            self._spawn(x, y, x, y - 1, 3, config=config)
            return
        if act == "barracks_down":
            self._update_money(player, -config.a_cost[3])
            self._spawn(x, y, x, y + 1, 3, config=config)
            return
        if act == "barracks_left":
            self._update_money(player, -config.a_cost[3])
            self._spawn(x, y, x - 1, y, 3, config=config)
            return
        if act == "barracks_right":
            self._update_money(player, -config.a_cost[3])
            self._spawn(x, y, x + 1, y, 3, config=config)
            return

    def _move(self, x, y, new_x, new_y):
        """
        Move actor to new location
        :param x: int - coordinate x where actor is located
        :param y: int - coordinate y where actor is located
        :param new_x: int - coordinate x where actor needs to be moved to
        :param new_y: int - coordinate y where actor needs to be moved to
        """
        self[new_x][new_y] = self[x][y]
        self[x][y] = [0] * NUM_ENCODERS
        self[x][y][TIME_IDX] = self[new_x][new_y][TIME_IDX]  # set time back to empty tile

    def _update_money(self, player, money_update):
        """
        :param player: int - player to which money gets appended/ decreased
        :param money_update: int - amount of money
        """
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y][P_NAME_IDX] == player:
                    assert self[x][y][MONEY_IDX] + money_update >= 0
                    self[x][y][MONEY_IDX] = self[x][y][MONEY_IDX] + money_update

    def _attack(self, x, y, n_x, n_y, config):
        """
        Actor attacks new actor on other coordinate
        :param x: actor on coordinate x
        :param y: actor on coordinate y
        :param n_x: attack new actor on coordinate n_x
        :param n_y: attack new actor on coordinate n_x
        :param config: config that specifies damage - different config can be used for each player
        """
        self[n_x][n_y][HEALTH_IDX] -= config.DAMAGE
        if self[n_x][n_y][HEALTH_IDX] <= 0:
            self[n_x][n_y] = [0] * NUM_ENCODERS
            self[n_x][n_y][TIME_IDX] = self[x][y][TIME_IDX]  # set time back to empty tile just in case

    def _spawn(self, x, y, n_x, n_y, a_type, config):
        """
        Actor spawns actor on other coordinate
        :param x: coordinate of building that is spawning new actor
        :param y: coordinate of building that is spawning new actor
        :param n_x: coordinate where new actor will spawn to
        :param n_y: coordinate where new actor will spawn to
        :param a_type: type of unit to spawn on new coordinate
        :param config: additional config that is separate for each player (maximum actor health for this type)
        """
        self[n_x][n_y] = [self[x][y][P_NAME_IDX], a_type, config.a_max_health[a_type], 0, self[x][y][MONEY_IDX],
                          self[x][y][TIME_IDX]]

    def _heal(self, x, y, n_x, n_y, config):
        """
        Actor heals actor on other coordinate
        :param x: coordinate of actor executing heal action
        :param y: oordinate of actor executing heal action
        :param n_x: coordinate of actor that will receive heal
        :param n_y: coordinate of actor that will receive heal
        :param config: additional config that is separate for each player (heal_cost, heal_amount, max_actor_health)
        """
        if config.SACRIFICIAL_HEAL:
            self[x][x][HEALTH_IDX] -= config.HEAL_COST
            if self[x][y][HEALTH_IDX] <= 0:
                self[x][y] = [0] * NUM_ENCODERS
                self[x][y][TIME_IDX] = self[x][y][TIME_IDX]
        elif self[n_x][n_y][MONEY_IDX] - config.HEAL_AMOUNT >= 0:
            self[n_x][n_y][HEALTH_IDX] += config.HEAL_AMOUNT
            self._update_money(self[n_x][n_y][P_NAME_IDX], -config.HEAL_COST)

        # clamp value to max
        self[n_x][n_y][HEALTH_IDX] = self.clamp(self[n_x][n_y][HEALTH_IDX] + config.HEAL_AMOUNT, 0,
                                                config.a_max_health[self[n_x][n_y][A_TYPE_IDX]])

    def get_moves_for_square(self, x, y, config) -> Any:
        """
        Returns all valid actions for specific tile
        :param x: x coordinate of tile
        :param y: y coordinate of tile
        :param config: additional config that is separate for each player
        :return: array of valid actions
        """
        # determine the color of the piece.
        player = self[x][y][P_NAME_IDX]

        if player == 0:
            return None
        a_type = self[x][y][A_TYPE_IDX]
        acts = d_acts[a_type]
        moves = [0] * NUM_ACTS
        for i in range(NUM_ACTS):
            act = ACTS_REV[i]
            if act in acts:
                # a is now string action
                move = self._valid_act(x, y, act, config=config) * 1
                if move:
                    moves[i] = move

        # return the generated move list
        return moves

    def _valid_act(self, x, y, act, config):
        """
        Returns true if action on specific tile is valid, false otherwise
        :param x: tile x that action will be executing upon
        :param y: tile y that action will be executing upon
        :param act: str: action that will be executing on this tile
        :param config: additional config that gets passed to functions
        :return: true/false
        """
        if act == "pass":
            return config.acts_enabled.
            pass
        if act == "up":
            return config.acts_enabled.up and self._check_if_empty(x, y - 1)
        if act == "down":
            return config.acts_enabled.down and self._check_if_empty(x, y + 1)
        if act == "right":
            return config.acts_enabled.right and self._check_if_empty(x + 1, y)
        if act == "left":
            return config.acts_enabled.left and self._check_if_empty(x - 1, y)

        if act == "upright":
            return config.acts_enabled.up and self._check_if_empty(x, y - 1)
        if act == "upleft":
            return config.acts_enabled.down and self._check_if_empty(x, y + 1)
        if act == "downright":
            return config.acts_enabled.right and self._check_if_empty(x + 1, y)
        if act == "downleft":
            return config.acts_enabled.left and self._check_if_empty(x - 1, y)

        if act == "attack":
            return config.acts_enabled.attack and self._check_if_attack(x, y)

        if act == "connect":
            return config.acts_enabled.barracks and config.a_cost[3] <= money and self._check_if_empty(x - 1, y)

        print("Unrecognised action", act)
        sys.exit(0)

    def _check_if_empty(self, x, y):
        """
        Checks if tile is empty
        :param x: if x coordinate is empty
        :param y: if y coordinate is empty
        :return: true/false
        """
        # noinspection PyChainedComparisons
        return self.n > x >= 0 and 0 <= y < self.n and self[x][y][ISLAND_IDX] == 1

    def _check_if_attack(self, x, y):
        """
        Check if actor on x,y can attack actor on n_x,n_y
        :param x: actor on coordinate x
        :param y: actor on coordinate y
        :param n_x: can attack actor on coordinate n_x
        :param n_y: can attack actor on coordinate n_y
        :return: true/false
        """
        # noinspection PyChainedComparisons
        return not self._check_if_empty(x, y) and self[x][y][A_TYPE_IDX] == d_a_type['Lighthouse']

    def _check_if_heal(self, x, y, config):
        """
        Check if actor on x,y can be healed
        :param x: coordinate of actor that is getting to be healed
        :param y: coordinate of actor that is getting to be healed
        :param config: special config specific for each player (max_health, heal_cost)
        :return: true/false
        """
        return 0 <= x < self.n and 0 <= y < self.n and self[x][y][P_NAME_IDX] == self[x][y][P_NAME_IDX] and self[x][y][
            A_TYPE_IDX] != d_a_type['Gold'] and self[x][y][A_TYPE_IDX] > 0 and self[x][y][HEALTH_IDX] < \
               config.a_max_health[self[x][y][A_TYPE_IDX]] and (
                       config.SACRIFICIAL_HEAL or self[x][y][MONEY_IDX] - config.HEAL_COST >= 0)

    def _check_if_nearby(self, x, y, a_type, check_friendly=False):
        """
        Checks if actor is nearby - friendly or foe
        :param x: coordinate of current actor
        :param y: coordinate of current actor
        :param a_type: type of nearby actor
        :param check_friendly: check if nearby actor should be friendly
        :return: true/false
        """
        coordinates = [(x - 1, y + 1),
                       (x, y + 1),
                       (x + 1, y + 1),
                       (x - 1, y),
                       (x + 1, y),
                       (x - 1, y - 1),
                       (x, y - 1),
                       (x + 1, y - 1)]
        for n_x, n_y in coordinates:
            if 0 <= n_x < self.n and 0 <= n_y < self.n:
                if self[n_x][n_y][A_TYPE_IDX] == a_type:
                    if not check_friendly:
                        return True
                    if self[n_x][n_y][P_NAME_IDX] == self[x][y][P_NAME_IDX]:
                        return True
        return False

    @staticmethod
    def clamp(num, min_value, max_value):
        return max(min(num, max_value), min_value)

    def get_money_score(self, player) -> int:
        """
        1. of 3 functions that define elo rating of specified player. This one takes into account only players money count
        :param player: player that requires to know his money count
        :return: money count for specified player
        """
        return sum(
            [self[x][y][MONEY_IDX] for x in range(self.n) for y in range(self.n) if self[x][y][P_NAME_IDX] == player])

    def get_health_score(self, player) -> int:
        """
        2. of 3 functions that define elo rating for specified player. This one takes into account only total current health of units. Players with more units, which have more health should win.
        :param player: player that requires to know sum of health for his units
        :return: sum of health for specified player
        """
        return sum(
            [self[x][y][HEALTH_IDX] for x in range(self.n) for y in range(self.n) if self[x][y][P_NAME_IDX] == player])

    def get_combined_score(self, player) -> int:
        """
        3. of 3 functions that define elo rating for specified player. This takes into account both 1. and 2. functions and joins them together.
        :param player: player that requires to know his money count + sum of health of his units
        :return: count of money + sum of health of specified players' units
        """
        # money is not worth more than 1hp because this forces players to spend money in order to create new units
        return sum([self[x][y][HEALTH_IDX] + self[x][y][MONEY_IDX] for x in range(self.n) for y in range(self.n) if
                    self[x][y][P_NAME_IDX] == player])
