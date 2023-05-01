# datafmt.py
from __future__ import annotations

from sys import stdout as _stdout

_newlines = ["\n"+("\t"*i) for i in range(11)]
def _get_newline(tablvl):
	if tablvl < len(_newlines):
		return _newlines[tablvl]
	else:
		return "\n"+("\t"*tablvl)

_dquote = lambda s: f'"{s}"'

class _Syntax:
	def __init__(self, **args):
		self.__dict__ = args
_syntaxes = {
	"jx": _Syntax(
		comments =  True,
		ident    =  str,
		numkey   =  str,
		list     =  "()",
		set      =  "{}",
		tuple    = ("( "," )"),
		gdict    =  False,
		gsep     =  " := "
	),
	"json": _Syntax(
		comments =  False,
		ident    =  _dquote,
		numkey   =  _dquote,
		list     =  "[]",
		set      =  "[]",
		tuple    = ("[ "," ]"),
		gdict    =  True
	),
	"json5": _Syntax(
		comments =  True,
		ident    =  str,
		numkey   =  _dquote,
		list     =  "[]",
		set      =  "[]",
		tuple    = ("[ "," ]"),
		gdict    =  True
	)
}

def tuple_table_pads(rows):
	ncols = len(rows[0])
	pads  = [0]*ncols
	for row in rows:
		for i in range(ncols):
			pads[i] = max(pads[i], len(row[i]))
	return pads

class Writer(object):
	"""
	...
	"""

	def __init__(self, syntax:str="json", dict=None, file=None):
		if type(syntax) is str:
			syntax = _syntaxes[syntax]
		self._syntax       = syntax
		self._stack        = []
		self._items        = []
		self._pad          = 0
		self._indent       = 0
		self._gdict        = False
		self._startcomment = None
		self._context      = self._context(self)
		self._file         = file

		if dict: self.begin_top_level_dict(dict)
		
	def finish(self):
		while self._stack: self.end_block()

		buf = []
		if self._startcomment:
			for line in self._startcomment.splitlines():
				buf.append(f"// {line}\n")
			buf.append("\n")
		
		gdict  = self._syntax.gdict
		braces = "{}" if gdict and len(self._items) > 1 else None
		gsep   = ": " if gdict else self._syntax.gsep
		return ''.join(self._compile_block(buf, braces, gsep))

	def write(self, file=_stdout):
		if isinstance(file, str):
			with open(file, "w") as f:
				f.write(self.finish())
		elif hasattr(file, "isatty") and file.isatty():
			print(self.finish(), file=file)
		else:
			file.write(self.finish())
	def __enter__(self):
		return self
	def __exit__(self, ex_type,*_):
		if ex_type is None: self.write()
	
	def _compile_block(self, buf, braces, sep=": "):
		pad      = self._pad + 2
		newline  = _get_newline(self._indent)
		comments = self._syntax.comments
		comment  = None
		ident    = self._syntax.ident
		
		if braces:
			buf.append(braces[0])
			buf.append(newline)
		
		first = True
		for item in self._items:
			if not first:
				buf.append(",")
				if comment and comments: buf.append(" // "+comment)
				buf.append(newline)
			first = False
		
			key, value, comment, off = item
			
			if key is not None:
				buf.append((ident(key)+sep).ljust((pad - off) if off != -1 else 0))
			
			if type(value) is str:
				buf.append(value)
			else:
				buf.extend(value)
				
		if comment and comments:
			if len(self._items) > 1: buf.append(" ")
			buf.append(" // "+comment)

		return buf

	class _context:
		def __init__(self, writer):
			self._w = writer
		def __enter__(self):
			return self
		def __exit__(self, *_):
			self._w.end_block()
	def _begin_block(self, braces, key=None):
		self._stack.append((key, braces, self._items, self._pad))
		self._items   = []
		self._pad     = 0
		self._indent += 1
		return self._context

	def end_block(self):
		key, braces, items, pad = self._stack.pop()
		indent = self._indent - 1
		
		buf = self._compile_block([], braces)
		buf.append(_get_newline(indent))
		buf.append(braces[1])
		items.append((key, buf, None, -1))
		
		self._items, self._indent, self._pad = items, indent, pad
	

	def heading_comment(self, comment: str):
		self._startcomment = comment
	
	
	def item(self, item, comment:str=None, off:int=0):
		self._items.append((None, str(item), comment, off))

	def prop(self, key: str, value, comment:str=None, off:int=0):
		if off != -1: self._pad = max(self._pad, len(key)+off)
		self._items.append((key, str(value), comment, off))
	

	def begin_list_item(self):
		return self._begin_block(self._syntax.list)
	def begin_set_item(self):
		return self._begin_block(self._syntax.set)
	def begin_dict_item(self):
		return self._begin_block("{}")
	def begin_object_item(self):
		return self._begin_block("{}")
	
	def begin_list_prop(self, key: str):
		return self._begin_block(self._syntax.list, key)
	def begin_set_prop(self, key: str):
		return self._begin_block(self._syntax.set, key)
	def begin_dict_prop(self, key: str):
		return self._begin_block("{}", key)
	def begin_object_prop(self, key: str):
		return self._begin_block("{}", key)
	
	def begin_top_level_dict(self, key:str=None):
		return self._begin_block("{}", key)
	def begin_top_level_object(self, key:str=None):
		return self._begin_block("{}", key)
	
	
	def id_item(self, item, comment:str=None):
		self.item(self._syntax.ident(item), comment)
	def id_prop(self, key: str, value, comment:str=None):
		self.prop(key, self._syntax.ident(value), comment)
	
	def string_prop(self, key: str, value: str, comment:str=None):
		self.prop(key, f'"{value}"', comment, off=1)
	
	
	def enum_repr(self, value, srepr, irepr=str, crepr=None, iskey:bool=False, **kargs):
		s = srepr(value, **kargs)
		if s is not None:
			return self._syntax.ident(s), None
		else:
			s = self._syntax.numkey(irepr(value)) if iskey else irepr(value)
			c = crepr(value) if crepr and self._syntax.comments else None
			return s, c
	
	def enum_item(self, value, srepr, irepr=str, crepr=None, **kargs):
		name, comment = self.enum_repr(value, srepr, irepr, crepr, **kargs)
		self.item(name, comment)
	
	def enum_prop(self, key: str, value, srepr, irepr=str, crepr=None, **kargs):
		name, comment = self.enum_repr(value, srepr, irepr, crepr, **kargs)
		self.prop(key, name, comment)


	def tuple_repr(self, tup: tuple, pads=None):
		if pads is not None:
			buf = []
			for i in range(len(tup)-1):
				buf.append((str(tup[i])+", ").ljust(pads[i]+2))
			buf.append(str(tup[-1]).ljust(pads[-1]))
			tup = ''.join(buf)
		else:
			tup = ", ".join(tup)
		b = self._syntax.tuple
		return b[0]+tup+b[1]

	def tuple_item(self, tup: tuple, pads:tuple[int]=None, comment:str=None):
		self.item(self.tuple_repr(tup, pads), comment=comment)

	def tuple_prop(self, key: str, tup: tuple, pads:tuple[int]=None, comment:str=None):
		self.prop(key, self.tuple_repr(tup, pads), comment=comment, off=2)
	
	def tuple_item_rows(self, rows: tuple[tuple], comments:tuple[str]=None):
		pads     = tuple_table_pads(rows)
		comments = iter(comments) if comments else None
		for row in rows:
			comment = next(comments) if comments else None
			self.tuple_item(row, pads=pads, comment=comment)
	
	def tuple_prop_rows(self, keys: tuple[str], rows: tuple[tuple], comments:tuple[str]=None):
		# check if rows is a generator:
		if hasattr(rows, "__next__"): rows = tuple(rows)
		pads = tuple_table_pads(rows)
		keys = iter(keys)
		if comments:
			comments = iter(comments)
			for row in rows:
				self.tuple_prop(next(keys), row, pads=pads, comment=next(comments))
		else:
			for row in rows:
				self.tuple_prop(next(keys), row, pads=pads)


	def enum_tuple_repr(self, tup: tuple, srepr, irepr=str, crepr=None, pads=None, **kargs) -> str:
		buf, comment = [], False
		for n in tup:
			s = srepr(n, **kargs)
			if s is not None:
				buf.append(s)
			else:
				buf.append(irepr(n))
				comment = True
		crepr = crepr if self._syntax.comments else None
		return self.tuple_repr(buf, pads), (crepr(tup) if (comment and crepr) else None)

	def enum_tuple_prop(self, key: str, tup: tuple, srepr, irepr=str, crepr=None, pads:tuple[int]=None, **kargs):
		tup, comment = self.enum_tuple_repr(tup, srepr, irepr, crepr, pads, **kargs)
		self.prop(key, tup, comment=comment, off=2)


	def multi_line_string_prop(self, key: str, value: str):
		newline = _get_newline(self._indent + 1)
		buf = ["("]
		for line in value.splitlines():
			buf.append(newline)
			buf.append(f'"{line}"')
		buf.append(_get_newline(self._indent))
		buf.append(")")
		self._items.append((key, ''.join(buf), None, -1))