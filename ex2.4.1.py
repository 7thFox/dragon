from abc import ABC, abstractmethod


class node:
    def __init__(self, value, children=[]):
        self.value = value
        self.children = children

    def __str__(self, level=0):
        return "|--"*level + "+ " + self.value + "\n" + "".join([c.__str__(level+1) for c in self.children])


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


class NodeParser(Parser):
    def MatchReturn(self, c):
        return node(c)


class AParser(NodeParser):

    def Start(self):
        children = {
            '+': lambda: [self.match('+'), self.Start(), self.Start()],
            '-': lambda: [self.match('-'), self.Start(), self.Start()],
            'a': lambda: [self.match('a')],
        }[self.tokens[self.lookahead]]()
        return node("S", children)


class BParser(NodeParser):

    def Start(self):
        if len(self.tokens) == self.lookahead or self.tokens[self.lookahead] != '(':
            return node("epsilon")
        return node("S", [self.match('('), self.Start(), self.match(')'), self.Start()])


class CParser(NodeParser):

    def Start(self):
        return node("S", [self.match('0'), self.R(), self.match('1')])

    def R(self):
        if len(self.tokens) == self.lookahead or self.tokens[self.lookahead] != '0':
            return node("epsilon")
        return node("R", [self.match('0'), self.R(), self.match('1')])


print(AParser().parse(input()))

print(BParser().parse(input()))

print(CParser().parse(input()))
