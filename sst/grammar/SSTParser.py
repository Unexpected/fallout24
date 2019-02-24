# Generated from grammar/SST.g4 by ANTLR 4.7.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\13")
        buf.write("\36\4\2\t\2\4\3\t\3\4\4\t\4\3\2\3\2\3\2\6\2\f\n\2\r\2")
        buf.write("\16\2\r\3\2\3\2\3\3\3\3\5\3\24\n\3\3\3\3\3\3\4\3\4\5\4")
        buf.write("\32\n\4\3\4\3\4\3\4\2\2\5\2\4\6\2\2\2\37\2\13\3\2\2\2")
        buf.write("\4\21\3\2\2\2\6\27\3\2\2\2\b\f\5\6\4\2\t\f\7\t\2\2\n\f")
        buf.write("\7\b\2\2\13\b\3\2\2\2\13\t\3\2\2\2\13\n\3\2\2\2\f\r\3")
        buf.write("\2\2\2\r\13\3\2\2\2\r\16\3\2\2\2\16\17\3\2\2\2\17\20\7")
        buf.write("\2\2\3\20\3\3\2\2\2\21\23\7\3\2\2\22\24\7\6\2\2\23\22")
        buf.write("\3\2\2\2\23\24\3\2\2\2\24\25\3\2\2\2\25\26\7\5\2\2\26")
        buf.write("\5\3\2\2\2\27\31\5\4\3\2\30\32\7\6\2\2\31\30\3\2\2\2\31")
        buf.write("\32\3\2\2\2\32\33\3\2\2\2\33\34\7\4\2\2\34\7\3\2\2\2\6")
        buf.write("\13\r\23\31")
        return buf.getvalue()


class SSTParser ( Parser ):

    grammarFileName = "SST.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'procedure'", "';'" ]

    symbolicNames = [ "<INVALID>", "PROCEDURE", "SEMICOLON", "IDENTIFIER", 
                      "WS", "NL", "NonCode", "Directive", "BlockComment", 
                      "LineComment" ]

    RULE_sst = 0
    RULE_procedureDeclaration = 1
    RULE_declaration = 2

    ruleNames =  [ "sst", "procedureDeclaration", "declaration" ]

    EOF = Token.EOF
    PROCEDURE=1
    SEMICOLON=2
    IDENTIFIER=3
    WS=4
    NL=5
    NonCode=6
    Directive=7
    BlockComment=8
    LineComment=9

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.7.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class SstContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(SSTParser.EOF, 0)

        def declaration(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SSTParser.DeclarationContext)
            else:
                return self.getTypedRuleContext(SSTParser.DeclarationContext,i)


        def Directive(self, i:int=None):
            if i is None:
                return self.getTokens(SSTParser.Directive)
            else:
                return self.getToken(SSTParser.Directive, i)

        def NonCode(self, i:int=None):
            if i is None:
                return self.getTokens(SSTParser.NonCode)
            else:
                return self.getToken(SSTParser.NonCode, i)

        def getRuleIndex(self):
            return SSTParser.RULE_sst

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSst" ):
                listener.enterSst(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSst" ):
                listener.exitSst(self)




    def sst(self):

        localctx = SSTParser.SstContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_sst)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 9 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 9
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [SSTParser.PROCEDURE]:
                    self.state = 6
                    self.declaration()
                    pass
                elif token in [SSTParser.Directive]:
                    self.state = 7
                    self.match(SSTParser.Directive)
                    pass
                elif token in [SSTParser.NonCode]:
                    self.state = 8
                    self.match(SSTParser.NonCode)
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 11 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << SSTParser.PROCEDURE) | (1 << SSTParser.NonCode) | (1 << SSTParser.Directive))) != 0)):
                    break

            self.state = 13
            self.match(SSTParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ProcedureDeclarationContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PROCEDURE(self):
            return self.getToken(SSTParser.PROCEDURE, 0)

        def IDENTIFIER(self):
            return self.getToken(SSTParser.IDENTIFIER, 0)

        def WS(self):
            return self.getToken(SSTParser.WS, 0)

        def getRuleIndex(self):
            return SSTParser.RULE_procedureDeclaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProcedureDeclaration" ):
                listener.enterProcedureDeclaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProcedureDeclaration" ):
                listener.exitProcedureDeclaration(self)




    def procedureDeclaration(self):

        localctx = SSTParser.ProcedureDeclarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_procedureDeclaration)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 15
            self.match(SSTParser.PROCEDURE)
            self.state = 17
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==SSTParser.WS:
                self.state = 16
                self.match(SSTParser.WS)


            self.state = 19
            self.match(SSTParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DeclarationContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def procedureDeclaration(self):
            return self.getTypedRuleContext(SSTParser.ProcedureDeclarationContext,0)


        def SEMICOLON(self):
            return self.getToken(SSTParser.SEMICOLON, 0)

        def WS(self):
            return self.getToken(SSTParser.WS, 0)

        def getRuleIndex(self):
            return SSTParser.RULE_declaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDeclaration" ):
                listener.enterDeclaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDeclaration" ):
                listener.exitDeclaration(self)




    def declaration(self):

        localctx = SSTParser.DeclarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_declaration)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 21
            self.procedureDeclaration()
            self.state = 23
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==SSTParser.WS:
                self.state = 22
                self.match(SSTParser.WS)


            self.state = 25
            self.match(SSTParser.SEMICOLON)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





