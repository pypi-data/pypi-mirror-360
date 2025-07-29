from antlr4 import *
from antlr4.tree.Tree import ParseTreeWalker
from .preprocessor import preprocess
from .PartixLexer import PartixLexer
from .PartixParser import PartixParser
from .PartixEvalListener import PartixEvalListener


def run(program):
    input_stream = InputStream(program)

    lexer = PartixLexer(input_stream)
    stream = CommonTokenStream(lexer)

    parser = PartixParser(stream)
    tree = parser.block()

    listener = PartixEvalListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)

    return listener.get_jsons()

def run_ptx_file(ptx_file):
    with open(ptx_file, "r", encoding="utf-8") as f:
        program = f.read()
    blocks = preprocess(program)
    i = 1
    for block in blocks:
        print(f"----------Block{i}----------")
        meta, passed, normal = run(block)
        print(meta)
        print(passed)
        print(normal)
        i += 1