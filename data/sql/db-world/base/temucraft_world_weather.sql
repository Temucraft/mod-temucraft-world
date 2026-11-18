-- mod-temucraft-world: thematic weather for zones without any, at low chances (1-5% per season) so it shows up now
-- and then: rain in green zones, light rain in cities, steady rain in swamps and wet coasts, snow in the north and on
-- high peaks, sand and dust storms in deserts. INSERT IGNORE: zones that already have weather keep theirs.
-- Values: spring/summer/fall/winter, each rain, snow, storm (storm = sand/dust storm). Zones underground, under water,
-- in the Twisting Nether or otherwise without a sky are left out.
INSERT IGNORE INTO `game_weather` (`zone`, `spring_rain_chance`, `spring_snow_chance`, `spring_storm_chance`, `summer_rain_chance`, `summer_snow_chance`, `summer_storm_chance`, `fall_rain_chance`, `fall_snow_chance`, `fall_storm_chance`, `winter_rain_chance`, `winter_snow_chance`, `winter_storm_chance`, `ScriptName`) VALUES
(4, 0, 0, 3, 0, 0, 4, 0, 0, 3, 0, 0, 2, ''), -- Blasted Lands
(14, 0, 0, 3, 0, 0, 4, 0, 0, 3, 0, 0, 2, ''), -- Durotar
(17, 0, 0, 3, 0, 0, 4, 0, 0, 3, 0, 0, 2, ''), -- The Barrens
(400, 0, 0, 3, 0, 0, 4, 0, 0, 3, 0, 0, 2, ''), -- Thousand Needles
(1637, 0, 0, 3, 0, 0, 4, 0, 0, 3, 0, 0, 2, ''), -- Orgrimmar
(3478, 0, 0, 3, 0, 0, 4, 0, 0, 3, 0, 0, 2, ''), -- Gates of Ahn'Qiraj
(5034, 0, 0, 3, 0, 0, 4, 0, 0, 3, 0, 0, 2, ''), -- Uldum
(5695, 0, 0, 3, 0, 0, 4, 0, 0, 3, 0, 0, 2, ''), -- Ahn'Qiraj: The Fallen Kingdom
(3483, 0, 0, 3, 0, 0, 4, 0, 0, 3, 0, 0, 2, ''), -- Hellfire Peninsula
(3522, 0, 0, 3, 0, 0, 4, 0, 0, 3, 0, 0, 2, ''), -- Blade's Edge Mountains
(6138, 0, 0, 3, 0, 0, 4, 0, 0, 3, 0, 0, 2, ''), -- Dread Wastes
(8501, 0, 0, 3, 0, 0, 4, 0, 0, 3, 0, 0, 2, ''), -- Vol'dun
(8, 5, 0, 0, 5, 0, 0, 5, 0, 0, 5, 0, 0, ''), -- Swamp of Sorrows
(4714, 5, 0, 0, 5, 0, 0, 5, 0, 0, 5, 0, 0, ''), -- Gilneas
(16756, 5, 0, 0, 5, 0, 0, 5, 0, 0, 5, 0, 0, ''), -- Ruins of Gilneas
(17065, 5, 0, 0, 5, 0, 0, 5, 0, 0, 5, 0, 0, ''), -- Gilneas
(61017, 5, 0, 0, 5, 0, 0, 5, 0, 0, 5, 0, 0, ''), -- Gilneas
(495, 5, 0, 0, 5, 0, 0, 5, 0, 0, 5, 0, 0, ''), -- Howling Fjord
(8500, 5, 0, 0, 5, 0, 0, 5, 0, 0, 5, 0, 0, ''), -- Nazmir
(8721, 5, 0, 0, 5, 0, 0, 5, 0, 0, 5, 0, 0, ''), -- Drustvar
(9042, 5, 0, 0, 5, 0, 0, 5, 0, 0, 5, 0, 0, ''), -- Stormsong Valley
(9466, 5, 0, 0, 5, 0, 0, 5, 0, 0, 5, 0, 0, ''), -- The Rotting Mire
(4922, 5, 0, 0, 5, 0, 0, 5, 0, 0, 5, 0, 0, ''), -- Highlands
(616, 4, 1, 0, 4, 0, 0, 4, 2, 0, 0, 5, 0, ''), -- Hyjal
(394, 4, 1, 0, 4, 0, 0, 4, 2, 0, 0, 5, 0, ''), -- Grizzly Hills
(3537, 4, 1, 0, 4, 0, 0, 4, 2, 0, 0, 5, 0, ''), -- Borean Tundra
(66, 4, 1, 0, 4, 0, 0, 4, 2, 0, 0, 5, 0, ''), -- Zul'Drak
(7503, 4, 1, 0, 4, 0, 0, 4, 2, 0, 0, 5, 0, ''), -- Highmountain
(10713, 4, 1, 0, 4, 0, 0, 4, 2, 0, 0, 5, 0, ''), -- Highmountain
(6555, 4, 1, 0, 4, 0, 0, 4, 2, 0, 0, 5, 0, ''), -- Northern Elwynn Mountains
(11026, 4, 1, 0, 4, 0, 0, 4, 2, 0, 0, 5, 0, ''), -- Kun-Lai Summit
(61005, 0, 4, 0, 0, 2, 0, 0, 4, 0, 0, 5, 0, ''), -- Icepoint Rock
(65, 0, 4, 0, 0, 2, 0, 0, 4, 0, 0, 5, 0, ''), -- Dragonblight
(67, 0, 4, 0, 0, 2, 0, 0, 4, 0, 0, 5, 0, ''), -- The Storm Peaks
(210, 0, 4, 0, 0, 2, 0, 0, 4, 0, 0, 5, 0, ''), -- Icecrown
(2817, 0, 4, 0, 0, 2, 0, 0, 4, 0, 0, 5, 0, ''), -- Crystalsong Forest
(4197, 0, 4, 0, 0, 2, 0, 0, 4, 0, 0, 5, 0, ''), -- Wintergrasp
(4742, 0, 4, 0, 0, 2, 0, 0, 4, 0, 0, 5, 0, ''), -- Hrothgar's Landing
(5841, 0, 4, 0, 0, 2, 0, 0, 4, 0, 0, 5, 0, ''), -- Kun-Lai Summit
(6720, 0, 4, 0, 0, 2, 0, 0, 4, 0, 0, 5, 0, ''), -- Frostfire Ridge
(7541, 0, 4, 0, 0, 2, 0, 0, 4, 0, 0, 5, 0, ''), -- Stormheim
(10714, 0, 4, 0, 0, 2, 0, 0, 4, 0, 0, 5, 0, ''), -- Stormheim
(13646, 0, 4, 0, 0, 2, 0, 0, 4, 0, 0, 5, 0, ''), -- The Azure Span
(4395, 0, 4, 0, 0, 2, 0, 0, 4, 0, 0, 5, 0, ''), -- Dalaran
(1519, 2, 0, 0, 2, 0, 0, 3, 0, 0, 2, 0, 0, ''), -- Stormwind City
(3430, 2, 0, 0, 2, 0, 0, 3, 0, 0, 2, 0, 0, ''), -- Eversong Woods
(3487, 2, 0, 0, 2, 0, 0, 3, 0, 0, 2, 0, 0, ''), -- Silvermoon City
(1638, 2, 0, 0, 2, 0, 0, 3, 0, 0, 2, 0, 0, ''), -- Thunder Bluff
(1657, 2, 0, 0, 2, 0, 0, 3, 0, 0, 2, 0, 0, ''), -- Darnassus
(3703, 2, 0, 0, 2, 0, 0, 3, 0, 0, 2, 0, 0, ''), -- Shattrath City
(7502, 2, 0, 0, 2, 0, 0, 3, 0, 0, 2, 0, 0, ''), -- Dalaran
(40, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Westfall
(130, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Silverpine Forest
(3433, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Ghostlands
(5095, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Tol Barad
(5389, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Tol Barad Peninsula
(408, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Gillijim's Isle
(409, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Island of Doctor Lapidis
(16591, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Riverglades
(60002, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Amani Empire
(293, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Thoradin's Wall
(269, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Dun Algaz
(2037, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Quel'thalas
(16, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Azshara
(331, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Ashenvale
(361, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Felwood
(406, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Stonetalon Mountains
(493, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Moonglade
(3524, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Azuremyst Isle
(3525, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Bloodmyst Isle
(4720, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- The Lost Isles
(4737, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Kezan
(61033, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Blackstone Island
(61004, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Sunnyglade Valley
(268, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Azshara Crater
(3518, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Nagrand
(3519, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Terokkar Forest
(3711, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Sholazar Basin
(4298, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Plaguelands: The Scarlet Enclave
(5785, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- The Jade Forest
(5805, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Valley of the Four Winds
(5840, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Vale of Eternal Blossoms
(5842, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Townlong Steppes
(6134, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Krasarang Wilds
(6661, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Isle of Giants
(6757, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Timeless Isle
(10920, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- The Veiled Stair
(11024, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- The Jade Forest
(11025, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Valley of the Four Winds
(11027, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Townlong Steppes
(11054, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- The Veiled Stair
(62004, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- The Veiled Stair
(6662, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Talador
(6719, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Shadowmoon Valley
(6721, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Gorgrond
(6722, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Spires of Arak
(6723, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Tanaan Jungle
(6755, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Nagrand
(6941, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Ashran
(7334, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Azsuna
(7558, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Val'sharah
(10430, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Val'sharah
(7637, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Suramar
(10727, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Suramar
(8499, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Zuldazar
(9570, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Zuldazar
(8567, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Tiragarde Sound
(10290, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Mechagon
(10413, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Revendreth
(11510, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Ardenweald
(13644, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- The Waking Shores
(13645, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Ohn'ahran Plains
(13647, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Thaldraszus
(14433, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- The Forbidden Reach
(15105, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Amirdrassil
(14717, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''), -- Isle of Dorn
(16593, 4, 0, 0, 3, 0, 0, 5, 0, 0, 4, 0, 0, ''); -- Zephras Isle
