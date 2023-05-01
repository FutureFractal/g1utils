# g1base.py
from __future__ import annotations

from typing import TypeVar, Sequence, Generator

import gbutils
from   gbutils import AddressError, unpack16, ptr

DEFAULT = gbutils.DEFAULT


class Info:
	def __init__(self, **props):
		self.__dict__ = props
	def __getattr__(self, _):
		return None # nonexistent attrs return None
	def __repr__(self):
		return repr(self.__dict__)
	__str__ = __repr__
	
	def update(self, **props):
		self.__dict__.update(props)


#== Misc. ====================================================================================================

def trim_mon_moves(moves: bytes) -> tuple:
	for i in (3,2,1,0):
		if moves[i] != 0: break
	return tuple(moves[:i+1])


#== BCD ======================================================================================================

def bcd_to_int(bcd: bytes) -> int:
	val = 0
	for b in bcd:
		# TODO: is this accurate for glitch (>9) digits?
		val = val*100 + (b & 0xF) + (b >> 4)*10
	return val

def bcd_to_hex(bcd: bytes) -> str:
	return ''.join(f"{i:02X}" for i in bcd)

def bcd_to_text(bcd: bytes) -> str:
	pass # ...


#== Memory =====================================================================================================

def open_rom(path: str, version:str=None) -> Memory:
	"""
	Open a Gen 1 Pokémon ROM file.
	"""
	with open(path, "rb") as f:
		return Memory(rom=f.read(), version=version)

def open_sav(path: str, version: str) -> Memory:
	"""
	Open a Gen 1 Pokémon SAV file.
	"""
	with open(path, "rb") as f:
		return Memory(sram=f.read(), version=version)

def open_savestate(path: str, type: str, version: str) -> Memory:
	"""
	Open a Gen 1 Pokémon emulator savestate file.
	"""
	return Memory(gbutils.open_savestate(path, type), version=version)

# Unfortunately for (most) Gen 1 ROMs, the ROM title alone is not enough to determine the exact version.
# The only Gen 1 ROMs with a four-character code are the French/Italian/German/Spanish Yellow versions.
# Thankfully, every Gen 1 ROM has a unique global checksum we can look up in a table.
_version_checksums = {
	0xA2C1: "JRv0",
	0xDDD5: "JGv0",
	0xB866: "JRv1",
	0xF547: "JGv1",
	0xDC36: "JB",
	0x91E6: "ER",
	0x9D0A: "EB",
	0x7AFC: "FR",
	0x56A4: "FB",
	0x89D2: "IR",
	0x5E9C: "IB",
	0x5CDC: "GR",
	0x2EBC: "GB",
	0x384A: "SR",
	0x14D7: "SB",
	0x9C29: "JYv0",
	0x8858: "JYv1",
	0xEDD9: "JYv2",
	0xD984: "JYv3",
	0x047C: "EY",
	0xB7C1: "FY",
	0x4E8F: "IY",
	0x66FB: "GY",
	0x5637: "SY",
}
_version_titles = {
	"R":  "POKEMON RED",
	"G":  "POKEMON GREEN",
	"B":  "POKEMON BLUE",
	"JY": "POKEMON YELLOW",
	"EY": "POKEMON YELLOW",
	"FY": "POKEMON YELAPSF",
	"IY": "POKEMON YELAPSI",
	"GY": "POKEMON YELAPSD",
	"SY": "POKEMON YELAPSS"
}
def _check_version_title(version, title):
	version = version[:2] if version[1] == "Y" else version[1]
	return title == _version_titles.get(version)

class Memory(gbutils.Memory):
	"""
	A Gen 1 Pokémon memory image.
	"""
	def __init__(
		self, *args,
		version   = None,
		locations = None,
		**kargs
	):
		super(Memory, self).__init__(*args, **kargs)

		from . import g1locations
	
		if version is None:
			if self.has_rom:
				title, checksum = self.title, self.checksum
				version = _version_checksums.get(checksum)
				if version is None or not _check_version_title(version, title):
					raise Exception(f"Unsupported ROM (cart ID: {title}, checksum: 0x{checksum:04X}")
			else:
				raise Exception("RAM-only images must specify a version")
		self.version = version
		
		if locations is None:
			locations = (
				g1locations.rom_locations[version],
				g1locations.ram_locations[version]
			)
		self._locations = locations

	def _name(self):
		return self.version
	
	def location(self, name: str) -> any:
		"""
		Returns a named location in this memory image.
		
		@param name: The name of the location.
		@raise KeyError: if the named location is not found.
		"""
		for locations in self._locations:
			location = locations.get(name)
			if location: return location
		raise KeyError(name)
		
	def location_ptr(self, name):
		val = self.location(name)
		if type(val) is int: val = (None, val)
		return val

	@property
	def lang(self) -> str:
		"""
		A letter denoting the language of this ROM:
		  - `J`: Japanese
		  - `E`: English
		  - `F`: French
		  - `I`: Italian
		  - `G`: German
		  - `S`: Spanish
		"""
		return self.version[0]
	
	@property
	def is_yellow(self) -> bool:
		"""True if this is Pokémon Yellow."""
		return self.version[1] == "Y"
	@property
	def is_rg(self) -> bool:
		"""True if this is Japanese Pokémon Red or Pokémon Green."""
		return self.version[:2] in ("JR","JG")


	def table_read8(self, location, n, default=gbutils.DEFAULT):
		bank, addr = self.location_ptr(location)
		return self.read8(bank, addr + n, default=default)
	
	def table_read16(self, location, n, default=gbutils.DEFAULT):
		bank, addr = self.location_ptr(location)
		return self.read16(bank, addr + n*2, default=default)

	def table_read_bytes(self, location, itemsize, n):
		bank, addr = self.location_ptr(location)
		return self.read_bytes(bank, addr + n*itemsize, itemsize)
	
	def table_read4(self, location, n): # read packed nybble
		bank, addr = self.location_ptr(location)
		b = self.read8(bank, addr + (n >> 1))
		return (b >> ((~n & 1)*4)) & 0xF
	
	def table_read_addr(self, location, n, default=gbutils.DEFAULT):
		bank, addr = self.location_ptr(location)
		return bank, self.read16(bank, addr + n*2, default=default)

	def table_index_ptr(self, location, itemsize, n):
		bank, addr = self.location_ptr(location)
		return bank, addr + n*itemsize


	from .g1rom import (
		get_mon_name, get_mon_name_bytes,
		get_mon_dex_num,
		get_mon_info, get_dex_mon_info,
		get_mon_base_stats, get_mon_base_stats_ptr,
		get_dex_mon_base_stats, get_dex_mon_base_stats_ptr,
		get_mon_cry, get_mon_cry_sound,
		get_mon_party_sprite, get_dex_mon_party_sprite,
		get_mon_evolutions, get_mon_evolutions_ptr,
		get_mon_learnset, get_mon_learnset_ptr,
		get_mon_dex_entry, get_mon_dex_entry_ptr,
		get_move_name,
		get_move_info,
		get_move_effect_ptr,
		get_type_name, get_type_name_ptr,
		get_exp_group_coefficients,
		get_exp_group_formula,
		get_item_name,
		get_item_price,
		get_item_effect_ptr,
		get_trainer_class_name,
		get_trainer_encounter_name,
		get_trainer_class_prize_money,
		get_trainer_class_ai_info,
		get_trainer_team,
		get_tileset_num_blocks,
		get_tileset_header_ptr,
		get_tileset_block_ptr,
		get_tileset_block_data,
		get_tileset_tile_info,
		get_town_map_landmark, get_town_map_landmark_data,
		get_map_soundbank_and_music,
		get_map_info,
		get_map_header_ptr,
		get_map_drawable_info,
		get_map_objects_ptr,
		get_map_objptr_actors_addr,
		get_map_objptr_warpdests_addr,
		get_map_objects,
		get_map_sprite_ids,
		get_map_warpdest,
		get_dungeon_warpdest,
		get_fly_warpdest,
		get_displaced_map_info,
		get_glitch_city_info,
		get_map_wild_encounters, get_map_wild_encounter_ptr,
		find_all_glitchmon_dex_nums,
		find_all_unused_glitch_dex_nums,
		find_all_learnable_glitch_moves,
		find_all_used_glitch_types,
		find_all_used_glitch_exp_groups,
		find_all_used_glitchmon_palette_ids,
		find_all_move_learners,
		can_mon_learn_move, can_dex_mon_learn_move,
		find_all_move_learners
	)
	from .g1gfx import (
		get_palette, get_raw_palette,
		get_mon_palette, get_mon_palette_id,
		get_dex_mon_palette, get_dex_mon_palette_id,
		get_map_palette,
		get_sprite_info,
		get_map_spriteset,
		get_tileset_gfx, get_tileset_gfx_ptr,
		get_tileset_gfx_bitmap,
		get_tileset_block_bitmaps,
		get_map_bitmap,
		get_displaced_map_bitmap,
		get_glitch_city_bitmap,
		get_mon_sprite_bank,
		get_mon_frontsprite_ptr_dims, get_dex_mon_frontsprite_addr_dims,
		get_mon_backsprite_ptr, get_dex_mon_backsprite_addr,
		get_dex_mon_frontsprite_bitmap, get_dex_mon_backsprite_bitmap,
		get_mon_frontsprite_bitmap, get_mon_backsprite_bitmap,
		get_trainer_sprite_bitmap,
		get_trainer_sprite_ptr,
		get_compressed_bitmap
	)
	from .g1text import (
		get_packed_name,
		read_string,
		find_string_end,
		find_printed_string_end
	)
	from .g1script import (
		get_152_owned_dex_rating, get_152_owned_dex_rating_ptr,
		read_text_script,
		get_rom0_glitch_txtcmd_sounds,
		get_romx_glitch_txtcmd_sounds,
		find_next_sfx_addr
	)

	class Stream(gbutils.Memory.Stream):
		from .g1text import next_string


ROM = Memory # alias
