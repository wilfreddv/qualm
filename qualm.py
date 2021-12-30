import sys
from collections import defaultdict


DEBUG = False

class EOF: ...

def print_usage():
    print(f"Usage: {sys.argv[0].split('/')[-1]} [file | -c prog] [-d]")


whitespace = " \t\n"


def debug(interpreter):
    command = input("> ")

    if command == "help":
        print("current stack code loops run help quit", )
    elif command == "current":
        print(interpreter.ch())
    elif command == "stack":
        print(f"working: {interpreter.w}")
        v = [str(kv[1]) for kv in sorted(interpreter.slots.items(), key=lambda kv: kv[0])]
        print(" | ".join(v))
    elif command == "code":
        print(interpreter.code)
        print(" " * interpreter.position, end="^\n")
    elif command == "loops":
        for loop in interpreter.loops:
            print(loop)
    elif command == "run":
        global DEBUG
        DEBUG = False
        return
    elif command == "quit":
        sys.exit()
    else:
        return
    
    debug(interpreter)


class Qualm:
    def __init__(self, code, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
        self.code = code
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.position = 0
        self.ch = lambda: self.code[self.position]

        self.w = 0
        self.slots = defaultdict(lambda: 0)

        self.loops = []

        self._has_errored = False

        self.operators = {
            "!": self.print,
            ".": self.read,
            "s": self.swap,
            ">": self.push,
            "<": self.pull,
            "v": self.data,
            "{": self.loop_open,
            "}": self.loop_close,
            "+": self.plus,
            "-": self.minus,
            "*": self.mul,
            "/": self.div,
            "%": self.mod,
            "w": self.get_w,
            "i": self.asint,
            "c": self.aschr,
            "o": self.asord,
            "|": self.split,
            "@": self.indexof,
            "$": self.getat,
        }


    def print(self):
        output = self.w

        next = self.peek()
        if next == "i":
            self.eat()
            output = int(output)
        elif next == "c":
            self.eat()
            output = chr(output)
        elif next == "o":
            self.eat()
            output = ord(output)

        self.stdout.write(str(output))
    
    def read(self):
        self.w = self.stdin.readline().strip("\n")

    def swap(self):
        slot = self.slot()
        self.w, self.slots[slot] = self.slots[slot], self.w

    def push(self):
        slot = self.slot()
        self.slots[slot] = self.w

    def pull(self):
        slot = self.slot()
        self.w = self.slots[slot]

    def data(self):
        if self.peek() == "'":
            self.position += 1 # Skip '
            value = self.string()
        else:
            value = self.number()
        self.w = value

    def loop_open(self):
        if len(self.loops) and (not self.loops[-1][1] or self.loops[-1][1] == self.position):
            # If encounter a { in a loop, and the position is 0,
            # it must be the body (otherwise the position would be set)
            self.loops[-1][1] = self.position
            return # And we go on
        elif len(self.loops) == 0:
            # New loop
            self.loops.append([self.position, 0, 0])
        
        if not self.condition():
            # Skip body and delete dey loopey
            if self.loops[-1][1] == 0:
                # Find closing
                while self.eat() != "}": pass
            else:
                self.position = self.loops[-1][2]
            self.loops = self.loops[:-1]

    def loop_close(self):
        if len(self.loops) == 0:
            self.error("Not in a loop.")
        
        self.loops[-1][2] = self.position
        self.position = self.loops[-1][0]-1

    
    def plus(self):
        if self.peek() == "'":
            self.position += 1 # Skip '
            val = self.string()
        elif self.peek() == "<":
            self.position += 1
            val = self.slots[self.slot()]
        else:
            val = self.number()
        
        self.w += val


    def minus(self):
        val = self.number()
        self.w -= val


    def mul(self):
        val = self.number()
        self.w *= val

    
    def div(self):
        val = self.number()
        self.w /= val


    def mod(self):
        val = self.number()
        self.w %= val

    
    def get_w(self):
        return self.w


    def asint(self):
        self.w = int(self.w)

    
    def aschr(self):
        self.w = chr(self.w)


    def asord(self):
        self.w = ord(self.w)

    
    def split(self):
        delim = self.eat()

        if delim == "\\":
            next = self.eat()
            if next == "n": delim = "\n"
            elif next == "t": delim = "\t"
            elif next == "\\": delim = "\\"
            else:
                self.error("Bad escape character for delimiter", self.stderr)
        
        if delim in self.w: # Don't split if there's no delimiter
            self.w = self.w.split(delim)


    def indexof(self):
        if self.peek() == "'":
            self.eat()
            item = self.string()
        elif self.peek() in "0123456789":
            item = self.number()
        elif self.peek() == "<":
            self.eat()
            item = self.slots[self.slot()]
        else:
            self.error(f"Invalid item to get index of at position {self.position}.", self.stderr)

        self.w = self.w.index(item)


    def getat(self):
        if self.peek() == "<":
            self.eat()
            at = int(self.slots[self.slot()])
        else:
            at = int(self.number())
        
        self.w = self.w[at]


    def run(self):
        self._has_errored = False

        while self.position < len(self.code):
            if self._has_errored:
                break
            
            ch = self.ch()

            if DEBUG:
                debug(self)

            
            if not ch in self.operators:
                self.error(f"Got unexpected `{ch}` at {self.position}.", self.stderr)
                continue
            self.operators[ch]()
            

            self.position += 1


    def peek(self):
        if self.position + 1 >= len(self.code):
            return EOF
        return self.code[self.position + 1]
    

    def eat(self):
        if self.position + 1 >= len(self.code):
            self.error("EOF", self.stderr)
            return EOF
        self.position += 1
        return self.ch()


    def condition(self):
        """
        <expr> <op> <expr>
        """
        
        ch = self.peek()
        if ch in ".,ws<v":
            self.position += 1
            self.operators[ch]()
            left = self.w
        elif self.peek() == "'":
            self.position += 1 # Skip '
            left = self.string()
        else:
            left = self.number()
            

        op = self.eat()
        if op == "=":
            pass
        else:
            if self.eat() != "=":
                self.error(f"Expected `=`, got {self.code[self.position-1]}", self.stderr)
            op += "="


        ch = self.peek()
        if ch in ".,ws<v":
            self.position += 1
            self.operators[ch]()
            right = self.w
        elif self.peek() == "'":
            self.position += 1 # Skip '
            right = self.string()
        else:
            right = self.number()


        return {
            "=": left == right,
            "!=": left != right,
            "<=": left <= right,
            ">=": left >= right,
        }[op]


    def slot(self):
        ch = self.eat()

        if ch == "w":
            ch = str(self.w)

        if not ch in "0123456789":
            self.error(f"Expected slot (number 0-9), got `{self.peek()}`.", self.stderr)

        return int(ch)

    
    def string(self):
        """
        Parse a string literal
        """

        if DEBUG:
            debug(self)

        s = ""
        while 1:
            if self.peek() == "\\":
                self.eat()
                next = self.peek()
                if next == "n":
                    s += "\n"
                elif next == "r":
                    s += "\r"
                elif next == "t":
                    s += "\t"
                elif next == "\\":
                    s += "\\\\"
                elif next == ":":
                    s += ":"
                self.eat()
                continue
            if self.peek() == ":":
                self.eat()
                break

            s += self.eat()
        return s


    def number(self):
        """
        Parse a number
        """

        n = ""
        has_decimal = False
        current = self.eat()

        if current is EOF: return 0

        if current == "w":
            return self.w

        if current in "01234567890-":
            n += current
        elif current == ".":
            n += current
            has_decimal = True
        else:
            self.error(f"Got `{current}`, expected numeric.", self.stderr)
            return -1

        while 1:
            next = self.peek()

            if next == ".":
                if has_decimal:
                    self.error("Cannot have multiple decimal points.", self.stderr)
                    return -1
                has_decimal = True
            elif not str(next) in "0123456789":
                break

            n += self.eat()

        return float(n)


    def error(self, msg, stderr):
        stderr.write(msg + '\n')
        
        self._has_errored = True

        if __name__ == '__main__':
            sys.exit(-1)


def main():
    global DEBUG

    DEBUG = "-d" in sys.argv
    if DEBUG: sys.argv.remove("-d")


    if len(sys.argv) < 2:
        print_usage()
        quit()


    if "-c" in sys.argv:
        code = sys.argv[sys.argv.index("-c") + 1]
        Qualm(code).run()
    else:
        try:
            with open(sys.argv[1], 'r') as f:
                source = f.read()
        except OSError as e:
            print(e.strerror)
            return 1
    
        Qualm(source).run()

    return 0


if __name__=='__main__':
    sys.exit(main())
