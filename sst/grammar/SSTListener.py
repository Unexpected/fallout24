# Generated from grammar/SST.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .SSTParser import SSTParser
else:
    from SSTParser import SSTParser

# This class defines a complete listener for a parse tree produced by SSTParser.
class SSTListener(ParseTreeListener):

    # Enter a parse tree produced by SSTParser#sst.
    def enterSst(self, ctx:SSTParser.SstContext):
        pass

    # Exit a parse tree produced by SSTParser#sst.
    def exitSst(self, ctx:SSTParser.SstContext):
        pass


    # Enter a parse tree produced by SSTParser#procedureDeclaration.
    def enterProcedureDeclaration(self, ctx:SSTParser.ProcedureDeclarationContext):
        pass

    # Exit a parse tree produced by SSTParser#procedureDeclaration.
    def exitProcedureDeclaration(self, ctx:SSTParser.ProcedureDeclarationContext):
        pass


    # Enter a parse tree produced by SSTParser#declaration.
    def enterDeclaration(self, ctx:SSTParser.DeclarationContext):
        pass

    # Exit a parse tree produced by SSTParser#declaration.
    def exitDeclaration(self, ctx:SSTParser.DeclarationContext):
        pass


