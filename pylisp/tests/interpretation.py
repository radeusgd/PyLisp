import pytest

from pylisp.errors import LispError
from pylisp.interpreter import interpret, represent_code, Symbol
from pylisp.builtins import builtins
from pylisp.environment import environment_with_builtins
from pylisp.parser import Parser


def parse_and_run(code):
    par = Parser()
    ast = par.parse_expr(code)
    data = represent_code(ast)
    return interpret(data, environment_with_builtins(builtins))


def test_lit():
    assert parse_and_run("2") == 2
    assert parse_and_run('"abc"') == "abc"
    assert parse_and_run("'a") == Symbol("a")


def test_let():
    with pytest.raises(LispError):
        parse_and_run("a")
    assert parse_and_run("(let (a 42) a)") == 42
    assert parse_and_run("(let (id (fun (x) x)) (id 33))") == 33


def test_define():
    assert parse_and_run("(begin (define! a 2) a)") == 2


def test_ops():
    assert parse_and_run("(+ 1 2 3)") == 6
    assert parse_and_run("(- 2 4)") == -2
    assert parse_and_run("(* 2 4)") == 8
    assert parse_and_run("(/ 4 2)") == 2
    with pytest.raises(LispError):
        parse_and_run("(/ 4 0)")


def test_list():
    assert parse_and_run("(str nil)") == "()"
    assert parse_and_run("(str (cons 2 3))") == "(2 . 3)"
    assert parse_and_run("(str (cons 2 nil))") == "(2)"
    assert parse_and_run("(str '(1 2 3))") == "(1 2 3)"
    assert parse_and_run("(str (list 2 3))") == "(2 3)"


def test_recursive():
    factorial_code = \
        "(letrec ((fact (fun (n) (if (= n 0) 1 (* n (fact (- n 1))))))) (fact 5))"
    assert parse_and_run(factorial_code) == 120
    even_code = \
        "(letrec (" \
        "   (not (fun (b) (if b false true)))" \
        "   (even (fun (n) (if (= n 0) true (not (even (- n 1))))))" \
        ") (even 8))"
    assert parse_and_run(even_code)


def test_binding():
    code1 = "(let (a 2) (let (f (fun () a)) (let (a 3) (f))))"
    assert parse_and_run(code1) == 2

    code2 = "(begin (define! a 2) (define! f (fun () a)) (define! a 3) (f))"
    assert parse_and_run(code2) == 2