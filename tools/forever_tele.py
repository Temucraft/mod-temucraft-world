#!/usr/bin/env python3
"""A .tele point for every new map from the Forever client data, so staff can visit and test them.

The Forever data has no spawns, entrances or exits, so there is no known start point. This takes the terrain:
for each map it finds the tile closest to the middle of its tiles, then the chunk closest to that tile's middle
that has no hole, and puts the point 2 yards above the ground there (ADT heights, MCNK position + MCVT). Points can
land outside the playable part of a map or under a roof; move them in game if needed (.gps, then edit the row).
The server needs each map's .map/.vmap files first (extract_new_maps.bat).

usage: python3 tools/forever_tele.py <Map.dbc> <world/maps folder of Forever's patch-z.MPQ>
Writes data/sql/db-world/base/temucraft_world_forever_tele.sql."""
import os, re, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), 'data', 'sql', 'db-world', 'base', 'temucraft_world_forever_tele.sql')
MAPS = [2720, 2784, 2789, 2791, 2804, 2806, 2807, 2817, 2832, 2853, 2856, 2868, 2875, 2902, 2921, 2959, 2980, 2991,
        2995, 2996, 2998, 2999, 3002, 3005, 3021, 3065, 3104]
TILE = 533.33333
CHUNK = TILE / 16


def map_rows(path):
    d = open(path, 'rb').read()
    n, fc, rs, ss = struct.unpack('<4I', d[4:20])
    so = 20 + n * rs
    out = {}
    for i in range(n):
        r = d[20 + i * rs:20 + (i + 1) * rs]
        u = lambda f: struct.unpack('<I', r[f * 4:f * 4 + 4])[0]
        s = lambda o: d[so + o:d.index(b'\0', so + o)].decode('latin1')
        out[u(0)] = (s(u(1)), s(u(5)))
    return out


def chunks(adt):
    """(cy, cx, ground z at the chunk middle, has a hole in the middle) for each MCNK."""
    d = open(adt, 'rb').read()
    i, out = 0, []
    while i < len(d) - 8:
        tag = d[i:i + 4][::-1]
        size = struct.unpack('<I', d[i + 4:i + 8])[0]
        if tag == b'MCNK':
            h = d[i + 8:i + 8 + 128]
            cx, cy = struct.unpack('<II', h[4:12])
            holes = struct.unpack('<H', h[0x3C:0x3E])[0]
            z = struct.unpack('<f', h[0x70:0x74])[0]
            j, end, mid = i + 8 + 128, i + 8 + size, 0.0
            while j < end - 8:
                t = d[j:j + 4][::-1]; n = struct.unpack('<I', d[j + 4:j + 8])[0]
                if t == b'MCVT':
                    mid = struct.unpack('<f', d[j + 8 + 4 * 76:j + 8 + 4 * 77])[0]   # vertex 76: middle of the 9x9/8x8 grid
                    break
                j += 8 + n
            out.append((cy, cx, z + mid, bool(holes & 0x0660)))   # the four middle hole bits
        i += 8 + size
    return out


def point(folder):
    tiles = []
    for f in os.listdir(folder):
        m = re.match(r'.*_(\d+)_(\d+)\.adt$', f, re.I)
        if m:
            tiles.append((int(m.group(1)), int(m.group(2)), f))
    if not tiles:
        return None
    mx = sum(t[0] for t in tiles) / len(tiles); my = sum(t[1] for t in tiles) / len(tiles)
    for tx, ty, f in sorted(tiles, key=lambda t: (t[0] - mx) ** 2 + (t[1] - my) ** 2):
        cs = [c for c in chunks(os.path.join(folder, f)) if not c[3]]
        if not cs:
            continue
        cy, cx, z, _ = min(cs, key=lambda c: (c[0] - 7.5) ** 2 + (c[1] - 7.5) ** 2)
        x = 32 * TILE - (ty * 16 + cy + 0.5) * CHUNK
        y = 32 * TILE - (tx * 16 + cx + 0.5) * CHUNK
        return round(x, 2), round(y, 2), round(z + 2, 2)
    return None


def main():
    rows, base = map_rows(sys.argv[1]), sys.argv[2]
    have = {x.lower(): x for x in os.listdir(base)}
    out, names = [], []
    for m in MAPS:
        folder, name = rows[m]
        p = have.get(folder.lower())
        pt = point(os.path.join(base, p)) if p else None
        if not pt:
            print('no terrain', m, name); continue
        tele = 'F' + str(m) + re.sub(r'[^A-Za-z0-9]', '', name)
        names.append(tele)
        out.append("INSERT INTO `game_tele` (`id`, `position_x`, `position_y`, `position_z`, `orientation`, `map`, `name`) "
                   "SELECT MAX(`id`) + 1, %s, %s, %s, 0, %d, '%s' FROM `game_tele`; -- %s" % (pt + (m, tele, name)))
    head = ['-- mod-temucraft-world: a .tele point on every new Forever map (tools/forever_tele.py), for staff to visit and',
            '-- test them. The points come from the terrain (middle of the map), not from real start points, which the',
            '-- Forever data does not have. Names start with F and the map id, e.g. .tele F2784DemonFallCanyon.',
            'DELETE FROM `game_tele` WHERE `name` IN (%s);' % ', '.join("'%s'" % n for n in names)]
    open(OUT, 'w').write('\n'.join(head + out) + '\n')
    print('ok', len(out))


main()
