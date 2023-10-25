#!/usr/bin/env python3
# g1dump.py
from typing import Sequence

import sys, os
import g1utils, g1const
from   g1utils import Memory, Info
from   datafmt import Writer

hex     = lambda x: f"0x{x:X}"
hexbyte = lambda x: f"0x{x:02X}"
hexaddr = lambda x: f"0x{x:04X}"
comaddr = lambda x: f"${x:04X}"

def percent(chance):
	chance *= 100
	if chance % 256 == 0:
		return f"{chance // 256}%"
	else:
		# % seems to round unnecessarily
		s = str(float(chance) / 256.0)
		return s[:(s.find(".")+2)] + "%"

DEFAULT_SYNTAX = "jx"


#== Mons ===================================================================================================

moveset_crepr = lambda _: "Super Glitch"

def dump_addr(writer, key, addr):
	if addr is not None:
		writer.prop(key, hexaddr(addr))

def dump_mon_species_info(writer: Writer, rom: Memory, n: int, combined:bool=False, expand:bool=True):
	info = rom.get_mon_info(n)

	dexno = info.dex_num
	if 0 < n <= 190: writer.prop("dexNo", str(dexno))
	else:            writer.enum_prop("family", dexno, g1const.dex_mon_name)
		
	writer.string_prop("name", rom.get_mon_name(n))

	if info.category is not None:
		writer.string_prop("category", info.category)

	if combined:
		dump_dex_mon_info(writer, rom, info, combined=True, expand=expand)
	else:
		dump_mon_dex_measurements(writer, info)

	dump_mon_cry(writer, info.cry)

	if combined:
		with writer.begin_list_prop("startMoves"):
			dump_mon_moves(writer, info.start_moves)

	dump_mon_level_moves(writer, info.level_moves)

	if combined:
		with writer.begin_set_prop("machineMoves"):
			dump_mon_moves(writer, info.machine_moves)

	dump_mon_evolutions(writer, rom, info)

	dump_mon_dex_description(writer, info)

	dump_addr(writer, "movesAddr", info.moves_addr)
	dump_addr(writer, "evosAddr",  info.evos_addr)
	dump_addr(writer, "dexAddr",   info.dex_addr)

def dump_mon_family_info(writer: Writer, rom: Memory, n: int):
	dump_dex_mon_info(writer, rom, rom.get_dex_mon_info(n))
def dump_dex_mon_info(writer: Writer, rom: Memory, info: Info, combined:bool=False, expand:bool=True):

	crepr = lambda t: "/".join(type_repr(rom, n) for n in t)
	writer.enum_tuple_prop("type", info.type, g1const.type_name, hexbyte, crepr=crepr, glitch=True)

	stats = info.stats
	writer.tuple_prop("stats", [str(stats[i]) for i in (0, 1, 2, 4, 3)]) # swap speed & special

	if combined:
		dump_mon_dex_measurements(writer, info)

	writer.prop("catchRate", str(info.catch_rate))
	writer.prop("expYield",  str(info.exp_yield))

	dump_mon_exp_group(writer, rom, info.exp_group, expand=expand)

	dump_dex_mon_palette(writer, rom, info.palette, expand=expand)
	dump_dex_mon_sprite_info(writer, rom, info, expand=expand)
						   
	writer.enum_prop("icon", info.party_sprite, g1const.party_sprite_name, hex, yellow=rom.is_yellow)

	if not combined:
		with writer.begin_list_prop("startMoves"):
			dump_mon_moves(writer, info.start_moves)
		with writer.begin_set_prop("machineMoves"):
			dump_mon_moves(writer, info.machine_moves)

def dump_mon_moves(writer: Writer, moves: Memory):
	for n in moves:
		writer.enum_item(n, g1const.move_name, hexbyte, crepr=moveset_crepr)

def dump_mon_level_moves(writer, moves):
	if moves:
		moves = sorted(moves.items())
		with writer.begin_dict_prop("levelMoves"):
			for level, move in moves:
				writer.enum_prop(str(level), move, g1const.move_name, hexbyte, crepr=moveset_crepr)

def dump_level_evos(writer, key, evos, crepr):
	if evos:
		evos = sorted(evos.items())
		with writer.begin_dict_prop(key):
			for level, mon in evos:
				writer.enum_prop(str(level), mon, g1const.mon_name, crepr=crepr)

def dump_item_evos(writer, evos, crepr):
	if evos:
		evos = sorted(evos.items())
		with writer.begin_dict_prop("itemEvos"):
			for item, mon in evos:
				key = g1const.item_name(item)
				if key is None: key = hexbyte(item)
				writer.enum_prop(key, mon, g1const.mon_name, crepr=crepr)

def dump_mon_evolutions(writer: Writer, rom: Memory, info: Info):
	crepr = lambda n: rom.get_mon_name(n, grepr="#").strip()
	dump_level_evos(writer, "levelEvos", info.level_evos, crepr)
	dump_item_evos(writer, info.item_evos, crepr)
	dump_level_evos(writer, "tradeEvos", info.trade_evos, crepr)

def dump_dex_mon_sprite_info(writer, rom, info, expand=True):
	return # TODO
	
	
	dump_dex_mon_palette(writer, rom, n, expand=expand)

def dex_decimal(x):
	x = f"{x:02}"
	return x[:-1]+"."+x[-1]
def dump_mon_dex_measurements(writer: Writer, info: Info):	
	height = info.height
	if height is not None:
		if info.is_metric:
			writer.prop("height", dex_decimal(height), comment="m")
		else:
			feet, inches = height
			comment = None
			if inches >= 12:
				feet  += inches // 12
				inches = inches %  12
				comment = f"{feet}' {inches}\""
			else:
				comment = "ft, in"
			writer.tuple_prop("height", [str(x) for x in height], comment=comment)

	if info.weight is not None:
		comment = "kg" if info.is_metric else "lbs"
		writer.prop("weight", dex_decimal(info.weight), comment=comment)

def dump_mon_dex_description(writer, info):
	if info.description:
		writer.multi_line_string_prop("description", info.description)


#== Moves ==================================================================================================

def accuracy_percent(accuracy: int) -> str:
	if accuracy != 0:
		return f"{(accuracy*100)/256.0:0.1f}%"

def dump_move_info(writer: Writer, rom: Memory, n: int):
	name = rom.get_move_name(n, default=None)
	if name: writer.string_prop("name", name)
	info = rom.get_move_info(n)
	writer.enum_prop("type", info.type, g1const.type_name, hexbyte, crepr=lambda n: type_repr(rom, n), glitch=True)
	effect = info.effect
	power, accuracy = g1const.move_effect_uses_power_accuracy(effect)
	if power:    writer.prop("power",    info.power)
	if accuracy: writer.prop("accuracy", info.accuracy, comment=accuracy_percent(info.accuracy))
	writer.prop("pp", info.pp)
	writer.enum_prop("animation", info.animation, g1const.animation_name, hexbyte)
	writer.enum_prop("effect", effect, g1const.move_effect_name, hexbyte, 
	                 crepr=lambda n: f"${rom.get_move_effect_ptr(n)[1]:04X}")

def dump_moves(writer: Writer, rom: Memory, ids: Sequence[int]):
	crepr = lambda n: "type: " + type_repr(rom, n)
	keys, rows, coms = [], [], []
	for n in ids:
		info = rom.get_move_info(n)
		effect = info.effect
		power, accuracy = g1const.move_effect_uses_power_accuracy(effect)
		type, comment   = writer.enum_repr(info.type, g1const.type_name, hexbyte, crepr)
		keys.append(hexbyte(n) if n <= 195 else g1const.machine_item_name(n))
		rows.append((
			type,
			str(info.power    if power    else 0),
			str(info.accuracy if accuracy else 0),
			str(info.pp),
			writer.enum_repr(info.animation, g1const.animation_name,   hexbyte)[0],
			writer.enum_repr(effect,         g1const.move_effect_name, hexbyte)[0]
		))
		coms.append(comment)
	writer.tuple_prop_rows(keys, rows, comments=coms)


#== Items ==================================================================================================

def dump_items(writer: Writer, rom: Memory, ids):
	keys = (hexbyte(n) for n in ids)
	rows = ((str(rom.get_item_price(n)), f'"{rom.get_item_name(n)}"') for n in ids)
	writer.tuple_prop_rows(keys, rows)


#== Types ==================================================================================================

def type_repr(rom: Memory, n: int) -> str:
 	return g1const.type_name(n) or rom.get_type_name(n, default=lambda a: f"<Glitch ${a:04X}>", grepr='#')

def dump_type_names(writer: Writer, rom: Memory, ids):
	for n in ids:
		name = rom.get_type_name(n, default=None)
		if name is not None:
			writer.string_prop(hexbyte(n), name)
		else:
			writer.prop(hexbyte(n), hexaddr(rom.get_type_name_ptr(n)[1]))


#== Palettes ===============================================================================================

def pal_repr(rom, n, type):
	return [f"0x{r:02X}{g:02X}{b:02X}" for r,g,b in rom.get_palette(type, n)]

def dump_dex_mon_palette(writer: Writer, rom: Memory, n: int, expand:bool=True):
	if not expand:
		writer.enum_prop("palette", n, g1const.palette_name, hexbyte)
	else:
		name = g1const.palette_name(n, yellow=rom.is_yellow)
		if name:
			writer.prop("palette", name)
		else:
			if rom.is_yellow and not rom.is_japan:
				with writer.begin_object_prop("palette"):
					writer.tuple_prop("sgb", pal_repr(rom, n, "sgb"))
					writer.tuple_prop("gbc", pal_repr(rom, n, "gbc"))
			else:
				writer.tuple_prop("palette", pal_repr(rom, n, "sgb"))

def dump_palettes(writer: Writer, rom: Memory, ids: Sequence[int]):
	with writer.begin_top_level_dict("palettes"):
		if rom.is_gbc:
			for n in ids:
				with writer.begin_object_prop(hexbyte(n)):
					writer.tuple_prop("sgb", pal_repr(rom, n, "sgb"))
					writer.tuple_prop("gbc", pal_repr(rom, n, "gbc"))
		else:
			for n in ids:
				writer.tuple_prop(hexbyte(n), pal_repr(rom, n, "sgb"))


#== Exp groups =============================================================================================

def dump_mon_exp_group(writer: Writer, rom: Memory, exp_group: int, expand:bool=True):
	if not expand:
		writer.enum_prop("expGroup", exp_group, g1const.exp_group_name, hexbyte, rom.get_exp_group_formula)
	else:
		name = g1const.exp_group_name(exp_group)
		if name:
			writer.prop("expGroup", name)
		else:
			nums = rom.get_exp_group_coefficients(exp_group)
			comment = g1utils.exp_group_formula_repr(nums)
			if nums[1] != 0:
				writer.tuple_prop("expGroup", [str(i) for i in nums], comment=comment)
			else:
				writer.prop("expGroup", "DIV_BY_ZERO")

def dump_exp_groups(writer: Writer, rom: Memory, ids):
	keys, rows, coms = [], [], []
	for n in ids:
		nums = rom.get_exp_group_coefficients(n)
		keys.append(hexbyte(n))
		rows.append([str(x) for x in nums])
		coms.append(g1utils.exp_group_formula_repr(nums))
	writer.tuple_prop_rows(keys, rows, coms)


#== Sounds =================================================================================================

def dump_mon_cry(writer: Writer, cry, key="cry"):
	n, pitch, tempo = cry
	s = g1const.static_sound_name(n)
	if s:
		if (0x86 > n > 0x13) and (n - 0x14) % 3 == 0:
			writer.tuple_prop(key, ( s, str(pitch), str(tempo) ))
		else:
			writer.prop(key, s)
	elif n != 0:
		battle = g1const.sound_name(0x08, n)
		bank02 = g1const.sound_name(0x02, n)
		if n <= 0xB7:
			overworld = "overworld:" + bank02
		else:
			bank1F = g1const.sound_name(0x1F, n)
			overworld = "overworld:( " + bank02 + ", " + bank1F + " )"
		if 0x9D <= n < 0xEA and battle[-4:-1] != "_ch":
			writer.tuple_prop(key, ( battle, str(pitch), str(tempo), overworld ))
		else:
			writer.tuple_prop(key, ( battle, overworld ))
	else:
		writer.prop(key, "0")

def dump_mon_cries(writer: Writer, rom: Memory, ids):
	for n in ids:
		dump_mon_cry(writer, rom, n, str(n))


#== Trainers ===============================================================================================

def dump_trainer_names(writer: Writer, rom: Memory, ids):
	for n in ids:
		writer.string_prop(hexbyte(n), rom.get_trainer_encounter_name(n))


#== Maps ===================================================================================================

def encounter_repr(rom: Memory, n: int) -> str:
	if n < 200:
		return rom.get_mon_name(n, grepr="#").strip()
	else:
		return "trainer: " + rom.get_trainer_encounter_name(n, grepr="#", default="<Glitch>").strip()

_actor_direction_names = {
	0x01: "UP_DOWN",
	0x02: "LEFT_RIGHT",
	0xD0: "DOWN",
	0xD1: "UP",
	0xD2: "LEFT",
	0xD3: "RIGHT",
}
def actor_direction_name(n: int) -> str:
	return _actor_direction_names.get(n, "RANDOM")

def actor_movement_name(n: int) -> str:
	if   n == 0xFF: return "STAY"
	elif n == 0xFE: return "WALK"
	else:           return str(0xFE - n)

def dump_encounter_list(writer: Writer, key: str, encounters, crepr):
	with writer.begin_set_prop(key):
		rows, coms = [], []
		for mon, level in sorted(encounters):
			mon, comment = writer.enum_repr(mon, g1const.wild_encounter_name, str, crepr=crepr)
			rows.append((mon, str(level)))
			coms.append(comment)
		writer.tuple_item_rows(rows, coms)

def dump_map_info(writer: Writer, rom: Memory, n: int):
	info = rom.get_map_info(n)

	if info.tileset is not None:
		writer.tuple_prop("size", (str(info.width), str(info.height)))
		writer.enum_prop("tileset", info.tileset, g1const.tileset_name, hexbyte)
	
	sbank, music = info.sound_bank & rom.rom_bank_mask, info.music
	writer.enum_prop("soundbank", sbank, g1const.sound_bank_name, hexbyte)
	writer.enum_prop("music", music, lambda n: g1const.sound_name(sbank, n, rom.is_yellow), hexbyte)

	if info.land_rate:  writer.prop("landRate",  info.land_rate,  comment=percent(info.land_rate))
	if info.water_rate: writer.prop("waterRate", info.water_rate, comment=percent(info.water_rate))

	if info.connections:
		connections = info.connections
		with writer.begin_object_prop("connections"):
			for dir in ("north", "south", "east", "west"):
				connection = connections.get(dir)
				if connection is not None:
					mapname = writer.enum_repr(connection.map, g1const.map_name, hexbyte, yellow=rom.is_yellow)[0]
					writer.tuple_prop(dir, ( mapname, ))

	if info.warps:
		with writer.begin_list_prop("warps"):
			warps = []
			for warp in info.warps:
				mapname = writer.enum_repr(warp.map, g1const.map_name, hexbyte, yellow=rom.is_yellow)[0]
				warps.append(( str(warp.x), str(warp.y), mapname, str(warp.warpdest) ))
			writer.tuple_item_rows(warps)

	if info.signs:
		with writer.begin_list_prop("signs"):
			signs = []
			for sign in info.signs:
				signs.append(( str(sign.x), str(sign.y), hexaddr(sign.script) ))
			writer.tuple_item_rows(signs)

	if info.actors:
		with writer.begin_list_prop("actors"):
			actors = []
			for actor in info.actors:
				sprite   = writer.enum_repr(actor.sprite, g1const.sprite_name, 
											hexbyte, yellow=rom.is_yellow)[0]
				movement = actor_movement_name(actor.movement)
				dir      = actor_direction_name(actor.direction)
				actors.append(( str(actor.x), str(actor.y), sprite, movement, dir, hexaddr(actor.script) ))
			writer.tuple_item_rows(actors)

	crepr = lambda n: encounter_repr(rom, n)
	if info.land_rate:  dump_encounter_list(writer, "landEncounters",  info.land_encounters,  crepr)
	if info.water_rate: dump_encounter_list(writer, "waterEncounters", info.water_encounters, crepr)

	writer.prop("headerAddr",    hexaddr(info.header_addr))
	if info.block_addr is not None:
		writer.prop("tilemapAddr", hexaddr(info.block_addr))
	if info.objects_addr is not None:
		writer.prop("objectsAddr", hexaddr(info.objects_addr))
	writer.prop("encounterAddr", hexaddr(info.encounter_addr))


#== Text verbs =============================================================================================

def dump_mon_species(rom: Memory, n: int, syntax:str=DEFAULT_SYNTAX):
	with Writer(syntax) as writer:
		writer.begin_object_item()
		dump_mon_species_info(writer, rom, n, combined=True)

def dump_mon_family(rom: Memory, n: int, syntax:str=DEFAULT_SYNTAX):
	with Writer(syntax) as writer:
		writer.begin_object_item()
		dump_mon_family_info(writer, rom, n)

def dump_move(rom: Memory, n: int, syntax:str=DEFAULT_SYNTAX):
	with Writer(syntax) as writer:
		writer.begin_object_item()
		dump_move_info(writer, rom, n)

def dump_map(rom: Memory, n: int, syntax:str=DEFAULT_SYNTAX):
	with Writer(syntax) as writer:
		writer.begin_object_item()
		dump_map_info(writer, rom, n)

def dump_all_glitchmons(rom: Memory, syntax:str=DEFAULT_SYNTAX):
	with Writer(syntax) as writer:
		with writer.begin_top_level_dict("glitchmon_families"):
			for n in rom.find_all_glitchmon_dex_nums():
				with writer.begin_dict_prop(str(n)):
					dump_mon_family_info(writer, rom, n)
		with writer.begin_top_level_dict("glitchmon_species"):
			for n in g1const.glitchmon_ids:
				with writer.begin_dict_prop(str(n)):
					dump_mon_species_info(writer, rom, n)

def _dump_glitchmon_families(rom, syntax, ids):
	with Writer(syntax, dict="glitchmonFamilies") as writer:
		for n in ids:
			with writer.begin_dict_prop(str(n)):
				dump_mon_family_info(writer, rom, n)
def dump_all_glitchmon_families(rom: Memory, syntax:str=DEFAULT_SYNTAX):
	_dump_glitchmon_families(rom, syntax, g1const.glitchmon_dex_nums, syntax)
def dump_all_unused_glitchmon_families(rom: Memory, syntax:str=DEFAULT_SYNTAX):
	_dump_glitchmon_families(rom, syntax, rom.find_all_unused_glitch_dex_nums())

def dump_all_glitch_moves(rom: Memory, syntax:str=DEFAULT_SYNTAX):
	with Writer(syntax, dict="glitchMoves") as writer:
		dump_moves(writer, rom, g1const.glitch_move_ids)

def dump_all_glitch_types(rom: Memory, syntax:str=DEFAULT_SYNTAX):
	with Writer(syntax, dict="glitchTypes") as writer:
		dump_type_names(writer, rom, g1const.glitch_type_ids)

def dump_all_used_glitchmon_palettes(rom: Memory, syntax:str=DEFAULT_SYNTAX):
	with Writer(syntax, dict="glitchPalettes") as writer:
		dump_palettes(writer, rom, rom.find_all_used_glitchmon_palette_ids())

def dump_all_glitch_exp_groups(rom: Memory, syntax:str=DEFAULT_SYNTAX):
	with Writer(syntax, dict="glitchExpGroups") as writer:
		dump_exp_groups(writer, rom, g1const.glitch_exp_group_ids)

def dump_all_used_glitch_exp_groups(rom: Memory, syntax:str=DEFAULT_SYNTAX):
	with Writer(syntax, dict="glitchExpGroups") as writer:
		dump_exp_groups(writer, rom, rom.find_all_used_exp_groups())

def dump_all_glitchmon_cries(rom: Memory, syntax:str=DEFAULT_SYNTAX):
	with Writer(syntax, dict="glitchmonCries") as writer:
		dump_mon_cries(writer, rom, g1const.glitchmon_ids)
	
def dump_all_used_glitch_trainer_names(rom: Memory, syntax=DEFAULT_SYNTAX):
	with Writer(syntax, dict="glitchTrainerNames") as writer:
		dump_trainer_names(writer, rom, g1const.glitch_trainer_encounter_ids)

def dump_all_glitch_items(rom: Memory, syntax=DEFAULT_SYNTAX):
	with Writer(syntax, dict="glitchItems") as writer:
		dump_items(writer, rom, g1const.glitch_item_ids)


#== Image verbs ============================================================================================

def write_2bpp_png(path, width, height, rows, palette):
	import png
	writer = png.Writer(
		width       = width,
		height      = height,
		palette     = palette,
		greyscale   = (palette is None),
		bitdepth    = 2,
		compression = 9
	)
	with open(path, "wb") as outfile:
		writer.write_packed(outfile, rows)

def export_tileset_gfx(rom: Memory, path: str, n: int):
	write_2bpp_png(path, 128, 48, rom.get_tileset_gfx_bitmap(n), None)

def export_tileset_blocks(rom: Memory, basepath: str, n: int, full:bool=None):
	i = 0
	for rows in rom.get_tileset_block_bitmaps(n, glitch=(full == "full")):
		write_2bpp_png(os.path.join(basepath, f"{i:03}.png"), 32, 32, rows, None)
		i += 1

def export_map(rom: Memory, path: str, n: int, color:str=None):
	write_2bpp_png(path, *rom.get_map_bitmap(n, color=color))

def export_displaced_map(rom: Memory, path: str, map: int, blockaddr: int, x: int, y: int, color:str=None):
	write_2bpp_png(path, *rom.get_glitch_map_bitmap(map, blockaddr, x, y, color=color))

def export_glitch_city(rom: Memory, path: str, map: int, warp: int, color:str=None):
	write_2bpp_png(path, *rom.get_glitch_city_bitmap(map, warp, color=color))

def export_map_actors(rom: Memory, path: str, n: int, color:str=None):
	write_2bpp_png(path, *rom.get_map_actors_bitmap(n, color=color))

def export_mon_frontsprite(rom: Memory, path: str, n: int, color=None):
	write_2bpp_png(path, *rom.get_mon_frontsprite_bitmap(n, color=color))
def export_mon_backsprite(rom: Memory, path: str, n: int, color=None):
	write_2bpp_png(path, *rom.get_mon_backsprite_bitmap(n, color=color))

def export_dex_mon_frontsprite(rom: Memory, path: str, n: int, color:str=None):
	write_2bpp_png(path, *rom.get_dex_mon_frontsprite_bitmap(n, color=color))
def export_dex_mon_backsprite(rom: Memory, path: str, n: int, color:str=None):
	write_2bpp_png(path, *rom.get_dex_mon_backsprite_bitmap(n, color=color))

def export_trainer_sprite(rom: Memory, path: str, n: int, color:str=None):
	write_2bpp_png(path, *rom.get_trainer_sprite_bitmap(n, color=color))


# ==========================================================================================================
if __name__ == "__main__":

	_verbs = {
		"mon":                           dump_mon_species,
		"mon-family":                    dump_mon_family,
		"move":                          dump_move,
		"map-info":                      dump_map,
		"all-glitchmons":                dump_all_glitchmons,
		"all-glitchmon-families":        dump_all_glitchmon_families,
		"all-unused-glitchmon-families": dump_all_unused_glitchmon_families,
		"all-glitch-moves":              dump_all_glitch_moves,
		"all-glitch-types":              dump_all_glitch_types,
		"all-used-glitch-trainers":      dump_all_used_glitch_trainer_names,
		"all-used-glitchmon-palettes":   dump_all_used_glitchmon_palettes,
		"all-glitch-exp-groups":         dump_all_glitch_exp_groups,
		"all-used-glitch-exp-groups":    dump_all_used_glitch_exp_groups,
		"all-glitchmon-cries":           dump_all_glitchmon_cries,
		"all-glitch-items":              dump_all_glitch_items,

		"map":                           export_map,
		"displaced-map":                 export_displaced_map,
		"glitchcity":                    export_glitch_city,
		"mon-sprite":                    export_mon_frontsprite,
		"mon-frontsprite":               export_mon_frontsprite,
		"mon-backsprite":                export_mon_backsprite,
		"mon-family-sprite":             export_dex_mon_frontsprite,
		"mon-family-frontsprite":        export_dex_mon_frontsprite,
		"mon-family-backsprite":         export_dex_mon_backsprite,
		"trainer-sprite":                export_trainer_sprite,

		"tileset-gfx":                   export_tileset_gfx,
		"tileset-blocks":                export_tileset_blocks
	}

	def error(msg):
		print(msg, file=sys.stderr)
		exit(1)

	def print_usage():
		usage = "Usage: g1dump.py <rom_path> <verb> [args...]"
		error(usage)

	def typed_args(func, args):
		argnames = func.__code__.co_varnames
		argtypes = func.__annotations__
		for i in range(len(args)):
			arg, argtype = args[i], argtypes.get(argnames[i+1])
			if argtype is int: arg = int(arg, 0)
			yield arg

	if len(sys.argv) < 3:
		print_usage()

	try: rom = g1utils.open_rom(sys.argv[1])
	except IOError as e:
		error(f"Couldn't open ROM file: {sys.argv[1]}: {e}")

	verb = _verbs.get(sys.argv[2])
	if verb is None:
		error(f"Unknown verb: {sys.argv[2]}")	
	verb(rom, *typed_args(verb, sys.argv[3:]))
