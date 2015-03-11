Lester
======

#### A Study in Minimal Interpreted Language Design ####

Syntax
------

Lester operates in prefix and postfix modes.

Lester does not define token separation characters.  The default is one or
more ASCII spaces (0x20).

Lester assumes statements are enclosed in a matching pair of any of the three
_normal_ grouping characters: () [] {}.  Grouping provides explicit precedence
of operations, optional parameters to functions, and multiple statements on
the same line.

A statement consists of a verb and zero or more arguments.  Without any
grouping characters, the entire line is assumed to be single statement.

Grouping characters also leave a statement "open" until the matching
character.  Thus, a statement can span multiple lines for readability.

Functional blocks of statements are not considered syntactically special.
Each sub-statement then becomes an argument to an outer statement.

Lester does not define string quotation characters.  The defaults are
apostrophes (0x27) and quotation marks (0x22).  The default escaping character
is a back slash (0x5C).

The interpretor allows manipulation of its delimiting characters at runtime
through a set of built-in functions.

Use-defined Symbols
-------------------

Users define their own symbols for purposes of variable substitution in
statements and function names.

The Stack
---------

Most programs will benefit from efficient use of the program stack.  Each
program has one master stack, and can add additional/nested stacks as needed.
The stack is how functions communicate with one another:  Parameters are
pushed onto the stack before calling, and return values are pushed onto the
stack before returning.  As a function retrieves its arguments, the parameters
are popped/removed from the stack.

The stack can be used to maintain simple order of operations without using
grouping characters.

The stack can be directly manipulated using built-in stack manipulation
functions.

Functions with a variable number of arguments are given a limit on the number
of arguments they can pop off the stack before it runs dry.  The limit is set
by calling the function with a list of arguments on a single line, or by
enclosing the function call within grouping characters.

Built-in Verbs
--------------

### Variable Assignment ###
  - set
  - =

### Statement Binding ###
  - :=

### Stack Manipulation ###
  - push (default verb)
  - pop
  - swap
  - drop

### Math ###
  - +
  - -
  - *
  - /
  - power
  - log

### Bitwise Operations ###
  - ~
  - |
  - &
  - ^
  - lshift
  - rshift

### Boolean Logic ###
  - not
  - or
  - and
  - xor

### Comparisons ###
  - ==
  - <
  - >
  - <=
  - >=

Decisions and Execution Control
-------------------------------

### Execution Blocks ###

A block of execution is considered any grouped list of statements.  For
example:

  := block [
    set a 1
    set b 2
    push 3
    + a
    + b
  ]

The statement binding verb `:=` works like the `set` or `=` verbs except that
is lets the interpretor know that this block should not be immediately
resolved.  This provides a sort of sub-routine feature by "calling" the
execution block using either the user's identifier (if it doesn't conflict
with a built-in verb), or explicitly passing the identifier to the `call`
function:

  block
  # stack is now: [ 6 ]

  call block
  # alternate "explicit" syntax if the user is avoiding a built-in verb

### Functions ###

Functions are execution blocks that may accept parameters and return values
using the stack:

  := add [
    = b pop
    = a pop
    + a b
  ]

  # can be called as a normal verb:
  add 1 2
  # stack is now: [ 3 ]

  # or, called using the stack explicitly
  push 1
  push 2
  add
  # stack is now: [ 3 ]

A function can use an optional auto-pop feature when defining a list of
parameters when binding the statement:

  := subtract [ - a b ] a b

This defines a function that must always have two items on the stack before
being called that will be consumed by the function when called.  If the stack
would be emptied before providing enough parameters, the interpretor throws
an exception indicating it can't call the function.

A function can also specify parameters as optional.  If calling the function
doesn't have enough parameters passed, a default value is automatically
set in the parameter.

  := optifun [ + a + b c ] a [ := b 2 ] [ := c 3 ]
  optifun 4
  # stack is now: [ 9 ]
  push 2
  push 1
  optifun
  # stack is now: [ 6 ]

### Controlling Execution ###

Execution is controlled by selecting which execution blocks to call, and
which ones to ignore.  Execution blocks may be anonymous or user-defined
verbs.

Selection of an execution block can be made using an if-test built-in
function:

  if and a b + a b push a
  # if a and b evaluate to boolean true, add them and push to stack,
  #  otherwise, just push a to stack
  # for clarity, this does the same thing:
  [ if [ and a b ] [ + a b ] [ push a ] ]


