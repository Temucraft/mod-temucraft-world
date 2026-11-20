-- mod-temucraft-world: Mists (and one Cataclysm) creatures and objects whose model or display id Temucraft's DBCs don't have
-- (CreatureDisplayInfo.dbc and GameObjectDisplayInfo.dbc in patch-T). They get the closest 3.3.5 look.
-- Safe to run again: each update only changes rows that still have the missing id.

-- 31379: second model of three invisible stalkers (World Trigger 59481, Lightning Charge 60241, Ghost Essence 62004)
-- 60569, 60570: Recovery Specialist (90007, the falling ash stalker of Siege of Orgrimmar)
-- 61807: Battleship Cannon (90000, the puddle point stalker of Immerseus)
-- all of them are script stalkers: the invisible trigger model
UPDATE `creature_template_model` SET `CreatureDisplayID` = 11686 WHERE `CreatureID` IN (59481, 60241, 62004) AND `CreatureDisplayID` = 31379;
-- 31379 is also the first model of Orb of the Sun (40835, Rajh in Halls of Origination, temucraft_world_cata.sql),
-- a stalker whose look comes from its spells
UPDATE `creature_template_model` SET `CreatureDisplayID` = 11686 WHERE `CreatureID` = 40835 AND `CreatureDisplayID` = 31379;
UPDATE `creature_template_model` SET `CreatureDisplayID` = 11686 WHERE `CreatureID` = 90007 AND `CreatureDisplayID` IN (60569, 60570);
UPDATE `creature_template_model` SET `CreatureDisplayID` = 11686 WHERE `CreatureID` = 90000 AND `CreatureDisplayID` = 61807;

-- 31460: The Golden Beetle (59545) -> crypt scarab
UPDATE `creature_template_model` SET `CreatureDisplayID` = 10005 WHERE `CreatureID` = 59545 AND `CreatureDisplayID` = 31460;

-- 9542: Orgrimmar elevators (219175, 219176, 219177) -> Thunder Bluff elevator car
UPDATE `gameobject_template` SET `displayId` = 360 WHERE `entry` IN (219175, 219176, 219177) AND `displayId` = 9542;
-- 9371: Doodad_Goblin_Forge_01 (219204) -> blacksmith forge
UPDATE `gameobject_template` SET `displayId` = 355 WHERE `entry` = 219204 AND `displayId` = 9371;
-- 26705: Bubble (220821) -> Coldarra camouflage bubble
UPDATE `gameobject_template` SET `displayId` = 8613 WHERE `entry` = 220821 AND `displayId` = 26705;
