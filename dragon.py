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