#!/usr/bin/env python3

from validdict import *

# Some advanced validation examples:


# The StartsWith() key validator allows multiple keys that start with the same prefix
schema = Schema({
    StartsWith("key_"): Any()        # accepts any key that starts with "key_"
})
assert schema.validate({
    "key_1": "value1",
    "key_2": "value2"
})

# However, it is invalid if the StartsWith() prefix overlaps with any other key names or other StartsWith() prefixes
try:
    schema = Schema({
        "key_1": "value1",
        StartsWith("key_"): Any()   # this will raise a ValueError because "key_" overlaps with "key_1"
    })
except TypeError as ex:
    print(ex.args[0])
#
# Map has ambiguous StartsWith() keys: ["StartsWith('key_') overlaps with Key('key_1')"]
#


# Or() can be a powerful tool to validate multiple types
# - the logical OR operator simplifies the writing schema
# - any Validators can be Or()'d together, even composite validators
schema = Schema({
    "key": Str() | Seq(Str())       # accepts a string or a list of strings
})


# Validators have some extended options to customize their results
# - `valid_outcome` and `invalid_outcome` can be set to PASS, INFO, WARN, or FAIL
# - instead of the default PASS/FAIL, these outcomes will be used in the results for valid/invalid values
# - `comment` can be set to provide additional context in logging output
v = Str("aaa", valid_outcome=Outcome.INFO, invalid_outcome=Outcome.WARN, comment="This reports INFO for valid strings, and WARN for invalid strings")
print(v.validate("aaa"))
#
# 'aaa' must be type 'str' with value 'aaa' = 'INFO' # This reports INFO for valid strings, and WARN for invalid strings
#
print(v.validate("bbb"))
#
# 'bbb' must be type 'str' with value 'aaa' = 'WARN' # This reports INFO for valid strings, and WARN for invalid strings
#


# If you have common validation patterns, functions that return a validator is a clean way to simplify the schema:
def RecommendedField(name:str):
    """
    Represents a key that will result in a warning if missing
    """
    return RequiredKey(name, invalid_outcome=Outcome.WARN, comment=f"Recommended field: {name}")

def DeprecatedField(name:str):
    """
    Represents a key that will result in a warning if present
    """
    return OptionalKey(name, valid_outcome=Outcome.WARN, comment=f"Deprecated field: {name}")

def StringOrSequenceEnum(*values:str):
    """
    Represents validator that accepts one or more strings from an enumeration
    with WARNing for strings that aren't in the enumeration
    """
    comment = f"Expected one of: ({', '.join(values)})"
    return ((Str(*values) | Str(valid_outcome=Outcome.WARN, comment=comment)) |
            (Seq(Str(*values) | Str(valid_outcome=Outcome.WARN, comment=comment))))

schema = Schema({
    RecommendedField("recommended"): Str(),
    DeprecatedField("old_key"): Str(),
    "status": StringOrSequenceEnum("active", "inactive", "pending")
})
results = schema.validate({
    "old_key": "value",
    "status": [ "pending", "deactivated" ]
})
assert results
print(results)
#
# '<dict>' must be a map like: { RequiredKey(): Str(), OptionalKey(): Str(), RequiredKey(): <snip> = 'PASS'
#   OptionalKey('old_key'):'old_key' must be type 'str' with value 'old_key' = 'WARN' # Deprecated field: old_key
#   old_key:'value' must be type 'str' = 'PASS'
#   RequiredKey('status'):'status' must be type 'str' with value 'status' = 'PASS'
#   status:'<list>' must be Str(...) | Str(...) | Seq(...) = 'PASS'
#     status.Or(Seq(...)):'<list>' must be a sequence like: [ must be Str(...) | Str(...) ] = 'PASS'
#       status.Or(Seq(...)).item_0:'pending' must be Str(...) | Str(...) = 'PASS'
#         status.Or(Seq(...)).item_0.Or(Str(...)):'pending' must be type 'str' with value one of ('active', 'inactive', 'pending') = 'PASS'
#       status.Or(Seq(...)).item_1:'deactivated' must be Str(...) | Str(...) = 'PASS'
#         status.Or(Seq(...)).item_1.Or(Str(...)):'deactivated' must be type 'str' = 'WARN' # Expected one of: (active, inactive, pending)
#


# The Schema class static log_results() method helps to filter and log results
# - the outcome_filter parameter can be used to filter the results to just the outcomes you want to log
# - the logging_config parameter is a dict that maps outcomes to a logging function
# - By default the logging maps to the default python logging module functions:
#   {
#       Outcome.PASS: logging.info
#       Outcome.INFO: logging.info
#       Outcome.WARN: logging.warning
#       Outcome.FAIL: logging.error
#       Outcome.NONE: logging.debug
#   }

schema = Schema({
    "key1": Str(),
    "key2": Num(),
    "key3": Bool(),
    OtherKeys(valid_outcome=Outcome.WARN): Any()
})

results = schema.validate({
    "key1": "value1",
    "key2": 1,
    "key3": True,
    "extra key1": "extra value",
})

# Filter to just the WARN outcomes, and log them with a custom function that prints the result
Schema.log_results(results, 
    Outcome.WARN,
    logging_config={
        Outcome.WARN: lambda result: print(f"WARN: {result}")
    }
)
#
# WARN: OtherKeys('extra key1'):'extra key1' must be type 'str' with value 'extra key1' = 'WARN'
#


# Contextual Validation allows for validation with additional context
# - a context object is passed to the validation function
# - by default, the context is the document itself
# - users may implement their own ContextualValidator classes to handle the context
# - validdict includes one such class, CallbackValidator that allows a user callback
#   to use the context to return a validator for the current value

def callback(cc:CallbackValidator.CallbackContext):
    """
    Callback function that returns a validator requiring the value to match the value at key1
    """
    return Str(                                 # return a Str validator
        cc.context["key1"],                     # that requires the value of key1 from the document
        valid_outcome=cc.valid_outcome,         # copy the valid outcome from the parent validator
        invalid_outcome=cc.invalid_outcome,     # copy the invalid outcome from the parent validator
        comment=cc.comment                      # copy the comment from the parent validator
    )

schema = Schema({
    "key1": Str(),
    "key2": CallbackValidator(callback, comment="key2 must match key1")
})

results = schema.validate({
    "key1": "value1",
    "key2": "value1"
})
assert results
print(results)
#
# '<dict>' must be a map like: { RequiredKey(): Str(), RequiredKey(): CallbackValidator() } = 'PASS'
#   RequiredKey('key1'):'key1' must be type 'str' with value 'key1' = 'PASS'
#   key1:'value1' must be type 'str' = 'PASS'
#   RequiredKey('key2'):'key2' must be type 'str' with value 'key2' = 'PASS'
#   key2:'value1' must be type 'str' with value 'value1' = 'PASS' # key2 must match key1
#

results = schema.validate({
    "key1": "value1",
    "key2": "value2"
})
assert not results
print(results)
#
# '<dict>' must be a map like: { RequiredKey(): Str(), RequiredKey(): CallbackValidator() } = 'PASS'
#   RequiredKey('key1'):'key1' must be type 'str' with value 'key1' = 'PASS'
#   key1:'value1' must be type 'str' = 'PASS'
#   RequiredKey('key2'):'key2' must be type 'str' with value 'key2' = 'PASS'
#   key2:'value2' must be type 'str' with value 'value1' = 'FAIL' # key2 must match key1
#
