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
        # Fibonacci
        ("v2>0v1>1{s1<=15{!iv' :!<1+<0s0}", "1 1 2 3 5 8 13 "),
        (".!", "Hello world!", Input("Hello world!")),
        (".!", "Hello\nworld!", Input("Hello\nworld!")),
        (".>0v123s0!s0!i", "Hello world!123", Input("Hello world!")),
        ("v1.2i!", "1"),
        (".i+3.9!i", "5", Input("2")),
        ("v1s0<w!i", "1"),
        ("v'A:!oo!!cc!", f"{ord('A')}{ord('A')}AA"),
        ("v'hello world:| !", "['hello', 'world']"),
        ("v'hello world:| >0$1!<0$-1!v0s0$<0!", "worldworldhello"),
        ("v42>0v0isw!i", "42"),
        ("v'Hello world:\n!\n", "Hello world"),
        ("v'Hello world:>!", "Expected slot (number 0-9), got `!`.\n"),
        ("    v'Hello World:    !", "Hello World"),
        ("v0{w=1{{w>=3{v'Hello world!\n:!}v1}", ""),
        (" (<0!v'\n:!)>9v'Hello:>0<9~v'world!:>0<9~", "Hello\nworld!\n"),
        ("v1337>42v'Number at 42 is\: :!<42!i", "Number at 42 is: 1337"),
        (".f!", "123.1", Input("123.1")),
        (".i!", "123", Input("123")),
        (".!f", "123.1", Input("123.1")),
        (".!i", "123", Input("123")),
        ("v'1234567890:@$!", "10"),
        ("v'b b c d:| $=0,'a:!", "['a', 'b', 'c', 'd']"),
        ("v42>0v'a b c d:| $=3,<0!", "['a', 'b', 'c', 42]")
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


if __name__ == '__main__':
    passed = 0
    for test_case in test_cases:
        if test(*test_case):
            passed += 1
    print(f"{passed}/{len(test_cases)} tests passed.", end="")
    print()
