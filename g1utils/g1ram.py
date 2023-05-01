# g1ram.py
from __future__ import annotations

from .g1base import *
from .g1text import *
from .g1rom  import get_map_header_ptr

from gbutils import AddressError

def _var_read8(mem, name, off=0):
	return mem.read8(None, mem.location(name) + off)

def _unpack16b(data, i): # big endian
	return (data[i] << 8) | data[i+1]

# locations that are the same across all versions
_loc_hall_of_fame      = 0xA598 # bank 0
_loc_saved_player_name = 0xA598 # bank 1
_loc_saved_actors      = 0xAD2C # bank 1
_loc_saved_party       = 0xAF2C # bank 1
_loc_saved_cur_box     = 0xB0C0 # bank 1
_loc_saved_daycare_mon = 0xAD0B # bank 1
_loc_save_checksum     = 0xB523 # bank 1
_loc_actors            = 0xC100
_loc_map_buffer        = 0xC6E8


#== Names ==================================================================================================

def _get_name(ram: Memory, location):
	length = 5 if ram.is_japan else 10
	return ram.read_string(None, ram.location(location), length)

def get_cur_player_name(wram: Memory) -> str:
	return _get_name(wram, "cur_player_name")
def get_saved_player_name(sram: Memory) -> str:
	return _get_name(sram, "saved_player_name")


def get_cur_rival_name(ram: Memory) -> str:
	return _get_name(ram, "cur_rival_name")

def get_opponent_trainer_name(ram):
	return _get_name(ram, "trainer_name")
def get_link_trainer_name(ram):
	return _get_name(ram, "link_trainer_name")


#== Player info ============================================================================================

def get_player_id(ram: Memory):
	addr = ram.location("player_id")
	return ram.read8(None, addr) << 8 | ram.read8(None, addr + 1)

def get_player_money(ram):
	return bcd_to_int(ram.var_read_bytes("player_money", 3))


#== Mons ===================================================================================================

def _read_mon(data):
	# all values here are big endian for some reason
	
	type = tuple(data[5:7])
	if type[0] == type[1]: type = type[:1]
	
	# IV order: Attack, Defense, Speed, Special
	# HP IV, from highest to lowest bit, is the lowest bits of the other four IVs respectively
	i1, i2 = data[27], data[28] # IV bytes
	hp  = ((i1 & 0x10) >> 1) | ((i1 & 1) << 2) | ((i2 & 0x10) >> 3) | (i2 & 1)
	ivs = tuple((
		hp,
		i1 >> 4,  # Attack
		i1 & 0xF, # Defense
		i2 & 0xF, # Special
		i2 >> 4,  # Speed
	))
	
	return Info(
		species   = data[0],
		cur_hp    = _unpack16b(data, 1),
		level     = data[3],
		status    = data[4],
		type      = type,
		moves     = trim_mon_moves(data[8:12]),
		ot_id     = _unpack16b(data, 12),
		exp       = (data[14] << 16) | (data[15] << 8) | data[16], # 24-bit int
		stat_exp  = tuple((_unpack16b(data, i) for i in range(17,27,2))),
		ivs       = ivs,
		
		# only meaningful when transferred to later gens
		g2_held_item = data[7],
		shiny        = ((i1 & 0x2F) == 0x2A) and (i2 == 0xAA)
	)

def _read_party_mon(mem, n, addr):
	data       = mem.read_bytes(None, addr, 44, n, sram_bank=1)
	info       = _read_mon(data)
	info.level = data[33]
	info.stats = tuple((_unpack16b(data, i) for i in range(36,44,2)))
	return info
def get_cur_party_mon_info(mem, n):
	return _read_party_mon(mem, n, mem.location("cur_party"))
def get_saved_party_mon_info(mem, n):
	return _read_party_mon(mem, n, _loc_saved_party)

def get_cur_daycare_mon_info(mem):
	return _read_mon(mem, mem.location("cur_daycare_mon"))
def get_saved_daycare_mon_info(mem):
	return _read_mon(mem, _loc_saved_daycare_mon)

def get_hall_of_fame_entry(sram, n):
	team = []
	data = sram.read_bytes(None, _loc_hall_of_fame + (n * 0x60), 96, sram_bank=0)
	for i in range(6):
		i *= 16
		species = data[i]
		if species == 0xFF: break
		team.append(Info(
			species = species,
			level   = data[i+1],
			name    = decode_string(sram.lang, data[i+2:i+13])
		))
	return tuple(team)


#== Inventory ==============================================================================================

def _get_inventory(ram, location):
	data = ram.stream(None, ram.location(location))
	return [(data.next8(), data.next8()) for i in range(data.next8())]

def get_bag_inventory(ram):
	return _get_inventory(ram, "bag_inventory")
def get_pc_inventory(ram):
	return _get_inventory(ram, "pc_inventory")


#== Overworld ==============================================================================================

def get_cur_map_id(ram):
	return _var_read8(ram, "cur_map_info", 3)

def get_cur_map_info(ram, unbound=False):
	addr = ram.location("cur_map_info")
	
	blockstep = ram.read8(addr  + 14) + 6
	
	blockaddr = ram.read16(addr + 4)
	x = ram.read8(addr + 7)
	y = ram.read8(addr + 6)
	
	if unbound:
		width, height = 128, 128
	else:
		w2 = ram.read8(addr + 458)
		h2 = ram.read8(addr + 457)
		width, height = w2>>1, h2>>1
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
	
	return Info(
		id              = ram.read8(addr  + 3),
		width           = width,
		height          = height,
		tileset         = ram.read8(addr  + 12),
		block_addr      = blockaddr,
		block_step      = ram.read8( ), # TODO
		textscript_addr = ram.read16(addr + 17),
	)

def get_overworld_text_script_ptr(mem, n):
	bank = mem.table_read8("map_banks", get_cur_map_id(mem))
	addr = mem.read16(None, mem.location("cur_map_info") + 5)
	return bank, addr

def get_overworld_actors(mem, all_slots=False):
	
	script_bank  = mem.table_read8("map_banks", _var_read8(mem, "cur_map"))
	scripts_addr = mem.read16(None, mem.location("cur_map_info") + 5)

	loc_actors2 = mem.location("actors2")

	num_actors = 16 if all_slots else _var_read8(mem, "num_actors")
	actors     = []
	for i in range(num_actors):
	
		addr1 = _loc_actors + (i+1)*16
		addr2 = loc_actors2 + i*2
		
		script     = mem.read8(None, addr2 + 1)
		script_ptr = None
		if scripts_addr is not None:
			script_addr = mem.try_read16(script_bank, scripts_addr + ((script - 1) & 0xFF) * 2)
			script_ptr  = (script_bank, script_addr)
	
		actor = Info(
			sprite        = mem.read8(None, addr1),
			x             = mem.read8(None, addr1 + 0x104),
			y             = mem.read8(None, addr1 + 0x105),
			movement_type = mem.read8(None, addr1 + 0x106),
			script_id     = script,
			script        = script_ptr
		)
		actors.append(actor)

	return tuple(actors)


#== Battle =================================================================================================

#def get_battle_text_ptrs(

