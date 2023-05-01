# g1gfx.py
from __future__ import annotations

from .g1base import *
from .g1rom  import *

import g1const


# type aliases:

Palette = tuple[bytes,bytes,bytes,bytes]
"""
An SGB/GBC palette.
"""

ImageGenerator = tuple[int, int, Generator[bytes, None, None], Palette]
"""
...
"""


#== Palettes ===============================================================================================

def get_raw_palette(rom: Memory, type: str, n: int) -> Palette:
	"""
	Return the raw 5-bit RGB data for palette `n`.
	"""
	if n is not None:
		pal, data = [], rom.table_read_bytes(type+"_palettes", 8, n)
		for i in range(0,8,2):
			rgb = unpack16(data,i)
			pal.append(bytes((rgb & 31, (rgb >> 5) & 31, (rgb >> 10) & 31)))
		return tuple(pal)

def get_palette(rom: Memory, type: str, n: int) -> Palette:
	"""
	Return palette `n` converted to an 8-bit RGB color.
	This is done by shifting the 5-bit components left by 3 and copying the highest 3 bits
	into the new lowest 3 bits.
	"""
	if n is not None:
		bank, addr = rom.location(type+"_palettes")
		data = rom.read_bytes(bank, addr + 8*n, 8)
		if type == "sgb":
			# SGB doesn't actually use the first color apparently?
			color = rom.read16(bank, addr + 8*0x1F, 8)
			data[0], data[1] = color & 0xFF, color >> 8
		pal = []
		for i in range(0,8,2):
			rgb = unpack16(data,i)
			r, g, b = rgb & 31, (rgb >> 5) & 31, (rgb >> 10) & 31
			pal.append(bytes((
				(r << 3) | (r >> 2),
				(g << 3) | (g >> 2),
				(b << 3) | (b >> 2)
			)))
		return tuple(pal)

def get_dex_mon_palette(rom: Memory, type: str, n: int) -> Palette:
	return rom.get_palette(type, rom.get_dex_mon_palette_id(n))
def get_mon_palette(rom: Memory, type: str, n: int) -> Palette:
	return rom.get_palette(type, rom.get_mon_palette_id(n))

def get_map_palette(rom: Memory, type: str, n: int) -> Palette:
	# Indoor map palettes (except caves/cemeteries) are determined from the palette of
	# the outdoor map they were entered from, which would be a huge pain to determine
	# from ROM data. Thus, I just use a predefined lookup table in g1const.
	return rom.get_palette(g1const.map_palette_id(n, rom.is_yellow), type)


#== Tilemaps ===============================================================================================

def _gfx_bitmap(gfx, width):
	goff, glen   = 0, len(gfx)
	pwidth, plen = width * 2, width * 16
	buf = bytearray(plen)
	while goff < glen:
		px, poff = 0, 0
		while px < pwidth:
			while poff < plen:
				b1, b2 = gfx[goff] ^ 0xFF, gfx[goff + 1] ^ 0xFF
				# interleave the bitplanes (aaaaaaaa bbbbbbbb -> abababab abababab)
				b1=(b1|b1<<4) & 0x0F0F; b1=(b1|b1<<2) & 0x3333; b1=(b1|b1<<1) & 0x5555
				b2=(b2|b2<<4) & 0x0F0F; b2=(b2|b2<<2) & 0x3333; b2=(b2|b2<<1) & 0x5555
				bits = b1 | (b2 << 1)
				buf[poff], buf[poff+1] = bits >> 8, bits & 0xFF
				goff += 2
				poff += pwidth
			px  += 2
			poff = px

		y = 0
		while y < plen:
			yield buf[y:y+pwidth]
			y += pwidth


#== Overworld sprites ======================================================================================

def get_sprite_info(rom: Memory, n: int):
	# bank, addr, length
	info = rom.table_read_bytes("sprite_gfx", 4, (n - 1) & 0xFF)
	return info[3], unpack16(info,0), info[2]

def _get_split_spriteset_side(rom: Memory, n, x, y):
	if n != 0xF8:
		t, div, s1, s2 = rom.table_read_bytes("split_spritesets", 4, (n - 0xF1) & 0xFF)
		return s1 if (x if t == 1 else y) < div else s2
	else:
		# Route 20 is special-cased because its split has a more complex shape
		if   x < 43:  return 0x01
		elif x >= 62: return 0x0A
		else:
			div = 13 if x < 55 else 8
			if y < div: return 0x0A
			else:       return 0x01

def get_map_spriteset(rom: Memory, n: int, info: Info, allow_partial:bool=False) -> bytes:
	sprites = bytearray((1,)) # sprite ID 1 (player's sprite) is always loaded
	if n < 0x25:
		# outdoor maps use predefined spritesets
		n = rom.table_read8("map_spritesets", n)
		if n > 0xF0:
			n = _get_split_spriteset_side(rom, n, info.player_x, info.player_y)
		sprites.extend(rom.table_read_bytes("spritesets", 11, (n - 1) & 0xFF))
	else:
		# for indoor maps, the map's sprite IDs are used directly
		sprites.extend(rom.get_map_sprite_ids(n, allow_partial=allow_partial))
	return sprites


#== Tilesets ===============================================================================================

def get_tileset_gfx_ptr(rom: Memory, n: int) -> ptr:
	bank, addr = rom.table_index_ptr("tilesets", 12, n)
	return rom.read8(bank, addr), rom.read16(bank, addr + 3)

def get_tileset_gfx(rom: Memory, n: int, glitch:bool=False, spriteset:bytes=None) -> bytes:
	bank, addr = get_tileset_gfx_ptr(rom, n)
	# Certain nonglitch tilesets' gfx are less than 0x600 bytes and are located at the end of a ROM bank,
	# so the game reads past the end of ROM and just grabs whatever graphics data is already at the
	# start of VRAM. This happens before sprite graphics are loaded, so there's no one "correct" way
	# to emulate this. Thus, I just leave it blank in this case.
	if not glitch:
		return rom.read_bytes(bank, addr, 0x600, allow_partial=True)
	else:
		gfx = bytearray(0x1000)
		rom.copy_bytes(bank, addr, gfx, 0, 0x600, allow_partial=True)
		_load_map_vram_glitch_tiles(rom, gfx, spriteset)
		return gfx

def get_tileset_gfx_bitmap(rom: Memory, n: int, glitch:bool=False, spriteset:bytes=None) -> ImageGenerator:
	return 128, 128 if glitch else 64, _gfx_bitmap(rom.get_tileset_gfx(n, glitch, spriteset), 16)

def _vram_load_font(rom: Memory, vram): 
	di = 0x800
	for b in rom.read_bytes(*rom.location("font"), 0x400):
		vram[di] = b; vram[di+1] = b # convert 1bpp to 2bpp
		di += 2
	rom.copy_bytes(*rom.location("font2"), vram, 0x600, 0x200)

def _load_map_vram_glitch_tiles(rom: Memory, vram, spriteset):
	# Emulate how graphics are laid out in VRAM when on the overworld.

	_vram_load_font(rom, vram)
	
	if spriteset is None: spriteset = (1,) # Player sprite is always loaded
	
	# Walking frames of overworld sprites occupy the area of VRAM usable by both backgrounds and objects.
	# (This is why many glitch map blocks have pieces of overworld sprites in them.)
	nowalk  = 0x47 if rom.is_yellow else 0x3D # sprite IDs starting here have no walking frames
	vramoff = 0x800
	for n in spriteset:
		if n >= nowalk: continue # skip any sprites without walking frames
		bank, addr, length = rom.get_sprite_info(n)
		addr += 0xC0 # start of walking frames
		rom.copy_bytes(bank, addr, vram, vramoff, length, allow_partial=True)
		vramoff += 0xC0

def get_tileset_block_bitmaps(rom: Memory, n: int, glitch:bool=False) -> Generator[ImageGenerator]:
	"""Return an iterator that yields a bitmap iterator for each block in tileset `n`."""
	gfx  = rom.get_tileset_gfx(n)
	data = rom.stream(*get_tileset_block_ptr(rom, n))
	buf  = bytearray(256) # 32*32px @ 2bpp
	for _ in range(rom.get_tileset_num_blocks(n, glitch)):
		yield _block_bitmap(data.next_bytes(16), gfx, buf)

def _block_bitmap(tiles, gfx, buf):
	ty, ti = 0, 0
	while ty < 256:
		tx = 0
		while tx < 8:
			goff = tiles[ti] * 16
			poff = ty + tx
			pend = poff + 64
			while poff < pend:
				b1, b2 = gfx[goff] ^ 0xFF, gfx[goff+1] ^ 0xFF
				# interleave the bitplanes (aaaaaaaa bbbbbbbb -> abababab abababab)
				b1=(b1|b1<<4) & 0x0F0F; b1=(b1|b1<<2) & 0x3333; b1=(b1|b1<<1) & 0x5555
				b2=(b2|b2<<4) & 0x0F0F; b2=(b2|b2<<2) & 0x3333; b2=(b2|b2<<1) & 0x5555
				bits = b1 | (b2 << 1)
				buf[poff], buf[poff+1] = bits >> 8, bits & 0xFF
				goff += 2
				poff += 8
			ti += 1
			tx += 2
		ty += 64
	y = 0
	while y < 256:
		yield buf[y:y+8]
		y += 8


#== Maps ===================================================================================================

def get_map_bitmap(rom: Memory, n: int, color:str=None) -> ImageGenerator:
	"""Draw a bitmap of map `n`.

	#### Arguments:
	- n:     The map ID.
	- color: The coloring to use (see `get_palette`.)

	#### Returns:
	- width, height:
		The width and height of the bitmap, in pixels.
	- rows:
		An iterator that returns one packed 2bpp row of the bitmap at a time.
	- palette:
		A 4-color RGB palette, if `color` is not `None`.
	"""
	return _map_bitmap(rom, n, rom.get_map_drawable_info(n), color)

def get_displaced_map_bitmap(mem: Memory, map: int, block_addr: int, 
                             x: int, y: int, color:str=None) -> ImageGenerator:
	"""Draw a bitmap of the map data at `block_addr`."""
	return _map_bitmap(mem, map, mem.get_displaced_map_info(map, block_addr, x, y), color, True)

def get_glitch_city_bitmap(rom: Memory, map: int, warp: int, color:str=None) -> ImageGenerator:
	"""Draw a bitmap of the glitch city obtained by entering `map` from `warp`."""
	return _map_bitmap(rom, map, rom.get_glitch_city_info(map, warp), color, True)

def get_cur_map_bitmap(mem: Memory) -> ImageGenerator:
	"""Draw a bitmap of the current map in memory."""
	return _map_bitmap(mem, )

def _map_bitmap(mem, n, info, palette, glitch=False):
	if palette: palette = mem.get_map_palette(type, n)
	rows = _map_bitmap_rows(mem, n, info, not palette, glitch)
	return info.width*32, info.height*32, rows, palette

def _map_bitmap_rows(mem: Memory, bank, addr, width, height, step, bitflip, gfx, blocktiles, glitch):
	spriteset = mem.get_map_spriteset(id, info, allow_partial=True) if glitch else None
	bitflip   = 0xFF if bitflip else 0
	pwidth    = width * 8              # image width in bytes (2bpp)
	buf       = bytearray(pwidth * 32) # one block row, each block is 32px tall
	blockrow  = mem.read_bytes(bank, addr, width)
	by, bx    = 0, 0
	while True:
		try:
			while by < height:
				while bx < width:
				
					tx, toff = 0, blockrow[bx] * 16
					while tx < 8:
						ty, poff = 0, bx*8 + tx
						while ty < 4:
							py, goff = 0, blocktiles[toff] * 16
							while py < 8:
								b1, b2 = gfx[goff] ^ bitflip, gfx[goff+1] ^ bitflip
								# interleave the bitplanes (aaaaaaaa bbbbbbbb -> abababab abababab)
								b1=(b1|b1<<4) & 0x0F0F; b1=(b1|b1<<2) & 0x3333; b1=(b1|b1<<1) & 0x5555
								b2=(b2|b2<<4) & 0x0F0F; b2=(b2|b2<<2) & 0x3333; b2=(b2|b2<<1) & 0x5555
								bits = b1 | (b2 << 1)
								buf[poff], buf[poff+1] = bits >> 8, bits & 0xFF
								py   += 1
								goff += 2
								poff += pwidth
							ty   += 1
							toff += 4
						tx   += 2
						toff -= 15
					bx += 1
			
				y, yend = 0, len(buf)
				while y < yend:
					yield buf[y:y+pwidth]
					y += pwidth
			
				by += 1
				bx  = 0
				addr += step
				blockrow   = mem.read_bytes(bank, addr, width)
			
			break
		except IndexError:
			# lazily switch to glitch map mode if we hit a glitch block/tile
			if glitch: raise
			glitch = True
			
			blocktiles = get_tileset_block_data(mem, info.tileset, glitch=True)
			
			# XXX is there a more efficient way to expand the gfx array size?
			gfx.extend(bytearray(0x1000 - len(gfx)))
			spriteset = mem.get_map_spriteset(id, info, allow_partial=True)
			_load_map_vram_glitch_tiles(mem, gfx, spriteset)

			continue


#== Mon / Trainer sprites ==================================================================================

def get_mon_sprite_bank(rom: Memory, n: int) -> int:
	"""
	Return the sprite bank for mon `n`.
	"""
	if   n >= 153: return 0xD
	elif n >= 116: return 0xC
	elif n >= 74:  return 0xB
	elif n >= 31:  return 0xA
	elif n == 21 and not rom.is_yellow: return 0x1 # Mew
	else:          return 0x9

def get_dex_mon_frontsprite_addr_dims(rom: Memory, n: int) -> tuple[int,int,int]:
	bank, addr = rom.get_dex_mon_base_stats_ptr(n)
	dims = rom.read8(bank, addr + 10)
	addr = rom.read16(bank, addr + 11)
	return addr, (dims & 0xF) or 256, (dims >> 4) or 256

def get_dex_mon_backsprite_addr(rom: Memory, n: int) -> int:
	bank, addr = rom.get_dex_mon_base_stats_ptr(n)
	return rom.read16(bank, addr + 13)

def get_mon_frontsprite_ptr_dims(rom: Memory, n: int) -> tuple[int,int,int,int]:
	if 182 <= n <= 184:
		width = height = 7 if n == 183 else 6
		return *rom.location(f"gfx_mon{n}"), width, height
	addr, width, height = rom.get_dex_mon_frontsprite_addr_dims(rom.get_mon_dex_num(n))
	return get_mon_sprite_bank(rom, n), addr, width, height
def get_mon_backsprite_ptr(rom: Memory, n: int) -> ptr:
	addr = rom.get_dex_mon_backsprite_addr(rom.get_mon_dex_num(n))
	return get_mon_sprite_bank(rom, n), addr

def get_trainer_sprite_ptr(rom: Memory, n: int) -> ptr:
	bank, addr = rom.location("trainer_gfx_pay")
	addr = rom.read16(bank, addr + ((n - 1) & 0xFF) * 5)
	return rom.location("trainer_gfx_bank"), addr

def get_dex_mon_frontsprite_bitmap(rom: Memory, n: int, gfx_bank: int, 
                                   color:str=None, truesize:bool=False) -> ImageGenerator:
	"""Return a bitmap row iterator for the front sprite of a mon with dex number `n`."""
	if color: color = rom.get_dex_mon_palette(color, n)
	return rom.get_compressed_bitmap(gfx_bank, *rom.get_dex_mon_frontsprite_addr_dims(n), color, truesize)

def get_dex_mon_backsprite_bitmap(rom: Memory, n: int, gfx_bank: int, 
                                  color:str=None, truesize:bool=False) -> ImageGenerator:
	"""Return a bitmap row iterator for the back sprite of a mon with dex number `n`."""
	if color: color = rom.get_dex_mon_palette(color, n)
	return rom.get_compressed_bitmap(gfx_bank, rom.get_dex_mon_backsprite_addr(n), 4, 4, color, truesize)

def get_mon_frontsprite_bitmap(rom: Memory, n: int, color:str=None, truesize:bool=False) -> ImageGenerator:
	"""Return a bitmap row iterator for the front sprite of mon `n`."""
	if color: color = rom.get_mon_palette(color, n)
	return rom.get_compressed_bitmap(*rom.get_mon_frontsprite_ptr_dims(n), color, truesize)

def get_mon_backsprite_bitmap(rom: Memory, n: int, color:str=None, truesize:bool=False) -> ImageGenerator:
	"""Return a bitmap row iterator for the back sprite of mon `n`."""
	if color: color = rom.get_mon_palette(color, n)
	return rom.get_compressed_bitmap(*rom.get_mon_backsprite_ptr(n), 4, 4, color, truesize)

def get_trainer_sprite_bitmap(rom: Memory, n: int, color:str=None, truesize:bool=False) -> ImageGenerator:
	"""Return a bitmap row iterator for the sprite of trainer class `n`."""
	if color: color = rom.get_palette(color, 0x10)
	return rom.get_compressed_bitmap(*rom.get_trainer_sprite_ptr(n), 7, 7, color, truesize)


#== Sprite decompression ===================================================================================

# TODO: properly split up decompress_gfx so it can export as both graphics and raw data

def get_compressed_bitmap(rom: Memory, bank: int, addr: int, width: int, height: int, 
                          palette: Palette, truesize:bool=False) -> ImageGenerator:
	"""Return a bitmap row iterator for a compressed sprite."""
	bitflip = 0 if palette else 0xFF
	return *decompress_gfx(rom.stream(bank, addr), width, height, bitflip, truesize), palette

def _bitstream(data):
	for b in data:
		yield (b >> 7) & 1
		yield (b >> 6) & 1
		yield (b >> 5) & 1
		yield (b >> 4) & 1
		yield (b >> 3) & 1
		yield (b >> 2) & 1
		yield (b >> 1) & 1
		yield  b       & 1

def decompress_gfx(data: Sequence[int], twidth: int, theight: int, bitflip: int, truesize:bool=False):
	data = iter(data)
	dims = next(data)
	width, height = (dims >> 4) or 256, (dims & 0xF) or 256

	bits = _bitstream(data)

	bufsize = max(width*height, twidth*theight) * 8
	if truesize:
		buf1, buf2 = bytearray(bufsize), bytearray(bufsize)
		off1, off2 = 0, 0
	else:
		buf = buf1 = buf2 = bytearray(392*2 + max(392, bufsize))
		off1, off2        = 392, 392*2

	if next(bits) == 1:
		sbuf1, soff1 = buf2, off2
		sbuf2, soff2 = buf1, off1
	else:
		sbuf1, soff1 = buf1, off1
		sbuf2, soff2 = buf2, off2
	
	_decompress_bitplane(bits, sbuf1, soff1, width, height)

	mode = next(bits)
	if mode == 1: mode += next(bits)

	_decompress_bitplane(bits, sbuf2, soff2, width, height)

	if mode != 1:
		_delta_decode_bitplane(sbuf2, soff2, width, height)
	_delta_decode_bitplane(sbuf1, soff1, width, height)

	if mode != 0: # xor buffer 2 with buffer 1
		for i in range(bufsize):
			sbuf2[soff2+i] ^= sbuf1[soff1+i]

	if not truesize:
		# buffer A hasn't been used yet so we don't need to clear it
		_center_bitplane(buf, 392,   0,   twidth, theight)
		buf[392:392*2] = (0 for _ in range(392)) # clear buffer B
		_center_bitplane(buf, 392*2, 392, twidth, theight)		

		return 56, 56, _sprite_bitmap(buf, buf, 392, 7, 7, bitflip)

	else:
		return width*8, height*8, _sprite_bitmap(buf1, buf2, 0, width, height)

def _parse_rle_packet(bits):
	n = 1
	while next(bits) != 0:
		n += 1
	l = 1 << n; v = 0
	while n > 0:
		n -= 1; v = (v << 1) | next(bits)
	return l + v - 1
	
def _decompress_bitplane(bits, buf, off, width, height):
	width *= 4; height *= 8
	px, by = 0, 0
	tx, sx = off, 6

	if next(bits) == 0:
		by += _parse_rle_packet(bits)

	while True:
		# data packet
		while True:
			if by >= height:
				px, by = px + (by // height), by % height
				if px >= width: return
				tx = (px >> 2)*height + off
				sx = (~px & 3) * 2
			p = (next(bits) << 1) | next(bits)
			if p == 0: break
			buf[tx + by] |= p << sx
			by += 1

		by += _parse_rle_packet(bits)

def _delta_decode_bitplane(buf, off, width, height):
	height *= 8
	y, xend = 0, off + width*height
	while y < height:
		x, c = off + y, 0
		while x < xend:
			b = buf[x]
			b = b^(b>>1)^(b>>2)^(b>>3)^(b>>4)^(b>>5)^(b>>6)^(b>>7) ^ c
			c = ((~(b & 1) + 1) & 0xFF) 
			buf[x] = b
			x += height
		y += 1

def _center_bitplane(buf, srcoff, dstoff, width, height):
	dstoff += ((7*((8 - width) >> 1) + (7 - height)) * 8) & 0xFF
	height *= 8
	endoff  = srcoff + width*height
	while srcoff < endoff:
		buf[dstoff:dstoff+height] = buf[srcoff:srcoff+height]
		srcoff += height; dstoff += 56

def _sprite_bitplane_bitmap(buf, off, twidth, theight):
	bwidth, bheight = twidth, theight*8
	rowbuf = bytearray(bwidth)
	for y in range(bheight):
		bi, pi = y, 0
		while pi < bwidth:
			rowbuf[pi] = buf[off+bi] ^ 0xFF
			pi += 1
			bi += bheight
		yield rowbuf

def _sprite_bitmap(buf1, buf2, off2, twidth, theight, bitflip):
	bwidth, bheight = twidth*2, theight*8
	rowbuf = bytearray(bwidth)
	y = 0
	while y < bheight:
		bx, px = y, 0
		while px < bwidth:
			b1, b2 = buf1[bx] ^ bitflip, buf2[off2+bx] ^ bitflip
			# interleave the bitplanes (aaaaaaaa bbbbbbbb -> abababab abababab)
			b1=(b1|b1<<4) & 0x0F0F; b1=(b1|b1<<2) & 0x3333; b1=(b1|b1<<1) & 0x5555
			b2=(b2|b2<<4) & 0x0F0F; b2=(b2|b2<<2) & 0x3333; b2=(b2|b2<<1) & 0x5555
			bits = b1 | (b2 << 1)
			rowbuf[px], rowbuf[px+1] = bits >> 8, bits & 0xFF
			px += 2
			bx += bheight
		y += 1
		yield rowbuf