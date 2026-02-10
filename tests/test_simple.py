import pytest
import tinysexpr

from io import StringIO

def to_list(sexpr):
    return [ to_list(x) if isinstance(x, tinysexpr.SExpr) else x for x in sexpr ]

@pytest.mark.parametrize("input,expected", [
    ('', [None]),
    ('()', [[]]),
    ('  ()    ', [[]]),
    ('(|a b c| || "abc\\"def" |abcgf xs!!|)', [['|a b c|', '||', '"abc"def"', '|abcgf xs!!|']]),
    ('(abc b0!@#$% c-d)', [['abc', 'b0!@#$%', 'c-d']]),
    (u'(1😀)', [['1😀']]),
    ('(a b c (d e f () |x yz|))', [['a', 'b', 'c', ['d', 'e', 'f', [], '|x yz|']]]),
    ('(1 (2 3) (4 5) 6 (7 (8 9)))', [['1', ['2', '3'], ['4', '5'], '6', ['7', ['8', '9']]]]),
    ('(1 (2 3) (4 5)); 6 (7 (8 9)))', [['1', ['2', '3'], ['4', '5']]]),
    ('(1 2) (3 (4 5))', [['1', '2'], ['3', ['4', '5']]]),
])
def test_correct(input, expected):
    for res, exp in zip(tinysexpr.read(StringIO(input)), expected):
        assert to_list(res) == exp if exp is not None else res == None

@pytest.mark.parametrize("input,cls", [
    # ('', tinysexpr.UnexpectedEOF),
    ('abc', tinysexpr.UnexpectedChar),
    ('(', tinysexpr.UnexpectedEOF),
    ('(  ', tinysexpr.UnexpectedEOF),
    ('(a  ', tinysexpr.UnexpectedEOF),
    ('(a', tinysexpr.UnexpectedEOF),
    ('(|a b c', tinysexpr.UnexpectedEOF),
    ('("abc"cde"', tinysexpr.UnexpectedEOF),
    ('("abc\\9cde"', tinysexpr.InvalidEscape),
    ('(1 (2 3) (4 5) 6 (7 (8 9))', tinysexpr.UnexpectedEOF),
])
def test_error(input, cls):
    with pytest.raises(cls) as e:
        for _ in tinysexpr.read(StringIO(input)):
            pass
