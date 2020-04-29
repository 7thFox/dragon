import dragon

class AParser(dragon.NodeParser):

    def Start(self):
        children = {
            '+': lambda: [self.match('+'), self.Start(), self.Start()],
            '-': lambda: [self.match('-'), self.Start(), self.Start()],
            'a': lambda: [self.match('a')],
        }[self.tokens[self.lookahead]]()
        return dragon.node("S", children)

class BParser(dragon.NodeParser):

    def Start(self):
        if len(self.tokens) == self.lookahead or self.tokens[self.lookahead] != '(':
            return dragon.node("epsilon")
        return dragon.node("S", [self.match('('), self.Start(), self.match(')'), self.Start()])


class CParser(dragon.NodeParser):

    def Start(self):
        return dragon.node("S", [self.match('0'), self.R(), self.match('1')])

    def R(self):
        if len(self.tokens) == self.lookahead or self.tokens[self.lookahead] != '0':
            return dragon.node("epsilon")
        return dragon.node("R", [self.match('0'), self.R(), self.match('1')])



print(AParser().parse(input()))

print(BParser().parse(input()))

print(CParser().parse(input()))
