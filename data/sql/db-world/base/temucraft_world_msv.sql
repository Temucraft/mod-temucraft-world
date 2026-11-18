-- mod-temucraft-world: Mogu'shan Vaults
-- Its spawns now come with the other Mists maps in temucraft_world_mists.sql (LegionCore spawns, which match the
-- ported scripts). This only removes the spawns an earlier version of this file added (GUIDs 7200000-7299999).
DELETE FROM `creature` WHERE `guid` BETWEEN 7200000 AND 7299999;
DELETE FROM `creature_addon` WHERE `guid` BETWEEN 7200000 AND 7299999;
DELETE FROM `creature_formations` WHERE `leaderGUID` BETWEEN 7200000 AND 7299999;
DELETE FROM `gameobject` WHERE `guid` BETWEEN 7200000 AND 7299999;
