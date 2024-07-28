#!/usr/bin/env python3

from validdict import *

# Expanding beyond literal schemas, the library provides type validation for scalar values


# The schema is declared with scalar validator objects
# Supported validators are:
# - Num() for numbers (int and float)
# - Bool() for boolean values
# - Str() for strings
# - Regex() for string values that must match a regular expression
schema = Schema({
    "int": Num(),
    "float": Num(),
    "bool": Bool(),
    "string": Str(),
    "regex": Regex(r"\w+@\w+\.com") # trivial email regex
})

# Values must be of the prescribed type
results = schema.validate({
    "int": 1,
    "float": 1.0,
    "string": "string",
    "bool": True,
    "regex": "example@email.com"
})
assert results
print(results)

# Values of the incorrect type will fail validation
results = schema.validate({
    "int": "string value",
    "float": "string value",
    "string": 1,
    "bool": "string value",
    "regex": "not an email"
})
assert not results
print(results)
#
# '<dict>' must be a map like: { RequiredKey(): Num(), RequiredKey(): Num(), RequiredKey(): <snip> = 'PASS'
#   RequiredKey('int'):'int' must be type 'str' with value 'int' = 'PASS'
#   int:'string value' must be type in ('int', 'float') = 'FAIL'
#   RequiredKey('float'):'float' must be type 'str' with value 'float' = 'PASS'
#   float:'string value' must be type in ('int', 'float') = 'FAIL'
#   RequiredKey('string'):'string' must be type 'str' with value 'string' = 'PASS'
#   string:'1' must be type 'str' = 'FAIL'
#   RequiredKey('bool'):'bool' must be type 'str' with value 'bool' = 'PASS'
#   bool:'string value' must be type 'bool' = 'FAIL'
#   RequiredKey('regex'):'regex' must be type 'str' with value 'regex' = 'PASS'
#   regex:'not an email' must be type 'str' with value matching '\w+@\w+\.com' = 'FAIL'
#


# Scalar validators can be parameterized with additional constraints beyond just type checking
schema = Schema({
    "int": Num(1, 2, 3, range(4, 10)),                      # one or more specific numerical values can be specified explicitly or by range()
    "float": Num(gte=0.0, lte=1.0),                         # constraints can be defined with greater/less than params (gt, gte, lt, lte)
    "bool": Bool(True),                                     # boolean values can be constrained to True or False
    "string": Str("aaa", "bbb", case_sensitive=False),      # string values can be constrained to specific values, case sensitivity can be toggled
    "regex": Regex(r"\w+@\w+\.com", r"\w+@\w+\.org")        # multiple regular expressions can be specified, patterns can be pre-compiled
})

# Values must meet the constraints to pass validation
assert schema.validate({
    "int": 1,
    "float": 0.5,
    "bool": True,
    "string": "AAA",
    "regex": "example@email.com"
})

# Out of constraint values will fail validation
results = schema.validate({
    "int": 100,
    "float": 1.1,
    "bool": False,
    "string": "ccc",
    "regex": "example@email.net"
})
assert not results
print(results)
#
# '<dict>' must be a map like: { RequiredKey(): Num(), RequiredKey(): Num(), RequiredKey(): <snip> = 'PASS'
#   RequiredKey('int'):'int' must be type 'str' with value 'int' = 'PASS'
#   int:'100' must be type in ('int', 'float') with value one of ('1', '2', '3', 'range(4, 10)') = 'FAIL'
#   RequiredKey('float'):'float' must be type 'str' with value 'float' = 'PASS'
#   float:'1.1' must be type in ('int', 'float') with value '>= 0.0' and '<= 1.0' = 'FAIL'
#   RequiredKey('bool'):'bool' must be type 'str' with value 'bool' = 'PASS'
#   bool:'False' must be type 'bool' with value 'True' = 'FAIL'
#   RequiredKey('string'):'string' must be type 'str' with value 'string' = 'PASS'
#   string:'ccc' must be type 'str' with value one of ('aaa', 'bbb') = 'FAIL'
#   RequiredKey('regex'):'regex' must be type 'str' with value 'regex' = 'PASS'
#   regex:'example@email.net' must be type 'str' with value matching one of ('\w+@\w+\.com', '\w+@\w+\.org') = 'FAIL'
#
