#!/usr/bin/env python3
"""Route the SP-1 keyboard matrix. Columns on B.Cu, rows on F.Cu."""
import math
import heapq
import uuid
import re
from collections import defaultdict

PCB = "/home/guthman/myCode/feahi_rp2350/hardware/kicad/sp-1/sp-1.kicad_pcb"
RES = 0.2
TRACK = 0.2
CLR = 0.2
HALF = TRACK / 2
TRACK_GAP = CLR + HALF  # track center to foreign copper
EPS = 0.002  # tolerate exact-clearance pad pitch (0.4 mm / 0.2 mm pads)
VIA_R = 0.3
VIA_GAP = VIA_R + CLR  # via center to foreign copper
HOLE_CLR = 0.25
EDGE = 0.5
OX, OY = 50.1, 47.0
X1, Y1 = 149.4, 190.2
NX = int(round((X1 - OX) / RES)) + 1
NY = int(round((Y1 - OY) / RES)) + 1

ROW_NETS = {f"/C6/MAT_R{i}" for i in range(5)} | {"Net-(D37-A)"}
COL_NETS = {f"/C6/MAT_C{i}" for i in range(6)}


def rot(x, y, deg):
    # KiCad applies the opposite of a plain CCW rotation to the stored angle.
    a = math.radians(-deg)
    c, s = math.cos(a), math.sin(a)
    return (x * c - y * s, x * s + y * c)


def dist_rect(px, py, cx, cy, ang_deg, hx, hy):
    dx, dy = px - cx, py - cy
    a = math.radians(ang_deg)
    c, s = math.cos(a), math.sin(a)
    lx = dx * c + dy * s
    ly = -dx * s + dy * c
    ox = abs(lx) - hx
    oy = abs(ly) - hy
    if ox <= 0 and oy <= 0:
        return 0.0
    return math.hypot(max(ox, 0), max(oy, 0))


def parse_board(text):
    parts = re.split(r'\n\t\(footprint "', text)
    pads = []
    keepouts = []
    for p in parts[1:]:
        at = re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', p)
        refm = re.search(r'\(property "Reference" "([^"]+)"', p)
        if not at:
            continue
        fx, fy = float(at.group(1)), float(at.group(2))
        fang = float(at.group(3) or 0)
        ref = refm.group(1) if refm else "?"
        # keepout zones
        idx = 0
        while True:
            k = p.find("(keepout", idx)
            if k < 0:
                break
            chunk = p[max(0, k - 800):k + 2500]
            if "(tracks not_allowed)" in chunk[chunk.find("(keepout"):]:
                pts = [(float(a), float(b)) for a, b in re.findall(
                    r'\(xy ([-\d.]+) ([-\d.]+)\)', chunk[chunk.find("(polygon"):chunk.find("(polygon") + 2000]
                    if "(polygon" in chunk else [])]
                if len(pts) >= 3:
                    # These polygons are already in board coordinates (matches pcbnew).
                    keepouts.append(pts)
            idx = k + 8
        # pads
        pos = 0
        while True:
            i = p.find('\n\t\t(pad ', pos)
            if i < 0:
                break
            # match parens from the pad
            j = p.find("(pad ", i)
            depth = 0
            end = j
            for t in range(j, len(p)):
                if p[t] == '(':
                    depth += 1
                elif p[t] == ')':
                    depth -= 1
                    if depth == 0:
                        end = t + 1
                        break
            body = p[j:end]
            pos = end
            hm = re.match(r'\(pad "([^"]*)" (\S+) (\S+)', body)
            if not hm:
                continue
            name, ptype, shape = hm.group(1), hm.group(2), hm.group(3)
            am = re.search(r'\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', body)
            sm = re.search(r'\(size ([-\d.]+) ([-\d.]+)\)', body)
            if not am or not sm:
                continue
            lx, ly = float(am.group(1)), float(am.group(2))
            pang = float(am.group(3) or 0)
            sx, sy = float(sm.group(1)), float(sm.group(2))
            dm = re.search(r'\(drill (?:oval )?([-\d.]+)(?: ([-\d.]+))?\)', body)
            drill = None
            if dm:
                dw = float(dm.group(1))
                dh = float(dm.group(2) or dw)
                drill = (dw, dh)
            layers = ""
            lm = re.search(r'\(layers ([^)]*)\)', body)
            if lm:
                layers = lm.group(1)
            netm = re.search(r'\(net "([^"]*)"\)', body)
            net = netm.group(1) if netm else ""
            rx, ry = rot(lx, ly, fang)
            ax, ay = fx + rx, fy + ry
            # The angle stored on a board pad is absolute (pcbnew GetOrientation).
            aang = pang
            both = ("*.Cu" in layers) or ("F.Cu" in layers and "B.Cu" in layers) or ptype in ("thru_hole", "np_thru_hole")
            if both:
                lay = 2
            elif "B.Cu" in layers:
                lay = 1
            else:
                lay = 0
            # custom primitive bbox in pad space, axis-aligned in the pad frame
            extra = 0
            if shape == "custom":
                xs, ys = [], []
                for a, b in re.findall(r'\(xy ([-\d.]+) ([-\d.]+)\)', body):
                    xs.append(float(a)); ys.append(float(b))
                if xs:
                    sx = max(sx, (max(xs) - min(xs)))
                    sy = max(sy, (max(ys) - min(ys)))
                    # shift center toward primitive centroid roughly by min/max mid if anchor is center
                    extra = 0.15
            pads.append({
                "ref": ref, "pad": name, "type": ptype, "shape": shape,
                "x": ax, "y": ay, "ang": aang,
                "hx": sx / 2 + extra, "hy": sy / 2 + extra,
                "drill": drill, "lay": lay, "net": net,
                "fx": fx, "fy": fy,
            })
    segs = []
    for m in re.finditer(
        r'\(segment\s+\(start ([-\d.]+) ([-\d.]+)\)\s+\(end ([-\d.]+) ([-\d.]+)\)\s+\(width ([-\d.]+)\)\s+\(layer "([^"]+)"\)\s+\(net "([^"]*)"\)',
        text):
        segs.append({
            "x1": float(m.group(1)), "y1": float(m.group(2)),
            "x2": float(m.group(3)), "y2": float(m.group(4)),
            "w": float(m.group(5)),
            "lay": 0 if m.group(6) == "F.Cu" else 1,
            "net": m.group(7),
        })
    return pads, keepouts, segs


def point_in_poly(x, y, poly):
    n = len(poly)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-15) + xi):
            inside = not inside
        j = i
    return inside


def cell_xy(ix, iy):
    return OX + ix * RES, OY + iy * RES


def idx_of(x, y):
    ix = int(round((x - OX) / RES))
    iy = int(round((y - OY) / RES))
    if 0 <= ix < NX and 0 <= iy < NY:
        return ix, iy
    return None


class World:
    def __init__(self, pads, keepouts, segs):
        self.pads = pads
        self.keepouts = keepouts
        self.segs = list(segs)
        self.vias = []  # {x,y,net}

    def track_hit(self, x, y, lay, ignore_net):
        if x < 49.5 + EDGE + HALF or x > 150 - EDGE - HALF:
            return True
        if y < 46.4 + EDGE + HALF or y > 190.85 - EDGE - HALF:
            return True
        for poly in self.keepouts:
            # inflate roughly by sampling; exact edge checked by poly
            if point_in_poly(x, y, poly):
                return True
        for pad in self.pads:
            if pad["net"] == ignore_net and pad["net"]:
                continue
            if pad["lay"] not in (lay, 2) and pad["type"] != "np_thru_hole":
                # copper only on its layer; hole handled below
                copper = False
            else:
                copper = True
            if copper and pad["type"] != "np_thru_hole":
                if pad["shape"] == "circle" or (pad["hx"] == pad["hy"] and pad["shape"] in ("circle",)):
                    if math.hypot(x - pad["x"], y - pad["y"]) < pad["hx"] + TRACK_GAP - EPS:
                        return True
                else:
                    if dist_rect(x, y, pad["x"], pad["y"], pad["ang"], pad["hx"], pad["hy"]) < TRACK_GAP - EPS:
                        return True
            if pad["drill"]:
                dw, dh = pad["drill"]
                hr = max(dw, dh) / 2 + HOLE_CLR + HALF
                if math.hypot(x - pad["x"], y - pad["y"]) < hr:
                    # own THT ring still needs the hole blocked
                    return True
        for s in self.segs:
            if s["net"] == ignore_net:
                continue
            if s["lay"] != lay:
                continue
            gap = s["w"] / 2 + CLR + HALF
            if dist_seg(x, y, s["x1"], s["y1"], s["x2"], s["y2"]) < gap - EPS:
                return True
        for v in self.vias:
            if v["net"] == ignore_net:
                continue
            if math.hypot(x - v["x"], y - v["y"]) < VIA_R + CLR + HALF - EPS:
                return True
        return False

    def via_hit(self, x, y, ignore_net):
        if x < 49.5 + EDGE + VIA_R or x > 150 - EDGE - VIA_R:
            return True
        if y < 46.4 + EDGE + VIA_R or y > 190.85 - EDGE - VIA_R:
            return True
        for poly in self.keepouts:
            # via center inside or within VIA_R of polygon: sample center and 4 points
            if point_in_poly(x, y, poly):
                return True
            for dx, dy in ((VIA_R, 0), (-VIA_R, 0), (0, VIA_R), (0, -VIA_R)):
                if point_in_poly(x + dx, y + dy, poly):
                    return True
        for pad in self.pads:
            if pad["net"] == ignore_net and pad["net"]:
                continue
            if pad["type"] != "np_thru_hole":
                if pad["shape"] == "circle":
                    d = math.hypot(x - pad["x"], y - pad["y"]) - pad["hx"]
                else:
                    d = dist_rect(x, y, pad["x"], pad["y"], pad["ang"], pad["hx"], pad["hy"])
                if d < VIA_GAP - EPS:
                    return True
            if pad["drill"]:
                dw, dh = pad["drill"]
                hr = max(dw, dh) / 2 + HOLE_CLR + VIA_R
                if math.hypot(x - pad["x"], y - pad["y"]) < hr:
                    return True
        for s in self.segs:
            if s["net"] == ignore_net:
                continue
            gap = s["w"] / 2 + CLR + VIA_R
            if dist_seg(x, y, s["x1"], s["y1"], s["x2"], s["y2"]) < gap - EPS:
                return True
        for v in self.vias:
            if math.hypot(x - v["x"], y - v["y"]) < VIA_R + CLR + VIA_R - EPS:
                return True
        return False


def dist_seg(px, py, x1, y1, x2, y2):
    vx, vy = x2 - x1, y2 - y1
    l2 = vx * vx + vy * vy
    if l2 < 1e-12:
        return math.hypot(px - x1, py - y1)
    t = max(0, min(1, ((px - x1) * vx + (py - y1) * vy) / l2))
    return math.hypot(px - (x1 + t * vx), py - (y1 + t * vy))


def seg_clear(x1, y1, x2, y2, lay, world, ignore_net, step=0.15):
    n = max(1, int(math.hypot(x2 - x1, y2 - y1) / step))
    for i in range(n + 1):
        t = i / n
        if world.track_hit(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, lay, ignore_net):
            return False
    return True


def fanout_u4(world):
    """Escape RP2350 matrix pads. Columns drop a via; rows stay on F.Cu."""
    u4 = [p for p in world.pads if p["ref"] == "U4" and p["net"] in ROW_NETS | COL_NETS]
    # outward from chip center
    committed = []  # segments and vias to add to the net before maze
    for pad in sorted(u4, key=lambda p: (abs(p["x"] - 116.12), p["y"])):
        vx, vy = pad["x"] - pad["fx"], pad["y"] - pad["fy"]
        # Escape straight off the package edge, along the pad's long axis.
        if abs(vx) >= abs(vy):
            ux, uy = (1.0 if vx > 0 else -1.0), 0.0
        else:
            ux, uy = 0.0, (1.0 if vy > 0 else -1.0)
        px, py = -uy, ux  # lateral
        is_col = pad["net"] in COL_NETS
        half = max(pad["hx"], pad["hy"])
        # Short straight exit, then a lateral jog, then further out.
        # A via on the neighbour pin is wider than the 0.4 mm pitch, so the
        # next pin has to leave its centreline before it passes that via.
        base = half + 0.42
        placed = False
        # Right-side columns cannot share a via lane: a via on one
        # centreline blocks the neighbour 0.4 mm away. Upper pins elbow
        # closer to the package; C5 stays on its pad row, then steps up
        # before the GPIO25 /CS trace that turns at x=123.3.
        polys = {
            "31": [(120.50, 77.18), (120.50, 78.80), (121.10, 78.80)],
            "33": [(121.10, 76.38), (121.10, 78.00), (121.90, 78.00)],
            "35": [(121.70, 75.58), (121.70, 77.20), (122.50, 77.20)],
            "36": [(122.50, 75.18), (122.50, 76.00)],
        }
        if pad["pad"] in polys:
            pts = [(pad["x"], pad["y"])] + polys[pad["pad"]]
            ok = all(seg_clear(a[0], a[1], b[0], b[1], 0, world, pad["net"])
                     for a, b in zip(pts, pts[1:])
                     if abs(a[0] - b[0]) + abs(a[1] - b[1]) >= 0.05)
            end = pts[-1]
            if ok and is_col and world.via_hit(end[0], end[1], pad["net"]):
                ok = False
            if ok:
                if is_col:
                    world.vias.append({"x": end[0], "y": end[1], "net": pad["net"]})
                for a, b in zip(pts, pts[1:]):
                    if abs(a[0] - b[0]) + abs(a[1] - b[1]) < 0.05:
                        continue
                    world.segs.append({"x1": a[0], "y1": a[1], "x2": b[0], "y2": b[1],
                                       "w": TRACK, "lay": 0, "net": pad["net"]})
                committed.append((pad["net"], end[0], end[1], 1 if is_col else 0))
                print(f"fanout {pad['net']:16} {pad['ref']}.{pad['pad']:3} -> ({end[0]:.2f},{end[1]:.2f}) {'via' if is_col else 'F'}")
                placed = True
            else:
                print(f"FANOUT FAIL {pad['net']} {pad['ref']}.{pad['pad']} at ({pad['x']:.2f},{pad['y']:.2f})")
            continue
        # Pre-spaced escapes. Adjacent 0.4 mm pins cannot share a via lane.
        manual = {
            "9": (111.5, 74.6),
            "10": (111.5, 75.6),
            "14": (111.5, 76.6),
            "15": (111.5, 77.6),
            "16": (113.32, 80.2),
            "17": (113.72, 80.2),
            "18": (114.12, 80.2),
        }
        if pad["pad"] in manual:
            target = manual[pad["pad"]]
            p0 = (pad["x"], pad["y"])
            p1 = (pad["x"] + ux * base, pad["y"] + uy * base)
            # Leave the pad, jog laterally, then run out to the target.
            p2 = (p1[0] + (target[0] - p1[0]) * abs(px),
                  p1[1] + (target[1] - p1[1]) * abs(py))
            p3 = target
            ok = (seg_clear(p0[0], p0[1], p1[0], p1[1], 0, world, pad["net"])
                  and seg_clear(p1[0], p1[1], p2[0], p2[1], 0, world, pad["net"])
                  and seg_clear(p2[0], p2[1], p3[0], p3[1], 0, world, pad["net"])
                  and not (is_col and world.via_hit(p3[0], p3[1], pad["net"])))
            if ok:
                if is_col:
                    world.vias.append({"x": p3[0], "y": p3[1], "net": pad["net"]})
                for a, b in zip((p0, p1, p2), (p1, p2, p3)):
                    if abs(a[0] - b[0]) + abs(a[1] - b[1]) < 0.05:
                        continue
                    world.segs.append({"x1": a[0], "y1": a[1], "x2": b[0], "y2": b[1],
                                       "w": TRACK, "lay": 0, "net": pad["net"]})
                committed.append((pad["net"], p3[0], p3[1], 1 if is_col else 0))
                print(f"fanout {pad['net']:16} {pad['ref']}.{pad['pad']:3} -> ({p3[0]:.2f},{p3[1]:.2f}) {'via' if is_col else 'F'}")
                placed = True
            else:
                print(f"FANOUT FAIL {pad['net']} {pad['ref']}.{pad['pad']} at ({pad['x']:.2f},{pad['y']:.2f})")
            continue
        if placed:
            continue
        laterals = [0, 0.8, -0.8, 1.4, -1.4, 2.0, -2.0, 2.7, -2.7]
        extras = [1.3, 1.9, 2.5, 3.2, 4.0]
        for lat in laterals:
            for extra in extras:
                p0 = (pad["x"], pad["y"])
                p1 = (pad["x"] + ux * base, pad["y"] + uy * base)
                p2 = (p1[0] + px * lat, p1[1] + py * lat)
                rawx = p2[0] + ux * extra
                rawy = p2[1] + uy * extra
                # Land on the maze grid so the router can start on this copper.
                p3 = (OX + round((rawx - OX) / RES) * RES,
                      OY + round((rawy - OY) / RES) * RES)
                if not seg_clear(p0[0], p0[1], p1[0], p1[1], 0, world, pad["net"]):
                    continue
                if abs(lat) > 0 and not seg_clear(p1[0], p1[1], p2[0], p2[1], 0, world, pad["net"]):
                    continue
                if not seg_clear(p2[0], p2[1], p3[0], p3[1], 0, world, pad["net"]):
                    continue
                if is_col and world.via_hit(p3[0], p3[1], pad["net"]):
                    continue
                if is_col:
                    world.vias.append({"x": p3[0], "y": p3[1], "net": pad["net"]})
                pts = [p0, p1, p2, p3]
                for a, b in zip(pts, pts[1:]):
                    if abs(a[0] - b[0]) + abs(a[1] - b[1]) < 0.05:
                        continue
                    world.segs.append({"x1": a[0], "y1": a[1], "x2": b[0], "y2": b[1],
                                       "w": TRACK, "lay": 0, "net": pad["net"]})
                committed.append((pad["net"], p3[0], p3[1], 1 if is_col else 0))
                print(f"fanout {pad['net']:16} {pad['ref']}.{pad['pad']:3} -> ({p3[0]:.2f},{p3[1]:.2f}) {'via' if is_col else 'F'}")
                placed = True
                break
            if placed:
                break
        if not placed:
            print(f"FANOUT FAIL {pad['net']} {pad['ref']}.{pad['pad']} at ({pad['x']:.2f},{pad['y']:.2f})")
    return committed


def raster_block(world, net, terminals):
    """Boolean block [2][NY][NX]. True = forbidden track center."""
    block = [[bytearray(NX) for _ in range(NY)] for _ in range(2)]
    # board edge and keepouts and pads and foreign copper
    # iterate pads and paint bbox
    for pad in world.pads:
        if pad["net"] == net and pad["net"]:
            continue
        reach = max(pad["hx"], pad["hy"]) + TRACK_GAP + 0.3
        if pad["drill"]:
            reach = max(reach, max(pad["drill"]) / 2 + HOLE_CLR + HALF + 0.2)
        ix0 = max(0, int((pad["x"] - reach - OX) / RES))
        ix1 = min(NX - 1, int((pad["x"] + reach - OX) / RES))
        iy0 = max(0, int((pad["y"] - reach - OY) / RES))
        iy1 = min(NY - 1, int((pad["y"] + reach - OY) / RES))
        for iy in range(iy0, iy1 + 1):
            y = OY + iy * RES
            rowf, rowb = block[0][iy], block[1][iy]
            for ix in range(ix0, ix1 + 1):
                x = OX + ix * RES
                hole = False
                if pad["drill"]:
                    hr = max(pad["drill"]) / 2 + HOLE_CLR + HALF
                    if (x - pad["x"]) ** 2 + (y - pad["y"]) ** 2 < hr * hr:
                        hole = True
                copper = False
                if pad["type"] != "np_thru_hole":
                    if pad["shape"] == "circle":
                        copper = math.hypot(x - pad["x"], y - pad["y"]) < pad["hx"] + TRACK_GAP - EPS
                    else:
                        copper = dist_rect(x, y, pad["x"], pad["y"], pad["ang"], pad["hx"], pad["hy"]) < TRACK_GAP - EPS
                if hole or copper:
                    if hole or pad["lay"] in (0, 2):
                        rowf[ix] = 1
                    if hole or pad["lay"] in (1, 2):
                        rowb[ix] = 1
    for s in world.segs:
        if s["net"] == net:
            continue
        gap = s["w"] / 2 + CLR + HALF
        xmin, xmax = min(s["x1"], s["x2"]) - gap, max(s["x1"], s["x2"]) + gap
        ymin, ymax = min(s["y1"], s["y2"]) - gap, max(s["y1"], s["y2"]) + gap
        ix0 = max(0, int((xmin - OX) / RES)); ix1 = min(NX - 1, int((xmax - OX) / RES))
        iy0 = max(0, int((ymin - OY) / RES)); iy1 = min(NY - 1, int((ymax - OY) / RES))
        lay = s["lay"]
        for iy in range(iy0, iy1 + 1):
            y = OY + iy * RES
            row = block[lay][iy]
            for ix in range(ix0, ix1 + 1):
                if row[ix]:
                    continue
                x = OX + ix * RES
                if dist_seg(x, y, s["x1"], s["y1"], s["x2"], s["y2"]) < gap - EPS:
                    row[ix] = 1
    for v in world.vias:
        if v["net"] == net:
            continue
        r = VIA_R + CLR + HALF
        ix0 = max(0, int((v["x"] - r - OX) / RES)); ix1 = min(NX - 1, int((v["x"] + r - OX) / RES))
        iy0 = max(0, int((v["y"] - r - OY) / RES)); iy1 = min(NY - 1, int((v["y"] + r - OY) / RES))
        for iy in range(iy0, iy1 + 1):
            y = OY + iy * RES
            for ix in range(ix0, ix1 + 1):
                x = OX + ix * RES
                if (x - v["x"]) ** 2 + (y - v["y"]) ** 2 < r * r:
                    block[0][iy][ix] = 1
                    block[1][iy][ix] = 1
    # edge + keepouts
    for iy in range(NY):
        y = OY + iy * RES
        edge_y = y < 46.4 + EDGE + HALF or y > 190.85 - EDGE - HALF
        for ix in range(NX):
            x = OX + ix * RES
            if edge_y or x < 49.5 + EDGE + HALF or x > 150 - EDGE - HALF:
                block[0][iy][ix] = 1
                block[1][iy][ix] = 1
                continue
    for poly in world.keepouts:
        xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
        ix0 = max(0, int((min(xs) - OX) / RES)); ix1 = min(NX - 1, int((max(xs) - OX) / RES))
        iy0 = max(0, int((min(ys) - OY) / RES)); iy1 = min(NY - 1, int((max(ys) - OY) / RES))
        for iy in range(iy0, iy1 + 1):
            y = OY + iy * RES
            for ix in range(ix0, ix1 + 1):
                x = OX + ix * RES
                if point_in_poly(x, y, poly):
                    block[0][iy][ix] = 1
                    block[1][iy][ix] = 1
    return block


def copper_cells(pad, block):
    cells = []
    reach = max(pad["hx"], pad["hy"])
    ix0 = max(0, int((pad["x"] - reach - OX) / RES))
    ix1 = min(NX - 1, int((pad["x"] + reach - OX) / RES))
    iy0 = max(0, int((pad["y"] - reach - OY) / RES))
    iy1 = min(NY - 1, int((pad["y"] + reach - OY) / RES))
    layers = (0, 1) if pad["lay"] == 2 else (pad["lay"],)
    for iy in range(iy0, iy1 + 1):
        y = OY + iy * RES
        for ix in range(ix0, ix1 + 1):
            x = OX + ix * RES
            if pad["shape"] == "circle":
                inside = math.hypot(x - pad["x"], y - pad["y"]) <= pad["hx"] - 0.02
            else:
                inside = dist_rect(x, y, pad["x"], pad["y"], pad["ang"], pad["hx"], pad["hy"]) <= 0.02
            if not inside:
                continue
            # reject cells inside the drill
            if pad["drill"]:
                hr = max(pad["drill"]) / 2
                if math.hypot(x - pad["x"], y - pad["y"]) < hr + 0.05:
                    continue
            for lay in layers:
                if not block[lay][iy][ix]:
                    cells.append((lay, ix, iy))
    return cells


def via_cells(x, y, lay, block):
    cells = []
    ip = idx_of(x, y)
    if not ip:
        return cells
    ix, iy = ip
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            jx, jy = ix + dx, iy + dy
            if not (0 <= jx < NX and 0 <= jy < NY):
                continue
            cx, cy = cell_xy(jx, jy)
            if math.hypot(cx - x, cy - y) <= VIA_R - 0.02 and not block[lay][jy][jx]:
                cells.append((lay, jx, jy))
    if not cells and not block[lay][iy][ix]:
        cells.append((lay, ix, iy))
    return cells


def astar(block, sources, goals, goal_pts, prefer):
    """sources/goals: list of (lay,ix,iy). prefer 0 or 1."""
    if not sources or not goals:
        return None
    goal_set = set(goals)
    INF = 10 ** 9
    # dist and parent packed
    N = NX * NY
    dist = [INF] * (2 * N)
    parent = [-1] * (2 * N)
    popped = bytearray(2 * N)

    def pack(lay, ix, iy):
        return lay * N + iy * NX + ix

    def heur(ix, iy):
        best = 1e9
        for gx, gy in goal_pts:
            best = min(best, abs(ix - gx) + abs(iy - gy))
        return best

    heap = []
    for lay, ix, iy in sources:
        p = pack(lay, ix, iy)
        dist[p] = 0
        heapq.heappush(heap, (heur(ix, iy), 0, lay, ix, iy, -1))
    found = None
    expands = 0
    while heap:
        f, g, lay, ix, iy, pdir = heapq.heappop(heap)
        p = pack(lay, ix, iy)
        if popped[p]:
            continue
        if g != dist[p]:
            continue
        popped[p] = 1
        expands += 1
        if p in goal_set or (lay, ix, iy) in goal_set:
            found = (lay, ix, iy)
            break
        if expands > 1800000:
            return None
        # 4-connect
        for d, (dx, dy) in enumerate(((1, 0), (-1, 0), (0, 1), (0, -1))):
            jx, jy = ix + dx, iy + dy
            if not (0 <= jx < NX and 0 <= jy < NY):
                continue
            if block[lay][jy][jx]:
                continue
            step = 1.0 if lay == prefer else 3.2
            if pdir != -1 and pdir != d:
                step += 0.35
            ng = g + step
            npk = pack(lay, jx, jy)
            if ng < dist[npk]:
                dist[npk] = ng
                parent[npk] = p
                heapq.heappush(heap, (ng + heur(jx, jy), ng, lay, jx, jy, d))
        # via
        olay = 1 - lay
        if not block[olay][iy][ix]:
            # via clearance approximated: both cells free and a small neighborhood
            ok = True
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    jx, jy = ix + dx, iy + dy
                    if 0 <= jx < NX and 0 <= jy < NY:
                        if block[0][jy][jx] or block[1][jy][jx]:
                            ok = False
                            break
                if not ok:
                    break
            if ok:
                ng = g + 6.0
                npk = pack(olay, ix, iy)
                if ng < dist[npk]:
                    dist[npk] = ng
                    parent[npk] = p
                    heapq.heappush(heap, (ng + heur(ix, iy), ng, olay, ix, iy, 4))
    if not found:
        return None
    path = []
    cur = pack(*found)
    # also need start
    seen = 0
    while cur != -1 and seen < 20000:
        lay = cur // N
        rem = cur % N
        iy, ix = divmod(rem, NX)
        path.append((lay, ix, iy))
        cur = parent[cur]
        seen += 1
    path.reverse()
    return path


def path_to_segs(path):
    if not path:
        return [], []
    pts = []
    for lay, ix, iy in path:
        x, y = cell_xy(ix, iy)
        if pts and pts[-1][0] == lay and abs(pts[-1][1] - x) < 1e-6 and abs(pts[-1][2] - y) < 1e-6:
            continue
        pts.append((lay, x, y))
    # simplify colinear
    simp = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = simp[-1], pts[i], pts[i + 1]
        if a[0] == b[0] == c[0]:
            col = (abs(a[1] - b[1]) < 1e-6 and abs(b[1] - c[1]) < 1e-6) or (
                abs(a[2] - b[2]) < 1e-6 and abs(b[2] - c[2]) < 1e-6)
            if col:
                continue
        simp.append(b)
    if len(pts) > 1:
        simp.append(pts[-1])
    segs, vias = [], []
    for a, b in zip(simp, simp[1:]):
        if a[0] != b[0]:
            vias.append((a[1], a[2]))
        else:
            if abs(a[1] - b[1]) < 1e-6 and abs(a[2] - b[2]) < 1e-6:
                continue
            segs.append((a[0], a[1], a[2], b[1], b[2]))
    return segs, vias


def route_net(world, net, pad_terms, extra_pts):
    """pad_terms: list of pads. extra_pts: list of (x,y,lay) already connected together (fanout ends).
    Returns segs, vias. Connects all pads and the extra group."""
    # terminals as groups. extra_pts are one already-connected group if len>=1
    groups = []
    if extra_pts:
        groups.append(("extra", extra_pts))
    # unique pads by position
    seen = set()
    for pad in pad_terms:
        key = (round(pad["x"], 2), round(pad["y"], 2), pad["ref"], pad["pad"])
        if key in seen:
            continue
        seen.add(key)
        groups.append(("pad", pad))
    if len(groups) < 2:
        return [], [], True
    # greedy order: start at group 0, always nearest remaining
    order = [0]
    left = set(range(1, len(groups)))
    def center(g):
        if g[0] == "extra":
            return g[1][0][0], g[1][0][1]
        return g[1]["x"], g[1]["y"]
    while left:
        cx, cy = center(groups[order[-1]])
        nxt = min(left, key=lambda i: (center(groups[i])[0] - cx) ** 2 + (center(groups[i])[1] - cy) ** 2)
        order.append(nxt)
        left.remove(nxt)
    prefer = 1 if net in COL_NETS else 0
    all_segs, all_vias = [], []
    # connected geometry grows
    connected_pts = []  # (x,y,lay) used as sources after first
    first = groups[order[0]]
    if first[0] == "extra":
        connected_pts.extend(first[1])
    else:
        connected_pts.append((first[1]["x"], first[1]["y"], first[1]["lay"]))
    for gi in order[1:]:
        block = raster_block(world, net, None)
        # also block our newly routed geometry? it is already in world.segs with this net,
        # and raster skips same net. Good. But the maze must be allowed to touch it.
        # Sources: cells of connected copper.
        sources = []
        for x, y, lay in connected_pts:
            if lay == 2:
                lays = (0, 1)
            else:
                lays = (lay,)
            # find pad cells if this point is a pad
            hit = False
            for pad in pad_terms:
                if abs(pad["x"] - x) < 0.05 and abs(pad["y"] - y) < 0.05:
                    sources.extend(copper_cells(pad, block))
                    hit = True
                    break
            if not hit:
                for L in lays:
                    sources.extend(via_cells(x, y, L, block))
        g = groups[gi]
        goals = []
        goal_pts = []
        if g[0] == "extra":
            for x, y, lay in g[1]:
                L = 1 if lay == 2 else lay
                goals.extend(via_cells(x, y, L if lay != 2 else 0, block))
                if lay == 2 or lay == 1:
                    goals.extend(via_cells(x, y, 1, block))
                if lay == 2 or lay == 0:
                    goals.extend(via_cells(x, y, 0, block))
                ip = idx_of(x, y)
                if ip:
                    goal_pts.append(ip)
        else:
            goals = copper_cells(g[1], block)
            ip = idx_of(g[1]["x"], g[1]["y"])
            if ip:
                goal_pts.append(ip)
        if not sources or not goals:
            print(f"  no cells {net} sources={len(sources)} goals={len(goals)} group={g[0]}")
            return all_segs, all_vias, False
        # dedup
        sources = list(set(sources))
        goals = list(set(goals))
        path = astar(block, sources, goals, goal_pts, prefer)
        if path is None:
            # retry with mild preference
            path = astar(block, sources, goals, goal_pts, prefer)
        if path is None:
            print(f"  ASTAR FAIL {net} -> {g[0]} {center(g)}")
            return all_segs, all_vias, False
        segs, vias = path_to_segs(path)
        # The maze starts on a grid cell near existing copper. Close that gap.
        if path:
            sx, sy = cell_xy(path[0][1], path[0][2])
            best = None
            for x, y, lay in connected_pts:
                d = math.hypot(x - sx, y - sy)
                if best is None or d < best[0]:
                    best = (d, x, y)
            if best and 0.02 < best[0] <= 1.5:
                segs.insert(0, (path[0][0], best[1], best[2], sx, sy))
        # extend ends to exact anchors
        if segs or vias or path:
            # snap last point to target anchor if needed
            if g[0] == "pad":
                tx, ty = g[1]["x"], g[1]["y"]
                tlay = 0 if g[1]["lay"] == 0 else (1 if g[1]["lay"] == 1 else path[-1][0])
                lx, ly = cell_xy(path[-1][1], path[-1][2])
                if math.hypot(lx - tx, ly - ty) > 0.05:
                    segs.append((path[-1][0], lx, ly, tx, ty))
            elif g[0] == "extra":
                tx, ty, tlay = g[1][0]
                lx, ly = cell_xy(path[-1][1], path[-1][2])
                if math.hypot(lx - tx, ly - ty) > 0.05:
                    segs.append((path[-1][0], lx, ly, tx, ty))
        for lay, x1, y1, x2, y2 in segs:
            world.segs.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2, "w": TRACK, "lay": lay, "net": net})
            all_segs.append((lay, x1, y1, x2, y2))
            connected_pts.append((x2, y2, lay))
            connected_pts.append((x1, y1, lay))
        for vx, vy in vias:
            world.vias.append({"x": vx, "y": vy, "net": net})
            all_vias.append((vx, vy))
            connected_pts.append((vx, vy, 2))
        # the target anchor is connected
        if g[0] == "pad":
            connected_pts.append((g[1]["x"], g[1]["y"], g[1]["lay"]))
        else:
            connected_pts.extend(g[1])
        print(f"  linked {net} +{len(segs)} segs +{len(vias)} vias")
    return all_segs, all_vias, True


def main():
    text = open(PCB).read()
    pads, keepouts, segs = parse_board(text)
    print(f"pads {len(pads)} keepouts {len(keepouts)} segs {len(segs)} grid {NX}x{NY}")
    world = World(pads, keepouts, segs)
    # only matrix-related new routing; existing segs already in world
    fan = fanout_u4(world)
    fan_by = defaultdict(list)
    for net, x, y, lay in fan:
        fan_by[net].append((x, y, lay))

    wanted = []
    # Local diode-to-switch links first, then the row and column buses.
    for i in range(24, 50):
        wanted.append(f"Net-(D{i}-K)")
    wanted.append("Net-(D37-A)")
    for i in range(5):
        wanted.append(f"/C6/MAT_R{i}")
    for i in range(6):
        wanted.append(f"/C6/MAT_C{i}")

    new_count = 0
    failed = []
    for net in wanted:
        terms = [p for p in pads if p["net"] == net and p["type"] != "np_thru_hole"]
        extra = fan_by.get(net, [])
        # drop U4 pads when a fanout stub already reaches them
        maze_pads = [p for p in terms if not (p["ref"] == "U4" and extra)]
        # distinct locations
        locs = {(round(p["x"], 2), round(p["y"], 2)) for p in maze_pads}
        if len(locs) + (1 if extra else 0) < 2:
            print(f"skip {net} pads={len(maze_pads)} fan={len(extra)}")
            continue
        print(f"route {net} pads={len(maze_pads)} fan={len(extra)}")
        before = len(world.segs)
        segs_n, vias_n, ok = route_net(world, net, maze_pads, extra)
        if not ok:
            failed.append(net)
            # roll back this net's maze segs but keep fanout (fanout segs were added before and are wanted)
            # Identify maze segs as those added after `before` — fanout already in world before this call.
            del world.segs[before:]
            world.vias = [v for v in world.vias if v["net"] != net or (v["x"], v["y"]) in {(x, y) for x, y, _ in extra}]
        else:
            new_count += 1

    # emit all matrix segs/vias that we added: those whose net is wanted and that were not in the original file
    orig_seg_keys = set()
    # original segs were the prefix; we only appended. Re-parse count:
    # world.segs started as a copy of original. Appended ones are new.
    # But we may have deleted failed maze segs. Fanout segs are appended too.
    # Safest: collect segs/vias with wanted nets that are not in the original text... 
    # We kept original segs at the front unchanged. Remember original length.
    print("---")
    print("routed", new_count, "failed", failed)
    # The function mutated from the initial copy. I need original length.
    # Recompute by storing wasn't done. I'll tag: original segs don't have a 'new' key.
    # I didn't tag. Original segs were copied at start. Let me mark by identity:
    # I'll just emit every world seg whose net is in wanted OR fan, comparing to initial set of coordinates from the file.
    initial = {(round(s["x1"], 3), round(s["y1"], 3), round(s["x2"], 3), round(s["y2"], 3), s["net"]) for s in segs}
    out = []
    for s in world.segs:
        key = (round(s["x1"], 3), round(s["y1"], 3), round(s["x2"], 3), round(s["y2"], 3), s["net"])
        if key in initial:
            continue
        if s["net"] not in set(wanted) and not s["net"].startswith("/C6/MAT_") and not s["net"].startswith("Net-(D"):
            continue
        lay = "F.Cu" if s["lay"] == 0 else "B.Cu"
        out.append(
            f'\t(segment\n\t\t(start {s["x1"]:.4f} {s["y1"]:.4f})\n\t\t(end {s["x2"]:.4f} {s["y2"]:.4f})\n'
            f'\t\t(width {TRACK})\n\t\t(layer "{lay}")\n\t\t(net "{s["net"]}")\n\t\t(uuid "{uuid.uuid4()}")\n\t)'
        )
    for v in world.vias:
        if v["net"] not in set(wanted):
            continue
        out.append(
            f'\t(via\n\t\t(at {v["x"]:.4f} {v["y"]:.4f})\n\t\t(size 0.6)\n\t\t(drill 0.3)\n'
            f'\t\t(layers "F.Cu" "B.Cu")\n\t\t(net "{v["net"]}")\n\t\t(uuid "{uuid.uuid4()}")\n\t)'
        )
    print(f"emit {len(out)} items")
    if not text.rstrip().endswith(")"):
        raise SystemExit("pcb ending unexpected")
    body = text.rstrip()
    body = body[:body.rfind(")")]
    new = body + "\n" + "\n".join(out) + "\n)\n"
    open(PCB, "w").write(new)
    print("wrote", PCB)
    if failed:
        print("FAILED NETS:", ", ".join(failed))


if __name__ == "__main__":
    main()
