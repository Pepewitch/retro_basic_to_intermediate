import sys

class RetroBasic():
    id = set([chr(e) for e in range(ord('A'), ord('Z')+1)])
    line_num = set([str(i) for i in range(1,1001)])
    const = set([str(i) for i in range(1,101)])
    terminal = set(["+", "-", "IF", "<", "=", "PRINT", "GOTO", "STOP", "EOF"])
    parse_table = {
        "pgm" : {
            "line_num" : ["line", "pgm"],
            "EOF" : ["EOF"]
        },
        "line" : {"line_num" : ["line_num", "stmt"]},
        "stmt" : {
            "id" : ["asgmnt"], 
            "IF" : ["if"], 
            "PRINT" : ["print"], 
            "GOTO" : ["goto"], 
            "STOP" : ["stop"]
        },
        "asgmnt" : {"id" : ["id", "=", "exp"]},
        "exp" : {
            "id" : ["term", "nextexp"], 
            "const" : ["term", "nextexp"]
        },
        "term" : {
            "id" : ["id"], 
            "const" : ["const"]
        },
        "if" : {"IF" : ["IF", "cond", "line_num"]},
        "cond" : {
            "id" : ["term", "nextcond"], 
            "const" : ["term", "nextcond"]
        },
        "nextexp" : {
            "line_num" : None, 
            "+" : ["+", "term"], 
            "-" : ["-", "term"], 
            "EOF" : None
        },
        "nextcond" : {
            "<" : ["<", "term"], 
            "=" : ["=", "term"]
        },
        "print" : {"PRINT" : ["PRINT", "id"]},
        "goto" : {"GOTO" : ["GOTO", "line_num"]},
        "stop" : {"STOP" : ["STOP"]},
    }
    bcode_list ={
        "#line" : 10,
        "#id" : 11,
        "#const" : 12,
        "#if" : 13,
        "#goto" : 14,
        "#print" : 15,
        "#stop" : 16,
        "#op" : 17,
    }
    def __init__(self , file):
        self.stack = ["EOF"]
        self.token2d = [ i.strip().split() for i in open(file) ]
        self.bcode2d = self.__parseBcode(self.token2d)
    def __parseBcode(self, token2d):
        bcode2d = []
        self.stack.append("pgm")
        last_token = None
        on_if_condition = False
        for tokens in token2d:
            bcode = []
            for token in tokens:
                top_stack = self.stack.pop()
                token_type , next_list = self.parseToken(token , top_stack)
                if token == 'IF':
                    on_if_condition = True
                while top_stack in self.parse_table and next_list is None:
                    top_stack = self.stack.pop()
                    token_type , next_list = self.parseToken(token , top_stack)
                if token_type != 'GOTO':
                    if token_type == 'line_num' and on_if_condition:
                        token_type = 'GOTO'
                        on_if_condition = False
                    bcode_tuple = RetroBasic.getBcode(token_type, token)
                    bcode.append(bcode_tuple)
                if last_token == 'GOTO' and token_type == 'line_num':
                    bcode_tuple = RetroBasic.getBcode(last_token, token)
                    bcode.append(bcode_tuple)
                    last_token = 'line_num'
                    continue
                if next_list is not None:
                    self.stack.extend(next_list[::-1])
                    while next_list is not None and next_list[0] != token_type:
                        top_stack = self.stack.pop()
                        token_type , next_list = self.parseToken(token , top_stack)
                        self.stack.extend(next_list[::-1])
                    top_stack = self.stack.pop()
                last_token = token
            bcode2d.append(bcode)
        return bcode2d
    def parseToken(self, token, top_stack):
        if top_stack in self.parse_table: #top_stack is terminal
            for terminal in self.parse_table[top_stack]:
                if terminal == 'line_num' and token in self.line_num:
                    return 'line_num' , self.parse_table[top_stack][terminal]
                if terminal == 'const' and token in self.const:
                    return 'const' , self.parse_table[top_stack][terminal]
                if terminal == 'id' and token in self.id:
                    return 'id' , self.parse_table[top_stack][terminal]
                if terminal == token:
                    return token , self.parse_table[top_stack][terminal]
        else: #top_stack is non-terminal
            if top_stack == 'line_num' and token in self.line_num:
                return 'line_num' , None
            if top_stack == 'const' and token in self.const:
                return 'const' , None
            if top_stack == 'id' and token in self.id:
                return 'id' , None
            if top_stack == token:
                return token , None
        raise Exception("Invalid token '{token}'".format(token=token))
    @staticmethod
    def getBcode(terminal_symbol, value):
        if(terminal_symbol == "line_num"): 
            return ("#line", int(value))
        if(terminal_symbol == "id"): 
            return ("#id", ord(value) - ord('A') + 1)
        if(terminal_symbol == "const"):
            return ("#const", int(value))
        if(terminal_symbol == "IF"): 
            return ("#if", 0)
        if(terminal_symbol == "GOTO"):
            return ("#goto", int(value))
        if(terminal_symbol == "PRINT"): 
            return ("#print", 0)
        if(terminal_symbol == "STOP"): 
            return ("#stop", 0)
        if(terminal_symbol == "+"): 
            return ("#op", 1)
        if(terminal_symbol == "-"): 
            return ("#op", 2)
        if(terminal_symbol == "<"): 
            return ("#op", 3)
        if(terminal_symbol == "="): 
            return ("#op", 4)

filename = str(sys.argv[1])
retro = RetroBasic(filename)
f = open('5931059421_RetroBasicIntermediate_output.txt' , 'w')
for i in retro.bcode2d:
    print(i)
    for typ , val in i:
        f.write(str(RetroBasic.bcode_list[typ]) + ' ' + str(val) + ' ')
    f.write('\n')