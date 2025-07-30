# Function-Calling Reflection Pipeline

This directory implements a full **pre-call reflection** workflow for conversational agents making API (function) calls. It leverages:

- **Static schema checks** - Ensure that calls conform exactly to the API schema and naming rules. 
- **Semantic LLM-driven metrics** - Evaluate the deeper meaning, context alignment, and correctness of calls beyond syntax. 
- **Optional unit-conversion transforms** via code generation 

All LLM and metric logic lives inside this package—no external frameworks are required.

---

## Table of Contents

1. [Syntactic Checks](#syntactic-checks)
2. [Semantic Metrics](#semantic-metrics)
3. [Quickstart](#quickstart)  
4. [Directory Structure](#directory-structure)  
5. [ReflectionPipeline API](#reflectionpipeline-api)  
   - `static_only`  
   - `semantic_sync` / `semantic_async`  
   - `run_sync` / `run_async`  
6. [Example Usage](#example-usage)  
7. [Custom Metrics](#custom-metrics)  
8. [Transform-Enabled Mode](#transform-enabled-mode)  
9. [Error Handling & Logging](#error-handling--logging)  

---


## Syntactic Checks

These catch straightforward, schema-level errors against your API specification:

* **NonExistentFunction**
  
  *Description:* The function name does not appear in the API spec.

  *Mistake Example:* Calling `get_customer_profile` when only `get_user_profile` is defined.

* **NonExistentParameter**
  
  *Description:* One or more parameters are not defined for the chosen function.

  *Mistake Example:* Using `user` in `get_user_profile(user=42)` when the function expects `user_id`.

* **IncorrectParameterType**
  
  *Description:* Provided parameter values do not match the expected types.

  *Mistake Example:* Passing `"true"` (string) to a boolean parameter `is_active`, instead of `true`.

* **MissingRequiredParameter**
  
  *Description:* A required parameter is omitted.

  *Mistake Example:* Calling `list_events(start_date="2025-05-01")` without the required `end_date`.

* **AllowedValuesViolation**
  
  *Description:* A parameter value falls outside its allowed enumeration.

  *Mistake Example:* Passing `"urgent"` to `priority` when only `"low"`, `"medium"`, or `"high"` are allowed.

---

## Semantic Metrics

Each semantic metric outputs a JSON object with fields you can customize in your JSONL file:

* **explanation**: Detailed reasoning behind the judgment.
* **evidence**: Exact conversation or spec excerpts used.
* **output**: Numeric or binary correctness indicator.
* **confidence**: Judge’s confidence (0.0-1.0).
* **correction**: Suggested snippet to fix issues.

You can add, remove, or modify metrics by editing the JSONL definitions.

### 2.1 General Metrics

Metrics evaluating the *meaning* and *contextual correctness* of a single API call:

**1. Function-Intent Alignment (1-5)**

Assess whether this function call (name + parameters) matches the user request and is the right next step.

*Mistake Example:* User: “Update my shipping address to 123 Main St.”  Call: `get_address(user_id=42)` instead of `update_address(user_id=42, address="123 Main St")`.

**2. Parameter Value Grounding (0 or 1)**

Ensure every parameter value is directly drawn from user text, assistant messages, previous outputs of api calls, or API spec defaults.

*Mistake Example:* User: “Show my account balance.”  Call: `get_balance(account_id=999)` when account\_id should come from an earlier login step (e.g., 1234).

**3. Parameter Completeness & Consistency (1-5)**

Verify all context-implied parameters are included and their values do not conflict.

*Mistake Example:* User: “Create meeting tomorrow at 10am called Standup.”  Call: `create_event(time="10am", title="Standup", specific_time=false)` conflicting time `specific_time` and `time` values.

**4. Prerequisite Satisfaction (0 or 1)**

Check that required upstream steps (auth, data fetch, prior calls) have already done.

*Mistake Example:* User: “Get information about item 35.”  Call: `get_item_info(item_id=35)` without prior `login(...)` to be logged in.

**5. Overall Call Correctness (0.00-1.00)**

Combine alignment, grounding, completeness, and prerequisites into one score.

*Mistake Example:* Calling `delete_email(email_id="abc123")` when user requested “Archive my emails,” missing alignment and prerequisites.

### 2.2 Function-Selection Metric

Choose the *single best* function among all available:

**6. Optimal Function Selection (0 or 1)**

Judge if no superior alternative exists in the tool inventory.

*Mistake Example:* User: “What time is it in Tokyo?”  Call: `list_timezones()` instead of `get_time(timezone="Asia/Tokyo")`.

### 2.3 Parameter Metrics

Evaluate each individual parameter’s correctness:

**7. Value Format Alignment (0 or 1)**

Confirm the value’s type, format, and units match the spec exactly.

*Mistake Example:* User: “Wait for 30 seconds.”  Call: `delay(ms=30)` instead of `delay(ms=30000)`. "Get all orders of item 67 since 24/5/2020." Call: `get_item_orders(item_id=67, from="24/5/2020")` instead of `from="5/24/2020"` as the api spec describes.

**8. Parameter Information Sufficiency (0 or 1)**

Determine if the value is unambiguous or if more detail is needed.

*Mistake Example:* User: “Set alarm for 7.”  Call: `set_alarm(time="7")` without AM/PM or timezone.

**9. Parameter Importance (0.00-1.00)**

Rate how essential the parameter is to the call’s success.

*Mistake Example:* User: “List my emails.”  Call includes optional `sortOrder` when user did not request sorting (low importance).

**10. Parameter Hallucination Check (0 or 1)**

Ensure the value isn’t hallucinated.

*Mistake Example:* Set `count=20` when no count was specified and default is 10.

**11. Overall Parameter Correctness (0 or 1)**

Final binary check across all semantic criteria. A parameter fails format, grounding, or completeness, resulting in an incorrect call.

---

**Customization:** Modify metrics, thresholds, and fields by editing your JSONL configuration files.

---

## Quickstart

```bash
pip install llmevalkit[litellm]  # or your preferred extras
```

```python
from llmevalkit.llm.registry import get_llm
from llmevalkit.function_calling.pipeline.pipeline import ReflectionPipeline

# 1) Pick your LLM provider and initialize clients
MetricsClient = get_llm("litellm.watsonx.output_val")
CodegenClient = get_llm("litellm.watsonx.output_val")
metrics_client = MetricsClient(model_name="meta-llama/llama-3-3-70b-instruct")
codegen_client = CodegenClient(model_name="meta-llama/llama-3-3-70b-instruct")

# 2) Create pipeline (loads bundled metrics JSONL by default)
pipeline = ReflectionPipeline(
    metrics_client=metrics_client,
    codegen_client=codegen_client,
    transform_enabled=False
)

# 3) Define your API specs (OpenAI-style function definitions)
apis_specs = [
    { "type":"function", "function": { ... } },
    ...
]

# 4) Provide a tool_call and context
call = {
  "id":"1","type":"function",
  "function":{"name":"get_weather","arguments":{"location":"Berlin"}}
}
context = "User: What's the weather in Berlin?"

# 5) Run end-to-end reflection
result = pipeline.run_sync(
    conversation=context,
    inventory=apis_specs,
    call=call,
    continue_on_static=False,
    retries=2
)
print(result.model_dump_json(indent=2))
```

---

## Directory Structure

```
src/llmevalkit/function_calling/
├── __init__.py
├── metrics/                <- MetricPrompt templates & JSONL definitions
│   ├── base.py
│   ├── loader.py
│   ├── function_call/
│   │   ├── general.py
│   │   └── general_metrics.jsonl
│   ├── function_selection/
│   │   ├── function_selection.py
│   │   └── function_selection_metrics.jsonl
│   └── parameter/
│       ├── parameter.py
│       └── parameter_metrics.jsonl
├── pipeline/
│   ├── adapters.py         <- API-spec / call normalization
│   ├── pipeline.py         <- High-level ReflectionPipeline
│   ├── semantic_checker.py <- Core LLM metrics orchestration
│   ├── static_checker.py   <- JSONSchema-based validation
│   ├── transformation_prompts.py <- Unit-conversion prompts
│   └── types.py            <- Pydantic models for inputs & outputs
└── examples/
    └── function_calling/
        └── pipeline.py     <- Complete runnable example
```

---

## ReflectionPipeline API

### Initialization

```python
ReflectionPipeline(
    metrics_client: LLMClient,
    codegen_client: LLMClient,
    transform_enabled: bool = False,
    general_metrics: Optional[Path] = None,
    function_metrics: Optional[Path] = None,
    parameter_metrics: Optional[Path] = None,
    transform_examples: Optional[Dict[str,str]] = None,
)
```

- **`metrics_client`**: llmevalkit LLM client for semantic metrics (e.g. output-validating OpenAI or LiteLLM).  
- **`codegen_client`**: llmevalkit LLM client for code generation (required if `transform_enabled=True`).  
- **`*_metrics`**: override paths to your own JSONL metric definitions (otherwise uses `metrics/.../*.jsonl`).  
- **`transform_enabled`**: whether to run unit-conversion checks.  

### `static_only(conversation, inventory, call) → StaticResult`

- Runs pure JSON-schema validation on `call` against `inventory` specs.  
- Checks required parameters, types, enums, etc.

### `semantic_sync(conversation, inventory, call, retries=1) → SemanticResult`

- Runs LLM-driven metric evaluations **synchronously**.  
- Returns per-category semantic results.

### `semantic_async(conversation, inventory, call, retries=1, max_parallel=10) → SemanticResult`

- Same as above, but issues LLM calls in parallel.

### `run_sync(conversation, inventory, call, continue_on_static=False, retries=1) → PipelineResult`

- Full pipeline:  
  1. Static checks  
  2. Semantic metrics (if static passes or `continue_on_static=True`)  
  3. Aggregates final `PipelineResult` with `static`, `semantic`, and `overall_valid`.  

### `run_async(...)`

- Asynchronous equivalent of `run_sync`.

---

## Example Usage

See `examples/function_calling/pipeline/example.py` for a complete, runnable demo:

```bash
python examples/function_calling/pipeline/example.py
```

It will:

1. Define three sample functions (`get_weather`, `create_event`, `translate_text`).  
2. Initialize Watsonx clients.  
3. Run sync reflection for valid and invalid calls.  
4. Print nicely formatted JSON results.

---

## Custom Metrics

By default we ship three JSONL files under `metrics/...`:

- **General**: overall call quality  
- **Function-Selection**: was the right function chosen?  
- **Parameter**: correctness of each parameter value  

Each line in a `.jsonl` file is a JSON object:

```jsonc
// general_metrics.jsonl
{"name":"Clarity", "description":"Rate clarity of the intent","schema":{...},
 "thresholds":{"output":[0,1],"confidence":[0,1]},
 "examples":[
   {"user_kwargs":{...}, "output":{...}}
 ]}
```

To add your own:

1. Create a new `.jsonl` in any folder.  
2. Pass its path into the pipeline constructor:

   ```python
   pipeline = ReflectionPipeline(
     metrics_client=...,
     codegen_client=...,
     general_metrics="path/to/my_general.jsonl",
     function_metrics="path/to/my_func.jsonl",
     parameter_metrics="path/to/my_param.jsonl",
   )
   ```

3. Follow the same JSONL format:  
   - `schema`: valid JSON-Schema object  
   - `thresholds`: dict of numeric field thresholds  
   - `examples`: few-shot examples validating against that schema  

---

## Transform-Enabled Mode

If you want automated unit conversions:

```python
pipeline = ReflectionPipeline(
  metrics_client=metrics_client,
  codegen_client=codegen_client,
  transform_enabled=True,
  transform_examples=my_transform_examples_dict,
)
```

- Uses two additional LLM prompts (in `transformation_prompts.py`):  
  1. **Extract units** from context  
  2. **Generate transformation code**  

- Finally executes the generated code in-process and reports a `TransformResult` per parameter.

---

## Error Handling & Logging

- Each stage wraps exceptions with clear, contextual messages.  
- The LLM clients emit optional hooks (`hooks=[...]`) for tracing or metrics.  
- In semantic phases, malformed or missing fields result in per-metric errors rather than crashing the entire pipeline.

---

Enjoy robust, end-to-end reflection on your function calls—static and semantic—powered entirely by `llmevalkit`!