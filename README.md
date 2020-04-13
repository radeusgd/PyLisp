# PyLisp

A simple LISP interpreter in Python.

The LISP dialect implemented is my own variation on the language.

## Usage

To install run `pip install .`.

Usage: 
`pylisp` to launch REPL, `pylisp program.cl` to execute a script.

## Language
The language is mostly focused on functional aspects, but it has some imperative structures.
It's eagerly executed and uses static binding in closures.

Syntax is usual to the LISP family, usable operators can be found in `pylisp/builtins.py`, some of them are:
let, letrec, define!, print!, fun, macro, quote, list, cons, nil, true, false, if, =.

To get the full list, type `help` in the REPL.
To get documentation of a builtin, type `(help! builtin)` (for example `(help! letrec)`) in the REPL.