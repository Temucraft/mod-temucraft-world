-- mod-temucraft-world: cosmetic-only rewards (tools/cosmetics.py).
DELETE FROM `item_template` WHERE `entry` BETWEEN 610060 AND 610069;
INSERT INTO `item_template` (`entry`, `class`, `subclass`, `SoundOverrideSubclass`, `name`, `displayid`, `Quality`, `BuyCount`, `BuyPrice`, `SellPrice`, `InventoryType`, `AllowableClass`, `AllowableRace`, `ItemLevel`, `RequiredLevel`, `RequiredReputationFaction`, `RequiredReputationRank`, `maxcount`, `stackable`, `bonding`, `description`, `Material`, `sheath`, `MaxDurability`, `armor`, `VerifiedBuild`) VALUES
(610060, 4, 0, -1, 'Pilfered Wastewander Wrap', 33848, 2, 1, 150000, 0, 1, -1, -1, 1, 1, 369, 6, 1, 1, 1, 'Cosmetic: no stats, just for the look.', 7, 0, 0, 0, -1811),
(610061, 4, 0, -1, 'Ratchet Dockhand''s Bandana', 28979, 2, 1, 150000, 0, 1, -1, -1, 1, 1, 470, 6, 1, 1, 1, 'Cosmetic: no stats, just for the look.', 8, 0, 0, 0, -1811),
(610062, 4, 0, -1, 'Blackwater Tricorne', 18872, 2, 1, 150000, 0, 1, -1, -1, 1, 1, 21, 6, 1, 1, 1, 'Cosmetic: no stats, just for the look.', 7, 0, 0, 0, -1811),
(610063, 4, 0, -1, 'Everlook Snowtrekker Goggles', 45782, 2, 1, 150000, 0, 1, -1, -1, 1, 1, 577, 6, 1, 1, 1, 'Cosmetic: no stats, just for the look.', 7, 0, 0, 0, -1811),
(610064, 4, 0, -1, 'Timbermaw Hide Mask', 51294, 2, 1, 200000, 0, 1, -1, -1, 1, 1, 576, 6, 1, 1, 1, 'Cosmetic: no stats, just for the look.', 8, 0, 0, 0, -1811),
(610065, 4, 0, -1, 'Cenarion Thornwrap', 44717, 2, 1, 200000, 0, 1, -1, -1, 1, 1, 609, 6, 1, 1, 1, 'Cosmetic: no stats, just for the look.', 7, 0, 0, 0, -1811),
(610066, 4, 0, -1, 'Dawnwatcher''s Shroud', 43221, 2, 1, 200000, 0, 1, -1, -1, 1, 1, 529, 6, 1, 1, 1, 'Cosmetic: no stats, just for the look.', 7, 0, 0, 0, -1811),
(610067, 4, 0, -1, 'Thorium Forgehand Goggles', 19399, 2, 1, 250000, 0, 1, -1, -1, 1, 1, 59, 6, 1, 1, 1, 'Cosmetic: no stats, just for the look.', 7, 0, 0, 0, -1811),
(610068, 4, 0, -1, 'Zandalari Ritual Mask', 25711, 2, 1, 250000, 0, 1, -1, -1, 1, 1, 270, 6, 1, 1, 1, 'Cosmetic: no stats, just for the look.', 8, 0, 0, 0, -1811),
(610069, 4, 0, -1, 'Extravaganza Bait Bucket', 34495, 2, 1, 0, 0, 1, -1, -1, 1, 1, 0, 0, 1, 1, 1, 'Cosmetic: no stats, just for the look.', 6, 0, 0, 0, -1811);
DELETE FROM `npc_vendor` WHERE `item` BETWEEN 610060 AND 610069;
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`, `VerifiedBuild`) VALUES
(8139, 0, 610060, 0, 0, 0, -1811),
(3498, 0, 610061, 0, 0, 0, -1811),
(2663, 0, 610062, 0, 0, 0, -1811),
(11189, 0, 610063, 0, 0, 0, -1811),
(11557, 0, 610064, 0, 0, 0, -1811),
(15293, 0, 610065, 0, 0, 0, -1811),
(10856, 0, 610066, 0, 0, 0, -1811),
(10857, 0, 610066, 0, 0, 0, -1811),
(11536, 0, 610066, 0, 0, 0, -1811),
(12944, 0, 610067, 0, 0, 0, -1811),
(14921, 0, 610068, 0, 0, 0, -1811);
-- Master Angler: the bait bucket as a third choice (next to the two fishing poles)
UPDATE `quest_template` SET `RewardChoiceItemID3` = 610069, `RewardChoiceItemQuantity3` = 1 WHERE `ID` = 8193 AND `RewardChoiceItemID3` IN (0, 610069);
