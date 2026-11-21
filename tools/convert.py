#!/usr/bin/env python3
"""Converts dungeon/raid content from a TrinityCore 4.3.4 (TDB) or SkyFire 5.4.8 (SFDB) world database to
AzerothCore's world schema, for the maps Temucraft added from the Cataclysm/Mists client data.

Only creatures, gameobjects and items that AzerothCore doesn't already have are added; spawns get new GUIDs in a
reserved range. Levels are moved down to the 3.3.5 range (Cata -5, Mists -10) and the health/damage/armor
modifiers are kept, so they scale from AzerothCore's own level stats.

usage: convert.py 434|548|lc|msv|pwb OUT.sql

pwb (Pandaria world bosses) reads a scratch database `pwb`: views onto every sf548 table except creature, gameobject
and creature_addon; creature_text as a view onto legioncore_world.creature_text; an empty areatrigger_teleport view;
and a creature table (lcx's layout) holding the LegionCore spawns of 60491, 62346 and 69161 on map 870."""
import sys, os, json, collections, pymysql
from pymysql.converters import escape_string

SRC = sys.argv[1]; OUT = sys.argv[2]
CFG = {
    '434': dict(db='tdb434', maps=(644, 657, 720, 754, 755, 939), guid=7000000, imm=70000, lvl=5,
                names={644: 'Halls of Origination', 657: 'The Vortex Pinnacle', 720: 'Firelands',
                       754: 'Throne of the Four Winds', 755: "Lost City of the Tol'vir", 939: 'Well of Eternity'}),
    '548': dict(db='sf548', maps=(960, 1136), guid=7100000, imm=71000, lvl=10,
                names={960: 'Temple of the Jade Serpent', 1136: 'Siege of Orgrimmar'}),
    'lc': dict(db='lcx', maps=(960, 1008, 1136, 1048), guid=7100000, imm=71000, lvl=10,
               names={960: 'Temple of the Jade Serpent', 1008: "Mogu'shan Vaults", 1136: 'Siege of Orgrimmar', 1048: 'Unga Ingoo'}),
    'msv': dict(db='sf548', maps=(1008,), guid=7200000, imm=72000, lvl=10, spawns='crz_',
                names={1008: "Mogu'shan Vaults"}),
    # Pandaria world bosses on the Pandaria continent: only these spawns (LegionCore positions), SkyFire templates
    'pwb': dict(db='pwb', maps=(870,), guid=7600000, imm=76000, lvl=10,
                names={870: 'Pandaria world bosses (Sha of Anger, Galleon, Oondasta)'}),
}[SRC]
SP = CFG.get('spawns', '')      # Mogu'shan Vaults: spawns from the Crazy repack, templates from SkyFire
MOP = SRC in ('548', 'msv', 'lc', 'pwb')
con = pymysql.connect(unix_socket='/home/claude/mdb/s.sock', user='root', db=CFG['db'], charset='utf8mb4',
                      cursorclass=pymysql.cursors.DictCursor)
def q(sql, *a):
    with con.cursor() as c: c.execute(sql, a); return c.fetchall()
def ids(sql, *a): return {next(iter(r.values())) for r in q(sql, *a)}
def cols(db, t): return [r['c'] for r in q("select column_name c from information_schema.columns where table_schema=%s and table_name=%s order by ordinal_position", db, t)]
def has(t): return bool(cols(CFG['db'], t))
AC_CT, AC_GT, AC_IT = ids("select entry from ac.ref_ct"), ids("select entry from ac.ref_gt"), ids("select entry from ac.ref_it")
MAPS = CFG['maps']; inmaps = ','.join(map(str, MAPS))
out = open(OUT, 'w', encoding='utf8')
def lit(v):
    if v is None: return 'NULL'
    if isinstance(v, (bytes, bytearray)): v = v.decode('utf8', 'replace')
    if isinstance(v, str): return "'" + escape_string(v) + "'"
    if isinstance(v, float): return repr(round(v, 6))
    return str(v)
def emit(table, columns, rows, comment=None):
    if not rows: return
    if comment: out.write(f'-- {comment}\n')
    head = f"INSERT INTO `{table}` ({', '.join('`%s`' % c for c in columns)}) VALUES\n"
    for i in range(0, len(rows), 500):
        chunk = rows[i:i + 500]
        out.write(head + ',\n'.join('(' + ', '.join(lit(r[c]) for c in columns) + ')' for r in chunk) + ';\n')
    out.write('\n')
def delete_in(table, col, values):
    values = sorted(values)
    for i in range(0, len(values), 1000):
        out.write(f"DELETE FROM `{table}` WHERE `{col}` IN ({','.join(map(str, values[i:i + 1000]))});\n")
ACCLS = {}
for line in open('/home/claude/db/ac_cls.tsv').read().split('\n')[1:]:
    if line.strip():
        p = line.split('\t'); ACCLS[(int(p[0]), int(p[1]))] = dict(hp=[float(p[2]), float(p[3]), float(p[4])], dmg=[float(p[7]), float(p[8]), float(p[9])])
SRCCLS = {(r['level'], r['class']): r for r in q("select * from creature_classlevelstats")}
POWER = 3.5 if SRC == '434' else 12.0     # how much stronger a level-cap player is there than at 80
def scale(t, hpmod, dmgmod, flatdmg=None):
    """Health and damage modifiers that keep the creature as hard for a level-80 group as it was for the old level cap."""
    lv, cl, ex = t['maxlevel'], t['unit_class'] or 1, t['exp']
    src, ac = SRCCLS.get((lv, cl)), ACCLS.get((lvl(lv), cl))
    if not src or not ac: return hpmod, dmgmod
    hs = src.get(f'basehp{ex}') or src.get('basehp2') or 1
    ha = ac['hp'][min(ex, 2)] or 1
    newhp = hpmod * hs / (ha * POWER)
    da = ac['dmg'][min(ex, 2)] or 1
    if flatdmg is not None: newdmg = flatdmg / (da * POWER)
    else:
        ds = src.get(f'damage_exp{ex}') if ex else src.get('damage_base')
        newdmg = dmgmod * (ds or da) / (da * POWER)
    return round(max(newhp, 0.01), 4), round(min(max(newdmg, 0.1), 80), 4)
# model and object display ids that Temucraft's CreatureDisplayInfo.dbc / GameObjectDisplayInfo.dbc (patch-T) don't
# have: the closest 3.3.5 look (temucraft_world_mists_displays.sql does the same for the converted rows)
MODEL_FIX = {31379: 11686, 60569: 11686, 60570: 11686, 61807: 11686,   # invisible stalkers -> the invisible trigger model
             31460: 10005}                                            # The Golden Beetle -> crypt scarab
GO_DISPLAY_FIX = {9542: 360, 9371: 355, 26705: 8613}                  # Orgrimmar elevators, goblin forge, bubble
MOP_DIFF = {1: 0, 2: 1, 3: 0, 4: 1, 5: 2, 6: 3}   # Mists difficulty id -> 3.3.5 difficulty
def spawnmask(m):
    m = m or 1
    if SRC == '434': return m & 0xFF
    if SRC == 'msv': return 15
    if SRC == 'pwb': return 1
    out = 0
    diff = dict(MOP_DIFF)
    if SRC == 'lc': diff.update({14: 0, 15: 2})           # LegionCore: flexible normal / heroic raid
    for d, a in diff.items():
        if m & (1 << d): out |= 1 << a
    if SRC == 'lc' and m & (1 << 14): out |= 2             # normal covers 10 and 25
    if SRC == 'lc' and m & (1 << 15): out |= 8             # heroic covers 10 and 25
    return out or 1
def lvl(v): return max(1, v - CFG['lvl']) if v > 80 else v
AC = lambda t: cols('ac', t)
stats = collections.OrderedDict()

out.write(f"-- mod-temucraft-world: {', '.join(CFG['names'][m] for m in MAPS)}\n"
          f"-- Converted from the {'TrinityCore 4.3.4 (TDB 434.22011)' if SRC == '434' else ('LegionCore 7.3.5 spawns, scripts and texts with SkyFire 5.4.8 (SFDB 548 27.001) templates where it has them' if SRC == 'lc' else 'SkyFire 5.4.8 (SFDB 548 27.001)' + (' templates and Crazy repack spawns' if SRC == 'msv' else ''))} world database.\n"
          f"-- Spawn GUIDs {CFG['guid']}-{CFG['guid'] + 99999}; levels lowered by {CFG['lvl']}; boss scripts come from C++ modules.\n\n")

# script names of the C++ scripts ported to Temucraft modules (kept on the rows so the order the module SQL runs in
# doesn't matter; without the script module the core just logs that the script is missing)
PORTED = set()
NAMES_FILE = '/mnt/user-data/uploads/Ryans World of Warcraft/Claude scratch/names.json'
if os.path.exists(NAMES_FILE):
    for k, v in json.load(open(NAMES_FILE)).items():
        if (SRC == '434') == (k not in ('tjs', 'msv', 'soo')): PORTED |= set(v['names'])

# ---------------------------------------------------------------- spawns
cre = q(f"select * from {SP}creature where map in ({inmaps}) order by map, guid")
gob = q(f"select * from {SP}gameobject where map in ({inmaps}) order by map, guid")
guidmap = {r['guid']: CFG['guid'] + i for i, r in enumerate(cre)}
gguidmap = {r['guid']: CFG['guid'] + i for i, r in enumerate(gob)}

# ---------------------------------------------------------------- creature templates (closure over heroic entries and summons)
want = {r['id'] for r in cre}
# creatures and objects the ported C++ scripts summon or look for (enum constants in their sources), and every
# template that uses one of their script names
EXTRA = {}
if SRC == '434' and os.path.exists('/mnt/user-data/uploads/Ryans World of Warcraft/Claude scratch/entries434.json'):
    EXTRA = json.load(open('/mnt/user-data/uploads/Ryans World of Warcraft/Claude scratch/entries434.json'))
    names = set()
    for v in json.load(open('/mnt/user-data/uploads/Ryans World of Warcraft/Claude scratch/names.json')).values(): names |= set(v['names'])
    want |= ids(f"select entry from creature_template where entry in ({','.join(map(str, EXTRA['npc'])) or 0})")
    if names: want |= ids("select entry from creature_template where ScriptName in (" + ','.join("'%s'" % n for n in names) + ")")
if SRC == 'pwb':
    # the world boss scripts (src/TemucraftPandariaWorldBosses.cpp) and the creatures they summon (Ire, Bitter
    # Thoughts, the Salyin Warmongers)
    PORTED |= {'boss_sha_of_anger', 'npc_bitter_thoughths', 'npc_ire', 'boss_galion', 'npc_galion', 'boss_oondasta'}
    want |= ids("select entry from creature_template where entry in (60579, 61523, 62351, 62352)")
elif MOP and os.path.exists('/home/claude/db/entries548.json'):
    EX = json.load(open('/home/claude/db/entries548.json'))
    EXTRA = EX[SRC] if SRC in EX else dict(npc=EX['548']['npc'] + EX['msv']['npc'], go=EX['548']['go'] + EX['msv']['go'])
    want |= ids(f"select entry from creature_template where entry in ({','.join(map(str, EXTRA['npc'])) or 0})")
ss_all = q("select * from smart_scripts")
summon_actions = {12: 1, 107: 1}         # SUMMON_CREATURE, SUMMON_CREATURE_GROUP(skip)
while True:
    tpl = q(f"select * from creature_template where entry in ({','.join(map(str, want)) or 0})")
    more = set()
    for t in tpl:
        for k in ('difficulty_entry_1', 'difficulty_entry_2', 'difficulty_entry_3'):
            if t[k]: more.add(t[k])
    for s in ss_all:
        if s['source_type'] == 0 and s['entryorguid'] in want and s['action_type'] == 12 and s['action_param1']:
            more.add(s['action_param1'])
    if more <= want: break
    want |= more
tpl = {t['entry']: t for t in tpl}
new_ct = {e for e in tpl if e not in AC_CT}
stats['creature templates'] = (len(new_ct), len(tpl) - len(new_ct))

# immunities
imm_rows, imm_key = [], {}
def immunity(mech, school):
    if not mech and not school: return 0
    k = (mech, school)
    if k not in imm_key:
        imm_key[k] = CFG['imm'] + len(imm_key)
        imm_rows.append(dict(ID=imm_key[k], SchoolMask=school & 0x7F, DispelTypeMask=0, MechanicsMask=mech, Effects='', Auras='',
                             ImmuneAoE=0, ImmuneChain=0, Comment=f'temucraft-world {SRC}: mechanics 0x{mech:X}, schools 0x{school:X}'))
    return imm_key[k]

ct_rows, model_rows, res_rows, spell_rows = [], [], [], []
if MOP:
    # damage: SkyFire keeps flat min/max damage; turn it into a modifier against a typical level-90 normal creature
    base = sorted((t['mindmg'] + t['maxdmg']) / 2 * max(t['dmg_multiplier'], 0.01) for t in q("select * from creature_template where maxlevel=90 and npc_rank=0 and mindmg>0"))
    DMG90 = base[len(base) // 2] if base else 1000
for e in sorted(new_ct):
    t = tpl[e]
    if SRC == '434':
        r = dict(t, faction=t['faction'], rank=t['rank'], exp=min(t['exp'], 2))
        mech, school = t['mechanic_immune_mask'], t['spell_school_immune_mask']
    else:
        dm = (t['mindmg'] + t['maxdmg']) / 2 * max(t['dmg_multiplier'], 0.01) / DMG90 if t['maxdmg'] else 1
        r = dict(t, faction=t['faction_A'], rank=t['npc_rank'], exp=min(t['exp'], 2), BaseAttackTime=t['baseattacktime'],
                 RangeAttackTime=t['rangeattacktime'], BaseVariance=1, RangeVariance=1, HealthModifier=t['Health_mod'],
                 ManaModifier=t['Mana_mod'], ArmorModifier=t['Armor_mod'], DamageModifier=round(min(max(dm, 0.5), 60), 3),
                 ExperienceModifier=1)
        mech, school = t['mechanic_immune_mask'], 0
    hm, dmm = scale(t, r['HealthModifier'], r['DamageModifier'],
                    (t['mindmg'] + t['maxdmg']) / 2 * max(t['dmg_multiplier'], 0.01) if MOP and t['maxdmg'] else None)
    r.update(HealthModifier=hm, DamageModifier=dmm)
    r.update(minlevel=lvl(t['minlevel']), maxlevel=lvl(t['maxlevel']), speed_swim=1, speed_flight=1,
             detection_range=t.get('detection_range') or 20, CreatureImmunitiesId=immunity(mech, school),
             ScriptName=t['ScriptName'] if t.get('ScriptName') in PORTED else '', VerifiedBuild=0, subname=t['subname'] or '', IconName=t['IconName'] or '',
             gossip_menu_id=0, AIName=t['AIName'] or '')
    if SRC == 'pwb':
        r.update(VehicleId=0)     # the Galleon's Mists vehicle (2232) isn't in the 3.3.5 Vehicle.dbc
        # some SkyFire names are French: the English name from LegionCore's creature cache
        en = q("select Name1 from legioncore_world.creature_template_wdb where Entry=%s", e)
        if en and en[0]['Name1']: r.update(name=en[0]['Name1'])
    ct_rows.append(r)
    for i in range(4):
        m = t[f'modelid{i + 1}']
        if m: model_rows.append(dict(CreatureID=e, Idx=i, CreatureDisplayID=MODEL_FIX.get(m, m), DisplayScale=t['scale'] or 1, Probability=1, VerifiedBuild=0))
    for s in range(1, 7):
        if t[f'resistance{s}']: res_rows.append(dict(CreatureID=e, School=s, Resistance=t[f'resistance{s}'], VerifiedBuild=0))
    for s in range(8):
        if t[f'spell{s + 1}']: spell_rows.append(dict(CreatureID=e, Index=s, Spell=t[f'spell{s + 1}'], VerifiedBuild=0))
delete_in('creature_template', 'entry', new_ct)
for tb, c in (('creature_template_model', 'CreatureID'), ('creature_template_resistance', 'CreatureID'), ('creature_template_spell', 'CreatureID'),
              ('creature_template_movement', 'CreatureId'), ('creature_template_addon', 'entry'), ('creature_equip_template', 'CreatureID'),
              ('creature_text', 'CreatureID')):
    delete_in(tb, c, new_ct)
out.write(f"DELETE FROM `creature_immunities` WHERE `ID` BETWEEN {CFG['imm']} AND {CFG['imm'] + 999};\n\n")
emit('creature_immunities', AC('creature_immunities'), imm_rows, 'immunities of the new creatures')
emit('creature_template', AC('creature_template'), ct_rows, 'creature templates')
emit('creature_template_model', AC('creature_template_model'), model_rows)
emit('creature_template_resistance', AC('creature_template_resistance'), res_rows)
emit('creature_template_spell', AC('creature_template_spell'), spell_rows)

# movement
if SRC == '434':
    mv = [dict(r, Chase=None) for r in q(f"select * from creature_template_movement where CreatureId in ({','.join(map(str, new_ct)) or 0})")]
else:   # InhabitType: 1 ground, 2 water, 4 air, 8 root
    mv = []
    for e in new_ct:
        it = tpl[e]['InhabitType']
        if it not in (3, 0, None):
            mv.append(dict(CreatureId=e, Ground=1 if it & 1 else 0, Swim=1 if it & 2 else 0, Flight=1 if it & 4 else 0,
                           Rooted=1 if it & 8 else 0, Chase=None, Random=None, InteractionPauseTimer=None))
emit('creature_template_movement', AC('creature_template_movement'), mv)

# template addon + paths
paths = {}   # old path id -> new
def newpath(old, owner):
    if not old: return 0
    if old not in paths: paths[old] = 70000000 + (owner - 7000000) * 10 + len(paths) % 10 if owner >= 7000000 else 79000000 + len(paths)
    return paths[old]
pk = 'waypointPathId' if SRC == '434' else 'path_id'
tad = q(f"select * from creature_template_addon where entry in ({','.join(map(str, new_ct)) or 0})")
tad_rows = [dict(r, path_id=newpath(r[pk], 0), visibilityDistanceType=r.get('visibilityDistanceType', 0) or 0, auras=r['auras'] or '') for r in tad]
emit('creature_template_addon', AC('creature_template_addon'), tad_rows)
eq = q(f"select * from creature_equip_template where {'CreatureID' if SRC == '434' else 'entry'} in ({','.join(map(str, new_ct)) or 0})")
if MOP:
    eq = [dict(CreatureID=r['entry'], ID=r.get('id', 1) or 1, ItemID1=r['itemEntry1'], ItemID2=r['itemEntry2'], ItemID3=r['itemEntry3'], VerifiedBuild=0) for r in eq]
emit('creature_equip_template', AC('creature_equip_template'), [dict(r, VerifiedBuild=0) for r in eq])

# ---------------------------------------------------------------- creature spawns
out.write(f"DELETE FROM `creature` WHERE `guid` BETWEEN {CFG['guid']} AND {CFG['guid'] + 99999};\n")
out.write(f"DELETE FROM `creature_addon` WHERE `guid` BETWEEN {CFG['guid']} AND {CFG['guid'] + 99999};\n")
out.write(f"DELETE FROM `creature_formations` WHERE `leaderGUID` BETWEEN {CFG['guid']} AND {CFG['guid'] + 99999};\n\n")
c_rows = []
for r in cre:
    if r['id'] not in tpl and r['id'] not in AC_CT: continue
    c_rows.append(dict(guid=guidmap[r['guid']], id=r['id'], map=r['map'], zoneId=r.get('zoneId', 0) or 0, areaId=r.get('areaId', 0) or 0,
                       spawnMask=spawnmask(r.get('spawnMask', 1)), phaseMask=(r.get('phaseMask') or 1) if SRC == '434' else 1,
                       equipment_id=r['equipment_id'], position_x=r['position_x'], position_y=r['position_y'], position_z=r['position_z'],
                       orientation=r['orientation'], spawntimesecs=r['spawntimesecs'], wander_distance=r['spawndist'],
                       currentwaypoint=r['currentwaypoint'], curhealth=r['curhealth'], curmana=r['curmana'], MovementType=r['MovementType'],
                       npcflag=r['npcflag'], unit_flags=r['unit_flags'], dynamicflags=r['dynamicflags'],
                       ScriptName=r['ScriptName'] if r.get('ScriptName') in PORTED else '', VerifiedBuild=0,
                       CreateObject=0, Comment=None))
emit('creature', AC('creature'), c_rows, 'creature spawns')
if SRC == 'pwb':
    # the Sha of Anger has four spawn points in Kun-Lai Summit: one of them is up at a time
    sha = [r['guid'] for r in c_rows if r['id'] == 60491]
    out.write(f"DELETE FROM `pool_creature` WHERE `pool_entry` = {CFG['imm']};\nDELETE FROM `pool_template` WHERE `entry` = {CFG['imm']};\n")
    out.write(f"INSERT INTO `pool_template` (`entry`, `max_limit`, `description`) VALUES ({CFG['imm']}, 1, 'Sha of Anger (Kun-Lai Summit)');\n")
    out.write("INSERT INTO `pool_creature` (`guid`, `pool_entry`, `chance`, `description`) VALUES\n" +
              ',\n'.join(f"({g}, {CFG['imm']}, 0, 'Sha of Anger')" for g in sha) + ';\n\n')
stats['creature spawns'] = len(c_rows)
cad = q(f"select * from {SP}creature_addon where guid in ({','.join(map(str, guidmap)) or 0})")
emit('creature_addon', AC('creature_addon'), [dict(r, guid=guidmap[r['guid']], path_id=newpath(r[pk], guidmap[r['guid']]),
                                                     visibilityDistanceType=r.get('visibilityDistanceType', 0) or 0, auras=r['auras'] or '') for r in cad])
wp_rows = []
for old, new in paths.items():
    for w in q("select * from waypoint_data where id=%s order by point", old):
        wp_rows.append(dict(id=new, point=w['point'], position_x=w['position_x'], position_y=w['position_y'], position_z=w['position_z'],
                            orientation=w.get('orientation'), velocity=w.get('velocity', 0) or 0, delay=w['delay'],
                            smoothTransition=w.get('smoothTransition', 0) or 0, move_type=w.get('move_type', w.get('move_flag', 0)) or 0,
                            action=0, action_chance=100, wpguid=0))
if paths: out.write(f"DELETE FROM `waypoint_data` WHERE `id` IN ({','.join(map(str, paths.values()))});\n")
emit('waypoint_data', AC('waypoint_data'), wp_rows, 'waypoint paths')
if has('creature_formations'):
    fk = cols(CFG['db'], 'creature_formations')
    fr = []
    for r in q("select * from creature_formations"):
        l, m = r[fk[0]], r[fk[1]]
        if l in guidmap and m in guidmap:
            fr.append(dict(leaderGUID=guidmap[l], memberGUID=guidmap[m], dist=r[fk[2]], angle=r[fk[3]], groupAI=r[fk[4]],
                           point_1=max(r[fk[5]], 0) if len(fk) > 5 else 0, point_2=max(r[fk[6]], 0) if len(fk) > 6 else 0))
    emit('creature_formations', AC('creature_formations'), fr)

# ---------------------------------------------------------------- gameobjects
gwant = {r['id'] for r in gob} | (ids(f"select entry from gameobject_template where entry in ({','.join(map(str, EXTRA.get('go', []))) or 0})") if EXTRA else set())
gwant.discard(0)
gtpl = {t['entry']: t for t in q(f"select * from gameobject_template where entry in ({','.join(map(str, gwant))})")} if gwant else {}
new_gt = {e for e in gtpl if e not in AC_GT}
stats['gameobject templates'] = (len(new_gt), len(gtpl) - len(new_gt))
delete_in('gameobject_template', 'entry', new_gt); delete_in('gameobject_template_addon', 'entry', new_gt)
gt_rows, gta_rows = [], []
for e in sorted(new_gt):
    t = gtpl[e]; r = {('Data' + k[4:]) if k.lower().startswith('data') else k: v for k, v in t.items()}
    r.update(ScriptName=t['ScriptName'] if t.get('ScriptName') in PORTED else '', VerifiedBuild=0, AIName=t.get('AIName') or '', IconName=t['IconName'] or '', castBarCaption=t['castBarCaption'] or '',
             unk1=t['unk1'] or '')
    r['displayId'] = GO_DISPLAY_FIX.get(r['displayId'], r['displayId'])
    gt_rows.append(r)
    if MOP and (t['faction'] or t['flags']): gta_rows.append(dict(entry=e, faction=t['faction'], flags=t['flags'], mingold=0, maxgold=0, artkit0=0, artkit1=0, artkit2=0, artkit3=0))
if SRC == '434':
    gta_rows = [dict(r, artkit0=r['artkit0'], artkit1=r['artkit1'], artkit2=r['artkit2'], artkit3=r['artkit3'])
                for r in q(f"select * from gameobject_template_addon where entry in ({','.join(map(str, new_gt)) or 0})")]
emit('gameobject_template', AC('gameobject_template'), gt_rows, 'gameobject templates')
emit('gameobject_template_addon', AC('gameobject_template_addon'), gta_rows)
out.write(f"DELETE FROM `gameobject` WHERE `guid` BETWEEN {CFG['guid']} AND {CFG['guid'] + 99999};\n")
g_rows = [dict(guid=gguidmap[r['guid']], id=r['id'], map=r['map'], zoneId=r.get('zoneId', 0) or 0, areaId=r.get('areaId', 0) or 0,
               spawnMask=spawnmask(r.get('spawnMask', 1)), phaseMask=(r.get('phaseMask') or 1) if SRC == '434' else 1,
               position_x=r['position_x'], position_y=r['position_y'], position_z=r['position_z'], orientation=r['orientation'],
               rotation0=r['rotation0'], rotation1=r['rotation1'], rotation2=r['rotation2'], rotation3=r['rotation3'],
               spawntimesecs=r['spawntimesecs'], animprogress=r['animprogress'], state=r['state'], ScriptName='', VerifiedBuild=0, Comment=None)
          for r in gob]
emit('gameobject', AC('gameobject'), g_rows, 'gameobject spawns')
stats['gameobject spawns'] = len(g_rows)

# ---------------------------------------------------------------- loot
items_needed = set()
import os, json as _json
GEN_ITEMS = set(_json.load(open('/home/claude/db/out/temucraft_world_items.sql.ids'))) if os.path.exists('/home/claude/db/out/temucraft_world_items.sql.ids') else None
def loot(table, entries, ac_table=None):
    ac_table = ac_table or table
    entries = {e for e in entries if e}
    if not entries or not has(table): return set()
    rows = q(f"select * from {table} where {'Entry' if SRC == '434' else 'entry'} in ({','.join(map(str, entries))})")
    conv, refs = [], set()
    for r in rows:
        if SRC == '434':
            if r.get('IsCurrency'): continue
            c = dict(r)
        else:
            ref = -r['mincountOrRef'] if r['mincountOrRef'] < 0 else 0
            c = dict(Entry=r['entry'], Item=r['item'], Reference=ref, Chance=abs(r['ChanceOrQuestChance']), QuestRequired=1 if r['ChanceOrQuestChance'] < 0 else 0,
                     LootMode=r['lootmode'], GroupId=r['groupid'], MinCount=1 if ref else r['mincountOrRef'], MaxCount=r['maxcount'], Comment=None)
        if c['Reference']: refs.add(c['Reference'])
        else:
            items_needed.add(c['Item'])
            if GEN_ITEMS is not None and c['Item'] not in AC_IT and c['Item'] not in GEN_ITEMS: continue
        c['Comment'] = c.get('Comment') or None
        conv.append(c)
    delete_in(ac_table, 'Entry', entries)
    emit(ac_table, AC(ac_table), conv)
    return refs
lootids = {tpl[e]['lootid'] for e in new_ct}
refs = loot('creature_loot_template', lootids)
refs |= loot('skinning_loot_template', {tpl[e]['skinloot'] for e in new_ct})
refs |= loot('pickpocketing_loot_template', {tpl[e]['pickpocketloot'] for e in new_ct})
golootids = {(gtpl[e].get('data1') if 'data1' in gtpl[e] else gtpl[e]['Data1']) for e in new_gt if gtpl[e]['type'] in (3, 25)}
refs |= loot('gameobject_loot_template', golootids)
seen = set()
while refs - seen:
    batch = refs - seen; seen |= batch
    refs |= loot('reference_loot_template', batch)
stats['loot items'] = len(items_needed)
open(OUT + '.items', 'w').write('\n'.join(str(i) for i in sorted(items_needed - AC_IT)))

# ---------------------------------------------------------------- SmartAI
negs = {-g for g in guidmap}; gnegs = {-g for g in gguidmap}
ss = []
lists = set()
for s in ss_all:
    k = s['entryorguid']
    if (s['source_type'] == 0 and (k in new_ct or k in negs)) or (s['source_type'] == 1 and (k in new_gt or k in gnegs)):
        ss.append(s)
        if s['action_type'] == 80: lists.add(s['action_param1'])
        if s['action_type'] in (87, 88): lists |= {s[f'action_param{i}'] for i in range(1, 7) if s[f'action_param{i}']}
        if s['action_type'] == 88: lists |= set(range(s['action_param1'], s['action_param2'] + 1))
ss += [s for s in ss_all if s['source_type'] == 9 and s['entryorguid'] in lists]
ss_rows = []
for s in ss:
    k = s['entryorguid']
    if k < 0: k = -(guidmap if s['source_type'] == 0 else gguidmap)[-k]
    ss_rows.append(dict(s, entryorguid=k, event_param5=s.get('event_param5', 0) or 0, event_param6=0, target_param4=0, comment=s['comment'] or ''))
for st, keys in ((0, new_ct | {-guidmap[g] for g in guidmap}), (1, new_gt | {-gguidmap[g] for g in gguidmap}), (9, lists)):
    keys = sorted(keys)
    for i in range(0, len(keys), 1000):
        out.write(f"DELETE FROM `smart_scripts` WHERE `source_type`={st} AND `entryorguid` IN ({','.join(map(str, keys[i:i + 1000]))});\n")
emit('smart_scripts', AC('smart_scripts'), ss_rows, 'SmartAI')
stats['smart_scripts'] = len(ss_rows)

# ---------------------------------------------------------------- texts
if SRC == '434':
    txt = q(f"select * from creature_text where CreatureID in ({','.join(map(str, new_ct)) or 0})")
    txt = [dict(r, BroadcastTextId=0, comment=r['comment'] or '') for r in txt]
else:
    txt = q(f"select * from creature_text where entry in ({','.join(map(str, new_ct)) or 0})")
    txt = [dict(CreatureID=r['entry'], GroupID=r['groupid'], ID=r['id'], Text=r['text'], Type=r['type'], Language=r['language'], Probability=r['probability'],
                Emote=r['emote'], Duration=r['duration'], Sound=r['sound'], BroadcastTextId=0, TextRange=0, comment=r['comment'] or '') for r in txt]
emit('creature_text', AC('creature_text'), txt, 'creature texts')
stats['creature texts'] = len(txt)

# ---------------------------------------------------------------- conditions for our loot and SmartAI
cond = q("select * from conditions")
cr = [c for c in cond if (c['SourceTypeOrReferenceId'] == 1 and c['SourceGroup'] in lootids) or
      (c['SourceTypeOrReferenceId'] == 22 and abs(c['SourceEntry']) in new_ct | {g for g in guidmap})]
for c in cr:
    if c['SourceTypeOrReferenceId'] == 22 and c['SourceEntry'] < 0: c['SourceEntry'] = -guidmap[-c['SourceEntry']]
    c['ScriptName'] = c.get('ScriptName') or ''; c['Comment'] = c.get('Comment') or ''
    out.write(f"DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId`={c['SourceTypeOrReferenceId']} AND `SourceGroup`={c['SourceGroup']} AND `SourceEntry`={c['SourceEntry']} AND `SourceId`={c['SourceId']};\n")
emit('conditions', AC('conditions'), [dict(c, ErrorType=c.get('ErrorType', c.get('ErrorTextId', 0)) or 0, ErrorTextId=c.get('ErrorTextId', 0) or 0) for c in cr])

# ---------------------------------------------------------------- teleporters into/out of the maps
at = q(f"select * from areatrigger_teleport where target_map in ({inmaps})")
delete_in('areatrigger_teleport', 'ID', {r.get('ID', r.get('id')) for r in at})
emit('areatrigger_teleport', AC('areatrigger_teleport'), [dict(r, ID=r.get('ID', r.get('id')), Name=r.get('Name', r.get('name'))) for r in at])
open(OUT + '.triggers', 'w').write('\n'.join(str(r.get('ID', r.get('id'))) for r in at))
stats['area triggers'] = len(at)
out.close()
for k, v in stats.items(): print(f'{k}: {v}')
print('model ids:', len({m["CreatureDisplayID"] for m in model_rows}), 'go displays:', len({t["displayId"] for t in gtpl.values()}))
open(OUT + '.models', 'w').write('\n'.join(str(m) for m in sorted({m["CreatureDisplayID"] for m in model_rows})))
open(OUT + '.godisplays', 'w').write('\n'.join(str(t["displayId"]) for t in gtpl.values() if t['entry'] in new_gt))
open(OUT + '.spells', 'w').write('\n'.join(str(s) for s in sorted({r['Spell'] for r in spell_rows} | {s['action_param1'] for s in ss_rows if s['action_type'] in (11, 75, 85, 86)})))
