import pytest
import tinysexpr

from io import StringIO

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
    assert tinysexpr.read(StringIO(input)) == expected

@pytest.mark.parametrize("input,msg", [
    ('', tinysexpr.UNEXPECTED_EOF),
    ('abc', "expected '(', got 'a'"),
    ('(a', tinysexpr.UNEXPECTED_EOF),
    ('|a b c', tinysexpr.UNEXPECTED_EOF),
    ('"abc"cde"', tinysexpr.UNEXPECTED_EOF),
    ('"abc\\9cde"', "invalid escape character"),
    ('(1 (2 3) (4 5) 6 (7 (8 9))', tinysexpr.UNEXPECTED_EOF),
])
def test_error(input, msg):
    with pytest.raises(tinysexpr.SyntaxError) as e:
        tinysexpr.read(StringIO(input))
        assert msg in str(e)

