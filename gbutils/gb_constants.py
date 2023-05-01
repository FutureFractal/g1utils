# gb_constants.py


nintendo_logo = (
	b"\xCE\xED\x66\x66\xCC\x0D\x00\x0B\x03\x73\x00\x83\x00\x0C\x00\x0D"
	b"\x00\x08\x11\x1F\x88\x89\x00\x0E\xDC\xCC\x6E\xE6\xDD\xDD\xD9\x99"
	b"\xBB\xBB\x67\x63\x6E\x0E\xEC\xCC\xDD\xDC\x99\x9F\xBB\xB9\x33\x3E"
)


_memory_region_names = (
	"rom0",
	"rom0",
	"romx",
	"romx",
	"vram",
	"sram",
	"wram",
	 None
)
def get_memory_region_name(addr: int) -> str:
	name = _memory_region_names[addr >> 13]
	if name is not None:
		return name
	elif addr < 0xFE00:     return "echoram"
	elif addr < 0xFF00:
		if   addr < 0xFEA0: return "oam"
		else:               return "unmapped"
	else:
		if   addr < 0xFF80: return "io"
		elif addr < 0xFFFF: return "hram"
		else:               return "io"


_ioreg_names = {
	0x00: "JOYP",
	0x01: "SB",
	0x02: "SC",
	0x04: "DIV",
	0x05: "TIMA",
	0x06: "TMA",
	0x07: "TMC",
	0x0F: "IF",
	0x10: "NR10",
	0x11: "NR11",
	0x12: "NR12",
	0x13: "NR13",
	0x14: "NR14",
	0x16: "NR21",
	0x17: "NR22",
	0x18: "NR23",
	0x19: "NR24",
	0x1A: "NR30",
	0x1B: "NR31",
	0x1C: "NR32",
	0x1D: "NR33",
	0x1E: "NR34",
	0x20: "NR41",
	0x21: "NR42",
	0x22: "NR43",
	0x23: "NR44",
	0x24: "NR50",
	0x25: "NR51",
	0x26: "NR52",
	0x40: "LCDC",
	0x41: "STAT",
	0x42: "SCY",
	0x43: "SCX",
	0x44: "LY",
	0x45: "LYC",
	0x46: "DMA",
	0x47: "BGP",
	0x48: "OBP0",
	0x49: "OBP1",
	0x4A: "WY",
	0x4B: "WX",
	0xFF: "IE"
}
_cgb_ioreg_names = {
	0x4D: "KEY1",
	0x4F: "VBK",
	0x51: "HDMA1",
	0x52: "HDMA2",
	0x53: "HDMA3",
	0x54: "HDMA4",
	0x55: "HDMA5",
	0x56: "RP",
	0x68: "BGPI",
	0x69: "BGPD",
	0x6A: "OBPI",
	0x6B: "OBPD",
	0x6C: "UNKNOWN1",
	0x70: "SVBK",
	0x72: "UNKNOWN2",
	0x73: "UNKNOWN3",
	0x74: "UNKNOWN4",
	0x75: "UNKNOWN5",
	0x76: "UNKNOWN6",
	0x77: "UNKNOWN7",
}
def get_io_reg_name(addr: int, cgb:bool=False) -> str:
	if addr >= 0xFF00:
		addr &= 0xFF
		name = _ioreg_names.get(addr)
		if name is None and cgb:
			name = _cgb_ioreg_names.get(addr)
		return name
