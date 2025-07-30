# numerical

Python library I made to learn regex and to have a better version of str.isnumeric()

PyPI rejected the name without telling me why (too similar to numerics?), so its called better-is-numeric there.

Supports decimals and negative numbers, managed by flags.

Even if you don't need to support decimals or negative numbers, this is
still better than str.isnumeric(), since that function for some reason
counts exponents (⅐, for example) as numeric.

Should work down to Python 3.9.

Importing is kind of ugly, maybe I'll fix it one day. In the meantime, you can avoid this and the PyPI name by just downloading the code from the Codeberg repository and putting it in the same directory as your program, for a simple `from numerical import *`

Here's some example code:

```python
from is_numeric.numerical import *

print(is_numeric("1", NM_ALLOW_NEGATIVE, NM_ALLOW_DECIMALS, NM_ALLOW_LEADING_ZERO))
```

This will print True, since the NM_ALLOW flags do not require, they only allow.
If you want to REQUIRE a negative number or decimals, simply check:

`if "-" in whatever_string_you_are_checking`

`if "." in whatever_string_you_are_checking`

I've copied this from the docstring(?) of the function, since it describes the flags:

```
This function uses a "flag" system to control what's allowed and what isn't.
You can pass these as individual arguments, you don't need a list or set or anything.
Certain flags switch the function to dictionary output, to include whatever data you requested.
The simple boolean output is still included in the dictionary output, in the "numeric" field.
The flags are in variables, but you can also use their string values.
1: NM_ALLOW_NEGATIVE - Set to the string "AN", this flag allows negative numbers.
2: NM_ALLOW_DECIMALS - Set to the string "AD", this flag allows numbers with decimals.
3: NM_ALLOW_LEADING_ZERO - Set to the string "AZ", this flag allows "invalid" numbers like 01.
4: NM_ALLOW_PLUS_SIGN - Set to the string "AP", this flag allows explicitly positive numbers, such as +2.
5: NM_RETURN_REGEX - Set to the string "RX", this flag uses dictionary output and returns the constructed regex inside the "regex" field.
```

If you want no flags, just don't give any.
That is, JUST give the string. `is_numeric(string)`