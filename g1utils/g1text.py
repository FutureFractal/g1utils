# g1text.py
from __future__ import annotations

from .g1base import *

import gbutils

_default = object() # default value for "default" param
_hexbyte = lambda b: f"<{b:02X}>"


#== Strings ================================================================================================

def read_string(mem: Memory, bank: int, addr: int, length:int=None,
             /, sram_bank:int=None, lang:str=None, default=_default, **opt) -> str:
	"""
	Read and decode a string from a memory image.
	"""
	if not lang: lang = mem.lang
	try:
		if length is None: data = mem.stream(bank, addr, sram_bank=sram_bank)
		else:              data = mem.read_bytes(bank, addr, length, sram_bank=sram_bank)
		return decode_string(lang, data, **opt)
	except AddressError:
		if default is _default: raise
		elif callable(default): return default(addr)
		else:                   return default

def next_string(s: Memory.Stream, lang:str=None, **opt) -> str:
	if not lang: lang = s.mem.lang
	return decode_string(lang, s, **opt)

def find_string_end(mem: Memory, bank: int, addr: int, /, sram_bank:int=None) -> int:
	i = mem.stream(bank, addr, sram_bank=sram_bank)
	for b in i:
		if b == 0x50: break
	return _printed_string_end(mem, b) or i.addr

def find_printed_string_end(rom: Memory, bank: int, addr: int, /, sram_bank:int=None) -> int:
	i = rom.stream(bank, addr, sram_bank=sram_bank)
	for b in i:
		if _chars_EFIGS[b] is None: break
	return _printed_string_end(rom, b) or i.addr

def _printed_string_end(mem: Memory, c):
	# The string printing routine returns a pointer to the last character read
	# in register de on completion. This is used by several routines to find the end
	# of a string after printing it. However, a few control characters will terminate
	# a string by printing their own special strings, which clobbers this register.
	# (This is why several glitchmons share the same dex entry aside from species name)
	if   c == 0x00:
		return mem.location("char00_script")
	elif c == 0x57 or c == 0x58:
		return mem.location("char57_script")

def get_packed_name(rom: Memory, bank: int, addr: int, n: int, length=None, default=_default, **opt) -> str:
	if n <= 195:
		s = rom.stream(bank, addr)
		try:
			for _ in range((n - 1) & 0xFF):
				while s.next8() != 0x50: pass
			if length is not None: s = s.next_bytes(length)
			return decode_string(rom.lang, s, **opt)
		except AddressError:
			if default is _default: raise
			elif callable(default): return default(n)
			else:                   return default
	elif n > 200:
		return f"TM{n-200:02}"
	else:
		return f"HM{n-195:02}"


#== Text decoding ==========================================================================================

def decode_char(lang: str, c: int, **opt) -> str:
	"""
	Decode a single character.
	"""
	if c >= 0x60:
		charset = _charsets.get(lang)
		if charset is None:
			raise Exception("lang must be one of [J,E,F,I,G,S]")

	else:
		return f"<{c:02X}>"

def decode_string(lang: str, data: Sequence[int], **opt) -> str:
	"""
	Decode a string.

	Arguments:
	
	data
		The string bytes.
	lang
		The language/character encoding.

	Optional arguments:
	
	grepr
		The string repsesentation for "glitch block" characters.
		Can be a string or a function that converts a character value to a string.
		Default: The character's hex code, with the form "<XX>"
	vrepr
		The contextual tileset to use for varying characters.
		Possible values:
		- field / overworld
		- dex / pokedex
		- party
		- stats
		- battle
		- hof / halloffame
	nocaps
		Pass True to make string control characters not be all caps.
	newlines
		Pass True to make newline control characters decode to newlines.
	"""
	data = iter(data)
	
	charset = _charsets.get(lang)
	if charset is None:
		raise Exception("lang must be one of [J,E,F,I,G,S]")
	chars = charset.chars
	
	opt.setdefault("grepr",    _hexbyte)
	opt.setdefault("caps",     True)
	opt.setdefault("newlines", False)
	opt["vchar"] = _vchar_opt.get(opt.get("vchar"))
	opt["data"]  = data
	
	buf = bytearray()
	for b in data:
		c = chars[b]
		if type(c) is str:
			buf.extend(c.encode())
		elif c is not None:
			buf.extend(c(b, charset, opt).encode())
		else: # terminator char
			if b != 0x50:
				if b == 0x5F:
					buf.extend(chars[0xE8].encode()) # dot char
				elif isinstance(data, gbutils.Memory.Stream):
					data.seek(None, _printed_string_end(data.mem, b))
			break

	return buf.decode()


#== Special characters =====================================================================================

def _c_lang(b, charset, opt):
	return charset.lang[b - 0xBA]

def _c_langctrl(b, charset, opt):
	s = charset.ctrl[b]
	if opt["caps"]: s = s.upper()
	return s

def _c_ctrl(b, charset, opt):
	return _ctrl_char_codes[b]

def _c_newline(b, charset, opt):
	if opt["newlines"]: return "\n"
	return _c_ctrl(b, charset, opt)
_c_prompt = _c_newline

def _c_player(b, charset, opt):
	return _c_ctrl(b, charset, opt)

def _c_rival(b, charset, opt):
	return _c_ctrl(b, charset, opt)

def _c_target(b, charset, opt):
	return _c_ctrl(b, charset, opt)

def _c_user(b, charset, opt):
	return _c_ctrl(b, charset, opt)
	
def _c_poke(b, charset, opt):
	return "POKé"   if opt["caps"] else "Poké"
def _c_rocket(b, charset, opt):
	return "ROCKET" if opt["caps"] else "Rocket"

# Non-text tiles ("glitch block" characters)
def _c_glitch(c, charset, opt):
	grepr = opt["grepr"]
	return grepr(c) if callable(grepr) else grepr

# Tiles/characters from 0x60-0x78 vary depending on the current gamemode (overworld, battle, etc)
def _c_varying(b, charset, opt):
	v = opt["vchar"]
	if v is not None:
		c = _varying_chars[b - 0x60][v]
		if type(c) is str:  return c
		elif c is not None: return charset.varying[c]
	return _c_glitch(b, charset, opt) # default to glitch block

# Characters E4 and E5 in japanese versions place a handakuten/dakuten above the following character
_cc_noncombining = ("゜","゛")
_cc_combining    = ("\u309A","\u3099") # Unicode combining handakuten/dakuten
def _c_combining(cc, charset, opt):
	data = opt["data"]

	# Combining chars will overwrite preceding combining chars, so loop until we get a non-combining char
	c = next(data, 0x50)
	while c & 0xFE == 0xE4:
		cc, c = c, next(data, 0x50)
	cc &= 1
	
	s = _chars_J[c]
	if   c > 0x78:
		return s + _cc_combining[cc]
	elif c < 0x7B:
		# Precomposed chars will overwrite combining chars
		return s
	elif s is not None:
		if type(s) is not str: s = s(c, charset, opt)
		if s[0] == "{" or s[0] == "<":
			return _cc_noncombining[cc] + s
		# Combining chars will combine with the first char of a string-printing char
		# if that first char is not a precomposed char.
		elif c not in (0x4D, 0x54, 0x5B):
			return s[0] + _cc_combining[cc] + s[1:]
		else:
			return s
	elif c == 0x5F:
		return "。" + _cc_combining[cc]
	else:
		return _cc_noncombining[cc]



#== Charsets ===============================================================================================

_G = _c_glitch
_V = _c_varying
_L = _c_lang
_C = _c_combining

_ctrl_char_codes = {
	0x00: "{ERROR}",
	0x49: "{dexp}",
	0x4B: "{_n}",
	0x4C: "{an}", # unused?
	0x4E: "{r}",
	0x4F: "{l}",
	0x50: None,
	0x51: "{p}",
	0x52: "{PLAYER}",
	0x53: "{RIVAL}",
	0x55: "{n}",
	0x57: "{end}",
	0x58: "{endp}",
	0x59: "{TARGET}",
	0x5A: "{USER}",
	0x5F: "{dexend}",
}

_chars_J = (
	# 00
	None,
			
	# 01-4A
		  "イ゙", "ヴ", "エ゙", "オ゙", "ガ", "ギ", "グ",
	"ゲ", "ゴ", "ザ", "ジ", "ズ", "ゼ", "ゾ", "ダ",
	"ヂ", "ヅ", "デ", "ド", "ナ゙", "ニ゙", "ヌ゙", "ネ゙",
	"ノ゙", "バ", "ビ", "ブ", "ボ", "マ゙", "ミ゙", "ム゙",
	"ィ゙", "あ゙", "い゙", "ゔ", "え゙", "お゙", "が", "ぎ",
	"ぐ", "げ", "ご", "ざ", "じ", "ず", "ぜ", "ぞ",
	"だ", "ぢ", "づ", "で", "ど", "な゙", "に゙", "ぬ゙",
	"ね゙", "の゙", "ば", "び", "ぶ", "べ", "ぼ", "ま゙",
	"パ", "ピ", "プ", "ポ", "ぱ", "ぴ", "ぷ", "ぺ",
	"ぽ", "ま゚", "が",
	
	_c_prompt,     # 4B
	_c_newline,    # 4C
	"も゚",          # 4D
	_c_newline,    # 4E
	_c_newline,    # 4F
	None,          # 50
	_c_prompt,     # 51
	_c_player,     # 52
	_c_rival,      # 53
	"ポケモン",     # 54
	_c_newline,    # 55
	"⋯⋯",        # 56
	None,          # 57
	None,          # 58
	_c_target,     # 59
	_c_user,       # 5A
	"パソコン",     # 5B
	"わざマシン",   # 5C
	"トレーナー",   # 5D
	"ロケットだん", # 5E
	None,          # 5F
	
	# 60-FF
	_V,   _V,   _V,   _V,   _V,   _V,   _V,   _V,
	_V,   _V,   _V,   _V,   _V,   _V,   _V,   _V,
	_V,   _V,   _V,   _V,   _V,   "⋯", _V,   _V,
	_V,   "╔",  "═",  "╗",  "║", "╚",  "╝",  " ",
	"ア", "イ", "ウ", "エ", "オ", "カ", "キ", "ク",
	"ケ", "コ", "サ", "シ", "ス", "セ", "ソ", "タ",
	"チ", "ツ", "テ", "ト", "ナ", "ニ", "ヌ", "ネ",
	"ノ", "ハ", "ヒ", "フ", "ホ", "マ", "ミ", "ム",
	"メ", "モ", "ヤ", "ユ", "ヨ", "ラ", "ル", "レ",
	"ロ", "ワ", "ヲ", "ン", "ッ", "ャ", "ュ", "ョ",
	"ィ", "あ", "い", "う", "え", "お", "か", "き",
	"く", "け", "こ", "さ", "し", "す", "せ", "そ",
	"た", "ち", "つ", "て", "と", "な", "に", "ぬ",
	"ね", "の", "は", "ひ", "ふ", "へ", "ほ", "ま",
	"み", "む", "め", "も", "や", "ゆ", "よ", "ら",
	"リ", "る", "れ", "ろ", "わ", "を", "ん", "っ",
	"ゃ", "ゅ", "ょ", "ー", _C,   _C,   "？", "！",
	"。", "ァ", "ゥ", "ェ", "▷", "▶", "▼", "♂",
	"円", "×",  ".",  "／", "ォ", "♀", "０", "１",
	"２", "３", "４", "５", "６", "７", "８", "９"
)
_chars_EFIGS = (
	# 00
	None,
		   
	# 01-48
		  _G,   _G,   _G,   _G,   _G,   _G,   _G,
	_G,   _G,   _G,   _G,   _G,   _G,   _G,   _G,
	_G,   _G,   _G,   _G,   _G,   _G,   _G,   _G,
	_G,   _G,   _G,   _G,   _G,   _G,   _G,   _G,
	_G,   _G,   _G,   _G,   _G,   _G,   _G,   _G,
	_G,   _G,   _G,   _G,   _G,   _G,   _G,   _G,
	_G,   _G,   _G,   _G,   _G,   _G,   _G,   _G,
	_G,   _G,   _G,   _G,   _G,   _G,   _G,   _G,
	_G,   _G,   _G,   _G,   _G,   _G,   _G,   _G,
	_G,
	
	_c_prompt,   # 49
	"<PKMN>",    # 4A
	_c_prompt,   # 4B
	_c_newline,  # 4C
	_G,          # 4D
	_c_newline,  # 4E
	_c_newline,  # 4F
	None,        # 50
	_c_prompt,   # 51
	_c_player,   # 52
	_c_rival,    # 53
	_c_poke,     # 54
	_c_newline,  # 55
	"⋯⋯",      # 56
	None,        # 57
	None,        # 58
	_c_target,   # 59
	_c_user,     # 5A
	"PC",        # 5B
	_c_langctrl, # 5C
	_c_langctrl, # 5D
	_c_rocket,   # 5E
	None,        # 5F

	# 60-B9
	_V,   _V,   _V,   _V,   _V,   _V,   _V,   _V,
	_V,   _V,   _V,   _V,   _V,   _V,   _V,   _V,
	_V,   _V,   _V,   _V,   _V,   "⋯", _V,   _V,
	_V,   "╔",  "═",  "╗",  "║",  "╚",  "╝",  " ",
	"A",  "B",  "C",  "D",  "E",  "F",  "G",  "H",
	"I",  "J",  "K",  "L",  "M",  "N",  "O",  "P",
	"Q",  "R",  "S",  "T",  "U",  "V",  "W",  "X",
	"Y",  "Z",  "(",  ")",  ":",  ";",  "[",  "]",
	"a",  "b",  "c",  "d",  "e",  "f",  "g",  "h",
	"i",  "j",  "k",  "l",  "m",  "n",  "o",  "p",
	"q",  "r",  "s",  "t",  "u",  "v",  "w",  "x",
	"y",  "z",  _L,   _L,   _L,   _L,   _L,   _L,
	_L,   _L,   _L,   _L,   _L,   _L,   _L,   _L,
	_L,   _L,   _L,   _L,   _L,   _L,   _L,   _L,
	_L,   _L,   _L,   _L,   _L,   _L,   _L,   _L,
	_L,   _L,   _L,   _L,   _L,   _L,   _L,   _L,
	"'","<PK>","<MN>","-",  _L,   _L,   "?",  "!",
	".",  "ァ", "ゥ", "ェ", "▷", "▶", "▼", "♂",
	"₽",  "×",  ".",  "/",  ",",  "♀",  "0",  "1",
	"2",  "3",  "4",  "5",  "6",  "7",  "8",  "9"
)

_chars_E = (
	# BA-E5
				"é",  "'d", "'l", "'s", "'t", "'v",
	" ",  " ",  " ",  " ",  " ",  " ",  " ",  " ",
	" ",  " ",  " ",  " ",  " ",  " ",  " ",  " ",
	" ",  " ",  " ",  " ",  " ",  " ",  " ",  " ",
	" ",  " ",  " ",  " ",  " ",  " ",  " ",  " ",
	None, None, None, None, "'r", "'m"
)
_chars_IS = (
	# BA-E5
				"à",  "è",  "é",  "ù",  "À",  "Á",
	"Ä",  "Ö",  "Ü",  "ä",  "ö",  "ü",  "È",  "É",
	"Ì",  "Í",  "Ñ",  "Ò",  "Ó",  "Ù",  "Ú",  "á",
	"ì",  "í",  "ñ",  "ò",  "ó",  "ú",  "°",  "&",
	"'d", "'l", "'m", "'r", "'s", "'t", "'v", " ",
	None, None, None, None, "¿",  "¡"
)
_chars_GF = (
	# BA-E5
				"à",  "è",  "é",  "ù",  "ß",  "ç",
	"Ä",  "Ö",  "Ü",  "ä",  "ö",  "ü",  "ë",  "ï",
	"â",  "ô",  "û",  "ê",  "î",  " ",  " ",  " ",
	" ",  " ",  " ",  " ",  "c'", "d'", "j'", "l'",
	"m'", "n'", "p'", "s'", "'s", "t'", "u'", "y'",
	None, None, None, None, "+",  " "
)

_vchar_opt = {
	"field":      0,
	"overworld":  0,
	"dex":        1,
	"pokedex":    1,
	"party":      2,
	"stats":      3,
	"battle":     4,
	"hof":        5,
	"halloffame": 5
}
_varying_chars = (
#     field  dex    party  stats  battle hof
	( "<A>", 4,     "<A>", "<A>", None,  None  ),
	( "<B>", 5,     "<B>", "<B>", None,  None  ),
	( "<C>", "<g>", None,  None,  None,  "<C>" ),
	( "<D>", None,  None,  None,  None,  "<D>" ),
	( "<E>", None,  None,  None,  None,  "<E>" ),
	( "<F>", None,  None,  None,  None,  "<F>" ),
	( "<G>", None,  None,  None,  None,  "<G>" ),
	( "<H>", None,  None,  None,  None,  "<H>" ),
	( "<I>", None,  None,  None,  None,  "<I>" ),
	( "<V>", None,  None,  None,  None,  "<V>" ),
	( "<S>", None,  None,  None,  None,  "<S>" ),
	( "<L>", None,  None,  None,  None,  "<L>" ),
	( "<M>", None,  None,  None,  None,  "<M>" ),
	( "：",  None,  "║",   "┃",  "┃",  "："  ),
	( "ぃ",  None,  6,     6,     6,     "ぃ"  ),
	( "ぅ",  None,  "◢",  "◢",  "◢",  "ぅ"   ),
	( 0,     7,     7,     7,     7,     0     ),
	( 1,     "┃",  None,  None,  None,  1     ),
	( 2,     None,  "『",  "<P>", "『",  2     ),
	( 3,     8,     8,     8,     "┃",  3     ),
	( "・",  9,     9,     9,     "┗",  "・"  ),
	None,
	( "ぁ",  "━",  "━",  "━",  "━",  "ぁ"   ),
	( "ぇ",  "▔",  "▔",  "┛",  "┛",  "ぇ"   ),
	( "ぉ",  "◣",  "◣",  "┃",  "◣",  "ぉ"   )
)
_varying_chars_J = ( "「", "」", "『", "』", "<m>","<k>",":ʟ", "ど",  "ɪᴅ", "№"   )
_varying_chars_E = ( "‘",  "’",  "“",  "”", "′",  "″",  ":ʟ", "<to>","ɪᴅ", "№"   )
_varying_chars_F = ( "‘",  "’",  "“",  "”", "<m>","<k>",":ɴ", "➡︎",   ".ɪᴅ","№"   )
_varying_chars_I = ( "‘",  "’",  "“",  "”", "<m>","<k>",":ʟ", "ᴀ",   "ɪᴅ", "№"   )
_varying_chars_G = ( "‘",  "’",  "“",  "”", "<m>","<k>",":ʟ", "➡︎",   "ɪᴅ·","ɴᵣ" )
_varying_chars_S = ( "‘",  "’",  "“",  "”", "<m>","<k>",":ɴ", "ᴀ",   "ɪᴅ", "№"   )

_ctrl_chars_EG = {
	0x5C: "TM",
	0x5D: "Trainer",
}
_ctrl_chars_F = {
	0x5C: "CT",
	0x5D: "Dres.",
}
_ctrl_chars_I = {
	0x5C: "MT",
	0x5D: "Allen.",
}
_ctrl_chars_S = {
	0x5C: "MT",
	0x5D: "Entren.",
}

_charsets = {
	"J": Info(
		chars   = _chars_J,
		varying = _varying_chars_J
	),
	"E": Info(
		chars   = _chars_EFIGS,
		lang    = _chars_E,
		varying = _varying_chars_E,
		ctrl    = _ctrl_chars_EG
	),
	"F": Info(
		chars   = _chars_EFIGS,
		lang    = _chars_GF,
		varying = _varying_chars_F,
		ctrl    = _ctrl_chars_F
	),
	"I": Info(
		chars   = _chars_EFIGS,
		lang    = _chars_IS,
		varying = _varying_chars_I,
		ctrl    = _ctrl_chars_I
	),
	"G": Info(
		chars   = _chars_EFIGS,
		lang    = _chars_GF,
		varying = _varying_chars_G,
		ctrl    = _ctrl_chars_EG
	),
	"S": Info(
		chars   = _chars_EFIGS,
		lang    = _chars_IS,
		varying = _varying_chars_S,
		ctrl    = _ctrl_chars_S
	)
}