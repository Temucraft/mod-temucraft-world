-- mod-temucraft-world: script names used by mod-temucraft-scenarios (kept here too because this module's own rows
-- for these creatures and objects are written after the scenario module's SQL; without that module the names are unused)
INSERT INTO `instance_template` (`map`, `parent`, `script`, `allowMount`) VALUES (1048, 0, 'instance_temucraft_unga_ingoo', 0)
  ON DUPLICATE KEY UPDATE `script` = VALUES(`script`);
UPDATE `creature_template` SET `ScriptName` = 'npc_temucraft_unga_bo', `npcflag` = `npcflag` | 1 WHERE `entry` = 62467;
UPDATE `gameobject_template` SET `ScriptName` = 'go_temucraft_unga_brew' WHERE `entry` IN (212248, 212253, 212254, 212255, 212256, 215853);
