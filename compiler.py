#!/usr/bin/env python

from constants import ACCEPTED_TYPES, \
                      IGNORE_CHARS
from mathParser import tokenize, \
                       infixToPostfix, \
                       evaluatePostfix

import re


class Compiler:

    state = 0                    # "States" are used to determine our next path for processing the C file
    currentVar = ""              # Name of variable being evaluated
    currentType = ""             # Current data type being read, before method/variable declaration
    currentMethod = ""           # String containing the current method being evaluated
    expectFlag = 0               # Used to control what input we expect next
    mathFormula = ""             # Will contain our fully assembled math expressions for variable assignments
    memoryLocation = 0x40000000  # Memory location for local variables.
    varList = []                 # Contains a list of variable names
    varLocation = {}             # Contains the memory location for all variables
    methodList = {}              # List of methods, along with their return type, variables (and types), and # of args
    argCount = 0                 # Used for number of operands in math expression, args in function calls, etc.
    variableCount = 0            # Number of variables declared in current function.
    identifier = ""              # Used to determine first token of a line
    functionCall = ""            # Name of the function we're calling when doing variable assignment
    whileFlag = 0                # Lets the compiler know if we're in a while loop
    ifOperator = ""              # Holds the logical operator between two sides of an if boolean expression
    nestedFlag = 0               # Lets the compiler know if we're in an if statement
    ifLabel = 0                  # For jump instructions, we need a unique label for every if statement
    lineno = 0                   # Line number for printing error messages
    functionArg = ""             # Used to read a function call's arguments

    def parseText(self, text):
        """
        Initializes parsing process. Opens the input file to read from, and initializes the output file we will create.
        :param text: str, name of file to read from
        :return:
        """

        try:
            file = open(text, mode="r")
            inputFile = file.readlines()
        except OSError as e:
            raise OSError("Couldn't open file {}".format(text))
        try:
            output = open("output.casm", mode="w")
        except OSError as e:
            raise OSError("Couldn't open file {}".format(text))

        for line in inputFile:
            self.lineno += 1
            for x in line:
                self.parse(x, output)

        output.write("end:\n")

        try:
            file.close()
            output.close()
        except OSError as e:
            raise OSError("Couldn't close file.")

    def parse(self, char, output):
        if self.state == 0:
            self.state0(char, output)

        elif self.state == 1:
            self.state1(char, output)

        elif self.state == 2:
            self.state2(char, output)

        elif self.state == 3:
            self.state3(char, output)

        elif self.state == 4:
            self.state4(char, output)

        elif self.state == 5:
            self.state5(char, output)

        elif self.state == 6:
            self.state6(char, output)

        elif self.state == 7:
            self.state7(char, output)

        elif self.state == 8:
            self.state8(char, output)

    def state0(self, char, output):

        if char in IGNORE_CHARS and self.expectFlag == 0:
            pass
        elif char in IGNORE_CHARS and self.expectFlag == 1:
            if self.currentType in ACCEPTED_TYPES:
                self.state = 1
                self.expectFlag = 0
            else:
                print(self.currentType)
                raise ValueError("Incorrect return type for method declaration at line {}.".format(self.lineno))
        else:
            self.currentType += char
            self.expectFlag = 1

    def state1(self, char, output):
        if char == " " and self.expectFlag == 0:
            pass
        elif char == " " and self.expectFlag == 1:
            self.currentVar = ""
            self.currentType = ""
            self.state = 2
        elif char == "(":
            # We read the opening parentheses
            self.methodList[self.currentMethod] = {"retType": self.currentType}
            output.write(self.currentMethod + ":\n")
            self.currentVar = ""
            self.currentType = ""
            self.state = 2
            self.expectFlag = 0
        else:
            self.currentMethod += char
            self.expectFlag = 1

    def state2(self, char, output):
        """
        Deals with the first argument's data type.
        :param char:
        :param output:
        :return:
        """

        if char == " " and self.expectFlag == 1:
            # we have our method name and return type, but have not yet seen the opening bracket for arguments "("
            pass

        elif char == "(" and self.expectFlag == 1:
            # We have our opening parentheses for arguments, we can now look for the first variable's data type
            self.expectFlag = 0
            self.methodList[self.currentMethod] = {"retType": self.currentType}
            output.write(self.currentMethod + ":\n")
            if self.currentMethod == "main":
                output.write("    MOV end $S\n")

        elif self.expectFlag == 0:
            # Here we expect to read the first character of the variable's data type
            if char == ")":
                # If instead we simply read a closing parentheses, we assume there are no arguments.
                self.state = 4
            elif char == " ":
                # If we have a space, we have not yet seen the first char of the variable's data type.
                pass
            else:
                # We read the first character of the variable's data type
                self.currentType += char
                self.expectFlag = 2

        elif self.expectFlag == 2:
            # Here we read the remainder of the variable's data type. If we read a comma, there are other
            if char == ")":
                self.state = 4
                self.expectFlag = 0
            elif char == " ":
                # we need to read a space before our variable's name. Now we're ready to read the name itself.
                if self.currentType in ACCEPTED_TYPES:
                    self.state = 3
                    self.expectFlag = 0
                else:
                    raise ValueError("Data type not supported for method variable: {}.".format(self.currentType))
            else:

                # append the character to the current type being read.
                self.currentType += char

    def state3(self, char, output):
        """
        This state reads the name of a method argument.
        :param char:
        :param output:
        :return:
        """

        if self.expectFlag == 0 and char == " ":
            # Here we're still reading whitespace after variable's data type declaration
            pass

        elif self.expectFlag == 1 and char == " ":
            # We read the variable's name, now we wait for the next character to decide where to go
            self.addVariableToMethodDict()
            self.expectFlag = 2

        elif self.expectFlag == 1 and char == ",":
            # We read a comma immediately after variable name (no space), so we expect to read more variables
            self.addVariableToMethodDict()
            self.expectFlag = 3

        elif self.expectFlag == 1 and char == ")":
            # Closing parentheses right after variable name. We go to method's body
            self.addVariableToMethodDict()
            self.state = 4
            self.expectFlag = 0

        elif self.expectFlag == 2:
            # We've read a space after variable's name, now we wait for the next key character to know where to go
            if char == " ":
                pass
            elif char == ",":
                self.expectFlag = 3
            elif char == ")":
                self.state = 4
                self.expectFlag = 0
            else:
                raise ValueError("Syntax error at line {}.".format(self.lineno))

        elif self.expectFlag == 3:
            # After reading a comma, we either read the beginning of a new variable declaration, or some more whitespace
            if char == " ":
                pass
            else:
                self.currentType = char
                self.state = 2
                self.expectFlag = 2

        else:
            # append the character to the current variable's name
            self.currentVar += char
            self.expectFlag = 1

    def state4(self, char, output):
        """
        In this state, we've read all the arguments of a method declaration. Now we simply expect to read the opening
        curly brace "{" to signify the opening body of the method. Here, we also write the appropriate casm instructions
        to the output file. The stack pointer gets moved to "end" if it's the main method, and the S2 pointer must point
        to the first argument pushed to the stack (if any).
        :param char:
        :param output:
        :return:
        """

        self.expectFlag = 0

        if char in IGNORE_CHARS:
            pass

        elif char == "{":
            # We add the total amount of variables present in the method's argument list. Used for function calls
            # in the body of another method to ensure the correct amount of variables are passed in.
            self.methodList[self.currentMethod]["totalVars"] = self.argCount
            self.state = 5
            if self.currentMethod == "main":
                output.write("    MOV end $S\n")
            else:
                if self.argCount > 0:
                    output.write("    MOV $S $S2\n")
                    output.write("    SUB #" + str(self.argCount * 4 + 4) + " $S2\n")

            self.argCount = 0

        else:
            raise ValueError("Syntax error, expecting \"{\", got {}".format(char))

    def state5(self, char, output):
        """
        Initial evaluation of a line. We read the input and concatenate to identifier string. Once we read a key token,
        we check various cases to see where we need to go with out identifier:
        space:
            -valid data type
            -if statement (we later check for opening parentheses)
            -variable (already declared)
            -while loop
            -return statement
        "=":
            -variable assignment only
        "(":
            -if statement
            -while loop
            -function call (e.g. add(a,b))
            -return statement
        "}"
            -end of method, loop, or if statement

        :param char:
        :param output:
        :return:
        """

        if char in IGNORE_CHARS and self.expectFlag == 0:
            pass

        elif char == " " and self.expectFlag == 1:
            if self.identifier == "if":
                pass
            elif self.identifier == "while":
                pass
            elif self.identifier == "return":
                pass
            elif (self.identifier in self.varList) or self.identifier in self.methodList[self.currentMethod]:
                self.currentVar = self.identifier
                self.identifier = ""
                self.state = 6
                self.expectFlag = 2
            elif self.identifier in ACCEPTED_TYPES:
                self.currentType = self.identifier
                self.identifier = ""
                self.state = 6
                self.expectFlag = 0
            elif self.identifier in self.methodList:
                self.expectFlag = 0
                self.state = 8
                self.functionCall = self.identifier
                self.identifier = ""
            else:
                raise ValueError("Error at line {}".format(self.lineno))

        elif char == "=" and self.expectFlag == 1:
            pass

        elif char == "(" and self.expectFlag == 1:
            if self.identifier in self.methodList:
                self.state = 8
                self.functionCall = self.identifier
                self.identifier = ""

            elif self.identifier == "if":
                pass
            elif self.identifier == "while":
                pass
            elif self.identifier == "return":
                # add parentheses to math expression
                pass

        elif char == "}":
            # end of method, if statement, or while loop
            if self.nestedFlag == 0:
                self.state = 0

                output.write("    RET\n")
                self.currentMethod = ""
                self.argCount = 0
                self.currentVar = ""
                self.currentType = ""
                self.varList.clear()
                self.varLocation.clear()
            else:
                self.nestedFlag -= 1


        else:
            self.identifier += char
            self.expectFlag = 1

    def state6(self, char, output):
        """
        Initial variable name declaration.
        :param char:
        :param output:
        :return:
        """

        if char in IGNORE_CHARS and self.expectFlag == 0:
            # ignore spaces/new line chars if we're not expecting any input in particular
            pass

        elif char == " " and self.expectFlag == 1:
            # we have the variable name, now we move to the next phase to determine appropriate action
            self.expectFlag = 2

        elif char == "=" and self.expectFlag == 1:
            # we have the variable name, and we see that an assignment will happen
            self.verifyVariable()
            self.state = 7
            self.expectFlag = 0

        elif char == ";" and self.expectFlag == 1:
            # end of variable declaration. we assign its memory location and add it to the variable list
            self.verifyVariable()
            self.currentVar = ""
            self.currentType = ""
            self.state = 5
            self.expectFlag = 0

        elif self.expectFlag == 2:
            # We reach this step if we have the variable name and we read at least one space
            if char in IGNORE_CHARS:
                # we may keep reading spaces/ new line until we reach a relevant token
                pass

            elif char == "=":
                # variable assignment. if the variable was not in the list, we add it
                if (self.currentVar not in self.varList) and self.currentVar not in self.methodList[self.currentMethod]:
                    self.varList.append(self.currentVar)
                    self.varLocation[self.currentVar] = self.memoryLocation
                    self.memoryLocation += 4
                    self.variableCount += 1

                self.state = 7
                self.expectFlag = 0
            elif char == ";":
                self.verifyVariable()
                self.currentVar = ""
                self.currentType = ""
                self.state = 5
                self.expectFlag = 0

            else:
                raise ValueError("Incorrect syntax at line {}".format(self.lineno))

        else:
            self.currentVar += char
            self.expectFlag = 1

    def state7(self, char, output):
        """
        Begins variable assignment. This could either be a math formula, or a function call
        :param char:
        :param output:
        :return:
        """

        if char in IGNORE_CHARS and self.expectFlag == 0:
            pass

        elif char == "(" and self.expectFlag == 1:
            if self.mathFormula in self.methodList:
                self.functionCall = self.mathFormula
                self.state = 10
            else:
                self.mathFormula += char

        elif char == " " and self.expectFlag == 1:
            if self.mathFormula in self.methodList:
                self.functionCall = self.mathFormula
                self.state = 10
            else:
                self.mathFormula += char

        elif char == ";":
            # End of our math statement. We may begin the evaluation and assign the result to the current variable
            tokens = tokenize(self.mathFormula)
            postfix = infixToPostfix(tokens)
            evaluatePostfix(postfix, self.varList, self.varLocation, self.methodList[self.currentMethod], output)

            if self.currentVar in self.methodList[self.currentMethod]:
                # The variable is an argument passed into the function. We use the stack pointer to fetch its
                # location before writing the value.
                output.write("    MOV $A2 $S2\n")
                output.write("    ADD #" + str(self.methodList[self.currentMethod][self.currentVar][1] * 4)
                             + " $A2\n")
                output.write("    MEMW [4] $A $A2\n")

            else:
                # The variable is local, so we just write the result to its memory location from the local list.
                output.write("    MEMW [4] $A #" + str(self.varLocation[self.currentVar]) + "\n")

            # now we reset everything
            self.state = 5
            self.mathFormula = ""
            self.currentType = ""
            self.currentVar = ""
            self.expectFlag = 0

        else:
            self.mathFormula += char
            self.expectFlag = 1

    def state8(self, char, output):
        """
        This deals with a function call
        :param char:
        :param output:
        :return:
        """

        if char in IGNORE_CHARS and self.expectFlag == 0:
            pass

        elif char == "(" and self.expectFlag == 0:
            self.expectFlag = 1

        elif self.expectFlag == 1:
            if char in IGNORE_CHARS:
                pass
            else:
                self.functionArg += char
                self.expectFlag = 2

        elif self.expectFlag == 2:
            # Here we read the argument name. If we read a space, we wait for appropriate token.
            # Tokens ("," and ")") may show up without spaces, so we handle that here too
            if char == ",":
                if self.functionArg in self.varList:
                    output.write("    PUSH #" + str(self.varLocation[self.functionArg]) + "\n")
                else:
                    raise ValueError("Invalid variable at line {}".format(self.lineno))
                self.expectFlag = 1
                self.functionArg = ""
                self.argCount += 1

            elif char in IGNORE_CHARS:
                self.expectFlag = 3

            elif char == ")":
                if self.functionArg in self.varList:
                    output.write("    PUSH #" + str(self.varLocation[self.functionArg]) + "\n")
                else:
                    raise ValueError("Invalid variable at line {}".format(self.lineno))
                self.expectFlag = 4
                self.argCount += 1

            else:
                self.functionArg += char

        elif self.expectFlag == 3:
            # We fully read the argument name, now we wait for valid token
            if char == ",":
                if self.functionArg in self.varList:
                    output.write("    PUSH #" + str(self.varLocation[self.functionArg]) + "\n")
                else:
                    raise ValueError("Invalid variable at line {}".format(self.lineno))
                self.expectFlag = 1
                self.functionArg = ""
                self.argCount += 1

            elif char in IGNORE_CHARS:
                # we can keep ignoring whitespace/new line until we read a correct token
                pass
            elif char == ")":
                if self.functionArg in self.varList:
                    output.write("    PUSH #" + str(self.varLocation[self.functionArg]) + "\n")
                else:
                    raise ValueError("Invalid variable at line {}".format(self.lineno))
                self.expectFlag = 4
                self.argCount += 1
            else:
                raise ValueError("Error at line {}".format(self.lineno))

        elif self.expectFlag == 4:
            # Here we're done our function call. We need to read ";" to end the statement and write function to output
            if char == ";":
                output.write("    CALL " + self.functionCall + "\n")
                self.state = 5
                if self.currentVar != "":
                    output.write("    MEMW [4] $A #" + self.varLocation[self.currentVar] + "\n")
                self.functionCall = ""
                self.functionArg = ""
                self.argCount = 0
                output.write("    SUB #" + str(self.variableCount * 4) + " $S\n")

    def validName(self, name):
        """
        will eventually do a RE search for characters now allowed for variable/method names
        :param name:
        :return:
        """
        pass

    def verifyVariable(self):
        """
        Method checks whether the variable is already present in the list. If so, we raise an error since we can't have
        duplicate variable names. Otherwise, we add it to the list, assign it a memory location, increment the memory
        location counter, and increase the total variable count.
        :return:
        """

        if (self.currentVar not in self.varList) and self.currentVar not in self.methodList[self.currentMethod]:
            self.varList.append(self.currentVar)
            self.varLocation[self.currentVar] = self.memoryLocation
            self.memoryLocation += 4
            self.variableCount += 1
        else:
            # can't have duplicate variable names
            raise ValueError("Duplicate variable declaration at line {}".format(self.lineno))

    def addVariableToMethodDict(self):
        """
        When called, we assume we have a new variable declaration to add to our method's dict of variables. The info
        should already be stored in the static variables, so we don't need to pass in any arguments. We take this
        opportunity to reset the values for current data type and current variable name, and we increase the argcount
        counter. Argcount holds the cumulative number of the variable being evaluated. In the method's dict, we also
        store in which order of appearance the variables are read. This is useful for our math parser, among other
        tools, to determine how far the S2 pointer must travel to reach that specific variable.
        :return:
        """

        self.methodList[self.currentMethod][self.currentVar] = (self.currentType, self.argCount)
        self.argCount += 1
        self.currentType = ""
        self.currentVar = ""
