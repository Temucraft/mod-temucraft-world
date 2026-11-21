-- mod-temucraft-world: Pandaria world bosses on map 870 (Sha of Anger, Galleon, Oondasta), made by tools/convert.py pwb
-- Spawns from the LegionCore 7.3.5 world database, templates from SkyFire 5.4.8 (SFDB 548 27.001), texts from LegionCore.
-- Spawn GUIDs 7600000-7699999; levels lowered by 10; the scripts are in src/TemucraftPandariaWorldBosses.cpp.

DELETE FROM `creature_template` WHERE `entry` IN (60491,60579,61523,62346,62351,62352,69161);
DELETE FROM `creature_template_model` WHERE `CreatureID` IN (60491,60579,61523,62346,62351,62352,69161);
DELETE FROM `creature_template_resistance` WHERE `CreatureID` IN (60491,60579,61523,62346,62351,62352,69161);
DELETE FROM `creature_template_spell` WHERE `CreatureID` IN (60491,60579,61523,62346,62351,62352,69161);
DELETE FROM `creature_template_movement` WHERE `CreatureId` IN (60491,60579,61523,62346,62351,62352,69161);
DELETE FROM `creature_template_addon` WHERE `entry` IN (60491,60579,61523,62346,62351,62352,69161);
DELETE FROM `creature_equip_template` WHERE `CreatureID` IN (60491,60579,61523,62346,62351,62352,69161);
DELETE FROM `creature_text` WHERE `CreatureID` IN (60491,60579,61523,62346,62351,62352,69161);
DELETE FROM `creature_immunities` WHERE `ID` BETWEEN 76000 AND 76999;

-- immunities of the new creatures
INSERT INTO `creature_immunities` (`ID`, `SchoolMask`, `DispelTypeMask`, `MechanicsMask`, `Effects`, `Auras`, `ImmuneAoE`, `ImmuneChain`, `Comment`) VALUES
(76000, 0, 0, 786382847, '', '', 0, 0, 'temucraft-world pwb: mechanics 0x2EDF3FFF, schools 0x0');

-- creature templates
INSERT INTO `creature_template` (`entry`, `difficulty_entry_1`, `difficulty_entry_2`, `difficulty_entry_3`, `KillCredit1`, `KillCredit2`, `name`, `subname`, `IconName`, `gossip_menu_id`, `minlevel`, `maxlevel`, `exp`, `faction`, `npcflag`, `speed_walk`, `speed_run`, `speed_swim`, `speed_flight`, `detection_range`, `rank`, `dmgschool`, `DamageModifier`, `BaseAttackTime`, `RangeAttackTime`, `BaseVariance`, `RangeVariance`, `unit_class`, `unit_flags`, `unit_flags2`, `dynamicflags`, `family`, `type`, `type_flags`, `lootid`, `pickpocketloot`, `skinloot`, `PetSpellDataId`, `VehicleId`, `mingold`, `maxgold`, `AIName`, `MovementType`, `HoverHeight`, `HealthModifier`, `ManaModifier`, `ArmorModifier`, `ExperienceModifier`, `RacialLeader`, `movementId`, `RegenHealth`, `CreatureImmunitiesId`, `flags_extra`, `ScriptName`, `VerifiedBuild`) VALUES
(60491, 0, 0, 0, 0, 0, 'Sha of Anger', '', '', 0, 80, 80, 2, 14, 0, 2.0, 1.14286, 1, 1, 20.0, 2, 0, 58.1076, 2800, 2000, 1, 1, 1, 4, 0, 0, 0, 4, 2097260, 60491, 0, 0, 0, 0, 3600, 3700, '', 0, 1.0, 1563.2579, 1.0, 1.0, 1, 0, 0, 1, 76000, 0, 'boss_sha_of_anger', 0),
(60579, 0, 0, 0, 0, 0, 'Ire', '', '', 0, 82, 82, 2, 14, 0, 1.0, 1.14286, 1, 1, 20.0, 0, 0, 9.6326, 2000, 2000, 1, 1, 1, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, '', 0, 1.0, 2.6061, 1.0, 1.0, 1, 0, 0, 1, 0, 0, '', 0),
(61523, 0, 0, 0, 0, 0, 'Sha of Anger', '', '', 0, 80, 80, 2, 14, 0, 1.0, 1.14286, 1, 1, 20.0, 0, 0, 5.9359, 900000, 2000, 1, 1, 1, 33554436, 2, 0, 0, 0, 1048576, 0, 0, 0, 0, 0, 0, 0, '', 0, 1.0, 2.6054, 1.0, 1.0, 1, 0, 0, 1, 0, 130, '', 0),
(62346, 0, 0, 0, 0, 0, 'Galleon', '', '', 0, 83, 83, 2, 14, 0, 5.6, 2.0, 1, 1, 20.0, 1, 0, 8.3524, 2000, 2000, 1, 1, 1, 32768, 1073743872, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, '', 0, 1.0, 2.6063, 735.0, 1.0, 1, 0, 912, 1, 0, 0, '', 0),
(62351, 0, 0, 0, 0, 0, 'Salyin Warmonger', '', '', 0, 82, 82, 2, 1771, 0, 1.0, 1.42857, 1, 1, 20.0, 1, 0, 15.2636, 2000, 2000, 1, 1, 2, 33587200, 4196352, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, '', 0, 1.0, 2.6061, 10.0, 1.0, 1, 0, 144, 1, 0, 0, '', 0),
(62352, 0, 0, 0, 0, 0, 'Chief Salyis', '', '', 0, 80, 80, 2, 14, 0, 1.0, 1.42857, 1, 1, 20.0, 1, 0, 11.8105, 2000, 2000, 1, 1, 2, 33587200, 4196352, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, '', 0, 1.0, 2.6054, 30.0, 1.0, 1, 0, 144, 1, 0, 0, '', 0),
(69161, 0, 0, 0, 0, 0, 'Oondasta', '', '', 0, 83, 83, 2, 14, 0, 1.0, 1.14286, 1, 1, 20.0, 1, 0, 8.3524, 2000, 2000, 1, 1, 1, 32768, 2099200, 0, 39, 1, 0, 0, 0, 0, 0, 0, 0, 0, '', 0, 1.0, 2.6063, 1000.0, 1.0, 1, 0, 0, 1, 0, 0, '', 0);

INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) VALUES
(60491, 0, 41448, 1.0, 1, 0),
(60579, 0, 40907, 1.0, 1, 0),
(61523, 0, 1126, 1.0, 1, 0),
(61523, 1, 11686, 1.0, 1, 0),
(62346, 0, 42439, 1.0, 1, 0),
(62351, 0, 42469, 1.0, 1, 0),
(62352, 0, 42468, 1.0, 1, 0),
(69161, 0, 47257, 1.0, 1, 0);

INSERT INTO `creature_template_spell` (`CreatureID`, `Index`, `Spell`, `VerifiedBuild`) VALUES
(60491, 0, 119626, 0),
(60491, 1, 116202, 0),
(60491, 2, 47008, 0),
(60491, 3, 10, 0),
(60491, 4, 55078, 0),
(60491, 5, 113344, 0),
(60491, 6, 31803, 0),
(60491, 7, 45524, 0),
(60579, 1, 129553, 0),
(60579, 2, 31589, 0);

INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) VALUES
(62351, 1, 83081, 0, 0, 0),
(62352, 1, 76267, 0, 0, 0);

DELETE FROM `creature` WHERE `guid` BETWEEN 7600000 AND 7699999;
DELETE FROM `creature_addon` WHERE `guid` BETWEEN 7600000 AND 7699999;
DELETE FROM `creature_formations` WHERE `leaderGUID` BETWEEN 7600000 AND 7699999;

-- creature spawns
INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `currentwaypoint`, `curhealth`, `curmana`, `MovementType`, `npcflag`, `unit_flags`, `dynamicflags`, `ScriptName`, `VerifiedBuild`, `CreateObject`, `Comment`) VALUES
(7600000, 60491, 870, 0, 0, 1, 1, 0, 2924.01, 1476.0, 648.314, 3.58546, 1200, 0.0, 0, 0, 0, 0, 0, 0, 0, '', 0, 0, NULL),
(7600001, 60491, 870, 0, 0, 1, 1, 0, 1958.73, 1634.28, 482.576, 0.491481, 1200, 0.0, 0, 0, 0, 0, 0, 0, 0, '', 0, 0, NULL),
(7600002, 60491, 870, 0, 0, 1, 1, 0, 2737.45, 1711.46, 647.72, 0.249445, 1200, 0.0, 0, 0, 0, 0, 0, 0, 0, '', 0, 0, NULL),
(7600003, 60491, 870, 0, 0, 1, 1, 0, 2361.8, 595.601, 494.394, 0.89169, 1200, 0.0, 0, 0, 0, 0, 0, 0, 0, '', 0, 0, NULL),
(7600004, 62346, 870, 0, 0, 1, 1, 0, -568.413, -94.4931, 156.18, 0.978626, 5400, 0.0, 0, 0, 0, 0, 0, 0, 0, '', 0, 0, NULL),
(7600005, 69161, 870, 0, 0, 1, 1, 0, 6024.96, 1114.3, 56.807, 5.94836, 7200, 0.0, 0, 0, 0, 0, 0, 0, 0, '', 0, 0, NULL);

DELETE FROM `pool_creature` WHERE `pool_entry` = 76000;
DELETE FROM `pool_template` WHERE `entry` = 76000;
INSERT INTO `pool_template` (`entry`, `max_limit`, `description`) VALUES (76000, 1, 'Sha of Anger (Kun-Lai Summit)');
INSERT INTO `pool_creature` (`guid`, `pool_entry`, `chance`, `description`) VALUES
(7600000, 76000, 0, 'Sha of Anger'),
(7600001, 76000, 0, 'Sha of Anger'),
(7600002, 76000, 0, 'Sha of Anger'),
(7600003, 76000, 0, 'Sha of Anger');

DELETE FROM `gameobject` WHERE `guid` BETWEEN 7600000 AND 7699999;
DELETE FROM `creature_loot_template` WHERE `Entry` IN (60491);
DELETE FROM `smart_scripts` WHERE `source_type`=0 AND `entryorguid` IN (-7600005,-7600004,-7600003,-7600002,-7600001,-7600000,60491,60579,61523,62346,62351,62352,69161);
-- creature texts
INSERT INTO `creature_text` (`CreatureID`, `GroupID`, `ID`, `Text`, `Type`, `Language`, `Probability`, `Emote`, `Duration`, `Sound`, `BroadcastTextId`, `TextRange`, `comment`) VALUES
(60491, 1, 0, 'Feed me with your ANGER!', 14, 0, 100.0, 0, 0, 0, 0, 0, ''),
(60491, 2, 0, 'Give in to your anger.', 14, 0, 100.0, 0, 0, 0, 0, 0, ''),
(60491, 2, 1, 'Your rage gives you strength!', 14, 0, 100.0, 0, 0, 0, 0, 0, ''),
(60491, 2, 2, 'Your rage sustains me!', 14, 0, 100.0, 0, 0, 0, 0, 0, ''),
(60491, 2, 3, 'You will not bury me again!', 14, 0, 100.0, 0, 0, 0, 0, 0, ''),
(60491, 2, 4, 'My wrath flows freely!', 14, 0, 100.0, 0, 0, 0, 0, 0, ''),
(60491, 0, 0, 'My fury is UNLEASHED!', 14, 0, 100.0, 0, 0, 0, 0, 0, ''),
(60491, 4, 0, 'Extinguished!', 14, 0, 100.0, 0, 0, 0, 0, 0, ''),
(60491, 4, 1, 'Let your rage consume you.', 14, 0, 100.0, 0, 0, 0, 0, 0, ''),
(60491, 4, 2, 'Does that make you angry?', 14, 0, 100.0, 0, 0, 0, 0, 0, ''),
(60491, 4, 3, 'Feel your rage!', 14, 0, 100.0, 0, 0, 0, 0, 0, ''),
(60491, 5, 0, 'Yes, YES! Bring your rage to bear! Try to strike me down!', 14, 0, 100.0, 0, 0, 0, 0, 0, ''),
(62352, 0, 0, 'Loot and pillage, bwahahaha!', 14, 0, 100.0, 0, 0, 32500, 0, 0, 'Chief Salyis to Galleon');

