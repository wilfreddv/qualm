# Qualm

Qualm is an esolang, which uses a stack based memory model. 

```
Data operations:
|<delimiter>    split string on delimiter   # UNIMPLEMENTED
i               turn into integer
c               turn into character (chr()) # UNIMPLEMENTED

.               read from STDIN
!               write to STDOUT
w               working cell
s<number>       swap <number> var with w
><number>       push w to <number>
<<number>       pop <number> to w
<operation>><number> write output of previous operation to <number>
<number> can also be `w`, like sw (Using `w` is unimplemented)
v<data>         put data in w
@               index of, e.g.: "'apples pears bananas:@'apples # UNIMPLEMENTED
$               indexing # UNIMPLEMENTED
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