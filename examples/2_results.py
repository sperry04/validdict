#!/usr/bin/env python3

from validdict import *

# Schema validation returns a result set that contains details about the validation

# Literal schema
schema = Schema({
    "key1": "value1",
    "key2": "value2"
})

# Validate an invalid dictionary against the schema
results = schema.validate({
    "key1": "bad value",
    "extra key": "extra value"
})

# The result set contains the description of the rules that were applied
# - results are hierarchical, but stored as a flat list of results
# - any failure in the set means the entire result set is also failed
# - missing keys are detected and reported
# - extra keys are detected and reported
# - values are validated to match the schema
# - printing the result set will list the individual results indented in hierarchical form
print(results)
#
# '<dict>' must be a map like: { RequiredKey(): Str(), RequiredKey(): Str() } = 'PASS'
#   RequiredKey('<all>'):'key2' missing required key(s) = 'FAIL'
#   RequiredKey('key1'):'key1' must be type 'str' with value 'key1' = 'PASS'
#   key1:'bad value' must be type 'str' with value 'value1' = 'FAIL'
#   Key('extra key'):'extra key' unknown key name = 'FAIL'
#

# Individual results from the result set can be counted and filtered
print(f"{len(results.filter(Outcome.FAIL))}/{len(results)} Failures:")
print(results.filter(Outcome.FAIL))
#
# 3/5 Failures:
#   RequiredKey('<all>'):'key2' missing required key(s) = 'FAIL'
#   key1:'bad value' must be type 'str' with value 'value1' = 'FAIL'
#   Key('extra key'):'extra key' unknown key name = 'FAIL'
#
