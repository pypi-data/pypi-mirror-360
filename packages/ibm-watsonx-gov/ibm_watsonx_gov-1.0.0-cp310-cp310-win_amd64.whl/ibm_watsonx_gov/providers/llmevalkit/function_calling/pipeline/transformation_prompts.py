from typing import Dict, Any, List
from copy import deepcopy

# ──────────────────────────────────────────────────────────────────────────────
# 1) extract_units
# ──────────────────────────────────────────────────────────────────────────────


SINGLE_PARAM_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "user_value": {
            "type": ["string", "null"],
            "description": "The raw value mentioned by the user (always a string).",
        },
        "user_units": {
            "type": ["string", "null"],
            "description": (
                "Units explicitly or implicitly attached to the user_value (e.g., "
                "'seconds', 'GB', 'MB', 'YYYY-MM-DD'). If none, return an empty string."
            ),
        },
        "spec_units": {
            "type": ["string", "null"],
            "description": (
                "Units defined or implied by the parameter's JSON Schema "
                "(e.g., 'seconds', 'bytes', 'YYYY-MM-DD'). If none, return an empty string."
            ),
        },
    },
    "required": ["user_value", "user_units", "spec_units"],
}


def build_multi_extract_units_schema(params: List[str]) -> Dict[str, Any]:
    """
    Construct a JSON Schema whose top-level properties are each parameter name.
    Each parameter maps to an object matching SINGLE_PARAM_SCHEMA.
    """
    schema: Dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": params.copy(),
    }
    for pname in params:
        schema["properties"][pname] = deepcopy(SINGLE_PARAM_SCHEMA)
    return schema


# -------------------------------------------------------------------
# 2) System prompt template for multi-parameter unit/format extraction
# -------------------------------------------------------------------
# We include a `{schema}` placeholder, which will be replaced at runtime
# with a JSON-dumped version of the schema built for the current params.
MULTI_EXTRACT_UNITS_SYSTEM: str = """\
You are an expert in natural language understanding and API specifications.
Given:
  1. A user context (natural-language instructions).
  2. A JSON Schema snippet that describes **all** parameters the tool expects.
  3. A list of all parameter names.

Your task:
  For each parameter name, identify:
    • The raw "user_value" mentioned in the user context (as a string).
    • The "user_units" explicitly or implicitly attached to that value.
      (If none, return an empty string `""`.)
    • The "spec_units" defined or implied by the JSON Schema (type/description).
      (If none, return an empty string `""`.)

Respond with exactly one JSON object whose keys are the parameter names,
and whose values are objects with "user_value", "user_units", and "spec_units".
The JSON must match this schema exactly:

{schema}
"""


# -------------------------------------------------------------------
# 3) User prompt template for multi-parameter unit extraction
# -------------------------------------------------------------------
# Use Python .format(...) placeholders for:
#   context        = The conversation/context string
#   full_spec      = JSON.dumps(...) of the combined JSON Schema snippet for all params
#   parameter_names = Comma-separated list of parameter names
MULTI_EXTRACT_UNITS_USER: str = """\

Examples (multi-parameter):

1) Context: "Change the interval to 30 seconds and set threshold to 0.75."
   Full Spec:
   {{
     "type": "object",
     "properties": {{
       "interval": {{
         "type": "integer",
         "description": "Interval duration in seconds"
       }},
       "threshold": {{
         "type": "number",
         "description": "Threshold limit (0.0 to 1.0)"
       }}
     }},
     "required": ["interval", "threshold"]
   }}
   Parameter names: "interval, threshold"
   -> {{
        "interval": {{
          "user_value":"30",
          "user_units":"seconds",
          "spec_units":"seconds"
        }},
        "threshold": {{
          "user_value":"0.75",
          "user_units":"",
          "spec_units":""
        }}
      }}

2) Context: "Download up to 2 GB of data and retry 5 times."
   Full Spec:
   {{
     "type": "object",
     "properties": {{
       "size": {{
         "type": "string",
         "description": "Size limit in bytes"
       }},
       "retries": {{
         "type": "integer",
         "description": "Maximum retry count"
       }}
     }},
     "required": ["size", "retries"]
   }}
   Parameter names: "size, retries"
   -> {{
        "size": {{
          "user_value":"2",
          "user_units":"GB",
          "spec_units":"bytes"
        }},
        "retries": {{
          "user_value":"5",
          "user_units":"",
          "spec_units":""
        }}
      }}

3) Context: "Set backup_date to December 1st, 2024 and limit to 100MB."
   Full Spec:
   {{
     "type": "object",
     "properties": {{
       "backup_date": {{
         "type": "string",
         "format": "date",
         "description": "Date of backup in YYYY-MM-DD"
       }},
       "limit": {{
         "type": "string",
         "description": "File size cap (in bytes)"
       }}
     }},
     "required": ["backup_date", "limit"]
   }}
   Parameter names: "backup_date, limit"
   -> {{
        "backup_date": {{
          "user_value":"December 1st, 2024",
          "user_units":"Month day, year",
          "spec_units":"YYYY-MM-DD"
        }},
        "limit": {{
          "user_value":"100",
          "user_units":"MB",
          "spec_units":"bytes"
        }}
      }}

Context:
{context}

Full Spec (JSON Schema snippet for all parameters):
{full_spec}

Parameter names: {parameter_names}

Please return exactly one JSON object matching the schema defined in the system prompt.
"""

# ──────────────────────────────────────────────────────────────────────────────
# 2) generate_transformation_code
# ──────────────────────────────────────────────────────────────────────────────

# System prompt for code generation
GENERATE_CODE_SYSTEM: str = """\
You are an expert in Python code generation. Your task is to generate a Python script
that defines two functions:

1) transformation_code(input_value: str) -> <transformed_type>:
   Converts an input string example from OLD_UNITS to TRANSFORMED_UNITS,
   returning a value of the given type.

2) convert_example_str_transformed_to_transformed_type(example_transformed_value: str) -> <transformed_type>:
   Parses the transformed example string into the target type, without any unit logic.

You will receive four illustrative examples followed by a TASK section.

You will receive:
- An old value example (string) and its unit.
- A transformed value example (string) and its unit.
- The transformed type (e.g., int, float, str, list[float], etc.).
If a requested transformation is not supported (cannot be done in Python), return "" in the generated_code field.

Respond with ONLY a JSON object matching this schema (no Markdown fences, no extra text):
{
  "generated_code": "<full python script>"
}
"""

generated_code_example1 = (
    "from datetime import datetime, timezone\n"
    "import dateutil.parser\n\n"
    "# input_value is a string with the format 'December 1st, 2011'\n"
    "def transformation_code(input_value: str) -> int:\n"
    "    # Parse the date string, dateutil.parser automatically handles 'st', 'nd', 'rd', 'th'\n"
    "    dt = dateutil.parser.parse(input_value)\n\n"
    "    # Ensure the datetime is treated as UTC\n"
    "    dt = dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)\n\n"
    "    # Convert to Unix timestamp\n"
    "    return int(dt.timestamp())\n\n"
    "# example_transformed_value is a string with the format '1322697600'\n"
    "def convert_example_str_transformed_to_transformed_type(example_transformed_value: str) -> int:\n"
    "    return int(example_transformed_value)\n"
)

transformation_eval_example1 = (
    """
### Example 1:

EXAMPLE FORMAT OF OLD VALUE: 'December 1st, 2011'
OLD UNITS: month day, year
EXAMPLE FORMAT OF TRANSFORMED VALUE: '1322697600'
TRANSFORMED UNITS: Unix timestamp
TRANSFORMED TYPE: int

RESPONSE:
{{"""
    + '"generated_code": "'
    + generated_code_example1
    + '"'
    + """}}"""
)

generated_code_example2 = (
    "# input_value is a string with the format '1000 (default)'\n"
    "def transformation_code(input_value: str) -> float:\n"
    "    return float(input_value.split()[0]) / 1000\n\n"
    "# example_transformed_value is a string with the format '10 '\n"
    "def convert_example_str_transformed_to_transformed_type(example_transformed_value: str) -> float:\n"
    "    return float(example_transformed_value.strip())\n"
)

transformation_eval_example2 = (
    """
### Example 2:

EXAMPLE FORMAT OF OLD VALUE: '1000 (default)'
OLD UNITS: milliseconds
EXAMPLE FORMAT OF TRANSFORMED VALUE: '10 '
TRANSFORMED UNITS: seconds
TRANSFORMED TYPE: float

RESPONSE:
{{"""
    + '"generated_code": "'
    + generated_code_example2
    + '"'
    + """}}"""
)

generated_code_example3 = (
    "# input_value is a string with the format '25°C'\n"
    "def transformation_code(input_value: str) -> list[float]:\n"
    "    return [float(input_value[0:2]) + 273.15]\n\n"
    "# example_transformed_value is a string with the format '[35] (default)'\n"
    "def convert_example_str_transformed_to_transformed_type(example_transformed_value: str) -> list[float]:\n"
    "    return [float(example_transformed_value[1:-9])]\n"
)

transformation_eval_example3 = (
    """
### Example 3:

EXAMPLE FORMAT OF OLD VALUE: '25°C'
OLD UNITS: Celsius
EXAMPLE FORMAT OF TRANSFORMED VALUE: '[35] (default)'
TRANSFORMED UNITS: Kelvin
TRANSFORMED TYPE: list

RESPONSE:
{{"""
    + '"generated_code": "'
    + generated_code_example3
    + '"'
    + """}}"""
)

transformation_eval_example4 = """
### Unsupported Transformation Example:

EXAMPLE FORMAT OF OLD VALUE: ABC
OLD UNITS: unit1
EXAMPLE FORMAT OF TRANSFORMED VALUE: DEF
TRANSFORMED UNITS: unit2
TRANSFORMED TYPE: str

RESPONSE:
{{"generated_code": ""}}"""


# User prompt template for code generation
# Use Python format-style placeholders:
#   transformation_eval_examples, old_value, old_units, transformed_value, transformed_units, transformed_type
GENERATE_CODE_USER: str = (
    f"""\
Few-shot examples for how to convert:

{transformation_eval_example1}

{transformation_eval_example2}

{transformation_eval_example3}

{transformation_eval_example4}

"""
    + """\

TASK:

EXAMPLE FORMAT OF OLD VALUE: {old_value}
OLD UNITS: {old_units}
EXAMPLE FORMAT OF TRANSFORMED VALUE: {transformed_value}
TRANSFORMED UNITS: {transformed_units}
TRANSFORMED TYPE: {transformed_type}

RESPONSE:
"""
)

# JSON Schema dict for validation
GENERATE_CODE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "generated_code": {
            "type": "string",
            "description": "The generated Python code for the transformation. Should be a valid Python script without any Markdown formatting.",
        }
    },
    "required": ["generated_code"],
}
