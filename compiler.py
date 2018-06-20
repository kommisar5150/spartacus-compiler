#!/usr/bin/env python

from constants import ACCEPTED_TYPES, \
                      OPERATORS

class CompilerTest:
    """
    STATE 0 = Function declaration
    STATE 1 = Within function, reset to 0 upon }
    """
    state = 0
    mathFormula = ""
    memoryLocation = 0x40000000
    varList = []
    varValues = {}
    varLocation = {}
    methodList = {}
    methodVars = {}
    expectedChar = ""
    currentType = ""
    currentVariable = ""
    expectedFlag = 0


    def parseText(self, text):

        file = open(text, mode="r")
        line = file.readlines()
        output = open("output.txt", mode="w")
        for x in line:
            self.readLine(x, output)

    def readLine(self, line, output):

        self.parseMethodHeader(line)

    def parseMethodHeader(self, line):

        for char in line:

            if self.state == 0:
                if char == " ":
                    pass
                else:
                    self.currentType += char
                    self.state = 1

            elif self.state == 1:
                if char == " ":
                    self.state = 2
                else:
                    self.currentType += char

            elif self.state == 2:
                # int
                if char == " " and self.expectedFlag == 0:
                    pass
                elif char == " " and self.expectedFlag == 1:
                    self.state = 3
                    self.expectedFlag = 0
                    self.methodList[self.currentVariable] = self.currentType
                elif char == "(" and self.expectedFlag == 1:
                    self.state = 3
                    self.methodList[self.currentVariable] = self.currentType
                else:
                    self.currentVariable += char
                    self.expectedFlag = 1

            elif self.state == 3:
                # int main(
                if char == " " and self.expectedFlag == 0:
                    pass
                elif char == "(" and self.expectedFlag == 0:
                    self.expectedFlag = 1
                elif char == " " and self.expectedFlag == 1:
                    self.state = 4
                    self.expectedFlag = 0
                else:
                    self.currentType += char

            elif self.state == 4:
                # int main( int
                if char == " " and self.expectedFlag == 0:
                    pass
                elif char == " " and self.expectedFlag == 1:
                    self.state = 5
                    self.expectedFlag = 0
                elif char == "," and self.expectedFlag == 1:
                    self.expectedFlag = 2
                elif char == ")" and self.expectedFlag == 1:
                    self.state = 7
                elif char == " " and self.expectedFlag == 2:
                    pass
                elif self.expectedFlag == 2:
                    self.currentType += char
                    self.state = 3
                    self.expectedFlag = 1
                else:
                    self.currentVariable += char
                    self.expectedFlag = 1

            elif self.state == 5:
                if char == " " and self.expectedFlag == 0:
                    pass
                elif char == "," and self.expectedFlag == 0:
                    self.expectedFlag = 1
                elif char == ")":
                    self.state = 7