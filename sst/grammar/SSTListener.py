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


    # Enter a parse tree produced by SSTParser#declaration.
    def enterDeclaration(self, ctx:SSTParser.DeclarationContext):
        pass

    # Exit a parse tree produced by SSTParser#declaration.
    def exitDeclaration(self, ctx:SSTParser.DeclarationContext):
        pass


    # Enter a parse tree produced by SSTParser#variableDeclaration.
    def enterVariableDeclaration(self, ctx:SSTParser.VariableDeclarationContext):
        pass

    # Exit a parse tree produced by SSTParser#variableDeclaration.
    def exitVariableDeclaration(self, ctx:SSTParser.VariableDeclarationContext):
        pass


    # Enter a parse tree produced by SSTParser#procedureDeclaration.
    def enterProcedureDeclaration(self, ctx:SSTParser.ProcedureDeclarationContext):
        pass

    # Exit a parse tree produced by SSTParser#procedureDeclaration.
    def exitProcedureDeclaration(self, ctx:SSTParser.ProcedureDeclarationContext):
        pass


    # Enter a parse tree produced by SSTParser#directive.
    def enterDirective(self, ctx:SSTParser.DirectiveContext):
        pass

    # Exit a parse tree produced by SSTParser#directive.
    def exitDirective(self, ctx:SSTParser.DirectiveContext):
        pass


    # Enter a parse tree produced by SSTParser#statements.
    def enterStatements(self, ctx:SSTParser.StatementsContext):
        pass

    # Exit a parse tree produced by SSTParser#statements.
    def exitStatements(self, ctx:SSTParser.StatementsContext):
        pass


    # Enter a parse tree produced by SSTParser#functionStatement.
    def enterFunctionStatement(self, ctx:SSTParser.FunctionStatementContext):
        pass

    # Exit a parse tree produced by SSTParser#functionStatement.
    def exitFunctionStatement(self, ctx:SSTParser.FunctionStatementContext):
        pass


    # Enter a parse tree produced by SSTParser#specialInstruction.
    def enterSpecialInstruction(self, ctx:SSTParser.SpecialInstructionContext):
        pass

    # Exit a parse tree produced by SSTParser#specialInstruction.
    def exitSpecialInstruction(self, ctx:SSTParser.SpecialInstructionContext):
        pass


    # Enter a parse tree produced by SSTParser#callStatement.
    def enterCallStatement(self, ctx:SSTParser.CallStatementContext):
        pass

    # Exit a parse tree produced by SSTParser#callStatement.
    def exitCallStatement(self, ctx:SSTParser.CallStatementContext):
        pass


    # Enter a parse tree produced by SSTParser#specialBlock.
    def enterSpecialBlock(self, ctx:SSTParser.SpecialBlockContext):
        pass

    # Exit a parse tree produced by SSTParser#specialBlock.
    def exitSpecialBlock(self, ctx:SSTParser.SpecialBlockContext):
        pass


    # Enter a parse tree produced by SSTParser#imperativeStatement.
    def enterImperativeStatement(self, ctx:SSTParser.ImperativeStatementContext):
        pass

    # Exit a parse tree produced by SSTParser#imperativeStatement.
    def exitImperativeStatement(self, ctx:SSTParser.ImperativeStatementContext):
        pass


    # Enter a parse tree produced by SSTParser#statement.
    def enterStatement(self, ctx:SSTParser.StatementContext):
        pass

    # Exit a parse tree produced by SSTParser#statement.
    def exitStatement(self, ctx:SSTParser.StatementContext):
        pass


    # Enter a parse tree produced by SSTParser#comparator.
    def enterComparator(self, ctx:SSTParser.ComparatorContext):
        pass

    # Exit a parse tree produced by SSTParser#comparator.
    def exitComparator(self, ctx:SSTParser.ComparatorContext):
        pass


    # Enter a parse tree produced by SSTParser#parameters.
    def enterParameters(self, ctx:SSTParser.ParametersContext):
        pass

    # Exit a parse tree produced by SSTParser#parameters.
    def exitParameters(self, ctx:SSTParser.ParametersContext):
        pass


    # Enter a parse tree produced by SSTParser#functionCall.
    def enterFunctionCall(self, ctx:SSTParser.FunctionCallContext):
        pass

    # Exit a parse tree produced by SSTParser#functionCall.
    def exitFunctionCall(self, ctx:SSTParser.FunctionCallContext):
        pass


    # Enter a parse tree produced by SSTParser#arithmeticExpression.
    def enterArithmeticExpression(self, ctx:SSTParser.ArithmeticExpressionContext):
        pass

    # Exit a parse tree produced by SSTParser#arithmeticExpression.
    def exitArithmeticExpression(self, ctx:SSTParser.ArithmeticExpressionContext):
        pass


    # Enter a parse tree produced by SSTParser#expression.
    def enterExpression(self, ctx:SSTParser.ExpressionContext):
        pass

    # Exit a parse tree produced by SSTParser#expression.
    def exitExpression(self, ctx:SSTParser.ExpressionContext):
        pass


    # Enter a parse tree produced by SSTParser#comparisonExpression.
    def enterComparisonExpression(self, ctx:SSTParser.ComparisonExpressionContext):
        pass

    # Exit a parse tree produced by SSTParser#comparisonExpression.
    def exitComparisonExpression(self, ctx:SSTParser.ComparisonExpressionContext):
        pass


    # Enter a parse tree produced by SSTParser#booleanExpression.
    def enterBooleanExpression(self, ctx:SSTParser.BooleanExpressionContext):
        pass

    # Exit a parse tree produced by SSTParser#booleanExpression.
    def exitBooleanExpression(self, ctx:SSTParser.BooleanExpressionContext):
        pass


    # Enter a parse tree produced by SSTParser#assignementStatement.
    def enterAssignementStatement(self, ctx:SSTParser.AssignementStatementContext):
        pass

    # Exit a parse tree produced by SSTParser#assignementStatement.
    def exitAssignementStatement(self, ctx:SSTParser.AssignementStatementContext):
        pass


    # Enter a parse tree produced by SSTParser#conditionStatement.
    def enterConditionStatement(self, ctx:SSTParser.ConditionStatementContext):
        pass

    # Exit a parse tree produced by SSTParser#conditionStatement.
    def exitConditionStatement(self, ctx:SSTParser.ConditionStatementContext):
        pass


    # Enter a parse tree produced by SSTParser#procedureBlock.
    def enterProcedureBlock(self, ctx:SSTParser.ProcedureBlockContext):
        pass

    # Exit a parse tree produced by SSTParser#procedureBlock.
    def exitProcedureBlock(self, ctx:SSTParser.ProcedureBlockContext):
        pass


    # Enter a parse tree produced by SSTParser#initializer.
    def enterInitializer(self, ctx:SSTParser.InitializerContext):
        pass

    # Exit a parse tree produced by SSTParser#initializer.
    def exitInitializer(self, ctx:SSTParser.InitializerContext):
        pass


