import dragon

class PostfixParser(dragon.Parser):
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