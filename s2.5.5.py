from abc import ABC, abstractmethod


class Parser(ABC):
    def match(self, c):
        if self.tokens[self.lookahead] != c:
            raise Exception("Parse Error: expected " + c)
        self.lookahead += 1
        return self.MatchReturn(c)

    def parse(self, tokens):
        self.tokens = tokens
        self.lookahead = 0
        ret = self.Start()
        if len(self.tokens) != self.lookahead:
            raise Exception("Unexpected token " + self.tokens[self.lookahead])
        return ret

    def peek(self):
        if len(self.tokens) == self.lookahead:
            return None
        return self.tokens[self.lookahead]

    def unexpected_token(self, token):
        raise Exception("Syntax Error: Unexpected token " + token)

    @abstractmethod
    def Start(self):
        pass

    @abstractmethod
    def MatchReturn(self, c):
        pass


class PostfixParser(Parser):
    def MatchReturn(self, c):
        return ""

    def Start(self):
        return self.Term() + self.Rest()

    def Rest(self):
        c = self.peek()
        if c == '+':
            return self.match('+') + self.Term() + "+" + self.Rest()
        elif c == '-':
            return self.match('-') + self.Term() + "-" + self.Rest()
        elif c == None:
            return ""
        else:
            self.unexpected_token(c)

    def Term(self):
        c = self.peek()
        if c.isdigit():
            k = self.match(c)
            return k + c
        else:
            self.unexpected_token(c)


print(PostfixParser().parse(input().replace(" ", "")))
