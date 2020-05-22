import sys
from antlr4 import *
from grammar.SSTLexer import SSTLexer
from grammar.SSTParser import SSTParser
from grammar.SSTListener import SSTListener

class MyListener(SSTListener):
	# Exit a parse tree produced by SSTParser#sst.
	def enterProcedureDeclaration(self, ctx:SSTParser.ProcedureDeclarationContext):
		pass #print("procDec %s" % ctx.Identifier())
	
	def enterVariableDeclaration(self, ctx:SSTParser.VariableDeclarationContext):
		pass #print("varDec %s := %s" % (ctx.Identifier(), ctx.initializer()))
		
	def enterDirective(self, ctx:SSTParser.DirectiveContext):
		pass #print("directive %s %s %s" % (ctx.children[0], ctx.children[1], "" if len(ctx.children) < 3 else ctx.children[2]))


def main(argv):
	input = FileStream(argv[1])
	lexer = SSTLexer(input)
	stream = CommonTokenStream(lexer)
	parser = SSTParser(stream)
	tree = parser.sst()
	walker = ParseTreeWalker()
	walker.walk(MyListener(), tree)
 
if __name__ == '__main__':
	main(sys.argv)