import sys
from antlr4 import *
from grammar.SSTLexer import SSTLexer
from grammar.SSTParser import SSTParser
from grammar.SSTListener import SSTListener

class MyListener(SSTListener):
	# Exit a parse tree produced by SSTParser#sst.
	def enterSst(self, ctx:SSTParser.SstContext):
		print("sst %s" % ctx)

	def enterProcedureDeclaration(self, ctx:SSTParser.ProcedureDeclarationContext):
		print("procDec %s" % ctx.IDENTIFIER())
		
	def enterDeclaration(self, ctx:SSTParser.SstContext):
		print("declaration %s" % ctx)


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