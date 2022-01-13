# g1constants.py

if "xrange" in globals(): range = xrange # py2 compat

class _range_0_:
	def __init__(self, start, end, zero=0):
		self._ids  = range(start, end)
		self._zero = zero
	def __iter__(self):
		yield self._zero
		for id in self._ids: yield id


_mon_dex_nums = (
	112, 115, 32,  35,  21,  100, 34,  80,  2,   103,
	108, 102, 88,  94,  29,  31,  104, 111, 131, 59,
	151, 130, 90,  72,  92,  123, 120, 9,   127, 114,
	0,   0,   58,  95,  22,  16,  79,  64,  75,  113,
	67,  122, 106, 107, 24,  47,  54,  96,  76,  0,
	126, 0,   125, 82,  109, 0,   56,  86,  50,  128,
	0,   0,   0,   83,  48,  149, 0,   0,   0,   84,
	60,  124, 146, 144, 145, 132, 52,  98,  0,   0,
	0,   37,  38,  25,  26,  0,   0,   147, 148, 140,
	141, 116, 117, 0,   0,   27,  28,  138, 139, 39,
	40,  133, 136, 135, 134, 66,  41,  23,  46,  61,
	62,  13,  14,  15,  0,   85,  57,  51,  49,  87,
	0,   0,   10,  11,  12,  68,  0,   55,  97,  42,
	150, 143, 129, 0,   0,   89,  0,   99,  91,  0,
	101, 36,  110, 53,  105, 0,   93,  63,  65,  17,
	18,  121, 1,   3,   73,  0,   118, 119, 0,   0,
	0,   0,   77,  78,  19,  20,  33,  30,  74,  137,
	142, 0,   81,  0,   0,   4,   7,   5,   8,   6,
	0,   0,   0,   0,   43,  44,  45,  69,  70,  71
)
_dex_mon_names = (
	"missingno",
	"bulbasaur",
	"ivysaur",
	"venusaur",
	"charmander",
	"charmeleon",
	"charizard",
	"squirtle",
	"wartortle",
	"blastoise",
	"caterpie",
	"metapod",
	"butterfree",
	"weedle",
	"kakuna",
	"beedrill",
	"pidgey",
	"pidgeotto",
	"pidgeot",
	"rattata",
	"raticate",
	"spearow",
	"fearow",
	"ekans",
	"arbok",
	"pikachu",
	"raichu",
	"sandshrew",
	"sandslash",
	"nidoran_f",
	"nidorina",
	"nidoqueen",
	"nidoran_m",
	"nidorino",
	"nidoking",
	"clefairy",
	"clefable",
	"vulpix",
	"ninetales",
	"jigglypuff",
	"wigglytuff",
	"zubat",
	"golbat",
	"oddish",
	"gloom",
	"vileplume",
	"paras",
	"parasect",
	"venonat",
	"venomoth",
	"diglett",
	"dugtrio",
	"meowth",
	"persian",
	"psyduck",
	"golduck",
	"mankey",
	"primeape",
	"growlithe",
	"arcanine",
	"poliwag",
	"poliwhirl",
	"poliwrath",
	"abra",
	"kadabra",
	"alakazam",
	"machop",
	"machoke",
	"machamp",
	"bellsprout",
	"weepinbell",
	"victreebel",
	"tentacool",
	"tentacruel",
	"geodude",
	"graveler",
	"golem",
	"ponyta",
	"rapidash",
	"slowpoke",
	"slowbro",
	"magnemite",
	"magneton",
	"farfetchd",
	"doduo",
	"dodrio",
	"seel",
	"dewgong",
	"grimer",
	"muk",
	"shellder",
	"cloyster",
	"gastly",
	"haunter",
	"gengar",
	"onix",
	"drowzee",
	"hypno",
	"krabby",
	"kingler",
	"voltorb",
	"electrode",
	"exeggcute",
	"exeggutor",
	"cubone",
	"marowak",
	"hitmonlee",
	"hitmonchan",
	"lickitung",
	"koffing",
	"weezing",
	"rhyhorn",
	"rhydon",
	"chansey",
	"tangela",
	"kangaskhan",
	"horsea",
	"seadra",
	"goldeen",
	"seaking",
	"staryu",
	"starmie",
	"mr_mime",
	"scyther",
	"jynx",
	"electabuzz",
	"magmar",
	"pinsir",
	"tauros",
	"magikarp",
	"gyarados",
	"lapras",
	"ditto",
	"eevee",
	"vaporeon",
	"jolteon",
	"flareon",
	"porygon",
	"omanyte",
	"omastar",
	"kabuto",
	"kabutops",
	"aerodactyl",
	"snorlax",
	"articuno",
	"zapdos",
	"moltres",
	"dratini",
	"dragonair",
	"dragonite",
	"mewtwo",
	"mew"
)
def get_mon_dex_num(n):
	i = (n - 1) & 0xFF
	if i < 190: return _mon_dex_nums[i]
def get_dex_mon_name(n):
	if n <= 151: return _dex_mon_names[n]
def get_mon_name(n):
	i = (n - 1) & 0xFF
	if i < 190: return _dex_mon_names[_mon_dex_nums[i]]

missingno_ids = (
	31,  32,  50,  52,  56,  61,
	62,  63,  67,  68,  69,  79,
	80,  81,  86,  87,  94,  95,
	115, 121, 122, 127, 134, 135,
	137, 140, 146, 156, 159, 160,
	161, 162, 172, 174, 175, 181,
	182, 183, 184
)
glitchmon_ids      = _range_0_(191, 256)
glitchmon_dex_nums = _range_0_(152, 256)


_machine_moves = (
	5,   13,  14,  18,  25,  92,  32,  34,  36,  38,
	61,  55,  58,  59,  63,  6,   66,  68,  69,  99,
	72,  76,  82,  85,  87,  89,  90,  91,  94,  100,
	102, 104, 115, 117, 118, 120, 121, 126, 129, 130,
	135, 138, 143, 156, 86,  149, 153, 157, 161, 164,
	15,  19,  57,  70,  148
)
_move_names = (
	"none",
	"pound",
	"karate_chop",
	"double_slap",
	"comet_punch",
	"mega_punch",
	"pay_day",
	"fire_punch",
	"ice_punch",
	"thunder_punch",
	"scratch",
	"vise_grip",
	"guillotine",
	"razor_wind",
	"swords_dance",
	"cut",
	"gust",
	"wing_attack",
	"whirlwind",
	"fly",
	"bind",
	"slam",
	"vine_whip",
	"stomp",
	"double_kick",
	"mega_kick",
	"jump_kick",
	"rolling_kick",
	"sand_attack",
	"headbutt",
	"horn_attack",
	"fury_attack",
	"horn_drill",
	"tackle",
	"body_slam",
	"wrap",
	"take_down",
	"thrash",
	"double_edge",
	"tail_whip",
	"poison_sting",
	"twineedle",
	"pin_missile",
	"leer",
	"bite",
	"growl",
	"roar",
	"sing",
	"supersonic",
	"sonic_boom",
	"disable",
	"acid",
	"ember",
	"flamethrower",
	"mist",
	"water_gun",
	"hydro_pump",
	"surf",
	"ice_beam",
	"blizzard",
	"psybeam",
	"bubble_beam",
	"aurora_beam",
	"hyper_beam",
	"peck",
	"drill_peck",
	"submission",
	"low_kick",
	"counter",
	"seismic_toss",
	"strength",
	"absorb",
	"mega_drain",
	"leech_seed",
	"growth",
	"razor_leaf",
	"solar_beam",
	"poison_powder",
	"stun_spore",
	"sleep_powder",
	"petal_dance",
	"string_shot",
	"dragon_rage",
	"fire_spin",
	"thunder_shock",
	"thunderbolt",
	"thunder_wave",
	"thunder",
	"rock_throw",
	"earthquake",
	"fissure",
	"dig",
	"toxic",
	"confusion",
	"psychic",
	"hypnosis",
	"meditate",
	"agility",
	"quick_attack",
	"rage",
	"teleport",
	"night_shade",
	"mimic",
	"screech",
	"double_team",
	"recover",
	"harden",
	"minimize",
	"smokescreen",
	"confuse_ray",
	"withdraw",
	"defense_curl",
	"barrier",
	"light_screen",
	"haze",
	"reflect",
	"focus_energy",
	"bide",
	"metronome",
	"mirror_move",
	"self_destruct",
	"egg_bomb",
	"lick",
	"smog",
	"sludge",
	"bone_club",
	"fire_blast",
	"waterfall",
	"clamp",
	"swift",
	"skull_bash",
	"spike_cannon",
	"constrict",
	"amnesia",
	"kinesis",
	"soft_boiled",
	"high_jump_kick",
	"glare",
	"dream_eater",
	"poison_gas",
	"barrage",
	"leech_life",
	"lovely_kiss",
	"sky_attack",
	"transform",
	"bubble",
	"dizzy_punch",
	"spore",
	"flash",
	"psywave",
	"splash",
	"acid_armor",
	"crabhammer",
	"explosion",
	"fury_swipes",
	"bonemerang",
	"rest",
	"rock_slide",
	"hyper_fang",
	"sharpen",
	"conversion",
	"tri_attack",
	"super_fang",
	"slash",
	"substitute",
	"struggle"
)
def get_move_name(n):
	if n <= 165: return _move_names[n]
	else:        return get_machine_item_name(n)
def get_machine_move(n):
	if n <= 55: return _machine_moves[n]
def get_machine_move_name(n):
	if n <= 55: return _move_names[_machine_moves[n]]
def get_machine_name(n):
	if   n < 50: return ("TM%.2d" % (n + 1))
	elif n < 55: return ("HM%.2d" % (n - 49))

glitch_move_ids      = _range_0_(166, 256)
glitch_move_name_ids = _range_0_(166, 196)


_item_names = (
	"none",
	"master_ball",
	"ultra_ball",
	"great_ball",
	"poke_ball",
	"town_map",
	"bicycle",
	"unused_07", # ????? (surfboard)
	"safari_ball",
	"pokedex",
	"moon_stone",
	"antidote",
	"burn_heal",
	"ice_heal",
	"awakening",
	"parlyze_heal",
	"full_restore",
	"max_potion",
	"hyper_potion",
	"super_potion",
	"potion",
	"boulder_badge",
	"cascade_badge",
	"thunder_badge",
	"rainbow_badge",
	"soul_badge",
	"marsh_badge",
	"volcano_badge",
	"earth_badge",
	"escape_rope",
	"repel",
	"old_amber",
	"fire_stone",
	"thunder_stone",
	"water_stone",
	"hp_up",
	"protein",
	"iron",
	"carbos",
	"calcium",
	"rare_candy",
	"dome_fossil",
	"helix_fossil",
	"secret_key",
	"unused_2C", # ?????
	"bike_voucher",
	"x_accuracy",
	"leaf_stone",
	"card_key",
	"nugget",
	"pp_up",
	"poke_doll",
	"full_heal",
	"revive",
	"max_revive",
	"guard_spec",
	"super_repel",
	"max_repel",
	"dire_hit",
	"coin",
	"fresh_water",
	"soda_pop",
	"lemonade",
	"ss_ticket",
	"gold_teeth",
	"x_attack",
	"x_defend",
	"x_speed",
	"x_special",
	"coin_case",
	"oaks_parcel",
	"itemfinder",
	"silph_scope",
	"poke_flute",
	"lift_key",
	"exp_share",
	"old_rod",
	"good_rod",
	"super_rod",
	"pp_up",
	"ether",
	"max_ether",
	"elixir",
	"max_elixir",
	"B2F",
	"B1F",
	"1F",
	"2F",
	"3F",
	"4F",
	"5F",
	"6F",
	"7F",
	"8F",
	"9F",
	"10F",
	"11F",
	"B4F"
)
def get_item_name(n):
	if n <= 97: return _item_names[n]
	else:       return get_machine_item_name(n)
def get_machine_item_name(n):
	if   n > 200: return ("TM%02d" % (n - 200))
	elif n > 195: return ("HM%02d" % (n - 195))

glitch_item_ids      = _range_0_(84, 196)
glitch_item_name_ids = _range_0_(97, 196)


_trainer_names = (
	"none",
	"youngster",
	"bug_catcher",
	"lass",
	"sailor",
	"camper",    # jr_trainer_m
	"picnicker", # jr_trainer_f
	"pokemaniac",
	"super_nerd",
	"hiker",
	"biker",
	"burglar",
	"engineer",
	"juggler",
	"fisherman",
	"swimmer",
	"cue_ball",
	"gambler",
	"beauty",
	"psychic",
	"rocker",
	"juggler",
	"tamer",
	"bird_keeper",
	"black_belt",
	"rival1",
	"prof_oak",
	"chief",
	"scientist",
	"giovanni",
	"rocket_grunt",  # rocket
	"ace_trainer_m", # cooltrainer_m
	"ace_trainer_f", # cooltrainer_f
	"bruno",
	"brock",
	"misty",
	"lt_surge",
	"erika",
	"koga",
	"blaine",
	"sabrina",
	"gentleman",
	"rival2",
	"rival3",
	"lorelei",
	"channeler",
	"agatha",
	"lance"
)
def get_trainer_name(n):
	if n <= 47: return _trainer_names[n]
	else:       return get_machine_item_name(n)

glitch_trainer_ids           = _range_0_(48, 256)
glitch_trainer_name_ids      = _range_0_(48, 196)
glitch_trainer_encounter_ids = _range_0_(248, 256, zero=200)


_type_names = (
	"NORMAL",
	"FIGHTING",
	"FLYING",
	"POISON",
	"GROUND",
	"ROCK",
	"BIRD",
	"BUG",
	"GHOST",
	"NORMAL",
	"NORMAL",
	"NORMAL",
	"NORMAL",
	"NORMAL",
	"NORMAL",
	"NORMAL",
	"NORMAL",
	"NORMAL",
	"NORMAL",
	"NORMAL",
	"FIRE",
	"WATER",
	"GRASS",
	"ELECTRIC",
	"PSYCHIC",
	"ICE",
	"DRAGON"
)
def get_type_name(n):
	i = n & 0x7F
	if i < 27: return _type_names[i]

glitch_type_ids = range(27, 128)


_exp_group_names = (
	"MEDIUM_FAST",
	"UNUSED_01",
	"UNUSED_02",
	"MEDIUM_SLOW",
	"FAST",
	"SLOW"
)
def get_exp_group_name(n):
	n &= 0x3F
	if n <= 5: return _exp_group_names[n]

glitch_exp_group_ids = range(6, 64)


_move_effect_names = (
	"none",
	"unused_01",
	"poison_20pct",
	"drain",
	"burn_10pct",
	"freeze_10pct",
	"paralyze_10pct",
	"selfDestruct",
	"dreamEater",
	"mirrorMove",
	"boostAttack1",
	"boostDefense1",
	"boostSpeed1",    # unused
	"boostSpecial1",
	"boostAccuracy1", # unused
	"boostEvasion1",
	"payDay",
	"neverMiss",
	"lowerAttack1",
	"lowerDefense1",
	"lowerSpeed1",
	"lowerSpecial1",  # unused
	"lowerAccuracy1",
	"lowerEvasion1",  # unused
	"conversion",
	"haze",
	"bide",
	"thrash",
	"teleport",
	"multiHit",
	"unused_1E",
	"flinch_10pct",
	"sleep",
	"poison_40pct",
	"burn_30pct",
	"freeze_30pct",   # unused outside japanese ver
	"paralyze_30pct",
	"flinch_30pct",
	"ohko",
	"chargeTurn",
	"superFang",
	"fixedDamage",
	"damagingTrap",
	"fly",
	"twoHit",
	"jumpKick",
	"mist",
	"focusEnergy",
	"recoil4",
	"confuse",
	"boostAttack2",
	"boostDefense2",
	"boostSpeed2",
	"boostSpecial2",
	"boostAccuracy2", # unused
	"boostEvasion2",  # unused
	"healHalf",
	"transform",
	"lowerAttack2",   # unused
	"lowerDefense2",
	"lowerSpeed2",    # unused
	"lowerSpecial2",  # unused
	"lowerAccuracy2", # unused
	"lowerEvasion2",  # unused
	"lightScreen",
	"reflect",
	"poison",
	"paralyze",
	"lowerAttack_33pct",
	"lowerDefense_33pct",
	"lowerSpeed_33pct",
	"lowerSpecial_33pct",
	"unused_48",
	"unused_49",
	"unused_4A",
	"unused_4B",
	"confuse_10pct",
	"twineedle",
	"unused_4E",
	"substitute",
	"rechargeTurn",
	"rage",
	"mimic",
	"metronome",
	"leechSeed",
	"splash",
	"disable"
)
def get_move_effect_name(n):
	if n <= 86: return _move_effect_names[n]


_party_sprite_names = (
	"MONSTER",
	"BALL",
	"SHELL",
	"FAIRY",
	"BIRD",
	"AQUATIC",
	"BUG",
	"PLANT",
	"SNAKE",
	"QUADRUPED",
				  
	# Yellow only:
	"PIKACHU"
)
def get_party_sprite_name(n, yellow=False):
	if n < (0xA if yellow else 0x9):
		return _party_sprite_names[n]


_sprite_names = (
	"none",
	"red",
	"blue",
	"oak",
	"youngster",
	"monster",
	"ace_trainer_m", # cooltrainer_m
	"ace_trainer_f", # cooltrainer_f
	"little_girl",
	"bird",
	"middle_aged_man",
	"old_man",
	"super_nerd",
	"girl",
	"hiker",
	"beauty",
	"gentleman",
	"daisy",
	"biker",
	"sailor",
	"cook",
	"bike_shop_cashier",
	"mr_fuji",
	"giovanni",
	"rocket_grunt",
	"channeler",
	"waiter",
	"erika",
	"middle_aged_woman",
	"ponytail_girl",
	"lance",
	"unused_1F",
	"scientist",
	"rocker",
	"swimmer",
	"safari_zone_employee",
	"gym_guide",
	"gramps",
	"clerk",
	"fishing_guru",
	"granny",
	"nurse",
	"link_receptionist",
	"silph_president",
	"silph_employee",
	"warden",
	"captain",
	"fisher",
	"koga",
	"guard",
	"unused_32",
	"mom",
	"balding_man",
	"little_boy",
	"unused_36",
	"gameboy_kid",
	"clefairy",
	"agatha",
	"bruno",
	"lorelei",
	"seel",
	
	# Yellow only
	"pikachu",
	"officer_jenny",
	"sandshrew",
	"oddish",
	"bulbasaur",
	"jigglypuff",
	"clefairy_2",
	"chansey",
	"jessie",
	"james"
)
_still_sprite_names = (
	"poke_ball",
	"fossil",
	"boulder",
	"paper",
	"pokedex",
	"clipboard",
	"snorlax",
	 None,
	"old_amber",
	 None,
	 None,
	"old_man_asleep"
)
def get_sprite_name(n, yellow=False):
	sn = n - (0x47 if yellow else 0x3D)
	if   sn < 0:  return _sprite_names[n]
	elif sn < 12:
		s = _still_sprite_names[sn]
		return s if s else ("unused_%.2X" % n)


_palette_names = (
	"ROUTE",
	"PALLET",
	"VIRIDIAN",
	"PEWTER",
	"CERULEAN",
	"LAVENDER",
	"VERMILION",
	"CELADON",
	"FUCHSIA",
	"CINNABAR",
	"INDIGO",
	"SAFFRON",
	"TOWN_MAP",
	"LOGO1",
	"LOGO2",
	"UNUSED_0F", # unused?
	"MEW",
	"BLUE",
	"RED",
	"CYAN",
	"PURPLE",
	"BROWN",
	"GREEN",
	"PINK",
	"YELLOW",
	"GRAY",
	"SLOTS1",
	"SLOTS2",
	"SLOTS3",
	"SLOTS4",
	"BLACK",
	"HPBAR_GREEN",
	"HPBAR_YELLOW",
	"HPBAR_RED",
	"BADGE_BLUE",
	"CAVE",
	"GAMEFREAK",
				  
	# Yellow only:
	"UNUSED_25",
	"UNUSED_26",
	"UNUSED_27"
)
def get_palette_name(n, yellow=False):
	if n <= (0x27 if yellow else 0x23):
		return _palette_names[n]

def glitch_palette_ids(yellow=False):
	return range(0x28 if yellow else 0x24, 0x100)


_base_cry_mon_names = (
	"nidoran_m",  # 00
	"nidoran_f",  # 01
	"slowpoke",   # 02
	"kangaskhan", # 03
	"rhyhorn",    # 04
	"grimer",     # 05
	"voltorb",    # 06 *
	"gengar",     # 07 *
	"marowak",    # 08 *
	"nidoking",   # 09
	"nidoqueen",  # 0A
	"exeggcute",  # 0B
	"lickitung",  # 0C
	"exeggutor",  # 0D
	"poliwrath",  # 0E *
	"venusaur",   # 0F *
	"spearow",    # 10
	"rhydon",     # 11
	"tangela",    # 12
	"blastoise",  # 13
	"pinsir",     # 14
	"arcanine",   # 15
	"scyther",    # 16
	"gyarados",   # 17
	"shellder",   # 18
	"cubone",     # 19
	"tentacool",  # 1A
	"lapras",     # 1B
	"gastly",     # 1C
	"tauros",     # 1D **
	"starmie",    # 1E
	"slowbro",    # 1F
	"mr_mime",    # 20 *
	"psyduck",    # 21 *
	"rattata",    # 22
	"aerodactyl", # 23 *
	"graveler",   # 24
	"ponyta"      # 25
)
def get_base_cry_mon_name(n):
	if n <= 0x25: return _base_cry_mon_names[n]

_static_sound_names = (
	"mon_evolved",                          # 89
	"mon_evolved_ch2",                      # 8A
	"mon_evolved_ch3",                      # 8B
	"ball_shake",                           # 8C
	"hp_restore_item",                      # 8D
	"use_item",                             # 8E
	"start_menu",                           # 8F
	"ab_press",                             # 90
)
def get_static_sound_name(n):
	if n >= 0x86:
		if 0x89 <= n <= 0x90:
			return _static_sound_names[n - 0x89]
		elif n == 0xFF:
			return "STOP_MUSIC"
	elif n > 0x13:
		n -= 0x14; c = n % 3
		s = "cry_"+_base_cry_mon_names[n // 3]
		if c != 0: s += "_ch"+str(c + 1)
		return s
	elif n != 0:
		return "noise%.2X" % (n - 1)

_overworld_sound_names = (
#   "item_get",                     1,2,    # 86   87 88
#    ...                                      ...
	"dex_rating",                   1,2,    # 91   92 93
	"key_item_get",                 1,2,    # 94   95 96
	"poison",                               # 97
	"trade_machine",                        # 98         [!]
	"pc_turn_on",                           # 99
	"pc_turn_off",                          # 9A
	"pc_log_in",                            # 9B
	"shrink",                               # 9C
	"switch",                               # 9D
	"healing_machine_ball",                 # 9E
	"teleport_exit",                        # 9F
	"teleport_enter",                       # A0
	"teleport_spin",                        # A1
	"ledge_jump",                           # A2
	"teleport_land",                        # A3         [!]
	"fly",                                  # A4
	"wrong",                        1,      # A5   A6
	"arrow_tile",                           # A7
	"push_boulder",                         # A8
	"ss_anne_horn",                 1,      # A9   AA
	"pc_move_item",                         # AB
	"cut",                                  # AC
	"open_door",                            # AD
	"ball_land",                    1,      # AE   AF
	"unused_B0",                    1,      # B0   B1    [!]
	"purchase",                     1,      # B2   B3
	"bump",                                 # B4
	"enter_exit",                           # B5
	"save",                         1       # B6   B7
)
_bank02_sound_names = (
	"MUS_poke_flute",                       # B8
	"safari_zone_pa",                       # B9
	"MUS_pallet_town",              1,2,    # BA   BB BC
	"MUS_pokemon_center",           1,2,    # BD   BE BF
	"MUS_gym",                      1,2,    # C0   C1 C2
	"MUS_pewter_city",              1,2,3,  # C3   C4 C5 C6
	"MUS_cerulean_city",            1,2,    # C7   C8 C9
	"MUS_celadon_city",             1,2,    # CA   CB CC
	"MUS_cinnabar_island",          1,2,    # CD   CE CF
	"MUS_vermilion_city",           1,2,3,  # D0   D1 D2 D3
	"MUS_lavender_town",            1,2,3,  # D4   D5 D6 D7
	"MUS_ss_anne",                  1,2,    # D8   D9 DA
	"MUS_professor_oak",            1,2,    # DB   DC DD
	"MUS_rival",                    1,2,    # DE   DF E0
	"MUS_guide",                    1,2,3,  # E1   E2 E3 E4
	"MUS_evolution",                1,2,    # E5   E6 E7
	"MUS_pokemon_healed",           1,2,    # E8   E9 EA
	"MUS_road_to_viridian_city",    1,2,3,  # EB   EC ED EE
	"MUS_road_to_bill",             1,2,3,  # EF   F0 F1 F2
	"MUS_road_to_cerulean_city",    1,2,3,  # F3   F4 F5 F6
	"MUS_road_to_lavender_town",    1,2,3,  # F7   F8 F9 FA
	"MUS_victory_road",             1,2,3   # FB   FC FD FE
)
_bank1F_sound_names = (
	"intro_lunge",                          # B8
	"intro_hip",                            # B9
	"intro_hop",                            # BA
	"intro_wind_up",                        # BB
	"intro_impact",                         # BC
	"intro_whoosh",                         # BD
	"slots_stop_wheel",                     # BE
	"slots_reward",                         # BF
	"slots_spin",                   1,      # C0   C1
	"shooting_star",                        # C2
	"MUS_title_screen",             1,2,3,  # C3   C4 C5 C6
	"MUS_credits",                  1,2,    # C7   C8 C9
	"MUS_hall_of_fame",             1,2,    # CA   CB CC
	"MUS_prof_oaks_lab",            1,2,    # CD   CE CF
	"MUS_jigglypuffs_song",         1,      # D0   D1
	"MUS_bicycle",                  1,2,3,  # D2   D3 D4 D5
	"MUS_surf",                     1,2,    # D6   D7 D8
	"MUS_game_corner",              1,2,    # D9   DA DB
	"MUS_intro",                    1,2,3,  # DC   DD DE DF
	"MUS_rocket_hideout",           1,2,3,  # E0   E1 E2 E3
	"MUS_viridian_forest",          1,2,3,  # E4   E5 E6 E7
	"MUS_mt_moon",                  1,2,3,  # E8   E9 EA EB
	"MUS_pokemon_mansion",          1,2,3,  # EC   ED EE EF
	"MUS_pokemon_tower",            1,2,    # F0   F1 F2
	"MUS_silph_co",                 1,2,    # F3   F4 F5
	"MUS_encounter_evil_trainer",   1,2,    # F6   F7 F8
	"MUS_encounter_cute_trainer",   1,2,    # F9   FA FB
	"MUS_encounter_trainer",        1,2     # FC   FD FE
)
_battle_sound_names = (
#   "level_up",                     1,2,    # 86   87 88
#    ...                                      ...
	"ball_throw",                   1,      # 91   92
	"ball_poof",                    1,      # 93   94
	"ball_deflect",                 1,      # 95   96
	"run_away",                             # 97
	"dex_registered",               1,      # 98   99
	"mon_caught",                   1,2,    # 9A   9B 9C
	"peck",                                 # 9D
	"faint_fall",                           # 9E
	"meditate",                             # 9F
	"pound",                                # A0
	"struggle",                             # A1
	"karate_chop",                          # A2
	"mega_punch",                           # A3
	"razor_wind",                           # A4
	"vise_grip",                            # A5
	"damage",                               # A6
	"not_very_effective",                   # A7
	"gust",                                 # A8
	"whirlwind",                            # A9
	"residual_damage",                      # AA
	"vine_whip",                            # AB
	"unused_AC",                            # AC
	"jump_kick",                            # AD
	"headbutt",                             # AE
	"pin_missile",                          # AF
	"super_effective",                      # B0
	"sand_attack",                          # B1
	"powder",                               # B2
	"double_slap",                          # B3
	"horn_attack",                  1,      # B4   B5
	"horn_drill",                           # B6
	"stomp",                                # B7
	"tail_whip",                            # B8
	"slam",                                 # B9
	"low_kick",                             # BA
	"absorb",                       1,      # BB   BC
	"growth",                               # BD
	"thunder",                              # BE
	"supersonic",                   1,2,    # BF   C0 C1
	"aurora_beam",                  1,2,    # C2   C3 C4
	"mist",                         1,      # C5   C6
	"hydro_pump",                   1,2,    # C7   C8 C9
	"swift",                        1,      # CA   CB
	"surf",                         1,2,    # CC   CD CE
	"psybeam",                      1,2,    # CF   D0 D1
	"solar_beam",                   1,2,    # D2   D3 D4
	"thunderbolt",                  1,2,    # D5   D6 D7
	"psychic",                      1,2,    # D8   D9 DA
	"screech",                      1,      # DB   DC
	"throw_object",                 1,      # DD   DE
	"fly",                          1,      # DF   E0
	"explosion",                    1,2,    # E1   E2 E3
	"sing",                         1,      # E4   E5
	"hyper_beam",                   1,2,    # E6   E7 E8
	"trainer_ping",                         # E9
	"MUS_battle_gym_leader",        1,2,    # EA   EB EC
	"MUS_battle_trainer",           1,2,    # ED   EE EF
	"MUS_battle_wild_pokemon",      1,2,    # F0   F1 F2
	"MUS_battle_champion",          1,2,    # F3   F4 F5
	"MUS_victory_trainer",          1,2,    # F6   F7 F8
	"MUS_victory_wild_pokemon",     1,2,    # F9   FA FB
	"MUS_victory_gym_leader",       1,2     # FC   FD FE
)
_yellow_sound_names = (
	"surfing_jump",                         # 91
	"surfing_flip",                         # 92
	"surfing_crash",                        # 93
	"surfing_tally_score",                  # 94
	"surfing_land",                         # 95
	"surfing_hi_score",             1,2,    # 96   97 98
	"MUS_surfing_pikachu",          1,2,    # 99   9A 9B
	"MUS_team_rocket",              1,2,    # 9C   9D 9E
	"MUS_unused_giovanni",          1,2,3,  # 9F   A0 A1 A2     # unused
	"MUS_gb_printer",                       # A3
)
_sound_banks = {
	0x02: ( 1, _bank02_sound_names ),
	0x08: ( 0, _battle_sound_names ),
	0x1F: ( 1, _bank1F_sound_names ),
	0x20: ( 2, _yellow_sound_names )
}
def get_sound_name(bank, n, yellow=False):
	bank = _sound_banks.get(bank)
	if bank:
		if n >= 0x91:
			t, names = bank
			if   t == 1:
				if n <= 0xB7: names = _overworld_sound_names
				else:         n -= 0x27
			elif t == 2 and not yellow:
				return None
			n -= 0x91
			if n < len(names):
				s = names[n]
				if type(s) is int:
					return names[n - s] + "_ch" + str(s + 1)
				return s
		else:
			s = get_static_sound_name(n)
			if s: return s
			s = "item_get" if bank[0] == 1 else "level_up"
			if n != 0x86: s += "_ch"+str(n - 0x85)
			return s

def get_battle_sound_name(n):
	return get_sound_name(0x08, n, False)


_anim_names = (
	"show_sprite",
	"enemy_damaged",
	"player_damaged",
	"enemy_screen_shake",
	"trade_ball_drop",
	"trade_ball_appear1",
	"trade_ball_appear2",
	"trade_ball_poof",
	"player_spiral_light",
	"enemy_spiral_light",
	"player_square_light",
	"enemy_square_light",
	"player_spiral_dark",
	"enemy_spiral_dark",
	"player_square_dark",
	"enemy_square_dark",
	"player_unused",
	"enemy_unused",
	"player_paralyzed",
	"enemy_paralyzed",
	"player_poison_burn",
	"enemy_poison_burn",
	"player_asleep",
	"enemy_asleep",
	"player_confused",
	"enemy_confused",
	"faint",
	"ball_throw",
	"ball_shake",
	"ball_poof",
	"ball_block",
	"great_ball_throw",
	"ultra_ball_throw",
	"screen_shake",
	"hide_sprite",
	"throw_rock",
	"throw_bait",
	"screen_wave"
)
def get_animation_name(n):
	if   n <= 165: return _move_names[n]
	elif n <= 202: return _anim_names[n - 166]


_tileset_names = (
	"overworld",
	"players_house",
	"pokemart",
	"forest",
	"players_room",
	"gym2",
	"pokecenter",
	"gym",
	"house",
	"forest_gate",
	"museum",
	"underground",
	"gatehouse",
	"ship",
	"shipyard",
	"cemetery",
	"building",
	"cave",
	"lobby",
	"mansion",
	"lab",
	"club",
	"facility",
	"indigo_plateau",
	
	# Yellow only:
	"beach_house"
)
def get_tileset_name(n, yellow=False):
	if n < (24 if yellow else 23):
		return _tileset_names[n]


_map_names = (
	"pallet_town",
	"viridian_city",
	"pewter_city",
	"cerulean_city",
	"lavender_town",
	"vermilion_city",
	"celadon_city",
	"fuchsia_city",
	"cinnabar_island",
	"indigo_plateau",
	"saffron_city",
	"unused_0B",
	"route_1",
	"route_2",
	"route_3",
	"route_4",
	"route_5",
	"route_6",
	"route_7",
	"route_8",
	"route_9",
	"route_10",
	"route_11",
	"route_12",
	"route_13",
	"route_14",
	"route_15",
	"route_16",
	"route_17",
	"route_18",
	"route_19",
	"route_20",
	"route_21",
	"route_22",
	"route_23",
	"route_24",
	"route_25",
	"players_house",
	"players_room",
	"rivals_house",
	"oaks_lab",
	"viridian_pokecenter",
	"viridian_mart",
	"trainers_school",
	"viridian_house1",
	"viridian_gym",
	"digletts_cave_route_2",
	"viridian_forest_north_gate",
	"route_2_trade_house",
	"route_2_gate",
	"viridian_forest_south_gate",
	"viridian_forest",
	"museum_1F",
	"museum_2F",
	"pewter_gym",
	"pewter_nidoran_house",
	"pewter_mart",
	"pewter_house",
	"pewter_pokecenter",
	"mt_moon_1F",
	"mt_moon_B1F",
	"mt_moon_B2F",
	"cerulean_trashed_house",
	"cerulean_trade_house",
	"cerulean_pokecenter",
	"cerulean_gym",
	"bike_shop",
	"cerulean_mart",
	"mt_moon_pokecenter",
	"unused_celadon_trashed_house_copy",
	"route_5_gate",
	"underground_route_5",
	"daycare",
	"route_6_gate",
	"underground_route_6",
	"unused_underground_route_6_copy",
	"route_7_gate",
	"underground_route_7",
	"unused_underground_route_7_copy",
	"route_8_gate",
	"underground_route_8",
	"rock_tunnel_pokecenter",
	"rock_tunnel_1F",
	"power_plant",
	"route_11_gate_1F",
	"digletts_cave_route_11",
	"route_11_gate_2F",
	"route_12_gate_1F",
	"bills_house",
	"vermilion_pokecenter",
	"pokemon_fan_club",
	"vermilion_mart",
	"vermilion_gym",
	"vermilion_pidgey_house",
	"vermilion_dock",
	"ss_anne_1F",
	"ss_anne_2F",
	"ss_anne_3F",
	"ss_anne_B1F",
	"ss_anne_bow",
	"ss_anne_kitchen",
	"ss_anne_captains_room",
	"ss_anne_1F_cabins",
	"ss_anne_2F_cabins",
	"unused_69",
	"unused_6A",
	"unused_6B",
	"victory_road_1F",
	"unused_6C",
	"unused_6D",
	"unused_6E",
	"unused_6F",
	"unused_70",
	"lances_room",
	"unused_72",
	"unused_73",
	"unused_74",
	"unused_75",
	"hall_of_fame",
	"underground_north_south",
	"champions_room",
	"underground_east_west",
	"celadon_dept_store_1F",
	"celadon_dept_store_2F",
	"celadon_dept_store_3F",
	"celadon_dept_store_4F",
	"celadon_dept_store_roof",
	"celadon_dept_store_elevator",
	"celadon_mansion_1F",
	"celadon_mansion_2F",
	"celadon_mansion_3F",
	"celadon_mansion_roof",
	"celadon_mansion_roof_house",
	"celadon_pokecenter",
	"celadon_gym",
	"game_corner",
	"celadon_dept_store_5F",
	"game_corner_prize_exchange",
	"celadon_diner",
	"chiefs_house",
	"celadon_hotel",
	"lavender_pokecenter",
	"pokemon_tower_1F",
	"pokemon_tower_2F",
	"pokemon_tower_3F",
	"pokemon_tower_4F",
	"pokemon_tower_5F",
	"pokemon_tower_6F",
	"pokemon_tower_7F",
	"mr_fujis_house",
	"lavender_mart",
	"lavender_cubone_house",
	"fuchsia_mart",
	"bills_grandpas_house",
	"fuchsia_pokecenter",
	"wardens_house",
	"safari_zone_entrance",
	"fuchsia_gym",
	"fuchsia_meeting_room",
	"seafoam_islands_B1F",
	"seafoam_islands_B2F",
	"seafoam_islands_B3F",
	"seafoam_islands_B4F",
	"vermilion_fishing_gurus_house",
	"fuchsia_fishing_gurus_house",
	"pokemon_mansion_1F",
	"cinnabar_gym",
	"cinnabar_lab",
	"cinnabar_lab_trade_room",
	"cinnabar_lab_metronome_room",
	"cinnabar_lab_fossil_room",
	"cinnabar_pokecenter",
	"cinnabar_mart",
	"unused_cinnabar_mart_copy",
	"indigo_plateau_lobby",
	"copycats_house_1F",
	"copycats_house_2F",
	"fighting_dojo",
	"saffron_gym",
	"saffron_pidgey_house",
	"saffron_mart",
	"silph_co_1F",
	"saffron_pokecenter",
	"mr_psychics_house",
	"route_15_gate_1F",
	"route_15_gate_2F",
	"route_16_gate_1F",
	"route_16_gate_2F",
	"route_16_fly_house",
	"route_12_fishing_gurus_house",
	"route_18_gate_1F",
	"route_18_gate_2F",
	"seafoam_islands_1F",
	"route_22_gate",
	"victory_road_2F",
	"route_12_gate_2F",
	"vermilion_trade_house",
	"digletts_cave",
	"victory_road_3F",
	"rocket_hideout_B1F",
	"rocket_hideout_B2F",
	"rocket_hideout_B3F",
	"rocket_hideout_B4F",
	"rocket_hideout_elevator",
	"unused_CC",
	"unused_CD",
	"unused_CE",
	"silph_co_2F",
	"silph_co_3F",
	"silph_co_4F",
	"silph_co_5F",
	"silph_co_6F",
	"silph_co_7F",
	"silph_co_8F",
	"pokemon_mansion_2F",
	"pokemon_mansion_3F",
	"pokemon_mansion_B1F",
	"safari_zone_east",
	"safari_zone_north",
	"safari_zone_west",
	"safari_zone_center",
	"safari_zone_center_rest_house",
	"safari_zone_secret_house",
	"safari_zone_west_rest_house",
	"safari_zone_east_rest_house",
	"safari_zone_north_rest_house",
	"cerulean_cave_2F",
	"cerulean_cave_B1F",
	"cerulean_cave_1F",
	"name_raters_house",
	"cerulean_badge_house",
	"unused_E7",
	"rock_tunnel_B1F",
	"silph_co_9F",
	"silph_co_10F",
	"silph_co_11F",
	"silph_co_elevator",
	"unused_ED",
	"unused_EE",
	"trade_center",
	"colosseum",
	"unused_F1",
	"unused_F2",
	"unused_F3",
	"unused_F4",
	"loreleis_room",
	"brunos_room",
	"agathas_room",
	
	# Yellow only
	"beach_house"
)
def get_map_name(n, yellow=False):
	if n < (0xF8 if yellow else 0xF7):
		return _map_names[n]

def glitch_map_ids(yellow=False):
	return range(248 if yellow else 247, 256)
