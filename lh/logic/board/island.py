from lh.logic.utils.geom import distt


class Island(object):
    MAX_ENERGY = 100
    HORIZON = 3

    def __init__(self, island_map):
        self._island = island_map
        self.h = len(self._island)
        self.w = len(self._island[0])
        self._energymap = [[0] * self.w for _ in range(self.h)]
        self._horizonmap = []
        dist = self.HORIZON
        for y in range(-dist, dist + 1):
            row = []
            for x in range(-dist, dist + 1):
                row.append(distt((0, 0), (x, y)) <= self.HORIZON)
            self._horizonmap.append(row)

        class _Energy(object):
            def __getitem__(unused, pos):
                xx, yy = pos
                if self[pos]:
                    return self._energymap[yy][xx]
                else:
                    return 0

            def __setitem__(unused, pos, val):
                xx, yy = pos
                if val > Island.MAX_ENERGY:
                    val = Island.MAX_ENERGY
                assert val >= 0
                if self[pos]:
                    self._energymap[yy][xx] = val

        self._energy = _Energy()

    def __getitem__(self, pos):
        x, y = pos
        if 0 <= x < self.w and 0 <= y < self.h:
            return self._island[y][x]
        else:
            return False

    @property
    def energy(self):
        return self._energy

    def get_view(self, pos):
        px, py = pos
        dist = self.HORIZON
        view = []
        for y in range(-dist, dist + 1):
            row = []
            for x in range(-dist, dist + 1):
                if self._horizonmap[y + dist][x + dist]:
                    row.append(self.energy[px + x, py + y])
                else:
                    row.append(-1)
            view.append(row)
        return view

    @property
    def map(self):
        return self._island
