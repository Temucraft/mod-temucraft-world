#!/usr/bin/env python3
"""The fixes made by hand in the release patch-V.MPQ (Forever maps), so a patch-V built again from the Forever data
gets them again. It writes the files to put into the new patch-V, and the names to take out of it:

    python3 forever_fixes.py <new patch-V.MPQ> <client Data folder> <out folder>

<out folder>/files/ gets one file per MPQ name (the name with \\ turned into #), <out folder>/hide.txt the names to
remove. Put them in with any MPQ editor (or `_seams/_scripts/mpq_put.py` and `mpq_hide.py`). The client Data folder is
a Temucraft client with every patch below V (patch-5 = Open Azeroth); the stock files are taken from the highest
patch below V that has them, the same file the game shows when patch-V does not override it.
Needs `mpqtool3.py` (Temucraft `_tools`, or set TEMUCRAFT_TOOLS to its folder).

What and why (2026-11-21 and 2026-11-24):
- TILES_OUT: Forever tiles that left height steps or shading lines against Open Azeroth's tiles (seam fixes, Mulgore).
- STOCK_BUILDINGS: Forever's own copies of stock buildings, placed exactly where the stock one stands. They are
  converted from a later client: groups marked inside that are outside (and the other way round), merged rooms,
  missing doodads. That gives black windows and doors, dark or bright patches inside, no weather or the wrong light.
  The fix puts the stock building (root and every group) under Forever's name, so the map tiles need no change.
- BLOCKERS: invisible collision models Forever put across Dalaran (map 2959), shrunk to scale 1/1024.
"""
import os, sys, struct, re

sys.path.insert(0, os.environ.get('TEMUCRAFT_TOOLS', os.path.expanduser('~/mnt/TemuCraft Server/_tools')))
import mpqtool3

TILES_OUT = [
    # 2026-11-21 seams (Open Azeroth's tile is used)
    'World\\Maps\\Kalimdor\\Kalimdor_40_23.adt', 'World\\Maps\\Kalimdor\\Kalimdor_40_24.adt',
    'World\\Maps\\Kalimdor\\Kalimdor_38_27.adt', 'World\\Maps\\Kalimdor\\Kalimdor_39_26.adt',
    'World\\Maps\\Kalimdor\\Kalimdor_34_36.adt', 'World\\Maps\\Kalimdor\\Kalimdor_28_11.adt',
    # 2026-11-24 Mulgore shading lines
    'World\\Maps\\Kalimdor\\Kalimdor_32_34.adt', 'World\\Maps\\Kalimdor\\Kalimdor_32_35.adt',
    'World\\Maps\\Kalimdor\\Kalimdor_32_37.adt', 'World\\Maps\\Kalimdor\\Kalimdor_33_37.adt',
]
# Forever tiles that must be IN patch-V (2026-11-21 seams, Forever's own version of the Open Azeroth neighbour):
# Azeroth 44_28, Azeroth 33_35, Kalimdor 39_20. Take them from the Forever data if the new build left them out.
TILES_NEEDED = ['World\\Maps\\Azeroth\\Azeroth_44_28.adt', 'World\\Maps\\Azeroth\\Azeroth_33_35.adt',
                'World\\Maps\\Kalimdor\\Kalimdor_39_20.adt']

U = 'world\\wmo\\autogen-names\\unknown\\'
STOCK_BUILDINGS = {   # Forever name -> stock building at the same spot
    U + '21072.wmo': 'World\\wmo\\Azeroth\\Buildings\\GoldshireInn\\GoldshireInn.wmo',          # Goldshire inn
    U + '21064.wmo': 'World\\wmo\\Azeroth\\Buildings\\Stranglethorn_BootyBay\\BootyBay.wmo',    # Booty Bay
    U + '21068.wmo': 'World\\wmo\\Azeroth\\Buildings\\Stranglethorn_BootyBay\\BootyBay_Fortress2.wmo',
    U + '21138.wmo': 'World\\wmo\\Azeroth\\Buildings\\Stormwind\\Stormwind.wmo',                # Stormwind
    'world\\wmo\\autogen-names\\ironforge\\20884.wmo': 'World\\wmo\\KhazModan\\Cities\\Ironforge\\ironforge.wmo',
    U + '21142.wmo': 'World\\wmo\\Kalimdor\\Ogrimmar\\Ogrimmar.wmo',                            # Orgrimmar
    U + '21067.wmo': 'World\\wmo\\Dungeon\\CavernsOfTime\\CavernsOfTime.wmo',                   # Caverns of Time
    U + '21071.wmo': 'World\\wmo\\Azeroth\\Buildings\\GuildHouses\\GuildHouseB.wmo',            # Hillsbrad
    U + '21076.wmo': 'World\\wmo\\Azeroth\\Buildings\\WorldTree\\DuskWorldTree.wmo',            # Duskwood tree
    U + '20543.wmo': 'World\\wmo\\Azeroth\\Buildings\\WorldTree\\TheWorldTreeHyjal.wmo',        # Nordrassil
    U + '21073.wmo': 'World\\wmo\\Kalimdor\\Buildings\\GoblinHut\\KL_Goblin_Ice_Observatory.wmo',  # Winterspring
    U + '21763.wmo': 'World\\wmo\\Kalimdor\\CollidableDoodads\\Teldrassil\\Dock\\TeldrassilPortDock.wmo',
}

BLOCKERS = {'map': '2959', 'tiles': ['31_30', '31_31'], 'model': 'collision_rectangle.m2', 'scale': 1}

BELOW_V = ['patch-U', 'patch-T', 'patch-S', 'patch-R', 'patch-Q', 'patch-P', 'patch-O', 'patch-M', 'patch-J',
           'patch-I', 'patch-H', 'patch-G', 'patch-E', 'patch-C', 'patch-B', 'patch-A', 'patch-8', 'patch-7',
           'patch-6', 'patch-5', 'patch-4', 'patch-3', 'patch-2', 'patch', 'lichking', 'expansion', 'common-2', 'common']

def chunks(d):
    o = 0
    while o + 8 <= len(d):
        yield d[o:o + 4][::-1].decode('latin1'), o + 8, struct.unpack_from('<I', d, o + 4)[0]
        o += 8 + struct.unpack_from('<I', d, o + 4)[0]

def main():
    patch_v, data, out = sys.argv[1:4]
    mpqs = [os.path.join(data, m + '.MPQ') for m in BELOW_V if os.path.exists(os.path.join(data, m + '.MPQ'))]
    def stock(name):
        for m in mpqs:
            d = mpqtool3.read_file(m, name)
            if d is not None: return d
        raise SystemExit('not found below patch-V: ' + name)
    os.makedirs(os.path.join(out, 'files'), exist_ok=True)
    def put(name, d): open(os.path.join(out, 'files', name.replace('\\', '#')), 'wb').write(d)
    for fname, sname in STOCK_BUILDINGS.items():
        root = stock(sname)
        groups = [struct.unpack_from('<7I', root, o)[1] for t, o, s in chunks(root) if t == 'MOHD'][0]
        put(fname, root)
        for g in range(groups): put(fname[:-4] + '_%03d.wmo' % g, stock(sname[:-4] + '_%03d.wmo' % g))
        print(fname, '<-', sname, groups, 'groups')
    for t in BLOCKERS['tiles']:
        name = 'World\\Maps\\%s\\%s_%s.adt' % (BLOCKERS['map'], BLOCKERS['map'], t)
        d = bytearray(mpqtool3.read_file(patch_v, name)); c = {t: (o, s) for t, o, s in chunks(d)}
        names = bytes(d[c['MMDX'][0]:c['MMDX'][0] + c['MMDX'][1]])
        ids = struct.unpack_from('<%dI' % (c['MMID'][1] // 4), d, c['MMID'][0]); n = 0
        for i in range(c['MDDF'][1] // 36):
            o = c['MDDF'][0] + i * 36; nid = struct.unpack_from('<I', d, o)[0]
            if names[ids[nid]:names.index(b'\0', ids[nid])].decode('latin1').lower().endswith(BLOCKERS['model']):
                struct.pack_into('<H', d, o + 32, BLOCKERS['scale']); n += 1
        put(name, bytes(d)); print(name, n, 'blockers shrunk')
    have = set(l.lower() for l in (mpqtool3.read_listfile(patch_v) or []) if l)
    open(os.path.join(out, 'hide.txt'), 'w').write('\n'.join(t for t in TILES_OUT if t.lower() in have) + '\n')
    for t in TILES_NEEDED:
        if t.lower() not in have: print('MISSING in the new patch-V, add it from the Forever data:', t)

if __name__ == '__main__':
    main()
