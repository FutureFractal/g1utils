# g1const.py

class _range_0_:
	def __init__(self, start, end, zero=0):
		self._ids  = range(start, end)
		self._zero = zero
	def __iter__(self):
		yield self._zero
		for id in self._ids: yield id


_mon_dex_nums = bytes((
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
))
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
def mon_index_dex_num(n: int) -> int:
	i = (n - 1) & 0xFF
	if i < 190: return _mon_dex_nums[i]
def dex_mon_name(n: int) -> str:
	if n <= 151: return _dex_mon_names[n]
def mon_name(n: int) -> str:
	i = (n - 1) & 0xFF
	if i < 190:
		i = _mon_dex_nums[i]
		if i != 0: return _dex_mon_names[i]
		else:      return f"missingno_{n:2X}"

def mon_dex_num(name: str) -> int:
	n = _dex_mon_names.index(name)
	if n != -1: return n
def mon_index(name: str) -> int:
	n = mon_dex_num(name)
	if n: return _mon_dex_nums.index(n) + 1


missingno_ids = bytes((
	31,  32,  50,  52,  56,  61,
	62,  63,  67,  68,  69,  79,
	80,  81,  86,  87,  94,  95,
	115, 121, 122, 127, 134, 135,
	137, 140, 146, 156, 159, 160,
	161, 162, 172, 174, 175, 181,
	182, 183, 184
))
glitchmon_ids      = _range_0_(191, 256)
glitchmon_dex_nums = _range_0_(152, 256)


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
def move_name(n: int) -> str:
	if n <= 165: return _move_names[n]
	else:        return machine_item_name(n)
def move_index(name: str) -> int:
	n = _move_names.index(name)
	if n != -1: return n
	else:       return machine_item_index(name)

glitch_move_ids      = _range_0_(166, 256)
glitch_move_name_ids = _range_0_(166, 196)


_machine_moves = bytes((
	5,   13,  14,  18,  25,  92,  32,  34,  36,  38,
	61,  55,  58,  59,  63,  6,   66,  68,  69,  99,
	72,  76,  82,  85,  87,  89,  90,  91,  94,  100,
	102, 104, 115, 117, 118, 120, 121, 126, 129, 130,
	135, 138, 143, 156, 86,  149, 153, 157, 161, 164,
	15,  19,  57,  70,  148
))
def machine_move(n: int) -> int:
	if n <= 55: return _machine_moves[n]
def machine_move_name(n: int) -> str:
	if n <= 55: return _move_names[_machine_moves[n]]
def machine_name(n: int) -> str:
	return machine_item_name(n + 200)
def move_machine(n: int) -> int:
	n = _machine_moves.find(n)
	if n != -1: return n


_item_names = (
	"none",
	"master_ball",
	"ultra_ball",
	"great_ball",
	"poke_ball",
	"town_map",
	"bicycle",
	"unused_surfboard", # ?????
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
	"unused_pp_up",
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
	"exp_all",
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
def item_name(n: int) -> str:
	if n <= 97: return _item_names[n]
	else:       return machine_item_name(n)
def machine_item_name(n: int) -> str:
	if   n > 200: return f"TM{n - 200:02}"
	elif n > 195: return f"HM{n - 195:02}"

def item_index(name: str) -> int:
	n = _item_names.index(name)
	if n != -1: return n
	else:       return machine_item_index(name)
def machine_item_index(name: str) -> int:
	t, n = name[:2].upper(), name[2:]
	if n.isdigit():
		n = int(n)
		if   t == "TM" and 0 <= n <= 55: return n + 200
		elif t == "HM" and 0 <= n <= 5:  return n + 195

glitch_item_ids      = _range_0_(84, 196)
glitch_item_name_ids = _range_0_(97, 196)


_trainer_names = (
	"none",
	"youngster",
	"bug_catcher",
	"lass",
	"sailor",
	"jr_trainer_m",
	"jr_trainer_f",
	"pokemaniac",
	"super_nerd",
	"hiker",
	"biker",
	"burglar",
	"engineer",
	"unused_juggler",
	"fisher",
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
	"rival",
	"professor_oak", # unused
	"chief",         # unused
	"scientist",
	"giovanni",
	"rocket",
	"cool_trainer_m",
	"cool_trainer_f",
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
	"rival_champion",
	"lorelei",
	"channeler",
	"agatha",
	"lance"
)
_modern_trainer_names = {
	5:  "camper",
	6:  "picnicker",
	13: "juggler",
	15: "swimmer_m",
	19: "psychic_m",
	30: "rocket_grunt_m",
	31: "ace_trainer_m",
	32: "ace_trainer_f"
}
def trainer_name(n: int, modern:bool=False):
	if n <= 47:
		if modern:
			name = _modern_trainer_names.get(n)
			if name: return name
		return _trainer_names[n]
	else: 
		return machine_item_name(n)

def trainer_index(name: str) -> int:
	n = _trainer_names.index(name)
	if n != -1: return n
	else:       return machine_item_index(name)

glitch_trainer_ids           = _range_0_(48, 256)
glitch_trainer_name_ids      = _range_0_(48, 196)
glitch_trainer_encounter_ids = _range_0_(248, 256, zero=200)


def encounter_name(n: int, modern:bool=False) -> str:
	if n < 200: return mon_name(n)
	else:       return trainer_name((n - 200) & 0xFF, modern)
def encounter_index(name: str) -> int:
	n = mon_index(name)
	if n is not None: return n
	n = trainer_index(name)
	if n is not None and n < 200: return n + 200

def wild_encounter_name(n: int, modern:bool=False) -> str:
	if n < 200: 
		return mon_name(n)
	else:
		name = trainer_name((n - 200) & 0xFF, modern)
		if name: return "trainer_" + name
def trainer_encounter_name(n: int, modern:bool=False) -> str:
	if n >= 200: 
		return trainer_name((n - 200) & 0xFF, modern)
	else:
		name = mon_name(n)
		if name: return "mon_" + name


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
	 None,
	 None,
	 None,
	 None,
	 None,
	 None,
	 None,
	 None,
	 None,
	 None,
	 None,
	"FIRE",
	"WATER",
	"GRASS",
	"ELECTRIC",
	"PSYCHIC",
	"ICE",
	"DRAGON"
)
_glitch_type_trainer_names = bytes((
	1, 1, 1, 0, 1, 1, 1, 1, 
	0, 0, 1, 1, 1, 0, 1, 0, 
	0, 1, 0, 1, 1, 0, 0, 1, 
	0, 1, 1, 1, 0, 1, 1, 1
))
def type_name(n: int, glitch:bool=False) -> str:
	if n < 27: return _type_names[n]
	elif glitch:
		n &= 0x7F
		if   n < 27:
			return _type_names[n] or "NORMAL"
		elif n >= 91:
			n -= 91
			if n < 32 and _glitch_type_trainer_names[n]:
				return _trainer_names[n+1].upper()
			else:
				return "LAST_TRAINER"	

def type_index(name: str) -> int:
	n = _type_names.index(name)
	if n != -1: return n

glitch_type_ids = range(27, 128)


_exp_group_names = (
	"MEDIUM_FAST",
	"UNUSED_01",
	"UNUSED_02",
	"MEDIUM_SLOW",
	"FAST",
	"SLOW"
)
def exp_group_name(n: int) -> str:
	n &= 0x3F
	if n <= 5: return _exp_group_names[n]

glitch_exp_group_ids = range(6, 64)


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
def animation_name(n: int) -> str:
	if   n <= 165: return _move_names[n]
	elif n <= 202: return _anim_names[n - 166]


_move_effect_info = (
	"none",                0b11,
	"sleep",               0b01, # unused
	"poison_20pct",        0b11,
	"drain",               0b11,
	"burn_10pct",          0b11,
	"freeze_10pct",        0b11,
	"paralyze_10pct",      0b11,
	"self_destruct",       0b11,
	"dream_eater",         0b11,
	"mirror_move",         0b00,
	"boostAttack",         0b00,
	"boostDefense",        0b00,
	"boostSpeed",          0b00, # unused
	"boostSpecial",        0b00,
	"boostAccuracy",       0b00, # unused
	"boostEvasion",        0b00,
	"pay_day",             0b11,
	"neverMiss",           0b10,
	"lowerAttack",         0b01,
	"lowerDefense",        0b01,
	"lowerSpeed",          0b01,
	"lowerSpecial",        0b01, # unused
	"lowerAccuracy",       0b01,
	"lowerEvasion",        0b01, # unused
	"conversion",          0b00,
	"haze",                0b00,
	"bide",                0b01,
	"thrash",              0b11,
	"endWildBattle",       0b00,
	"multiHit",            0b11,
	"multiHit",            0b11, # unused
	"flinch_10pct",        0b11,
	"sleep",               0b01,
	"poison_40pct",        0b11,
	"burn_30pct",          0b11,
	"freeze_30pct",        0b11, # unused outside japanese ver
	"paralyze_30pct",      0b11,
	"flinch_30pct",        0b11,
	"ohko",                0b01,
	"chargeTurn",          0b11,
	"super_fang",          0b01,
	"fixedDamage",         0b01,
	"trapAttack",          0b11,
	"fly",                 0b11,
	"twoHit",              0b11,
	"jump_kick",           0b11,
	"mist",                0b00,
	"focus_energy",        0b00,
	"recoil4",             0b11,
	"confuse",             0b01,
	"boostAttack2",        0b00,
	"boostDefense2",       0b00,
	"boostSpeed2",         0b00,
	"boostSpecial2",       0b00,
	"boostAccuracy2",      0b00, # unused
	"boostEvasion2",       0b00, # unused
	"healHalf",            0b00,
	"transform",           0b00,
	"lowerAttack2",        0b01, # unused
	"lowerDefense2",       0b01,
	"lowerSpeed2",         0b01, # unused
	"lowerSpecial2",       0b01, # unused
	"lowerAccuracy2",      0b01, # unused
	"lowerEvasion2",       0b01, # unused
	"light_screen",        0b00,
	"reflect",             0b00,
	"poison",              0b01,
	"paralyze",            0b01,
	"lowerAttack_33pct",   0b11,
	"lowerDefense_33pct",  0b11,
	"lowerSpeed_33pct",    0b11,
	"lowerSpecial_33pct",  0b11,
	"lowerAccuracy_33pct", 0b11, # unused
	"lowerEvasion_33pct",  0b11, # unused
	"lowerStat6_33pct",    0b11, # unused
	"lowerStat7_33pct",    0b11, # unused
	"confuse_10pct",       0b11,
	"twineedle",           0b11,
	"unused_4E",           0b11, # unused, crashes
	"substitute",          0b00,
	"rechargeTurn",        0b11,
	"rage",                0b11,
	"mimic",               0b00,
	"metronome",           0b00,
	"leech_seed",          0b01,
	"splash",              0b00,
	"disable",             0b01
)
_glitch_move_effect_names = {
	0x1C: "whirlwind",
	0x27: "glitchy_dig",
	0x29: "psywave"
}
def move_effect_name(n: int, move:int=None) -> str:
	if n < 87:
		if move is not None and (move - 1) & 0xFF >= 165:
			name = _glitch_move_effect_names.get(n)
			if name: return name
		return _move_effect_info[n*2]
def move_effect_uses_power_accuracy(n: int) -> tuple[bool,bool]:
	if n < 87: pa = _move_effect_info[n*2 + 1]
	else:      pa = 0b11
	return bool(pa & 0b10), bool(pa & 0b01)


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
def party_sprite_name(n: int, yellow:bool=False) -> str:
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
def sprite_name(n: int, yellow:bool=False) -> str:
	sn = n - (0x47 if yellow else 0x3D)
	if   sn < 0:  return _sprite_names[n]
	elif sn < 12:
		s = _still_sprite_names[sn]
		return s if s else f"unused_{n:02X}"

def glitch_sprite_ids(yellow:bool=False) -> range:
	return range(0x53 if yellow else 0x49, 0x100)


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
	"TRAINER",
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
	"HP_BAR_GREEN",
	"HP_BAR_YELLOW",
	"HP_BAR_RED",
	"BADGE_BLUE",
	"CAVE",
	"GAMEFREAK",
				  
	# Yellow only:
	"UNUSED_25",
	"UNUSED_26",
	"UNUSED_27"
)
def palette_name(n: int, yellow:bool=False) -> str:
	if n <= (0x27 if yellow else 0x23):
		return _palette_names[n]

def glitch_palette_ids(yellow:bool=False) -> range:
	return range(0x28 if yellow else 0x24, 0x100)


# For most base cries there's a Pokémon with an unmodified version of it as its cry
# (its pitch and tempo modifiers are 0x00, 0x80 respectively.) These Pokémon are
# typically the first ones with that basecry in index order too, so they make the
# most sense to name the base cry after.
# For some base cries though, denoted by a * here, there are no Pokémon with an 
# unmodified version of it. For these I just chose the Pokémon whose cry is the 
# closest to unmodified, and/or is the first with that base cry in index order.
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
	"tauros",     # 1D *
	"starmie",    # 1E
	"slowbro",    # 1F
	"mr_mime",    # 20 *
	"psyduck",    # 21 *
	"rattata",    # 22
	"aerodactyl", # 23 *
	"graveler",   # 24
	"ponyta"      # 25
)
def base_cry_mon_name(n: int) -> str:
	if n <= 0x25: return _base_cry_mon_names[n]

_static_sound_names = (
	"mon_evolved",                          # 89
	"mon_evolved_ch2",                      # 8A
	"mon_evolved_ch3",                      # 8B
	"ball_shake",                           # 8C
	"hp_restore_item",                      # 8D
	"use_item",                             # 8E
	"start_menu",                           # 8F
	"ui_press",                             # 90
)
def static_sound_name(n: int) -> str:
	if n >= 0x86:
		if 0x89 <= n <= 0x90:
			return _static_sound_names[n - 0x89]
		elif n == 0xFF:
			return "STOP_MUSIC"
	elif n > 0x13:
		n -= 0x14; c = n % 3
		s = "basecry_"+_base_cry_mon_names[n // 3]
		if c != 0: s += f"_ch{c + 1}"
		return s
	elif n != 0:
		return f"noise{n}"

_overworld_sound_names = (
	"item_get",                     1,2,    # 86   87 88
	 None,None,None,                        # 89   8A 8B
	 None,                                  # 8C
	 None,                                  # 8D
	 None,                                  # 8E
	 None,                                  # 8F
	 None,                                  # 90
	"dex_rating",                   1,2,    # 91   92 93
	"key_item_get",                 1,2,    # 94   95 96
	"poison_damage",                        # 97
	"trade_machine",                        # 98
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
	"teleport_land",                        # A3
	"fly",                                  # A4
	"wrong",                        1,      # A5   A6
	"arrow_tile",                           # A7
	"push_boulder",                         # A8
	"ss_anne_horn",                 1,      # A9   AA
	"pc_move_item",                         # AB
	"cut",                                  # AC
	"open_door",                            # AD
	"ball_land",                    1,      # AE   AF
	"unused_B0",                    1,      # B0   B1
	"purchase",                     1,      # B2   B3
	"bump",                                 # B4
	"enter_exit",                           # B5
	"save",                         1       # B6   B7
)
_bank02_sound_names = (
	"mus_poke_flute",                       # B8
	"safari_zone_pa",                       # B9
	"mus_pallet_town",              1,2,    # BA   BB BC
	"mus_pokemon_center",           1,2,    # BD   BE BF
	"mus_gym",                      1,2,    # C0   C1 C2
	"mus_pewter_city",              1,2,3,  # C3   C4 C5 C6
	"mus_cerulean_city",            1,2,    # C7   C8 C9
	"mus_celadon_city",             1,2,    # CA   CB CC
	"mus_cinnabar_island",          1,2,    # CD   CE CF
	"mus_vermilion_city",           1,2,3,  # D0   D1 D2 D3
	"mus_lavender_town",            1,2,3,  # D4   D5 D6 D7
	"mus_ss_anne",                  1,2,    # D8   D9 DA
	"mus_professor_oak",            1,2,    # DB   DC DD
	"mus_rival",                    1,2,    # DE   DF E0
	"mus_guide",                    1,2,3,  # E1   E2 E3 E4
	"mus_evolution",                1,2,    # E5   E6 E7
	"mus_pokemon_healed",           1,2,    # E8   E9 EA
	"mus_road_to_viridian_city",    1,2,3,  # EB   EC ED EE
	"mus_road_to_bill",             1,2,3,  # EF   F0 F1 F2
	"mus_road_to_cerulean_city",    1,2,3,  # F3   F4 F5 F6
	"mus_road_to_lavender_town",    1,2,3,  # F7   F8 F9 FA
	"mus_victory_road",             1,2,3   # FB   FC FD FE
)
_bank1F_sound_names = (
	"intro_lunge",                          # B8
	"intro_hip",                            # B9
	"intro_hop",                            # BA
	"intro_wind_up",                        # BB
	"intro_impact",                         # BC
	"intro_whoosh",                         # BD
	"slots_stop_wheel",                     # BE
	"slots_payout",                         # BF
	"slots_spin",                   1,      # C0   C1
	"shooting_star",                        # C2
	"mus_title_screen",             1,2,3,  # C3   C4 C5 C6
	"mus_credits",                  1,2,    # C7   C8 C9
	"mus_hall_of_fame",             1,2,    # CA   CB CC
	"mus_prof_oaks_lab",            1,2,    # CD   CE CF
	"jigglypuffs_song",             1,      # D0   D1
	"mus_bicycle",                  1,2,3,  # D2   D3 D4 D5
	"mus_surf",                     1,2,    # D6   D7 D8
	"mus_game_corner",              1,2,    # D9   DA DB
	"mus_intro",                    1,2,3,  # DC   DD DE DF
	"mus_rocket_hideout",           1,2,3,  # E0   E1 E2 E3
	"mus_viridian_forest",          1,2,3,  # E4   E5 E6 E7
	"mus_mt_moon",                  1,2,3,  # E8   E9 EA EB
	"mus_pokemon_mansion",          1,2,3,  # EC   ED EE EF
	"mus_pokemon_tower",            1,2,    # F0   F1 F2
	"mus_silph_co",                 1,2,    # F3   F4 F5
	"mus_encounter_shady_trainer",  1,2,    # F6   F7 F8
	"mus_encounter_cute_trainer",   1,2,    # F9   FA FB
	"mus_encounter_trainer",        1,2     # FC   FD FE
)
_battle_sound_names = (
	"level_up",                     1,2,    # 86   87 88
	 None,None,None,                        # 89   8A 8B
	 None,                                  # 8C
	 None,                                  # 8D
	 None,                                  # 8E
	 None,                                  # 8F
	 None,                                  # 90
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
	"mus_battle_gym_leader",        1,2,    # EA   EB EC
	"mus_battle_trainer",           1,2,    # ED   EE EF
	"mus_battle_wild_pokemon",      1,2,    # F0   F1 F2
	"mus_battle_champion",          1,2,    # F3   F4 F5
	"mus_victory_trainer",          1,2,    # F6   F7 F8
	"mus_victory_wild_pokemon",     1,2,    # F9   FA FB
	"mus_victory_gym_leader",       1,2     # FC   FD FE
)
_yellow_sound_names = (
	"surfing_jump",                         # 91
	"surfing_flip",                         # 92
	"surfing_crash",                        # 93
	"surfing_tally_score",                  # 94
	"surfing_land",                         # 95
	"surfing_hi_score",             1,2,    # 96   97 98
	"mus_surfing_pikachu",          1,2,    # 99   9A 9B
	"mus_team_rocket",              1,2,    # 9C   9D 9E
	"mus_unused_giovanni",          1,2,3,  # 9F   A0 A1 A2
	"mus_gb_printer",                       # A3
)
_sound_banks = {
	0x02: _bank02_sound_names,
	0x08: _battle_sound_names,
	0x1F: _bank1F_sound_names,
}
def sound_name(bank: int, n: int, yellow:bool=False) -> str:
	names = _sound_banks.get(bank)
	if names is None:
		if yellow and bank == 0x20:
			names = _yellow_sound_names
		else:
			return None
	if n >= 0x86:
		i = n - 0x86
		if bank == 0x02 or bank == 0x1F:
			if n < 0xB8: names = _overworld_sound_names
			else:        i -= 0x32 # 0xB8 - 0x86
		if i < len(names):
			s = names[i]
			if type(s) is int: return f"{names[i - s]}_ch{s + 1}"
			elif s:            return s
	return static_sound_name(n)

def battle_sound_name(n: int) -> str:
	return sound_name(8, n)

def does_sound_loop(bank: int, n: int, yellow:bool=False) -> bool:
	if   bank == 0x02: return n >= 0xBA
	elif bank == 0x08: return n >= 0xEA
	elif bank == 0x1F: return n >= 0xC3 and n not in b"\xD1\xD2\xDC\xDD\xDE\xDF"
	elif yellow:
		if bank == 0x20: return 0x99 <= n <= 0xA3

def sound_bank_name(bank: int, yellow:bool=False) -> str:
	if   bank == 0x02: return "overworld"
	elif bank == 0x08: return "battle"
	elif bank == 0x1F: return "misc"
	elif yellow:
		if bank == 0x20: return "yellow"


_tileset_names = (
	"overworld",
	"players_house", # also Copycat's house
	"pokemart",
	"forest",
	"players_room",  # also Copycat's room
	"gym2",          # Oak's Lab, Fighting Dojo, Lance's room
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
	"building",      # Bill's house, Pokemon Fan Club, Silph Co. top floor
	"cave",
	"business",      # elevators, Game Corner, Celadon Department Store
	"celadon_mansion",
	"lab",           # Cinnabar Lab, Warden's house, Safari Zone buildings
	"cable_club",    # also Bike Shop
	"facility",      # Rocket Hideout, Power Plant, Silph Co., Cinnabar Mansion
	"indigo_plateau",
	
	# Yellow only:
	"beach_house"
)
def tileset_name(n: int, yellow:bool=False) -> str:
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
	 None,
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
	 None,
	"route_7_gate",
	"underground_route_7",
	 None,
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
	 None,
	 None,
	 None,
	"victory_road_1F",
	 None,
	 None,
	 None,
	 None,
	 None,
	"lances_room",
	 None,
	 None,
	 None,
	 None,
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
def map_name(n: int, yellow:bool=False) -> str:
	if n < (0xF8 if yellow else 0xF7):
		name = _map_names[n]
		if name is None: name = f"unused_{n:02X}"
		return name
def map_index(name: str, yellow:bool=False) -> int:
	n = _map_names.index(name)
	if n != -1 and (n < 0xF7 or yellow):
		return n

dummy_map_ids = bytes((
	0x0B, 0x69, 0x6A, 0x6B, 0x6D, 0x6E,
	0x6F, 0x70, 0x72, 0x73, 0x74, 0x75,
	0xCC, 0xCD, 0xCE, 0xE7, 0xED, 0xEE,
	0xF1, 0xF2, 0xF3, 0xF4
))
def glitch_map_ids(yellow:bool=False) -> range:
	return range(0xF8 if yellow else 0xF7, 0x100)


_map_palette_ids = bytes((
	1,   2,   3,   4,   5,   6,   7,   8,   9,   10,
	11,  0xFF,0,   0,   0,   0,   0,   0,   0,   0,
	0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
	0,   0,   0,   0,   0,   0,   0,   1,   1,   1,
	1,   2,   2,   2,   2,   2,   35,  0,   0,   0,
	0,   0,   3,   3,   3,   3,   3,   3,   3,   35,
	35,  35,  4,   4,   4,   4,   4,   4,   0,   0xFF,
	0,   0,   0,   0,   0,   0xFF,0,   0,   0xFF,0,
	0,   0,   35,  0,   0,   35,  0,   0,   0,   6,
	6,   6,   6,   6,   6,   6,   6,   6,   6,   6,
	6,   6,   6,   6,   6,   0xFF,0xFF,0xFF,35,  0xFF,
	0xFF,0xFF,0xFF,10,  0xFF,0xFF,0xFF,0xFF,10,  0,
	10,  0,   7,   7,   7,   7,   7,   7,   7,   7,
	7,   7,   7,   7,   7,   7,   7,   7,   7,   7,
	7,   5,   25,  25,  25,  25,  25,  25,  25,  5,
	5,   5,   8,   8,   8,   8,   8,   8,   8,   35,
	35,  35,  35,  6,   8,   9,   9,   9,   9,   9,
	9,   9,   9,   9,   10,  11,  11,  11,  11,  11,
	11,  11,  11,  11,  0,   0,   0,   0,   0,   0,
	0,   0,   35,  0,   35,  0,   6,   35,  35,  7,
	7,   7,   7,   7,   0xFF,0xFF,0xFF,11,  11,  11,
	11,  11,  11,  11,  9,   9,   9,   8,   8,   8,
	8,   8,   8,   8,   8,   8,   35,  35,  35,  5,
	4,   0xFF,35,  11,  11,  11,  11,  0xFF,0xFF,0xFF,
	0xFF,0xFF,0xFF,0xFF,0xFF,1,   35,  25,
					
	# Yellow only:
	0
))
def map_palette_id(n: int, yellow:bool=False) -> int:
	if n <= (0xF8 if yellow else 0xF7):
		n = _map_palette_ids[n]
		if n != 0xFF: return n
