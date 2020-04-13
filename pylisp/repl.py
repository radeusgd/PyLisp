from traceback import print_exc

from parsy import ParseError

from pylisp.environment import environment_with_builtins
from pylisp.builtins import builtins
from pylisp.errors import LispError
from pylisp.interpreter import represent_code, interpret, lisp_data_to_str
from pylisp.parser import Parser

class Repl:
    def __init__(self):
        self.parser = Parser()
        self.env = environment_with_builtins(builtins)

    def eval(self, code: str):
        try:
            ast = self.parser.parse_expr(code)
            code = represent_code(ast)
            print(lisp_data_to_str(code))
            res = interpret(code, self.env)
            print(lisp_data_to_str(res))
        except LispError as e:
            print("Runtime error:", e)
        except ParseError as e:
            print("Parse error:", e)

    def run(self):
        while True:
            try:
                line = input("> ")
            except EOFError:
                return

            if line == ":q":
                return
            self.eval(line)
