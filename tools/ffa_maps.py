#!/usr/bin/env python3
"""The Crazy repack's three free-for-all PvP maps, with their own map ids.

Their terrain (World\\Maps\\<name>_2) is already in the client's patch-Z.MPQ; only the Map.dbc rows were missing,
because Crazy used ids 1210-1212 and our Map.dbc has a garrison map at 1212. New ids:
  1210 ValleyOfPower_2   -> 1210  Valley of Power (Free-for-All)
  1211 TolVirArena_2     -> 1211  Tol'vir Proving Grounds (Free-for-All)
  1212 ShadoPanArena_2   -> 1246  Shado-Pan Arena (Free-for-All)
Writes data/sql/db-world/base/temucraft_world_ffa_maps.sql (map_dbc rows + .tele points). With --client the rows also
go into the client's Map.dbc in patch-X.MPQ (game closed), where our Map.dbc changes live.
The server still needs .map / vmap files for the new ids (extract_new_maps.bat with 1210, 1211, 1246)."""
import os, sys
sys.path.insert(0, os.path.expanduser('~/tc'))
import dbctool as T

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
CRAZY_MAP = '/tmp/cz/Map.dbc'          # from CrazyPublicDesed/server_dbc_maps/VmapsMapsDBC.zip, dbc/Map.dbc
PATCH_X = os.path.expanduser('~/mnt/ChromieCraft_3.3.5a/Data/patch-X.MPQ')
MAPS = [  # crazy id, new id, name, tele name, x, y, z, o (a spawn point from Crazy's own creatures)
    (1210, 1210, 'Valley of Power (Free-for-All)', 'FFAValleyOfPower', 1786.12, 1367.22, 5.556, 1.759),
    (1211, 1211, "Tol'vir Proving Grounds (Free-for-All)", 'FFATolvir', -10719.0, 411.453, 24.412, 1.609),
    (1212, 1246, 'Shado-Pan Arena (Free-for-All)', 'FFAShadoPan', 481.041, 561.548, 400.053, 0.771),
]
F_DIR, F_NAME, F_NAME_MASK = 1, 5, 21


def rows_into(dbc, crazy):
    out = []
    for old, new, name, *_ in MAPS:
        r = list(crazy.rows[old])
        r[0] = new
        r[F_DIR] = dbc.add(crazy.s(crazy.rows[old][F_DIR]))
        # Map.dbc 3.3.5: 1 Directory, 2 InstanceType, 3 Flags, 4 PVP, 5-20 MapName, 21 mask, 22 AreaTableID,
        # 23-38 MapDescription0, 39 mask, 40-55 MapDescription1, 56 mask, 57 LoadingScreenID, 58 MinimapIconScale,
        # 59 CorpseMapID, 60-61 Corpse x/y, 62 TimeOfDayOverride, 63 ExpansionID, 64 RaidOffset, 65 MaxPlayers
        for i in range(5, 21):
            r[i] = 0
        r[F_NAME] = dbc.add(name)
        for i in list(range(23, 39)) + list(range(40, 56)):
            r[i] = 0
        r[63] = 2                                  # Wrath: every account may enter
        dbc.put(r)
        out.append(r)
    return out


crazy = T.DBC(CRAZY_MAP)
server = T.DBC(T.SERVER_DBC + '/Map.dbc')
for old, new, *_ in MAPS:
    assert new not in server.rows or new == old and server.s(server.rows[new][F_DIR]).endswith('_2'), new
rows = rows_into(server, crazy)
sql = ['-- mod-temucraft-world: the Crazy repack\'s free-for-all PvP maps under their own ids (tools/ffa_maps.py).',
       'DELETE FROM `map_dbc` WHERE `ID` IN (%s);' % ', '.join(str(m[1]) for m in MAPS),
       T.sql_insert('map_dbc', rows, server),
       "DELETE FROM `game_tele` WHERE `name` IN (%s);" % ', '.join("'%s'" % m[3] for m in MAPS)]
for old, new, name, tele, x, y, z, o in MAPS:
    sql.append("INSERT INTO `game_tele` (`id`, `position_x`, `position_y`, `position_z`, `orientation`, `map`, `name`) "
               "SELECT MAX(`id`) + 1, %s, %s, %s, %s, %d, '%s' FROM `game_tele`;" % (x, y, z, o, new, tele))
out = os.path.join(MOD, 'data', 'sql', 'db-world', 'base', 'temucraft_world_ffa_maps.sql')
open(out, 'w').write('\n'.join(sql) + '\n')
print('wrote', out)

if '--client' in sys.argv:
    tmp = '/tmp/Map_client.dbc'
    assert T.client_get('DBFilesClient\\Map.dbc', tmp, mpq=PATCH_X), 'no Map.dbc in patch-X'
    client = T.DBC(tmp)
    rows_into(client, crazy)
    client.save(tmp)
    T.client_put({'DBFilesClient\\Map.dbc': tmp}, mpq=PATCH_X)
    os.remove(tmp)
    print('client Map.dbc (patch-X) updated')
