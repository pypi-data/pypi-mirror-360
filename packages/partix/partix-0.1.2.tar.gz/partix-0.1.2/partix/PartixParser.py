# Generated from Partix.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *

import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,13,40,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,1,0,4,0,10,8,0,11,0,12,
        0,11,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,
        28,8,1,1,2,1,2,1,2,5,2,33,8,2,10,2,12,2,36,9,2,1,3,1,3,1,3,0,0,4,
        0,2,4,6,0,1,1,0,8,10,39,0,9,1,0,0,0,2,27,1,0,0,0,4,29,1,0,0,0,6,
        37,1,0,0,0,8,10,3,2,1,0,9,8,1,0,0,0,10,11,1,0,0,0,11,9,1,0,0,0,11,
        12,1,0,0,0,12,13,1,0,0,0,13,14,5,0,0,1,14,1,1,0,0,0,15,16,5,4,0,
        0,16,17,5,1,0,0,17,18,5,7,0,0,18,19,5,2,0,0,19,28,3,2,1,0,20,21,
        5,3,0,0,21,22,5,5,0,0,22,23,5,8,0,0,23,28,3,4,2,0,24,25,5,5,0,0,
        25,26,5,8,0,0,26,28,3,4,2,0,27,15,1,0,0,0,27,20,1,0,0,0,27,24,1,
        0,0,0,28,3,1,0,0,0,29,34,3,6,3,0,30,31,5,6,0,0,31,33,3,6,3,0,32,
        30,1,0,0,0,33,36,1,0,0,0,34,32,1,0,0,0,34,35,1,0,0,0,35,5,1,0,0,
        0,36,34,1,0,0,0,37,38,7,0,0,0,38,7,1,0,0,0,3,11,27,34
    ]

class PartixParser ( Parser ):

    grammarFileName = "Partix.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'('", "')'", "'meta'", "'pass'", "'@'", 
                     "'+'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "META", "PASS", 
                      "AT", "CONCAT", "ENUM", "ID", "STRING", "MULTILINE_STRING", 
                      "LINE_COMMENT", "BLOCK_COMMENT", "WS" ]

    RULE_block = 0
    RULE_stmt = 1
    RULE_value = 2
    RULE_atom = 3

    ruleNames =  [ "block", "stmt", "value", "atom" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    META=3
    PASS=4
    AT=5
    CONCAT=6
    ENUM=7
    ID=8
    STRING=9
    MULTILINE_STRING=10
    LINE_COMMENT=11
    BLOCK_COMMENT=12
    WS=13

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class BlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(PartixParser.EOF, 0)

        def stmt(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PartixParser.StmtContext)
            else:
                return self.getTypedRuleContext(PartixParser.StmtContext,i)


        def getRuleIndex(self):
            return PartixParser.RULE_block

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBlock" ):
                listener.enterBlock(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBlock" ):
                listener.exitBlock(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBlock" ):
                return visitor.visitBlock(self)
            else:
                return visitor.visitChildren(self)




    def block(self):

        localctx = PartixParser.BlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_block)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 9 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 8
                self.stmt()
                self.state = 11 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 56) != 0)):
                    break

            self.state = 13
            self.match(PartixParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return PartixParser.RULE_stmt

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class Meta_stmtContext(StmtContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PartixParser.StmtContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def META(self):
            return self.getToken(PartixParser.META, 0)
        def AT(self):
            return self.getToken(PartixParser.AT, 0)
        def ID(self):
            return self.getToken(PartixParser.ID, 0)
        def value(self):
            return self.getTypedRuleContext(PartixParser.ValueContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMeta_stmt" ):
                listener.enterMeta_stmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMeta_stmt" ):
                listener.exitMeta_stmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMeta_stmt" ):
                return visitor.visitMeta_stmt(self)
            else:
                return visitor.visitChildren(self)


    class Pass_stmtContext(StmtContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PartixParser.StmtContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def PASS(self):
            return self.getToken(PartixParser.PASS, 0)
        def ENUM(self):
            return self.getToken(PartixParser.ENUM, 0)
        def stmt(self):
            return self.getTypedRuleContext(PartixParser.StmtContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPass_stmt" ):
                listener.enterPass_stmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPass_stmt" ):
                listener.exitPass_stmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPass_stmt" ):
                return visitor.visitPass_stmt(self)
            else:
                return visitor.visitChildren(self)


    class Normal_stmtContext(StmtContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PartixParser.StmtContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def AT(self):
            return self.getToken(PartixParser.AT, 0)
        def ID(self):
            return self.getToken(PartixParser.ID, 0)
        def value(self):
            return self.getTypedRuleContext(PartixParser.ValueContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNormal_stmt" ):
                listener.enterNormal_stmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNormal_stmt" ):
                listener.exitNormal_stmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNormal_stmt" ):
                return visitor.visitNormal_stmt(self)
            else:
                return visitor.visitChildren(self)



    def stmt(self):

        localctx = PartixParser.StmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_stmt)
        try:
            self.state = 27
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [4]:
                localctx = PartixParser.Pass_stmtContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 15
                self.match(PartixParser.PASS)
                self.state = 16
                self.match(PartixParser.T__0)
                self.state = 17
                self.match(PartixParser.ENUM)
                self.state = 18
                self.match(PartixParser.T__1)
                self.state = 19
                self.stmt()
                pass
            elif token in [3]:
                localctx = PartixParser.Meta_stmtContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 20
                self.match(PartixParser.META)
                self.state = 21
                self.match(PartixParser.AT)
                self.state = 22
                self.match(PartixParser.ID)
                self.state = 23
                self.value()
                pass
            elif token in [5]:
                localctx = PartixParser.Normal_stmtContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 24
                self.match(PartixParser.AT)
                self.state = 25
                self.match(PartixParser.ID)
                self.state = 26
                self.value()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ValueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def atom(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PartixParser.AtomContext)
            else:
                return self.getTypedRuleContext(PartixParser.AtomContext,i)


        def CONCAT(self, i:int=None):
            if i is None:
                return self.getTokens(PartixParser.CONCAT)
            else:
                return self.getToken(PartixParser.CONCAT, i)

        def getRuleIndex(self):
            return PartixParser.RULE_value

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterValue" ):
                listener.enterValue(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitValue" ):
                listener.exitValue(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitValue" ):
                return visitor.visitValue(self)
            else:
                return visitor.visitChildren(self)




    def value(self):

        localctx = PartixParser.ValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_value)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 29
            self.atom()
            self.state = 34
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==6:
                self.state = 30
                self.match(PartixParser.CONCAT)
                self.state = 31
                self.atom()
                self.state = 36
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AtomContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(PartixParser.ID, 0)

        def STRING(self):
            return self.getToken(PartixParser.STRING, 0)

        def MULTILINE_STRING(self):
            return self.getToken(PartixParser.MULTILINE_STRING, 0)

        def getRuleIndex(self):
            return PartixParser.RULE_atom

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAtom" ):
                listener.enterAtom(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAtom" ):
                listener.exitAtom(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAtom" ):
                return visitor.visitAtom(self)
            else:
                return visitor.visitChildren(self)




    def atom(self):

        localctx = PartixParser.AtomContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_atom)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 37
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 1792) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





