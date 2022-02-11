# Qualm

Qualm is an esolang, which uses a cell-based memory model. 


## Installation
You can install Qualm from PyPi: `python3 -m pip install --user qualm`

Or clone the repository:
```
$ git clone https://github.com/wilfreddv/qualm.git
$ cd qualm
$ python3 -m pip install --user .
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

&               open file
.               read from STDIN
.&[<]<slot>     read from file handle
!               write to STDOUT
!&<slot>        write to file handle
w               working cell
s<number>       swap <number> var with w
><number>       push w to <number>
<<number>       pop <number> to w
<operation>><number> write output of previous operation to <number>
<number> can also be `w`, like sw
v<data>         put data in w
'...:           string data
{<condition>{...} loop
(...)             function definition
~                 call a function
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


## Opening a file
When the `&` instruction is issued, Qualm will open a file with the following parameters:

* `w`: filename
* `0`: the mode (0, 1, 2, 3 for r, w, r+, a respectively)

If `w` is `__SOCKET`, it opens a TCP server-socket that will listen. The arguments are `host` and `port`.

A file handle will be returned to `w`. This can be used for reading and writing.

## Functions
A function is defined using parentheses. After the definition, the pointer to the function will be stored in `w`.
When a call `~` is issued, the pointer will be read from `w`.
The return address is remembered automatically.

## Examples
#### Hello world
```
Hello world:
v'Hello World!:!

v write into working cell
' denotes string data
! prints
```

#### Fibonacci sequence
`v2>0v1>1{s1<=23416728348467685{!iv' :!<1+<0s0}`
