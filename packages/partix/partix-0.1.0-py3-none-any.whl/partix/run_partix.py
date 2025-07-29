from antlr4 import *
from PartixLexer import PartixLexer
from PartixParser import PartixParser
from antlr4.tree.Tree import ParseTreeWalker
from PartixEvalListener import PartixEvalListener

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