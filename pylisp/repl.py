from traceback import print_exc

from parsy import ParseError
from cmd import Cmd

from pylisp.environment import environment_with_builtins
from pylisp.builtins import builtins
from pylisp.errors import LispError
from pylisp.interpreter import represent_code, interpret, lisp_data_to_str
from pylisp.parser import Parser


class Repl(Cmd):
    def __init__(self, debug=False):
        super().__init__()
        self.parser = Parser()
        self.env = environment_with_builtins(builtins)
        self.prompt = "> "
        self._debug = debug

    def default(self, line):
        if line == "EOF":
            print("Bye!")
            return True
        try:
            ast = self.parser.parse_expr(line)
            code = represent_code(ast)
            res = interpret(code, self.env)
            if res is not None or self._debug:
                print(lisp_data_to_str(res))
        except LispError as e:
            if self._debug:
                print_exc()
            print("Runtime error:", e)
        except ParseError as e:
            print("Parse error:", e)

    def do_help(self, arg):
        print("Available builtins are:", " ".join(builtins.keys()))

