# Map validator

from .results import Outcome, FixedOutcome, Result, ResultSet
from .validator import Validator, Any
from .key import KeyValidator, RequiredKey, OtherKeys, StartsWith
from .contextual import ContextualValidator
from .helpers import format_sequence, extend_path
from .locator import Locator

class Map(ContextualValidator):
    """
    Validates a map (aka dictionary)

    Notes:
        For map validation to work, the keys must not be ambiguous... every key we're validating must
        match one, and only one, key in the schema or we won't know which value validator to validate
        the key's value with.

        As such, during __init__ we need to validate the KeyValidators themselves to catch any duplicate
        key names, or validators that might otherwise be ambiguous, like two StartsWith() keys that
        are subsets of each other, and limit to just a single OtherKeys() which is a wildcard for all 
        other non-matched keys.
    """
    def __init__(self, map:dict=None, *, valid_outcome:Outcome=Outcome.PASS, invalid_outcome:Outcome=Outcome.FAIL, comment:str="") -> None:
        """
        constructor
        :param map:         dict structure of validators
        """
        if map is None: map = { OtherKeys(): Any() }                                                # assume a pretty open-ended dict validator if none was provided
        if not isinstance(map, dict):
            raise TypeError(f"Map must be of type dict (not {type(map)})")
        super().__init__(valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment)

        # convert all the raw keys/values that aren't Validators into Validators
        self.map = {                                                                                # dictionary comprehension that... 
            RequiredKey(key,
                valid_outcome=valid_outcome, 
                invalid_outcome=invalid_outcome, 
                comment=comment
            ) if not isinstance(key, Validator) else key:                                           # converts all non-Validator keys into Required() KeyValidators, and...
            Validator.for_value(value,
                valid_outcome=valid_outcome, 
                invalid_outcome=invalid_outcome, 
                comment=comment
            ) if not isinstance(value, Validator) else value                                        # converts all non-Validator values into Validators of the appropriate type...
            for key, value in map.items()                                                           # for all the key:value pairs in the provided schema map
        }

        # prevent non-KeyValidators being used on the key side of the map schema
        illegal_validators = [ validator for validator in self.map.keys() if isinstance(validator, Validator) and not isinstance(validator, KeyValidator) ]
        if len(illegal_validators) != 0:
            raise TypeError(f"Validator(s) ({format_sequence([ type(v).__name__ for v in illegal_validators ])}) may not be used to validate keys")

        # prevent KeyValidators being used on the value side of the map schema
        illegal_validators = [ validator for validator in self.map.values() if isinstance(validator, KeyValidator) ]
        if len(illegal_validators) != 0:
            raise TypeError(f"KeyValidator(s) ({format_sequence([ type(v).__name__ for v in illegal_validators ])}) may not be used to validate values")

        # look for ambiguous fixed key names
        key_names = []
        for key in self.map.keys():                                                                 # loop over all the keys in the map...
            if not isinstance(key, (OtherKeys, StartsWith)):                                        # if they are a KeyValidator with a fixed "accepted_value"...
                key_names.append(key.accepted_name)                                                 # add the KeyValidator's accepted value to the key_names
        duplicates = set(name for name in key_names if key_names.count(name) > 1)                   # look for duplicates in the fixed value key_names
        if len(duplicates) != 0:
            raise TypeError(f"Map has duplicate key names: {duplicates}")

        # look for cases where StartsWith() KeyValidators overlap with fixed keys
        duplicates = []
        for kv in (kv for kv in self.map.keys() if isinstance(kv, StartsWith)):
            for prefix in kv.accepted_prefixes:
                for fk in (fk for fk in self.map.keys() if not isinstance(fk, (OtherKeys, StartsWith))):
                    if kv.case_sensitive:
                        if fk.accepted_name.startswith(prefix):
                            duplicates.append(f"StartsWith('{prefix}') overlaps with Key('{fk.accepted_name}')")
                    else:
                        if fk.accepted_name.lower().startswith(prefix.lower()):
                            duplicates.append(f"StartsWith('{prefix}') overlaps with Key('{fk.accepted_name}')")
        if len(duplicates) != 0:
            raise TypeError(f"Map has ambiguous StartsWith() keys: {duplicates}")

        # now look for StartsWith() KeyValidators that overlap with each other, this is not pretty, 
        # and it's even worse due to the fact that some StartsWith are case_sensitive and some are not
        duplicates = []
        for i, kv_i in enumerate(kv for kv in self.map.keys() if isinstance(kv, StartsWith)):
            case_sensitive_i = kv_i.case_sensitive
            for prefix_i in kv_i.accepted_prefixes:
                for j, kv_j in enumerate(kv for kv in self.map.keys() if isinstance(kv, StartsWith)):
                    if i != j:  # don't compare a list against itself
                        case_sensitive_j = kv_j.case_sensitive
                        for prefix_j in kv_j.accepted_prefixes:
                            if case_sensitive_i and case_sensitive_j:
                                if prefix_i.startswith(prefix_j):
                                    duplicates.append(f"StartsWith({prefix_j}) overlaps with StartsWith({prefix_i})")
                            else:
                                if prefix_i.lower().startswith(prefix_j.lower()):
                                    duplicates.append(f"StartsWith({prefix_j}) overlaps with StartsWith({prefix_i})")
        if len(duplicates) != 0:
            raise TypeError(f"Map has ambiguous StartsWith() keys: {duplicates}")

        # TODO: are there additional structural checks that need to be done?

        # gather some lists of keys that will be used during validations
        self.required_keys = [ key for key in self.map.keys() if isinstance(key, RequiredKey) ]     # will be used for required key validations
        self.keys = [ key for key in self.map.keys() if not isinstance(key, OtherKeys) ]            # will be used for first-chance validations
        self.other_keys = [ key for key in self.map.keys() if isinstance(key, OtherKeys) ]          # will be used fore second-chance (OtherKeys() catch-all) validations
        if len(self.other_keys) > 1:
            raise TypeError("Map cannot have multiple OtherKeys() keys")

    def __repr__(self) -> str:
        """
        string representation of the validator
        """
        validator_repr_max_len = 60
        map_description = "{ " + ", ".join(k.__class__.__name__ + "(): " + v.__class__.__name__ + "()" for k, v in self.map.items()) + " }"
        return "must be a map like: " + (map_description if len(map_description) <= validator_repr_max_len else (map_description[:validator_repr_max_len] + " <snip>"))
    
    def _validate_key_value_pair(self, k:object, v:object, key_validators:list[KeyValidator], path:list[str]=None, context:object=None) -> ResultSet:
        """
        Class helper function that validates a key:value pair against the map
        :param k:                   the Key to validate
        :param v:                   the Value to validate
        :param key_validators:      list of key validators to validate k against, if k is valid, v is validated against the corresponding value validator in the map
        :param path:                list of parent keys for nested/compound structures
        """
        rval = ResultSet()
        for key_validator in key_validators:
            key_result = ContextualValidator.validate_with_context(key_validator, k, extend_path(path, f"{key_validator.__class__.__name__}(<value>)"), context)
            if key_result:
                rval.add_results(key_result)
                rval.add_results(ContextualValidator.validate_with_context(self.map[key_validator], v, extend_path(path, k), context))
                break # out of for each key_validator
        return rval
    
    def validate(self, value:object, path:list[str]=None, context:object=None) -> ResultSet:
        """
        validates a dict, makes sure it has all required keys and validates all values against the validator's own map of validators
        :param value:       the map to validate
        :param path:        list of parent keys for nested/compound structures
        :param context:     the root dict that is being validated, used to pass context down to ContextualValidators
        :return:            validation result set containing the result of all nested validations
        """
        rval = ResultSet()
        if isinstance(value, dict):                                                                 # make sure the value is a dict
            rval.add_results(Result(outcome=self.valid_outcome, value=value, path=path, validator=self))

            # validate that all required keys are present in the dict
            missing_required_keys = []
            for key_validator in self.required_keys:
                if not any(key_validator.validate(key).outcome != Outcome.FAIL for key in value.keys()):
                    missing_required_keys.append(key_validator.accepted_name)
            if len(missing_required_keys) > 0:
                rval.add_results(Result(outcome=self.invalid_outcome, value=format_sequence(missing_required_keys, quote=""), path=extend_path(path, f"RequiredKey('<all>')"), validator=FixedOutcome(self.invalid_outcome, is_valid=False, message="missing required key(s)")))

            # validate each key/value pair against it's KeyValidator and matching value Validator
            for k, v in value.items():                                                              # loop over all the key/value pairs in the dict to validate each of them
                first_chance_results = self._validate_key_value_pair(k, v, self.keys, path, context)
                if len(first_chance_results) > 0:                                           # if the first chance (required/optional keys) results were found
                    rval.add_results(first_chance_results)                                          # add the results
                else:                                                                               # else, move on to trying to match the second chance (other) key
                    second_chance_results = self._validate_key_value_pair(k, v, self.other_keys, path, context)
                    if len(second_chance_results) > 0:                                      # if the second chance (other key) results were found 
                        rval.add_results(second_chance_results)                                     # add the results
                    else:
                        rval.add_results(Result(outcome=self.invalid_outcome, value=k, path=extend_path(path, f"Key('{k}')"), validator=FixedOutcome(self.invalid_outcome, is_valid=False, message="unknown key name")))      # no keys validated, it must be illegal

        else:
            rval.add_results(Result(outcome=self.invalid_outcome, value=value, path=path, validator=self))        # not a dict, it must be invalid
        return rval

# register the Map validator with the Locator to validate dict objects
Locator.register(dict, Map)
