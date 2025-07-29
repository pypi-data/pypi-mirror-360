# Generated from Partix.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .PartixParser import PartixParser
else:
    from .PartixParser import PartixParser

# This class defines a complete listener for a parse tree produced by PartixParser.
class PartixListener(ParseTreeListener):

    # Enter a parse tree produced by PartixParser#block.
    def enterBlock(self, ctx:PartixParser.BlockContext):
        pass

    # Exit a parse tree produced by PartixParser#block.
    def exitBlock(self, ctx:PartixParser.BlockContext):
        pass


    # Enter a parse tree produced by PartixParser#pass_stmt.
    def enterPass_stmt(self, ctx:PartixParser.Pass_stmtContext):
        pass

    # Exit a parse tree produced by PartixParser#pass_stmt.
    def exitPass_stmt(self, ctx:PartixParser.Pass_stmtContext):
        pass


    # Enter a parse tree produced by PartixParser#meta_stmt.
    def enterMeta_stmt(self, ctx:PartixParser.Meta_stmtContext):
        pass

    # Exit a parse tree produced by PartixParser#meta_stmt.
    def exitMeta_stmt(self, ctx:PartixParser.Meta_stmtContext):
        pass


    # Enter a parse tree produced by PartixParser#normal_stmt.
    def enterNormal_stmt(self, ctx:PartixParser.Normal_stmtContext):
        pass

    # Exit a parse tree produced by PartixParser#normal_stmt.
    def exitNormal_stmt(self, ctx:PartixParser.Normal_stmtContext):
        pass


    # Enter a parse tree produced by PartixParser#value.
    def enterValue(self, ctx:PartixParser.ValueContext):
        pass

    # Exit a parse tree produced by PartixParser#value.
    def exitValue(self, ctx:PartixParser.ValueContext):
        pass


    # Enter a parse tree produced by PartixParser#atom.
    def enterAtom(self, ctx:PartixParser.AtomContext):
        pass

    # Exit a parse tree produced by PartixParser#atom.
    def exitAtom(self, ctx:PartixParser.AtomContext):
        pass



del PartixParser