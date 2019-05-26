import random
import sys


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


class LightGoLogic(Bot):
    """
    Lightgo player bot
    """
    NAME = "Lightgo"
    MAX_INT = 1e40

    def __init__(self):
        super().__init__()

    def initialize(self, init_state):
        super().initialize(init_state)

    def play(self, state):
        """
        Play as it was called by turn

        :param: state
        :return: action (pass, move, attack, connect)
        """
        my_pos = tuple(state["position"])

        if my_pos in lhs:
            # Connect - AVAILABLE ACTION - LH - CONNECTION
            if lhs[my_pos]["owner"] == self.player_num:  # AVAILABLE ACTION - LH - OWN
                possible_connections = self._get_possible_connections(lhs, my_pos)

            # Attack - AVAILABLE ACTION - LH - ATTACK
            if state["energy"] >= lhs[my_pos]["energy"]:  # 100
                energy = state["energy"]

        # Move - AVAILABLE ACTION - WK - MOVE
        move = self._decide_movement(state, lhs)
        self.move(move[0], move[1])

        # Pass
        return self.nop()

    ##########################################################################

    """
    LH MOVES
    """

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

    """
    Player moves
    """

    # Decide player moves # AVAILABLE ACTION - WK - MOVE + ENERGY
    def _decide_movement(self, state, lh_states):
        possible_moves = self._get_available_moves(state["position"])  # AVAILABLE ACTION - WK - MOVE
        move, energy_gain = self._harvest_movement(state["view"],
                                                   possible_moves)  # AVAILABLE ACTION - WK - MOVE + ENERGY

    ##########################################################################

    """
    LH HELPERS
    """

    # Get LH connections # AVAILABLE ACTIONS - LH - CONNECTIONS
    def _get_possible_connections(self, lh_states, orig):
        possible_connections = []
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

    """
    Player helpers
    """

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

    ##########################################################################

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


class LightGoDecision(Bot):
    """
    Lightgo player bot
    """
    NAME = "Lightgo"
    MAX_INT = 1e40

    def __init__(self):
        super().__init__()
        self.lh_dist_maps = []

    def initialize(self, init_state):
        super().initialize(init_state)
        self.lh_dist_maps = {
            lh: self._get_lh_dist_map(lh, init_state["map"])
            for lh in self.lighthouses
        }

    def play(self, state):
        """
        Play as it was called by turn

        :param: state
        :return: action (pass, move, attack, connect)
        """
        lh_states = self._get_lh_dist(state)
        my_pos = tuple(state["position"])

        if my_pos in lh_states:
            # Connect
            if lh_states[my_pos]["owner"] == self.player_num:
                possible_connections = self._get_possible_connections(lh_states, my_pos)
                if possible_connections:
                    conn = self._decide_connection(
                        possible_connections, my_pos, lh_states)
                    self.connect(conn)

            # Attack
            if state["energy"] >= lh_states[my_pos]["energy"]:  # 100
                energy = state["energy"]
                self.log("ATTACK TO: %s", str(my_pos))
                self.attack(energy)

        # Move
        move = self._decide_movement(state, lh_states)
        self.move(move[0], move[1])

        # Pass
        return self.nop()

    ##########################################################################

    """
    LH MOVES
    """

    # Decide LH connection
    def _decide_connection(self, possible_connections, my_pos, lh_states):
        for conn in possible_connections:
            if self._closes_tri(lh_states, my_pos, conn):
                self.log("CONNECT TRI: %s", str(conn))
                return conn

        conn = random.choice(possible_connections)
        self.log("CONNECT RANDOM: %s", str(conn))
        return conn

    # Decide LH destination
    def _decide_dest_lh(self, state, lh_states):
        # Go to a interesting lighthouse
        for dest_lh in lh_states:
            lh_points = random.uniform(0.0, 1.0)
            lh_points -= lh_states[dest_lh]['cur_dist']
            if lh_states[dest_lh]["owner"] == self.player_num:
                if not lh_states[dest_lh]["have_key"]:
                    lh_points += 1000
                if lh_states[dest_lh]["energy"] < state["energy"]:
                    lh_points += 500
            else:
                possible_connections = self._get_possible_connections(lh_states, dest_lh)
                lh_points += len(possible_connections) * 100
                if len(possible_connections) > 1:
                    for orig_conn in possible_connections:
                        for dest_conn in lh_states[orig_conn]["connections"]:
                            if tuple(dest_conn) in possible_connections:
                                tri_size = self._closes_tri(lh_states, dest_conn, orig_conn, size=True)
                                lh_points += 1000000 * tri_size

                if lh_states[dest_lh]["energy"] < state["energy"]:
                    lh_points += 100
            lh_states[dest_lh]['points'] = lh_points

        dest_lh = max(lh_states.items(),
                      key=lambda x: x[1]['points'])[0]
        return dest_lh

    """
    Player moves
    """

    # Decide player moves
    def _decide_movement(self, state, lh_states):
        possible_moves = self._get_available_moves(state["position"])
        if state["energy"] < 500:
            move, energy_gain = self._harvest_movement(state["view"], possible_moves)
            if energy_gain > 10:
                self.log("MOVE TO HARVEST: %s", str(move))
                return move
        dest_lh = self._decide_dest_lh(state, lh_states)
        move = self._to_lh_movement(dest_lh,
                                    state["position"],
                                    possible_moves)

        self.log("MOVE TO LH: %s", str(move))
        return move

    ##########################################################################

    """
    LH HELPERS
    """

    # Get LH distance map
    def _get_lh_dist_map(self, lh, world_map):
        lh_map = [[-1 if pos else self.MAX_INT for pos in row] for row in world_map]
        lh_map[lh[1]][lh[0]] = 0
        dist = 1
        points = self._get_possible_points(lh, lh_map)
        while len(points):
            next_points = []
            for x, y in points:
                lh_map[y][x] = dist
            for x, y in points:
                cur_points = self._get_possible_points((x, y), lh_map)
                next_points.extend(cur_points)
            points = list(set(next_points))
            dist += 1

        lh_map = [[self.MAX_INT if pos == -1 else pos
                   for pos in row]
                  for row in lh_map]

        return lh_map

    # Get LH distance
    def _get_lh_dist(self, state):
        my_pos = tuple(state["position"])
        dists_to_lhs = {
            lh: self.lh_dist_maps[lh][my_pos[1]][my_pos[0]]
            for lh in self.lh_dist_maps
        }

        _lh_states = {
            tuple(lh["position"]): lh
            for lh in state["lighthouses"]
        }

        for lh in _lh_states:
            _lh_states[lh]['cur_dist'] = \
                dists_to_lhs[tuple(_lh_states[lh]["position"])]

        return _lh_states

    # Get LH connections
    def _get_possible_connections(self, lh_states, orig):
        possible_connections = []
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

    """
    Player helpers
    """

    # Get player moves
    def _get_available_moves(self, pos):
        # All possible movements
        moves = ((-1, -1), (-1, 0), (-1, 1),
                 (0, -1), (0, 1),
                 (1, -1), (1, 0), (1, 1))

        # Get possible movements
        cx, cy = pos
        moves = [(x, y) for x, y in moves if self.map[cy + y][cx + x]]

        return moves

    # Do player moves
    def _to_lh_movement(self, lh, my_pos, possible_moves):
        dist_map = self.lh_dist_maps[lh]
        dist = {
            move: dist_map[move[1] + my_pos[1]][move[0] + my_pos[0]]
            for move in possible_moves
        }
        move = min(dist, key=dist.get)

        return move

    ##########################################################################

    # Get LH-distance map
    @staticmethod
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

    # Get LH connections
    def _has_lhs(self, orig, dest, lh_states):
        x0, x1 = sorted((orig[0], dest[0]))
        y0, y1 = sorted((orig[1], dest[1]))
        for lh in lh_states:
            if (x0 <= lh[0] <= x1 and y0 <= lh[1] <= y1 and
                    lh not in (orig, dest) and
                    self._colinear(orig, dest, lh)):
                return True

        return False

    # Decide LH connection and destination
    def _has_connections(self, lh_states, orig, dest):
        for lh in lh_states:
            for c in lh_states[lh]["connections"]:
                if self._intersect(
                        (lh_states[lh]["position"], tuple(c)),
                        (orig, dest)):
                    return True

        return False

    # Decide LH connection and destination
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

    # Decide player motion
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
