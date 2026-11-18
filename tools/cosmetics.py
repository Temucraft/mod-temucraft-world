#!/usr/bin/env python3
"""Cosmetic-only rewards: hats, masks and goggles with no stats, sold at Revered by reputation vendors (and one for
the Stranglethorn Fishing Extravaganza's Master Angler). Anyone can wear them (Miscellaneous armor), they never break
(no durability) and they bind on pickup.

Writes data/sql/db-world/base/temucraft_world_cosmetics.sql (item_template, npc_vendor, the quest reward).
With --client the items also go into the client's Item.dbc (patch-T.MPQ, game closed), so they show the right model
before the server answers."""
import os, sys
sys.path.insert(0, os.path.expanduser('~/tc'))
import dbctool as T

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
REVERED = 6
DESC = 'Cosmetic: no stats, just for the look.'

# id, name, looks like item, faction, vendor (0: quest reward), price (copper)
ITEMS = [
    (610060, "Pilfered Wastewander Wrap",   21472, 369, 8139,  150000),  # Gadgetzan: Jabbey
    (610061, "Ratchet Dockhand's Bandana",  15167, 470, 3498,  150000),  # Ratchet: Jazzik
    (610062, "Blackwater Tricorne",         10030, 21,  2663,  150000),  # Booty Bay: Narkk
    (610063, "Everlook Snowtrekker Goggles", 41112, 577, 11189, 150000), # Everlook: Qia
    (610064, "Timbermaw Hide Mask",         37391, 576, 11557, 200000),  # Timbermaw Hold: Meilosh
    (610065, "Cenarion Thornwrap",          10175, 609, 15293, 200000),  # Cenarion Circle: Aendel Windspear
    (610066, "Dawnwatcher's Shroud",        30931, 529, 10856, 200000),  # Argent Dawn quartermasters
    (610067, "Thorium Forgehand Goggles",   10500, 59,  12944, 250000),  # Thorium Brotherhood: Lokhtos
    (610068, "Zandalari Ritual Mask",       8201,  270, 14921, 250000),  # Zandalar Tribe: Rin'wosho
    (610069, "Extravaganza Bait Bucket",    20640, 0,   0,     0),       # Master Angler (quest 8193)
]
MORE_VENDORS = {610066: [10857, 11536]}   # the other Argent Dawn quartermasters
MASTER_ANGLER = 8193

# looks of the originals (displayid, material, sheath), from item_template
LOOKS = {21472: (33848, 7), 15167: (28979, 8), 10030: (18872, 7), 41112: (45782, 7), 37391: (51294, 8),
         10175: (44717, 7), 30931: (43221, 7), 10500: (19399, 7), 8201: (25711, 8), 20640: (34495, 6)}


def q(s): return "'" + s.replace("'", "''") + "'"


def sql():
    out = ['-- mod-temucraft-world: cosmetic-only rewards (tools/cosmetics.py).',
           'DELETE FROM `item_template` WHERE `entry` BETWEEN 610060 AND 610069;',
           'INSERT INTO `item_template` (`entry`, `class`, `subclass`, `SoundOverrideSubclass`, `name`, `displayid`, `Quality`, '
           '`BuyCount`, `BuyPrice`, `SellPrice`, `InventoryType`, `AllowableClass`, `AllowableRace`, `ItemLevel`, `RequiredLevel`, '
           '`RequiredReputationFaction`, `RequiredReputationRank`, `maxcount`, `stackable`, `bonding`, `description`, `Material`, '
           '`sheath`, `MaxDurability`, `armor`, `VerifiedBuild`) VALUES']
    rows = []
    for entry, name, like, faction, vendor, price in ITEMS:
        display, material = LOOKS[like]
        rows.append('(%d, 4, 0, -1, %s, %d, 2, 1, %d, 0, 1, -1, -1, 1, 1, %d, %d, 1, 1, 1, %s, %d, 0, 0, 0, -1811)' % (
            entry, q(name), display, price, faction, REVERED if faction else 0, q(DESC), material))
    out.append(',\n'.join(rows) + ';')
    out.append('DELETE FROM `npc_vendor` WHERE `item` BETWEEN 610060 AND 610069;')
    vend = []
    for entry, name, like, faction, vendor, price in ITEMS:
        for v in ([vendor] if vendor else []) + MORE_VENDORS.get(entry, []):
            vend.append('(%d, 0, %d, 0, 0, 0, -1811)' % (v, entry))
    out.append('INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`, `VerifiedBuild`) VALUES\n' +
               ',\n'.join(vend) + ';')
    out.append('-- Master Angler: the bait bucket as a third choice (next to the two fishing poles)')
    out.append('UPDATE `quest_template` SET `RewardChoiceItemID3` = 610069, `RewardChoiceItemQuantity3` = 1 '
               'WHERE `ID` = %d AND `RewardChoiceItemID3` IN (0, 610069);' % MASTER_ANGLER)
    return '\n'.join(out) + '\n'


path = os.path.join(MOD, 'data', 'sql', 'db-world', 'base', 'temucraft_world_cosmetics.sql')
open(path, 'w').write(sql())
print('wrote', path)

if '--client' in sys.argv:
    tmp = '/tmp/Item_client.dbc'
    assert T.client_get('DBFilesClient\\Item.dbc', tmp), 'no Item.dbc in patch-T'
    dbc = T.DBC(tmp)
    for entry, name, like, faction, vendor, price in ITEMS:
        display, material = LOOKS[like]
        dbc.put([entry, 4, 0, 0xFFFFFFFF, material, display, 1, 0])
    dbc.save(tmp)
    T.client_put({'DBFilesClient\\Item.dbc': tmp})
    print('client Item.dbc updated')
