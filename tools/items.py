#!/usr/bin/env python3
"""item_template rows (and Item.dbc rows) for Cataclysm/Mists loot, from the 4.3.4 and 5.4.8 Item-sparse.db2.

Item levels are moved into the 3.3.5 range (Cata 333 -> 219 ... 391 -> 264, Mists 450 -> 226 ... 572 -> 283),
stats are scaled to match, Mastery becomes Defense (tank items) or Crit, and armor/weapon damage are worked out
for the new item level with the same tables the 4.3.4 client uses.
usage: items.py ITEM_IDS_FILE OUT.sql OUT_ITEMDBC.json"""
import sys, struct, json, os
D = '/mnt/user-data/uploads/Ryans World of Warcraft/Claude scratch/items/'
IDS, OUT, OUTDBC = sys.argv[1:4]
need = {int(x) for x in open(IDS).read().split()}
ours = lambda t: {int(x) for x in open(D + t + '.ids').read().split()}
OUR_ITEM, OUR_DISPLAY, OUR_SPELL, OUR_ENCH, OUR_SET, OUR_RP = (ours(t) for t in ('Item', 'ItemDisplayInfo', 'Spell', 'SpellItemEnchantment', 'ItemSet', 'ItemRandomProperties'))
from pymysql.converters import escape_string

def wdb2(path):
    d = open(path, 'rb').read()
    magic, n, f, rs, ss, h, build, ts, mn, mx, loc, cp = struct.unpack_from('<4s11I', d, 0)
    off = 48
    if mx: off += (mx - mn + 1) * 6
    recs = d[off:off + n * rs]; st = d[off + n * rs:off + n * rs + ss]
    return n, f, rs, recs, st
def dbc(path):
    d = open(path, 'rb').read(); n, f, rs, ss = struct.unpack_from('<4I', d, 4)
    return [d[20 + i * rs:20 + (i + 1) * rs] for i in range(n)]

def sparse(path, extra_flag):
    n, f, rs, recs, st = wdb2(path)
    s = lambda o: st[o:st.index(b'\0', o)].decode('utf8', 'replace') if o < len(st) else ''
    out = {}
    for i in range(n):
        raw = recs[i * rs:(i + 1) * rs]
        u = struct.unpack_from(f'<{f}I', raw); fl = struct.unpack_from(f'<{f}f', raw); si = struct.unpack_from(f'<{f}i', raw)
        if u[0] not in need: continue
        k = 1 if extra_flag else 0          # Mists has a third Flags field
        g = lambda idx: idx + k if idx >= 4 else idx
        r = dict(ID=u[0], Quality=u[1], Flags=u[2], Flags2=u[3], BuyCount=u[g(6)], BuyPrice=u[g(7)], SellPrice=u[g(8)], InventoryType=u[g(9)],
                 AllowableClass=si[g(10)], AllowableRace=si[g(11)], ItemLevel=u[g(12)], RequiredLevel=si[g(13)], RequiredSkill=u[g(14)],
                 RequiredSkillRank=u[g(15)], RequiredSpell=si[g(16)], RequiredHonorRank=u[g(17)], RequiredCityRank=u[g(18)],
                 RequiredReputationFaction=u[g(19)], RequiredReputationRank=u[g(20)], MaxCount=si[g(21)], Stackable=si[g(22)],
                 ContainerSlots=u[g(23)], StatType=[si[g(24) + j] for j in range(10)], StatValue=[si[g(34) + j] for j in range(10)],
                 DamageType=si[g(65)], Delay=u[g(66)], RangedModRange=fl[g(67)], SpellID=[si[g(68) + j] for j in range(5)],
                 SpellTrigger=[si[g(73) + j] for j in range(5)], SpellCharges=[si[g(78) + j] for j in range(5)],
                 SpellCooldown=[si[g(83) + j] for j in range(5)], SpellCategory=[si[g(88) + j] for j in range(5)],
                 SpellCategoryCooldown=[si[g(93) + j] for j in range(5)], Bonding=si[g(98)], Name=s(u[g(99)]), Description=s(u[g(103)]),
                 PageText=u[g(104)], LanguageID=si[g(105)], PageMaterial=si[g(106)], StartQuest=si[g(107)], LockID=u[g(108)], Material=si[g(109)],
                 Sheath=si[g(110)], RandomProperty=si[g(111)], RandomSuffix=u[g(112)], ItemSet=u[g(113)], Area=u[g(114)], Map=si[g(115)],
                 BagFamily=si[g(116)], TotemCategory=si[g(117)], SocketColor=[si[g(118) + j] for j in range(3)],
                 SocketContent=[u[g(121) + j] for j in range(3)], SocketBonus=si[g(124)], GemProperties=si[g(125)],
                 ArmorDamageModifier=fl[g(126)], Duration=si[g(127)], ItemLimitCategory=u[g(128)], HolidayID=si[g(129)],
                 StatScalingFactor=fl[g(130)])
        out[u[0]] = r
    return out
def items_db2(path):
    n, f, rs, recs, st = wdb2(path)
    return {struct.unpack_from('<I', recs, i * rs)[0]: struct.unpack_from('<8i', recs, i * rs) for i in range(n)}

# The struct layout above counts SpellCategoryCooldown as 5 fields (93-97), so Bonding is 98 etc.
src = {}
for tag, extra in (('434', False), ('548', True)):
    sp = sparse(D + f'{tag}_Item-sparse.db2', extra); base = items_db2(D + f'{tag}_Item.db2')
    for i, r in sp.items():
        if i in base: r['base'] = base[i]; r['src'] = tag; src[i] = r     # Mists wins when both have it
print('found', len(src), 'of', len(need))

# ---------------------------------------------------------------- scaling
def new_ilvl(r):
    il = r['ItemLevel']
    if il < 420:          # Cataclysm item levels (whichever client file the record came from)
        if il <= 200: return il
        return max(187, round(200 + (il - 308) * 0.78))
    if il <= 200: return il
    return max(200, round(226 + (il - 450) * 0.47))
FACTOR = {'434': 0.27, '548': 0.07}
VALID = set(range(0, 49)) - {2, 8, 9, 10, 11}

arm_q = {struct.unpack_from('<I', r)[0]: struct.unpack_from('<7f', r, 4) for r in dbc(D + 'ItemArmorQuality.dbc')}
arm_s = {struct.unpack_from('<I', r, 4)[0]: struct.unpack_from('<7f', r, 8) for r in dbc(D + 'ItemArmorShield.dbc')}
arm_t = {struct.unpack_from('<I', r, 4)[0]: struct.unpack_from('<4f', r, 8) for r in dbc(D + 'ItemArmorTotal.dbc')}
arm_l = {struct.unpack_from('<I', r)[0]: struct.unpack_from('<5f', r, 4) for r in dbc(D + 'ArmorLocation.dbc')}
dmg = {n: {struct.unpack_from('<I', r, 32)[0]: struct.unpack_from('<7f', r, 4) for r in dbc(D + f'ItemDamage{n}.dbc')}
       for n in ('Ammo', 'OneHand', 'OneHandCaster', 'Ranged', 'Thrown', 'TwoHand', 'TwoHandCaster', 'Wand')}
def armor(cls, sub, inv, q, il):
    if cls != 4 or q > 6: return 0
    if sub == 6: return round(arm_s.get(il, [0] * 7)[q])
    if not 1 <= sub <= 4: return 0
    inv = 5 if inv == 20 else inv
    if il not in arm_q or il not in arm_t or inv not in arm_l: return 0
    return int(arm_q[il][q] * arm_t[il][sub - 1] * arm_l[inv][sub - 1] + 0.5)
def weapon(cls, sub, inv, q, il, delay, flags2, ssf, adm):
    if cls != 2 or q > 6 or not delay: return 0, 0
    caster = flags2 & 0x200
    store = None
    if inv == 17: store = 'TwoHandCaster' if caster else 'TwoHand'
    elif inv in (15, 25, 26): store = {19: 'Wand', 16: 'Thrown', 2: 'Ranged', 3: 'Ranged', 18: 'Ranged'}.get(sub)
    elif inv in (13, 21, 22): store = 'OneHandCaster' if caster else 'OneHand'
    if not store or il not in dmg[store]: return 0, 0
    avg = delay * dmg[store][il][q] * 0.001
    mx = int((ssf * 0.5 + 1) * avg + 0.5); mn = (1 - ssf * 0.5) * avg
    return max(1, round(mn)), max(1, mx)
DUR = {1: 100, 3: 100, 5: 165, 20: 165, 6: 55, 7: 120, 8: 75, 9: 55, 10: 55, 13: 105, 21: 105, 22: 105, 17: 120, 14: 120, 15: 90, 26: 90, 25: 90}

rows, dbcrows, skipped = [], [], []
for i, r in sorted(src.items()):
    b = r['base']; cls, sub, sound, mat, disp, inv, sheath = b[1], b[2], b[3], b[4], b[5], b[6], b[7]
    if cls == 3: skipped.append((i, 'gem')); continue            # Cataclysm gems: no 3.3.5 gem properties
    il = new_ilvl(r); f = (FACTOR['434'] if r['ItemLevel'] < 420 else FACTOR['548']) if r['ItemLevel'] > 200 else 1
    stats = {}
    tank = any(t in (12, 13, 14) for t in r['StatType'])
    for t, v in zip(r['StatType'], r['StatValue']):
        if not t or not v: continue
        if t == 49: t = 12 if tank else 32                       # Mastery
        if t == 57: t = 35                                       # PvP Power -> Resilience
        if t not in VALID: continue
        stats[t] = stats.get(t, 0) + max(1, round(v * f))
    st = list(stats.items())[:10]
    mn, mx = weapon(cls, sub, inv, r['Quality'], il, r['Delay'], r['Flags2'], r['StatScalingFactor'], r['ArmorDamageModifier'])
    spells = [(s, t, c, cd, cat, ccd) for s, t, c, cd, cat, ccd in zip(r['SpellID'], r['SpellTrigger'], r['SpellCharges'], r['SpellCooldown'],
              r['SpellCategory'], r['SpellCategoryCooldown']) if s > 0 and s in OUR_SPELL]
    while len(spells) < 5: spells.append((0, 0, 0, -1, 0, -1))
    row = dict(entry=i, **{'class': cls}, subclass=sub, SoundOverrideSubclass=sound, name=r['Name'], displayid=disp, Quality=r['Quality'],
               Flags=r['Flags'] & 0x7FFFFFFF, FlagsExtra=r['Flags2'] & 0x3, BuyCount=max(r['BuyCount'], 1), BuyPrice=int(r['BuyPrice'] * 0.25),
               SellPrice=int(r['SellPrice'] * 0.25), InventoryType=inv, AllowableClass=r['AllowableClass'], AllowableRace=r['AllowableRace'],
               ItemLevel=il, RequiredLevel=min(r['RequiredLevel'], 80) if r['RequiredLevel'] > 0 else 0,
               RequiredSkill=r['RequiredSkill'], RequiredSkillRank=min(r['RequiredSkillRank'], 450), requiredspell=0, requiredhonorrank=0,
               RequiredCityRank=0, RequiredReputationFaction=0, RequiredReputationRank=0, maxcount=max(r['MaxCount'], 0),
               stackable=max(r['Stackable'], 1), ContainerSlots=r['ContainerSlots'], ScalingStatDistribution=0, ScalingStatValue=0,
               dmg_min1=mn, dmg_max1=mx, dmg_type1=r['DamageType'] if mn else 0, dmg_min2=0, dmg_max2=0, dmg_type2=0,
               armor=armor(cls, sub, inv, r['Quality'], il), holy_res=0, fire_res=0, nature_res=0, frost_res=0, shadow_res=0, arcane_res=0,
               delay=r['Delay'] if cls == 2 else 0, ammo_type=0, RangedModRange=r['RangedModRange'], bonding=r['Bonding'],
               description=r['Description'], PageText=0, LanguageID=r['LanguageID'], PageMaterial=r['PageMaterial'], startquest=0,
               lockid=0, Material=mat, sheath=sheath, RandomProperty=r['RandomProperty'] if r['RandomProperty'] in OUR_RP else 0, RandomSuffix=0,
               block=0, itemset=r['ItemSet'] if r['ItemSet'] in OUR_SET else 0, MaxDurability=DUR.get(inv, 0) if cls in (2, 4) and inv else 0,
               area=0, Map=0, BagFamily=r['BagFamily'], TotemCategory=r['TotemCategory'],
               socketBonus=r['SocketBonus'] if r['SocketBonus'] in OUR_ENCH else 0, GemProperties=0, RequiredDisenchantSkill=-1,
               ArmorDamageModifier=0, duration=max(r['Duration'], 0), ItemLimitCategory=0, HolidayId=0, ScriptName='', DisenchantID=0,
               FoodType=0, minMoneyLoot=0, maxMoneyLoot=0, flagsCustom=0, VerifiedBuild=0)
    for j in range(10):
        row[f'stat_type{j + 1}'], row[f'stat_value{j + 1}'] = st[j] if j < len(st) else (0, 0)
    for j in range(5):
        s, t, c, cd, cat, ccd = spells[j]
        row.update({f'spellid_{j + 1}': s, f'spelltrigger_{j + 1}': t, f'spellcharges_{j + 1}': c, f'spellppmRate_{j + 1}': 0,
                    f'spellcooldown_{j + 1}': cd, f'spellcategory_{j + 1}': cat, f'spellcategorycooldown_{j + 1}': ccd})
    for j in range(3):
        row[f'socketColor_{j + 1}'] = r['SocketColor'][j] if r['SocketColor'][j] in (1, 2, 4, 8) else 0
        row[f'socketContent_{j + 1}'] = 0
    rows.append(row)
    if i not in OUR_ITEM: dbcrows.append(list(b))
print('item_template rows', len(rows), 'Item.dbc rows to add', len(dbcrows), 'skipped', len(skipped),
      'without display in ItemDisplayInfo', sum(1 for r in rows if r['displayid'] not in OUR_DISPLAY))
cols = [l.strip().split(',') for l in [open('/home/claude/db/item_cols.txt').read()]][0]
def lit(v):
    if isinstance(v, str): return "'" + escape_string(v) + "'"
    if isinstance(v, float): return repr(round(v, 4))
    return str(v)
with open(OUT, 'w', encoding='utf8') as o:
    o.write('-- mod-temucraft-world: items dropped in the converted instances (stats scaled to the 3.3.5 item levels)\n')
    ids = sorted(r['entry'] for r in rows)
    for k in range(0, len(ids), 1000): o.write(f"DELETE FROM `item_template` WHERE `entry` IN ({','.join(map(str, ids[k:k + 1000]))});\n")
    for k in range(0, len(rows), 300):
        o.write(f"INSERT INTO `item_template` ({', '.join('`%s`' % c for c in cols)}) VALUES\n")
        o.write(',\n'.join('(' + ', '.join(lit(r[c]) for c in cols) + ')' for r in rows[k:k + 300]) + ';\n')
json.dump(dbcrows, open(OUTDBC, 'w'))
json.dump(sorted(r['entry'] for r in rows), open(OUT + '.ids', 'w'))
