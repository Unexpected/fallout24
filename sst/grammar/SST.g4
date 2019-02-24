// Define a grammar for SST files

grammar SST;

sst	: ( declaration 
		| Directive
		| NonCode)+ EOF;
	
PROCEDURE: 'procedure';
SEMICOLON: ';';

IDENTIFIER: ([a-z] | '_')+;
WS: (' ' | '\t')+ -> skip;
NL: ('\r\n' | '\r' '\n'? | '\n') -> skip;

procedureDeclaration: PROCEDURE WS? IDENTIFIER;
declaration: procedureDeclaration WS? SEMICOLON;



NonCode: (WS | NL | BlockComment | LineComment)+;


Directive
	:	('#include' ()*? ~[\r\n]*
    |   '#define' ()*? ~[\r\n]*)
	-> skip
    ;

BlockComment
   : '/*' .*? '*/' 
   -> skip
   ;
LineComment
   : '//' ~ [\r\n]* 
   -> skip
   ;