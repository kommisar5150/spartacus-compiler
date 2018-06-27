#!/usr/bin/env python

import re

ACCEPTED_TYPES = ["int", "void", "char"]
OPERATORS = ['+', '-', '*', '/']
BOOLEAN_OPERATORS = ["<", ">", "="]
IGNORE_CHARS = [" ", "\n"]
REGISTERS = {
    0: "A",
    1: "B",
    2: "C",
    3: "D",
    4: "E",
    5: "F",
    6: "G"
}
REGISTER_NAMES = ["A", "B", "C", "D", "E", "F", "G"]

L_PARENTHESES = '('
R_PARENTHESES = ')'
PLUS = '+'
MINUS = '-'
MULTIPLICATION = '*'
DIVISION = '/'

OPERATIONS = {
              PLUS: {'priority': 1, 'function': lambda a, b: a + b},
              MINUS: {'priority': 1, 'function': lambda a, b: a - b},
              MULTIPLICATION: {'priority': 2, 'function': lambda a, b: a * b},
              DIVISION: {'priority': 2, 'function': lambda a, b: a / b},
}

INSTRUCTIONS = {
                PLUS: "ADD",
                MINUS: "SUB",
                MULTIPLICATION: "MUL",
                DIVISION: "DIV"
}

TOKEN_SEPARATOR = re.compile(r'\s*(%s|%s|%s|%s|%s|%s)\s*' % (
                  re.escape(L_PARENTHESES),
                  re.escape(R_PARENTHESES),
                  re.escape(PLUS),
                  re.escape(MINUS),
                  re.escape(MULTIPLICATION),
                  re.escape(DIVISION)))
