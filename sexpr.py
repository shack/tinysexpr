from io import StringIO

import pytest

_UNEXPECTED_EOF = 'unexpected end of file'

class SyntaxError(Exception):
    def __init__(self, msg):
        self.value = msg

    def __str__(self):
        return self.value

DEFAULT_DELIMS = {
    '"': ('\\', { 'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"' }),
    '|': (None, {})
}

def read(file_like, delims=DEFAULT_DELIMS, comment_char=';', atom_handler=lambda x: x):
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

    def error(msg):
        raise SyntaxError(f'{msg} at {row}:{col}')

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
                            error(f"invalid escape character '{c}'")
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
                error(_UNEXPECTED_EOF)
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

    c = skip_ws()
    if c == '(':
        next()
    else:
        error(f"expected '(', got '{c}'")
    return parse()

@pytest.mark.parametrize("input,expected", [
    ('()', []),
    ('(|a b c| || "abc\\"def" |abcgf xs!!|)', ['|a b c|', '||', '"abc"def"', '|abcgf xs!!|']),
    ('(abc b0!@#$% c-d)', ['abc', 'b0!@#$%', 'c-d']),
    (u'(1😀)', ['1😀']),
    ('(a b c (d e f () |x yz|))', ['a', 'b', 'c', ['d', 'e', 'f', [], '|x yz|']]),
    ('(1 (2 3) (4 5) 6 (7 (8 9)))', ['1', ['2', '3'], ['4', '5'], '6', ['7', ['8', '9']]]),
    ('(1 (2 3) (4 5)); 6 (7 (8 9)))', ['1', ['2', '3'], ['4', '5']]),
])
def test_correct(input, expected):
    assert read(StringIO(input)) == expected

@pytest.mark.parametrize("input,msg", [
    ('', _UNEXPECTED_EOF),
    ('abc', "expected '(', got 'a'"),
    ('(a', _UNEXPECTED_EOF),
    ('|a b c', _UNEXPECTED_EOF),
    ('"abc"cde"', _UNEXPECTED_EOF),
    ('"abc\\9cde"', "invalid escape character"),
    ('(1 (2 3) (4 5) 6 (7 (8 9))', _UNEXPECTED_EOF),
])
def test_error(input, msg):
    with pytest.raises(SyntaxError) as e:
        read(StringIO(input))
        assert msg in str(e)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        print(read(open(sys.argv[1], 'rt')))