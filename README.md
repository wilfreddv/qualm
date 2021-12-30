# Qualm

Qualm is an esolang, which uses a stack based memory model. 


## Installation
You can install Qualm from PyPi: `python3 -m pip install -U qualm`

Or clone the repository:
```
$ git clone https://github.com/wilfreddv/qualm.git
$ cd qualm
$ python3 -m pip install -U .
```

## Documentation
```
Data operations:
|<delimiter>    split string on delimiter
@               index of, e.g.: "'apples pears bananas:@'apples
$               indexing
i               turn into integer
c               turn into character (chr())
o               turn into ascii value (ord())

.               read from STDIN
!               write to STDOUT
w               working cell
s<number>       swap <number> var with w
><number>       push w to <number>
<<number>       pop <number> to w
<operation>><number> write output of previous operation to <number>
<number> can also be `w`, like sw
v<data>         put data in w
"...            array, space separated # UNIMPLEMENTED
'...:           stringular data
{<condition>{...} loop
<number>+<number> add
<number>-<number> sub
<number>*<number> mul
<number>/<number> div
<number>%<number> mod
<number>=<number> equals
<expr>!=<expr>    neq
<expr><=<expr>    smaller
<expr>>=<expr>    bigger
```


## Examples
#### Hello world
```
Hello world:
v'Hello World!:!

v write into working cell
' denotes stringular data
! prints
```

#### Fibonacci sequence
`v2>0v1>1{s1<=23416728348467685{!iv' :!<1+<0s0}`
