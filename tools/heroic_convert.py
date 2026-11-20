#!/usr/bin/env python3
"""Heroic-only port of a Cataclysm-revamped classic dungeon (TrinityCore 4.3.4 / TDB 434.22011 world database) to
AzerothCore's world schema. The normal mode keeps AzerothCore's own classic spawns; the Cataclysm creatures and
objects are spawned for the heroic mode only (spawnMask 2). Levels -5, health and damage scaled like
mod-temucraft-world/tools/convert.py does for the other Cataclysm maps.

Needs the TDB 434.22011 world database (tdb434) and AzerothCore's template ids (ac.ref_ct / ref_gt / ref_it), like
convert.py. The ported C++ sources are read from the modules next to this one (for the script names, and the creature,
object and spell ids they use).

usage: heroic_convert.py dm|sfk OUTDIR"""
import sys, os, re, json, collections, pymysql
HERE = os.path.dirname(os.path.abspath(__file__))
MODULES = os.path.normpath(os.path.join(HERE, '..', '..'))
BASE = os.path.join(HERE, '..', 'data', 'sql', 'db-world', 'base')
from pymysql.converters import escape_string

KEY, OUTDIR = sys.argv[1], sys.argv[2]
CFG = {
    'dm': dict(map=36, guid=7300000, imm=73000, mod='mod-temucraft-deadmines', name='The Deadmines',
               src=os.path.join(MODULES, 'mod-temucraft-deadmines', 'src'), instance='instance_deadmines', sg=7300,
               # entrance quest givers of each faction (their Cataclysm quests don't exist here, and both factions would see both)
               exclude={46612, 46613, 46614, 50595, 491, 46889, 46890, 46902, 46903, 46906, 24935}),
    'sfk': dict(map=33, guid=7350000, imm=73500, mod='mod-temucraft-shadowfang-keep', name='Shadowfang Keep',
                src=os.path.join(MODULES, 'mod-temucraft-shadowfang-keep', 'src'), instance='instance_shadowfang_keep', sg=7350),
}[KEY]
# Cataclysm model ids that neither AzerothCore's nor Temucraft's CreatureDisplayInfo.dbc has: the closest 3.3.5 look
DISPLAY_FIX = {30184: 37710, 30185: 38641, 30186: 38642, 30187: 38811,     # mining monkeys -> Creature\Monkey
               30244: 32385, 30261: 33003, 30262: 39247,                   # hobgoblin lackeys -> Creature\Hobgoblin
               29346: 1140,                                                # Slinky Sharpshiv -> goblin
               32183: 36223,                                               # mystery meat -> the steak's meat
               30054: 34172, 30056: 34173, 30057: 34174,                   # Forsaken Blightspreader -> Veteran Forsaken Trooper
               30210: 8181, 30211: 8181, 30212: 8181, 30213: 8181}         # Rabid Mastiff -> Bloodhound Mastiff
MAP, GUID0, LVL, POWER = CFG['map'], CFG['guid'], 5, 3.5
MODSQL = CFG['mod'].replace('-', '_')
con = pymysql.connect(unix_socket='/home/claude/mdb/s.sock', user='root', db='tdb434', charset='utf8mb4',
                      cursorclass=pymysql.cursors.DictCursor)
def q(sql, *a):
    with con.cursor() as c: c.execute(sql, a); return c.fetchall()
def ids(sql, *a): return {next(iter(r.values())) for r in q(sql, *a)}
def cols(db, t): return [r['c'] for r in q("select column_name c from information_schema.columns where table_schema=%s and table_name=%s order by ordinal_position", db, t)]
def inlist(s): return ','.join(map(str, sorted(s))) or '0'
AC_CT, AC_GT, AC_IT = ids("select entry from ac.ref_ct"), ids("select entry from ac.ref_gt"), ids("select entry from ac.ref_it")
def sql_ids(fn, table, col):
    # the ids a mod-temucraft-world file deletes and adds again
    found = set()
    for m in re.finditer(r"DELETE FROM `%s` WHERE `%s` IN \(([^)]*)\)" % (table, col), open(os.path.join(BASE, fn), encoding='utf8').read()):
        found |= {int(x) for x in m.group(1).split(',')}
    return found
GEN_ITEMS = sql_ids('temucraft_world_items.sql', 'item_template', 'entry')
# templates mod-temucraft-world already adds (other Cataclysm/Mists maps): used as they are, not added again
for f in ('temucraft_world_cata.sql', 'temucraft_world_mists.sql'):
    AC_CT |= sql_ids(f, 'creature_template', 'entry')
    AC_GT |= sql_ids(f, 'gameobject_template', 'entry')
AC = lambda t: cols('ac', t)
os.makedirs(OUTDIR, exist_ok=True)
out = open(f'{OUTDIR}/{MODSQL}_world.sql', 'w', encoding='utf8')
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
        out.write(head + ',\n'.join('(' + ', '.join(lit(r.get(c)) for c in columns) + ')' for r in chunk) + ';\n')
    out.write('\n')
def delete_in(table, col, values, extra=''):
    values = sorted(values)
    for i in range(0, len(values), 1000):
        out.write(f"DELETE FROM `{table}` WHERE {extra}`{col}` IN ({','.join(map(str, values[i:i + 1000]))});\n")
ACCLS = {}
for line in open('/home/claude/db/ac_cls.tsv').read().split('\n')[1:]:
    if line.strip():
        p = line.split('\t'); ACCLS[(int(p[0]), int(p[1]))] = dict(hp=[float(p[2]), float(p[3]), float(p[4])], dmg=[float(p[7]), float(p[8]), float(p[9])])
SRCCLS = {(r['level'], r['class']): r for r in q("select * from creature_classlevelstats")}
def lvl(v): return max(1, v - LVL) if v > 80 else v
def scale(t, hpmod, dmgmod):
    lv, cl, ex = t['maxlevel'], t['unit_class'] or 1, t['exp']
    src, ac = SRCCLS.get((lv, cl)), ACCLS.get((lvl(lv), cl))
    if not src or not ac or lv <= 80: return hpmod, dmgmod
    hs = src.get(f'basehp{ex}') or src.get('basehp2') or 1
    ha = ac['hp'][min(ex, 2)] or 1
    da = ac['dmg'][min(ex, 2)] or 1
    ds = src.get(f'damage_exp{ex}') if ex else src.get('damage_base')
    return round(max(hpmod * hs / (ha * POWER), 0.01), 4), round(min(max(dmgmod * (ds or da) / (da * POWER), 0.1), 80), 4)

# ------------------------------------------------------------------ what the ported C++ uses
srcs = ''.join(open(os.path.join(CFG['src'], f), encoding='utf8').read() for f in os.listdir(CFG['src']) if f.endswith(('.cpp', '.h')))
PORTED = set(re.findall(r'(?:CreatureScript|GameObjectScript|SpellScriptLoader|AuraScriptLoader|InstanceMapScript|AreaTriggerScript|OnlyOnceAreaTriggerScript)\("(\w+)"', srcs))
PORTED |= set(re.findall(r'Register\w+(?:AI|Script)\((\w+)\)', srcs))
PORTED |= set(re.findall(r'Register\w+AIWithFactory\((\w+),', srcs))
PORTED |= set(re.findall(r'RegisterSpellAndAuraScriptPair\((\w+),', srcs))
PORTED.discard('ai_name')
CPP_NPC = {int(v) for v in re.findall(r'\b(?:NPC|BOSS)_\w+\s*=\s*(\d+)', srcs)}
CPP_GO = {int(v) for v in re.findall(r'\bGO_\w+\s*=\s*(\d+)', srcs)}
CPP_SPELL = {int(v) for v in re.findall(r'\bSPELL_\w+\s*=\s*(\d+)', srcs)}

# ------------------------------------------------------------------ spawns (heroic ones only)
cre = [r for r in q("select * from creature where map=%s and spawnMask & 2 order by guid", MAP) if r['id'] not in CFG.get('exclude', ())]
gob = q("select * from gameobject where map=%s and spawnMask & 2 order by guid", MAP)
guidmap = {r['guid']: GUID0 + i for i, r in enumerate(cre)}
gguidmap = {r['guid']: GUID0 + i for i, r in enumerate(gob)}
assert len(cre) < 50000 and len(gob) < 50000

# ------------------------------------------------------------------ creature templates
want = {r['id'] for r in cre} | ids(f"select entry from creature_template where entry in ({inlist(CPP_NPC)})")
want |= ids("select entry from creature_template where ScriptName in (" + (','.join("'%s'" % n for n in PORTED) or "''") + ")")
ss_all = q("select * from smart_scripts")
while True:
    tpl = {t['entry']: t for t in q(f"select * from creature_template where entry in ({inlist(want)})")}
    more = set()
    for t in tpl.values():
        for k in ('difficulty_entry_1', 'difficulty_entry_2', 'difficulty_entry_3'):
            if t[k]: more.add(t[k])
    for s in ss_all:
        if s['source_type'] == 0 and s['entryorguid'] in want and s['action_type'] == 12 and s['action_param1']:
            more.add(s['action_param1'])
    if more <= want: break
    want |= more
# AzerothCore templates the heroic spawns share with the classic dungeon: they get the Cataclysm heroic template as
# their heroic difficulty entry; the classic normal mode doesn't change
shared = {}
for e in sorted({r['id'] for r in cre} | (CPP_NPC & set(tpl))):
    if e in AC_CT and e in tpl and tpl[e]['difficulty_entry_1'] and tpl[e]['difficulty_entry_1'] not in AC_CT:
        shared[e] = tpl[e]['difficulty_entry_1']
new_ct = {e for e in tpl if e not in AC_CT}
heroic_tpl = {tpl[e]['difficulty_entry_1'] for e in tpl if tpl[e]['difficulty_entry_1']}

imm_rows, imm_key = [], {}
def immunity(mech, school):
    if not mech and not school: return 0
    k = (mech, school)
    if k not in imm_key:
        imm_key[k] = CFG['imm'] + len(imm_key)
        imm_rows.append(dict(ID=imm_key[k], SchoolMask=school & 0x7F, DispelTypeMask=0, MechanicsMask=mech, Effects='', Auras='',
                             ImmuneAoE=0, ImmuneChain=0, Comment=f'{CFG["mod"]}: mechanics 0x{mech:X}, schools 0x{school:X}'))
    return imm_key[k]
ct_rows, model_rows, res_rows, spell_rows = [], [], [], []
for e in sorted(new_ct):
    t = tpl[e]
    r = dict(t, exp=min(t['exp'], 2))
    hm, dm = scale(t, t['HealthModifier'], t['DamageModifier'])
    # a template that is only some other template's heroic entry can't have difficulty entries of its own
    r.update(HealthModifier=hm, DamageModifier=dm, minlevel=lvl(t['minlevel']), maxlevel=lvl(t['maxlevel']), speed_swim=1, speed_flight=1,
             detection_range=20, CreatureImmunitiesId=immunity(t['mechanic_immune_mask'], t['spell_school_immune_mask']),
             ScriptName=t['ScriptName'] if t['ScriptName'] in PORTED and e not in heroic_tpl else '', VerifiedBuild=0,
             subname=t['subname'] or '', IconName=t['IconName'] or '', gossip_menu_id=0, AIName=t['AIName'] or '',
             difficulty_entry_2=0, difficulty_entry_3=0)
    if e in heroic_tpl: r.update(difficulty_entry_1=0, AIName='')   # the base template's AI is the one used
    # the base template is only the heroic one's entry point: same expansion, so the core doesn't complain
    if t['difficulty_entry_1'] in tpl: r.update(exp=min(tpl[t['difficulty_entry_1']]['exp'], 2))
    ct_rows.append(r)
    for i in range(4):
        m = t[f'modelid{i + 1}']
        if m: model_rows.append(dict(CreatureID=e, Idx=i, CreatureDisplayID=DISPLAY_FIX.get(m, m), DisplayScale=t['scale'] or 1, Probability=1, VerifiedBuild=0))
    for s in range(1, 7):
        if t[f'resistance{s}']: res_rows.append(dict(CreatureID=e, School=s, Resistance=t[f'resistance{s}'], VerifiedBuild=0))
    for s in range(8):
        if t[f'spell{s + 1}']: spell_rows.append(dict(CreatureID=e, Index=s, Spell=t[f'spell{s + 1}'], VerifiedBuild=0))

out.write(f"-- {CFG['mod']}: {CFG['name']} heroic (Cataclysm version), map {MAP}\n"
          f"-- Converted from the TrinityCore 4.3.4 (TDB 434.22011) world database: creatures and objects of the heroic mode,\n"
          f"-- spawned for the heroic mode only (spawnMask 2); the normal mode keeps AzerothCore's classic spawns.\n"
          f"-- Spawn GUIDs {GUID0}-{GUID0 + 49999}; levels lowered by {LVL} with health and damage rescaled.\n\n")
delete_in('creature_template', 'entry', new_ct)
for tb, c in (('creature_template_model', 'CreatureID'), ('creature_template_resistance', 'CreatureID'), ('creature_template_spell', 'CreatureID'),
              ('creature_template_movement', 'CreatureId'), ('creature_template_addon', 'entry'), ('creature_equip_template', 'CreatureID'),
              ('creature_text', 'CreatureID')):
    delete_in(tb, c, new_ct)
out.write(f"DELETE FROM `creature_immunities` WHERE `ID` BETWEEN {CFG['imm']} AND {CFG['imm'] + 499};\n\n")
emit('creature_immunities', AC('creature_immunities'), imm_rows, 'immunities of the new creatures')
emit('creature_template', AC('creature_template'), ct_rows, 'creature templates (normal ones are only used as the base entry of the heroic ones)')
emit('creature_template_model', AC('creature_template_model'), model_rows)
emit('creature_template_resistance', AC('creature_template_resistance'), res_rows)
emit('creature_template_spell', AC('creature_template_spell'), spell_rows)
if shared:
    out.write('-- classic creatures the heroic mode shares: their heroic difficulty is the Cataclysm heroic template\n')
    for b, h in sorted(shared.items()):
        out.write(f"UPDATE `creature_template` SET `difficulty_entry_1` = {h} WHERE `entry` = {b} AND `difficulty_entry_1` IN (0, {h});\n")
    out.write('\n')
mv = [dict(r, Chase=None) for r in q(f"select * from creature_template_movement where CreatureId in ({inlist(new_ct)})")]
emit('creature_template_movement', AC('creature_template_movement'), mv)
paths = {}
def newpath(old, owner):
    if not old: return 0
    if old not in paths: paths[old] = (owner * 10 + len([p for p in paths.values() if p // 10 == owner])) if owner else (GUID0 * 10 + 499990 + len(paths))
    return paths[old]
tad = q(f"select * from creature_template_addon where entry in ({inlist(new_ct)})")
emit('creature_template_addon', AC('creature_template_addon'), [dict(r, path_id=newpath(r['waypointPathId'], 0), visibilityDistanceType=0, auras=r['auras'] or '') for r in tad])
eq = q(f"select * from creature_equip_template where CreatureID in ({inlist(new_ct)})")
emit('creature_equip_template', AC('creature_equip_template'), [dict(r, VerifiedBuild=0) for r in eq])

# ------------------------------------------------------------------ creature spawns
out.write(f"DELETE FROM `creature` WHERE `guid` BETWEEN {GUID0} AND {GUID0 + 49999};\n")
out.write(f"DELETE FROM `creature_addon` WHERE `guid` BETWEEN {GUID0} AND {GUID0 + 49999};\n")
out.write(f"DELETE FROM `creature_formations` WHERE `leaderGUID` BETWEEN {GUID0} AND {GUID0 + 49999};\n\n")
c_rows = []
for r in cre:
    e = r['id']
    if e not in tpl and e not in AC_CT: continue
    sn = r['ScriptName'] if r['ScriptName'] in PORTED else ''
    # the Cataclysm script of a classic creature goes on the spawn, so the normal mode keeps AzerothCore's
    if not sn and e in AC_CT and e in tpl and tpl[e]['ScriptName'] in PORTED: sn = tpl[e]['ScriptName']
    c_rows.append(dict(guid=guidmap[r['guid']], id=e, map=MAP, zoneId=r['zoneId'] or 0, areaId=r['areaId'] or 0, spawnMask=2,
                       phaseMask=r['phaseMask'] or 1, equipment_id=r['equipment_id'], position_x=r['position_x'], position_y=r['position_y'],
                       position_z=r['position_z'], orientation=r['orientation'], spawntimesecs=r['spawntimesecs'], wander_distance=r['spawndist'],
                       currentwaypoint=r['currentwaypoint'], curhealth=r['curhealth'], curmana=r['curmana'], MovementType=r['MovementType'],
                       npcflag=r['npcflag'], unit_flags=r['unit_flags'], dynamicflags=r['dynamicflags'], ScriptName=sn, VerifiedBuild=0,
                       CreateObject=0, Comment=None))
emit('creature', AC('creature'), c_rows, 'creature spawns (heroic only)')
cad = q(f"select * from creature_addon where guid in ({inlist(guidmap)})")
emit('creature_addon', AC('creature_addon'), [dict(r, guid=guidmap[r['guid']], path_id=newpath(r['waypointPathId'], guidmap[r['guid']]),
                                                     visibilityDistanceType=0, auras=r['auras'] or '') for r in cad])
wp_rows = []
for old, new in paths.items():
    for w in q("select * from waypoint_data where id=%s order by point", old):
        wp_rows.append(dict(id=new, point=w['point'], position_x=w['position_x'], position_y=w['position_y'], position_z=w['position_z'],
                            orientation=w.get('orientation'), velocity=w.get('velocity', 0) or 0, delay=w['delay'],
                            smoothTransition=0, move_type=w.get('move_type', 0) or 0, action=0, action_chance=100, wpguid=0))
if paths: out.write(f"DELETE FROM `waypoint_data` WHERE `id` IN ({inlist(paths.values())});\n")
emit('waypoint_data', AC('waypoint_data'), wp_rows, 'waypoint paths')
fk = cols('tdb434', 'creature_formations')
fr = []
for r in q("select * from creature_formations"):
    l, m = r[fk[0]], r[fk[1]]
    if l in guidmap and m in guidmap:
        fr.append(dict(leaderGUID=guidmap[l], memberGUID=guidmap[m], dist=r[fk[2]], angle=r[fk[3]], groupAI=r[fk[4]],
                       point_1=max(r[fk[5]], 0), point_2=max(r[fk[6]], 0)))
emit('creature_formations', AC('creature_formations'), fr)

# ------------------------------------------------------------------ gameobjects
gwant = {r['id'] for r in gob} | ids(f"select entry from gameobject_template where entry in ({inlist(CPP_GO)})")
gtpl = {t['entry']: t for t in q(f"select * from gameobject_template where entry in ({inlist(gwant)})")}
new_gt = {e for e in gtpl if e not in AC_GT}
delete_in('gameobject_template', 'entry', new_gt); delete_in('gameobject_template_addon', 'entry', new_gt)
gt_rows = []
for e in sorted(new_gt):
    t = gtpl[e]; r = {('Data' + k[4:]) if k.lower().startswith('data') else k: v for k, v in t.items()}
    r.update(ScriptName=t['ScriptName'] if t['ScriptName'] in PORTED else '', VerifiedBuild=0, AIName=t.get('AIName') or '',
             IconName=t['IconName'] or '', castBarCaption=t['castBarCaption'] or '', unk1=t['unk1'] or '')
    gt_rows.append(r)
emit('gameobject_template', AC('gameobject_template'), gt_rows, 'gameobject templates')
emit('gameobject_template_addon', AC('gameobject_template_addon'), q(f"select * from gameobject_template_addon where entry in ({inlist(new_gt)})"))
out.write(f"DELETE FROM `gameobject` WHERE `guid` BETWEEN {GUID0} AND {GUID0 + 49999};\n")
g_rows = []
for r in gob:
    e = r['id']
    if e not in gtpl and e not in AC_GT: continue
    sn = gtpl[e]['ScriptName'] if e in AC_GT and e in gtpl and gtpl[e]['ScriptName'] in PORTED else ''
    g_rows.append(dict(guid=gguidmap[r['guid']], id=e, map=MAP, zoneId=r['zoneId'] or 0, areaId=r['areaId'] or 0, spawnMask=2,
                       phaseMask=r['phaseMask'] or 1, position_x=r['position_x'], position_y=r['position_y'], position_z=r['position_z'],
                       orientation=r['orientation'], rotation0=r['rotation0'], rotation1=r['rotation1'], rotation2=r['rotation2'],
                       rotation3=r['rotation3'], spawntimesecs=r['spawntimesecs'], animprogress=r['animprogress'], state=r['state'],
                       ScriptName=sn, VerifiedBuild=0, Comment=None))
emit('gameobject', AC('gameobject'), g_rows, 'gameobject spawns (heroic only)')

# ------------------------------------------------------------------ loot (items AzerothCore or mod-temucraft-world have)
items_needed, dropped = set(), set()
def loot(table, entries):
    entries = {e for e in entries if e}
    if not entries: return set()
    rows = q(f"select * from {table} where Entry in ({inlist(entries)})")
    conv, refs = [], set()
    for r in rows:
        if r.get('IsCurrency'): continue
        c = dict(r)
        if c['Reference']: refs.add(c['Reference'])
        else:
            items_needed.add(c['Item'])
            if c['Item'] not in AC_IT and c['Item'] not in GEN_ITEMS: dropped.add(c['Item']); continue
        c['Comment'] = c.get('Comment') or None
        conv.append(c)
    delete_in(table, 'Entry', entries)
    emit(table, AC(table), conv)
    return refs
# only the new templates carry loot ids of their own (shared classic ones keep AzerothCore's normal loot; their
# heroic template is new)
lootids = {tpl[e]['lootid'] for e in new_ct}
refs = loot('creature_loot_template', lootids)
refs |= loot('skinning_loot_template', {tpl[e]['skinloot'] for e in new_ct})
refs |= loot('pickpocketing_loot_template', {tpl[e]['pickpocketloot'] for e in new_ct})
refs |= loot('gameobject_loot_template', {gtpl[e]['Data1'] if 'Data1' in gtpl[e] else gtpl[e]['data1'] for e in new_gt if gtpl[e]['type'] in (3, 25)})
seen = set()
while refs - seen:
    batch = refs - seen; seen |= batch
    refs |= loot('reference_loot_template', batch)

# ------------------------------------------------------------------ SmartAI
negs = {-g for g in guidmap}; gnegs = {-g for g in gguidmap}
ss, lists = [], set()
for s in ss_all:
    k = s['entryorguid']
    if (s['source_type'] == 0 and (k in new_ct or k in negs)) or (s['source_type'] == 1 and (k in new_gt or k in gnegs)):
        ss.append(s)
        if s['action_type'] == 80: lists.add(s['action_param1'])
        if s['action_type'] == 87: lists |= {s[f'action_param{i}'] for i in range(1, 7) if s[f'action_param{i}']}
        if s['action_type'] == 88: lists |= set(range(s['action_param1'], s['action_param2'] + 1))
ss += [s for s in ss_all if s['source_type'] == 9 and s['entryorguid'] in lists]
ss_rows = []
for s in ss:
    k = s['entryorguid']
    if k < 0: k = -(guidmap if s['source_type'] == 0 else gguidmap)[-k]
    ss_rows.append(dict(s, entryorguid=k, event_param5=s.get('event_param5', 0) or 0, event_param6=0, target_param4=0, comment=s['comment'] or ''))
for st, keys in ((0, new_ct | {-v for v in guidmap.values()}), (1, new_gt | {-v for v in gguidmap.values()}), (9, lists)):
    if keys: delete_in('smart_scripts', 'entryorguid', keys, f'`source_type`={st} AND ')
emit('smart_scripts', AC('smart_scripts'), ss_rows, 'SmartAI')

# ------------------------------------------------------------------ texts
txt = [dict(r, BroadcastTextId=0, comment=r['comment'] or '') for r in q(f"select * from creature_text where CreatureID in ({inlist(new_ct)})")]
emit('creature_text', AC('creature_text'), txt, 'creature texts')

# ------------------------------------------------------------------ conditions: loot, SmartAI, and the spell targets of the Cataclysm spells
cond = q("select * from conditions")
spells_used = CPP_SPELL | {r['Spell'] for r in spell_rows} | {s['action_param1'] for s in ss_rows if s['action_type'] in (11, 75, 85, 86)}
cr = [c for c in cond if (c['SourceTypeOrReferenceId'] == 1 and c['SourceGroup'] in lootids) or
      (c['SourceTypeOrReferenceId'] == 22 and abs(c['SourceEntry']) in new_ct | set(guidmap)) or
      (c['SourceTypeOrReferenceId'] in (13, 17) and c['SourceEntry'] in spells_used and c['SourceEntry'] > 80864)]
keys = set()
for c in cr:
    if c['SourceTypeOrReferenceId'] == 22 and c['SourceEntry'] < 0: c['SourceEntry'] = -guidmap[-c['SourceEntry']]
    if c['ConditionTypeOrReference'] == 31 and c['ConditionValue1'] == 3 and False: pass
    c['ScriptName'] = c.get('ScriptName') or ''; c['Comment'] = c.get('Comment') or ''
    keys.add((c['SourceTypeOrReferenceId'], c['SourceGroup'], c['SourceEntry'], c['SourceId']))
for k in sorted(keys):
    out.write(f"DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId`={k[0]} AND `SourceGroup`={k[1]} AND `SourceEntry`={k[2]} AND `SourceId`={k[3]};\n")
emit('conditions', AC('conditions'), [dict(c, ErrorType=c.get('ErrorType', 0) or 0, ErrorTextId=c.get('ErrorTextId', 0) or 0) for c in cr])

# ------------------------------------------------------------------ spawn groups (manual spawns the instance script starts)
sg = q(f"select * from spawn_group where (spawnType=0 and spawnId in ({inlist(guidmap)})) or (spawnType=1 and spawnId in ({inlist(gguidmap)}))")
system = ids("select groupId from spawn_group_template where groupFlags & 1")
sg = [r for r in sg if r['groupId'] not in system]
sgids = sorted({r['groupId'] for r in sg})
SGMAP = {g: CFG['sg'] + i for i, g in enumerate(sgids)}
if sgids:
    out.write(f"DELETE FROM `spawn_group` WHERE `groupId` BETWEEN {CFG['sg']} AND {CFG['sg'] + 49};\n")
    out.write(f"DELETE FROM `spawn_group_template` WHERE `groupId` BETWEEN {CFG['sg']} AND {CFG['sg'] + 49};\n")
    emit('spawn_group_template', AC('spawn_group_template'), [dict(r, groupId=SGMAP[r['groupId']]) for r in q(f"select * from spawn_group_template where groupId in ({inlist(sgids)})")], 'spawn groups')
    emit('spawn_group', AC('spawn_group'), [dict(groupId=SGMAP[r['groupId']], spawnType=r['spawnType'],
         spawnId=(guidmap if r['spawnType'] == 0 else gguidmap)[r['spawnId']]) for r in sg])
out.close()

# ------------------------------------------------------------------ script names
sn = [f"-- {CFG['mod']}: script names (from the TrinityCore 4.3.4 world database). The instance script keeps AzerothCore's\n"
      f"-- name `{CFG['instance']}`: the module's copy replaces AzerothCore's and runs the classic script in the normal mode."]
lit2 = lambda s: "'" + escape_string(s) + "'"
inn = ','.join(lit2(n) for n in sorted(PORTED)) or "''"
# templates: only new ones (classic shared ones get the name on their heroic spawns, in the world file)
for r in q(f"select entry, ScriptName from creature_template where ScriptName in ({inn}) order by entry"):
    if r['entry'] in new_ct and r['entry'] not in heroic_tpl: sn.append(f"UPDATE `creature_template` SET `ScriptName` = {lit2(r['ScriptName'])} WHERE `entry` = {r['entry']};")
for r in q(f"select entry, ScriptName from gameobject_template where ScriptName in ({inn}) order by entry"):
    if r['entry'] in new_gt: sn.append(f"UPDATE `gameobject_template` SET `ScriptName` = {lit2(r['ScriptName'])} WHERE `entry` = {r['entry']};")
ssn = q(f"select spell_id, ScriptName from spell_script_names where ScriptName in ({inn}) order by ScriptName, spell_id")
if ssn:
    sn.append(f"DELETE FROM `spell_script_names` WHERE `ScriptName` IN ({','.join(sorted({lit2(r['ScriptName']) for r in ssn}))});")
    sn.append("INSERT INTO `spell_script_names` (`spell_id`, `ScriptName`) VALUES\n" + ',\n'.join(f"({r['spell_id']}, {lit2(r['ScriptName'])})" for r in ssn) + ';')
ats = q(f"select entry, ScriptName from areatrigger_scripts where ScriptName in ({inn})")
if ats:
    sn.append(f"DELETE FROM `areatrigger_scripts` WHERE `entry` IN ({','.join(str(r['entry']) for r in ats)});")
    sn.append("INSERT INTO `areatrigger_scripts` (`entry`, `ScriptName`) VALUES\n" + ',\n'.join(f"({r['entry']}, {lit2(r['ScriptName'])})" for r in ats) + ';')
open(f'{OUTDIR}/{MODSQL}_scriptnames.sql', 'w', encoding='utf8').write('\n'.join(sn) + '\n')

# ------------------------------------------------------------------ report
used_names = set(re.findall(r"'(\w+)'", '\n'.join(sn))) | {r['ScriptName'] for r in c_rows if r['ScriptName']} | {r['ScriptName'] for r in g_rows if r['ScriptName']}
rep = dict(spawngroups=SGMAP, spawns=len(c_rows), objects=len(g_rows), new_ct=len(new_ct), shared=shared, new_gt=len(new_gt), texts=len(txt), smart=len(ss_rows),
           waypoints=len(wp_rows), cond=len(cr), loot_items=len(items_needed), loot_dropped=len(dropped), ported=len(PORTED),
           ported_unused=sorted(PORTED - used_names),
           models=sorted({m['CreatureDisplayID'] for m in model_rows}), godisplays=sorted({gtpl[e]['displayId'] for e in new_gt}),
           spells=sorted(spells_used | {s['spell_id'] for s in ssn}))
json.dump(rep, open(f'{OUTDIR}/{KEY}.report.json', 'w'), indent=1)
print({k: v for k, v in rep.items() if k not in ('models', 'godisplays', 'spells')})
