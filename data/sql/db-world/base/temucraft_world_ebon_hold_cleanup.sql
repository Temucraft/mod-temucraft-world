-- mod-temucraft-world: map 609 (Ebon Hold / Death Knight start) now uses the Scarlet Enclave terrain from Forever.
-- The old Death Knight starting spawns would float or sit inside the new ground, so they are removed.
-- Everything removed is copied to temucraft_backup_609_* tables first; to undo, copy those rows back.

CREATE TABLE IF NOT EXISTS `temucraft_backup_609_creature` LIKE `creature`;
CREATE TABLE IF NOT EXISTS `temucraft_backup_609_creature_addon` LIKE `creature_addon`;
CREATE TABLE IF NOT EXISTS `temucraft_backup_609_gameobject` LIKE `gameobject`;
CREATE TABLE IF NOT EXISTS `temucraft_backup_609_gameobject_addon` LIKE `gameobject_addon`;
INSERT IGNORE INTO `temucraft_backup_609_creature` SELECT * FROM `creature` WHERE `map` = 609;
INSERT IGNORE INTO `temucraft_backup_609_creature_addon` SELECT a.* FROM `creature_addon` a JOIN `creature` c ON c.`guid` = a.`guid` WHERE c.`map` = 609;
INSERT IGNORE INTO `temucraft_backup_609_gameobject` SELECT * FROM `gameobject` WHERE `map` = 609;
INSERT IGNORE INTO `temucraft_backup_609_gameobject_addon` SELECT a.* FROM `gameobject_addon` a JOIN `gameobject` g ON g.`guid` = a.`guid` WHERE g.`map` = 609;

-- rows that point at the spawns go first
DELETE a FROM `creature_addon` a JOIN `creature` c ON c.`guid` = a.`guid` WHERE c.`map` = 609;
DELETE f FROM `creature_formations` f JOIN `creature` c ON c.`guid` = f.`memberGUID` WHERE c.`map` = 609;
DELETE f FROM `creature_formations` f JOIN `creature` c ON c.`guid` = f.`leaderGUID` WHERE c.`map` = 609;
DELETE p FROM `pool_creature` p JOIN `creature` c ON c.`guid` = p.`guid` WHERE c.`map` = 609;
DELETE e FROM `game_event_creature` e JOIN `creature` c ON c.`guid` = e.`guid` WHERE c.`map` = 609;
DELETE l FROM `linked_respawn` l JOIN `creature` c ON c.`guid` = l.`guid` WHERE c.`map` = 609 AND l.`linkType` IN (0, 1);
DELETE a FROM `gameobject_addon` a JOIN `gameobject` g ON g.`guid` = a.`guid` WHERE g.`map` = 609;
DELETE p FROM `pool_gameobject` p JOIN `gameobject` g ON g.`guid` = p.`guid` WHERE g.`map` = 609;
DELETE e FROM `game_event_gameobject` e JOIN `gameobject` g ON g.`guid` = e.`guid` WHERE g.`map` = 609;
DELETE l FROM `linked_respawn` l JOIN `gameobject` g ON g.`guid` = l.`guid` WHERE g.`map` = 609 AND l.`linkType` IN (2, 3);

DELETE FROM `creature` WHERE `map` = 609;
DELETE FROM `gameobject` WHERE `map` = 609;
