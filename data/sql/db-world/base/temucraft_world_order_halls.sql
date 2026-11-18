-- mod-temucraft-world: teleports to the order hall maps we have terrain for. The Heart of Azeroth (map 1469, the
-- shaman order hall in the Maelstrom) has client terrain (patch-5) and server maps/vmaps; it is empty (no creatures).
-- The spot is the flat ground at the top of the island (from the server map heights).
DELETE FROM `game_tele` WHERE `name` IN ('HeartOfAzeroth');
INSERT INTO `game_tele` (`id`, `position_x`, `position_y`, `position_z`, `orientation`, `map`, `name`) SELECT MAX(`id`) + 1, 816.7, 1050.0, 51.0, 0.0, 1469, 'HeartOfAzeroth' FROM `game_tele`;
