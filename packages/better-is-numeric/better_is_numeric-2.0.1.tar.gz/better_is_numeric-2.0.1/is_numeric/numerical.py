"""
An enhancement of str.isnumeric()
"""

from re import fullmatch
from io import StringIO
from typing import Union

NM_ALLOW_NEGATIVE = "AN"
NM_ALLOW_DECIMALS = "AD"
NM_ALLOW_LEADING_ZERO = "AZ"
NM_ALLOW_PLUS_SIGN = "AP"
NM_RETURN_REGEX = "RX"

# DELETED FLAGS
# NM_ALLOW_COMMAS = "AC" # too difficult for now
# above: Set to the string "AC", this flag allows comma-separated numbers like 1,000,000. Useful if you don't need to actually cast to a number.
# NM_RETURN_MATCH = "RM"
# above: this used to be a flag that returned the raw match object, but that was a pretty useless feature.

def is_numeric(string:str, *flags:str) -> Union[bool, dict[str, Union[bool, str]]]:
    """
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
    """
    # removed the default flags
    flags = set(flags)
    regex = StringIO() # should be faster than being a string and using regex += "stuff"
    AllowNegative = NM_ALLOW_NEGATIVE in flags
    AllowPlus = NM_ALLOW_PLUS_SIGN in flags
    if AllowNegative or AllowPlus: # avoid re-doing checks by using variables. there are a lot of if statements here its crazy we need to conserve resources
        AllowBoth = AllowNegative and AllowPlus
        if AllowBoth: regex.write(r"(") # start group
        if AllowNegative: regex.write(r"-") # allow a minus symbol
        if AllowBoth: regex.write(r"|") # OR (not and/or)
        if AllowPlus: regex.write(r"\+") # allow a plus symbol
        if AllowBoth: regex.write(r")") # end group
        regex.write(r"?") # make the previous token (either the group if both flags are used, or the one character otherwise) optional
    if NM_ALLOW_LEADING_ZERO in flags:
        regex.write(r"\d+") # allow one or more digits. must be digits
    else:
        regex.write(r"([1-9]\d*|0)") # allows either: a non-zero digit followed by any (including zero) amount of any digits OR a single zero
    if NM_ALLOW_DECIMALS in flags:
        regex.write(r"(\.\d+)?") # allow zero or one instances of: a decimal point followed by one or more digits
    regex = regex.getvalue()
    match = fullmatch(regex, string) # instead of writing to the StringIO twice to ensure the whole string matches, we just use fullmatch
    MatchBool = bool(match) # we always need this so there is no need to set it separately in dict and bool output
    if NM_RETURN_REGEX in flags: return {"numeric": MatchBool, "regex": regex}
    else: return MatchBool

__all__ = [
    "NM_ALLOW_NEGATIVE", "NM_ALLOW_DECIMALS", "NM_ALLOW_LEADING_ZERO", "NM_ALLOW_PLUS_SIGN", "NM_RETURN_REGEX",
    "is_numeric"
]