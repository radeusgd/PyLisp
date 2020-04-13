import argparse

from pylisp.repl import Repl
from pylisp.interpreter import interpret_file
from pylisp.builtins import builtins
from pylisp.environment import environment_with_builtins


def main():
    parser = argparse.ArgumentParser(description='PyLisp interpreter')
    parser.add_argument('prog', nargs="?",
                        default="",
                        help='program to run (if not specified, launches a REPL)')

    args = parser.parse_args()
    if args.prog == "":
        Repl(debug=True).cmdloop()
    else:
        with open(args.prog) as f:
            interpret_file(f, environment_with_builtins(builtins))


if __name__ == "__main__":
    main()
