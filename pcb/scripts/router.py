"""A small two-layer maze router.

KiCad ships no scriptable autorouter, so this does the job: an 8-way A* on a
0.1 mm grid, routing each net as a minimum spanning tree of its pads, with
vias costed high enough that the router prefers to stay on one layer.

Grid cells carry three labels per layer:
    occ  - hard copper (pad body or finished track), -1 free, -2 wall
    clr  - clearance halo sized for a 0.25 mm track approaching
    clrv - clearance halo sized for a 0.6 mm via or a wide power/RF track
A cell is passable for net N only if every label is free or already N.

Halos must record conflict, not just the first writer: if net A and net B both
claim a cell the label becomes MULTI and neither may route there.  Storing only
the first writer lets a net's own pad halo mask a neighbour's halo, which reads
as free space and lands a via on top of someone else's track.
"""
import heapq
import numpy as np

WALL = -2
FREE = -1
MULTI = -3      # halo claimed by two or more different nets -> nobody may route here

# 8-way moves: (dx, dy, cost).  Diagonals give 45-degree track runs.
MOVES = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
         (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142), (-1, -1, 1.4142)]
VIA_COST = 40.0          # in grid units; ~4 mm of track, so vias stay rare


def _claim(sub, code):
    """Add net `code` to a halo region, marking multi-net cells as MULTI."""
    free = sub == FREE
    other = (~free) & (sub != code)
    sub[free] = code
    sub[other] = MULTI


class Grid:
    def __init__(self, w_mm, h_mm, res=0.1, layers=2):
        self.res = res
        self.nx = int(round(w_mm / res)) + 1
        self.ny = int(round(h_mm / res)) + 1
        self.nl = layers
        self.occ = np.full((layers, self.nx, self.ny), FREE, dtype=np.int16)
        # two halo levels: clr sized for a 0.25 mm track approaching, clrv sized
        # for a 0.6 mm via or a wide power/RF track.  Without the second level a
        # via can legally land half-way inside another net's track.
        self.clr = np.full((layers, self.nx, self.ny), FREE, dtype=np.int16)
        self.clrv = np.full((layers, self.nx, self.ny), FREE, dtype=np.int16)
        # drills ignore nets: two holes may not overlap even on the same net,
        # so via placement needs its own keep-out map
        self.hole = np.zeros((self.nx, self.ny), dtype=bool)

    # ---------------------------------------------------------------- stamps
    def _box(self, x0, y0, x1, y1, grow=0.0):
        a = max(0, int(np.floor((x0 - grow) / self.res)))
        b = max(0, int(np.floor((y0 - grow) / self.res)))
        c = min(self.nx - 1, int(np.ceil((x1 + grow) / self.res)))
        d = min(self.ny - 1, int(np.ceil((y1 + grow) / self.res)))
        return a, b, c, d

    def stamp_rect(self, layers, x0, y0, x1, y1, code, halo=0.0, halo_v=0.0):
        a, b, c, d = self._box(x0, y0, x1, y1)
        for l in layers:
            self.occ[l, a:c + 1, b:d + 1] = code
        for h, arr in ((halo, self.clr), (halo_v, self.clrv)):
            if not h:
                continue
            a, b, c, d = self._box(x0, y0, x1, y1, h)
            for l in layers:
                _claim(arr[l, a:c + 1, b:d + 1], code)

    def stamp_seg(self, layer, p, q, width, code, halo, halo_v=None):
        """Stamp a track segment (grid coords) as copper + both halo levels."""
        if halo_v is None:
            halo_v = halo + 0.325
        rw = width / 2.0 / self.res
        rh = (width / 2.0 + halo) / self.res
        rv = (width / 2.0 + halo_v) / self.res
        n = max(abs(q[0] - p[0]), abs(q[1] - p[1])) + 1
        for t in np.linspace(0.0, 1.0, int(n) * 2 + 1):
            cx = p[0] + (q[0] - p[0]) * t
            cy = p[1] + (q[1] - p[1]) * t
            for r, arr in ((rv, self.clrv), (rh, self.clr), (rw, self.occ)):
                a = max(0, int(cx - r)); c = min(self.nx - 1, int(np.ceil(cx + r)))
                b = max(0, int(cy - r)); d = min(self.ny - 1, int(np.ceil(cy + r)))
                if arr is self.occ:
                    arr[layer, a:c + 1, b:d + 1] = code
                else:
                    _claim(arr[layer, a:c + 1, b:d + 1], code)

    def stamp_hole(self, cx, cy, radius):
        a, b, c, d = self._box(cx, cy, cx, cy, radius)
        self.hole[a:c + 1, b:d + 1] = True

    def to_grid(self, x, y):
        return (int(round(x / self.res)), int(round(y / self.res)))

    def to_mm(self, ix, iy):
        return (ix * self.res, iy * self.res)

    # ---------------------------------------------------------------- search
    def passable(self, l, ix, iy, net, heavy=False):
        o = self.occ[l, ix, iy]
        if o != FREE and o != net:
            return False
        c = self.clr[l, ix, iy]
        if c != FREE and c != net:
            return False
        if heavy:
            c = self.clrv[l, ix, iy]
            return c == FREE or c == net
        return True

    def route(self, sources, targets, net, via_cost=VIA_COST, heavy=False):
        """Multi-source -> multi-target A*.  Returns [(layer, ix, iy), ...] or None."""
        tset = set(targets)
        if not tset or not sources:
            return None
        tx = sum(t[1] for t in tset) / len(tset)
        ty = sum(t[2] for t in tset) / len(tset)

        def h(ix, iy):
            dx, dy = abs(ix - tx), abs(iy - ty)
            return (dx + dy) - 0.586 * min(dx, dy)

        dist = {}
        prev = {}
        pq = []
        for s in sources:
            if s in tset:
                return [s]
            dist[s] = 0.0
            heapq.heappush(pq, (h(s[1], s[2]), 0.0, s))
        while pq:
            f, g, cur = heapq.heappop(pq)
            if g > dist.get(cur, 1e18):
                continue
            if cur in tset:
                path = [cur]
                while path[-1] in prev:
                    path.append(prev[path[-1]])
                return path[::-1]
            l, ix, iy = cur
            for dx, dy, c in MOVES:
                nx_, ny_ = ix + dx, iy + dy
                if not (0 <= nx_ < self.nx and 0 <= ny_ < self.ny):
                    continue
                if not self.passable(l, nx_, ny_, net, heavy):
                    continue
                if dx and dy:      # do not cut corners diagonally
                    if not (self.passable(l, ix + dx, iy, net, heavy) and
                            self.passable(l, ix, iy + dy, net, heavy)):
                        continue
                nxt = (l, nx_, ny_)
                ng = g + c
                if ng < dist.get(nxt, 1e18):
                    dist[nxt] = ng
                    prev[nxt] = cur
                    heapq.heappush(pq, (ng + h(nx_, ny_), ng, nxt))
            if self.hole[ix, iy]:            # no via on top of another drill
                continue
            for l2 in range(self.nl):        # via: both layers, heavy halo
                if l2 == l or not self.passable(l2, ix, iy, net, True):
                    continue
                if not self.passable(l, ix, iy, net, True):
                    continue
                nxt = (l2, ix, iy)
                ng = g + via_cost
                if ng < dist.get(nxt, 1e18):
                    dist[nxt] = ng
                    prev[nxt] = cur
                    heapq.heappush(pq, (ng + h(ix, iy), ng, nxt))
        return None


def path_to_segments(path):
    """Collapse a cell path into (layer, (x0,y0), (x1,y1)) runs plus via points."""
    segs, vias = [], []
    i = 0
    while i < len(path) - 1:
        l, x, y = path[i]
        l2, x2, y2 = path[i + 1]
        if l2 != l:
            vias.append((x, y))
            i += 1
            continue
        dx, dy = np.sign(x2 - x), np.sign(y2 - y)
        j = i + 1
        while j < len(path) - 1:
            la, xa, ya = path[j]
            lb, xb, yb = path[j + 1]
            if lb != la or np.sign(xb - xa) != dx or np.sign(yb - ya) != dy:
                break
            j += 1
        segs.append((l, (path[i][1], path[i][2]), (path[j][1], path[j][2])))
        i = j
    return segs, vias


def mst_order(points):
    """Prim's algorithm over pad groups; yields (from_group, to_group) pairs."""
    n = len(points)
    if n < 2:
        return []
    inside = {0}
    order = []
    while len(inside) < n:
        best = None
        for a in inside:
            for b in range(n):
                if b in inside:
                    continue
                d = min((px - qx) ** 2 + (py - qy) ** 2
                        for px, py in points[a] for qx, qy in points[b])
                if best is None or d < best[0]:
                    best = (d, a, b)
        order.append((best[1], best[2]))
        inside.add(best[2])
    return order
