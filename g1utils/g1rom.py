# g1rom.py
from __future__ import annotations

from .g1base import *
from .g1text import *

import g1const


#== Mons ===================================================================================================

def get_mon_name_bytes(rom: Memory, n: int) -> bytes:
	"""Return the raw bytes of mon `n`'s name."""
	return rom.table_read_bytes("mon_names", 5 if rom.is_japan else 10, (n - 1) & 0xFF)
def get_mon_name(rom: Memory, n: int, **opt) -> str:
	"""Return the name of mon `n`."""
	return decode_string(rom.lang, rom.get_mon_name_bytes(n), **opt)

def get_mon_dex_num(rom: Memory, n: int) -> int:
	"""Return the dex number of mon `n`."""
	return rom.table_read8("dex_nums", (n - 1) & 0xFF)

def get_dex_mon_info(rom: Memory, n: int) -> Info:
	"""
	Return all information for a mon with dex number `n`.
	This combines:
	  - `get_dex_mon_base_stats`
	  - `get_dex_mon_party_sprite`
	  - `get_dex_mon_palette_id`
	"""
	info = rom.get_dex_mon_base_stats(n)
	info.party_sprite = rom.get_dex_mon_party_sprite(n)
	info.palette      = rom.get_dex_mon_palette_id(n)
	return info

def get_mon_info(rom: Memory, n: int) -> Info:
	"""
	Return all information for mon `n`.
	This combines:
	  - `get_mon_name`
	  - `get_mon_base_stats`
	  - `get_mon_cry`
	  - `get_mon_party_sprite`
	  - `get_mon_palette_id`
	  - `get_mon_sprite_bank`
	  - `get_mon_learnset`
	  - `get_mon_evolutions`
	  - `get_mon_dex_entry`
	"""
	dexno = rom.get_mon_dex_num(n)
	info  = rom.get_dex_mon_info(dexno)
	info.dex_num     = dexno
	info.name        = rom.get_mon_name(n)
	info.cry         = rom.get_mon_cry_sound(n)
	info.sprite_bank = rom.get_mon_sprite_bank(n)
	rom.get_mon_learnset(n, info)
	rom.get_mon_evolutions(n, info)
	rom.get_mon_dex_entry(n, info)
	return info

def get_dex_mon_base_stats_ptr(rom: Memory, n: int) -> ptr:
	"""Return a pointer to the base stats of a mon with dex number `n`."""
	if n == 151 and not rom.is_yellow:
		return rom.location("base_stats_mew")
	else:
		return rom.table_index_ptr("base_stats", 28, (n - 1) & 0xFF)
def get_mon_base_stats_ptr(rom: Memory, n: int) -> ptr:
	"""Return a pointer to the base stats of mon `n`."""
	return rom.get_dex_mon_base_stats_ptr(rom.get_mon_dex_num(n))

def get_dex_mon_base_stats(rom: Memory, n: int, moves:bool=True):
	"""Return the base stats of a mon with dex number `n`."""
	bank, addr = rom.get_dex_mon_base_stats_ptr(n)
	data = rom.read_bytes(bank, addr, 20)

	# having only one type is encoded as the same type twice
	type = data[6:8]
	if type[0] == type[1]: type = type[:1]

	bbox = data[10]
	bbox = ((bbox & 0xF) or 256, (bbox >> 4) or 256)

	info = Info(
		stats            = tuple(data[1:6]),
		type             = tuple(type),
		catch_rate       = data[8],
		exp_yield        = data[9],
		exp_group        = data[19],
		frontsprite_bbox = bbox,
		frontsprite_addr = unpack16(data, 11),
		backsprite_addr  = unpack16(data, 13)
	)
	if moves:
		info.start_moves   = trim_mon_moves(data[15:19])
		info.machine_moves = expand_machine_flags(rom.read_bytes(bank, addr + 20, 8))
	return info

def get_mon_base_stats(rom: Memory, n: int, moves:bool=True):
	"""Return the base stats of mon `n`."""
	return rom.get_dex_mon_base_stats(rom.get_mon_dex_num(n), moves)

def expand_machine_flags(flags: bytes) -> bytearray:
	"""Convert a mon's TM/HM flags from a bitfield to a list of move IDs."""
	moves = bytearray()
	for i in range(55):
		if (flags[i >> 3] >> (i & 7)) & 1 != 0:
			moves.append(g1const.machine_move(i))
	return moves

def get_mon_cry(rom: Memory, n: int) -> tuple[int, int, int]:
	"""Return the basecry ID, pitch, and tempo of mon `n`'s cry."""
	basecry, pitch, tempo = rom.table_read_bytes("cries", 3, (n - 1) & 0xFF)
	return basecry, pitch, tempo - 0x80
def get_mon_cry_sound(rom: Memory, n: int) -> tuple[int, int, int]:
	"""Return the sound ID, pitch, and tempo of mon `n`'s cry."""
	basecry, pitch, tempo = rom.get_mon_cry(n)
	# Base cry ID is multiplied by 3 and added to 0x14 to get the proper sound ID.
	# The way the game multiplies by 3 here only works for small values, though:
	# it's intended to be x = (x<<1)+x but the devs used a bitwise rotate instruction
	# instead of a bitwise shift to save a byte. This works correctly for non-glitch
	# base cries so it's not really a bug, but glitch base cries above 0x7F aren't
	# correctly multiplied by 3.
	return (0x14 + (basecry << 1 | basecry >> 7) + basecry) & 0xFF, pitch, tempo

def get_dex_mon_party_sprite(rom: Memory, n: int) -> int:
	"""Return the party menu sprite ID of a mon with dex number `n`."""
	return rom.table_read4("party_sprites", (n - 1) & 0xFF)
def get_mon_party_sprite(rom: Memory, n: int) -> int:
	"""Return the party menu sprite ID of mon `n`."""
	return rom.get_dex_mon_party_sprite(rom.get_mon_dex_num(n))

def get_dex_mon_palette_id(rom: Memory, n: int) -> int:
	"""Return the palette ID of a mon with dex number `n`."""
	return rom.table_read8("mon_palettes", n)
def get_mon_palette_id(rom: Memory, n: int) -> int:
	"""Return the palette ID of mon `n`."""
	# mon 0 is hardcoded to always use Missingno's palette
	return get_dex_mon_palette_id(rom, n and get_mon_dex_num(rom, n))

def get_mon_evolutions_ptr(rom: Memory, n: int) -> ptr:
	"""Return a pointer to mon `n`'s evolution list."""
	return rom.table_read_addr("learnsets_evos", (n - 1) & 0xFF)

def get_mon_learnset_ptr(rom: Memory, n: int) -> ptr:
	"""Return a pointer to mon `n`'s level-up learnset."""
	s = rom.stream(*rom.get_mon_evolutions_ptr(n))
	while next(s) != 0: pass # skip over evolutions
	return s.rom_bank, s.addr
	
def get_mon_learnset(rom: Memory, n: int, info=None) -> dict[int, int]:
	moves, addr = {}, None
	try:
		bank, addr = rom.get_mon_learnset_ptr(n)
		s = rom.stream(bank, addr)
		for level in s:
			if level == 0: break
			move = next(s)
			# Only one move can be learned per level-up in Gen 1, so only the first move
			# in the movelist for any given level is actually learnable. Any later moves 
			# for that level will be "shadowed" by the first one.
			if level not in moves: moves[level] = move
	except AddressError: pass

	if info:
		info.moves_addr  = addr
		info.level_moves = moves
	return moves

def get_mon_evolutions(rom: Memory, n: int, info=None) -> Info:
	level_evos, item_evos, trade_evos, addr = {}, {}, {}, None
	
	# The game doesn't actually stop iterating through a mon's evolution entries
	# after finding a match, so evolution entries cannot actually "shadow" other
	# entries later in the list. This also means the same mon can evolve multiple
	# times in a row if it has multiple evolutions that match the criteria.
	
	# Index FF glitchmons can never evolve because the evolution routine interprets
	# them as the end-of-party marker.
	if n != 0xFF:
		try:
			bank, addr = rom.get_mon_evolutions_ptr(n)
			s = rom.stream(bank, addr)
			t = s.next8()
			while t == 3:    # EV_TRADE
				# trade evolutions only work if they are first in the list
				level, mon = s.next_bytes(2)
				if level not in trade_evos:
					trade_evos[level] = mon
				t = s.next8()
			while t != 0:
				if   t == 1: # EV_LEVEL
					level, mon = s.next_bytes(2)
					if level not in level_evos:
						level_evos[level] = mon
				elif t == 2: # EV_ITEM
					item, level, mon = s.next_bytes(3)
					if item not in item_evos:
						item_evos[item] = mon
				else:        # EV_TRADE, all glitch evos (non-functional)
					s.skip(2)
				t = s.next8()
	
		except AddressError: pass

	if info is None: info = Info()
	info.evos_addr  = addr
	info.level_evos = level_evos
	info.item_evos  = item_evos
	info.trade_evos = trade_evos
	return info

def get_mon_dex_entry_ptr(rom: Memory, n: int) -> ptr:
	return rom.table_read_addr("dex_entries", (n - 1) & 0xFF, default=None)

def get_mon_dex_entry(rom: Memory, n: int, info=None, **opt) -> Info:
	"""
	Get a mon's dex entry.
	"""
	opt.setdefault("vchar", "dex")

	bank, addr = rom.get_mon_dex_entry_ptr(n)
	metric     = rom.lang != 'E'

	if info is None: info = Info()
	info.dex_addr  = addr
	info.is_metric = metric

	s = rom.stream(bank, addr)
	try:
		info.category = s.next_string(**opt)
		
		if metric:
			# u8 decimeters, u16 hectograms
			info.height, info.weight = s.next8(), s.next16()
		else:
			# u8 feet, u8 inches, u16 tenths of pounds
			info.height, info.weight = tuple(s.next_bytes(2)), s.next16()

		# In Japanese versions dex descriptions are just strings, but in localized versions they're changed
		# to be text scripts instead. This was probably just done to enable quick-and-dirty repointing of
		# descriptions to other banks with the far command, like with most of the localized text.
		info.desc_addr = s.addr
		if rom.is_japan:
			info.description = s.next_string(**opt)
		else:
			if opt.setdefault("sound_bank", 8) == 8:
				# If the battle soundbank is used, we can safely assume the last sounds played are:
				# ball_shake, dex_registered, ui_press, and the mon's cry (or Rhydon's cry, if the mon
				# has a glitch dex number.)
				dexno = rom.get_mon_dex_num(n)
				if "prev_sfx" not in opt and (not(0 < n <= 190) or dexno == 0):
					cry = rom.get_mon_cry_sound(n if (0 < dexno <= 151) else 1)
					opt["prev_sfx"] = (0x93, 0x98, 0x90, cry[0])
			info.description = rom.read_text_script(bank, s.addr, **opt)
	
	except AddressError: pass
	return info


#== Moves ==================================================================================================

def get_move_name(rom: Memory, n: int, **opt) -> str:
	return rom.get_packed_name(*rom.location("move_names"), n, **opt)

def get_move_info(rom: Memory, n: int) -> Info:
	data = rom.table_read_bytes("moves", 6, (n - 1) & 0xFF)
	return Info(
		animation = data[0],
		effect    = data[1],
		power     = data[2],
		type      = data[3],
		accuracy  = data[4],
		pp        = data[5]
	)

def get_move_effect_ptr(rom: Memory, n: int) -> ptr:
	return rom.table_read_addr("move_effects", (n - 1) & 0xFF)


#== Types ==================================================================================================

def get_type_name_ptr(rom: Memory, n: int) -> ptr:
	return rom.table_read_addr("type_names", (n & 0x7F))
def get_type_name(rom: Memory, n: int, **opt) -> str:
	return rom.read_string(*rom.get_type_name_ptr(n), **opt)


#== Exp groups =============================================================================================

def _gcd(a, b): # compute greatest common denominator
	while b: a, b = b, a%b
	return a
def get_exp_group_coefficients(rom: Memory, n: int) -> tuple[int]:
	"""Return the coefficients of the experience group formula `n`."""
	ab, c, d, e = rom.table_read_bytes("exp_formulas", 4, n & 0x3F)
	a, b = ab >> 4, ab & 0xF
	if b != 0: # reduce the fraction
		f = _gcd(a, b); a, b = a//f, b//f
	# instead of two's complement, c uses a sign bit for some reason
	if c & 0x80: c = -(c & 0x7F)
	return a, b, c, d, -e

def exp_group_formula_repr(coefficients: tuple[int]) -> str:
	"""Return a text representation of an experience formula with the given coefficients."""
	a, b, c, d, e = coefficients
	if b == 0: return "x / 0"
	s = []
	if a:
		if   b != 1: s.append(f"({a}/{b})")
		elif a != 1: s.append(str(a))
		s.append("x^3")
	if c:
		if s:
			s.append(" - " if c < 0 else " + ")
			c = abs(c)
		if c != 1: s.append(str(c))
		s.append("x^2")
	if d:
		if s:      s.append(" + ")
		if d != 1: s.append(str(d))
		s.append("x")
	if s:
		if e: s.append(f" - {abs(e)}")
		return ''.join(s)
	else:
		return str(e)

def get_exp_group_formula(rom: Memory, n: int) -> str:
	"""
	Return a text representation of an experience group's formula.
	An experience group formula is of the form `(a/b)x^3 + cx^2 + dx - e`.
	"""
	return exp_group_formula_repr(rom.get_exp_group_coefficients(n))


#== Items ==================================================================================================

def get_item_name(rom: Memory, n: int, **opt) -> str:
	return rom.get_packed_name(*rom.location("item_names"), n, **opt)

def get_item_price(rom: Memory, n: int) -> int:
	if n < 201:
		return bcd_to_int(rom.table_read_bytes("item_prices", 3, (n - 1) & 0xFF))
	else:
		return rom.table_read4("tm_prices", n - 201) * 1000

def get_item_effect_ptr(rom: Memory, n: int) -> ptr:
	return rom.table_read_addr("item_effects", n & 0x7F)

def is_key_item(mem: Memory, n: int) -> bool:
	if n < 196:
		# The game copies 15 bytes from the key item bitfield into a RAM buffer before examining it.
		# Therefore, only the first 120 bits come from ROM, and the remaining 76 bits come from
		# whatever was last in the RAM buffer.
		i = n >> 3
		if i < 15: b = mem.table_read8("key_items", i)
		else:      b = mem.table_read8("buffer",    i)
		return bool((b >> (n & 7)) & 1)
	else:
		return (n < 201) # HMs are key items, TMs are not


#== Trainers ===============================================================================================

def get_trainer_class_name(rom: Memory, n: int, **opt) -> str:
	opt.setdefault("vchar", "battle")
	if n in (0x19, 0x2A, 0x2B):
		return decode_string(rom.lang, b"\x53", **opt)
	return rom.get_packed_name(*rom.location("trainer_names"), n, length=13, **opt)

def get_trainer_encounter_name(rom: Memory, n: int, **opt) -> str:
	return rom.get_trainer_class_name((n - 200) & 0xFF, **opt)

def get_trainer_class_prize_money(rom: Memory, n: int) -> str:
	bank, addr = rom.table_index_ptr("trainer_gfx_pay", 5, n)
	return rom.read_bytes(bank, addr + 2, 2) # third BCD byte goes unused

def get_trainer_class_ai_info(rom: Memory, n: int):
	"""
	@return the bank+addr of the AI routine, and the max number of AI calls per mon
	"""
	bank, addr = rom.location("trainer_ai")
	info = rom.read_bytes(bank, addr + n*3, 3)
	return bank, unpack16(info, 1), info[0]

def get_trainer_team_ptr(rom: Memory, trainer: int, team: int):
	bank, addr = rom.table_read_addr("trainer_teams", (trainer - 1) & 0xFF)
	s = rom.stream(bank, addr)

	# Teams are null-terminated and stored sequentially.
	# Skip all the teams before the one we're looking for.
	for _ in range((team - 1) & 0xFF):
		while next(s) != 0: pass
	return bank, s.addr

def get_trainer_team(rom: Memory, trainer: int, team: int):
	s = rom.stream(*get_trainer_team_ptr(rom, trainer, team))

	# If the team's level is FF, each member's level is specified individually.
	# Otherwise, every member has the team's level.
	level, team = s.next8(), []
	if level == 0xFF:
		for level in s:
			if level == 0: break
			team.append((s.next8(), level))
	else:
		for mon in s:
			if mon == 0: break
			team.append((mon, level))

	return tuple(team)


#== Tilesets ===============================================================================================

def get_tileset_header_ptr(rom: Memory, n: int) -> ptr:
	bank, addr = rom.location("tilesets")
	return bank, addr + ((n * 12) & 0x1FF)

_tileset_lengths = bytes((
	128, 19,  37,  128, 19,  116,
	37,  116, 35,  128, 128, 17,
	128, 62,  23,  110, 58,  128,
	79,  72,  58,  36,  128, 75,
	
	# Yellow only
	20
))
def get_tileset_num_blocks(rom: Memory, n: int, glitch:bool=False) -> int:
	"""
	Returns the number of blocks in tileset `n`.
	If `glitch` is `True` or `n` is a glitch tileset ID, the returned length will be 256.
	"""
	if not glitch and n < (0x18 if rom.is_yellow else 0x17):
		return _tileset_lengths[n]
	return 256

def get_tileset_block_ptr(rom: Memory, n: int) -> ptr:
	"""Returns a pointer to tileset `n`'s block data."""
	bank, addr = rom.get_tileset_header_ptr(n)
	return rom.read8(bank, addr), rom.read16(bank, addr + 1)

def get_tileset_block_data(rom: Memory, n: int, glitch:bool=False) -> bytes:
	bank, addr = rom.get_tileset_block_ptr(n)
	nblocks    = rom.get_tileset_num_blocks(n, glitch)
	return rom.read_bytes(bank, addr, nblocks*16, allow_partial=True)

def get_tileset_blocks(rom: Memory, n: int, glitch:bool=False) -> Generator[bytes]:
	s = rom.stream(*rom.get_tileset_block_ptr(n))
	for _ in range(rom.get_tileset_num_blocks(n, glitch)):
		yield s.next_bytes(16)

def get_tileset_metatiles(rom: Memory, n: int, glitch:bool=False) -> set[bytes]:
	"""Return all unique 2x2 metatiles in the given tileset."""
	s = rom.stream(*rom.get_tileset_block_ptr(n))
	tiles = set()
	for _ in range(rom.get_tileset_num_blocks(n, glitch)):
		b = s.next_bytes(16)
		tiles.add(bytes(b[0], b[1], b[4], b[5] ))
		tiles.add(bytes(b[2], b[3], b[6], b[7] ))
		tiles.add(bytes(b[8], b[9], b[12],b[13]))
		tiles.add(bytes(b[10],b[11],b[14],b[15]))
	return tiles

def get_tileset_tile_info(rom: Memory, n: int) -> Info:
	bank, addr = rom.get_tileset_header_ptr(n)
	data = rom.read_bytes(bank, addr + 5, 7)
	
	walk_addr  = unpack16(data, 0)
	counters   = data[2:5] # Counter tile IDs (list of tile IDs the player can talk to NPCs across)
	grass      = data[5]   # Tall grass tile ID
	anims      = data[6]   # Tileset animations (water, flowers)
	
	# Collision data (list of tile IDs that can be walked on)
	# All nonglitch collision data is located in the home bank, so any glitch tilesets whose
	# collision pointer points to the switchable ROM bank will end up pulling their collision data
	# from whatever bank is currently mapped. Unfortunately for us, there are several different
	# routines that read from collision data, and each one ends up having a different bank mapped:
	#   - Player movement routines are in home bank, the bank mapped is the current map's bank
	#   - NPC and Strength boulder movement routines are in switchable banks, so the bank mapped
	#     is the bank containing the respective routine
	walkable = set()
	for b in rom.stream(None, walk_addr, allow_partial=True):
		if b == 0xFF: break
		walkable.add(b)
	
	# Warp tile IDs
	warp_tiles, warp_bank, warp_addr = set(), *rom.table_read_addr("warp_tiles", n)
	for b in rom.stream(warp_bank, warp_addr, allow_partial=True):
		if b == 0xFF: break
		warp_tiles.add(b)

	return Info(
		walkable_tiles      = walkable,
		walkable_tiles_addr = walk_addr,
		warp_tiles          = warp_tiles,
		warp_tiles_addr     = warp_addr,
		counter_tiles       = set(counters),
		grass_tile          = grass,
		water_anim          = anims != 0,
		flower_anim         = anims != 0 and (anims & 1) == 0
	)

TILE_WALKABLE = 1 << 1
TILE_WARP     = 1 << 2
TILE_COUNTER  = 1 << 3
TILE_GRASS    = 1 << 4
def get_tileset_tile_attributes(rom: Memory, n: int, glitch:bool=False) -> tuple:
	ntiles = 0x60 if not glitch else 0x100
	tiles  = bytearray(ntiles)
	info   = rom.get_tileset_tile_info(n)	

	tiles[info.grass_tile] |= TILE_GRASS

	for tile in info.walkable_tiles:
		tiles[tile] |= TILE_WALKABLE

	for tile in info.counter_tiles:
		tiles[tile] |= TILE_COUNTER

	for tile in info.warp_tiles:
		tiles[tile] |= TILE_WARP


#== Maps ===================================================================================================

Warpdest = tuple[int,int,int]

# lookup table for map connections bitfield
_bitcount = b"\0\1\1\2\1\2\2\3\1\2\2\3\2\3\3\4"

def get_map_header_ptr(rom: Memory, n: int) -> ptr:
	return rom.table_read8("map_banks", n), rom.table_read16("map_headers", n)

def get_map_objects_ptr(rom: Memory, n: int) -> ptr:
	bank, addr = rom.get_map_header_ptr(n)
	# skip map connections:
	cflags = rom.read8(bank, addr + 9) & 0xF
	return bank, rom.read16(bank, addr + 10 + _bitcount[cflags] * 11)

def get_map_objptr_actors_addr(rom: Memory, bank: int, addr: int) -> int:
	# skip border block and warps:
	addr += 2 + rom.read8(bank, addr+1)*4
	# skip signposts:
	addr += 1 + rom.read8(bank, addr)*3
	return addr

def get_map_objptr_warpdests_addr(rom: Memory, bank: int, addr: int) -> int:
	# skip border block and warps:
	addr += 2 + rom.read8(bank, addr+1)*4
	# skip signposts:
	addr += 1 + rom.read8(bank, addr)*3
	# skip actors:
	count = rom.read8(bank, addr)
	addr += 1
	for _ in range(count):
		# actor struct is variable-length so we can't just trivially jump past the whole list
		t = rom.read8(bank, addr+5)
		if   t & 0x40 != 0: addr += 8
		elif t & 0x80 != 0: addr += 7
		else:               addr += 6
	return addr

_directions = ("north", "south", "west", "east")
def get_map_info(rom: Memory, n: int) -> Info:

	bank, addr = rom.get_map_header_ptr(n)
	info = Info(
		bank        = bank,
		header_addr = addr
	)

	s = rom.stream(bank, addr)
	try:
		data = s.next_bytes(10)
		textscript_addr = unpack16(data, 5)
		info.update(
			width           = data[2],
			height          = data[1],
			tileset         = data[0],
			block_addr      = unpack16(data, 3),
			textscript_addr = textscript_addr,
			mapscript_addr  = unpack16(data, 7),
		)

		connections = {}
		i, cflags   = 0, data[9] & 0xF
		while i < 4:
			if cflags & (8 >> i):
				data = s.next_bytes(11)
				connections[_directions[i]] = Info(
					map = data[0],
					# TODO: coordinates/offset
				)
			i += 1
		info.connections = connections
		
		objects_addr      = s.next16()
		info.objects_addr = objects_addr
		_read_map_objects(rom, bank, objects_addr, info, textscript_addr)
	except AddressError: pass

	info.sound_bank, info.music = rom.get_map_soundbank_and_music(n)

	rom.get_map_wild_encounters(n, info)

	return info

def get_map_drawable_info(rom: Memory, n: int) -> Info:
	bank, addr = rom.get_map_header_ptr(n)
	data = rom.read_bytes(bank, addr, 5)
	width, height = data[2] or 256, data[1] or 256
	return Info(
		bank         = bank,
		header_addr  = addr,
		width        = width,
		height       = height,
		tileset      = data[0],
		block_addr   = unpack16(data, 3),
		block_step   = width
	)

def _read_map_objects(rom: Memory, bank, addr, info, textscript_addr):
	border    = None
	warps     = []
	signs     = []
	actors    = []
	warpdests = []

	i = rom.stream(bank, addr)
	try:
		border = i.next8()
	
		nwarps = i.next8()
		for _ in range(nwarps):
			data = i.next_bytes(4)
			warps.append(Info(
				x        = data[1],
				y        = data[0],
				map      = data[3],
				warpdest = data[2]
			))
	
		info.signs_addr = i.addr
		for _ in range(i.next8()):
			data = i.next_bytes(3)
			script = data[2]
			if textscript_addr is not None:
				script = rom.read16(bank, textscript_addr + ((script - 1) & 0xFF) * 2)
			sign = Info(
				x         = data[1],
				y         = data[0],
				script_id = script
			)
			signs.append(sign)

		info.actors_addr = i.addr
		actors = _read_map_actors(i, rom, textscript_addr)

		info.warpdests_addr = i.addr

	except AddressError:
		pass

	info.border    = border
	info.warps     = warps
	info.signs     = signs
	info.actors    = actors
	info.warpdests = warpdests
	return info

def _read_map_actors(i: Memory.Stream, rom: Memory, textscript_addr):
	actors = []
	for _ in range(i.next8()):
		data   = i.next_bytes(6)
		script = data[5]
		actor = Info(
			x         = data[2] - 4,
			y         = data[1] - 4,
			sprite    = data[0],
			movement  = data[3],
			facing    = data[4],
			script_id = script,
		)

		# Encounter flag is checked before item flag
		if   script & 0x40 != 0:
			actor.type = "encounter"
			actor.encounter = tuple(i.next_bytes(2))
		elif script & 0x80 != 0:
			actor.type = "item"
			actor.item = i.next8()
		else:
			actor.type = None

		if textscript_addr is not None:
			actor.script = rom.read16(i.rom_bank, textscript_addr + ((script - 1) & 0xFF) * 2)

		actors.append(actor)

	return actors

def get_map_objects(rom: Memory, n: int) -> Info:
	bank, addr = rom.get_map_objects_ptr(n)
	return _read_map_objects(rom, bank, addr, Info(), None)

def get_map_actors(rom: Memory, n: int) -> list[Info]:
	bank, addr = rom.get_map_objects_ptr(n)
	addr = get_map_objptr_actors_addr(rom, bank, addr)
	return _read_map_actors(rom, rom.stream(bank, addr), None)

def get_map_sprite_ids(rom: Memory, n: int, allow_partial:bool=False):
	sprites = bytearray()
	try:
		bank, addr = rom.get_map_objects_ptr(n)
		addr  = get_map_objptr_actors_addr(rom, bank, addr)
		count = rom.read8(bank, addr)
		addr += 1
		for _ in range(count):
			sprite = rom.read8(bank, addr)
			if sprite not in sprites:
				sprites.append(sprite)
				if len(sprites) >= 9: break
			t = rom.read8(bank, addr + 5)
			if   t & 0x40 != 0: addr += 8
			elif t & 0x80 != 0: addr += 7
			else:               addr += 6
	except AddressError:
		if not allow_partial: raise
	return sprites

def get_map_warpdest(rom: Memory, map: int, warp: int) -> Warpdest:
	bank, addr = rom.get_map_objects_ptr(map)
	addr = get_map_objptr_warpdests_addr(rom, bank, addr)
	data = rom.read_bytes(bank, addr + warp*4, 4)
	return unpack16(data,0), data[3], data[2]

def get_dungeon_warpdest(rom: Memory, map: int, warp: int) -> Warpdest:
	bank, addr = rom.location("dungeon_warp_ids")
	i = 0
	m, w = rom.read_bytes(bank, addr, 2)
	while m != map or w != warp:
		i = (i + 6) & 0xFF
		addr += 2
		m, w = rom.read_bytes(bank, addr, 2)
	bank, addr = rom.location("dungeon_warps")
	info = rom.read_bytes(bank, addr + i, 6)
	return unpack16(info,0), info[3]*2 + info[5], info[2]*2 + info[4]

def get_fly_warpdest(rom: Memory, n: int) -> Warpdest:
	bank, addr = rom.location("fly_warps")
	b = rom.read8(bank, addr)
	while b != n:
		addr += 4
		b = rom.read8(bank, addr)
	addr = rom.read16(bank, addr + 2)
	info = rom.read_bytes(bank, addr, 6)
	return unpack16(info,0), info[3]*2 + info[5], info[2]*2 + info[4]

def undisplace_map_addr(addr: int, step: int, x: int, y: int) -> int:
	"""
	Find the address of the top-left corner of a map given the block pointer for (x, y).
	"""
	return addr - (1 + step + step*(y>>1) + (x>>1))

def get_displaced_map_info(rom: Memory, info, blockaddr: int, x: int, y: int, unbound:bool=False) -> Info:
	width, height = info.width, info.height
	
	# The step interval is the offset added to a block address to advance down by one row
	# in the map buffer. It's equal to the map width plus 3 border blocks on each side.
	blockstep = width + 6
	
	# Find the top-left corner of the map (including border blocks)
	blockaddr = undisplace_map_addr(blockaddr, blockstep, x, y)

	# Set the boundaries to the "quadrant" of map space we're in.
	# If unbound is true, the boundaries encompass all of map space.
	if unbound:
		width, height = 128, 128
	else:
		w2, h2 = width*2, height*2
		if x > w2:
			blockaddr += width
			width = 128 - width
		elif x == w2:
			width = 128
		if y > h2:
			blockaddr += height * blockstep
			height = 128 - height
		elif y == h2:
			height = 128

	# Cut out the outermost border of blocks because those are never visible.
	# Add 6 to width and height to account for the border blocks,
	# but subtract 2 since the outermost border is never visible.
	blockaddr += blockstep + 1
	width     += 4
	height    += 4

	# Due to how the game's overworld logic is written, the current ROM bank whenever
	# the map buffer is accessed is the bank containing the current tileset's gfx and blocks.
	bank, _ = rom.get_tileset_block_ptr(info.tileset)

	return Info(
		bank       = bank,
		tileset    = info.tileset,
		width      = width,
		height     = height,
		block_addr = blockaddr,
		block_step = blockstep,
		player_x   = x,
		player_y   = y,
	)

def get_glitch_city_info(rom: Memory, map: int, warp: int) -> Info:
	info = rom.get_map_drawable_info(map)
	return rom.get_displaced_map_info(info, *rom.get_map_warpdest(map, warp))

def get_town_map_landmark_data(rom: Memory, n: int):
	if n < 0x24:
		bank, addr = rom.location("outdoor_map_names")
		addr += n*3
	else:
		bank, addr = rom.location("indoor_map_names")
		while rom.read8(bank, addr) <= n: addr += 4
		addr += 1
	xy, addr = rom.read8(bank, addr), rom.read16(bank, addr + 1)
	return xy >> 4, xy & 0xF, bank, addr
def get_town_map_landmark(rom: Memory, n: int, **opt):
	x, y, bank, addr = rom.get_town_map_landmark_data(n)
	return x, y, rom.read_string(bank, addr, **opt)

def get_map_soundbank_and_music(rom: Memory, n: int) -> tuple[int,int]:
	music, bank = rom.table_read_bytes("map_music", 2, n)
	return bank, music

def get_map_wild_encounter_ptr(rom: Memory, n: int) -> ptr:
	return rom.table_read_addr("wild_encounters", n)

def _read_encounters(s):
	encounters, rate = [], s.next8()
	if rate != 0:
		for _ in range(10):
			level, mon = s.next8(), s.next8()
			encounters.append((mon, level))
	return tuple(encounters), rate
def get_map_wild_encounters(rom: Memory, n: int, info=None) -> Info:
	"""
	Return the wild encounter data for map `n`.
	"""
	if info is None: info = Info()
	try:
		bank, addr = rom.get_map_wild_encounter_ptr(n)
		s = rom.stream(bank, addr)
		info.encounter_addr = addr
		info.land_encounters,  info.land_rate  = _read_encounters(s)
		info.water_encounters, info.water_rate = _read_encounters(s)
	except AddressError: pass
	return info


#== Glitch IDs =============================================================================================

def find_all_glitchmon_dex_nums(rom: Memory, hybrids=False) -> bytearray:
	"""Return a list of all dex numbers used by glitchmons."""
	ids = {0} # Missingno. is always #000
	bank, addr = rom.location("dex_nums")
	for n in rom.read_bytes(bank, addr + 190, 66):
		if n > 151 or hybrids: ids.add(n)
	return bytearray(sorted(ids))

def find_all_unused_glitch_dex_nums(rom: Memory, dex_nums=None) -> bytearray:
	"""Return a list of all glitch dex numbers not used by glitchmons."""
	if dex_nums is None: dex_nums = rom.find_all_glitchmon_dex_nums()
	dex_nums = iter(dex_nums); n = next(dex_nums)
	while n < 152: n = next(dex_nums)
	ids = bytearray()
	for i in range(152,256):
		if i == n:
			n = next(dex_nums, 0)
		else:
			ids.append(i)
	return ids

def find_all_learnable_glitch_moves(rom: Memory, dex_nums=None) -> bytearray:
	"""Return a list of all glitch moves learnable by glitchmons."""
	ids = set()
	if dex_nums is None: dex_nums = rom.find_all_glitchmon_dex_nums()
	for mon in dex_nums:
		bank, addr = rom.get_dex_mon_base_stats_ptr(mon)
		start_moves = rom.read_bytes(bank, addr + 15, 4)
		for n in start_moves:
			if n == 0 or n > 165: ids.add(n)

	for mon in g1const.glitchmon_species_ids:
		for n in rom.get_mon_learnset(mon):
			if n == 0 or n > 165: ids.add(n)

	return bytearray(sorted(ids))

def find_all_used_glitch_types(rom: Memory, dex_nums=None, moves=g1const.glitch_move_ids) -> bytearray:
	"""Return a list of all glitch type IDs used by glitchmons and glitch moves."""
	ids = set()
	if dex_nums is None: dex_nums = rom.find_all_glitchmon_dex_nums()
	for mon in dex_nums:
		bank, addr = rom.get_dex_mon_base_stats_ptr(mon)
		type1, type2 = rom.read_bytes(bank, addr + 6, 2)
		if type1 > 26: ids.add(type1)
		if type2 > 26: ids.add(type2)

	for move in moves:
		type = rom.read8(bank, addr + (((move - 1) & 0xFF) * 6) + 3)
		if type > 26: ids.add(type)

	return bytearray(sorted(ids))

def find_all_used_glitch_exp_groups(rom: Memory, dex_nums=None) -> bytearray:
	"""Return a list of all glitch experience group IDs used by glitchmons."""
	ids = set()
	if dex_nums is None: dex_nums = rom.find_all_glitchmon_dex_nums()
	for mon in dex_nums:
		bank, addr = rom.get_dex_mon_base_stats_ptr(mon)
		n = rom.read8(bank, addr + 19) & 0x3F
		if n > 5: ids.add(n)
	return bytearray(sorted(ids))

def find_all_used_glitchmon_palette_ids(rom: Memory, dex_nums=None) -> bytearray:
	"""Return a list of all glitch palette IDs used by glitchmons."""
	ids    = set()
	glitch = 0x28 if rom.is_yellow else 0x24 # first glitch ID
	if dex_nums is None: dex_nums = rom.find_all_glitchmon_dex_nums()
	for mon in dex_nums:
		n = rom.get_dex_mon_palette_id(mon)
		if n >= glitch: ids.add(n)
	return bytearray(sorted(ids))

def find_all_used_glitch_tilesets(rom: Memory, maps=None) -> bytearray:
	"""Return a list of all glitch tileset IDs used by glitch maps."""
	ids    = set()
	glitch = 0x19 if rom.is_yellow else 0x18 # first glitch ID
	if maps is None:
		maps = []
		maps.extend(g1const.dummy_map_ids)
		maps.extend(g1const.glitch_map_ids(rom.is_yellow))
	for map in maps:
		n = rom.read8(*rom.get_map_header_ptr(map), default=None)
		if n and n >= glitch: ids.add(n)
	return bytearray(sorted(ids))
	

#== Searches ===============================================================================================

def can_dex_mon_learn_move(rom: Memory, mon: int, move: int) -> bool:
	bank, addr = rom.get_dex_mon_base_stats_ptr(mon)

	for n in rom.read_bytes(bank, addr + 15, 4):
		if n == move: return True

	if move < 165:
		m = g1const.move_machine(move)
		if m is not None:
			if (rom.read8(bank, addr + 20 + (m >> 3)) >> (m & 7)) & 1 != 0:
				return True

	return False

def can_mon_learn_move(rom: Memory, mon: int, move: int) -> bool:
	dex = rom.get_mon_dex_num(mon)
	if rom.can_dex_mon_learn_move(dex, move): return True

	try:
		s = rom.stream(*rom.get_mon_learnset_ptr(mon))
		for level in s:
			if level == 0: break
			if next(s) == move: return True
	except AddressError:
		pass

	return False

def find_all_move_learners(rom: Memory, n: int, mons=range(256)) -> bytearray:
	"""Return a list of the IDs of all mons that learn move `n`."""
	ids = set()
	for mon in mons:
		if can_mon_learn_move(rom, mon, n): ids.add(mon)
	return bytearray(sorted(ids))