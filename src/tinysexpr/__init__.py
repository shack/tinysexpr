from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

type Coord = tuple[int, int]
type Range = tuple[Coord, Coord]

@dataclass(frozen=True)
class SExpr(Sequence):
    s: tuple[Any, ...]
    range: Range

    def __getitem__(self, i):
        return self.s[i]

    def __len__(self):
        return len(self.s)

    def __str__(self):
        inner = ' '.join(str(s) for s in self.s)
        return f'({inner})'

class SyntaxError(Exception):
    def __init__(self, coord, msg):
        self.value = msg
        self.coord = coord

    def __str__(self):
        return f'{self.coord}: {self.value}'

class UnexpectedEOF(SyntaxError):
    def __init__(self, coord):
        super().__init__(coord, 'unexpected end of file')

class UnexpectedChar(SyntaxError):
    def __init__(self, coord, expected, got):
        super().__init__(coord, f"expected '{expected}', got '{got}'")

class InvalidEscape(SyntaxError):
    def __init__(self, coord, char):
        super().__init__(coord, f"invalid escape character '{char}'")

DEFAULT_DELIMS = {
    '"': ('\\', { 'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"' }),
    '|': (None, {})
}

def read(file_like, delims=DEFAULT_DELIMS, comment_char=';', atom_handler=lambda x, ran: x):
    """Parse an S-expression from a file-like object.

    The function takes the following arguments:
    `file_like`: An object that is file like, i.e. provides a `read` method.
    `delims`: A map of delimiters used to surround atoms that contain spaces.
        Commonly these are double-quotes to represent strings as in `"Hello"` or
        vertical bars to allow for symbols that contain spaces as in `|some
        symbol|`.  The map maps the delimiter character to a tuple of two
        elements: the escape character and a map of escape sequences.  See
        `DEFAULT_DELIMS` for an example.  The map `DEFAULT_DELIMS` specifies
        delimiters for strings and symbols.
    `comment_char`: The character that starts a single line comment.
        The default value is `;`.
    `atom_handler`: A function that is called when an atom is parsed.
        This function is passed a string that consists of the text of the parsed
        atom and a range (a pair of row/col pairs) with the coordinates of the
        atom in the file.  The function can convert this string into something
        else and the returned value is used to construct the S-expression.

    The function returns the parsed S-expression as a nested list.  When a parse
    error is encountered, a `SyntaxError` is raised with a message that
    describes the error and the source coordinates in the field coord of the
    exception.
    """

    sym_delim = { c for c in '()' + comment_char + ''.join(delims.keys()) }
    ch = file_like.read(1)
    next_coord = (1, 1)
    coord = None

    def curr():
        return ch

    def next():
        nonlocal ch, coord, next_coord
        ch = file_like.read(1)
        coord = next_coord
        row, col = next_coord
        if ch == '\n':
            next_coord = (row + 1, 1)
        else:
            next_coord = (row, col + 1)
        return ch

    def skip_ws():
        while True:
            c = curr()
            if c.isspace():
                next()
            elif c == comment_char:
                while c and c != '\n':
                    c = next()
            else:
                break
        return c

    def parse(begin):
        def read_delim(delim, delim_info):
            escape_char, escape_map = delim_info
            begin = coord
            read = [curr()]
            c = next()
            while c:
                if c == escape_char:
                    c = next()
                    if c in escape_map:
                        read.append(escape_map[c])
                    else:
                        raise InvalidEscape(coord, c)
                elif c == delim:
                    read.append(c)
                    next()
                    return (''.join(read), (begin, coord))
                else:
                    read.append(c)
                c = next()
            raise UnexpectedEOF(coord)

        def read_atom():
            read = []
            begin = coord
            c = curr()
            while c and not c.isspace() and c not in sym_delim:
                read.append(c)
                c = next()
            return (''.join(read), (begin, coord))

        exp = []
        while True:
            c = skip_ws()
            if not c:
                raise UnexpectedEOF(coord)
            match c:
                case '(':
                    next()
                    s = parse(coord)
                    exp.append(s)
                case ')':
                    next()
                    return SExpr(tuple(exp), (begin, coord))
                case _ if c in delims:
                    exp.append(atom_handler(*read_delim(c, delims[c])))
                case _:
                    assert not c.isspace()
                    exp.append(atom_handler(*read_atom()))

    while True:
        match skip_ws():
            case '(':
                next()
                try:
                    res = parse(coord)
                except SyntaxError as e:
                    raise e
                yield res
            case '':
                return
            case c:
                raise UnexpectedChar(coord, '(', c)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        print(read(open(sys.argv[1], 'rt')))