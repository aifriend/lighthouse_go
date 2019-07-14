#!/usr/bin/python
# -*- coding: utf-8 -*-

import random

from lighthouses_aicontest.gamer.p_random import bot


class RandBot(bot.Bot):
    """Bot que juega aleatoriamente."""
    NAME = "RandBot"

    def play(self, state):
        """Jugar: llamado cada turno.
        Debe devolver una acción (jugada)."""
        cx, cy = state["position"]
        lighthouses = dict((tuple(lh["position"]), lh)
                           for lh in state["lighthouses"])

        # Si estamos en un faro...
        if (cx, cy) in self.lighthouses:
            # Probabilidad 60%: conectar con faro remoto válido
            if lighthouses[(cx, cy)]["owner"] == self.player_num:
                if random.randrange(100) < 60:
                    possible_connections = []
                    for dest in self.lighthouses:
                        # No conectar con sigo mismo
                        # No conectar si no tenemos la clave
                        # No conectar si ya existe la conexión
                        # No conectar si no controlamos el destino
                        # Nota: no comprobamos si la conexión se cruza.
                        if (dest != (cx, cy) and
                                lighthouses[dest]["have_key"] and
                                [cx, cy] not in lighthouses[dest]["connections"] and
                                lighthouses[dest]["owner"] == self.player_num):
                            possible_connections.append(dest)

                    if possible_connections:
                        conn = random.choice(possible_connections)
                        self.log("CONNECT RANDOM: %s", str(conn))
                        return self.connect(conn)

            # Probabilidad 60%: recargar el faro
            if random.randrange(100) < 60:
                energy = random.randrange(state["energy"] + 1)
                self.log("ATTACK TO: %s", str(state["position"]))
                return self.attack(energy)

        # Mover aleatoriamente
        moves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))

        # Determinar movimientos válidos
        moves = [(x, y) for x, y in moves if self.map[cy + y][cx + x]]
        move = random.choice(moves)
        self.log("MOVE TO HARVEST: %s", str(move))

        return self.move(move[0], move[1])
