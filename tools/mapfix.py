#!/usr/bin/env python3
"""map_dbc / mapdifficulty_dbc rows so the Cataclysm / Mists / scenario maps can be entered on 3.3.5:
expansion 3/4 -> 2 (the core refuses maps of a later expansion than the account), scenarios -> dungeon type, and
MapDifficulty rows for instance maps that have none (the core refuses those too)."""
import struct, sys, os
DBC = os.path.expanduser('~/mnt/Ryans World of Warcraft/Y) Build/bin/RelWithDebInfo/Data/dbc')
LANGS = "enUS enGB koKR frFR deDE enCN zhCN enTW zhTW esES esMX ruRU ptPT ptBR itIT Unk".split()
def load(f):
    d = open(f, 'rb').read(); n, fc, rs, ss = struct.unpack_from('<4I', d, 4); st = 20 + n * rs
    S = lambda o: d[st + o:d.index(b'\0', st + o)].decode('utf8', 'replace')
    return d, n, fc, rs, S
esc = lambda s: "'" + s.replace('\\', '\\\\').replace("'", "''") + "'"
sgn = lambda x: x - (1 << 32) if x >= 1 << 31 else x
d, n, fc, rs, S = load(f'{DBC}/Map.dbc')
maps = {struct.unpack_from('<I', d, 20 + i * rs)[0]: d[20 + i * rs:20 + (i + 1) * rs] for i in range(n)}
def map_row(mid, newtype=None, newexp=None):
    raw = maps[mid]; u = lambda k: struct.unpack_from('<I', raw, 4 * k)[0]; f = lambda k: struct.unpack_from('<f', raw, 4 * k)[0]
    vals = [u(0), esc(S(u(1))), u(2) if newtype is None else newtype, u(3), u(4)]; k = 5
    for blk in range(3):
        if blk == 1: vals.append(u(k)); k += 1
        vals += [esc(S(u(k + j))) if u(k + j) else "''" for j in range(16)]; vals.append(u(k + 16)); k += 17
    vals += [u(k), round(f(k + 1), 4), sgn(u(k + 2)), round(f(k + 3), 4), round(f(k + 4), 4), sgn(u(k + 5)),
             u(k + 6) if newexp is None else newexp, u(k + 7), u(k + 8)]
    return vals
cols = ['ID', 'Directory', 'InstanceType', 'Flags', 'PVP'] + [f'MapName_Lang_{l}' for l in LANGS] + ['MapName_Lang_Mask', 'AreaTableID'] + \
       [f'MapDescription0_Lang_{l}' for l in LANGS] + ['MapDescription0_Lang_Mask'] + [f'MapDescription1_Lang_{l}' for l in LANGS] + \
       ['MapDescription1_Lang_Mask', 'LoadingScreenID', 'MinimapIconScale', 'CorpseMapID', 'CorpseX', 'CorpseY', 'TimeOfDayOverride',
        'ExpansionID', 'RaidOffset', 'MaxPlayers']
MAPS = [int(x) for x in sys.argv[2].split(',')]
SCEN = {1048, 1099}
NOMAP = len(sys.argv) > 4 and sys.argv[4] == 'nomap'
out = [f"-- map_dbc: {', '.join(S(struct.unpack_from('<I', maps[m], 20)[0]) for m in MAPS)} as Wrath-era maps (expansion 2), scenarios as dungeons"]
if NOMAP: out = []
else: out.append(f"DELETE FROM `map_dbc` WHERE `ID` IN ({','.join(map(str, MAPS))});")
if not NOMAP: out.append(f"INSERT INTO `map_dbc` ({', '.join('`%s`' % c for c in cols)}) VALUES\n" +
           ',\n'.join('(' + ', '.join(map(str, map_row(m, 1 if m in SCEN else None, 2))) + ')' for m in MAPS) + ';')
# MapDifficulty rows for instance maps without one
md, mn, mfc, mrs, MS = load(f'{DBC}/MapDifficulty.dbc')
have = set(); top = 0
for i in range(mn):
    r = struct.unpack_from(f'<{mfc}I', md, 20 + i * mrs); have.add((r[1], r[2])); top = max(top, r[0])
nid = max(top + 1, int(sys.argv[3]))
rows = []
for m in MAPS:
    t = struct.unpack_from('<I', maps[m], 8)[0]; t = 1 if m in SCEN else t
    name = S(struct.unpack_from('<I', maps[m], 20)[0])
    if t == 1: wanted = [(0, 5, 0, 'DUNGEON_DIFFICULTY_5PLAYER'), (1, 5, 86400, 'DUNGEON_DIFFICULTY_5PLAYER_HEROIC')] if m not in SCEN else [(0, 5, 0, 'DUNGEON_DIFFICULTY_5PLAYER')]
    elif t == 2 and struct.unpack_from('<I', maps[m], len(maps[m]) - 4)[0] not in (0, 10, 25):
        wanted = [(0, struct.unpack_from('<I', maps[m], len(maps[m]) - 4)[0], 604800, 'RAID_DIFFICULTY_40PLAYER' if struct.unpack_from('<I', maps[m], len(maps[m]) - 4)[0] == 40 else 'RAID_DIFFICULTY_20PLAYER')]
    elif t == 2: wanted = [(0, 10, 604800, 'RAID_DIFFICULTY_10PLAYER'), (1, 25, 604800, 'RAID_DIFFICULTY_25PLAYER'),
                           (2, 10, 604800, 'RAID_DIFFICULTY_10PLAYER_HEROIC'), (3, 25, 604800, 'RAID_DIFFICULTY_25PLAYER_HEROIC')]
    else: continue
    for diff, players, reset, ds in wanted:
        if (m, diff) in have: continue
        rows.append(f"({nid}, {m}, {diff}, '', {players}, {reset}, '{ds}')  /* {name} */"); nid += 1
if rows:
    ids = [r.split(',')[0][1:] for r in rows]
    out.append(f"-- mapdifficulty_dbc: difficulties for the instance maps that had none\nDELETE FROM `mapdifficulty_dbc` WHERE `ID` IN ({','.join(ids)});")
    out.append("INSERT INTO `mapdifficulty_dbc` (`ID`, `MapID`, `Difficulty`, `Message_Lang_enUS`, `MaxPlayers`, `RaidDuration`, `Difficultystring`) VALUES\n" + ',\n'.join(rows) + ';')
open(sys.argv[1], 'w').write('\n'.join(out) + '\n')
print(sys.argv[1], len(MAPS), 'maps,', len(rows), 'difficulty rows')
