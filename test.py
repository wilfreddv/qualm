from os import strerror
import sys, qualm
from textwrap import dedent


class Output:
    def __init__(self):
        self.data = ""

    def write(self, s):
        self.data += s

    def __str__(self):
        return self.data

    def __eq__(self, obj):
        return str(self) == str(obj)


class Input:
    def __init__(self, data):
        self.data = data

    def readline(self):
        return self.data + "\n"


test_cases = [
        ("v'Hello World!:!", "Hello World!"),
        ("v'Hello\\nWorld!:!", "Hello\nWorld!"),
        ("vHello\\nWorld!:!", "Got `H`, expected numeric.\n"),
        # Numbers
        ("v-0.2!", "-0.2"),
        ("v-.2!", "-0.2"),
        ("v.2!", "0.2"),
        ("v-2!", "-2.0"),
        ("v2!", "2.0"),
        ("v2-", "EOF\n"),
        # ("v2>0>1!s9!s0!"),
        # Fibonacci
        ("v2>0v1>1{s1<=15{!iv' :!<1+<0s0}", "1 1 2 3 5 8 13 "),
        (".!", "Hello world!", Input("Hello world!")),
        (".!", "Hello\nworld!", Input("Hello\nworld!")),
        (".>0v123s0!s0!i", "Hello world!123", Input("Hello world!")),
        ("v1.2i!", "1"),
        (".i+3.9!i", "5", Input("2")),
]


def test(code, expected_output, stdin=sys.stdin):
    output = Output()
    qualm.Qualm(code, stdin=stdin, stdout=output, stderr=output).run()
    
    if output != expected_output:
        print(dedent(f"""
        Input:    {code}
        Expected: {expected_output}
        Output:   {output}
        """), end="")
        return False
    
    return True


if __name__=='__main__':
    passed = 0
    for test_case in test_cases:
        if test(*test_case):
            passed += 1
    print(f"{passed}/{len(test_cases)} tests passed.", end="")
    print()