# ValidDictorian
### Declarative Python Dictionary Validator
Copyright 2024 Scott Perry, 
Available under the MIT license, 
GitHub repo: https://github.com/sperry04/validdict


## Purpose

`validdict` provides a way to declare schema validation rules for a Python dictionary using Python objects and types, rather than using a bespoke or interpreted schema validation language.  This allows validation of virtually any data that can be represented as a Python `dict`, such as input strings parsed by modules such as `pyyaml` or `json`.

Schemas are declarative with built-in scalar type validators, plus compositable map and sequence validators that allow the construction of complex schemas.


## Basic Usage

To use the `validdict` library, follow these steps:

1. Install the library by running the following command:
    ```
    pip install validdict
    ```

2. Import the `validdict` module in your Python script:
    ```python
    import validdict
    ```

3. Create a `Schema` instance with the declaration of a valid document. Each key in the document represents a field in the input dictionary, and the corresponding validation rules for allowed values. 

    For example:
    ```python
    from validdict import *

    schema = Schema({
        "int": Num(),
        "float": Num(),
        "bool": Bool(),
        "string": Str(),
        "regex": Regex(r"\w+@\w+\.com") # trivial email regex
    })
    ```

4. Use the schema to validate documents:

    ```python
    results = schema.validate({
        "int": 1,
        "float": 1.0,
        "string": "string",
        "bool": True,
        "regex": "example@email.com"
    })
    ```

5. Print, or otherwise process, the validation results:

    ```python
    print(results)
    ```

    Output:
    ```
    '<dict>' must be a map like: { RequiredKey(): Num(), RequiredKey(): Num(), RequiredKey(): <snip> = 'PASS'
        RequiredKey('int'):'int' must be type 'str' with value 'int' = 'PASS'
        int:'1' must be type in ('int', 'float') = 'PASS'
        RequiredKey('float'):'float' must be type 'str' with value 'float' = 'PASS'
        float:'1.0' must be type in ('int', 'float') = 'PASS'
        RequiredKey('string'):'string' must be type 'str' with value 'string' = 'PASS'
        string:'string' must be type 'str' = 'PASS'
        RequiredKey('bool'):'bool' must be type 'str' with value 'bool' = 'PASS'
        bool:'True' must be type 'bool' = 'PASS'
        RequiredKey('regex'):'regex' must be type 'str' with value 'regex' = 'PASS'
        regex:'example@email.com' must be type 'str' with value matching '\w+@\w+\.com' = 'PASS'
    ```

## Examples

1. [Validating literals](examples/1_literals.py)
2. [Handling validation results](examples/2_results.py)
3. [Validating scalar types](examples/3_scalars.py)
4. [Validating dictionary keys](examples/4_keys.py)
5. [Composition of large schemas](examples/5_composition.py)
6. [Advanced techniques](examples/6_advanced.py)
