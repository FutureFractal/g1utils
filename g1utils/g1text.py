# g1text.py
#coding=UTF-8

from gbutils import AddressError

if "xrange" in globals(): range = xrange # py2 compat


### Names

def get_mon_name(rom, n, **opt):
	length = 5 if rom.is_japan else 10
	return decode_string(rom.lang, rom.table_read_bytes("mon_names", length, (n - 1) & 0xFF), **opt)

def _get_packed_name(rom, n, location, opt, len=None):
	if n <= 195:
		bank, addr = rom.get_location(location)
		for i in range((n - 1) & 0xFF):
			addr = get_string_end(rom, bank, addr)
		return get_string(rom, bank, addr, len=len, **opt)
	elif n > 200:
		return "TM%.2d" % (n - 200)
	else:
		return "HM%.2d" % (n - 195)
def get_item_name(rom, n, **opt):
	return _get_packed_name(rom, n, "item_names", opt)
def get_move_name(rom, n, **opt):
	return _get_packed_name(rom, n, "move_names", opt)
def get_trainer_name(rom, n, **opt):
	if n in (0x19, 0x2A, 0x2B): return _rival_name(rom)
	return _get_packed_name(rom, n, "trainer_names", opt, 12)

def get_type_name(rom, n, **opt):
	bank, addr = rom.table_read_addr("type_names", n)
	return get_string(rom, bank, addr, **opt)


### Strings

def get_string_end(rom, bank, addr):
	i = rom.byte_iter(bank, addr)
	for b in i:
		if b == 0x50: break
	return i.addr

def get_print_string_end(rom, bank, addr):
	i = rom.byte_iter(bank, addr)
	for b in i:
		if _chars_EFIGS[b] is None: break
	return i.addr

def get_string_and_end(rom, bank, addr, lang=None, **opt):
	if not lang: lang = rom.lang
	i = rom.byte_iter(bank, addr)
	s = decode_string(lang, i, **opt)
	return s, i.addr

_default = object()
def get_string(rom, bank, addr, len=None, lang=None, default=_default, **opt):
	if not lang: lang = rom.lang
	try:
		if len is None: i = rom.byte_iter(bank, addr)
		else:           i = rom.read_bytes(bank, addr, len)
		return decode_string(lang, i, **opt)
	except AddressError:
		if default is not _default: return default
		else: raise


### Text decoding

_hexbyte = lambda b: ("<%.2X>" % b)
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
def decode_string(lang, bytes, gchar=_hexbyte, vchar=None):
	charset = _charsets[lang]
	if vchar:
		vchar = _vchar_opt[vchar]
	chars  = charset[0]
	bytes  = iter(bytes)
	params = charset + (bytes, gchar, vchar)
	buf    = []
	for b in bytes:
		c = chars[b]
		if type(c) is str:
			buf.append(c)
		elif c:
			buf.append(c(b, params))
		else:
			if b == 0x5F: buf.append(chars[0xE8])
			break
	return ''.join(buf)

def _c_lang(b, params):
	return params[1][b - 0xBA]
def _c_langctrl(b, params):
	return params[3][b]

def _c_ctrl(b, params):
	return _ctrl_char_codes[b]

# TODO: add in options for converting these to newlines
_c_newline = _c_ctrl
_c_prompt  = _c_ctrl

# TODO: if I ever support reading from RAM savestates, have these chars read from RAM
_c_player = _c_ctrl
_c_rival  = _c_ctrl
_c_target = _c_ctrl
_c_user   = _c_ctrl

# "glitch block" chars
def _c_glitch(b, params):
	return params[5](b)

# chars from 0x60-0x78 vary depending on the current gamemode (overworld, battle, etc)
def _c_varying(b, params):
	mode = params[6]
	if mode is not None:
		c = _varying_chars[b - 0x60][mode]
		if type(c) is str:  return c
		elif c is not None: return params[2][c]
	return params[5](b) # default to glitch block behavior

# chars E4 and E5 in Japanese versions place a handakuten or dakuten, respectively,
# above the following char.
_cc_chars     = ("゜", "゛")
_cc_combining = ("゚", "゙") # Unicode combining chars
_python3      = "unicode" not in globals()
def _c_combining(bc, params):
	bytes = params[4]
	b = next(bytes, 0x50)
	
	# combining chars will overwrite preceding combining chars
	while b == 0xE4 or b == 0xE5:
		bc, b = b, next(bytes, 0x50)
	
	bc -= 0xE4
	c = _chars_J[b]
	if b >= 0x60:
		if c is not _c_varying:
			return c + _cc_combining[bc]
		elif params[6] is not None:
			c = _c_varying(b, params)
			if c[0] == "<": return c + _cc_chars[bc]
			else:           return c + _cc_combining[bc]
		else:
			return params[5](b) + _cc_chars[bc]
	elif type(c) is str:
		# precomposed chars will overwrite combining chars.
		# combining chars will combine with the first char of a string-printing char
		# if that first char is not a precomposed char.
		if b not in (0x46, 0x4C, 0x4D, 0x4E):
			return c
		elif _python3:
			return c[0] + _cc_combining[bc] + c[1:]
		else:
			c = unicode(c)
			return (c[0] + _cc_combining[bc] + c[1:]).encode("utf-8")
	elif c:
		return _cc_chars[bc] + c(b, params)
	elif b == 0x5F:
		return "。" + _cc_combining[bc]
	else:
		return _cc_chars[bc]

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
			
	# 01-4F
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
		  
	# 4B-5F
	_c_prompt,
	_c_newline,
	"も゚",
	_c_newline,
	_c_newline,
	None,
	_c_prompt,
	_c_player,
	_c_rival,
	"ポケモン",
	_c_newline,
	"⋯⋯",
	None,
	None,
	_c_target,
	_c_user,
	"パソコン",
	"わざマシン",
	"トレーナー",
	"ロケットだん",
	None,
	
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
		   
	# 01-47
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
		 
	# 49-5F
	_c_prompt,
	"<PKMN>",
	_c_prompt,
	_c_newline,
	_G,
	_c_newline,
	_c_newline,
	None,
	_c_prompt,
	_c_player,
	_c_rival,
	"Poké",
	_c_newline,
	"⋯⋯",
	None,
	None,
	_c_target,
	_c_user,
	"PC",
	_c_langctrl,
	_c_langctrl,
	"Rocket",
	None,

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
	( "ぅ",  None,  "◢",  "◢",  "◢",  "ぅ"  ),
	( 0,     7,     7,     7,     7,     0     ),
	( 1,     "┃",  None,  None,  None,  1     ),
	( 2,     None,  "『",  "<P>", "『",  2     ),
	( 3,     8,     8,     8,     "┃",  3     ),
	( "・",  9,     9,     9,     "┗",  "・"  ),
	None,
	( "ぁ",  "━",  "━",  "━",  "━",  "ぁ"  ),
	( "ぇ",  "▔",  "▔",  "┛",  "┛",  "ぇ"  ),
	( "ぉ",  "◣",  "◣",  "┃",  "◣",  "ぉ"  )
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
	"J": ( _chars_J,     None,      _varying_chars_J, None           ),
	"E": ( _chars_EFIGS, _chars_E,  _varying_chars_E, _ctrl_chars_EG ),
	"F": ( _chars_EFIGS, _chars_GF, _varying_chars_F, _ctrl_chars_F  ),
	"I": ( _chars_EFIGS, _chars_IS, _varying_chars_I, _ctrl_chars_I  ),
	"G": ( _chars_EFIGS, _chars_GF, _varying_chars_G, _ctrl_chars_EG ),
	"S": ( _chars_EFIGS, _chars_IS, _varying_chars_S, _ctrl_chars_S  )
}
