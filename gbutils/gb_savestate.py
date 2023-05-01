# gb_savestate.py

from .gb_memory import Memory, _decode_title


def _read16l(b, i):
	return (b[i]
	     | (b[i+1] << 8))
def _read32l(b, i):
	return (b[i]
	     | (b[i+1] << 8)
	     | (b[i+2] << 16)
	     | (b[i+3] << 24))

def _read_cstr(b, i):
	return b[i:b.find(0, i)]

class _stream:
	def __init__(self, data, offset=0):
		self.buf = data
		self.off = offset
		self.len = len(data)
	def __iter__(self):
		return self

	def seek(self, offset):
		self.off = offset
	def skip(self, nbytes):
		self.off += nbytes

	def u8(self):
		b, i = self.buf, self.off; self.off = i + 1
		return b[i]
	__next__ = u8

	def lu16(self):
		b, i = self.buf, self.off; self.off = i + 2
		return _read16l(b, i)
	def lu32(self):
		b, i = self.buf, self.off; self.off = i + 4
		return _read32l(b, i)

	def bytes(self, nbytes):
		b, i = self.buf, self.off; self.off = i + nbytes
		return b[i:i+nbytes]

	def cstr(self):
		b, i = self.buf, self.off
		end  = b.find(0, i)
		self.off = end + 1
		return b[i:end]


_ERR_NOT_SAVESTATE = "Not a savestate"
_ERR_CORRUPT       = "Savestate is corrupt or invalid"

def _ERR_FORMAT_VERSION_TOO_NEW(ver, maxver):
	return f"" # ...


#== mGBA ===================================================================================================
# (Source code: https://github.com/mgba-emu/mgba/)

_MGBA_SAVESTATE_MAX_VERSION = 3

def _extract_mgba_png_savestate(pngdata):
	import png, zlib
	data   = None
	sram   = None
	reader = png.Reader(bytes=pngdata)
	for chunktype, chunk in reader.chunks():
		if   chunktype == b"gbAs":
			data = chunk

		elif chunktype == b"gbAx":
			if _read32l(chunk, 0) == 2: # EXTDATA_SAVEDATA
				sram = zlib.decompress(chunk[8:])
				assert len(sram) == _read32l(chunk, 4)

	if data is None:
		raise Exception(_ERR_NOT_SAVESTATE)
	return data, sram

def load_mgba_savestate(data: bytes) -> Memory:
	"""Load an mGBA savestate."""
	import zlib

	# mGBA savestate files can optionally be PNG files
	# with the savestate and related metadata stored in special PNG chunks.
	is_png = data[:4] == b"\x89PNG"
	if is_png:
		data, sram = _extract_mgba_png_savestate(data)
	
	data = zlib.decompress(data)
	size = len(data)
	if size < 8:
		raise Exception(_ERR_NOT_SAVESTATE)
	magic_ver = _read32l(data, 0)
	if magic_ver < 0x00400000: # magic number
		raise Exception(_ERR_NOT_SAVESTATE)
	if magic_ver > 0x00400000 + _MGBA_SAVESTATE_MAX_VERSION:
		pass # ...

	if size < 0x11800:
		raise Exception(_ERR_CORRUPT)

	if not is_png:
		offset = 0x11800
		while offset < size:
			extsize = _read32l(data, offset + 4)
			offset += 8
			if _read32l(data, offset) == 2: # EXTDATA_SAVEDATA
				sram = data[offset:offset+extsize]
				break
			offset += extsize	

	high = bytearray(0x200)
	high[0x000:0x0A0] = data[0x260:0x300] # OAM
	high[0x100:0x1FF] = data[0x300:0x400] # HRAM

	return Memory(
		title = data[0x0010:0x0020],
		vram  = data[0x0400:0x4400],
		sram  = sram,
		wram  = data[0x4400:0xC400],
		high  = high
	)


#===========================================================================================================

_savestate_types = {
	"mgba": load_mgba_savestate
}
def open_savestate(path: str, type: str, **opt) -> Memory:
	load = _savestate_types.get(type.lower())
	if load is None:
		raise Exception("Unknown savestate type: %s" % type)
	with open(path, "rb") as f:
		return load(f.read(), **opt)
