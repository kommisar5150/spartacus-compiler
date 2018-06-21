#!/usr/bin/env python

from constants import ACCEPTED_TYPES, \
                      OPERATORS

from mathParser import tokenize, \
                       infixToPostfix, \
                       evaluatePostfix

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
    argCount = 0
    currentType = ""
    currentVariable = ""


    def parseText(self, text):

        file = open(text, mode="r")
        line = file.readlines()
        output = open("output.txt", mode="w")
        for x in line:
            self.readLine(x, output)

    def readLine(self, line, output):

        self.parseMethodHeader(line)

    def parseMethodHeader(self, line):

        line = line.split()

        for char in line:

            if self.state == 0:
                self.varList.clear()
                self.varLocation.clear()
                if char in ACCEPTED_TYPES:
                    self.currentType = char
                    self.state = 1
                else:
                    raise ValueError("incorrect data return type for method declaration.")

            elif self.state == 1:
                self.methodList[char] = self.currentType
                print(char + ":")
                self.state = 2

            elif self.state == 2:
                if char == "(":
                    self.state = 3
                else:
                    raise ValueError("Incorrect syntax.")

            elif self.state == 3:
                if char in ACCEPTED_TYPES:
                    self.currentType = char
                    self.state = 4
                elif char == ")":
                    self.state = 6
                else:
                    raise ValueError("incorrect data type for argument.")

            elif self.state == 4:
                self.methodVars[char] = self.currentType, self.argCount
                self.argCount += 1
                self.state = 5

            elif self.state == 5:
                if char == ",":
                    self.state = 3
                elif char == ")":
                    self.state = 6
                else:
                    raise ValueError("Incorrect syntax.")

            elif self.state == 6:
                if char == "{":
                    self.state = 7
                    if self.argCount > 0:
                        print("MOV $S2 $S")
                        print("SUB #" + str(self.argCount * 4) + " $S2")
                else:
                    raise ValueError("Incorrect syntax.")

            elif self.state == 7:
                self.argCount = 0
                self.mathFormula = ""
                if char in ACCEPTED_TYPES:
                    self.currentType = char
                    self.state = 8
                elif char in self.varList:
                    self.currentVariable = char
                    self.state = 9
                elif char in self.methodList:
                    self.currentVariable = char
                    self.state = 11
                elif char in self.methodVars:
                    self.currentVariable = char
                    print("MOV $A2 $S2")
                    print("ADD #" + str(self.methodVars[char][1] * 4) + " $A2")
                    self.state = 9
                elif char == "}":
                    self.state = 0

            elif self.state == 8:
                # int
                self.varList.append(char)
                self.varLocation[char] = self.memoryLocation
                self.memoryLocation += 4
                self.currentVariable = char
                self.state = 9

            elif self.state == 9:
                # int a / a
                if char == "=":
                    self.state = 10
                elif char == ";":
                    self.state = 7

            elif self.state == 10:
                if char == ";":
                    if self.argCount == 1:
                        if self.mathFormula in self.varList:
                            print("MEMR [4] #" + str(self.varLocation[self.mathFormula]) + " $A")
                        elif self.mathFormula in self.methodVars:
                            print("MOV $B2 $S2")
                            print("ADD #" + str(self.methodVars[self.mathFormula][1] * 4) + " $B2")
                            print("MEMR [4] $B2 $A")
                        else:
                            print("MOV #" + self.mathFormula + " $A")
                        if self.currentVariable in self.methodVars:
                            print("MEMW [4] $A $A2")
                        else:
                            print("MEMW [4] $A #" + str(self.varLocation[self.currentVariable]))
                    else:
                        tokens = tokenize(self.mathFormula)
                        postfix = infixToPostfix(tokens)
                        evaluatePostfix(postfix, self.varList, self.varLocation, self.methodVars)
                        if self.currentVariable in self.methodVars:
                            print("MEMW [4] $A $A2")
                        else:
                            print("MEMW [4] $A #" + str(self.varLocation[self.currentVariable]))

                    self.state = 7
                else:
                    self.mathFormula += str(char)
                    self.argCount += 1

            elif self.state == 11:
                if char == "(":
                    self.state = 12
                else:
                    raise ValueError("Incorrect syntax.")

            elif self.state == 12:
                if char in self.varList:
                    print("PUSH #" + str(self.varLocation[char]))
                    self.state = 13
                elif char in self.methodVars:
                    print("MOV $A2 $S2")
                    print("ADD #" + str(self.methodVars[char][1] * 4) + " $A2")
                    print("PUSH $A")
                    self.state =13
                elif char == ")":
                    self.state = 15

            elif self.state == 13:
                if char == ",":
                    self.state = 14
                elif char == ")":
                    self.state = 15

            elif self.state == 14:
                if char in self.varList:
                    print("PUSH #" + str(self.varLocation[char]))
                    self.state = 13
                elif char in self.methodVars:
                    print("MOV $A2 $S2")
                    print("ADD #" + str(self.methodVars[char][1] * 4) + " $A2")
                    print("PUSH $A")
                    self.state = 13

            elif self.state == 15:
                if char == ";":
                    print("CALL " + self.currentVariable)
                    self.state = 7
