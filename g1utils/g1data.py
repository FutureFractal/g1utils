# g1data.py

import g1constants
from gbutils import AddressError, read16

from .g1text import *

if "xrange" in globals(): range = xrange # py2 compat


class Object: pass


### BCD

def bcd_to_int(bcd):
	val = 0
	for b in bcd:
		# TODO: is this accurate for glitch (>9) digits?
		val = val*100 + (b & 0xF) + (b >> 4)*10
	return val

def bcd_to_hex_string(bcd):
	return ''.join([("%.2X" % i) for i in bcd])


### Glitch IDs

def get_all_glitchmon_dex_nums(rom, hybrids=False):
	ids = {0} # Missingno. is always #000
	bank, addr = rom.get_location("dex_nums")
	for n in rom.read_bytes(bank, addr + 190, 66):
		if n > 151 or hybrids: ids.add(n)
	return sorted(ids)

def get_all_learnable_glitch_moves(rom, dex_nums=None):
	ids = set()
	
	if dex_nums is None: dex_nums = get_glitchmon_dex_nums(rom)
	for mon in dex_nums:
		bank, addr = get_base_stats_ptr(rom, mon)
		start_moves = rom.read_bytes(bank, addr + 15, 4)
		for n in start_moves:
			if n == 0 or n > 165: ids.add(n)

	for mon in glitchmon_species_ids:
		for n in get_learnset(rom, mon):
			if n == 0 or n > 165: ids.add(n)
	
	return sorted(ids)

def get_all_used_glitch_types(rom, dex_nums=None, moves=g1constants.glitch_move_ids):
	ids = set()
	
	if dex_nums is None: dex_nums = get_glitchmon_dex_nums(rom)
	for mon in dex_nums:
		bank, addr = get_base_stats_ptr(rom, mon)
		type1, type2 = rom.read_bytes(bank, addr + 6, 2)
		if type1 > 26: ids.add(type1)
		if type2 > 26: ids.add(type2)

	for move in moves:
		type = rom.read8(bank, addr + (((n - 1) & 0xFF) * 6) + 3)
		if type > 26: ids.add(type)

	return sorted(ids)

def get_all_used_glitch_exp_groups(rom, dex_nums=None):
	ids = set()
	if dex_nums is None: dex_nums = get_glitchmon_dex_nums(rom)
	for mon in dex_nums:
		bank, addr = get_base_stats_ptr(rom, mon)
		n = rom.read8(bank, addr + 19) & 0x3F
		if n > 5: ids.add(n)
	return sorted(ids)


### Mons

def get_mon_dex_num(rom, n):
	bank, addr = rom.get_location("dex_nums")
	return rom.read8(bank, addr + ((n - 1) & 0xFF))

def get_dex_mon_base_stats_ptr(rom, n):
	if n == 151 and not rom.is_yellow:
		return rom.get_location("base_stats_mew")
	else:
		bank, addr = rom.get_location("base_stats")
		return bank, addr + ((n - 1) & 0xFF) * 28

def get_dex_mon_base_stats(rom, n):
	info = Object()
	bank, addr = get_dex_mon_base_stats_ptr(rom, n)
	data = rom.read_bytes(bank, addr, 28)
	info.stats         = data[1:6]
	type               = data[6:8]
	if type[0] == type[1]: type = type[0:]
	info.type          = type
	info.catch_rate    = data[8]
	info.exp_yield     = data[9]
	info.start_moves   = data[15:19]
	info.exp_group     = data[19]
	info.machine_moves = data[20:]
	return info
def get_mon_base_stats(rom, n):
	return get_dex_mon_base_stats(rom, get_mon_dex_num(rom, n))

def get_mon_learn_evo_ptr(rom, n):
	return rom.table_read_addr("learnsets_evos", (n - 1) & 0xFF)

def get_mon_learnset(rom, n):
	moves = {}
	bank, addr = get_mon_learn_evo_ptr(rom, n)
	try:
		b = rom.read8(bank, addr)
		while b != 0: # skip over evolutions the same way the game does
			addr += 1
			b = rom.read8(bank, addr)
		addr += 1
		lv = rom.read8(bank, addr)
		while lv != 0: # iterate over learnset
			mv = rom.read8(bank, addr+1)
			if lv not in moves: moves[lv] = mv
			addr += 2
			lv = rom.read8(bank, addr)
	except AddressError:
		pass
	return moves

def get_mon_evolutions(rom, n):
	level_evos, item_evos, trade_evos = {}, {}, {}
	if n == 0xFF: # index-FF glitchmons are always unable to evolve
		return level_evos, item_evos, trade_evos
	bank, addr = get_mon_learn_evo_ptr(rom, n)
	try:
		t = rom.read8(bank, addr)
		while t == 3:    # EV_TRADE
			# trade evolutions only work if they are first in the list
			level = rom.read8(bank, addr+1)
			if level not in trade_evos:
				trade_evos[level] = rom.read8(bank, addr+2)
			addr += 3
			t = rom.read8(bank, addr)
		while t != 0:
			if   t == 1: # EV_LEVEL
				level = rom.read8(bank, addr+1)
				if level not in level_evos:
					level_evos[level] = rom.read8(bank, addr+2)
				addr += 3
			elif t == 2: # EV_ITEM
				item = rom.read8(bank, addr+1)
				if item not in item_evos:
					item_evos[item] = rom.read8(bank, addr+3)
				addr += 4
			else:        # EV_TRADE, all glitch evos (non-functional)
				addr += 3
			t = rom.read8(bank, addr)
	except AddressError:
		pass
	return level_evos, item_evos, trade_evos

def get_mon_dex_entry(rom, n, vchar="dex", **opt):
	species, height, weight, desc = None, None, None, None
	bank, addr = rom.get_location("dex_entries")
	addr = rom.read16(bank, addr + ((n - 1) & 0xFF) * 2)
	try:
		species, addr = get_string_and_end(rom, bank, addr, vchar=vchar, **opt)
		
		# certain end-of-string control chars will clobber the register the dex code reads
		# to find the end of the species string after printing it.
		c = rom.read8(bank, addr - 1)
		if   c == 0x00:
			addr = rom.get_location("char00_script")
		elif c == 0x57 or c == 0x58:
			addr = rom.get_location("char57_script")
	
		if rom.lang == "E":
			# u8 feet, u8 inches, u16 pounds/10
			height = rom.read_bytes(bank, addr, 2)
			weight = rom.read16(bank, addr + 2)
			addr += 4
		else:
			# u8 decimeters, u16 hectograms
			height = rom.read8(bank, addr)
			weight = rom.read16(bank, addr + 1)
			addr += 3

		if rom.is_japan: desc = get_string(rom, bank, addr, vchar=vchar, **opt)
		else:            desc = (bank, addr)
	
	except AddressError:
		pass
	info = Object()
	info.species = species
	info.height  = height
	info.weight  = weight
	info.desc    = desc
	return info

def _gcd(a, b):
	while b: a, b = b, a%b
	return a
def get_exp_group_coefficients(rom, n):
	# formula is a polynomial with the form (a/b)x^3 + cx^2 + dx - e
	ab, c, d, e = rom.table_read_bytes("exp_formulas", 4, n & 0x3F)
	a, b = ab >> 4, ab & 0xF
	if b == 0: return (0, 0, 0, 0, 0)
	f = _gcd(a, b) # reduce the fraction
	return (a//f, b//f, (c & 0x7F) * (1 - 2*(c >> 7)), d, -e)

def exp_group_formula_repr(coefficients):
	a, b, c, d, e = coefficients
	if b == 0:
		return "x / 0"
	s = []
	if a:
		if   b != 1: s.append("(%d/%d)" % (a,b))
		elif a != 1: s.append(str(a))
		s.append("x^3")
		next = True
	if c:
		if s:
			s.append(" - " if c < 0 else " + ")
			s.append(str(abs(c)))
		else:
			s.append(str(c))
		s.append("x^2")
	if d:
		if s: s.append(" + ")
		s.append("%dx" % d)
	if e:
		if s: s.append(" - %d" % -e)
		else: s.append(str(e))
	return ''.join(s)
def get_exp_group_formula(rom, n):
	return exp_group_formula_repr(get_exp_group_coefficients(rom, n))


### Moves

def get_move_info(rom, n):
	info = Object()
	data = rom.table_read_bytes("moves", 6, (n - 1) & 0xFF)
	info.animation = data[0]
	info.effect    = data[1]
	info.power     = data[2]
	info.type      = data[3]
	info.accuracy  = data[4]
	info.pp        = data[5]

def get_move_effect_ptr(rom, n):
	assert 0,"TODO: find move effect table locations"
	return rom.table_read_addr("move_effects", (n - 1) & 0xFF)


### Items

def get_item_price(rom, n):
	if n < 201:
		return bcd_to_int(rom.table_read_bytes("item_prices", 3, (n - 1) & 0xFF))
	else:
		return rom.table_read4("tm_prices", n - 201) * 1000

def is_key_item(rom, n):
	if n < 196:
		# The game copies 15 bytes from the key item bitfield into a RAM buffer before examining it.
		# Therefore, only the first 120 bits come from ROM, and the remaining 76 bits come from
		# whatever was last in the RAM buffer.
		i = n >> 3
		if i < 15:
			return bool((rom.table_read8("key_items", i) >> (n & 7)) & 1)
		else:
			# NOTE: reading from RAM
			return None
	else:
		# HMs are key items, TMs are not
		return (n < 201)

def get_item_effect(rom, n):
	assert 0,"TODO: find item effect table locations"
	return rom.table_read_addr("item_effects", n & 0x7F)


### Trainers

def get_trainer_base_prize_money(rom, n):
	bank, addr = rom.get_location("trainer_gfx_pay")
	return rom.read_bytes(bank, addr + n*5 + 2, 2) # third BCD byte goes unused

def get_trainer_team(rom, trainer, team):
	bank, addr = rom.table_read_addr("trainer_teams", (trainer - 1) & 0xFF)

	# Teams are null-terminated and stored sequentially.
	# Skip all the teams before the one we're looking for.
	for i in range(team):
		while rom.read8(bank, addr) != 0:
			addr += 1
		addr += 1

	# If the team's level is FF, each member's level is specified individually.
	# Otherwise, every member has the team's level.
	level = rom.read8(bank, addr)
	team  = []
	addr += 1
	if lvl == 0xFF:
		level = rom.read8(bank, addr)
		while level != 0:
			mon = rom.read8(bank, addr + 1)
			team.append((mon, level))
			addr += 2
			level = rom.read8(bank, addr)
		return None, team
	else:
		mon = rom.read8(bank, addr)
		while mon != 0:
			team.append(mon)
			addr += 1
			mon = rom.read8(bank, addr)
		return level, team

def get_trainer_ai_info(rom, n):
	assert 0,"TODO: find trainer AI table locations"
	info = rom.table_read_bytes("trainer_ai", 3, n)
	return n[0], read16(n,1)


### Tilesets

def _get_tileset_bank(rom, n):
	bank, addr = rom.get_location("tilesets")
	return rom.read8(bank, addr + n*12)

_tilesets_num_blocks = (
	0x80, # 00
	0x13, # 01
	0x25, # 02
	0x80, # 03
	0x13, # 04
	0x74, # 05
	0x25, # 06
	0x74, # 07
	0x23, # 08
	0x80, # 09
	0x80, # 0A
	0x11, # 0B
	0x80, # 0C
	0x3E, # 0D
	0x17, # 0E
	0x6E, # 0F
	0x3A, # 10
	0x80, # 11
	0x4F, # 12
	0x48, # 13
	0x3A, # 14
	0x24, # 15
	0x80, # 16
	0x4B, # 17
	
	# Yellow only
	0x14, # 18
)
def get_tileset_blocks_len(n, yellow=False):
	if n <= (0x18 if yellow else 0x17): return _tilesets_num_blocks[n]

def get_tileset_blocks_ptr(rom, n):
	bank, addr = rom.get_location("tilesets")
	addr += n*12
	return rom.read8(bank, addr), rom.read16(bank, addr + 1)

def get_tileset_blocks(rom, n, glitch=False):
	bank, addr = get_tileset_blocks_ptr(rom, n)
	nblocks = get_tileset_blocks_len(n, rom.is_yellow) if not glitch else 256
	blocks = rom.read_bytes(bank, addr, nblocks*16, allow_partial=True)
	if len(blocks) < nblocks*16:
		assert 0,"TODO"
	return blocks

def get_tileset_attributes(rom, n, glitch=False):
	bank, addr = rom.get_location("tilesets")
	addr += n*12
	data = rom.read_bytes(bank, addr + 5, 7)
	
	# Collision data (list of tile IDs that can be walked on)
	# TODO: all nonglitch collision data is in ROM0, but which bank is mapped when collision data is read?
	addr, walkable = read16(data, 0), []
	b = rom.read8(None, addr)
	while b != 0xFF:
		walkable.append(b)
		addr += 1
		b = rom.read8(None, addr)
	
	counters = data[2:5] # Counter tile IDs (list of tile IDs the player can talk to NPCs across)
	grass    = data[5]   # Tall grass tile ID (self-explanatory)
	type     = data[6]   # Tileset type (outdoors, indoors, or dungeon)

	return type, walkable, counters, grass


### Maps

# lookup table for map connections bitfield
_bitcount = ( 0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4 )

def get_map_header_ptr(rom, n):
	return rom.table_read8("map_banks", n), rom.table_read_addr("map_headers", n)[1]

def get_map_info(rom, n):
	bank, addr = get_map_header_ptr(rom, n)
	data = rom.read_bytes(bank, addr, 5)
	info = Object()
	info.id          = n
	info.bank        = bank
	info.width       = data[2]
	info.height      = data[1]
	info.tileset     = data[0]
	info.block_addr  = read16(data, 3)
	info.block_step  = info.width
	cskip = _bitcount[rom.read8(bank, addr+9) & 0xF]*11 # map connections size
	info.obj_addr    = rom.read16(bank, addr + 10 + cskip)
	info.header_addr = addr + 10
	info.glitch      = False
	return info

def get_map_objects_ptr(rom, n):
	bank, addr = get_map_header_ptr(rom, n)
	cskip = _bitcount[rom.read8(bank, addr+9) & 0xF]*11 # map connections size
	return bank, rom.read16(bank, addr + 10 + cskip)

def get_mapobj_objects(rom, bank, addr):
	addr += 1 # skip border block
	
	num, warps = rom.read8(bank, addr), []
	addr += 1
	for i in range(num):
		x, y, dest, map = rom.read_bytes(bank, addr, 4)
		warps.append((x, y, map, dest))
		addr += 4
	
	num, signs = rom.read8(bank, addr), []
	addr += 1
	for i in range(num):
		signs.append(rom.read_bytes(bank, addr, 3))
		addr += 3
	
	actors, warpdests_addr = _get_mapobj_actors(rom, bank, addr)

	return actors, signs, warps, warpdests_addr

def get_mapobj_actors_ptr(rom, bank, addr):
	# skip border block and warps:
	addr += 2 + rom.read8(bank, addr+1)*4
	# skip signposts:
	addr += 1 + rom.read8(bank, addr)*3
	return bank, addr

def get_mapobj_actors(rom, bank, addr):
	num, sprites = rom.read8(bank, addr), []
	addr += 1
	for i in range(num):
		sprite, x, y, move, dir, text = rom.read_bytes(bank, addr, 6)
		if   text & 0x40 != 0:
			# Trainers and stationary wild encounters
			id, arg = rom.read_bytes(bank, addr + 6, 2)
			sprites.append((x, y, sprite, move, dir, text, id, arg))
			addr += 8
		elif text & 0x80 != 0:
			# Items
			item = rom.read8(bank, addr + 6)
			sprites.append((x, y, sprite, move, dir, text, item))
			addr += 7
		else:
			# All other actors
			sprites.append((x, y, sprite, move, dir, text))
			addr += 6
	return sprites, addr

def get_mapobj_warpdests_ptr(rom, bank, addr):
	# skip border block and warps:
	addr += 2 + rom.read8(bank, addr+1)*4
	# skip signposts:
	addr += 1 + rom.read8(bank, addr)*3
	# skip sprites:
	nobj = rom.read8(bank, addr)
	addr += 1
	for i in range(nobj):
		# object struct is variable-length so we can't just trivially jump past the whole list
		t = rom.read8(bank, addr+5)
		if   t & 0x40 != 0: addr += 8
		elif t & 0x80 != 0: addr += 7
		else:               addr += 6
	return bank, addr
def get_mapobj_warpdest(rom, bank, addr, warp):
	bank, addr = get_mapobj_warpdests_ptr(rom, bank, addr)
	data = rom.read_bytes(bank, addr + warp*4, 4)
	return read16(data,0), data[3], data[2]

def get_dungeon_warpdest(rom, map, warp):
	bank, addr = rom.get_location("dungeon_warp_ids")
	i = 0
	m, w = rom.read_bytes(bank, addr, 2)
	while m != map or w != warp:
		i = (i + 6) & 0xFF
		addr += 2
		m, w = rom.read_bytes(bank, addr, 2)
	bank, addr = rom.get_location("dungeon_warps")
	info = rom.read_bytes(bank, addr + i, 6)
	return read16(info,0), info[3]*2 + info[5], info[2]*2 + info[4]

def get_fly_warpdest(rom, n):
	bank, addr = rom.get_location("fly_warps")
	b = rom.read8(bank, addr)
	while b != n:
		addr += 4
		b = rom.read8(bank, addr)
	addr = rom.read16(bank, addr + 2)
	info = rom.read_bytes(bank, addr, 6)
	return read16(info,0), info[3]*2 + info[5], info[2]*2 + info[4]

def get_glitch_map_info(rom, map, blockaddr, x, y, unbound=False):
	if type(map) is int: map = get_map_info(rom, map)
	info = map
	
	width, height = info.width, info.height
	blockstep     = width + 6
	addr_offset   = 0
	if unbound:
		width, height = 128, 128
	else:
		w2, h2 = width*2, height*2
		if x > w2:
			addr_offset += width
			width = 128 - width
		elif x == w2:
			width = 128
		if y > h2:
			addr_offset += height * blockstep
			height = 128 - height
		elif y == h2:
			height = 128

	# cut out the outermost border of blocks because those are never visible
	blockaddr += blockstep + 1
	width     -= 2
	height    -= 2

	# Due to how the game's overworld logic is written, the current ROM bank whenever
	# the tilemap is accessed is the bank containing the current tileset's gfx and blocks.
	info.bank = _get_tileset_bank(rom, info.tileset)

	# Find the top-left corner of the map given the block pointer for x,y
	info.block_addr = blockaddr + addr_offset - (1 + blockstep + blockstep*(y>>1) + (x>>1))

	info.glitch     = True
	info.width      = width + 6
	info.height     = height + 6
	info.block_step = blockstep
	info.entry_x    = x
	info.entry_y    = y
	return info

def get_glitch_city_info(rom, map, warp):
	info = get_map_info(rom, map)
	return get_glitch_map_info(rom, info, *get_mapobj_warpdest(rom, info.bank, info.obj_addr, warp))
