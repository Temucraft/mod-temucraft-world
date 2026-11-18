/*
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 */

// - Busy spots respawn faster: when an open-world creature dies, every other player near it cuts its respawn time
//   (never below a minimum). Quest givers, rares and world bosses keep their timers.
// - Corpses in dungeons and raids stay longer, so there's time to loot and skin after a pull.

#include "CellImpl.h"
#include "Config.h"
#include "Creature.h"
#include "GridNotifiers.h"
#include "GridNotifiersImpl.h"
#include "Map.h"
#include "Player.h"
#include "ScriptMgr.h"
#include <algorithm>

namespace
{
    struct Settings
    {
        bool respawn = true;
        float radius = 50.0f;
        float perPlayer = 25.0f;        // % faster for each extra player nearby
        uint32 minimum = 30;            // seconds
        uint32 dungeonCorpse = 1800;    // seconds a corpse stays in dungeons and raids (0 = as normal)
    } cfg;

    void LoadSettings()
    {
        cfg.respawn = sConfigMgr->GetOption<bool>("Temucraft.World.BusyRespawn", true);
        cfg.radius = sConfigMgr->GetOption<float>("Temucraft.World.BusyRespawn.Radius", 50.0f);
        cfg.perPlayer = sConfigMgr->GetOption<float>("Temucraft.World.BusyRespawn.PerPlayer", 25.0f);
        cfg.minimum = sConfigMgr->GetOption<uint32>("Temucraft.World.BusyRespawn.Minimum", 30);
        cfg.dungeonCorpse = sConfigMgr->GetOption<uint32>("Temucraft.World.DungeonCorpseSeconds", 1800);
    }

    struct NearbyPlayer
    {
        WorldObject const* center; float range;
        bool operator()(Player* p) const { return p->IsAlive() && !p->IsGameMaster() && center->IsWithinDistInMap(p, range); }
    };
}

class TemucraftWorldRespawn_World : public WorldScript
{
public:
    TemucraftWorldRespawn_World() : WorldScript("TemucraftWorldRespawn_World", { WORLDHOOK_ON_AFTER_CONFIG_LOAD }) { }
    void OnAfterConfigLoad(bool /*reload*/) override { LoadSettings(); }
};

class TemucraftWorldRespawn_Unit : public UnitScript
{
public:
    TemucraftWorldRespawn_Unit() : UnitScript("TemucraftWorldRespawn_Unit", true, { UNITHOOK_ON_UNIT_DEATH }) { }

    void OnUnitDeath(Unit* unit, Unit* /*killer*/) override
    {
        Creature* c = unit ? unit->ToCreature() : nullptr;
        if (!c || !c->GetSpawnId() || c->IsPet() || c->IsSummon())
            return;
        Map* map = c->GetMap();

        if (map->Instanceable())
        {
            if (cfg.dungeonCorpse && map->IsDungeon() && c->GetCorpseDelay() < cfg.dungeonCorpse)
            {
                c->SetCorpseDelay(cfg.dungeonCorpse);
                c->SetCorpseRemoveTime(cfg.dungeonCorpse);
            }
            return;
        }

        if (!cfg.respawn || cfg.perPlayer <= 0.0f || c->IsQuestGiver() || c->isWorldBoss())
            return;
        uint32 const rank = c->GetCreatureTemplate()->rank;
        if (rank == CREATURE_ELITE_RARE || rank == CREATURE_ELITE_RAREELITE || rank == CREATURE_ELITE_WORLDBOSS)
            return;
        uint32 const delay = c->GetRespawnDelay();
        if (delay <= cfg.minimum)
            return;

        std::list<Player*> players;
        NearbyPlayer check{ c, cfg.radius };
        Acore::PlayerListSearcher<NearbyPlayer> searcher(c, players, check);
        Cell::VisitObjects(c, searcher, cfg.radius);
        if (players.size() < 2)
            return;
        float const factor = 1.0f + (players.size() - 1) * cfg.perPlayer / 100.0f;
        uint32 const faster = std::max<uint32>(cfg.minimum, uint32(delay / factor));
        c->SetRespawnTime(faster + c->GetCorpseDelay());
    }
};

void AddTemucraftWorldRespawnScripts()
{
    new TemucraftWorldRespawn_World();
    new TemucraftWorldRespawn_Unit();
}
