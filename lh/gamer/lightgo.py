#
#     Copyright 2019 Aifriend
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

import operator
import random

from lh.gamer.interface import Bot, Interface
from lh.gamer.utils import Utils


class LightGo(Bot):
    """
    Lightgo player
    """
    NAME = "LightGo"
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

    def _get_lh_dist_map(self, lh, world_map):
        """
        :param lh:
        :param world_map:
        :return:
        """
        lh_map = [[-1 if pos else self.MAX_INT for pos in row] for row in world_map]
        lh_map[lh[1]][lh[0]] = 0
        dist = 1
        points = Utils.get_possible_points(lh, lh_map)
        while len(points):
            next_points = []
            for x, y in points:
                lh_map[y][x] = dist

            for x, y in points:
                cur_points = Utils.get_possible_points((x, y), lh_map)
                next_points.extend(cur_points)
            points = list(set(next_points))
            dist += 1

        lh_map = [[self.MAX_INT if pos == -1 else pos
                   for pos in row]
                  for row in lh_map]

        return lh_map

    def _get_lh_states(self, state):
        """

        :param state:
        :return:
        """
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

    def play(self, state):
        """
        Play as it was called by turn

        :param: state
        :return: action (pass, move, attack, connect)
        """
        lh_states = self._get_lh_states(state)
        my_pos = tuple(state["position"])

        # Lighthouse, first
        if my_pos in lh_states:
            # Connect owned lighthouse
            if lh_states[my_pos]["owner"] == self.player_num:
                # Get only possible connections
                possible_connections = self._get_possible_connections(lh_states, my_pos)
                if possible_connections:
                    # Decide on all possible connections
                    conn = self._decide_connection(
                        possible_connections, state, lh_states)
                    return {
                        "command": "connect",
                        "destination": conn
                    }

            # Attack lighthouse
            if 10 < state["energy"] >= lh_states[my_pos]["energy"]:  # 100
                energy = state["energy"]
                self.log("ATTACK TO: %s", str(my_pos))
                return {
                    "command": "attack",
                    "energy": energy
                }

        # Move to lighthouse, later on
        move = self._decide_movement(state, lh_states)
        return {
            "command": "move",
            "x": move[0],
            "y": move[1]
        }

    ### CONNECTIONS ###

    def _get_possible_connections(self, lh_states, orig):
        """
        Get all possible connection within the game rules

        :param lh_states:
        :param orig:
        :return:
        """
        possible_connections = []
        for dest in lh_states:
            if (dest != orig and  # Do not connect with self
                    lh_states[dest]["have_key"] and  # Do not connect if we have not the key
                    orig not in lh_states[dest]["connections"] and  # Do not connect if it is already connected
                    lh_states[dest]["owner"] == self.player_num and  # Do not connect if we do not own destiny
                    not Utils.has_lhs(orig, dest, lh_states) and  # Do not connect if intersects
                    not Utils.has_connections(lh_states, orig, dest)):
                possible_connections.append(dest)
        return possible_connections

    def _decide_connection(self, possible_connections, state, lh_states):
        """

        :param possible_connections:
        :param state:
        :param lh_states:
        :return:
        """

        my_pos = tuple(state["position"])
        for conn in possible_connections:
            if Utils.closes_tri(lh_states, my_pos, conn):
                self.log("CONNECT TRI: %s", str(conn))
                return conn

        dest_lh = self._decide_dest_lh_connection(state, lh_states)
        if dest_lh is not None:
            self.log("CONNECT CEL: %s", str(dest_lh))
            return dest_lh
        else:
            conn = random.choice(possible_connections)
            self.log("CONNECT RANDOM: %s", str(conn))
            return conn

    def _decide_dest_lh_connection(self, state, lh_states):
        """
        Go to a interesting lighthouse with more chance to sum up bigger tri cells

        :param state:
        :param lh_states:
        :return:
        """

        tri = None
        best_tri = 0
        my_pos = tuple(state["position"])
        possible_connections = self._get_possible_connections(lh_states, my_pos)
        if len(possible_connections) > 1:
            for dest_conn in possible_connections:
                third_possible_connections = possible_connections.copy()
                third_possible_connections.remove(dest_conn)
                for third_conn in third_possible_connections:
                    new_tri = len(Utils.closes_tri_by(my_pos, dest_conn, third_conn, True))
                    if new_tri > best_tri:
                        best_tri = new_tri
                        tri = third_conn

        return tri

    ### MOVEMENTS ###

    def _get_possible_moves(self, pos):
        """
        Get all possible move from current position

        :param pos:
        :return:
        """
        # Random move
        moves = ((0, 0),
                 (-1, -1), (-1, 0), (-1, 1),
                 (0, -1), (0, 1),
                 (1, -1), (1, 0), (1, 1))

        # Check possible movements
        cx, cy = pos
        moves = [(x, y) for x, y in moves if self.map[cy + y][cx + x]]

        return moves

    def _decide_movement(self, state, lh_states):
        """
        Move to a lighthouse with priority

        1) distance to lh => -dist
        2) lh owned
            2.1) with no key => +1000
            2.2) with energy <= (distance*decay) => +500
        3) lh not owned
            3.1) with possible tris => tri_size*1000000
            3.2) with more connections => *200
            3.3) with faint energy < player energy => +400

        :param state:
        :param lh_states:
        :return:
        """

        # Energy re-filling
        possible_moves = self._get_possible_moves(state["position"])
        if state["energy"] < 500:
            try:
                energy_on_move = Utils.harvest_movement(state["view"], possible_moves)
                move = max(energy_on_move, key=energy_on_move.get)
                self.log("MOVE TO HARVEST: %s", str(move))
                return move
            except ValueError as ve:
                exit(-9)

        # Got to the best lighthouse with minimal distance
        dest_lh = self._decide_dest_lh_movement(state, lh_states)
        move_to_lh = self._to_lh_with_optimal_movement(dest_lh, state)

        self.log("MOVE TO LH: %s", str(move_to_lh))
        return move_to_lh

    def _decide_dest_lh_movement(self, state, lh_states):
        """
        Decide best action based on...

        :param state:
        :param lh_states:
        :return:
        """

        # Go to a interesting lighthouse
        for dest_lh in lh_states:
            lh_points = 0

            # Keep fit my owned lighthouses
            if lh_states[dest_lh]["owner"] == self.player_num:
                if not lh_states[dest_lh]["have_key"]:
                    lh_points += 10000000

            else:
                # Look for new promising tris lighthouses
                possible_connections = self._get_possible_connections(lh_states, dest_lh)
                lh_points += len(possible_connections) * 1000
                if len(possible_connections) > 1:
                    for orig_conn in possible_connections:
                        for dest_conn in lh_states[orig_conn]["connections"]:
                            if tuple(dest_conn) in possible_connections:
                                tri_size = Utils.closes_tri(lh_states, dest_conn, orig_conn, size=True)
                                lh_points += 100 * tri_size

            if lh_states[dest_lh]["energy"] < state["energy"]:
                lh_points += 1000

            lh_states[dest_lh]['points'] = lh_points

        dest_lh = max(lh_states.items(), key=lambda x: x[1]['points'])[0]

        return dest_lh

    def _dist_to_lh(self, lh, state):
        """
        Get distance to a lighthouse to move to

        :param lh:
        :param state:
        :return:
        """

        # Movement map with distance to lighthouses
        my_pos = state["position"]
        possible_moves = self._get_possible_moves(my_pos)
        dist_map = self.lh_dist_maps[lh]
        dist = {
            move: dist_map[move[1] + my_pos[1]][move[0] + my_pos[0]]
            for move in possible_moves
        }
        move = min(dist, key=dist.get)

        return dist[move]

    def _to_lh_with_optimal_movement(self, lh, state):
        """
        Get a lighthouse to move to with minimal distance to travel and max energy gain

        :param lh:
        :param state:
        :return:
        """

        # Movement with minimal distance to lighthouse
        my_pos = state["position"]
        possible_moves = self._get_possible_moves(my_pos)
        dist_map = self.lh_dist_maps[lh]
        distance_on_move = {
            move: dist_map[move[1] + my_pos[1]][move[0] + my_pos[0]]
            for move in possible_moves
        }

        # Movement with maximal energy gain
        energy_on_move = Utils.harvest_movement(state["view"], possible_moves)

        # Optimal move with minimal distance and max energy gain
        distance_energy = list()
        for move, dist in distance_on_move.items():
            energy_gain = energy_on_move[move]
            distance_energy.append([move, dist, energy_gain])

        # Guess optimal move
        distance_energy_sorted = sorted(distance_energy, key=operator.itemgetter(1))
        if len(distance_energy_sorted) > 0:
            dist_energy_group = list([distance_energy_sorted.copy().pop(0)])
            for i in range(len(distance_energy_sorted) - 1):
                if dist_energy_group[-1][1] == distance_energy_sorted[i + 1][1]:
                    dist_energy_group.append(distance_energy_sorted[i + 1])
                else:
                    break
            sorted_distance_energy = sorted(dist_energy_group, key=operator.itemgetter(2), reverse=True)
            optimal_move = sorted_distance_energy.pop(0)[0]
        elif len(distance_on_move) > 0:
            # First possible move with no guess on energy gain
            optimal_move = distance_on_move.pop(0)[0]
        else:
            # Random possible move with no guess on energy gain
            optimal_move = random.choice(possible_moves)

        return optimal_move


if __name__ == "__main__":
    iface = Interface(LightGo)
    iface.run()
