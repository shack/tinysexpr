# S-Expression Parser

A very simple [S-expression](https://en.m.wikipedia.org/wiki/S-expression) parser that tries to make as little fuss as possible.

## Example

This module provides a single function
```
def read(file_like, delims=DEFAULT_DELIMS, comment_char=';', atom_handler=lambda x: x):
```
that returns the read S-expression.
Reading
```
(a b c (123 e f () x))
```
returns
```
['a', 'b', 'c', ['123', 'e', 'f', [], 'x']]
```

## Atoms

`a`, `b`, `c` in the above example are called **atoms**.
Atoms are parsed using two different rules:
1. Every sequence that does not contain a whitespace, opening of closing parenthesis or the comment character is an atom.
2. Every sequence that starts and ends with a **delimiter** is an atom.
   The default delimiters are `"` for strings with the usual escape characters (`\n`, `\t`, `\"`, `\\`, ...) and `|` without escape characters.
   Using the `delims` parameter, you can customize the delimiters and their escape sequences.

## Details

The parameters of `read` are:
1. `file_like`: An object that is [file like](https://docs.python.org/3/glossary.html#term-file-object) i.e. provides a `read` method.
2. `delims`: A map of delimiters used to surround atoms that contain spaces.
   Commonly these are double-quotes to represent strings as in `"Hello"` or
   vertical bars to allow for symbols that contain spaces as in `|some symbol|`.
   The map `DEFAULT_DELIMS` specifies delimiters for strings and symbols.
3. `comment_char`: The character that starts a single line comment.
   The default value is `;`.
4. `atom_handler`: A function that is called when an atom is parsed.
   This function is passed a string that consists of the text of the parsed
   atom. The function can convert this string into something else and the
   returned value is used to construct the S-expression.
   For example, this allows for converting digit sequences into ints.
