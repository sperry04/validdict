#!/usr/bin/env python3

from validdict import *

# `validdict` provides the means to:
# - declare a validation schema
# - validate dictionaries against it
# - report the results of the validation


# The default schema will validate any dict
schema = Schema()

# Validate returns a result set that contains the results of the validation
results = schema.validate({})

# The returned result set evaluates to True when the dictionary is valid
assert results

# The result set evaluates to False when the dictionary is invalid
results = schema.validate("not a dict")
assert not results


# A literal schema is the most basic schema that requires:
# - no missing keys
# - no extra keys
# - the exact matching values for each key
# - the order of the key/value pairs does not matter

# Define a literal schema
schema = Schema({
    "key1": "value1",
    "key2": "value2"
})

# Validate a dictionary against the schema
assert schema.validate({
    "key2": "value2",
    "key1": "value1"
})

# Validating an invalid dictionary will return False
assert not schema.validate({
    "key1": "value1",
    "key2": "bad value",
    "extra key": "extra value"
})
