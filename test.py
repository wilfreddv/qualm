import sys, qualm
from textwrap import dedent



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
        ("v2-", "Got unexpected `-` at 2.\n"),
        ("v2>0>1!s9!s0!"),
        # Fibonacci
        ("v1>0>1{s1=7{s1+1s1!v' !w+<0s0}", "1 1 2 3 5 8 13"),
]


class Output:
    def __init__(self):
        self.data = ""

    def write(self, s):
        self.data += s

    def __str__(self):
        return self.data

    def __eq__(self, obj):
        return str(self) == str(obj)



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