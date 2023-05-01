# __init__.py

from .gb_memory    import *
from .gb_constants import *
from .gb_savestate import *

AddressError.__module__ = __name__
Memory.__module__       = __name__

__exports__ = (
	"AddressError",
	"Memory",
	"ROM",

	"unpack16",
	"is_rom_addr",
	"is_rom0_addr",
	"is_romx_addr",
	"rom_bank_to_offset",
	"rom_ptr_to_offset",
	"rom_offset_to_bank",
	"rom_offset_tp_addr",
	"rom_offset_to_ptr",
	"open_rom",
	"open_sav",
	"open_sameboy_savestate",
	"read_sameboy_savestate",
	"open_bgb_savestate",
	"read_bgb_savestate",
	"open_mgba_savestate",
	"read_mgba_savestate",
	"open_vba_savestate",
	"read_vba_savestate",
	"open_kigb_savestate",
	"read_kigb_savestate"
)
