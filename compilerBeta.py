#!/usr/bin/env python

# TODO: if statements
# TODO: while loops

from constants import ACCEPTED_TYPES, \
                      BOOLEAN_OPERATORS

from mathParser import tokenize, \
                       infixToPostfix, \
                       evaluatePostfix

class CompilerTest:
    """
    Beta for a C compiler which converts C code to Capua ASM. The compiler makes use of the cdecl calling convention,
    often used by C compilers for the x86 architecture. This convention stipulates that "subroutine arguments are passed
    on the stack. Integer values and memory addresses are returned in the EAX register". In our case, contrary to cdecl,
    arguments will be pushed onto the stack from left to right, meaning the first argument gets pushed first. Integer
    values and memory addresses are returned to the "A" register for this Capua ASM compiler.
    """

    state = 0                     # This determines which state the compiler is in. Each state has specific instructions
    mathFormula = ""              # Will contain our fully assembled math expressions for variable assignments
    memoryLocation = 0x40000000   # Memory location for local variables.
    varList = []                  # Contains a list of variable names
    varLocation = {}              # Contains the memory location for all variables
    methodList = {}               # List of methods, along with their return type, variables (and types), and # of args
    currentMethod = ""            # Keeps track of which method we're currently in
    argCount = 0                  # Used for number of operands in math expression, args in function calls, etc.
    variableCount = 0             # Number of variables declared in current function.
    currentType = ""              # Current data type of variable or function to be evaluated
    currentVariable = ""          # Current variable or function being evaluated
    functionCall = ""             # Name of the function we're calling when doing variable assignment
    whileFlag = 0                 # Lets the compiler know if we're in a while loop
    ifOperator = ""               # Holds the logical operator between two sides of an if boolean expression
    ifFlag = 0                    # Lets the compiler know if we're in an if statement
    ifLabel = 0                   # For jump instructions, we need a unique label for every if statement


    def parseText(self, text):
        """
        Initializes parsing process. Opens the input file to read from, and initializes the output file we will create.
        :param text: str, name of file to read from
        :return:
        """
        file = open(text, mode="r")
        lines = file.readlines()
        output = open("output.casm", mode="w")

        for x in lines:
            self.readLine(x, output)

        if self.ifFlag > -1:
            raise ValueError("Missing closing curly brace after If statement.")
        output.write("end:\n")
        file.close()
        output.close()

    def readLine(self, line, output):
        """
        Takes each line from the input file and sorts the information accordingly. We make use of states to determine
        the next appropriate action. Line is split into individual tokens, and the correct state handles how the output
        will be formatted.
        :param line: str, line read from our input file
        :param output: file, location where output will be written to.
        :return:
        """

        line = line.split()
        for char in line:

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

            elif self.state == 9:
                self.state9(char, output)

            elif self.state == 10:
                self.state10(char, output)

            elif self.state == 11:
                self.state11(char, output)

            elif self.state == 12:
                self.state12(char, output)

            elif self.state == 13:
                self.state13(char, output)

            elif self.state == 14:
                self.state14(char, output)

            elif self.state == 15:
                self.state15(char, output)

            elif self.state == 16:
                self.state16(char, output)

            elif self.state == 17:
                self.state17(char, output)

            elif self.state == 18:
                self.state18(char, output)

            elif self.state == 19:
                self.state19(char, output)

            elif self.state == 20:
                self.state20(char, output)

            elif self.state == 21:
                self.state21(char, output)

    def state0(self, char, output):
        """
        Initial state before method return type declaration. Here we determine if the return type is valid. If so,
        we move on to state 1
        :param char: token from line being read.
        :param output: output file to write to.
        :return:
        """
        if self.state == 0:
            self.varList.clear()
            self.varLocation.clear()
            self.variableCount = 0
            if char in ACCEPTED_TYPES:
                self.currentType = char
                self.state = 1
            else:
                raise ValueError("incorrect data return type for method declaration.")

    def state1(self, char, output):
        """
        This state determines the name of the method. We add the method's name to the dict along with its return type,
        then move on to state 2
        :param char: token from line being read.
        :param output: output file to write to.
        :return:
        """
        self.methodList[char] = {"retType": self.currentType}
        self.currentMethod = char
        output.write(char + ":\n")
        if char == "main":
            output.write("    MOV end $S\n")
        self.state = 2

    def state2(self, char, output):
        """
        This state simply checks for an opening parentheses for potential arguments passed in.
        :param char: token from line being read.
        :param output: output file to write to.
        :return:
        """
        if char == "(":
            self.state = 3
        else:
            raise ValueError("Incorrect syntax.")

    def state3(self, char, output):
        """
        This state verifies if the argument's data type is valid, or if there's a closing parentheses. If we find a
        valid data type, we go to state 4. If there's a parentheses, we go to state 6.
        :param char: token from line being read.
        :param output: output file to write to.
        :return:
        """
        if char in ACCEPTED_TYPES:
            self.currentType = char
            self.state = 4
        elif char == ")":
            self.state = 6
        else:
            raise ValueError("incorrect data type for argument.")

    def state4(self, char, output):
        """
        This state stores the variable and its data type in the dict at the current method's index. We then continue to
        state 5.
        :param char: token from line being read.
        :param output: output file to write to.
        :return:
        """
        # method list dict will have, at the index of the specified method,
        # a list of all variables passed in as arguments (as a nested dict), which in turn
        # holds a tuple of its data type and order of appearance in the function call.
        self.methodList[self.currentMethod][char] = (self.currentType, self.argCount)
        self.argCount += 1
        self.state = 5

    def state5(self, char, output):
        """
        If we read a comma, there are more arguments to read, so we jump to state 3. If we read a closing parentheses,
        we just to state 6.
        :param char: token from line being read.
        :param output: output file to write to.
        :return:
        """
        if char == ",":
            self.state = 3
        elif char == ")":
            self.state = 6
        else:
            raise ValueError("Incorrect syntax.")

    def state6(self, char, output):
        """
        This is the last state in method declaration. We tally up the number of variables and append it to the method's
        dict entry. If the next character is an opening curly brace, we proceed to state 7 where we will parse the
        method's body.
        :param char: token from line being read.
        :param output: output file to write to.
        :return:
        """
        self.methodList[self.currentMethod]["totalVars"] = self.argCount
        if char == "{":
            self.state = 7
            self.varList.clear()
            if self.argCount > 0:
                output.write("    MOV $S $S2\n")
                output.write("    SUB #" + str(self.argCount * 4 + 4) + " $S2\n")
        else:
            raise ValueError("Incorrect syntax.")

    def state7(self, char, output):
        """
        The first stop in parsing the method's body. Temporary instances are reset to evaluate the next expression. If
        we read a valid data type, we assume a new variable is being declared, so we jump to state 8. If the token is
        an already declared variable, we skip to state 9. If we read a function call, we jump to state 11. If we read
        a return statement, we jump to state 16.
        :param char: token from line being read.
        :param output: output file to write to.
        :return:
        """

        self.argCount = 0
        self.mathFormula = ""
        self.currentVariable = ""
        self.functionCall = ""

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
            self.state = 9

        elif char == "}":

            if self.ifFlag > 0:
                output.write("endif" + str(self.ifLabel-1) + ":\n")
                self.ifFlag -= 1

            else:
                self.state = 0
                self.ifFlag -= 1

        elif char == "return":
            self.state = 16

        elif char == "if":
            self.ifFlag += 1
            self.state = 18

    def state8(self, char, output):
        """
        Here we should read the variable's name. We add the new variable to the list of local variables, assign its
        memory location, and update the current variable being evaluated. We then jump to state 9.
        :param char: token from line being read.
        :param output: output file to write to.
        :return:
        """

        # int
        self.varList.append(char)
        self.varLocation[char] = self.memoryLocation
        self.memoryLocation += 4
        self.variableCount += 1
        self.currentVariable = char
        self.state = 9

    def state9(self, char, output):
        """
        In this state, we either reach the end of a variable declaration, or evaluate a variable assignment. If we read
        a semi-colon, the statement is done and we return to state 7. If we read an equals operator "=", we jump to
        state 10 for mathematical evaluation.
        :param char: token from line being read.
        :param output: output file to write to.
        :return:
        """
        # int a / a
        if char == "=":
            self.state = 10
        elif char == ";":
            self.state = 7

    def state10(self, char, output):
        """
        This is the state which handles parsing of math expressions for variable assignment.
        Once we're done, we jump back to state 7. However, if the first operand is a function call,
        we jump to state 11.
        :param char: token from line being read.
        :param output: output file to write to.
        :return:
        """

        if char == ";":
            # we reach the end of the formula, so we can evaluate it and assign the result to the variable.

            if self.argCount == 1:
                # We only have one operand, so there's no need to pass the expression through the math parser.

                if self.mathFormula in self.varList:
                    # The operand is a variable from the local list. We read its value and write it to the variable
                    output.write("    MEMR [4] #" + str(self.varLocation[self.mathFormula]) + " $A\n")

                elif self.mathFormula in self.methodList[self.currentMethod]:
                    # The operand is one of the function's arguments. We use the stack pointer to locate its memory
                    # location (we assume it was pushed onto the stack during function call), then we read its value
                    # before writing it to the variable.
                    output.write("    MOV $B2 $S2\n")
                    output.write("    ADD #" + str(self.methodList[self.currentMethod][self.mathFormula][1] * 4)
                                 + " $B2\n")
                    output.write("    MEMR [4] $B2 $A\n")

                else:
                    # The operand is simply an immediate value (integer). We can move it to a register and write to the
                    # appropriate memory location.
                    output.write("    MOV #" + self.mathFormula + " $A\n")

                if self.currentVariable in self.methodList[self.currentMethod]:
                    # The variable is an argument passed into the function. We use the stack pointer to fetch its
                    # location before writing the value.
                    output.write("    MOV $A2 $S2\n")
                    output.write("    ADD #" + str(self.methodList[self.currentMethod][char][1] * 4) + " $A2\n")
                    output.write("    MEMW [4] $A $A2\n")

                else:
                    # The variable is local, so we just write the result to its memory location from the local list.
                    output.write("    MEMW [4] $A #" + str(self.varLocation[self.currentVariable]) + "\n")

            elif self.argCount < 1:
                # This is in case we write something like "int a = ;", which is invalid.
                raise ValueError("Incorrect syntax: variable assignment has no operand!")

            else:
                # Otherwise, we have multiple operands to evaluate. We use the mathParser's functions to print out the
                # appropriate Capua ASM code. We tokenize the formula into individual tokens, determine its postfix
                # notation, then evaluate it.
                tokens = tokenize(self.mathFormula)
                postfix = infixToPostfix(tokens)
                evaluatePostfix(postfix, self.varList, self.varLocation,
                                self.methodList[self.currentMethod], output)

                if self.currentVariable in self.methodList[self.currentMethod]:
                    # The variable is an argument passed into the function. We use the stack pointer to fetch its
                    # location before writing the value.
                    output.write("    MOV $A2 $S2\n")
                    output.write("    ADD #" + str(self.methodList[self.currentMethod][self.currentVariable][1] * 4)
                                                                                                         + " $A2\n")
                    output.write("    MEMW [4] $A $A2\n")

                else:
                    # The variable is local, so we just write the result to its memory location from the local list.
                    output.write("    MEMW [4] $A #" + str(self.varLocation[self.currentVariable]) + "\n")

            self.state = 7

        elif char in self.methodList:
            # If we read a function call, we need to handle this case a special way.
            self.functionCall = char
            self.state = 11

        else:
            # We read another operand which we append to the formula list.
            self.mathFormula += str(char)
            self.argCount += 1

    def state11(self, char, output):
        """
        This state simply checks that the function call is followed by an opening parentheses. We then jump to state 12.
        :param char: token from line being read.
        :param output: output file to write to.
        :return:
        """

        self.argCount = 0
        if char == "(":
            self.state = 12
        else:
            raise ValueError("Incorrect syntax.")

    def state12(self, char, output):
        """
        Here we read the parameters for the function call. Arguments are pushed onto the stack so they can be used
        within the function's stack frame. The stack pointer "S" always points to the top of the stack, so we can
        determine the location of pushed arguments based on that offset. The register "S2" will be used to point to the
        bottom of the stack frame, meaning the first argument pushed before the function call.
        :param char: token from line being read. Once we read our argument, we jump to state 13. If we read a closing
        parentheses, jump to state 15.
        :param output: output file to write to.
        :return:
        """

        if char in self.varList:
            # variable is in the local list
            output.write("    PUSH #" + str(self.varLocation[char]) + "\n")
            self.state = 13
            self.argCount += 1

        elif char in self.methodList[self.currentMethod]:
            # variable is passed into the function as an argument
            output.write("    MOV $A2 $S2\n")
            output.write("    ADD #" + str(self.methodList[self.currentMethod][char][1] * 4) + " $A2\n")
            output.write("    PUSH $A2\n")
            self.state = 13
            self.argCount += 1

        elif char == ")":
            # we're done verifying for arguments within the function call
            self.state = 15

    def state13(self, char, output):
        """
        This state simply checks if there are more arguments to read, or if we're done. A comma indicates there are more
        to read, so we jump to state 14. A closing parentheses means we're done, and we jump to state 15.
        :param char: token from line being read.
        :param output: output file to write to.
        :return:
        """
        if char == ",":
            self.state = 14
        elif char == ")":
            self.state = 15

    def state14(self, char, output):
        """
        Identical to state 12, but for organisational purposes, this state was necessary. The only difference is that at
        this point in parsing, we should not be able to read a closing parentheses (following a comma, which would
        look like this: c = add ( a , )". In all valid cases, we jump back to state 13.
        :param char: token from line being read.
        :param output: output file to write to.
        :return:
        """

        if char in self.varList:
            # variable is in the local list
            output.write("    PUSH #" + str(self.varLocation[char]) + "\n")
            self.state = 13
            self.argCount += 1

        elif char in self.methodList[self.currentMethod]:
            # variable is passed into the function as an argument
            output.write("    MOV $A2 $S2\n")
            output.write("    ADD #" + str(self.methodList[self.currentMethod][char][1] * 4) + " $A2\n")
            output.write("    PUSH $A\n")
            self.argCount += 1
            self.state = 13

    def state15(self, char, output):
        """
        This state finalizes the function call. We write the CALL function to the .casm file, and we assign the returned
        value to the appropriate variable (stored in register A). Once we're all done, we switch back to state 7
        :param char: token from line being read.
        :param output: output file to write to.
        :return:
        """

        if char == ";":
            # We ensure the statement is ended with a semi-colon properly

            if self.functionCall == "":
                # This is if the function is being called by itself on a line (no variable assignment)

                if self.argCount == self.methodList[self.currentVariable]["totalVars"]:
                    output.write("    CALL " + self.currentVariable + "\n")
                    self.state = 7
                else:
                    raise ValueError("Arguments don't match function parameters.")

            else:
                # Here, a variable is assigned the output of a function call

                if self.argCount == self.methodList[self.functionCall]["totalVars"]:
                    output.write("    CALL " + self.functionCall + "\n")

                    if self.currentVariable in self.varList:
                        # variable is in the local list
                        output.write("    MEMW [4] $A #" + str(self.varLocation[self.currentVariable]) + "\n")

                    elif self.currentVariable in self.methodList[self.currentMethod]:
                        # variable is passed into the function as an argument
                        output.write("    MOV $A2 $S2\n")
                        output.write("    ADD #" + str(self.methodList[self.currentMethod][char][1] * 4) + " $A2\n")
                        output.write("    MEMW [4] $A $A2\n")
                    self.state = 7

                else:
                    raise ValueError("Arguments don't match function parameters.")

    def state16(self, char, output):
        """
        This state begins the process of evaluating a return statement. If we immediately read a semi-colon, we free up
         the memory used by variables pushed onto the stack and we return to state 7. If we read anything else, we
         append it to the mathFormula string.
        to be evaluated.
        :param char: token from line being read.
        :param output: output file to write to.
        :return:
        """

        if char == ";":
            # Free up the memory used by variable declarations during this stack frame, then return
            self.memoryLocation -= self.variableCount * 4
            output.write("    SUB #" + str(self.variableCount * 4) + " $S\n")
            output.write("    RET\n")
            self.state = 7

        else:
            self.mathFormula += char
            self.argCount += 1
            self.state = 17

    def state17(self, char, output):
        """
        Similar to state 10, this state evaluates a mathematical function, but following a return statement. We append
        each operand until we reach a semi-colon indicating the end of the expression. In this case, rather than
        assigning the result to a variable, we write it to register A. This follows the cdecl calling conventions which
        ensures the correct value is being returned. After a CALL function, any result will always be stored in register
        A. Once finished, we free up the memory used by pushed variables for the stack frame, and we return to state 7.
        :param char: token from line being read.
        :param output: output file to write to.
        :return:
        """

        if char == ";":
            if self.argCount == 1:
                # We only have one operand, no need to use the math parser
                if self.mathFormula in self.varList:
                    output.write("    MEMR [4] #" + str(self.varLocation[self.mathFormula]) + " $A\n")
                elif self.mathFormula in self.methodList[self.currentMethod]:
                    output.write("    MOV $B2 $S2\n")
                    output.write("    ADD #" + str(self.methodList[self.currentMethod][self.mathFormula][1] * 4)
                                                                                                     + " $B2\n")
                    output.write("    MEMR [4] $B2 $A\n")
                else:
                    output.write("    MOV #" + self.mathFormula + " $A\n")

            else:
                # We make use of the math parser to write the appropriate Capua ASM output
                tokens = tokenize(self.mathFormula)
                postfix = infixToPostfix(tokens)
                evaluatePostfix(postfix, self.varList, self.varLocation,
                                self.methodList[self.currentMethod], output)

            # Free up the memory used by variable declarations during this stack frame, then return
            self.memoryLocation -= self.variableCount * 4
            output.write("    SUB #" + str(self.variableCount * 4) + " $S\n")
            output.write("    RET\n")
            self.state = 7

        else:
            # We have more operands to read, so we append them to the math formula string
            self.mathFormula += str(char)
            self.argCount += 1

    def state18(self, char, output):
        """
        Reads an opening parentheses for an if statement. If successful, we jump to state 19.
        :param char: token from line being read.
        :param output: output file to write to.
        :return:
        :return:
        """

        if char == "(":
            self.state = 19
        else:
            raise ValueError("Incorrect syntax.")

    def state19(self, char, output):
        """
        Begins the evaluation of the left hand side for if boolean statement.
        :param char: token from line being read.
        :param output: output file to write to.
        :return:
        :return:
        """

        if char in BOOLEAN_OPERATORS:
            self.ifOperator = char

            if self.argCount == 1:
                # We only have one operand, so there's no need to pass the expression through the math parser.

                if self.mathFormula in self.varList:
                    # The operand is a variable from the local list. We read its value and write it to the variable
                    output.write("    MEMR [4] #" + str(self.varLocation[self.mathFormula]) + " $A2\n")

                elif self.mathFormula in self.methodList[self.currentMethod]:
                    # The operand is one of the function's arguments. We use the stack pointer to locate its memory
                    # location (we assume it was pushed onto the stack during function call), then we read its value
                    # before writing it to the variable.
                    output.write("    MOV $C2 $S2\n")
                    output.write("    ADD #" + str(self.methodList[self.currentMethod][self.mathFormula][1] * 4)
                                 + " $B2\n")
                    output.write("    MEMR [4] $C2 $A2\n")

                else:
                    # The operand is simply an immediate value (integer). We can move it to a register and write to the
                    # appropriate memory location.
                    output.write("    MOV #" + self.mathFormula + " $A2\n")

            else:
                tokens = tokenize(self.mathFormula)
                postfix = infixToPostfix(tokens)
                evaluatePostfix(postfix, self.varList, self.varLocation, self.methodList[self.currentMethod], output)
                output.write("    MEMW [4] $A $A2\n")

            self.mathFormula = ""
            self.argCount = 0
            self.state = 20

        else:
            self.mathFormula += char
            self.argCount += 1

    def state20(self, char, output):
        """
        Begins the evaluation of the right hand side for if boolean statement.
        :param char: token from line being read.
        :param output: output file to write to.
        :return:
        """

        if char == ")":
            if self.argCount == 1:
                # We only have one operand, so there's no need to pass the expression through the math parser.

                if self.mathFormula in self.varList:
                    # The operand is a variable from the local list. We read its value and write it to the variable
                    output.write("    MEMR [4] #" + str(self.varLocation[self.mathFormula]) + " $B2\n")

                elif self.mathFormula in self.methodList[self.currentMethod]:
                    # The operand is one of the function's arguments. We use the stack pointer to locate its memory
                    # location (we assume it was pushed onto the stack during function call), then we read its value
                    # before writing it to the variable.
                    output.write("    MOV $C2 $S2\n")
                    output.write("    ADD #" + str(self.methodList[self.currentMethod][self.mathFormula][1] * 4)
                                 + " $B2\n")
                    output.write("    MEMR [4] $C2 $B2\n")

                else:
                    # The operand is simply an immediate value (integer). We can move it to a register and write to the
                    # appropriate memory location.
                    output.write("    MOV #" + self.mathFormula + " $B2\n")

            else:
                tokens = tokenize(self.mathFormula)
                postfix = infixToPostfix(tokens)
                evaluatePostfix(postfix, self.varList, self.varLocation, self.methodList[self.currentMethod], output)
                output.write("    MEMW [4] $A $B2\n")

            self.state = 21
        else:
            self.mathFormula += char
            self.argCount += 1

    def state21(self, char, output):
        """
        Determines which jump statement is appropriate based on the operator for the if boolean expression.
        :param char: token from line being read.
        :param output: output file to write to.
        :return:
        """

        if char == "{":

            if self.ifOperator == "<":
                flag = "<HE>"
            elif self.ifOperator == "<=":
                flag = "<H>"
            elif self.ifOperator == "=":
                flag = "<LH>"
            elif self.ifOperator == ">":
                flag = "<LE>"
            elif self.ifOperator == ">=":
                flag = "<L>"
            else:
                raise ValueError("Incorrect operator for if statement.")

            output.write("    CMP $B2 $A2\n")
            output.write("    JMP " + flag + " endif" + str(self.ifLabel) + "\n")
            self.ifLabel += 1
            self.state = 7

        else:
            raise ValueError("Syntax error.")
