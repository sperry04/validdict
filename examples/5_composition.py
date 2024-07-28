#!/usr/bin/env python3

from validdict import *

# Useful schemas are assembled out of composite validators
# - Map() validates a `dict` with key/value pairs
# - Seq() validates a `list` with typed elements
# - Or() allows for logical OR between validators
# - Any() allows for any type of value
# These can be nested to create complex schemas that validate real-world data structures

# Combining composite validators with scalar validators allows for complex schemas
# - literal keys are the same as RequiredKey()
schema = Schema({
    "map": Map({                # map is a dict with specific keys
        "key1": Str(),          # key1 is a string
        "key2": Num(),          # key2 is a number
        "key3": Bool()          # key3 is a boolean
    }),
    "seq": Seq(Num()),          # seq is a list of numbers
    "or": Str() | Num(),        # or is a string or a number
    OtherKeys(): Any()          # any other keys are allowed with any values
})
assert schema.validate({
    "map": {
        "key1": "value1",
        "key2": 1,
        "key3": True
    },
    "seq": [ 1, 2, 3 ],
    "or": "string",
    "extra key1": "extra value",
    "extra key2": [ 1, 2, 3 ]
})


# Here's a schema that validates a made-up user record
# - `userid` is required and must be a number
# - `username` is required and must be a string
# - `active` is required and must be a boolean
# - `address` is optional, but if present must be a map with specific keys
# - `emails` is optional, but if present must be a list at least 1 string that match an email regex
# - `phone` is optional, but if present must be a number or string
schema = Schema({
    "userid": Num(),
    "username": Str(),
    "active": Bool(),
    OptionalKey("address"): Map({
        "street": Str(),
        "city": Str(),
        "state": Str(),
        "zip": Str() | Num()
    }),
    OptionalKey("emails"): Seq(Regex(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"), min_len=1),
    OptionalKey("phone"): Num() | Str()
})
    
assert schema.validate({
    "userid": 1,
    "username": "user1",
    "active": True,
    "address": {
        "street": "123 Main St",
        "city": "Anytown",
        "state": "NY",
        "zip": "12345"
    },
    "emails": [ "example@email.com" ],
    "phone": "555-555-5555"
})

# Some failure modes:
results = schema.validate({
    "userid": "1",                  # userid must be a number
    "username": 1,                  # username must be a string
    "active": "True",               # active must be a boolean
    "address": {
        "street": "123 Main St",
        "city": "Anytown",
        "state": "NY"
                                    # zip is missing
    },
    "emails": [ ],                  # emails must have at least one value
    "phone": [ "555-555-5555", 5555555555 ], # phone must be a number or string, not a list
    "phone2": "555-555-5555"        # extra key
})
assert not results
print(results)
#
# '<dict>' must be a map like: { RequiredKey(): Num(), RequiredKey(): Str(), RequiredKey(): <snip> = 'PASS'
#   RequiredKey('userid'):'userid' must be type 'str' with value 'userid' = 'PASS'
#   userid:'1' must be type in ('int', 'float') = 'FAIL'
#   RequiredKey('username'):'username' must be type 'str' with value 'username' = 'PASS'
#   username:'1' must be type 'str' = 'FAIL'
#   RequiredKey('active'):'active' must be type 'str' with value 'active' = 'PASS'
#   active:'True' must be type 'bool' = 'FAIL'
#   OptionalKey('address'):'address' must be type 'str' with value 'address' = 'PASS'
#   address:'<dict>' must be a map like: { RequiredKey(): Str(), RequiredKey(): Str(), RequiredKey(): <snip> = 'PASS'
#     address.RequiredKey('<all>'):'zip' missing required key(s) = 'FAIL'
#     address.RequiredKey('street'):'street' must be type 'str' with value 'street' = 'PASS'
#     address.street:'123 Main St' must be type 'str' = 'PASS'
#     address.RequiredKey('city'):'city' must be type 'str' with value 'city' = 'PASS'
#     address.city:'Anytown' must be type 'str' = 'PASS'
#     address.RequiredKey('state'):'state' must be type 'str' with value 'state' = 'PASS'
#     address.state:'NY' must be type 'str' = 'PASS'
#   OptionalKey('emails'):'emails' must be type 'str' with value 'emails' = 'PASS'
#   emails:'<list>' must be a sequence like: [ must be type 'str' with value matching '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$' ] = 'PASS'
#     emails.min_len:'0' must be type in ('int', 'float') with value '>= 1' = 'FAIL'
#   OptionalKey('phone'):'phone' must be type 'str' with value 'phone' = 'PASS'
#   phone:'<list>' must be Num() | Str() = 'FAIL'
#     phone.Or(Num()):'<list>' must be type in ('int', 'float') = 'FAIL'
#     phone.Or(Str()):'<list>' must be type 'str' = 'FAIL'
#   Key('phone2'):'phone2' unknown key name = 'FAIL'
#
