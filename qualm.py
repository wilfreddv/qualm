#!/usr/bin/env python3

import sys
import socket
from collections import defaultdict


DEBUG = False
DEBUG_STEPS_LEFT = 0
WHITESPACE = " \t\n"


class EOF:
    ...


class QualmSocket:
    def __init__(self, host, port):
        print(f"{host = }\n{port = }")
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        self.s.listen(1)
        self.conn, self.addr = None, None

    def read(self):
        if self.conn:
            self.conn.close()

        self.conn, self.addr = self.s.accept()
        data = self.conn.recv(1024).decode('utf-8')
        return data
    
    def write(self, data):
        if not self.conn:
            raise ConnectionError()

        self.conn.send(data.encode())
        self.conn.close()
        self.conn = None

    def flush(self):
        ...


def print_usage():
    print(f"Usage: {sys.argv[0].split('/')[-1]} FILE [-d]")


def debug(interpreter):
    command, *args = input("> ").split() or [""]

    if command == "help":
        print("current stack code step\n"
              "loops run help quit")
    elif command == "current":
        print(interpreter.ch())
    elif command == "stack":
        print(f"working: {interpreter.w}")
        v = [str(kv[1]) for
             kv in sorted(interpreter.slots.items(), key=lambda kv: kv[0])]
        # TODO: show files mo better
        print(" | ".join(v))
    elif command == "code":
        print(interpreter.code)
        print(" " * interpreter.position, end="^\n")
    elif command == "step":
        try:
            steps = int(args[0])
        except (ValueError, IndexError):
            print("Invalid number...")
            debug(interpreter)
            return
        global DEBUG_STEPS_LEFT
        DEBUG_STEPS_LEFT = steps
        return
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
    def __init__(self, code, stdin=sys.stdin,
                 stdout=sys.stdout, stderr=sys.stderr):
        self.code = code
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.position = 0
        self.ch = lambda: self.code[self.position]

        self.w = 0
        self.slots = defaultdict(lambda: 0)

        self.loops = []
        self.functions = []
        self.call_stack = []  # (return address, loops)

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
            "f": self.asfloat,
            "c": self.aschr,
            "o": self.asord,
            "|": self.split,
            "@": self.indexof,
            "$": self.getat,
            "&": self.open_file,
            "(": self.func_open,
            ")": self.func_close,
            "~": self.func_call,
        }

    def print(self):
        output = self.w

        next = self.peek()
        if next == "i":
            self.eat()
            output = int(float(output))
        if next == "f":
            self.eat()
            output = float(output)
        elif next == "c":
            self.eat()
            output = chr(output)
        elif next == "o":
            self.eat()
            output = ord(output)

        # Change file descriptor, standard is stdout
        if self.peek() == "&":
            self.eat()

            file_handle = self.slots[self.slot()]
            try:
                file_handle.write("".join(output))
                file_handle.flush()
            except AttributeError:
                self.error("Cannot write to non-file handle.", self.stderr)
            except ConnectionError:
                self.error("Problem writing to socket.", self.stderr)
        else:
            self.stdout.write(str(output))

    def read(self):
        if self.peek() == "&":
            self.eat()

            if self.peek() == "<":
                self.eat()
                file_handle = self.slots[self.slot()]
            else:
                file_handle = self.w

            try:
                self.w = file_handle.read()
            except AttributeError:
                self.error("Cannot read from non-file handle.", self.stderr)
        else:
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
            self.position += 1  # Skip '
            value = self.string()
        else:
            value = self.number()
        self.w = value

    def loop_open(self):
        if len(self.loops) and (self.loops[-1][1] == 0 or
                                self.loops[-1][1] == self.position):
            # If encounter a { in a loop, and the position is 0,
            # it must be the body (otherwise the position would be set)

            self.loops[-1][1] = self.position
            if DEBUG:
                print(f"Found loop body: {self.loops[-1]}")

            return  # And we go on
        elif len(self.loops) == 0 or self.loops[-1][0] != self.position:
            # If the position isn't the start of the loop,
            # it must be a new one
            self.loops.append([self.position, 0, 0])

            if DEBUG:
                print(f"Found new loop: {self.loops[-1]}")

        if not self.condition():
            # Skip body and delete dey loopey
            if self.loops[-1][1] == 0:
                # Find closing
                # FIXME: doesn't work for braces in a string
                while self.eat() != "{":  # Parse until body
                    pass

                depth = 1
                while ch := self.eat():
                    if ch == '{':
                        depth += 1
                        while self.eat() != "{":  # Parse until body
                            pass
                    elif ch == '}':
                        depth -= 1

                    if depth == 0:  # Reached end of loop body
                        break
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
            self.position += 1  # Skip '
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
        self.w = int(float(self.w))
    
    def asfloat(self):
        self.w = float(self.w)

    def aschr(self):
        self.w = chr(self.w)

    def asord(self):
        self.w = ord(self.w)

    def split(self):
        delim = self.eat()

        if delim == "\\":
            next = self.eat()
            if next == "n":    delim = "\n"
            elif next == "t":  delim = "\t"
            elif next == "\\": delim = "\\"
            else:
                self.error("Bad escape character for delimiter", self.stderr)

        if delim in self.w:  # Don't split if there's no delimiter
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

    def open_file(self):
        try:
            filename = self.w
            if filename == "__SOCKET":
                host = self.slots[0]
                port = int(self.slots[1])
                self.w = QualmSocket(host, port)
            else:
                mode = ["r", "w", "r+", "a"][int(self.slots[0])]
                self.w = open(filename, mode)
        except ValueError:
            self.error(f"Invalid port number: {port}", self.stderr)
        except FileNotFoundError:
            self.error(f"File `{filename}` does not exist.", self.stderr)
        except (TypeError, IndexError):
            self.error(f"Invalid mode: {self.slots[0]}", self.stderr)

    def func_open(self):
        self.functions.append(self.position)
        
        while self.peek() != ")": self.eat()
        self.eat()
        
        self.w = self.functions[-1]

    def func_close(self):
        if len(self.call_stack) > 0:
            self.position, self.loops = self.call_stack.pop()
        else:
            self.error(f"Cannot close unopened function at position: {self.position}", self.stderr)

    def func_call(self):
        if (not isinstance(self.w, (float, int)) and
            int(self.w) not in self.functions):
            self.error("Invalid function", self.stderr)
        else:
            fptr = int(self.w)
            self.call_stack.append((self.position, self.loops))
            self.loops = []
            self.position = fptr

    def run(self):
        self._has_errored = False

        while self.position < len(self.code):
            if self._has_errored:
                break

            ch = self.ch()

            if DEBUG:
                global DEBUG_STEPS_LEFT
                if DEBUG_STEPS_LEFT == 0:
                    debug(self)
                else:
                    DEBUG_STEPS_LEFT -= 1

            if ch in self.operators:
                self.operators[ch]()
            elif ch in WHITESPACE:
                # Ignore whitespace
                pass
            else:
                self.error(f"Got unexpected `{ch}` at {self.position}.", self.stderr)
                break

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
            self.position += 1  # Skip '
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
            self.position += 1  # Skip '
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

        if ch in "0123456789":
            while self.peek() in "0123456789":
                ch += self.eat()
        else:
            self.error(f"Expected slot (number 0-9), got `{ch}`.", self.stderr)
            return -1

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

        # Make embedded Qualm not break
        if __name__ == '__main__':
            sys.exit(-1)


def main():
    global DEBUG

    DEBUG = "-d" in sys.argv
    if DEBUG: sys.argv.remove("-d")

    if len(sys.argv) < 2:
        print_usage()
        quit()

    try:
        with open(sys.argv[1], 'r') as f:
            source = f.read()
    except OSError as e:
        print(e.strerror)
        return 1

    Qualm(source).run()

    return 0


if __name__ == '__main__':
    sys.exit(main())
