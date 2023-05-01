# gb_memory.py

from __future__ import annotations

DEFAULT = object()


# Types:
ptr = tuple[int, int]


class AddressError(Exception):
	"""Thrown when an address is read from that is not part of a memory image."""
	_DEFAULT_MSG = "Address not in memory image"
	def __init__(self, addr: int, msg:str=_DEFAULT_MSG):
		super(Exception, self).__init__()
		self.addr = addr
		self.msg  = msg
	def __str__(self):
		return f"{self.msg}: ${self.addr:04X}"

def _bank_error(addr):
	if addr < 0x8000: s = "ROM"
	else:             s = "SRAM"
	return AddressError(addr, f"{s} bank not specified for address")


def open_rom(path: str) -> Memory:
	"""Load a GameBoy ROM file."""
	with open(path, "rb") as f:
		return Memory(rom=f.read())
		
def open_sav(path: str) -> Memory:
	"""Load a GameBoy battery save file."""
	with open(path, "rb") as f:
		return Memory(sram=f.read())

def _decode_title(title: bytes):
	code = None
	if title[15] >= 0x80:
		# All GBC-compatible games repurpose the last title byte as a GBC flag.
		title = title[:15]
		# Newer GBC-compatible games also repurpose the four title bytes before that for the game's
		# four-character code. Unfortunately there doesn't really seem to be a reliable way to check 
		# if that code exists, though we can at least check for obvious cases.
		maybecode = title[:10]
		if maybecode.isalnum():
			code = maybecode.decode("ascii")
	return title.split(b"\0", 1)[0].decode("ascii"), code

_mbc_masks = {
	0x00: 0,      # 32KB
	0x01: 0x0003, # 64KB
	0x02: 0x0007, # 128KB
	0x03: 0x000F, # 256KB
	0x04: 0x001F, # 512KB
	0x05: 0x003F, # 1MB
	0x06: 0x007F, # 2MB
	0x07: 0x00FF, # 4KB
	0x08: 0x01FF  # 8KB
}
_sbc_masks = {
#	0x00: no SRAM
#	0x01: never used
	0x02: 0,    # 8KB
	0x03: 0x3,  # 32KB
	0x04: 0xF,  # 128KB
	0x05: 0x7,  # 64KB
}
class Memory(object):
	"""
	A GameBoy memory image.
	All accessors emulate the GameBoy's address bus and MBC.
	"""
	def __init__(
		self, *args,
		rom:   bytes = None,
		vram:  bytes = None,
		sram:  bytes = None,
		wram:  bytes = None,
		high:  bytes = None,
		title: str   = None,
		gbc:   bool  = False
	):
		for arg in args:
			if not isinstance(arg, Memory):
				raise TypeError(f"args must be Memory, not {type(arg).__name__}")
			if rom   is None: rom   = arg._rom
			if vram  is None: vram  = arg._vram
			if sram  is None: sram  = arg._sram
			if wram  is None: wram  = arg._wram
			if high  is None: high  = arg._high
			if title is None: title = arg._title
	
		if rom is not None:
			if title is None:
				title = rom[0x134:0x144]
			self._mbc_mask = _mbc_masks[rom[0x148]]

		code = None
		if title is not None:
			title, code = _decode_title(title)

		self._rom   = rom
		self._vram  = vram
		self._sram  = sram
		self._wram  = wram
		self._high  = high
		self._title = title
		self._code  = code
		self._gbc   = gbc
		
	def close(self):
		pass
	__exit__ = close
	
	def _name(self):
		return self.title
	def __repr__(self):
		cls = type(self); cls = f"{cls.__module__}.{cls.__name__}"
		if self.title: return f"<{cls}: {self._name()}>"
		else:          return f"<{cls}>"
	
	
#== ROM header properties ======================================================================================

	@property
	def title(self) -> str:
		"""The ROM title of this memory image."""
		return self._title
	@property
	def code(self) -> str:
		return self._code
	
	@property
	def is_sgb(self) -> bool:
		"""True if this ROM has SGB features."""
		return self._rom[0x146] == 3
	@property
	def is_gbc(self) -> bool:
		"""True if this ROM has GBC features."""
		return self._rom[0x143] & 0xBF == 0x80
	@property
	def is_gbc_only(self) -> bool:
		"""True if this ROM only runs on GBC."""
		return self._rom[0x143] == 0xC0
	
	@property
	def is_japan(self) -> bool:
		"""True if this is a Japanese ROM."""
		return self._rom[0x14A] == 0
	
	@property
	def revision(self) -> int:
		"""The revision number of this ROM."""
		return self._rom[0x14C]
	
	@property
	def licensee(self) -> int:
		rom = self._rom
		code = rom[0x14B]
		if code != 0x33: return code
		else: return rom[0x144:0x145].decode()

	@property
	def checksum(self) -> int:
		"""
		The global checksum of this ROM, computed by adding together
		every byte in the ROM (except these two checksum bytes.)
		"""
		rom = self._rom
		if rom is not None:
			return rom[0x14E]<<8 | rom[0x14F] # stored big endian for some reason

	def verify_checksum(self) -> bool:
		"""
		Check if this ROM's checksum is valid.
		"""
		rom    = self._rom
		c1, c2 = rom[0x14E], rom[0x14F]
		return ((sum(rom) - (c1 + c2)) & 0xFFFF) == (c1 << 8 | c2)
	
	@property
	def cart_type(self) -> int:
		"""
		Specifies which memory bank controller the cartridge uses,
		as well as any other external hardware present in the cartridge.
		"""
		return self._rom[0x147]
	@property
	def rom_type(self) -> int:
		"""Specifies the size of the ROM on the cartridge."""
		return self._rom[0x148]
	@property
	def sram_type(self) -> int:
		"""Specifies the size of the SRAM on the cartridge."""
		return self._rom[0x149]

	@property
	def rom_bank_mask(self) -> int:
		return self._mbc_mask
	@property
	def sram_bank_mask(self) -> int:
		return self._sbc_mask


#== Memory access ==============================================================================================

	_has_addr_switch = (
		"_rom",
		"_rom",
		"_rom",
		"_rom",
		"_vram",
		"_sram",
		"_wram",
		 None
	)
	def has_addr(self, addr: int) -> bool:
		"""True if this memory image contains the specified address."""
		name = self._has_addr_switch[addr >> 13]
		if name is not None:
			return getattr(self, name) is not None
		elif addr < 0xFE00:
			return self._wram is not None
		elif ((addr - 0xA0) & 0x1FF) > 0x60: # equiv: addr < 0xFEA0 or addr >= 0xFF00
			return self._high is not None
		else:
			return False

	@property
	def has_rom(self)  -> bool:
		return self._rom  is not None
	@property
	def has_vram(self) -> bool:
		return self._vram is not None
	@property
	def has_sram(self) -> bool:
		return self._sram is not None
	@property
	def has_wram(self) -> bool:
		return self._wram is not None
	@property
	def has_hram(self) -> bool:
		return self._high is not None
	
	
	def next_valid_addr(self, addr: int) -> int:
		raise Exception("not implemented yet") # TODO ...
	

	def _read8_rom0(self, addr, rom_bank, sram_bank):
		return self._rom[addr]

	def _read8_romx(self, addr, rom_bank, sram_bank):
		if rom_bank is None: raise _bank_error(addr)
		return self._rom[(addr & 0x3FFF) | ((rom_bank & self._mbc_mask) << 14)]

	def _read8_vram(self, addr, rom_bank, sram_bank):
		return self._vram[addr & 0x1FFF] # TODO: bank support

	def _read8_sram(self, addr, rom_bank, sram_bank):
		if sram_bank is None: raise _bank_error(addr)
		return self._sram[(addr & 0x1FFF) | (sram_bank << 13)] # TODO: MBC mask

	def _read8_wram0(self, addr, rom_bank, sram_bank):
		return self._wram[addr & 0x1FFF]
	_read8_wramx = _read8_wram0 # TODO

	def _read8_high(self, addr, rom_bank, sram_bank):
		if addr < 0xFE00:
			return self._wram[addr & 0x1FFF]
		elif ((addr - 0xA0) & 0x1FF) > 0x60: # equiv: addr < 0xFEA0 or addr >= 0xFF00
			return self._high[addr & 0x1FF]
		else:
			raise AddressError(addr) # FEA0-FF00 is always unusable

	_read8_switch = (
		_read8_rom0,  _read8_rom0,
		_read8_rom0,  _read8_rom0,
		_read8_romx,  _read8_romx,
		_read8_romx,  _read8_romx,
		_read8_vram,  _read8_vram,
		_read8_sram,  _read8_sram,
		_read8_wram0, _read8_wramx,
		_read8_wram0, _read8_high
	)
	def read8(self, rom_bank: int, addr: int, /, sram_bank:int=None, default=DEFAULT) -> int:
		"""
		Read a byte.
		
		@arg rom_bank:  The ROM bank to read from. Can be None.
		@arg addr:      The address to read from.
		@arg sram_bank: (Optional) The SRAM bank to read from.
		
		@raises AddressError: if the address is unmapped.
		"""
		try:
			return self._read8_switch[addr >> 12](self, addr, rom_bank, sram_bank)
		except TypeError:
			if default is not DEFAULT: return default
		raise AddressError(addr)


	def _read16_rom0(self, addr, rom_bank, sram_bank):
		rom = self._rom
		return rom[addr] | (rom[addr+1] << 8)

	def _read16_romx(self, addr, rom_bank, sram_bank):
		if rom_bank is None: raise _bank_error(addr)
		rom, offset = self._rom, (addr & 0x3FFF) | ((rom_bank & self._mbc_mask) << 14)
		return rom[offset] | (rom[offset+1] << 8)

	def _read16_vram(self, addr, rom_bank, sram_bank):
		vram, offset = self._vram, addr & 0x1FFF
		return vram[offset] | (vram[offset+1] << 8)

	def _read16_sram(self, addr, rom_bank, sram_bank):
		if sram_bank is None: raise _bank_error(addr)
		sram, offset = self._sram, (addr & 0x1FFF) | (sram_bank << 13)
		return sram[offset] | (sram[offset+1] << 8)

	def _read16_wram(self, addr, rom_bank, sram_bank):
		wram, offset = self._wram, addr & 0x1FFF
		return wram[offset] | (wram[offset+1] << 8)

	def _read16_high(self, addr, rom_bank, sram_bank):
		if addr < 0xFDFE:
			wram, offset = self._wram, addr & 0x1FFF
			return wram[offset] | (wram[offset+1] << 8)
		else:
			read8_high = self._read8_high
			l = read8_high(self,  addr,             None, None)
			h = read8_high(self, (addr+1) & 0xFFFF, None, None)
			return l | (h<<8)
	
	_read16_switch = (
		_read16_rom0,
		_read16_rom0,
		_read16_romx,
		_read16_romx,
		_read16_vram,
		_read16_sram,
		_read16_wram,
		_read16_high
	)
	def read16(self, rom_bank: int, addr: int, /, sram_bank:int=None, default=DEFAULT) -> int:
		"""
		Read a word (16 bits).
		
		:param rom_bank:  The ROM bank to read from. Can be None.
		:param addr:      The address to read from.
		:param sram_bank: (Optional) The SRAM bank to read from.
		
		:raises AddressError: if the address is unmapped.
		"""
		try:
			if addr & 0x1FFF != 0x1FFF:
				return self._read16_switch[addr >> 13](self, addr, rom_bank, sram_bank)
			else:
				read8_switch = self._read8_switch
				l = read8_switch[addr >> 12](self, addr, rom_bank, sram_bank)
				addr = (addr+1) & 0xFFFF
				h = read8_switch[addr >> 12](self, addr, rom_bank, sram_bank)
				return l | (h<<8)
		except TypeError:
			if default is not DEFAULT: return default
		raise AddressError(addr)


	def read_bytes(self, rom_bank: int, addr: int, length: int,
				/, sram_bank:int=None, allow_partial:bool=False) -> bytearray:
		"""
		Read a sequence of bytes.
		
		:param rom_bank:  The ROM bank to read from. Can be None.
		:param addr:      The address to start reading from.
		:param length:    The number of bytes to read.
		:param sram_bank: (Optional) The SRAM bank to read from.
		
		:param allow_partial: (Optional) If true and an unmapped address is reached,
			return the bytes that were read successfully instead of raising an error.
			
		:raises AddressError: if an unmapped address is reached and `allow_partial` is false.
		"""
		array, endaddr, offset = self._next_chunk(addr, rom_bank, sram_bank)
		if array is not None:
			chunklen = endaddr - addr
			if chunklen >= length:
				buf = array[offset:offset+length]
				if not isinstance(buf, bytearray): buf = bytearray(buf)
			else:
				buf = array[offset:offset+chunklen]
				if not isinstance(buf, bytearray): buf = bytearray(buf)
				self.copy_bytes(rom_bank, addr, buf, chunklen, length - chunklen, sram_bank, allow_partial)
			assert len(buf) == length
			return buf
		elif allow_partial:
			return bytearray()
		else:
			raise AddressError(addr)


	def copy_bytes(self, rom_bank: int, addr: int, dest: bytearray, dest_offset: int, length: int,
				/, sram_bank=None, allow_partial=False):
		"""
		Copy a a sequence of bytes into an array.
		
		:param addr:        The address to start reading from.
		:param dest:        The array to copy into.
		:param dest_offset: The offset in dest to start copying to.
		:param length:      The number of bytes to copy.
		:param rom_bank:    The ROM bank to read from.
		:param sram_bank:   (Optional) The SRAM bank to read from.
		
		:param allow_partial: (Optional) If true and an unmapped address is reached,
			copy the bytes that were read successfully instead of raising an error.
		
		:raises AddressError: if an unmapped address is reached and `allow_partial` is false.
		"""
		while length > 0:
			array, endaddr, offset = self._next_chunk(addr, rom_bank, sram_bank)
			if array is not None:
				chunklen = min(endaddr - addr, length)
				dest[dest_offset:dest_offset+chunklen] = array[offset:offset+chunklen]
				dest_offset += chunklen
				length      -= chunklen
				addr         = endaddr & 0xFFFF
			elif allow_partial:
				break
			else:
				raise AddressError(addr)
	
	def stream(self, rom_bank: int, addr: int, /, sram_bank:int=None, allow_partial:bool=False):
		"""
		Returns a `Memory.Stream` instance that iterates over the contents of memory.
		
		Arguments:
		- rom_bank:  The ROM bank to read from. Can be None.
		- addr:      The address to start from.
		- sram_bank: (Optional) The SRAM bank to read from.
		
		- allow_partial: (Optional) If true and the iterator reaches an unmapped address,
		  raise `StopIteration` instead of `AddressError`.
		"""
		return self.Stream(self, addr, rom_bank, sram_bank, allow_partial)
	
	byte_iter = stream # alias
	
	class Stream:
		"""
		An iterator that iterates over a memory image.
		"""
		def __init__(self, mem, addr, rom_bank, sram_bank, allow_partial):
			self.mem           = mem
			self.rom_bank      = rom_bank
			self.sram_bank     = sram_bank
			self.allow_partial = allow_partial
			self._i = self._next_chunk(addr, rom_bank, sram_bank, False)
		
		def __iter__(self):
			return self

		def _next_chunk(self, addr, rom_bank, sram_bank, error):
			array, endaddr, offset = self.mem._next_chunk(addr, rom_bank, sram_bank)
			if array is None:
				# Only raise an AddressError in the next* methods.
				# Constructor and seek() should never raise an AddressError.
				if error:
					if self.allow_partial: raise StopIteration
					elif offset is None:   raise _bank_error(addr)
					else:                  raise AddressError(addr)
				endaddr, offset = addr, 0
			self._a       = array
			self._endoff  = offset + (endaddr-addr)
			self._endaddr = endaddr & 0xFFFF
			return offset

		@property
		def addr(self):
			"""The current address."""
			return self._endaddr - (self._endoff - self._i)

		def seek(self, rom_bank: int, addr: int, sram_bank:int=None):
			"""Move to the address `addr`."""
			if rom_bank  is not None: self.rom_bank  = rom_bank
			if sram_bank is not None: self.sram_bank = sram_bank
			self._i = self._next_chunk(addr, rom_bank, sram_bank, False)
		
		def skip(self, length: int):
			"""Skip forward `length` bytes."""
			i = self._i + length
			if i >= self._endoff:
				i = self._next_chunk(self.addr + length, self.rom_bank, self.sram_bank, False)
			self._i = i

		def next8(self) -> int:
			"""Yield the next byte."""
			i = self._i
			if i & 0x1FF == 0 and i >= self._endoff:
				i = self._next_chunk(self._endaddr, self.rom_bank, self.sram_bank, True)
			b = self._a[i]
			self._i = i + 1
			return b
		__next__ = next8
	
		def next16(self) -> int:
			"""Yield the next word (16 bits)."""
			i = self._i
			if i & 0x1FE == 0 and i >= self._endoff:
				return self.next8() | (self.next8() << 8)
			a = self._a
			v = a[i] | (a[i+1] << 8)
			self._i = i + 2
			return v
	
		def next_bytes(self, length: int) -> bytearray:
			"""Yield an array of the next `length` bytes."""
			i, array = self._i, self._a
			end = i + length
			if end < self._endoff:
				self._i = end
				return array[i:end]
			else:
				addr      = self.addr
				rom_bank  = self.rom_bank
				sram_bank = self.sram_bank
				data = self.mem.read_bytes(rom_bank, addr, length,
										   sram_bank     = sram_bank,
										   allow_partial = self.allow_partial)
				self._next_chunk((addr + length) & 0xFFFF, rom_bank, sram_bank)
				return data

	def _next_chunk_rom0(self, addr, rom_bank, sram_bank):
		return self._rom, 0x4000, addr

	def _next_chunk_romx(self, addr, rom_bank, sram_bank):
		if rom_bank is None:
			return None, 0x8000, (0 if self._rom is None else None)
		return self._rom, 0x8000, (addr & 0x3FFF) | ((rom_bank & self._mbc_mask) << 14)

	def _next_chunk_vram(self, addr, rom_bank, sram_bank):
		# TODO: GBC VRAM banking
		return self._vram, 0xA000, addr & 0x1FFF

	def _next_chunk_sram(self, addr, rom_bank, sram_bank):
		if sram_bank is None:
			return None, 0xC000, (0 if self._sram is None else None)
		return self._sram, 0xC000, (addr & 0x1FFF) | (sram_bank << 13)

	def _next_chunk_wram0(self, addr, rom_bank, sram_bank):
		# TODO: GBC WRAM banking
		return self._wram, 0xE000, addr & 0x1FFF
	_next_chunk_wramx = _next_chunk_wram0
	
	def _next_chunk_echoram(self, addr, rom_bank, sram_bank):
		return self._wram, 0xFE00, addr & 0x1FFF

	def _next_chunk_high(self, addr, rom_bank, sram_bank):
		if   addr < 0xFE00: # echoram
			# TODO: GBC WRAM banking
			return self._wram, 0xFE00,  addr & 0x1FFF
		elif addr >= 0xFF00:
			return self._high, 0x10000, addr & 0x1FF
		elif addr < 0xFEA0:
			return self._high, 0xFEA0,  addr & 0x1FF
		else:
			return None,       0xFFE0,  0

	_next_chunk_switch = (
		_next_chunk_rom0,    _next_chunk_rom0,
		_next_chunk_rom0,    _next_chunk_rom0,
		_next_chunk_romx,    _next_chunk_romx,
		_next_chunk_romx,    _next_chunk_romx,
		_next_chunk_vram,    _next_chunk_vram,
		_next_chunk_sram,    _next_chunk_sram,
		_next_chunk_wram0,   _next_chunk_wramx,
		_next_chunk_echoram, _next_chunk_high
	)
	def _next_chunk(self, addr, /, rom_bank, sram_bank):
		return self._next_chunk_switch[addr >> 12](self, addr, rom_bank, sram_bank)


	# array operator overload
	# (not especially useful but it's kinda neat)
	def __getitem__(self, i):
		t = type(i)
		if   t is int:
			return self.read8(None, i)
		elif t is slice:
			start = i.start
			return self.read_bytes(None, start, i.stop-start)
		else:
			raise TypeError(f"index must be int or slice, not {type(i).__name__}")


	def get_vram_bg_gfx(self):
		vram = self._vram
		if vram is None: raise AddressError(0x9000)
		gfx = bytearray()
		gfx.extend(vram[0x1000:0x1800])
		gfx.extend(vram[0x0800:0x1000])
		return gfx

	def get_vram_obj_gfx(self):
		vram = self._vram
		if vram is None: raise AddressError(0x8000)
		return vram[0x0000:0x1000]


ROM = Memory # alias


def bytes_repr(bytes: bytes) -> str:
	return ' '.join(f"{b:02X}" for b in bytes)

def unpack16(a: bytes, index: int) -> int:
	return a[index] | (a[index + 1] << 8)

def is_rom_addr(addr: int)  -> bool:
	"""True if this address is mapped to ROM."""
	return (addr < 0x8000)
def is_rom0_addr(addr: int) -> bool:
	"""True if this address is mapped to bank 0 of ROM."""
	return (addr < 0x4000)
def is_romx_addr(addr: int) -> bool:
	"""True if this address is mapped to a switchable bank of ROM."""
	return (addr & 0xC000 == 0x4000)

# pointer/offset conversion functions:
def rom_bank_to_offset(bank: int) -> int:
	"""Convert a ROM bank to a ROM file offset."""
	return bank << 14
def rom_ptr_to_offset(bank: int, addr: int) -> int:
	"""Convert a ROM bank and memory address to a ROM file offset."""
	if   addr < 0x4000: return addr
	elif addr < 0x8000: return (bank << 14) | (addr & 0x3FFF)
def rom_offset_to_bank(offset: int) -> int:
	"""Determine the ROM bank of a ROM file offset."""
	return offset >> 14
def rom_offset_to_addr(offset: int) -> int:
	"""Convert a ROM file offset to a memory address."""
	if offset < 0x4000: return offset
	else:               return (offset & 0x3FFF) | 0x4000
def rom_offset_to_ptr(offset: int) -> int:
	"""Convert a ROM file offset to a ROM bank and memory address."""
	return ((offset >> 14), rom_offset_to_addr(offset))
