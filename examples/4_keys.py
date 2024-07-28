#!/usr/bin/env python3

from validdict import *

# Keys can be required or optional
# - RequiredKey() will fail if the key is missing
# - OptionalKey() will pass if the key is missing
# - OtherKeys() will allow any other keys to be present

schema = Schema({
    RequiredKey("key1"): Str(),
    OptionalKey("key2"): Str(),
    OtherKeys(): Bool()
})

# `key1` is required
assert schema.validate({
    "key1": "value1"
})

# `key2` is optional, but if present the value must be a string
assert schema.validate({
    "key1": "value1",
    "key2": "value2"
})

# any extra keys are allowed with any values, as long as they are bools
assert schema.validate({
    "key1": "value1",
    "key2": "value2",
    "extra key1": True,
    "extra key2": False
})

# Some failure modes:
results = schema.validate({
                                # key1 is missing
    "key2": 100,                # key2 must be a string
    "extra key": "extra value"  # extra key is not a bool
})
assert not results
print(results)
#
# '<dict>' must be a map like: { RequiredKey(): Str(), OptionalKey(): Str(), OtherKeys(): B <snip> = 'PASS'
#   RequiredKey('<all>'):'key1' missing required key(s) = 'FAIL'
#   OptionalKey('key2'):'key2' must be type 'str' with value 'key2' = 'PASS'
#   key2:'100' must be type 'str' = 'FAIL'
#   OtherKeys('extra key'):'extra key' must be type 'str' with value 'extra key' = 'PASS'
#   extra key:'extra value' must be type 'bool' = 'FAIL'
#

