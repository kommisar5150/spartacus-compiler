#!/usr/bin/env python

from constants import L_PARENTHESES, \
                      R_PARENTHESES, \
                      OPERATIONS, \
                      INSTRUCTIONS, \
                      TOKEN_SEPARATOR, \
                      REGISTERS, \
                      REGISTER_NAMES


def tokenize(expression):
    """
    Transforms an expression into individual tokens, separating operators from operands.
    :param expression: str, mathematical expression to tokenize.
    :return: str list, each element of the expression split into a list.
    """
    return [t.strip() for t in TOKEN_SEPARATOR.split(expression.strip()) if t]


def infixToPostfix(tokens):
    """
    Takes a tokenized mathematical expression and returns its postfix representation. For example, the formula:
    "4 + a * b" will return: "4 a b * +".
    :param tokens: str list, Math expression tokenized into list of individual strings
    :return: str list, our postfix representation
    """

    stack = []                        # temporary stack to hold operators and operands
    postfix = []                      # confirmed list of elements for the postfix representation

    for element in tokens:
        # Evaluate each token in sequence
        if element in OPERATIONS:
            # Here we find an operator (+, -, *, /), so we push the operands on the stack
            # and reorganize them based on the order of precedence of operations. The ordered operations are then
            # Pushed onto the postfix "stack"

            while len(stack) > 0 and stack[-1] in OPERATIONS\
                  and OPERATIONS[element]['priority'] <= OPERATIONS[stack[-1]]['priority']:
                postfix.append(stack.pop())
            stack.append(element)

        elif element == L_PARENTHESES:
            # Left parentheses found, simply append to the stack
            stack.append(element)

        elif element == R_PARENTHESES:
            # Right parentheses found, so we pop all the elemends and push onto postfix stack
            # until we reach left parentheses
            while stack[-1] != L_PARENTHESES:
                postfix.append(stack.pop())
            stack.pop()

        else:
            # Otherwise no significant order of operations needs to be followed, so we simply push to postfix stack
            postfix.append(element)

    # We need to append any remaining operands from the stack, so we add them to the postfix "stack" in reverse
    postfix.extend(reversed(stack))

    return postfix


def evaluatePostfix(postfix, variableList, variableLocation, methodVariables, output):
    """
    Evaluates the postfix math expression. Variables have their values read and loaded into registers before executing
    the operation. If variables are in the methodVariables list, we make use of the stack frame pointer "S2" to fetch
    their memory location.For immediate values, since multiplications and divisions may only be done with registers, we
    also load them into registers for ease of automation.
    :param postfix: str list, our postfix mathematical expression to evaluate.
    :param variableList: str list, list of all the variables in the method thus far
    :param variableLocation: dict, each variable has a mapped memory location (e.g. 0x40000000).
    :param methodVariables: dict, variables passed into the method as arguments.
    :param output: file, our output file we write to.
    :return:
    """

    stack = []                      # Stack that will contain our pushed operands from the postfix expression
    immediateCount = 0              # Keeps count of how many immediate values are being expressed (not variables)
    sourceRegister = 1              # Source register starts at 1: "B", and increments as needed
    destRegister = 0                # Destination register starts at 0: 'A" and increments as needed
    immFlag = 0                     # Used to determine whether source or destination register holds an immediate

    for element in postfix:
        # Evaluate each postfix element one by one to determine appropriate action

        if sourceRegister > 6 or destRegister > 6:
            # We cap the total amount of registers used to 7 (0-6)
            raise ValueError("Too many operands in formula.")

        if element in OPERATIONS:
            # Here, our element is an operator. This means we need to pop the top two values from the stack and
            # execute the given operation.
            operand1, operand2 = stack.pop(), stack.pop()

            if operand1 in variableList:
                # The operand is in the list of local variables, so we read the value from memory
                output.write("MEMR [4] #" + str(variableLocation[operand1]) + " $" + REGISTERS[sourceRegister] + "\n")
                operand1 = REGISTERS[sourceRegister]

            elif operand1 in methodVariables:
                # The operand is in the list of arguments passed into the method. We consult the methodVariables list
                # to determine the appropriate offset from the stack pointer register S2.
                output.write("MOV $A2 $S2\n")
                output.write("ADD #" + str(int(methodVariables[operand1][1]) * 4) + " $A2\n")
                output.write("MEMR [4] $A2 $" + REGISTERS[sourceRegister] + "\n")
                operand1 = REGISTERS[sourceRegister]

            elif operand1 in REGISTER_NAMES:
                # This is simply a register that was pushed onto the stack. We can keep it as is
                 pass

            else:
                # The operand is an immediate value. We test to see if it's a valid integer
                try:
                    isinstance(operand1, int)
                    immediateCount += 1
                    immFlag = 1
                except ValueError as e:
                    raise ValueError("Invalid operand")

            if operand2 in variableList:
                # The operand is in the list of local variables, so we read the value from memory
                output.write("MEMR [4] #" + str(variableLocation[operand2]) + " $" + REGISTERS[destRegister] + "\n")
                operand2 = REGISTERS[destRegister]

            elif operand2 in methodVariables:
                # The operand is in the list of arguments passed into the method. We consult the methodVariables list
                # to determine the appropriate offset from the stack pointer register S2.
                output.write("MOV $B2 $S2\n")
                output.write("ADD #" + str(int(methodVariables[operand2][1]) * 4) + " $B2\n")
                output.write("MEMR [4] $B2 $" + REGISTERS[destRegister] + "\n")
                operand2 = REGISTERS[destRegister]

            elif operand2 in REGISTER_NAMES:
                # This is simply a register that was pushed onto the stack. We can keep it as is
                pass

            else:
                # The operand is an immediate value. We test to see if it's a valid integer
                try:
                    isinstance(operand2, int)
                    immediateCount += 1
                    immFlag = 2
                except ValueError as e:
                    raise ValueError("Invalid operand")

            if immediateCount == 2:
                # If we have two immediate values, we don't really need to calculate the arithmetic in Capua ASM.
                # We discretely do the calculations in the background and push the value to the stack. This avoids
                # unnecessary processing.
                try:
                    stack.append(int(OPERATIONS[element]['function'](float(operand2), float(operand1))))

                except ZeroDivisionError:
                    raise ValueError("Error: Division by zero! - {} {} {}".format(operand2, element, operand1))
            else:
                if immediateCount == 1:
                    # only one of the operands was an immediate value. We determine which one is the immediate value,
                    # as the correct instruction output depends on it.
                    if immFlag == 1:
                        output.write("MOV #" + str(int(operand1)) + " $" + REGISTERS[sourceRegister] + "\n")
                        operand1 = REGISTERS[sourceRegister]

                    elif immFlag == 2:
                        output.write("MOV #" + str(int(operand2)) + " $" + REGISTERS[destRegister] + "\n")
                        operand2 = REGISTERS[destRegister]

                else:
                    # No operands were immediate values. We can do the arithmetic operation as is.
                    # We move the source and destination registers up one letter for the next operation
                    sourceRegister += 1
                    destRegister += 1

                    output.write(INSTRUCTIONS[element] + " $" + str(operand1) + " $" + str(operand2) + "\n")
                stack.append(operand2)

            immediateCount = 0

        else:
            # We have an operand to push onto the stack
            stack.append(element)

    if len(stack) != 1:
        # If the stack has more than or less than one element, the expression is incorrect.
        raise ValueError("invalid expression.")

    # our result is then "saved" into register A. The assignment can now be completed.
    result = stack.pop()

    if result in REGISTER_NAMES:
        pass
    else:
        try:
            isinstance(int(result), int)
            output.write("MOV #" + str(result) + " $A\n")
        except ValueError as e:
            raise ValueError("Invalid mathematical expression")