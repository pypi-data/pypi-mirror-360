# Technical Features

This page details the technical capabilities of `polars-as-config`, using examples inspired by the project's test suite.

## Polars as JSON

The core idea is to represent Polars operations and expressions in a JSON structure. Each step in your data transformation pipeline is an object in the `"steps"` array of the configuration JSON.

```json
{
  "steps": [
    {
      "operation": "scan_csv",
      "kwargs": {"source": "path/to/your/data.csv"}
    },
    {
      "operation": "with_columns",
      "kwargs": {
        "new_column": {
          "expr": "add",
          "on": {"expr": "col", "kwargs": {"name": "column_a"}},
          "kwargs": {"other": 10}
        }
      }
    },
    {"operation": "collect"}
  ]
}
```

In this example:
1.  We first load a CSV file using `scan_csv`.
2.  Then, we add a new column named `"new_column"` by adding `10` to `"column_a"`.
3.  Finally, we collect the lazy frame into a DataFrame.

## Passing Arguments and Keyword Arguments

You can pass both positional arguments (`args`) and keyword arguments (`kwargs`) to Polars operations and expressions.

### Args and Kwargs in Operations

```json
{
  "steps": [
    {
      "operation": "scan_csv",
      "args": ["tests/test_data/xy.csv"],
      "kwargs": {"has_header": true}
    }
  ]
}
```
Here, `scan_csv` receives the file path as a positional argument and `has_header` as a keyword argument.

### Args and Kwargs in Expressions

```json
{
  "steps": [
    {"operation": "scan_csv", "kwargs": {"source": "tests/test_data/xy.csv"}},
    {
      "operation": "with_columns",
      "kwargs": {
        "x_plus_y": {
          "expr": "add",
          "on": {"expr": "col", "kwargs": {"name": "x"}},
          "args": [{"expr": "col", "kwargs": {"name": "y"}}]
        }
      }
    }
  ]
}
```
In this `with_columns` step, the `add` expression takes its "other" operand (column `y`) from the `args` list.

## Expressions as Arguments/Kwargs

Polars expressions can be directly embedded as values for arguments or keyword arguments.

```json
{
  "steps": [
    {"operation": "scan_csv", "kwargs": {"source": "tests/test_data/xy.csv"}},
    {
      "operation": "with_columns",
      "kwargs": {
        "x_eq_y": {
          "expr": "eq",
          "on": {"expr": "col", "kwargs": {"name": "x"}},
          "kwargs": {"other": {"expr": "col", "kwargs": {"name": "y"}}}
        }
      }
    }
  ]
}
```
Here, the `other` kwarg for the `eq` (equals) expression is another expression: `{"expr": "col", "kwargs": {"name": "y"}}`.

## Nested Expressions with "on"

Expressions can be chained or nested by using the `"on"` keyword. The expression defined in `"on"` becomes the subject upon which the current expression operates.

```json
{
  "steps": [
    {"operation": "scan_csv", "kwargs": {"source": "tests/test_data/string_join.csv"}},
    {
      "operation": "with_columns",
      "kwargs": {
        "sliced_and_upper": {
          "expr": "str.to_uppercase",
          "on": {
            "expr": "str.slice",
            "on": {"expr": "col", "kwargs": {"name": "first"}},
            "kwargs": {"offset": 1, "length": 2}
          }
        }
      }
    }
  ]
}
```
In this example:
1. We select the column `"first"`.
2. We apply `str.slice` (with `offset: 1`, `length: 2`) *on* the `"first"` column.
3. We then apply `str.to_uppercase` *on* the result of the `str.slice` operation.

This allows for building complex, multi-step transformations for a single column. A more complex example:

```json
{
  "variables": {
    "multiplier": 3
  },
  "steps": [
    {"operation": "scan_csv", "kwargs": {"source": "tests/test_data/xy.csv"}},
    {
      "operation": "with_columns",
      "kwargs": {
        "complex_calc": {
          "expr": "add",
          "on": {
            "expr": "mul",
            "on": {"expr": "col", "kwargs": {"name": "x"}},
            "args": ["$multiplier"]
          },
          "args": [1]
        }
      }
    }
  ]
}
```
This calculates `(x * multiplier) + 1`.

## Variables and Escaping

Configurations can be parameterized using a `"variables"` section. Variables are prefixed with `$` when used.

```json
{
  "variables": {
    "input_file": "tests/test_data/xy.csv",
    "add_amount": 5
  },
  "steps": [
    {"operation": "scan_csv", "kwargs": {"source": "$input_file"}},
    {
      "operation": "with_columns",
      "kwargs": {
        "x_plus_var": {
          "expr": "add",
          "on": {"expr": "col", "kwargs": {"name": "x"}},
          "kwargs": {"other": "$add_amount"}
        }
      }
    }
  ]
}
```

### Variable Escaping

If you need to use a literal string that starts with a dollar sign, you can escape it by using two dollar signs (`$$`).

```json
{
  "variables": {
    "my_var": "should_not_be_used"
  },
  "steps": [
    {"operation": "scan_csv", "kwargs": {"source": "tests/test_data/string_join.csv"}},
    {
      "operation": "with_columns",
      "kwargs": {
        "literal_dollar": {
          "expr": "lit",
          "kwargs": {"value": "$$my_var"}
        }
      }
    }
  ]
}
```
In the example above, the `literal_dollar` column will contain the string `"$my_var"` rather than the value of the `my_var` variable.

You can mix escaped and unescaped variables:
```json
{
  "variables": {
    "actual_value": 42.0,
    "file_path": "tests/test_data/xy.csv"
  },
  "steps": [
    {"operation": "scan_csv", "kwargs": {"source": "$file_path"}},
    {
      "operation": "with_columns",
      "kwargs": {
        "escaped_text": {
          "expr": "lit",
          "kwargs": {"value": "$$actual_value"}
        },
        "real_value": {
          "expr": "lit",
          "kwargs": {"value": "$actual_value"}
        }
      }
    }
  ]
}
```
This will result in a column `"escaped_text"` with the literal string `"$actual_value"` and a column `"real_value"` with the number `42.0`.

## Custom Functions

You can extend `polars-as-config` with your own Python functions. These functions are typically applied using Polars' `map_elements` (or similar methods like `apply` or `map_groups`).

### Defining and Registering Custom Functions

First, define your Python function:
```python
# In your Python code
def multiply_by_two(value: int) -> int:
    return value * 2

def hash_row(row: dict) -> str:
    import hashlib
    row_str = "".join(str(val) for val in row.values())
    return hashlib.sha256(row_str.encode()).hexdigest()
```

Then, register it with the `Config` object:
```python
from polars_as_config.config import Config

custom_functions_dict = {
    "multiply_by_two": multiply_by_two,
    "hash_row": hash_row
}

config_runner = Config().add_custom_functions(custom_functions_dict)
# Now use config_runner.run_config(your_json_config)
```

### Using Custom Functions in JSON

To use a registered custom function, specify its name within a `"custom_function"` key:

```json
{
  "steps": [
    {"operation": "scan_csv", "kwargs": {"source": "tests/test_data/xy.csv"}},
    {
      "operation": "with_columns",
      "kwargs": {
        "x_doubled": {
          "expr": "map_elements",
          "on": {"expr": "col", "kwargs": {"name": "x"}},
          "kwargs": {"function": {"custom_function": "multiply_by_two"}}
        },
        "row_hash": {
          "expr": "map_elements",
          "on": {"expr": "struct", "args": [{"expr": "all"}]},
          "kwargs": {"function": {"custom_function": "hash_row"}}
        }
      }
    }
  ]
}
```
In this example:
- `multiply_by_two` is applied element-wise to column `"x"`.
- `hash_row` is applied to a struct containing all columns, effectively hashing each row.

**Note:** Variables cannot be used to specify the name of a custom function (e.g., `{"custom_function": "$my_func_name"}` is not supported). The function name must be a literal string. 