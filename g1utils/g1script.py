# g1script.py
from __future__ import annotations

from .g1text import *

import gbutils, g1const


def glitch_char(c):
	return f"<{c:02X}>"


#== Misc. scripts ==============================================================================================

def get_152_owned_dex_rating_ptr(rom: Memory) -> ptr:
	bank, addr = rom.location("dex_ratings")
	s = rom.stream(bank, addr)
	for b in s:
		if b > 152: break
		s.skip(2)
	return bank, s.next16()
def get_152_owned_dex_rating(rom: Memory, **opt) -> str:
	opt.setdefault("sound_bank", 2)
	return rom.read_text_script(*rom.get_152_owned_dex_rating_ptr(), **opt)


#== Script parsing =============================================================================================

def _cmd_text(i, c, opt):
	return True, i.next_string(**opt)

def _cmd_ellipsis(i, c, opt):
	return True, "⋯" * i.next8()

def _cmd_pause(i, c, opt):
	return False, "{pause}"
def _cmd_wait(i, c, opt):
	return False, "{wait}"

def _cmd_newline(s, opt):
	if opt["newlines"]: s = "\n"
	return False, s

def _cmd_line(i, c, opt):
	return _cmd_newline("{l}", opt)
def _cmd_prompt(i, c, opt):
	return _cmd_newline("{prompt}", opt)
def _cmd_scroll(i, c, opt):
	return _cmd_newline("{scroll}", opt)

def _cmd_writeto(i, c, opt):
	addr = i.next16()
	return False, f"{{writeto ${addr:04X}}}"

def _cmd_drawbox(i, c, opt):
	addr, height, width = i.next16(), i.next8(), i.next8()
	return False, f"{{drawbox ${addr:04X}, {width}, {height}}}"

def _cmd_str_ptr(i, c, opt):
	s, mem, addr = '', i.mem, i.next16()
	if mem.has_addr(addr):
		i = mem.stream(i.rom_bank, addr, allow_partial=True)
		s = i.next_string(**opt)
		addr = i.addr
		if mem.has_addr(addr): return True, s
	return True, s + f"{{str ${addr:04X}}}"

def _cmd_bcd(i, c, opt):
	addr, spec = i.next16(), i.next8()
	nbytes = spec & 0x1F
	# TODO: print bcd ...
	return True, f"{{bcd ${addr:04X}, {nbytes}}}"

def _cmd_num(i, c, opt):
	mem, bank  = i.mem, i.rom_bank
	addr, spec = i.next16(), i.next8()
	nbytes, ndigits = spec >> 4, spec & 0xF	
	# Only 2-7 digit numbers are supported, all other lengths fall through to 7.
	if not(2 <= ndigits <= 6): ndigits = 7
	# Only 1-3 byte numbers are supported, all other lengths fall through to 3.
	# The length value is checked without masking out the flag bits, so if any flag bits are set
	# it will always be treated as length 3.
	if nbytes != 1 and nbytes != 2: nbytes = 3
	try:
		num = mem.read8(bank, addr) # big endian
		if nbytes != 1:
			num = (num << 8) | mem.read8(bank, addr+1)
			if nbytes != 2:
				num = (num << 8) | mem.read8(bank, addr+2)
	except AddressError:
		return True, f"{{num ${addr:04X}, {nbytes}, {ndigits}}}"
	s = str(num)
	if len(s) > ndigits:
		# If ndigits is shorter than the actual amount of digits, the first digit will be glitched.
		split = -(ndigits-1)
		s = glitch_char(int(s[:split] - 10) & 0xFF) + s[split:]
	if   nbytes & 0x80 != 0: s.rjust(ndigits, '0')
	elif nbytes & 0x40 == 0: s.rjust(ndigits, ' ')
	return False, s

def _cmd_asm(i, c, opt):
	if opt.get("disasm", False):
		return True, gbutils.disasm(i)
	else:
		addr = i.addr
		if addr < 0x8000: s = f"{{asm @ ${addr:04X}}}"
		else:             s = f"{{asm @ ${i.bank:02X}:{addr:04X}}}"
		return True, s

def _cmd_sound_common(sound, name, i, opt):
	if not i.mem.is_japan:
		bank = opt.get("sound_bank")
		if bank is not None:
			_update_sound_channels(i.mem, opt["sound_bank"], sound, opt["channels"])
	# TODO: formatting options maybe?
	return False, "{"+name+"}"

_textcmd_sounds = bytearray((
	0x86, # 0B: sfx_item_get
	0,    # 0C
	0,    # 0D
	0x91, # 0E: sfx_dex_rating
	0x86, # 0F: sfx_item_get (duplicate)
	0x89, # 10: sfx_mon_evolved
	0x94, # 11: sfx_key_item_get
	0x9A, # 12: sfx_mon_caught
	0x98, # 13: sfx_dex_registered
))
def _cmd_sound(i, c, opt):
	sound = _textcmd_sounds[c - 0x0B]
	name  = g1const.sound_name(opt.get("sound_bank"), sound, i.mem.is_yellow)
	if name: name = f"sfx_{name}"
	else:    name = f"sfx_{sound:02X}"
	return _cmd_sound_common(sound, name, i, opt)

def _cmd_cry_intro(i, c, opt):
	if i.mem.is_yellow: n, name = 0x41, "cry_pikachu"
	else:               n, name = 0x17, "cry_nidorina"
	return _cmd_sound_common(n, name, i, opt)
def _cmd_cry_pidgeot(i, c, opt):
	return _cmd_sound_common(0x50, "cry_pidgeot", i, opt)
def _cmd_cry_dewgong(i, c, opt):
	return _cmd_sound_common(0x38, "cry_dewgong", i, opt)


def _cmd_glitch(buf, c, opt):
	if opt.get("cmdlines") and len(buf) != 0:
		buf.append("\n")
	buf.append(f"{{cmd_{c:02X}}}")


_text_cmds = (
	_cmd_text,        # 00
	_cmd_str_ptr,     # 01
	_cmd_bcd,         # 02
	_cmd_writeto,     # 03
	_cmd_drawbox,     # 04
	_cmd_line,        # 05
	_cmd_prompt,      # 06
	_cmd_scroll,      # 07
	_cmd_asm,         # 08
	_cmd_num,         # 09
	_cmd_pause,       # 0A
	_cmd_sound,       # 0B
	_cmd_ellipsis,    # 0C
	_cmd_wait,        # 0D
	_cmd_sound,       # 0E
	_cmd_sound,       # 0F
	_cmd_sound,       # 10
	_cmd_sound,       # 11
	_cmd_sound,       # 12
	_cmd_sound,       # 13
	_cmd_cry_intro,   # 14
	_cmd_cry_pidgeot, # 15
	_cmd_cry_dewgong, # 16
)
def read_text_script(rom: Memory, bank: int, addr: int, 
                  /, sram_bank: int=None, **opt) -> str:
	"""
	Return a string representation of a text script.

	#### Options
	- sound_bank: The sound bank to use for text command sounds.
	- cmdlines:   Print each command on its own line.
	- disasm:     Disassemble TXT_ASM commands.
	"""
	opt.setdefault("newlines", False)
	cmdlines = opt.get("cmdlines", True)

	prev_inline = False
	rom0_sounds = None
	if not rom.is_japan:
		stack       = []
		start_addr  = addr

		sound_bank = opt.get("sound_bank")
		if sound_bank is not None:
			romx_sounds = None
			bank_sounds = {}
			addr_ids    = None
			channels    = _init_sound_channels(rom, sound_bank, opt.get("prev_sfx", ()))
			opt["channels"] = channels

	buf, i = [], rom.stream(bank, addr, sram_bank=sram_bank)
	for c in i:
		if c <= 0x17:
			if c != 0x17:
				inline, s = _text_cmds[c](i, c, opt)
				if cmdlines:
					if not(inline and prev_inline) and len(buf) != 0: 
						buf.append("\n")
					prev_inline = inline
				buf.append(s)
	
			else: # cmd_far (only added in non-Japanese versions)
				if rom.is_japan:
					_cmd_glitch(buf, c, opt)
					break

				addr, bank = i.next16(), i.next8()

				if not rom.has_addr(addr):
					if cmdlines and len(buf) != 0:
						buf.append("\n"); prev_inline = False
					buf.append(f"{{far ${bank:02X}:{addr:04X}}}")
					continue

				# Check if this is an infinite loop:
				for pbank, _, pstart, bufpos in stack:
					if bank == pbank and addr == pstart:
						s = "{infinite_loop_start}"
						if cmdlines:
							if bufpos != 0:          s = "\n"+s
							if bufpos != len(buf)-1: s = s+"\n"
						buf.insert(bufpos, s)
						break
						
				stack.append((i.rom_bank, i.addr, start_addr, len(buf)))
				start_addr  = addr
				romx_sounds = None
				i.seek(bank, addr)
	
		elif c == 0x50: # cmd_end
			if len(stack) != 0:
				bank, addr, start_addr, _ = stack.pop()
				i.seek(bank, addr)
			else:
				break
		else:
			# Glitch text commands.
			# In Japanese versions, these index a jump table OOB and execute garbage code, which often crashes.
			# In all other versions, they behave like sound commands, except they search past the end of the
			# sound command table and pull garbage sound IDs to play.
			if rom0_sounds is None:
				if rom.is_japan:
					_cmd_glitch(buf, c, opt)
					break

				rom0_sounds, remaining = rom.get_rom0_glitch_txtcmd_sounds()

			if cmdlines and len(buf) != 0:
				buf.append("\n"); prev_inline = False

			sound = rom0_sounds[c]
			if sound is None:
				# If we can't find the sound ID in the home bank, search the current ROM bank.
				if romx_sounds is None:
					romx_sounds = rom.get_romx_glitch_txtcmd_sounds(bank, rom0_sounds, remaining)
					bank_sounds[bank] = romx_sounds
					
				sound = romx_sounds.get(c)
				if sound is None:
					# If we can't find it at all in ROM, just give up.
					# (We could continue into VRAM if we have it mapped, but VRAM reads are non-deterministic 
					# because they're timing-dependent, so there's no one correct way to emulate them here.)
					buf.append(f"{{cmd_{c:02X}}}")
					continue

			name = g1const.sound_name(sound_bank, sound, rom.is_yellow)
			if name is None:
				buf.append(f"{{sfx_{sound:02X}}}")
				if sound_bank is not None:
					_update_sound_channels(rom, sound_bank, sound, channels)
				continue
				
			# Sound IDs that play an isolated channel of a basecry have very interesting glitchy behavior.
			# The game is hardcoded to always play channels 5, 6, and 8 whenever a basecry sound is played,
			# but since this sound is an isolated channel, only that one channel gets its playback pointer
			# set properly, and the the other two channels will play whatever sound data they last pointed to.
			# This is why certain glitchmons' cries vary whenever they play, and is also responsible for
			# all of the distorted sounds in glitch textscripts. It's also why some glitch textscripts cause
			# musical softlocks, since those are caused by a basecry channel playing looping music data.
			elif 0x13 < sound < 0x86:
				ch = (sound - 0x14) % 3
				if ch != 0:
					if addr_ids is None:
						addr_ids = get_sound_address_ids(rom, sound_bank)

					ch5  = _next_sound_name(rom, sound_bank, addr_ids, channels, 0)
					addr = rom.read16(sound_bank, 0x4000 + sound*3)
					if ch == 1:
						ch6, ch8 = name, _next_sound_name(rom, sound_bank, addr_ids, channels, 2)
						channels[1] = addr
					else:  # 2
						ch8, ch6 = name, _next_sound_name(rom, sound_bank, addr_ids, channels, 1)
						channels[2] = addr
					buf.append(f"{{{','.join((ch5,ch6,ch8))}}}")
				else:
					buf.append("{"+name+"}")

			# Sound ID FF is hardcoded to zero out all music and sfx channel pointers
			elif sound == 0xFF:
				buf.append("{stop_music}")
				channels[:] = (0, 0, 0)
				continue
				
			else:
				if not name.startswith("mus_"):
					name = f"sfx_{name}"
				buf.append("{"+name+"}")

			_update_sound_channels(rom, sound_bank, sound, channels)	

	return ''.join(buf)


#== Sounds =====================================================================================================

def _get_glitch_textcmd_sounds(s, sounds, exclude, remaining):
	try:
		while remaining > 0:
			cmd, sound = s.next8(), s.next8()
			if exclude[cmd] is None and cmd > 0x17 and cmd != 0x50:
				sounds[cmd] = sound; remaining -= 1
	except StopIteration: pass
	return sounds, remaining

def get_rom0_glitch_txtcmd_sounds(rom: Memory):
	s = rom.stream(None, rom.location("txtcmd_sounds"), allow_partial=True)
	sounds = [None]*0x100
	return _get_glitch_textcmd_sounds(s, sounds, sounds, 0x100 - 0x19)
def get_romx_glitch_txtcmd_sounds(rom: Memory, bank: int, exclude: list, remaining: int):
	s = rom.stream(bank, 0x4000 + (rom.location("txtcmd_sounds") & 1), allow_partial=True)
	return _get_glitch_textcmd_sounds(s, {}, exclude, remaining)[0]

def _init_sound_channels(rom, bank, sounds):
	channels = [None,None,None]
	for sound in sounds:
		_update_sound_channels(rom, bank, sound, channels)
		if 0x86 > sound > 0x13:
			c = (sound - 0x14) % 3
			if c != 0:
				_next_sound(rom, bank, channels, 0)
				if c == 1: _next_sound(rom, bank, channels, 2)
				else:      _next_sound(rom, bank, channels, 1)
	return channels

def _update_sound_channels(rom, bank, sound, channels):
	addr = 0x4000 + sound*3
	c    = rom.read8(bank, addr)
	c, i = c & 0xF, (c >> 6) + 1
	dest = c
	while i > 0:
		# We only care about channels 5, 6, and 8.
		# Do some bit magic to turn channels 5,6,8 into indices 0,1,2 and ignore all other channels.
		d = dest ^ 4; d ^= d >> 1
		if d < 3:
			channels[d] = rom.read16(bank, addr + 1)
		addr += 3
		c2 = rom.read8(bank, addr)
		c, dest = c2, dest + ((c2 - c) & 0xFF)
		i -= 1

def _next_sound(rom, bank, channels, i):
	addr = channels[i]
	if addr is not None:
		channels[i] = find_next_sfx_addr(rom, bank, addr, i == 2)

def _next_sound_name(rom: Memory, bank, addr_ids, channels, i):
	addr = channels[i]
	if addr is not None:
		addr = channels[i] = find_next_sfx_addr(rom, bank, addr, i == 2)
		if addr is not None:
			sound = addr_ids.get(addr)
			if sound is not None:
				name = g1const.sound_name(bank, sound, rom.is_yellow)
			else:
				name = rom.location("unrefd_sounds").get((bank, addr))
				if name is None:
					return f"${addr:04X}"
			if name.startswith("mus_"):
				name = "softlock_"+name
			elif not name.startswith("basecry_"): 
				name = "sfx_"+name
			return name
	return "?"


#== Audio data =================================================================================================

def get_sound_address_ids(rom: Memory, sound_bank: int) -> dict:
	ids, s = {}, rom.stream(sound_bank, 0x4003)
	for id in range(1,0xFF):
		_, addr = s.next8(), s.next16()
		ids[addr] = id
	return ids

_cmd_skip = bytearray((
	1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, # D_
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 2, 1, 1, # E_
	1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1           # F_
))
def skip_sfx_data(s, noise: bool):
	# The sound data interpreter doesn't have a call stack, so it can only store one return address at a time.
	# Recursive calls will just clobber the last return address.
	ret_addr   = None
	loop_addr  = None
	loop_count = 1
	is_music   = False
	for b in s:
		if b >= 0xD0:
			if b < 0xF8:
				s.skip(_cmd_skip[b - 0xD0])
			
			elif b == 0xFF: # ret
				if ret_addr is not None: 
					s.seek(None, ret_addr)
					ret_addr = None
				else: 
					return
			
			elif b == 0xFD: # call
				addr = s.next16()
				ret_addr = s.addr
				s.seek(None, addr)
			
			elif b == 0xFE: # loop
				# The loop command was only ever intended to be used for actual loops, but it's essentially
				# a jump instruction that can go anywhere, and in glitch/desynced command streams it won't
				# necessarily jump to somewhere that leads back to it.
				count, addr = s.next8(), s.next16()
				# TODO: follow jumps but also detect infinite loops and skip finite loops

			elif b == 0xF8: # do_music
				is_music = True

			else:
				s.skip(_cmd_skip[b - 0xD0])
		elif b & 0x30 != 0:
			b &= 0xF0
			if   b == 0x10: # pitch_sweep
				if not is_music: s.skip(1)
			elif b == 0x20: # square_note / noise_note
				if not is_music: s.skip(2 if noise else 3)

def find_next_sfx_addr(rom: Memory, bank: int, addr: int, noise: bool) -> int:
	try:
		s = rom.stream(bank, addr)
		skip_sfx_data(s, noise)
		return s.addr
	except AddressError:
		return None
