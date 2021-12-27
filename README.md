|<delimiter>    split string on delimiter
.               read from STDIN
,<filename>     read from file
!               write to STDOUT
w               working cell
s<number>       swap <number> var with w
><number>       push w to <number>
<<number>       pop <number> to w
<operation>><number> write output of previous operation to <number>
<number> can also be `w`, like sw
v<data>:        put data in w
@               index of, e.g.: "'apples pears bananas:@'apples
$               indexing
"...            array, space separated
'...            stringular data
{<condition>{...} loop
<number>+<number> add
<number>-<number> sub
<number>*<number> mul
<number>/<number> div
<number>%<number> mod
<number>=<number> equals
<expr>=!<expr>    neq
<expr><=<expr>    smaller
<expr>>=<expr>    bigger


maximum of 10 slots (0-9)



Hello world:
v'Hello World!:!

v write into working cell
' denotes stringular data
! prints


v"'0 one two three four five six seven eight nine ten:>0.|,>1<0@<1$0>2
v"'   #write into working, array of strings
0 one two three four five six seven eight nine ten/
>0      # move it to cell 0
.|,>1   # read from stdin, split on ,, move to cell 1
<0      # move cell 0 into w
@       # get the index
<1      # of cell 1
$0      # 's 0th element
>2      # and store it into cell 2


Fibonacci:      v implied w
v1>0>1{s1=10{s1+1s1!v' !w+<0s0}