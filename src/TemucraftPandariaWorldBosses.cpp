/*
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program. If not, see <http://www.gnu.org/licenses/>.
 */

// mod-temucraft-world: the Pandaria world bosses on map 870 (Sha of Anger in Kun-Lai Summit, Galleon in the Valley of
// the Four Winds, Oondasta on the Isle of Giants). Ported to AzerothCore 3.3.5a from The Legion Preservation
// Project's LegionCore 7.3.5 (src/server/scripts/Pandaria: boss_sha_of_anger.cpp, boss_galion.cpp,
// boss_oondasta.cpp), GNU GPL v2.
//
// Changes for 3.3.5:
// - these are open world bosses, so they use ScriptedAI (no instance script, no BossAI);
// - "zone in combat" pulls the players around the boss (the core's DoZoneInCombat only works in dungeons);
// - the Sha of Anger's energy is counted by the script (no RegeneratePower hook here);
// - Dominate Mind's "aggressive behaviour" aura script is left out: it works on a sixth spell effect, and 3.3.5
//   spells have three. Dominate Mind still charms its target.
// Nalak is on the Isle of Thunder (map 1064, no terrain in the client) and Ordos has no script, so they are not here.

#include "CellImpl.h"
#include "CreatureScript.h"
#include "GridNotifiers.h"
#include "GridNotifiersImpl.h"
#include "Player.h"
#include "ScriptedCreature.h"

namespace
{
// Pull every living player within the range into the fight (open world version of DoZoneInCombat).
void PullPlayersAround(Creature* me, float range)
{
    std::list<Player*> players;
    Acore::AnyPlayerInObjectRangeCheck checker(me, range, true, true);
    Acore::PlayerListSearcher<Acore::AnyPlayerInObjectRangeCheck> searcher(me, players, checker);
    Cell::VisitObjects(me, searcher, range);
    for (Player* player : players)
        if (me->IsValidAttackTarget(player))
        {
            me->SetInCombatWith(player);
            player->SetInCombatWith(me);
            me->AddThreat(player, 0.0f);
        }
}
}

// ----------------------------------------------------------------- Sha of Anger (60491)
enum ShaOfAnger
{
    SPELL_SEETHE                = 119487,
    SPELL_ENDLESS_RAGE          = 119587,
    SPELL_BITTER_THOUGHTS       = 119601,
    SPELL_BERSERK               = 47008,
    SPELL_UNLEASHED_WRATH       = 119488,

    SAY_UNLEASHED               = 0,
    SAY_SPAWN                   = 2,
    SAY_RESET                   = 3,
    SAY_KILL                    = 4,
    SAY_AGGRO                   = 5
};

struct boss_sha_of_anger : public ScriptedAI
{
    boss_sha_of_anger(Creature* creature) : ScriptedAI(creature), _summons(creature) { }

    void Reset() override
    {
        Talk(SAY_RESET);
        _summons.DespawnAll();
        me->SetRegeneratingPower(false);
        me->setPowerType(POWER_ENERGY);
        me->SetMaxPower(POWER_ENERGY, 100);
        me->SetPower(POWER_ENERGY, 0);
        _checkDistance = 0;
        _berserk = 0;
        _drain = 0;
        _spawn = 0;
        _regen = 1000;
        _phaseOne = true;
    }

    void JustSummoned(Creature* summon) override { _summons.Summon(summon); }

    void KilledUnit(Unit* who) override
    {
        if (who->IsPlayer())
            Talk(SAY_KILL);
    }

    void JustEngagedWith(Unit* /*who*/) override
    {
        Talk(SAY_AGGRO);
        _checkDistance = 1500;
        _spawn = 5000;
        _berserk = 900000;
    }

    void JustDied(Unit* /*killer*/) override { _summons.DespawnAll(); }

    void UpdateAI(uint32 diff) override
    {
        if (!UpdateVictim())
            return;

        // energy: fills by 2 every 2 seconds in the first phase, the second phase spends 4 a second
        if (_phaseOne)
        {
            if (_regen <= diff)
            {
                me->SetPower(POWER_ENERGY, std::min<uint32>(100, me->GetPower(POWER_ENERGY) + 1));
                _regen = 1000;
            }
            else
                _regen -= diff;
        }

        if (me->HasUnitState(UNIT_STATE_CASTING))
            return;

        if (_drain && !_phaseOne)
        {
            if (_drain <= diff)
            {
                if (me->GetPower(POWER_ENERGY) >= 4)
                {
                    me->SetPower(POWER_ENERGY, me->GetPower(POWER_ENERGY) - 4);
                    _drain = 1000;
                }
                else
                {
                    _drain = 0;
                    _phaseOne = true;
                }
            }
            else
                _drain -= diff;
        }

        if (_checkDistance <= diff)
        {
            if (Unit* victim = me->GetVictim())
            {
                if (me->GetDistance(victim) >= 25.0f)
                {
                    EnterEvadeMode();
                    return;
                }

                if (!me->IsWithinMeleeRange(victim))
                    DoCastAOE(SPELL_SEETHE);

                if (me->GetPower(POWER_ENERGY) >= 100 && _phaseOne)
                {
                    _phaseOne = false;
                    Talk(SAY_UNLEASHED);
                    DoCastSelf(SPELL_UNLEASHED_WRATH);
                    _drain = 1000;
                }
            }
            _checkDistance = 1500;
        }
        else
            _checkDistance -= diff;

        if (_spawn && _phaseOne)
        {
            if (_spawn <= diff)
            {
                Talk(SAY_SPAWN);
                for (uint8 n = 0; n < 3; ++n)
                    if (Unit* target = SelectTarget(SelectTargetMethod::Random, 0, 30.0f, true))
                        DoCast(target, SPELL_ENDLESS_RAGE);
                _spawn = 15000;
            }
            else
                _spawn -= diff;
        }

        if (_berserk)
        {
            if (_berserk <= diff)
            {
                DoCastSelf(SPELL_BERSERK);
                _berserk = 0;
            }
            else
                _berserk -= diff;
        }

        DoMeleeAttackIfReady();
    }

private:
    SummonList _summons;
    uint32 _checkDistance = 0;
    uint32 _berserk = 0;
    uint32 _drain = 0;
    uint32 _spawn = 0;
    uint32 _regen = 1000;
    bool _phaseOne = true;
};

// Bitter Thoughts (61523): an invisible spot that keeps the Bitter Thoughts aura for 30 seconds
struct npc_bitter_thoughths : public ScriptedAI
{
    npc_bitter_thoughths(Creature* creature) : ScriptedAI(creature)
    {
        me->SetReactState(REACT_PASSIVE);
        me->SetDisplayId(11686);
        me->SetUnitFlag(UNIT_FLAG_NOT_SELECTABLE);
        me->SetUnitFlag(UNIT_FLAG_NON_ATTACKABLE);
        me->SetUnitFlag(UNIT_FLAG_DISABLE_MOVE);
    }

    void Reset() override
    {
        me->AddAura(SPELL_BITTER_THOUGHTS, me);
        _unsummon = 30000;
    }

    void JustEngagedWith(Unit* /*who*/) override { }
    void EnterEvadeMode(EvadeReason /*why*/) override { }

    void UpdateAI(uint32 diff) override
    {
        if (_unsummon <= diff)
            me->DespawnOrUnsummon();
        else
            _unsummon -= diff;
    }

private:
    uint32 _unsummon = 30000;
};

// Ire (60579): attacks the nearest player as soon as it appears
struct npc_ire : public ScriptedAI
{
    npc_ire(Creature* creature) : ScriptedAI(creature) { }

    void Reset() override
    {
        if (Player* target = me->SelectNearestPlayer(15.0f))
            AttackStart(target);
    }

    void UpdateAI(uint32 /*diff*/) override
    {
        if (!UpdateVictim())
            return;

        DoMeleeAttackIfReady();
    }
};

// ----------------------------------------------------------------- Galleon (62346) and the Salyin Warmongers
enum Galleon
{
    SPELL_STOMP                 = 121787,
    SPELL_CANNON_BARRAGE        = 121600,
    SPELL_EMPALLING_PULL        = 121747,
    SPELL_GALLEON_BERSERK       = 47008,

    NPC_SALYIN_WARMONGER        = 62351,

    EVENT_STOMP                 = 1,
    EVENT_CANNON,
    EVENT_SPAWN,
    EVENT_BERSERK,
    EVENT_EMPALLING
};

struct boss_galion : public ScriptedAI
{
    boss_galion(Creature* creature) : ScriptedAI(creature), _summons(creature) { }

    void Reset() override
    {
        _events.Reset();
        _summons.DespawnAll();
    }

    void JustSummoned(Creature* summon) override
    {
        _summons.Summon(summon);
        if (Unit* target = SelectTarget(SelectTargetMethod::Random, 0, 60.0f, true))
            summon->AI()->AttackStart(target);
    }

    void JustEngagedWith(Unit* /*who*/) override
    {
        _events.ScheduleEvent(EVENT_STOMP, 50s);
        _events.ScheduleEvent(EVENT_CANNON, 25s);
        _events.ScheduleEvent(EVENT_SPAWN, 60s);
        _events.ScheduleEvent(EVENT_BERSERK, 15min);
    }

    void JustDied(Unit* /*killer*/) override { _summons.DespawnAll(); }

    void UpdateAI(uint32 diff) override
    {
        if (!UpdateVictim())
            return;

        _events.Update(diff);

        if (me->HasUnitState(UNIT_STATE_CASTING))
            return;

        while (uint32 eventId = _events.ExecuteEvent())
        {
            switch (eventId)
            {
                case EVENT_STOMP:
                    DoCastSelf(SPELL_STOMP, true);
                    _events.ScheduleEvent(EVENT_STOMP, 60s);
                    break;
                case EVENT_CANNON:
                    DoCastSelf(SPELL_CANNON_BARRAGE, true);
                    _events.ScheduleEvent(EVENT_CANNON, 60s);
                    break;
                case EVENT_SPAWN:
                    for (uint8 i = 0; i < 6; ++i)
                        me->SummonCreature(NPC_SALYIN_WARMONGER, me->GetPositionX(), me->GetPositionY(), me->GetPositionZ(), me->GetOrientation(),
                                           TEMPSUMMON_CORPSE_TIMED_DESPAWN, 10000);
                    _events.ScheduleEvent(EVENT_SPAWN, 60s);
                    break;
                case EVENT_BERSERK:
                    DoCastSelf(SPELL_GALLEON_BERSERK);
                    break;
                default:
                    break;
            }
        }

        DoMeleeAttackIfReady();
    }

private:
    EventMap _events;
    SummonList _summons;
};

struct npc_galion : public ScriptedAI
{
    npc_galion(Creature* creature) : ScriptedAI(creature) { }

    void Reset() override { _events.Reset(); }

    void JustEngagedWith(Unit* /*who*/) override { _events.ScheduleEvent(EVENT_EMPALLING, 50s); }

    void UpdateAI(uint32 diff) override
    {
        if (!UpdateVictim())
            return;

        _events.Update(diff);

        if (_events.ExecuteEvent() == EVENT_EMPALLING)
        {
            if (Unit* target = SelectTarget(SelectTargetMethod::Random, 1))
                DoCast(target, SPELL_EMPALLING_PULL, true);
            _events.ScheduleEvent(EVENT_EMPALLING, 60s);
        }

        DoMeleeAttackIfReady();
    }

private:
    EventMap _events;
};

// ----------------------------------------------------------------- Oondasta (69161)
enum Oondasta
{
    SPELL_CRUSH                 = 137504,
    SPELL_FRILL_BLAST           = 137505,
    SPELL_PIERCING_ROAR         = 137457,

    EVENT_CRUSH                 = 1,
    EVENT_FRILL_BLAST,
    EVENT_PIERCING_ROAR,
    EVENT_RE_ATTACK
};

struct boss_oondasta : public ScriptedAI
{
    boss_oondasta(Creature* creature) : ScriptedAI(creature) { }

    void Reset() override
    {
        _events.Reset();
        me->SetReactState(REACT_DEFENSIVE);
    }

    void JustEngagedWith(Unit* /*who*/) override
    {
        PullPlayersAround(me, 75.0f);
        _events.ScheduleEvent(EVENT_CRUSH, 60s);
        _events.ScheduleEvent(EVENT_FRILL_BLAST, 25s, 60s);
        _events.ScheduleEvent(EVENT_PIERCING_ROAR, 25s, 30s);
    }

    void UpdateAI(uint32 diff) override
    {
        if (!UpdateVictim() || me->HasUnitState(UNIT_STATE_CASTING))
            return;

        _events.Update(diff);

        if (uint32 eventId = _events.ExecuteEvent())
        {
            switch (eventId)
            {
                case EVENT_CRUSH:
                    if (Unit* victim = me->GetVictim())
                        DoCast(victim, SPELL_CRUSH);
                    _events.ScheduleEvent(EVENT_CRUSH, 26s);
                    break;
                case EVENT_FRILL_BLAST:
                    me->AttackStop();
                    me->SetReactState(REACT_PASSIVE);
                    DoCastAOE(SPELL_FRILL_BLAST);
                    _events.DelayEvents(3s);
                    _events.ScheduleEvent(EVENT_RE_ATTACK, 2500ms);
                    _events.ScheduleEvent(EVENT_FRILL_BLAST, 25s, 60s);
                    break;
                case EVENT_PIERCING_ROAR:
                    DoCastAOE(SPELL_PIERCING_ROAR);
                    _events.ScheduleEvent(EVENT_PIERCING_ROAR, 25s, 30s);
                    break;
                case EVENT_RE_ATTACK:
                    me->SetReactState(REACT_AGGRESSIVE);
                    PullPlayersAround(me, 75.0f);
                    break;
                default:
                    break;
            }
        }

        DoMeleeAttackIfReady();
    }

private:
    EventMap _events;
};

void AddTemucraftPandariaWorldBossScripts()
{
    RegisterCreatureAI(boss_sha_of_anger);
    RegisterCreatureAI(npc_bitter_thoughths);
    RegisterCreatureAI(npc_ire);
    RegisterCreatureAI(boss_galion);
    RegisterCreatureAI(npc_galion);
    RegisterCreatureAI(boss_oondasta);
}
