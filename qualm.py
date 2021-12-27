import sys
from collections import defaultdict


DEBUG = False

class EOF: ...

def print_usage():
    print(f"{sys.argv[0]} [file | -c prog] [-d]")



whitespace = " \t\n"


_has_errored = False
def error(msg, stderr):
    stderr.write(msg + '\n')
    
    global _has_errored
    _has_errored = True

    if __name__ == '__main__':
        sys.exit(-1)


def debug(interpreter):
    command = input("> ")

    if command == "help":
        print("current stack code loops run help", )
    elif command == "current":
        print(interpreter.ch())
    elif command == "stack":
        print(f"working: {interpreter.w}")
        v = [str(kv[0]) for kv in sorted(interpreter.slots.items(), key=lambda kv: kv[0])]
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
    else:
        return
    
    debug(interpreter)


class Qualm:
    def __init__(self, code, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
        self.code = code
        self.stdout = stdout
        self.stderr = stderr
        self.position = 0
        self.ch = lambda: self.code[self.position]

        self.w = 0
        self.slots = defaultdict(lambda: 0)

        self.loops = []


    def run(self):
        global _has_errored
        _has_errored = False

        while self.position < len(self.code):
            if _has_errored:
                break

            
            ch = self.ch()

            if DEBUG:
                debug(self)

            if ch == "!":
                self.stdout.write(str(self.w))
            elif ch == ",":
                error("Reading from file is not implemented yet!", self.stderr)
            elif ch == ".":
                error("Reading from stdin is not implemented yet!", self.stderr)
            elif ch == "s":
                slot = self.slot()
                self.w, self.slots[slot] = self.slots[slot], self.w
            elif ch == ">":
                slot = self.slot()
                self.slots[slot] = self.w
            elif ch == "<":
                slot = self.slot()
                self.w = self.slots[slot]
            elif ch == "v":
                if self.peek() == "'":
                    self.position += 1 # Skip '
                    value = self.string()
                else:
                    value = self.number()
                self.w = value
            elif ch == "{":
                if len(self.loops) and not self.loops[-1][1]:
                    # If encounter a { in a loop, and the position is 0,
                    # it must be the body (otherwise the position would be set)
                    self.loops[-1][1] = self.position
                elif len(self.loops) == 0:
                    # New loop
                    self.loops.append((self.position, 0, 0))

                assert(self.loops[-1][0] == self.position)
                
                if not self.condition():
                    # Skip body and delete dey loopey
                    if self.loops[-1][1] == 0:
                        # Find closing
                        while self.eat() != "}": pass
                    else:
                        self.position = self.loops[-1][2]
                    self.loops = self.loops[:-1]

            elif ch == "}":
                if len(self.loops) == 0:
                    error("Not in a loop.")
                
                self.position = self.loops[-1][0]
            else:
                error(f"Got unexpected `{ch}` at {self.position}.", self.stderr)

            self.position += 1


    def peek(self):
        if self.position + 1 >= len(self.code):
            return EOF
        return self.code[self.position + 1]
    

    def eat(self):
        if self.position + 1 >= len(self.code):
            error("EOF", self.stderr)
        self.position += 1
        return self.ch()


    def condition(self):
        """
        <expr> <op> <expr>
        """
        return False


    def slot(self):
        if not self.peek() in "0123456789":
            error(f"Expected slot (number 0-9), got `{self.peek()}`.", self.stderr)
        r = int(self.peek())
        self.position += 1
        return r

    
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

        if current in "01234567890-":
            n += current
        elif current == ".":
            n += current
            has_decimal = True
        else:
            error(f"Got `{current}`, expected numeric.", self.stderr)
            return -1

        while 1:
            next = self.peek()

            if next == ".":
                if has_decimal:
                    error("Cannot have multiple decimal points.", self.stderr)
                    return -1
                has_decimal = True
            elif not next in "0123456789":
                break

            n += self.eat()

        return float(n)



def main(filename: str):
    try:
        with open(filename, 'r') as f:
            source = f.read()
    except OSError as e:
        print(e.strerror)
        return 1

    Qualm(source).run()

    return 0


if __name__=='__main__':
    DEBUG = "-d" in sys.argv
    if DEBUG: sys.argv.remove("-d")


    if len(sys.argv) < 2:
        print_usage()
        quit()


    if "-c" in sys.argv:
        code = sys.argv[sys.argv.index("-c") + 1]
        Qualm(code).run()
        print()
    else:
        sys.exit(main(sys.argv[1]))