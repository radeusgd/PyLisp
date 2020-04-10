import sys
from traceback import print_exc

from pylisp.environment import environment_with_builtins
from pylisp.builtins import builtins
from pylisp.errors import LispError
from pylisp.interpreter import interpret
from pylisp.parser import Parser


class Repl:
    def __init__(self):
        self.parser = Parser()
        self.env = environment_with_builtins(builtins)

    def eval(self, code: str):
        try:
            term = self.parser.parse_expr(code)
            print(term)  # TODO remove debug
            res = interpret(term, self.env)
            print(res)
        except LispError:
            print_exc()

    def run(self):
        while True:
            try:
                line = input("> ")
            except EOFError:
                return

            if line == ":q":
                return
            self.eval(line)
