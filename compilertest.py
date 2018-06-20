#!/usr/bin/env python

from mathParser import evaluatePostfix, \
                       infixToPostfix, \
                       tokenize


def main():
    varValues = {"b": "10", "d": "2"}
    varLocation = {"a": "0x40000000", "b": "0x40000004", "c": "0x40000008", "d": "0x4000000C"}
    expression = " a * b * (a + c) - ( 4 / 2 ) + (b * a + 4) + 4"
    methodVars = {"a": "0", "c": "1"}
    tokenized = tokenize(expression)
    postfix = infixToPostfix(tokenized)
    print (postfix)
    result = evaluatePostfix(postfix, varValues, varLocation, methodVars)

if __name__ == '__main__':
    main()
