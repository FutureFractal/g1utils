# g1gfx.py

from gbutils import read16
from .g1data import *

if "xrange" in globals(): range = xrange # py2 compat


### Glitch IDs

def glitch_palette_ids(yellow=False):
	return range(43 if yellow else 40, 256)

def get_glitchmon_palette_ids(rom, families):
	palettes = set()
	for f in families:
		palettes.add(get_dex_mon_palette_id(rom, n))
	return sorted(palettes)


### Palettes

def get_raw_palette(rom, n, type="sgb"):
	if n is None: return None
	data = rom.table_read_bytes(type+"_palettes", 8, n)
	pal = []
	for i in range(0,8,2):
		rgb = read16(data,i)
		pal.append((rgb & 31, (rgb >> 5) & 31, (rgb >> 10) & 31))
	return pal

def get_palette(rom, n, type="sgb"):
	if n is None: return None
	# convert from RGB555 to RGB888 and copy the highest 3 bits into the new lowest 3 bits
	return [((r << 3) | (r >> 2),
	         (g << 3) | (g >> 2),
	         (b << 3) | (b >> 2)) for r, g, b in get_raw_palette(rom, n, type)]

# Indoor map palettes (except caves/cemeteries) are determined from the palette of
# the outdoor map they were entered from, which would be a huge pain to determine
# from ROM data. Thus, I just use a predef lookup table.
_map_palette_ids = (
	1,   2,   3,   4,   5,   6,   7,   8,   9,   10,
	11,  None,0,   0,   0,   0,   0,   0,   0,   0,
	0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
	0,   0,   0,   0,   0,   0,   0,   1,   1,   1,
	1,   2,   2,   2,   2,   2,   35,  0,   0,   0,
	0,   0,   3,   3,   3,   3,   3,   3,   3,   35,
	35,  35,  4,   4,   4,   4,   4,   4,   0,   None,
	0,   0,   0,   0,   0,   None,0,   0,   None,0,
	0,   0,   35,  0,   0,   35,  0,   0,   0,   6,
	6,   6,   6,   6,   6,   6,   6,   6,   6,   6,
	6,   6,   6,   6,   6,   None,None,None,35,  None,
	None,None,None,10,  None,None,None,None,10,  0,
	10,  0,   7,   7,   7,   7,   7,   7,   7,   7,
	7,   7,   7,   7,   7,   7,   7,   7,   7,   7,
	7,   5,   25,  25,  25,  25,  25,  25,  25,  5,
	5,   5,   8,   8,   8,   8,   8,   8,   8,   35,
	35,  35,  35,  6,   8,   9,   9,   9,   9,   9,
	9,   9,   9,   9,   10,  11,  11,  11,  11,  11,
	11,  11,  11,  11,  0,   0,   0,   0,   0,   0,
	0,   0,   35,  0,   35,  0,   6,   35,  35,  7,
	7,   7,   7,   7,   None,None,None,11,  11,  11,
	11,  11,  11,  11,  9,   9,   9,   8,   8,   8,
	8,   8,   8,   8,   8,   8,   35,  35,  35,  5,
	4,   None,35,  11,  11,  11,  11,  None,None,None,
	None,None,None,None,None,1,   35,  25,
					
	# Yellow only:
	0
)
def get_map_palette_id(n, yellow=False):
	if n <= (0xF8 if yellow else 0xF7):
		return _map_palette_ids[n]
def get_map_palette(rom, n, type="sgb"):
	n = get_map_palette_id(n, rom.is_yellow)
	if n is not None: return get_palette(rom, n, type)

def get_dex_mon_palette_id(rom, n):
	return rom.table_read8("mon_palettes", n)
def get_mon_palette_id(rom, n):
	return get_dex_mon_palette_id(rom, get_mon_dex_num(rom, n))

def get_dex_mon_palette(rom, n, type="sgb"):
	return get_palette(rom, get_dex_mon_palette_id(rom, n), type)
def get_mon_palette(rom, n, type="sgb"):
	return get_palette(rom, get_mon_palette_id(rom, n), type)


### VRAM emulation

def _vram_load_font(rom, vram):
	bank, addr = rom.get_location("font")
	bytes = rom.read_bytes(bank, addr, 0x400)
	di = 0x800
	for b in bytes:
		vram[di] = b; vram[di+1] = b
		di += 2
	bank, addr = rom.get_location("font2")
	rom.copy_bytes(bank, addr, vram, 0x600, 0x200)

def get_map_vram_chr_image(rom, tileset, spriteset=None):
	vram = bytearray(0x1000)
	
	# Certain tilesets' gfx are less than 0x600 bytes and are located at the end of a ROM bank,
	# so the game reads past the end of ROM and just grabs whatever graphics data is already at the
	# start of VRAM. This happens before sprite graphics are loaded, so there's no one "correct"
	# way to emulate this. Thus, I just leave it blank in this case.
	bank, addr = get_tileset_gfx_ptr(rom, tileset)
	rom.copy_bytes(bank, addr, vram, 0, 0x600, allow_partial=True)
	
	_vram_load_font(rom, vram)
	
	if spriteset:
		# Sprites starting at this ID have no walking frames
		nowalk  = 0x47 if rom.is_yellow else 0x3D
		gfxiter = 0x800
		for n in spriteset:
			# We only care about sprites with walking frames here, since those are
			# the only sprite frames loaded into the VRAM area indexable by backgrounds.
			if n >= nowalk: continue
			bank, addr, length = get_sprite_info(rom, n)
			addr += 0xC0 # start of walking frames
			rom.copy_bytes(bank, addr, vram, gfxiter, length)
			gfxiter += 0xC0
	
	return vram


### Sprites

def get_dex_mon_party_sprite(rom, n):
	return rom.table_read4("party_sprites", (n - 1) & 0xFF)
def get_mon_party_sprite(rom, n):
	return get_dex_mon_party_sprite(rom, get_mon_dex_num(rom, n))

def get_sprite_info(rom, n):
	# bank, addr, length
	info = rom.table_read_bytes("sprites", 4, (n - 1) & 0xFF)
	return info[3], read16(info,0), info[2]

def get_map_sprite_ids(rom, n):
	bank, addr = get_map_actors_ptr(rom, n)
	num, ids = rom.read8(bank, addr), []
	addr += 1
	for i in range(num):
		id = rom.read8(bank, addr)
		if id not in ids: ids.append(id)
		t = rom.read8(bank, addr+5)
		if   t & 0x40 != 0: addr += 8
		elif t & 0x80 != 0: addr += 7
		else:               addr += 6
	return ids

def get_split_spriteset_side(rom, n, x, y):
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

def get_map_effective_spriteset(rom, n, x, y):
	sprites = [1] # sprite ID 1 (player's sprite) is always loaded
	if n < 0x25:
		# outdoor maps use predefined spritesets
		n = rom.table_read8("map_spritesets", n)
		if n > 0xF0:
			n = get_split_spriteset_side(rom, n, x, y)
		sprites.extend(rom.table_read_bytes("spritesets", 11, (n - 1) & 0xFF))
	else:
		# for indoor maps, the map's sprite IDs are used directly
		sprites.extend(get_map_sprite_ids(rom, n))
	return sprites


### Tilesets

def get_tileset_gfx_ptr(rom, n):
	bank, addr = rom.get_location("tilesets")
	addr += n*12
	return rom.read8(bank, addr), rom.read16(bank, addr + 3)

def get_tileset_gfx(rom, n):
	bank, addr = get_tileset_gfx_ptr(rom, n)
	return rom.read_bytes(bank, addr, 0x600, allow_partial=True)


### Maps

def get_map_gfx(rom, id, info, glitch=False):
	if glitch:
		spriteset = get_map_effective_spriteset(rom, id, info.entry_x, info.entry_y)
		return get_map_vram_chr_image(rom, info.tileset, spriteset)
	else:
		return get_tileset_gfx(rom, info.tileset)

def _map_bitmap_row(blockrow, y, blocktiles, tilegfx, bitflip):
	for block in blockrow:
		toff  = block*16 + (y >> 3)*4
		tiles = blocktiles[toff:(toff+4)]
		assert len(tiles) == 4
		for tile in tiles:
			poff   = tile*16 + (y & 7)*2
			b1, b2 = tilegfx[poff] ^ bitflip, tilegfx[poff+1] ^ bitflip
			yield ((b1 >> 7) & 1) | ((b2 >> 6) & 2)
			yield ((b1 >> 6) & 1) | ((b2 >> 5) & 2)
			yield ((b1 >> 5) & 1) | ((b2 >> 4) & 2)
			yield ((b1 >> 4) & 1) | ((b2 >> 3) & 2)
			yield ((b1 >> 3) & 1) | ((b2 >> 2) & 2)
			yield ((b1 >> 2) & 1) | ((b2 >> 1) & 2)
			yield ((b1 >> 1) & 1) | ( b2       & 2)
			yield ( b1       & 1) | ((b2 << 1) & 2)

def _map_bitmap_rows(rom, id, info, invert):
	width, height = info.width, info.height
	bank          = info.bank
	blockaddr     = info.block_addr
	blockstep     = info.block_step
	blocktiles    = get_tileset_blocks(rom, info.tileset, glitch=info.glitch)
	tilegfx       = get_map_gfx(rom, id, info, glitch=info.glitch)
	bitflip       = 0xFF if invert else 0
	range32 = range(32)
	for by in range(height):
		blockrow = rom.read_bytes(bank, blockaddr, width)
		for y in range32:
			yield _map_bitmap_row(blockrow, y, blocktiles, tilegfx, bitflip)
		blockaddr += blockstep

def _get_map_bitmap(rom, id, info, color):
	palette = get_map_palette(rom, id, type=color) if color else None
	return info.width*32, info.height*32, _map_bitmap_rows(rom, id, info, not color), palette

def get_map_bitmap(rom, n, color="sgb"):
	return _get_map_bitmap(rom, n, get_map_info(rom, n), color)

def get_glitch_map_bitmap(rom, n, block_addr, x, y, color="sgb"):
	return _get_map_bitmap(rom, n, get_glitch_map_info(rom, n, block_addr, x, y), color)
def get_glitch_city_bitmap(rom, map, warp, color="sgb"):
	return _get_map_bitmap(rom, map, get_glitch_city_info(rom, map, warp), color)
