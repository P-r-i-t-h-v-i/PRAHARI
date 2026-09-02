"""Build PRAHARI.kicad_pcb: outline, placement, nets, routing, ground pours."""
import os, sys, math, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew as P
import design as D
import router as R

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, ".."))
KI = os.path.join(os.environ["LOCALAPPDATA"], "Programs", "KiCad", "10.0", "share", "kicad")
STOCK_FP = os.path.join(KI, "footprints")
LOCAL_FP = os.path.join(PROJ, "PRAHARI.pretty")
PCB = os.path.join(PROJ, "PRAHARI.kicad_pcb")

mm, tomm = P.FromMM, P.ToMM
OX, OY = D.ORIGIN
W, H = D.BOARD_W, D.BOARD_H
GRID_RES = 0.1
LAYERS = [P.F_Cu, P.B_Cu]          # grid layer 0 -> F.Cu, 1 -> B.Cu

TRACK_W = {"ANT": 0.9, "+3V3": 0.5, "VBAT": 0.5, "MOTOR_N": 0.5}
CLEAR = {"ANT": 0.35, "+3V3": 0.25, "VBAT": 0.25, "MOTOR_N": 0.25}
DEF_W, DEF_CLR = 0.25, 0.2


def V(x, y):
    return P.VECTOR2I(mm(OX + x), mm(OY + y))


def rel(v):                         # board VECTOR2I -> board-relative mm
    return (tomm(v.x) - OX, tomm(v.y) - OY)


def lib_path(fpid):
    lib, name = fpid.split(":")
    return (LOCAL_FP if lib == "PRAHARI" else os.path.join(STOCK_FP, lib + ".pretty")), name


# ===================================================================== board
board = P.NewBoard(PCB)
board.SetCopperLayerCount(2)
board.GetDesignSettings().SetBoardThickness(mm(1.6))
for name in D.NETS:
    board.Add(P.NETINFO_ITEM(board, name))

# --------------------------------------------------------------- edge cuts
r = D.CORNER_R


def edge_line(x1, y1, x2, y2):
    s = P.PCB_SHAPE(board, P.SHAPE_T_SEGMENT)
    s.SetStart(V(x1, y1)); s.SetEnd(V(x2, y2))
    s.SetLayer(P.Edge_Cuts); s.SetWidth(mm(0.1)); board.Add(s)


def edge_arc(cx, cy, a0, a1):
    s = P.PCB_SHAPE(board, P.SHAPE_T_ARC)
    sa, ea = math.radians(a0), math.radians(a1)
    s.SetStart(V(cx + r * math.cos(sa), cy + r * math.sin(sa)))
    s.SetEnd(V(cx + r * math.cos(ea), cy + r * math.sin(ea)))
    s.SetCenter(V(cx, cy))
    s.SetLayer(P.Edge_Cuts); s.SetWidth(mm(0.1)); board.Add(s)


edge_line(r, 0, W - r, 0); edge_line(r, H, W - r, H)
edge_line(0, r, 0, H - r); edge_line(W, r, W, H - r)
edge_arc(r, r, 180, 270); edge_arc(W - r, r, 270, 360)
edge_arc(W - r, H - r, 0, 90); edge_arc(r, H - r, 90, 180)

# ------------------------------------------------------------- place parts
placed = {}
for ref, (fpid, val, x, y, rot, side, descr) in D.COMPONENTS.items():
    lib, name = lib_path(fpid)
    fp = P.FootprintLoad(lib, name)
    if fp is None:
        raise SystemExit(f"could not load {fpid}")
    board.Add(fp)
    fp.SetPosition(V(x, y))
    if rot:
        fp.SetOrientation(P.EDA_ANGLE(rot, P.DEGREES_T))
    if side == "B":
        fp.Flip(V(x, y), False)
    fp.SetReference(ref); fp.SetValue(val); fp.SetLibDescription(descr)
    # FootprintLoad() drops the library nickname, but schematic parity compares
    # the board's footprint id against the symbol's Footprint field.
    fp.SetFPIDAsString(fpid)
    fp.SetField("Description", descr)
    placed[ref] = fp

# ------------------------------------------------------------- assign nets
pad_index = {}
for ref, fp in placed.items():
    for pad in fp.Pads():
        pad_index.setdefault((ref, pad.GetNumber()), []).append(pad)
missing = []
for net, conns in D.NETS.items():
    ni = board.FindNet(net)
    for ref, padnum in conns:
        pads = pad_index.get((ref, padnum))
        if not pads:
            missing.append(f"{ref}.{padnum}")
        for pad in pads or []:
            pad.SetNet(ni)
if missing:
    raise SystemExit("no such pads: " + ", ".join(missing))

# ------------------------------------------------------- placement checking
def crt_bbox(fp):
    poly = fp.GetCourtyard(P.B_CrtYd if fp.IsFlipped() else P.F_CrtYd)
    b = poly.BBox() if (poly and poly.OutlineCount()) else fp.GetBoundingBox(False, False)
    return (tomm(b.GetLeft()) - OX, tomm(b.GetTop()) - OY,
            tomm(b.GetRight()) - OX, tomm(b.GetBottom()) - OY)


problems = []
boxes = {k: crt_bbox(v) for k, v in placed.items()}
ks = list(boxes)
for i in range(len(ks)):
    for j in range(i + 1, len(ks)):
        if placed[ks[i]].IsFlipped() != placed[ks[j]].IsFlipped():
            continue                      # opposite sides cannot collide
        a, b = boxes[ks[i]], boxes[ks[j]]
        if min(a[2], b[2]) - max(a[0], b[0]) > 0.001 and min(a[3], b[3]) - max(a[1], b[1]) > 0.001:
            problems.append(f"OVERLAP {ks[i]}/{ks[j]}")
for k, b in boxes.items():
    if b[0] < -0.01 or b[1] < -0.01 or b[2] > W + .01 or b[3] > H + .01:
        problems.append(f"OFF-BOARD {k}")
print(f"placed {len(placed)} footprints, {len(D.NETS)} nets"
      + ("  PROBLEMS: " + ", ".join(problems) if problems else "  (placement clean)"))

# =================================================================== routing
grid = R.Grid(W, H, GRID_RES, 2)

# board edge wall: 0.3 mm edge rule + half of the widest track (0.9 mm RF)
EDGE_KEEP = 0.75
m = int(EDGE_KEEP / GRID_RES)
for l in (0, 1):
    grid.occ[l, :m, :] = R.WALL; grid.occ[l, -m:, :] = R.WALL
    grid.occ[l, :, :m] = R.WALL; grid.occ[l, :, -m:] = R.WALL
# rounded corners
for (cx, cy) in [(r, r), (W - r, r), (r, H - r), (W - r, H - r)]:
    for ix in range(grid.nx):
        for iy in range(grid.ny):
            x, y = ix * GRID_RES, iy * GRID_RES
            if ((x < r) == (cx < W / 2)) and ((y < r) == (cy < H / 2)):
                if (x - cx) ** 2 + (y - cy) ** 2 > (r - EDGE_KEEP) ** 2 and \
                   (abs(x - cx) < r and abs(y - cy) < r):
                    grid.occ[0, ix, iy] = R.WALL; grid.occ[1, ix, iy] = R.WALL

# solid ground reference under the LoRa module: no routing there
u2x, u2y = D.COMPONENTS["U2"][2], D.COMPONENTS["U2"][3]
grid.stamp_rect([0, 1], u2x - 8.0, u2y - 6.5, u2x + 8.0, u2y + 6.5, R.WALL)

# stamp every pad
GNDCODE = board.FindNet("GND").GetNetCode()
pad_targets = {}
for ref, fp in placed.items():
    for pad in fp.Pads():
        bb = pad.GetBoundingBox()
        x0, y0 = tomm(bb.GetLeft()) - OX, tomm(bb.GetTop()) - OY
        x1, y1 = tomm(bb.GetRight()) - OX, tomm(bb.GetBottom()) - OY
        att = pad.GetAttribute()
        if att in (P.PAD_ATTRIB_PTH, P.PAD_ATTRIB_NPTH):
            dr = max(tomm(pad.GetDrillSizeX()), tomm(pad.GetDrillSizeY())) / 2
            px, py = rel(pad.GetPosition())
            grid.stamp_hole(px, py, dr + 0.25 + 0.15)
        if att == P.PAD_ATTRIB_NPTH:
            grid.stamp_rect([0, 1], x0, y0, x1, y1, R.WALL, 0.4)
            continue
        ls = [0, 1] if att in (P.PAD_ATTRIB_PTH,) else \
             ([0] if pad.IsOnLayer(P.F_Cu) else [1])
        code = pad.GetNetCode() if pad.GetNetCode() > 0 else R.WALL
        grid.stamp_rect(ls, x0, y0, x1, y1, code,
                        DEF_CLR + DEF_W / 2, DEF_CLR + 0.45)
        if code > 0:
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            # inscribe the target box inside the pad: the corners of a
            # circumscribed box fall outside a round pad, and a track ending
            # there lands on bare laminate.
            hw = max((x1 - x0) * 0.28, 0.05); hh = max((y1 - y0) * 0.28, 0.05)
            a, b_, c, d = grid._box(cx - hw, cy - hh, cx + hw, cy + hh)
            cells = [(l, ix, iy) for l in ls
                     for ix in range(a, c + 1) for iy in range(b_, d + 1)]
            pad_targets.setdefault(pad.GetNetname(), []).append(
                (cells, (cx, cy)))

# ------------------------------------------------------------- route order
def net_span(name):
    pts = [p[1] for p in pad_targets.get(name, [])]
    if len(pts) < 2:
        return 0
    return max(abs(a[0] - b[0]) + abs(a[1] - b[1]) for a in pts for b in pts)


routable = [n for n in D.NETS if n != "GND" and len(pad_targets.get(n, [])) > 1]
# BAT_NEG is the cell-negative leg: it crosses the board from J4 to the
# protection FETs, so sorting by span would route it last, after the short
# local nets have boxed in the SOT-23-6 pads.  Route it with the other
# power paths instead.
priority = ["ANT", "VBAT", "BAT_NEG", "+3V3"]
order = priority + sorted([n for n in routable if n not in priority], key=net_span)
order = [n for n in order if n in routable]

tracks = vias = 0
failed = []
t0 = time.time()
for name in order:
    ni = board.FindNet(name)
    code = ni.GetNetCode()
    width = TRACK_W.get(name, DEF_W)
    clr = CLEAR.get(name, DEF_CLR)
    groups = pad_targets[name]
    pts = [[g[1]] for g in groups]
    connected = set(groups[0][0])
    remaining = list(range(1, len(groups)))
    # greedily attach the nearest remaining pad to the growing tree
    while remaining:
        cx, cy = None, None
        best = min(remaining, key=lambda i:
                   min((groups[i][1][0] - groups[j][1][0]) ** 2 +
                       (groups[i][1][1] - groups[j][1][1]) ** 2
                       for j in range(len(groups)) if j not in remaining))
        path = grid.route(sorted(connected), groups[best][0], code,
                          heavy=(width > DEF_W))
        if path is None:
            failed.append(f"{name}->pad{best}")
            remaining.remove(best)
            continue
        segs, vps = R.path_to_segments(path)
        for l, p, q in segs:
            if p == q:
                continue
            t = P.PCB_TRACK(board)
            t.SetStart(V(*grid.to_mm(*p))); t.SetEnd(V(*grid.to_mm(*q)))
            t.SetWidth(mm(width)); t.SetLayer(LAYERS[l]); t.SetNet(ni)
            board.Add(t); tracks += 1
            grid.stamp_seg(l, p, q, width, code, clr + DEF_W / 2, clr + 0.45)
        for vp in vps:
            v = P.PCB_VIA(board)
            v.SetPosition(V(*grid.to_mm(*vp)))
            v.SetViaType(P.VIATYPE_THROUGH)
            v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3))
            v.SetLayerPair(P.F_Cu, P.B_Cu); v.SetNet(ni)
            board.Add(v); vias += 1
            grid.stamp_hole(*grid.to_mm(*vp), 0.15 + 0.25 + 0.15)
            for l in (0, 1):
                grid.stamp_seg(l, vp, vp, 0.6, code, clr + DEF_W / 2, clr + 0.45)
        connected |= set(path)
        connected |= set(groups[best][0])
        remaining.remove(best)

print(f"routed {len(order)} nets -> {tracks} tracks, {vias} vias "
      f"in {time.time() - t0:.1f}s" + (f"  FAILED: {failed}" if failed else "  (all connected)"))

# ============================================================= ground pours
gnd = board.FindNet("GND")
for layer in (P.F_Cu, P.B_Cu):
    z = P.ZONE(board)
    board.Add(z)
    z.SetLayer(layer)
    z.SetNet(gnd)
    z.SetAssignedPriority(0)
    z.SetLocalClearance(mm(0.25))
    z.SetMinThickness(mm(0.2))
    z.SetThermalReliefGap(mm(0.3))
    z.SetThermalReliefSpokeWidth(mm(0.5))
    z.SetPadConnection(P.ZONE_CONNECTION_THERMAL)
    # Delete pour islands outright rather than keep and flag them: routing
    # leaves slivers between adjacent header pins that are too narrow to take a
    # stitching via, and the pads they sit between are plated through, so they
    # reach the other layer's plane regardless.
    z.SetIslandRemovalMode(P.ISLAND_REMOVAL_MODE_ALWAYS)
    chain = P.SHAPE_LINE_CHAIN()
    g = 0.3
    for (x, y) in [(r, g), (W - r, g), (W - g, r), (W - g, H - r),
                   (W - r, H - g), (r, H - g), (g, H - r), (g, r)]:
        chain.Append(V(x, y))
    chain.SetClosed(True)
    z.Outline().AddOutline(chain)

# ground stitching vias on a 3.5 mm lattice wherever both layers are clear:
# ties the pours together and starves the router's leftover pour fragments
stitched = 0
for sx in [x * 0.5 for x in range(4, 2 * int(W) - 3)]:
    for sy in [y * 0.5 for y in range(4, 2 * int(H) - 3)]:
        if (round(sx * 2) % 5) or (round(sy * 2) % 5):
            continue
        ix, iy = grid.to_grid(sx, sy)
        if grid.hole[ix, iy]:
            continue
        if grid.passable(0, ix, iy, GNDCODE, True) and grid.passable(1, ix, iy, GNDCODE, True):
            v = P.PCB_VIA(board)
            v.SetPosition(V(sx, sy)); v.SetViaType(P.VIATYPE_THROUGH)
            v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3))
            v.SetLayerPair(P.F_Cu, P.B_Cu); v.SetNet(gnd)
            board.Add(v); stitched += 1
            grid.stamp_hole(sx, sy, 0.15 + 0.25 + 0.15)
            grid.stamp_seg(0, (ix, iy), (ix, iy), 0.6, GNDCODE, 0.375, 0.70)
            grid.stamp_seg(1, (ix, iy), (ix, iy), 0.6, GNDCODE, 0.375, 0.70)
print(f"{stitched} ground stitching vias")

# ============================================================== silkscreen
def silk(text, x, y, size=0.8, layer=P.F_SilkS, rot=0, thick=0.13):
    t = P.PCB_TEXT(board)
    t.SetText(text); t.SetPosition(V(x, y)); t.SetLayer(layer)
    t.SetTextSize(P.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(thick))
    if rot:
        t.SetTextAngle(P.EDA_ANGLE(rot, P.DEGREES_T))
    if layer == P.B_SilkS:
        t.SetMirrored(True)
    board.Add(t)
    return t


silk("PRAHARI  rev B", 39.5, 1.7, 0.8)
# J6 sits at (12, 2.5) since ANT moved to pad 1 of the radio.  Keep these
# labels clear of the two header pads or DRC reports silk_over_copper.
silk("ANT", 8.6, 5.0, 0.8)
silk("GND", 8.6, 2.5, 0.8)
# the front is crowded; the descriptive block goes on the empty back silkscreen
silk("PRAHARI - The Countdown Band", 32.0, 16.0, 1.0, layer=P.B_SilkS)
silk("Point Break - SIH 2026 - PS 26181", 32.0, 18.5, 0.8, layer=P.B_SilkS)
silk("rev B - 70 x 40 mm - 2 layer - 868 MHz", 32.0, 21.0, 0.8, layer=P.B_SilkS)

# sensor-header pin legends, set vertical so 0.8 mm text fits a 2.54 mm pitch
LEGEND = {
    "J1": ["3V3", "GND", "SCL", "SDA", "INT", "IRD", "RD"],
    "J2": ["3V3", "GND", "SCL", "SDA"],
    "J3": ["3V3", "GND", "SCL", "SDA"],
    "J7": ["3V3", "GND", "SCL", "SDA"],
}
for ref, names in LEGEND.items():
    for pad in placed[ref].Pads():
        i = int(pad.GetNumber()) - 1
        if i < len(names):
            x, y = rel(pad.GetPosition())
            silk(names[i], x, y - 2.6, 0.8, rot=90)

# test-point labels sit above their pad
for ref in ("TP1", "TP2", "TP3", "TP4", "TP5", "TP6"):
    x, y = rel(placed[ref].GetPosition())
    silk(D.COMPONENTS[ref][1], x, y - 2.3, 0.8)

# battery / motor polarity, marked directly over each pad
for ref in ("J4", "J5"):
    for pad in placed[ref].Pads():
        x, y = rel(pad.GetPosition())
        silk("+" if pad.GetNumber() == "1" else "-", x, y - 2.0, 0.8)

# silk hygiene: holes and test points carry their own labels, and the two caps
# at the top edge would have their reference clipped by the board outline.
for ref in ("MH1", "MH2", "MH3", "MH4", "TP1", "TP2", "TP3",
            "TP4", "TP5", "TP6", "J6"):
    placed[ref].Reference().SetVisible(False)
for ref, dx in (("C1", 2.6), ("C3", -3.0)):
    fp = placed[ref]
    fp.Reference().SetPosition(P.VECTOR2I(fp.GetPosition().x + mm(dx),
                                          fp.GetPosition().y))


# --------------------------------------------- reference designator placement
# Small parts sit close together here, so the default refdes position lands on a
# neighbour's silk or over an exposed pad.  Nudge each one to the first spot that
# is clear of pads, other silk and the board edge.
def bb(item):
    b = item.GetBoundingBox()
    return (tomm(b.GetLeft()) - OX, tomm(b.GetTop()) - OY,
            tomm(b.GetRight()) - OX, tomm(b.GetBottom()) - OY)


def hits(a, b, gap=0.18):
    return (min(a[2], b[2]) - max(a[0], b[0]) > -gap and
            min(a[3], b[3]) - max(a[1], b[1]) > -gap)


static = []
for fp in placed.values():
    for pad in fp.Pads():
        if pad.IsOnLayer(P.F_Cu):
            static.append(bb(pad))
    for g in fp.GraphicalItems():
        if g.GetLayer() == P.F_SilkS:
            static.append(bb(g))
for d in board.GetDrawings():
    if d.GetLayer() == P.F_SilkS:
        static.append(bb(d))

OFFSETS = [(0, -1.5), (0, 1.5), (-2.4, 0), (2.4, 0), (0, -2.3), (0, 2.3),
           (-3.2, 0), (3.2, 0), (-2.6, -1.8), (2.6, -1.8), (-2.6, 1.8),
           (2.6, 1.8), (0, -3.1), (0, 3.1), (-4.2, 0), (4.2, 0),
           (-4.0, -2.6), (4.0, -2.6), (-4.0, 2.6), (4.0, 2.6),
           (0, -4.0), (0, 4.0), (-5.4, 0), (5.4, 0), (-5.0, -3.4), (5.0, -3.4),
           (-5.0, 3.4), (5.0, 3.4), (0, -5.0), (0, 5.0), (-6.6, 0), (6.6, 0)]

moved = unresolved = 0
for ref in sorted(placed, key=lambda k: -len(k)):
    fp = placed[ref]
    field = fp.Reference()
    if not field.IsVisible() or fp.IsFlipped():
        continue
    ox_, oy_ = rel(fp.GetPosition())
    best = None
    for dx, dy in OFFSETS:
        field.SetPosition(V(ox_ + dx, oy_ + dy))
        box = bb(field)
        if box[0] < 0.3 or box[1] < 0.3 or box[2] > W - 0.3 or box[3] > H - 0.3:
            continue
        if any(hits(box, o) for o in static):
            continue
        best = (dx, dy)
        break
    if best is None:
        # nothing is fully clear; take the first candidate that is at least
        # on the board rather than letting it fall off the edge
        unresolved += 1
        for dx, dy in OFFSETS:
            field.SetPosition(V(ox_ + dx, oy_ + dy))
            box = bb(field)
            if (box[0] > 0.3 and box[1] > 0.3
                    and box[2] < W - 0.3 and box[3] < H - 0.3):
                break
    else:
        moved += 1
        field.SetPosition(V(ox_ + best[0], oy_ + best[1]))
        static.append(bb(field))
print(f"reference designators: {moved} placed clear, {unresolved} unresolved")

# ----------------------------------------------------------------- zone fill
board.Save(PCB)
print("saved", os.path.basename(PCB))

# Reload before filling: netclass clearances and the DRC constraints live in
# PRAHARI.kicad_pro, and only get applied to a board that is loaded from disk.
# Filling the in-memory board instead fills to plain defaults.
board = P.LoadBoard(PCB)
gnd = board.FindNet("GND")
zones = {z.GetLayer(): z for z in board.Zones()}
P.ZONE_FILLER(board).Fill(board.Zones())


def add_via(x, y):
    v = P.PCB_VIA(board)
    v.SetPosition(V(x, y)); v.SetViaType(P.VIATYPE_THROUGH)
    v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3))
    v.SetLayerPair(P.F_Cu, P.B_Cu); v.SetNet(gnd)
    board.Add(v)


# GND carries no tracks, only pours, so every GND via is a stitching via: drop
# the ones that did not land inside the fill on both layers.
dropped = 0
for t in list(board.Tracks()):
    if not isinstance(t, P.PCB_VIA) or t.GetNetname() != "GND":
        continue
    pos = t.GetPosition()
    if not all(zones[l].HitTestFilledArea(l, pos) for l in (P.F_Cu, P.B_Cu)):
        board.Remove(t)
        dropped += 1
if dropped:
    P.ZONE_FILLER(board).Fill(board.Zones())

# Routing splits the pour into regions.  A region with no via and no GND pad is
# copper that floats: find one and stitch it back to the other layer's plane.
rescued = 0
for _pass in range(4):
    added = False
    vias = [t.GetPosition() for t in board.Tracks()
            if isinstance(t, P.PCB_VIA) and t.GetNetname() == "GND"]
    # Only a plated-through GND pad ties a pour region to the other layer's
    # plane.  An SMD pad does not: a region whose only GND contact is an SMD pad
    # is floating copper, and the part on that pad is floating with it.
    gnd_pads = [p.GetPosition() for f in board.GetFootprints() for p in f.Pads()
                if p.GetNetname() == "GND"
                and p.GetAttribute() in (P.PAD_ATTRIB_PTH,)]
    for l in (P.F_Cu, P.B_Cu):
        other = P.B_Cu if l == P.F_Cu else P.F_Cu
        poly = zones[l].GetFilledPolysList(l)
        for i in range(poly.OutlineCount()):
            o = poly.Outline(i)
            if abs(o.Area()) / 1e12 < 1.2:          # nm^2 -> mm^2
                continue
            if any(o.PointInside(v) for v in vias) or                any(o.PointInside(q) for q in gnd_pads):
                continue
            bx = o.BBox()
            x0, y0 = tomm(bx.GetLeft()) - OX, tomm(bx.GetTop()) - OY
            x1, y1 = tomm(bx.GetRight()) - OX, tomm(bx.GetBottom()) - OY
            spot = None
            yy = y0
            while yy <= y1 and spot is None:
                xx = x0
                while xx <= x1:
                    ix, iy = grid.to_grid(xx, yy)
                    if (0 <= ix < grid.nx and 0 <= iy < grid.ny
                            and o.PointInside(V(xx, yy))
                            and zones[other].HitTestFilledArea(other, V(xx, yy))
                            and not grid.hole[ix, iy]
                            and grid.passable(0, ix, iy, GNDCODE, True)
                            and grid.passable(1, ix, iy, GNDCODE, True)):
                        spot = (xx, yy)
                        break
                    xx += 0.25
                yy += 0.25
            if spot:
                add_via(*spot)
                grid.stamp_hole(spot[0], spot[1], 0.55)
                rescued += 1
                added = True
    if not added:
        break
    P.ZONE_FILLER(board).Fill(board.Zones())

board.Save(PCB)
print(f"ground pours filled: {dropped} unreached stitching vias dropped, "
      f"{rescued} floating pour regions stitched back")
