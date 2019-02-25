// Define a grammar for SST files

grammar SST;

sst
	: (declaration
	| procedureBlock)+
	EOF
	;

declaration
	: (variableDeclaration
	| procedureDeclaration
	| directive)
	;

variableDeclaration
	: Variable Identifier initializer? Semicolon
	;
	
procedureDeclaration
	: Procedure Identifier Semicolon
	;

directive
	: Sharp 
	(Include StringLiteral
	| Define Identifier Whitespace?
		(Identifier | LeftParenthesis Constant RightParenthesis)
	)
	; 

statements
	: statement*
	;

functionStatement
	: functionCall Semicolon
	;

specialInstruction
	: ('Flee_From_Dude'
	| 'GetReaction' Semicolon
	| 'end_dialogue' Semicolon
	| 'inc_good_critter'
	| 'script_overrides' Semicolon)
	;

callStatement
	: Call Identifier Semicolon
	;

specialBlock
	: 'gSay_Start' Semicolon statements 'gSay_End' Semicolon
	;
	
imperativeStatement
	: (assignementStatement
	| functionStatement
	| callStatement
	| specialInstruction)
	;
	
statement
	: (specialBlock
	| conditionStatement
	| imperativeStatement);

comparator
	: ('==' | '<' | '>' | '<=' | '>=')
	;

parameters
	: expression? 
	( ',' expression)*
	;
	
functionCall
	: Identifier LeftParenthesis parameters RightParenthesis
	;

arithmeticExpression
	: arithmeticExpression '*' arithmeticExpression
	| arithmeticExpression '/' arithmeticExpression
	| arithmeticExpression '+' arithmeticExpression
	| arithmeticExpression '-' arithmeticExpression	
	| LeftParenthesis arithmeticExpression RightParenthesis
	| expression
	;

expression
	: (Identifier
	| Constant
	| functionCall)
	;
	
comparisonExpression
	: arithmeticExpression comparator arithmeticExpression
	;

booleanExpression
	: booleanExpression 'and' booleanExpression
	| booleanExpression 'or' booleanExpression
	| LeftParenthesis booleanExpression RightParenthesis
	| comparisonExpression
	| expression
	;
	
assignementStatement
	: Identifier AssignmentOperator Constant Semicolon
	;
	
conditionStatement
	: If LeftParenthesis booleanExpression RightParenthesis Then 
	( Begin statements End 
	| statement)
	( Else 
		(Begin statements End
		| statement)
	)?
	;
	
procedureBlock
	: Procedure Identifier Begin statements End
	;

initializer
	: AssignmentOperator Constant
	;

Variable: 'variable';	
Procedure: 'procedure';
Include: 'include';
Define: 'define';
Begin: 'begin';
End: 'end';
If: 'if';
Then: 'then';
Else: 'else';
Or: 'or';
And: 'and';
Call: 'call';

Semicolon: ';';
Double_quote: '"';
Sharp: '#';
LeftParenthesis: '(';
RightParenthesis: ')';
AssignmentOperator: ':=';
	
Identifier
    :   Nondigit
	(   Nondigit
	|   Digit
	)*
    ;

StringLiteral
    :   Double_quote SCharSequence? Double_quote
    ;

fragment
SCharSequence
    :   SChar+
    ;
	
fragment
SChar
    :   ~["\r\n]
    ;

fragment
Nondigit
    :   [a-zA-Z_]
    ;

fragment
Digit
    :   [0-9]
    ;

Constant
    :   IntegerConstant
    |   StringLiteral
    ;
fragment
IntegerConstant
    :   '-'? Digit+
    ;

Whitespace
    :   [ \t]+
        -> skip
    ;

Newline
    :   (   '\r' '\n'?
        |   '\n'
        )
        -> skip
    ;

BlockComment
    :   '/*' .*? '*/'
        -> skip
    ;

LineComment
    :   '//' ~[\r\n]*
        -> skip
    ;





