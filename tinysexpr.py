class SyntaxError(Exception):
    def __init__(self, msg):
        self.value = msg

    def __str__(self):
        return self.value

class X:
    pass

class UnexpectedEOF(SyntaxError):
    def __init__(self):
        super().__init__('unexpected end of file')

class UnexpectedChar(SyntaxError):
    def __init__(self, expected, got):
        super().__init__(f"expected '{expected}', got '{got}'")

class InvalidEscape(SyntaxError):
    def __init__(self, char):
        super().__init__(f"invalid escape character '{char}'")

DEFAULT_DELIMS = {
    '"': ('\\', { 'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"' }),
    '|': (None, {})
}

def read(file_like, delims=DEFAULT_DELIMS, comment_char=';', atom_handler=lambda x: x):
    """Parse an S-expression from a file-like object.

    The function takes the following arguments:
    `file_like`: An object that is file like, i.e. provides a `read` method.
    `delims`: A map of delimiters used to surround atoms that contain spaces.
        Commonly these are double-quotes to represent strings as in `"Hello"` or vertical bars to allow for symbols that contain spaces as in `|some symbol|`.
        The map maps the delimiter character to a tuple of two elements: the escape character and a map of escape sequences.
        See `DEFAULT_DELIMS` for an example.
        The map `DEFAULT_DELIMS` specifies delimiters for strings and symbols.
    `comment_char`: The character that starts a single line comment.
        The default value is `;`.
    `atom_handler`: A function that is called when an atom is parsed.
        This function is passed a string that consists of the text of the parsed atom. The function can convert this string into something else and the returned value is used to construct the S-expression.

    The function returns the parsed S-expression as a nested list.
    When a parse error is encountered, a `SyntaxError` is raised with a message that describes the error.
    """

    sym_delim = { c for c in '()' + comment_char + ''.join(delims.keys()) }
    ch = file_like.read(1)
    row = 1
    col = 1

    def curr():
        return ch

    def next():
        nonlocal ch, row, col
        ch = file_like.read(1)
        if ch == '\n':
            row += 1
            col = 1
        else:
            col += 1
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

    def parse():

        def read_delim(delim, delim_info):
            escape_char, escape_map = delim_info
            read = [curr()]
            c = next()
            while c:
                match c:
                    case _ if c == escape_char:
                        c = next()
                        if c in escape_map:
                            read.append(escape_map[c])
                        else:
                            raise InvalidEscape(c)
                    case _ if c == delim:
                        read.append(c)
                        next()
                        return ''.join(read)
                    case _:
                        read.append(c)
                c = next()

        def read_atom():
            read = []
            c = curr()
            while c and not c.isspace() and c not in sym_delim:
                read.append(c)
                c = next()
            return ''.join(read)

        exp = []
        while True:
            c = skip_ws()
            if not c:
                raise UnexpectedEOF()
            match c:
                case '(':
                    next()
                    s = parse()
                    exp.append(s)
                case ')':
                    next()
                    return exp
                case _ if c in delims:
                    exp.append(atom_handler(read_delim(c, delims[c])))
                case _:
                    assert not c.isspace()
                    exp.append(atom_handler(read_atom()))

    match skip_ws():
        case '(':
            next()
            return parse()
        case '':
            return None
        case c:
            raise UnexpectedChar('(', c)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        print(read(open(sys.argv[1], 'rt')))