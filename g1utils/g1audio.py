# g1audio.py

if "xrange" in globals(): range = xrange # py2 compat


def get_mon_cry(rom, n):
	sound, pitch, tempo = rom.table_read_bytes("cries", 3, (n - 1) & 0xFF)
	return (sound*3 + 0x14) & 0xFF, pitch, tempo - 0x80

def get_map_soundbank_and_music(rom, n):
	return rom.table_read_bytes("map_music", 2, n)

def get_sound_header(rom, bank, n):
	addr = 0x4000 + n*3 # sound table is at the start of each sound bank
	ch = rom.read8(bank, addr)
	channels = b >> 6
	ptrs = []
	ch &= 0x3F
	ptrs.append((ch, rom.read16(bank, addr + 1)))
	for i in range(channels):
		addr += 3
		ch, ptr = rom.read8(bank, addr), rom.read16(bank, addr + 1)
		ptrs.append((ch, ptr))
	return ptrs
