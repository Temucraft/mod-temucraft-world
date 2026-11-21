# mod-temucraft-world

World data for the maps salvaged from the Crazy repack and WoW Forever client files. SQL only; boss scripts live in their own modules.

- `temucraft_world_instance_template.sql`: lets players into the new dungeons and raids (no boss scripts yet).
- `temucraft_world_ebon_hold_cleanup.sql`: map 609 uses the Scarlet Enclave terrain now, so the old Death Knight
  start spawns are removed. They are copied to `temucraft_backup_609_*` tables first.

- `temucraft_world_cata.sql`: Halls of Origination, Vortex Pinnacle, Firelands, Throne of the Four Winds, Lost City of
  the Tol'vir, Well of Eternity (from the TrinityCore 4.3.4 world database).
- `temucraft_world_mists.sql`: Temple of the Jade Serpent, Mogu'shan Vaults, Siege of Orgrimmar and the Unga Ingoo
  scenario map (LegionCore 7.3.5 spawns, texts and script names, which match the ported scripts; SkyFire 5.4.8
  templates where SkyFire has them, LegionCore's for the rest).
- `temucraft_world_map_dbc.sql`: `map_dbc` / `mapdifficulty_dbc` overrides so the Cataclysm, Mists and scenario maps
  can be entered: expansion set to 2 (the core turns away maps of a later expansion than the account), the two
  scenario maps as dungeons, and difficulty rows for the instance maps that had none (Firelands Terrain 2, Well of
  Eternity heroic, Temple of the Jade Serpent, Siege of Orgrimmar, the scenarios). Made by `tools/mapfix.py`.
- `temucraft_world_msv.sql`: only removes the Mogu'shan Vaults spawns an earlier version added (GUIDs 72xxxxx).
- `temucraft_world_items.sql`: the items those instances drop (also the Deadmines and Shadowfang Keep heroic boss loot),
  with their `item_dbc` rows so the server knows the items the 3.3.5 Item.dbc doesn't have.
- `temucraft_world_pandaria_bosses.sql`: the Pandaria world bosses on map 870: the Sha of Anger (one of four spawn
  points in Kun-Lai Summit, pool 76000), Galleon (Valley of the Four Winds) and Oondasta (Isle of Giants), with the
  creatures they summon. Spawns from LegionCore, templates from SkyFire 5.4.8, GUIDs 7600000-7699999. Their scripts
  are in `src/TemucraftPandariaWorldBosses.cpp` (ported from LegionCore 7.3.5, GNU GPL v2). Made by
  `tools/convert.py pwb`. Nalak (Isle of Thunder, map 1064, no client terrain) and Ordos (no script) are not in.
  Battle on the High Seas (1099) is still not done: the server has its terrain, but none of the source databases has
  its spawns (TDB 434: none, SkyFire 548: one, LegionCore: none) and LegionCore has no script for it.
- `temucraft_world_mists_displays.sql`: 5 model ids and 3 object displays the Mists rows use that the DBCs don't have
  (31379, 31460, 60569, 60570, 61807 / 9542, 9371, 26705) get the closest 3.3.5 look: the invisible trigger model for
  the script stalkers, a crypt scarab for The Golden Beetle, the Thunder Bluff elevator car for the Orgrimmar
  elevators, a blacksmith forge and the Coldarra camouflage bubble. `tools/convert.py` makes the same swap.

How the content was fitted to 3.3.5:
- Spawns use GUIDs 7000000-7299999; creature immunities 70000-72999; waypoint paths from 70000000.
- Levels: Cataclysm -5 (85 -> 80, 88 -> 83), Mists -10. Health and damage modifiers are recalculated so a level-80
  group meets about the same difficulty a level-85 (or 90) group did.
- Items: item levels moved to the 3.3.5 range (Cataclysm 346 -> 229, 378 -> 255, 391 -> 265; Mists 463 -> 232,
  553 -> 274, 566 -> 280), stats scaled to match, Mastery turned into Defense on tank items and Crit otherwise;
  armor and weapon damage recalculated for the new item level. The Item.dbc rows are in `item_dbc` for the server
  and in patch-T's Item.dbc for the client.
- Gossip menus are not converted yet, and most boss fights need their C++ scripts (see the boss modules).

`tools/convert.py` and `tools/items.py` rebuild these files from the source databases.
`tools/heroic_convert.py` (with `tools/heroic_vehicles.json`, the Cataclysm vehicle rows from the 4.3.4 Vehicle.dbc
and VehicleSeat.dbc) makes the SQL of the Deadmines and Shadowfang Keep heroics in
[mod-temucraft-instances](https://github.com/Temucraft/mod-temucraft-instances) (the Cataclysm
versions of those dungeons as their heroic modes, GUIDs 7300000-7399999).

The SQL runs through the normal database updater on the next worldserver start.

## Client and server data this goes with

- `Data/patch-T.MPQ`: client DBCs (Open Azeroth's client tables plus the new Crazy/Forever rows).
- `Data/patch-U.MPQ`: Forever sounds used by the new SoundEntries rows.
- `Data/patch-V.MPQ`: Forever maps, the 19 new Eastern Kingdoms tiles, Dalaran in the crater, Scarlet Enclave on 609,
  and Forever's version of the continent tiles Open Azeroth left unchanged.
- Server `Data/dbc`: same rows (backup in `Data/dbc.backup-before-forever-crazy`).

## Forever maps: .tele points

`temucraft_world_forever_tele.sql` (made by `tools/forever_tele.py`) adds a `.tele` point on each of the 27 new
Forever maps that have terrain, named `F<map id><name>`, for example `.tele F2784DemonFallCanyon`. The Forever data
has no spawns, entrances or start points, so each point is the ground near the middle of the map. Some can land
outside the playable part or under a roof (3065 and 3104 came out at height 0): move them in game if needed. The
server needs the map files of each map first (`extract_new_maps.bat`).

## Weather

`temucraft_world_weather.sql` gives 117 zones that had no weather a low chance of it (1-5% per season): rain in green
zones, light rain in cities, steady rain in swamps and wet coasts, rain with winter snow in cold forests, snow in the
north and on high peaks, sand and dust storms in deserts. It covers the old world, Outland, Northrend and the later
continents on the server (Pandaria, Draenor, Broken Isles, Zandalar, Kul Tiras, Shadowlands, Dragon Isles, Khaz Algar).
Zones that already have weather keep theirs (INSERT IGNORE).

## Free-for-all PvP maps (from the Crazy repack)

`temucraft_world_ffa_maps.sql` (made by `tools/ffa_maps.py`) adds the Crazy repack's three free-for-all maps under
their own ids; their terrain is already in the client's patch-Z.MPQ, and the same Map.dbc rows are in patch-X.MPQ.

| Id | Map | Was | `.tele` |
|---|---|---|---|
| 1210 | Valley of Power (Free-for-All) | 1210 | FFAValleyOfPower |
| 1211 | Tol'vir Proving Grounds (Free-for-All) | 1211 | FFATolvir |
| 1246 | Shado-Pan Arena (Free-for-All) | 1212 (our 1212 is a garrison map) | FFAShadoPan |

The server needs their .map / vmap / mmap files: `extract_new_maps.bat` now lists 1210, 1211 and 1246. Crazy's own
spawns on them (mostly 1,410 copies of one custom creature on the Shado-Pan map) are not brought over.

Part of the Temucraft modules for AzerothCore 3.3.5a.
