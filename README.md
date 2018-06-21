## C compiler for Capua ASM conversion

I know very little about compilers, so I'm just designing this the way it makes sense in my head. 
Current functionality for the compiler will be limited to the following options:
* Variable declaration
* Variable assignment (only integers, and function calls may only be used on their own as a single operand)
* Function calls
* Return statements (arithmetic operations also allowed for return statements)
* Mathematical function evaluation (limited to 4-5 operands until I can figure out how to extend this)
* If statements
* While loops

The way I'm organizing the compiler as a 2nd year co-op student is by using a finite state machine model. The input determines which 
"state" the compiler is in to determine the next appropriate action. For the beta of this compiler, I'm enforcing the C code to be
written with spaces between each relevant token.

```
int main ( ) {
    int a = 5 ;
    int b = 10 ;
    int c = add ( a , b ) ;
    return 0 ;

```

It's a very noobish approach, but it works for now. Any suggestions are welcome. 

## Mathematical expression parsing

The compiler will make use of a simple infix/postfix algorithm to evaluate mathematical
expressions. It only supports integer operations, and variables/integers as operands. It does not
currently accept function calls within an expression.

**infix : a * 4 + ( b / 5) * 2 + 4 **

**postfix : a 4 * b 5 / 2 * + 4 + **

The postfix notation is easier to evaluate, and can be converted to Capua ASM code using a stack. 
