# PCIO

Input from stdin by format. Values can distrubuted on different lines.

``` python
import pcio

# Input two integer numbers as tuple
a,b=pcio.input('ii')

# Input a list of integer numbers
arr=pcio.input(100,'i')

# Input a list of pair float numbers
arr=pcio.input(100,'ff')

# Input one symbol
pcio.input(1)

# Input one line by default
s=pcio.input()
```
Function raises EOFError on end of file and ValueError if value is not a number.

Input Format|Description
--|--
i | Integer number, skip spaces before number
f | Float number, skip spaces before number
w | Word, skip spaces before word
c | One character as string
l | One line as a string
L | One line with new line as a string
a | All input as one string


Also specialized variants

``` python
import pcio

a=pcio.input_int()
b=pcio.input_float()
c=pcio.input_char()
d=pcio.input_word()
e=pcio.input_line()
```

Print according to the format specified by the first argument.

``` python
import pcio

# Print by format
pcio.print("Hello, {}!\n", "world")

# Print a list separated by space and new line
arr=[1,2,3,10,12.2,'a']
pcio.println(arr)
# 1 2 3 10 12.2 a
pcio.println('{:02i}',arr) 
# 01 02 03 10 12 a
pcio.println('{!r}',arr)
# [1,2,3,10,12.2,'a']
```

If the first argument is not a string then the format ``'{} {} {}'`` is used where the number of parentheses is equal to the number of arguments.

Format contain "replacement fields" surrounded by curly braces ``{}``.
Anything that is not contained in braces is considered literal text, which is copied unchanged to the output. 
If you need to include a brace character in the literal text, it can be escaped by doubling: ``{{`` and ``}}``.

```
replacement_field ::=  "{" [arg_index] [format_spec] "}"
format_spec ::=  "!" "r" | ":" [align][sign]["0"][width]["." precision][type]
align  ::=  "<" | ">" | "^"
sign            ::=  "+" | "-"
width           ::=  digit+
precision       ::=  digit+
type            ::=  "i" | "d" | "o" | "x" | "X" | "e" | "E" | "f" | "F" | "g" | "G" | "s"
```

``"!r"`` calls repr() to print.

The meaning of the various *alignment* options is as follows:

Option|Meaning
--|--
'<' | Forces the field to be left-aligned within the available space (this is the default for most objects).
'>'|Forces the field to be right-aligned within the available space (this is the default for numbers).
'^'|Forces the field to be centered within the available space.


The *sign* option is only valid for number types, and can be one of the following:

Option|Meaning
--|--
'+'| indicates that a sign should be used for both positive as well as negative numbers.
'-'| indicates that a sign should be used only for negative numbers (this is the default behavior).

*width* is a decimal integer defining the minimum total field width, including any prefixes, separators, and other formatting characters. If not specified, then the field width will be determined by the content.
Preceding the width field by a zero ('0') character enables zero-padding for numeric types.

The *precision* is a decimal integer indicating how many digits should be displayed after the 
decimal point for presentation types 'f' and 'F', or before and after the decimal point 
for presentation types 'g' or 'G'. 
For string presentation types the field indicates the maximum field size - in other words, how many
characters will be used from the field content. The precision is ignored for integer presentation types.

The available *types* are:

Type|Meaning
--|--
's'| String format. Numbers is converted to the string ('g' or 'd') and precision is ignored.
'd', 'i' | Decimal Integer. Outputs the number in base 10. String the 's' format is used instead.
'o' | Octal format. Outputs the number in base 8. For float numbers and string the 'g' and 's' format is used instead.
'x', 'X' | Hex format. Outputs the number in base 16. 
'f', 'F' | Fixed-point notation. For strings the 's' format is used and precision is ignored.
'e', 'E' | Scientific notation.
'g', 'G' | General format.

Select input/output encoding (``'utf-8'``, ``'cp1251'`` or ``'cp866'``).

``` python
# Select encoding 
pcio.encoding('cp1251')
```
