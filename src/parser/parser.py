from .lexer import TokenType
from .ast import *


def s(msg):
    print(msg)


class ParseError(RuntimeError):
    def __init__(self, token, message):
        self.token = token
        self.message = message


class Parser(object):
    def __init__(self, tokens):
        self._tokens = tokens
        self._current = 0

    def parse(self):
        statements = list()
        while not self._at_end():
            try:
                statement = self._statement()
            except ParseError as err:
                s.error(err.token, err.message)
                break
            else:
                statements.append(statement)
        return statements

    def _advance(self):
        if not self._at_end():
            self._current += 1
        return self._previous()

    def _match(self, *types):
        for type in types:
            if self._check(type):
                self._advance()
                return True
        return False

    def _consume(self, type, message):
        if self._check(type):
            return self._advance()
        raise ParseError(self._peek(), message)

    def _check(self, type):
        if self._at_end():
            return False
        return self._peek().type == type

    def _peek(self):
        return self._tokens[self._current]

    def _previous(self):
        return self._tokens[self._current - 1]

    def _at_end(self):
        return self._current >= len(self._tokens)

    def _expression(self):
        return self._assignment()

    def _statement(self):
        if self._match(TokenType.IF):
            return self._if_stmt()
        elif self._match(TokenType.WHILE):
            return self._while_stmt()
        elif self._match(TokenType.FOR):
            return self._for_stmt()
        elif self._match(TokenType.FUNCTION):
            return self._function()
        elif self._match(TokenType.CLASS):
            return self._class()
        elif self._match(TokenType.TYPE):
            return self._var_decl_stmt()
        elif self._match(TokenType.BREAK, TokenType.CONTINUE, TokenType.EXIT):
            return self._keyword()
        elif self._match(TokenType.TRY):
            return self._try_stmt()
        elif self._match(TokenType.THROW):
            return self._throw_stmt()
        elif self._match(TokenType.INCLUDE, TokenType.INSERT):
            return self._directive()
        elif self._match(TokenType.LBRACE):
            return self._block()
        else:
            return self._expr_stmt()

    def _keyword(self):
        type = self._previous().type
        if type == TokenType.BREAK:
            self._consume(TokenType.SEMICOLON,
                          "Expect ';' after 'brake' statement.")
            return BreakStmt()
        elif type == TokenType.CONTINUE:
            self._consume(TokenType.SEMICOLON,
                          "Expect ';' after 'continue' statement.")
            return ContinueStmt()
        elif type == TokenType.EXIT:
            self._consume(TokenType.SEMICOLON,
                          "Expect ';' after 'exit' statement.")
            return ExitStmt()

    def _directive(self):
        self._consume(TokenType.STRING, "Expect path after directive.")
        return

    def _throw_stmt(self):
        expression = None
        if not self._check(TokenType.SEMICOLON):
            expression = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after 'throw' statement.")
        return ThrowStmt(expression)

    def _try_stmt(self):
        self._consume(TokenType.LBRACE, "Expect '{' after 'try'.")
        try_branch = self._block()

        exception = None
        catch_branch = None
        finally_branch = None
        if self._match(TokenType.CATCH):
            if self._match(TokenType.LPAREN):
                exception = self._consume(TokenType.IDENTIFIER,
                                          "Expect exception name.")
            self._consume(TokenType.RPAREN, "Expect ')'.")
            self._consume(TokenType.LBRACE, "Expect '{' after 'catch'.")
            catch_branch = self._block()
        elif self._match(TokenType.FINALLY):
            self._consume(TokenType.LBRACE, "Expect '{' after 'finally'.")
            finally_branch = self._block()

        return TryStmt(try_branch, exception, catch_branch, finally_branch)

    def _var_decl_stmt(self):
        variables = list()

        type = self._previous()
        while True:
            name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
            initializer = None
            if self._match(TokenType.ASSIGN):
                initializer = self._expression()

            variables.append((type, name, initializer))
            if not self._match(TokenType.COMMA):
                break

        self._consume(TokenType.SEMICOLON,
                      "Expect ';' after variable declaration.")

        return DeclarationStmt(variables)

    def _for_stmt(self):
        self._consume(TokenType.LPAREN, "Expect '(' after 'for'.")

        initializer = list()
        if not self._check(TokenType.SEMICOLON):
            if self._match(TokenType.TYPE):
                initializer.append(self._var_decl_expr())
            else:
                initializer = list()
                while True:
                    initializer.append(self._expression())
                    if not self._match(TokenType.COMMA):
                        break
        self._consume(TokenType.SEMICOLON, "Expect ';' after loop initializer.")

        condition = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment = list()
        if not self._check(TokenType.RPAREN):
            while True:
                increment.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break
        self._consume(TokenType.RPAREN, "Expect ')' after 'for' clauses.")

        body = None
        if not self._match(TokenType.SEMICOLON):
            body = self._statement()

        return ForStmt(initializer, condition, increment, body)

    def _while_stmt(self):
        self._consume(TokenType.LPAREN, "Expect '(' after 'while'.")
        condition = self._expression()
        self._consume(TokenType.RPAREN, "Expect ')' after condition.")

        body = None
        if not self._match(TokenType.SEMICOLON):
            body = self._statement()

        return WhileStmt(condition, body)

    def _if_stmt(self):
        self._consume(TokenType.LPAREN, "Expect '(' after 'if'.")
        condition = self._expression()
        self._consume(TokenType.RPAREN, "Expect ')' after condition.")

        then_branch = None
        if not self._match(TokenType.SEMICOLON):
            then_branch = self._statement()

        else_branch = None
        if self._match(TokenType.ELSE):
            else_branch = self._statement()

        return IfStmt(condition, then_branch, else_branch)

    def _class(self):
        name = self._consume(TokenType.IDENTIFIER, "Expect class name.")

        parents = None
        if self._match(TokenType.COLON):
            parents = list()
            while True:
                parent = self._consume(TokenType.IDENTIFIER,
                                       "Expect superclass name.")
                parents.append(parent)
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.LBRACE, "Expect '{' before class body.")
        body = self._block()

        return ClassStmt(name, parents, body)

    def _function(self):
        fun_name = self._consume(TokenType.IDENTIFIER, "Expect function name.")

        self._consume(TokenType.LPAREN, "Expect '(' after function name.")

        parameters = list()
        if not self._check(TokenType.RPAREN):
            while True:
                type = None
                if self._match(TokenType.TYPE):
                    type = self._previous()

                var_name = self._consume(TokenType.IDENTIFIER,
                                         "Expect parameter name.")
                initializer = None
                if self._match(TokenType.ASSIGN):
                    if self._match(TokenType.STRING, TokenType.NUMBER):
                        initializer = self._previous()
                    else:
                        raise ParseError(initializer,
                                         "Initializer can be string or number only.")

                parameters.append((type, var_name, initializer))

                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RPAREN, "Expect ')' after parameters.")

        self._consume(TokenType.LBRACE, "Expect '{' before function body.")
        body = self._block()

        return FunctionStmt(fun_name, DeclarationExpr(parameters), body)

    def _block(self):
        statements = list()
        while not self._check(TokenType.RBRACE) and not self._at_end():
            statements.append(self._statement())
        self._consume(TokenType.RBRACE, "Expect '}' after block.")
        return BlockStmt(statements)

    def _expr_stmt(self):
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return ExpressionStmt(expr)

    def _var_decl_expr(self):
        variables = list()

        type = self._previous()
        while True:
            name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
            initializer = None
            if self._match(TokenType.ASSIGN):
                initializer = self._expression()

            variables.append((type, name, initializer))
            if not self._match(TokenType.COMMA):
                break

        return DeclarationExpr(variables)

    def _assignment(self):
        expr = self._logical_or()
        if self._match(TokenType.ASSIGN):
            assign = self._previous()
            value = self._assignment()
            if isinstance(expr, VariableExpr) or \
               isinstance(expr, AccessExpr) or \
               isinstance(expr, ArrayExpr):
                name = expr
                return AssignExpr(name, value)
            raise ParseError(assign, "Invalid assignment target.")
        return expr

    def _logical_or(self):
        expr = self._logical_and()
        while self._match(TokenType.OR):
            operator = self._previous()
            right = self._logical_and()
            expr = BinaryExpr(operator, expr, right)
        return expr

    def _logical_and(self):
        expr = self._bitwise_and()
        while self._match(TokenType.AND):
            operator = self._previous()
            right = self._bitwise_or()
            expr = BinaryExpr(operator, expr, right)
        return expr

    def _bitwise_or(self):
        expr = self._bitwise_and()
        while self._match(TokenType.BIT_OR):
            operator = self._previous()
            right = self._bitwise_and()
            expr = BinaryExpr(operator, expr, right)
        return expr

    def _bitwise_and(self):
        expr = self._equality()
        while self._match(TokenType.BIT_AND):
            operator = self._previous()
            right = self._equality()
            expr = BinaryExpr(operator, expr, right)
        return expr

    def _equality(self):
        expr = self._comparison()
        while self._match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self._previous()
            right = self._comparison()
            expr = BinaryExpr(operator, expr, right)
        return expr

    def _comparison(self):
        expr = self._shift()
        while self._match(TokenType.MORE, TokenType.MORE_EQUAL,
                          TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self._previous()
            right = self._shift()
            expr = BinaryExpr(operator, expr, right)
        return expr

    def _shift(self):
        expr = self._addition()
        while self._match(TokenType.SHL, TokenType.SHR):
            operator = self._previous()
            right = self._addition()
            expr = BinaryExpr(operator, expr, right)
        return expr

    def _addition(self):
        expr = self._multiplication()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous()
            right = self._multiplication()
            expr = BinaryExpr(operator, expr, right)
        return expr

    def _multiplication(self):
        expr = self._unary()
        while self._match(TokenType.MUL, TokenType.DIV, TokenType.MOD):
            operator = self._previous()
            right = self._unary()
            expr = BinaryExpr(operator, expr, right)
        return expr

    def _unary(self):
        if self._match(TokenType.MINUS, TokenType.BIT_NOT, TokenType.NOT):
            operator = self._previous()
            right = self._unary()
            return UnaryExpr(operator, right)
        return self._operand()

    def _array(self, expr):
        indices = None
        if not self._check(TokenType.RSQUARE):
            indices = list()
            while True:
                indices.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break
        self._consume(TokenType.RSQUARE, "Expect bracket after indices.")

        return ArrayExpr(expr, indices)

    def _call(self, expr):
        arguments = list()
        if not self._check(TokenType.RPAREN):
            while True:
                arguments.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break
        self._consume(TokenType.RPAREN, "Expect bracket after arguments.")

        return CallExpr(expr, arguments)

    def _variable(self):
        expr = VariableExpr(self._previous())

        while self._match(TokenType.DOT):
            name = self._consume(TokenType.IDENTIFIER,
                                 "Expect property name after '.'.")
            expr = AccessExpr(expr, name)

        if self._match(TokenType.LPAREN):
            expr = self._call(expr)
        elif self._match(TokenType.LSQUARE):
            expr = self._array(expr)

        return expr

    def _operand(self):
        if self._match(TokenType.STRING, TokenType.NUMBER):
            return LiteralExpr(self._previous())
        if self._match(TokenType.IDENTIFIER):
            return self._variable()
        if self._match(TokenType.LPAREN):
            expr = self._expression()
            self._consume(TokenType.RPAREN, "Expect ')' after expression.")
            return GroupExpr(expr)
