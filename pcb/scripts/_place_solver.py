"""Offline placement checker/searcher. Temporary - delete after use.

Reads each footprint's courtyard from its .kicad_mod, transforms it by the
position and rotation in design.COMPONENTS, and reports overlapping pairs on the
same side.  This runs in milliseconds, so candidate placements can be searched
without paying for a route + DRC cycle each time.
"""
import io, os, re, sys, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import design as D

LOCAL = os.environ.get("LOCALAPPDATA", "")
KFP = os.path.join(LOCAL, "Programs", "KiCad", "10.0", "share", "kicad", "footprints")
PRETTY = os.path.join(PROJ, "PRAHARI.pretty")

_cache = {}


def fp_path(fpid):
    lib, name = fpid.split(":", 1)
    if lib == "PRAHARI":
        return os.path.join(PRETTY, name + ".kicad_mod")
    return os.path.join(KFP, lib + ".pretty", name + ".kicad_mod")


def courtyard_bbox(fpid):
    """(xmin, ymin, xmax, ymax) of the courtyard in footprint-local mm."""
    if fpid in _cache:
        return _cache[fpid]
    p = fp_path(fpid)
    if not os.path.isfile(p):
        _cache[fpid] = None
        return None
    s = io.open(p, encoding="utf-8", errors="replace").read()
    xs, ys = [], []
    # rects
    for m in re.finditer(r'\(fp_rect\s*\(start ([-\d.]+) ([-\d.]+)\)\s*\(end ([-\d.]+) ([-\d.]+)\)'
                         r'(?:(?!\(fp_).)*?\(layer "([^"]+)"', s, re.S):
        if "CrtYd" in m.group(5):
            xs += [float(m.group(1)), float(m.group(3))]
            ys += [float(m.group(2)), float(m.group(4))]
    # lines / polys
    for m in re.finditer(r'\(fp_(?:line|poly)((?:(?!\(fp_).)*?)\(layer "([^"]+)"', s, re.S):
        if "CrtYd" not in m.group(2):
            continue
        for xy in re.finditer(r'\(xy ([-\d.]+) ([-\d.]+)\)|\((?:start|end) ([-\d.]+) ([-\d.]+)\)',
                              m.group(1)):
            a, b = (xy.group(1), xy.group(2)) if xy.group(1) else (xy.group(3), xy.group(4))
            xs.append(float(a)); ys.append(float(b))
    if not xs:   # no courtyard: fall back to pad extents + 0.25 mm
        for m in re.finditer(r'\(pad "[^"]*"[^\n]*\n?\s*\(at ([-\d.]+) ([-\d.]+)[^)]*\)\s*'
                             r'\(size ([\d.]+) ([\d.]+)\)', s):
            px, py, sx, sy = map(float, m.groups())
            xs += [px - sx / 2 - 0.25, px + sx / 2 + 0.25]
            ys += [py - sy / 2 - 0.25, py + sy / 2 + 0.25]
    _cache[fpid] = (min(xs), min(ys), max(xs), max(ys)) if xs else None
    return _cache[fpid]


def placed_box(ref, override=None):
    fpid, _val, x, y, rot, side, _d = D.COMPONENTS[ref]
    if override and ref in override:
        x, y, rot = override[ref][:3]
        if len(override[ref]) > 3:
            side = override[ref][3]
    bb = courtyard_bbox(fpid)
    if bb is None:
        return None
    x0, y0, x1, y1 = bb
    if rot % 180 == 90:                      # swap axes for 90/270
        x0, y0, x1, y1 = y0, x0, y1, x1
    return (x + x0, y + y0, x + x1, y + y1, side)


def overlaps(override=None, skip_pairs=()):
    boxes = {}
    for ref in D.COMPONENTS:
        b = placed_box(ref, override)
        if b:
            boxes[ref] = b
    bad = []
    for a, b in itertools.combinations(sorted(boxes), 2):
        ax0, ay0, ax1, ay1, as_ = boxes[a]
        bx0, by0, bx1, by1, bs = boxes[b]
        # through-hole parts occupy both sides; treat MH/J/TP conservatively
        both_a = D.COMPONENTS[a][0].split(":")[1].startswith(("PinHeader", "JST", "MountingHole")) \
            or D.COMPONENTS[a][0].startswith("PRAHARI:XIAO")
        both_b = D.COMPONENTS[b][0].split(":")[1].startswith(("PinHeader", "JST", "MountingHole")) \
            or D.COMPONENTS[b][0].startswith("PRAHARI:XIAO")
        if as_ != bs and not (both_a or both_b):
            continue
        if tuple(sorted((a, b))) in skip_pairs:
            continue
        ox = min(ax1, bx1) - max(ax0, bx0)
        oy = min(ay1, by1) - max(ay0, by0)
        if ox > 0 and oy > 0:
            bad.append((a, b, round(ox, 3), round(oy, 3)))
    return bad


def off_board(override=None, margin=0.3):
    out = []
    for ref in D.COMPONENTS:
        b = placed_box(ref, override)
        if not b:
            continue
        x0, y0, x1, y1, _ = b
        if x0 < margin or y0 < margin or x1 > D.BOARD_W - margin or y1 > D.BOARD_H - margin:
            out.append((ref, round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)))
    return out


if __name__ == "__main__":
    print("=== courtyard boxes (as placed) ===")
    for ref in sorted(D.COMPONENTS):
        b = placed_box(ref)
        print("  %-4s %-52s %s" % (ref, D.COMPONENTS[ref][0],
                                   "none" if not b else
                                   "(%6.2f,%6.2f)-(%6.2f,%6.2f) %s" % b))
    print("\n=== overlapping pairs ===")
    ov = overlaps()
    for a, b, ox, oy in ov:
        print("  %s / %s  overlap %.2f x %.2f mm" % (a, b, ox, oy))
    print("  none" if not ov else "  %d pair(s)" % len(ov))
    print("\n=== parts within 0.3 mm of the board edge ===")
    ob = off_board()
    for r in ob:
        print("  %s box (%s,%s)-(%s,%s)" % r)
    print("  none" if not ob else "  %d part(s)" % len(ob))
