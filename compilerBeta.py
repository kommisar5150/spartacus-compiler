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
    currentMethod = ""
    argCount = 0
    currentType = ""
    currentVariable = ""


    def parseText(self, text):

        file = open(text, mode="r")
        lines = file.readlines()
        output = open("output.txt", mode="w")
        for x in lines:
            self.readLine(x, output)

    def readLine(self, line, output):

        line = line.split()

        for char in line:

            if self.state == 0:
                self.state0(char, output)

            elif self.state == 1:
                self.methodList[char] = {"retType": self.currentType}
                self.currentMethod = char
                output.write(char + ":\n")
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
                # method list dict will have, at the index of the specified method,
                # a list of all variables passed in as arguments (as a nested dict), which in turn
                # holds a tuple of its data type and order of appearance in the function call.
                self.methodList[self.currentMethod][char] = (self.currentType, self.argCount)
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
                print(self.argCount)
                self.methodList[self.currentMethod]["totalVars"] = self.argCount
                if char == "{":
                    self.state = 7
                    self.varList.clear()
                    if self.argCount > 0:
                        output.write("MOV $S2 $S\n")
                        output.write("SUB #" + str(self.argCount * 4 + 4) + " $S2\n")
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
                elif char in self.methodList[self.currentMethod]:
                    self.currentVariable = char
                    output.write("MOV $A2 $S2\n")
                    output.write("ADD #" + str(self.methodList[self.currentMethod][char][1] * 4 + 4) + " $A2\n")
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
                            output.write("MEMR [4] #" + str(self.varLocation[self.mathFormula]) + " $A\n")
                        elif self.mathFormula in self.methodList[self.currentMethod]:
                            output.write("MOV $B2 $S2\n")
                            output.write("ADD #" + str(self.methodList[self.currentMethod][self.mathFormula][1]*4+4)
                                                                                                         + " $B2\n")
                            output.write("MEMR [4] $B2 $A\n")
                        else:
                            output.write("MOV #" + self.mathFormula + " $A\n")
                        if self.currentVariable in self.methodList[self.currentMethod]:
                            output.write("MEMW [4] $A $A2\n")
                        else:
                            output.write("MEMW [4] $A #" + str(self.varLocation[self.currentVariable]) + "\n")
                    else:
                        tokens = tokenize(self.mathFormula)
                        postfix = infixToPostfix(tokens)
                        postfix = infixToPostfix(tokens)
                        evaluatePostfix(postfix, self.varList, self.varLocation,
                                        self.methodList[self.currentMethod], output)

                        if self.currentVariable in self.methodList[self.currentMethod]:
                            output.write("MEMW [4] $A $A2\n")
                        else:
                            output.write("MEMW [4] $A #" + str(self.varLocation[self.currentVariable]) + "\n")

                    self.state = 7
                else:
                    self.mathFormula += str(char)
                    self.argCount += 1

            elif self.state == 11:
                self.argCount = 0
                if char == "(":
                    self.state = 12
                else:
                    raise ValueError("Incorrect syntax.")

            elif self.state == 12:
                if char in self.varList:
                    output.write("PUSH #" + str(self.varLocation[char]) + "\n")
                    self.state = 13
                    self.argCount += 1
                elif char in self.methodList[self.currentMethod]:
                    output.write("MOV $A2 $S2")
                    output.write("ADD #" + str(self.methodList[self.currentMethod][char][1] * 4 + 4) + " $A2\n")
                    output.write("PUSH $A\n")
                    self.state = 13
                    self.argCount += 1
                elif char == ")":
                    self.state = 15

            elif self.state == 13:
                if char == ",":
                    self.state = 14
                elif char == ")":
                    self.state = 15

            elif self.state == 14:
                if char in self.varList:
                    output.write("PUSH #" + str(self.varLocation[char]) + "\n")
                    self.state = 13
                    self.argCount += 1
                elif char in self.methodList[self.currentMethod]:
                    output.write("MOV $A2 $S2\n")
                    output.write("ADD #" + str(self.methodVars[self.currentMethod][char][1] * 4 + 4) + " $A2\n")
                    output.write("PUSH $A\n")
                    self.argCount += 1
                    self.state = 13

            elif self.state == 15:
                if char == ";":
                    if self.argCount == self.methodList[self.currentVariable]["totalVars"]:
                        output.write("CALL " + self.currentVariable + "\n")
                        self.state = 7
                    else:
                        raise ValueError("Arguments don't match function parameters.")

    def state0(self, char, output):
        if self.state == 0:
            self.varList.clear()
            self.varLocation.clear()
            if char in ACCEPTED_TYPES:
                self.currentType = char
                self.state = 1
            else:
                raise ValueError("incorrect data return type for method declaration.")