import sys
from traceback import print_exc

from pylisp.environment import empty_environment
from pylisp.interpreter import Interpreter
from pylisp.parser import Parser


class Repl(object):
    def __init__(self):
        self.parser = Parser()
        self.interpreter = Interpreter()

    def eval(self, code: str):
        try:
            term = self.parser.parse_expr(code)
            print(term)
            res = self.interpreter.interpret(term, empty_environment())
            print(res)
        except BaseException:  # TODO narrow down exception handling
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
