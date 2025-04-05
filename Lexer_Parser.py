
#Lexer & Parser 
#Created by: Javier Strang

class Lexer:
    def __init__(self, code):
        self.code = code
        self.position = 0

    def increment(self):
        #Increment the position by 1
        self.position += 1
        return self.position

    def wordsAndNumbers(self):
        #Saves the first position of the variable or number 
        firsPos = self.position
        #If the element is a letter
        if self.code[self.position].isalpha():
            #Increment through the length of the word or number
            while (self.code[self.position].isalnum()):
                self.increment()
            #If the word is a statement define it as a statement
            if self.code[firsPos:self.position] in ['while', 'do', 'then', 'else', 'if']: 
                return self.code[firsPos:self.position], self.code[firsPos:self.position]
            #Otherwise it is just a variable 
            return 'variable', self.code[firsPos:self.position]
        #Otherwise the element is a number
        else:
            #Increment through the entire number
            while (self.code[self.position].isdigit()):
                self.increment()
            #Return the number
            return 'number', self.code[firsPos:self.position]
        
    def arithAndOper(self):
        if self.code[self.position] in self.arith:  
            #Create a dictionary that holds all of the arithmetic
            types = {'=': '=', '*': '* or /', '/': '* or /', '+': '+ or -', '-': '+ or -', '(': '(', ')': ')'}
            #Save the element
            arith = self.code[self.position]
            #Increment to the next element
            self.increment()
            #Return what arithmetic it is
            return types.get(arith), arith
        else: 
            #Save the element
            oper = self.position
            #Increment to next element
            self.increment()
            #Return the operator
            return 'operator', self.code[oper:self.position]

    def get_token(self):
        #List of valid arithmetic
        self.arith = ['(', ')', '=', '/', '*', '-', '+']
        #List of valid operators
        self.oper = ['>', '<', '>=', '<=', '!=', '==']
        #Increments the position past spaces in the given input
        while self.position < len(self.code) and (self.code[self.position].isspace()): 
            self.increment()
        #If we have reached the end of input return nothing
        if self.position >= len(self.code):
               return "", None
        #If the element is a letter or number call the helper function
        elif self.code[self.position].isalpha() or self.code[self.position].isdigit():
            return self.wordsAndNumbers()
        #If the element is arithmetic or an operator call the helper function
        elif self.code[self.position] in self.arith or self.code[self.position] in self.oper:
            return self.arithAndOper()
        
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = None

    def parse(self):
        #Parse the program
        return self.program()
        
    def advance(self):
        #set the current token as the next token 
        self.current_token = self.lexer.get_token()

    def program(self):
        #Call advance function to get next token
        self.advance()
        #Return a string that loops until the current token is none, joining the statments together
        return ''.join(self.statement() for i in iter(lambda: self.current_token[1] != None, False))
        
    def statement(self):
        #Create a dictiony that holds token types and what methods need to be called
        token_type = {'if': self.if_statement, 'while': self.while_loop, 'variable': self.assignment}
        #Finds the method that needs to be called for the current token and returns it
        return token_type.get(self.current_token[0])()
    
    def assignment(self):
        #Get the variable from the current token
        vari = self.current_token[1]
        #Call advance to get the next token
        self.advance()
        #Get the operator from the current token
        oper = self.current_token[1]
        #Output the operator, the variable, and the result of the arithmetic expression function
        return f"('{oper}', '{vari}', {self.arithmetic_expression()})"
     
    def arithmetic_expression(self):
        hold = self.term() 
        #If the current token is addition of subtraction 
        if self.current_token[0] == "+ or -":
            #Save the operator
            oper = self.current_token[1]
            #Move to next token
            self.advance() 
            #Format and call term to parse the next term
            hold = f"('{oper}', {hold}, {self.term()})"
        #Check if there is a ) and move to next token if there is
        self.parenthesisChecker()
        return hold

    def parenthesisChecker(self):
        #If the current token is a ) move to next token
        if self.current_token[0] == ')':
            self.advance()

    def term(self):
        hold = self.factor()
        #If the current token is multiplication or division
        if self.current_token[0] == "* or /":
            #Save the operator
            oper = self.current_token[1]  
            #Move to next token
            self.advance() 
            #Format and call factor to parse the next factor 
            hold = f"('{oper}', {hold}, {self.factor()})"
        #Check if there is a ) and move to next token if there is
        self.parenthesisChecker()
        return hold

    def factor(self):
        #Get the current token type and its value
        type, value = self.current_token
        #Call advance to get the next token
        self.advance()
        #If the current token is a variable or number return the value
        if type in ["variable", "number"]:
            return f"'{value}'" if type == "variable" else value
        #Otherwise parse the arithmetic expression
        return self.arithmetic_expression()

    def if_statement(self):
        #Save the condition of the if statment
        cond = self.condition()
        #Move to the next token to get the statement
        self.advance()
        #Get the statement (if or else)
        stmnt = self.statement()
        #If there is not an else statement just return the if statement
        if self.current_token[0] != 'else':
            return f"('if', {cond}, {stmnt})"
        #Otherwise add the else statement
        self.advance()
        return f"('if', {cond}, {stmnt}, {self.statement()})"
    
    def while_loop(self):
        #Save the condition
        cond = self.condition()
        #Move to the next token
        self.advance()
        #Save the statement and make it a string 
        stmnt = str([self.statement()]).replace('"', '')
        #Output the while loop with its condition and statment
        return f"('while', {cond}, {stmnt})"

    def condition(self):
        #Get the arithmetic expression for the right side
        value = self.arithmetic_expression()
        #Get the operator between expressions
        oper = self.current_token[1]
        #Move to next token 
        self.advance()
        #Format and output the operator with its left and right expressions
        return f"('{oper}', {value}, {self.arithmetic_expression()})"
    