class MoveError(Exception):
    pass


class GameError(Exception):
    pass


class CommError(Exception):
    pass


class GameConfig(object):
    def __init__(self, map_file):
        with open(map_file, "r") as fd:
            lines = [l.replace("\n", "") for l in fd.readlines()]

        self.lighthouses = []
        players = []
        self.island = []

        # lighthouses
        for y, line in enumerate(lines[::-1]):
            row = []
            for x, c in enumerate(line):
                if c == "#":
                    row.append(0)
                elif c == "!":
                    row.append(1)
                    self.lighthouses.append((x, y))
                elif c == " ":
                    row.append(1)
                else:
                    row.append(1)
                    players.append((c, (x, y)))
            self.island.append(row)

        # players
        self.players = [(c, pos) for c, pos in sorted(players)]

        # island
        self.width = len(self.island[0])
        self.height = len(self.island)
        if not all(len(l) == self.width for l in self.island):
            raise GameError("All map rows must have the same width")
        if (not all(not i for i in self.island[0]) or
                not all(not i for i in self.island[-1]) or
                not all(not (i[0] or i[-1]) for i in self.island)):
            raise GameError("Map border must not be part of island")
