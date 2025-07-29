
| Protocol Name | Flexible Evaluation Protocol (FEP) |
| :---- | :---- |
| **Version** | 0.0.1 |
| **Status** | Draft |
| **Last Update** | Jun 25, 2025 |
| **Author** | Shane Kercheval \- r.Potential |
| **Purpose** | This document proposes the `Flexible Evaluation Protocol` (`FEP`) \- a protocol for evaluating complex system outputs with standardized data formats, evaluation procedures, and complete REST/gRPC API specifications. |
| **Github** | Python Package: [https://github.com/shane-kercheval/flex-evals](https://github.com/shane-kercheval/flex-evals) |

```
Copyright © 2025 r.Potential Inc.

This specification is licensed under the Creative Commons
Attribution 4.0 International licence (CC-BY-4.0).
You may copy, distribute, translate, or create derivative works,
provided you give appropriate credit and indicate changes.
```

# Abstract {#abstract}

The **Flexible Evaluation Protocol (FEP)** is a vendor‑neutral, schema‑driven standard for measuring the quality of any system that produces complex or variable outputs \- whether they are deterministic APIs, non‑deterministic large‑language models, agentic workflows, or traditional software pipelines.

FEP defines:

* **Portable data formats** for test cases, system outputs, and result records.  
* **Pluggable “checks”** that support boolean, numeric, categorical, and free‑text assessments \- each addressable via JSON Schema and JSONPath.  
* **Reference APIs** (REST and gRPC) that let tooling run evaluations locally or at scale in the cloud.

By decoupling how outputs are *generated* from how they are *evaluated*, FEP delivers reproducible, multi‑criteria evaluations that are easy to share, automate, and audit across teams, organizations, and technology stacks.

For example, LLM benchmark suites such as `GSM‑8K` and `MMLU` ship in incompatible formats, each requiring its own bespoke evaluation harness and scoring script. Once those test cases are mapped onto FEP’s shared schema, a single FEP‑compliant runner can execute them against any model or agentic system (FEP is agnostic to how outputs are generated) and merge the resulting scores with an organization’s proprietary evaluations in one cohesive system.

[Abstract](#abstract)

[1\. Introduction](#1.-introduction)

[1.1 Purpose](#1.1-purpose)

[1.1.1 Broader Applicability](#1.1.1-broader-applicability)

[1.2 Scope](#1.2-scope)

[1.3 Terminology](#1.3-terminology)

[2\. Core Protocol Specification](#2.-core-protocol-specification)

[2.1 Test Cases](#2.1-test-cases)

[2.2 Output Format](#2.2-output-format)

[2.3 Checks](#2.3-checks)

[2.3.1 Evaluation Context](#2.3.1-evaluation-context)

[2.3.2 JSONPath vs Literal Values in Arguments](#2.3.2-jsonpath-vs-literal-values-in-arguments)

[2.3.3 Check-to-Test-Case Relationship Patterns:](#2.3.3-check-to-test-case-relationship-patterns:)

[2.3.4 Check Result Format](#2.3.4-check-result-format)

[2.3.5 Standard Check Definitions](#2.3.5-standard-check-definitions)

[2.3.6 Extended Check Definitions \- LLM/Agentic Evaluations](#2.3.6-extended-check-definitions---llm/agentic-evaluations)

[3\. Evaluation Interface](#3.-evaluation-interface)

[3.1 Core Evaluation Function](#3.1-core-evaluation-function)

[3.2 Experiment Metadata Format](#3.2-experiment-metadata-format)

[4\. Result Specifications](#4.-result-specifications)

[4.1 Test Case Result Format](#4.1-test-case-result-format)

[4.2 Evaluation Run Result Format](#4.2-evaluation-run-result-format)

[5\. API Specification](#5.-api-specification)

[5.1 REST API (OpenAPI 3.0)](#5.1-rest-api-\(openapi-3.0\))

[5.2 gRPC API (Protocol Buffers)](#5.2-grpc-api-\(protocol-buffers\))

[6\. Implementation Requirements](#6.-implementation-requirements)

[6.1 Compliance Levels](#6.1-compliance-levels)

[Level 1 \- Basic Compliance](#level-1---basic-compliance)

[Level 2 \- Full Compliance](#level-2---full-compliance)

[Level 3 \- Extended Compliance](#level-3---extended-compliance)

[6.2 JSONPath Implementation Notes](#6.2-jsonpath-implementation-notes)

[6.3 Versioning and Compatibility](#6.3-versioning-and-compatibility)

[6.4 Security Considerations](#6.4-security-considerations)

[7\. References](#7.-references)

---

# 1\. Introduction {#1.-introduction}

As software systems evolve, they increasingly integrate both deterministic and stochastic components \- each requiring different evaluation strategies. A typical workflow might call a deterministic micro-service, funnel the result through an LLM for natural‑language explanation, and then hand control to an autonomous agent to schedule delivery. Each layer exposes a different failure mode: arithmetic errors, semantic inaccuracies, policy violations, latency spikes, tool‑usage mis‑steps, and more.

Classic unit tests can assert that 2 \+ 2 \= 4, but they cannot judge whether the LLM’s explanation is clear or whether an agent chose the optimal path. Manual spot‑checks and trace reviews are critical for exploring failure modes, but do not scale. **FEP provides one evaluation fabric that spans the entire spectrum \- allowing strict equality checks where determinism matters and rubric‑based or probabilistic checks where nuance rules \- all encoded in a single, JSON‑based contract.**

The protocol is designed around three guiding principles:

1. **Flexibility first.** Every field in FEP can hold either a literal value or a JSONPath that resolves dynamically at runtime, enabling users to evaluate anything from a plain‑text answer to a deeply nested execution trace.  
2. **Separation of concerns.** Generation and evaluation are treated as independent phases. Systems under test remain black boxes; evaluators only need the inputs and produced outputs.  
3. **Interoperability and reproducibility.** With strict schemas and semantic versioning, FEP results can be compared apples‑to‑apples across different vendors, model versions, or deployment setups.

## 1.1 Purpose {#1.1-purpose}

FEP exists to give engineers, researchers, and auditors a repeatable, machine‑readable way to answer the question, “Did this system behave acceptably?” By providing shared schemas and a unified evaluation contract, FEP enables:

* Standardizing LLM benchmarks like GSM‑8K or MMLU across providers without reinventing scoring logic or data formats  
* Running internal and external benchmarks interchangeably using a single evaluation engine or pipeline  
* Multi‑criteria quality checks that combine boolean, numeric, and semantic assessments within one protocol  
* Consistent evaluations across models, vendors, and versions, enabling fair comparison and longitudinal tracking  
* Integrating rich acceptance tests into CI/CD beyond traditional pass/fail logic  
* Supporting audit and compliance use cases with versioned schemas and traceable results

### 1.1.1 Broader Applicability {#1.1.1-broader-applicability}

Although originally motivated by the challenges of evaluating non-deterministic systems (e.g., large language models), FEP’s design is general-purpose. Its value extends to any domain where outputs are complex, variable, or multi-dimensional:

* **Data pipeline QA**, where intermediate and final outputs must meet conditional criteria  
* **Autonomous agents and tool-using systems**, where evaluation involves traces, tool usage, or external actions  
* **Custom product evaluation frameworks**, where product-specific metrics and domain rules must be applied  
* **A/B testing infrastructures**, where evaluation must separate signal from noise across variant outputs

FEP allows all of these systems to express and evaluate expectations using a consistent, extensible protocol \- without prescribing how systems are built or outputs are generated.

## 1.2 Scope {#1.2-scope}

FEP specifies:

* Test‑case, output, check, and result schemas.  
* Execution interfaces for running evaluations.  
* Reporting structures.

FEP deliberately does **not** dictate:

* How systems generate their outputs.  
* Which statistical methods are used to aggregate mixed result types.  
* Human‑in‑the‑loop workflows.  
* Storage, deployment, or UI specifics.

## 1.3 Terminology {#1.3-terminology}

`Test Case`: A single evaluation unit consisting of input, an optional expected value, and optional metadata.

`Check`: An evaluation function that assesses (i.e. evaluates) some aspect of the system's output generated from the corresponding test case. *The term* `check` *is used rather than* `metric` *or* `score` *(which are commonly used in LLM evaluation APIs) because we are "checking" various aspects of the output; checks can return boolean results, categorical assessments, structured annotations, or numerical scores. "Metrics" implies numerical measurement, but "checks" can be qualitative.*

`Output`: The output produced by the system being evaluated. *FEP considers output generation a black box; therefore, outputs must be created before evaluation, as the FEP-compliant system itself does not natively generate responses.*

`Evaluation Context`: The data that a `check` has access to for evaluation, including the `test case` and `output`.

`Evaluation Run`: The execution of one or more checks against a collection of test cases and their corresponding outputs.

---

# 2\. Core Protocol Specification {#2.-core-protocol-specification}

`FEP (Flexible Evaluation Protocol)`  
`├── 📋 Test Cases`  
`│   ├── id (required)`  
`│   ├── input (required)`  
`│   ├── expected (optional)`  
`│   └── metadata (optional)`  
`│`  
`├── 📤 Outputs`  
`│   ├── id (optional)`  
`│   ├── value (required)`  
`│   └── metadata (optional)`  
`│`  
`├── ✅ Checks`  
`│   ├── type (required)`  
`│   ├── arguments (required)`  
`│   └── version (optional)`  
`│`  
`└── 📊 Results Hierarchy`  
    `└── Evaluation Run Result`  
        `├── evaluation_id`  
        `├── status`  
        `├── summary`  
        `├── experiment (optional)`  
        `└── results[]`  
            `└── Test Case Result`  
                `├── execution_context`  
                `│   ├── test_case`  
                `│   └── output`  
                `├── status`    
                `├── summary`  
                `└── check_results[]`  
                    `└── Check Result`  
                        `├── check_type`  
                        `├── status`  
                        `├── results (check-specific)`  
                        `├── resolved_arguments`  
                        `├── evaluated_at`  
                        `├── metadata`  
                        `└── error (if status = error)`

## 2.1 Test Cases {#2.1-test-cases}

A test case provides the input and optional expected output for evaluation. Checks (described below) define how the evaluation is performed. Together, they form the complete evaluation specification.

**Purpose**: Represents a single evaluation unit with input data and optional expected output for checks to reference.

##### Schema

```
{
  "id": "string (required)",
  "input": "string | object (required)",
  "expected": "string | object | null (optional)",
  "metadata": "object (optional)"
}
```

##### Required Fields

* `id`: Unique identifier for the test case  
* `input`: The input provided to the system being evaluated

##### Optional Fields

* `expected`: Reference output for comparison or validation (can contain any structure)  
* `metadata`: Descriptive information about the test case (open structure)

##### Example:

```
id: "test_001"
input:
  - role: "system"
    message: "You are a helpful assistant."
  - role: "user"
    message: "What is the capital of France?"
expected:
  - role: "assistant"
    message: "Paris"

metadata:
  version: 0.0.1
  tags: ["geography"]                 # Example / Not in Official Spec
  data_source: "knowledge_qa"         # Example / Not in Official Spec
  created_at: "2025-06-25T10:00:00Z"  # Example / Not in Official Spec
```

## 2.2 Output Format {#2.2-output-format}

**Purpose**: Contains the output generated by the system being evaluated, along with optional metadata about the generation process. As mentioned, the output generation process is treated as a black box by the protocol. The output, combined with the test case, form the complete “evaluation context” that is given to the checks.

##### Schema

```
{
  "id": Unique identifier for this output. Useful for traceability, caching, and complex evaluation scenarios.
  "value": "string | object (required)",
  "metadata": "object (optional)"
}
```

##### Required Fields

* `value`: The actual output from the system being evaluated (can contain any structure). Checks can reference specific attributes of the `value` structure via JSONPath described below.

##### Optional Fields

* `metadata`: System-specific information about the output generation (open structure)

##### Key Design Principle

The `value` field can contain whatever the system naturally outputs \- whether simple text, structured data, or complex objects with traces and metadata. This respects the system's output boundaries while allowing the evaluation framework to add its own metadata separately.

##### Examples:

```
# Simple text output
value: "The capital of France is Paris."
metadata:
  execution_time_ms: 245
  model_version: "gpt-4-turbo"

# Complex structured output
value:
  output:
  - role: "assistant"
    message: "Paris"
  confidence: 0.95
  reasoning: "Based on geographical knowledge..."
  trace:
    - step: "knowledge_lookup"
      result: "France -> Paris"
metadata:
  execution_time_ms: 380
  cost_usd: 0.0023

# Example where performance is assumed to be part of the evaluation
# (i.e. included in value rather than metadata)
value:
  result: "Booking confirmed for flight UA123"
  execution_data:
    tools_used: ["flight_search", "booking_api"]
    total_cost: "$450.00"
    processing_time: "2.3s"
    execution_time_ms: 2300
metadata:
  api_version: "v2.1"
```

## 2.3 Checks {#2.3-checks}

**Purpose**: Defines evaluation criteria for test cases, specifying how to assess outputs. Each check definition represents a single evaluation function with its required arguments.

##### Schema

```
{
  "type": "string (required)",
  "arguments": "object (required)",
  "version": "string (semver) (optional)",
}
```

##### Required Fields

* `type`: Identifier for the check implementation (e.g., `exact_match`, `contains`, `regex`)  
* `arguments`: Parameters passed to the check function \- specific to each check type

##### Optional Fields

* `version`: Semantic version of the check implementation

### 2.3.1 Evaluation Context {#2.3.1-evaluation-context}

The structure and corresponding data available for checks to evaluate (i.e. “execution context”) is the combination of the `test case` and the `output`:

##### Schema

```
{
  "test_case": {
    "id": "string",
    "input": "string | object", 
    "expected": "string | object | null",
    "metadata": "object"
  },
  "output": {
    "value": "string | object",
    "metadata": "object"
  }
}
```

##### Key Access Patterns

* `$.test_case.input` \- Access the original input  
* `$.test_case.expected` \- Access the expected/reference output  
* `$.output.value` \- Access the system's actual output (most common)  
* `$.output.value.custom_property` \- Access a property within the output  
* `$.output.metadata` \- Access metadata  
* `$.output.metadata.custom_property` \- Access a property within the metadata

### 2.3.2 JSONPath vs Literal Values in Arguments {#2.3.2-jsonpath-vs-literal-values-in-arguments}

Check arguments support two types of values: **literal values** and **JSONPath expressions**. This provides powerful flexibility for evaluation:

##### Literal Values

```
type: exact_match
arguments:
  expected: "Paris"                    # Literal string
  actual: <we need a way to specify the `value` property in `output` structure>
```

##### JSONPath Expressions

Strings beginning with `$.` are automatically interpreted as JSONPath expressions that extract data from the evaluation context:

```
type: exact_match
arguments:
  expected: "$.test_case.expected"     # Extract from test case
  actual: "$.output.value"             # Extract from output
```

##### Escape Syntax for Literal Dollar Signs

To use a literal string that begins with `$.`, escape it with a backslash:

```
arguments:
  pattern: "\\$.this.is.literal"       # Literal: "$.this.is.literal"
  text: "$.output.value"               # JSONPath: extracts output value
```

##### Common Patterns

```
# Compare output to expected value
arguments:
  actual: "$.output.value"
  expected: "$.test_case.expected"

# Check system confidence score.
arguments:
  value: "$.output.value.confidence"
  min_threshold: 0.8

# Validate execution time
arguments:
  value: "$.output.metadata.execution_time_ms"
  max_value: 5000

# Check tool usage in system trace
arguments:
  items: "$.output.value.trace.tools_used"
  required_items: ["search", "calculator"]
```

### **2.3.3 Check-to-Test-Case Relationship Patterns:** {#2.3.3-check-to-test-case-relationship-patterns:}

While this **protocol is agnostic to test case organization and storage**, users will commonly organize their evaluations in two patterns: **shared checks** (same evaluation criteria applied to all test cases) or **per-test-case checks** (custom evaluation criteria for each test case). *Regardless of organization, test cases and checks are passed to the evaluation method using the same interface; see* [*3\. Evaluation Interface*](#3.-evaluation-interface)*.*

##### Pattern 1: Shared Checks (1-to-Many)

`# One set of checks applied to all test cases`  
`Evaluation`  
`├── Test Cases [Array]`  
`│   ├── Test Case 1`  
`│   ├── Test Case 2`  
`│   └── Test Case N`  
`│`  
`└── Checks [Array] ────┐`  
    `├── Check A        │ Applied to ALL`  
    `├── Check B        │ test cases`  
    `└── Check C ───────┘`

`Results:`  
`├── Test Case 1 → [Check A result, Check B result, Check C result]`  
`├── Test Case 2 → [Check A result, Check B result, Check C result]`    
`└── Test Case N → [Check A result, Check B result, Check C result]`

##### Pattern 2: Per-Test-Case Checks (1-to-1)

`# Each test case has its own specific checks`  
`Evaluation`  
`├── Test Case 1`  
`│   └── Checks [Array]`  
`│       ├── Check A`  
`│       └── Check B`  
`│`  
`├── Test Case 2`    
`│   └── Checks [Array]`  
`│       ├── Check C`  
`│       ├── Check D`  
`│       └── Check E`  
`│`  
`└── Test Case N`  
    `└── Checks [Array]`  
        `└── Check F`

`Results:`  
`├── Test Case 1 → [Check A result, Check B result]`  
`├── Test Case 2 → [Check C result, Check D result, Check E result]`  
`└── Test Case N → [Check F result]`

##### Example

```
# Pattern 1: Shared Checks (1-to-many relationship)
# Same evaluation criteria applied to all test cases
test_cases:
  - id: "test_001"
    input: "What is the capital of France?"
    expected: "Paris"
  - id: "test_002"
    input: "What is 2 + 2?"
    expected: "4"

checks:
  - type: exact_match
    arguments:
      actual: "$.output.value"
      expected: "$.test_case.expected"

# Pattern 2: Per-Test-Case Checks (checks defined inline with each test case)
test_cases:
  - id: "test_001"
    input: "Write a Python function that returns the nth Fibonacci number."
    checks:
      - type: regex
        arguments:
          text: "$.output.value"
          pattern: "^def fibonacci\\(n\\):"

  - id: "test_002"
    input: "Write a Python function that checks if a string is a palindrome."
    checks:
      - type: regex
        arguments:
          text: "$.output.value"
          pattern: "^def is_palindrome\\(s\\):"
```

### 2.3.4 Check Result Format {#2.3.4-check-result-format}

**Purpose:** Represents the complete results of executing a single check against a test case and system output. This format provides full auditability by capturing the execution context metadata (i.e. test case and output), resolved arguments, check outcome, and any errors that occurred. The structure separates execution status (whether the check ran successfully) from the evaluation outcome. **Each check type defines its own results schema** \- implementations must understand the specific check types they support and handle the corresponding result structures. FEP-compliant systems are responsible for result extraction and aggregation based on check-type-specific result schemas.

##### Schema

```
{
  "type": "object",
  "required": ["check_type", "status", "results", "evaluated_at", metadata],
  "properties": {
    "check_type": {
      "type": "string",
      "description": "The type of check that was executed"
    },
    "status": {
      "type": "string",
      "enum": ["completed", "error", "skip"],
      "description": "Execution status of the check"
    },
    "evaluated_at": {
      "type": "string",
      "format": "date-time", 
      "description": "UTC timestamp when check was evaluated (ISO 8601 format)"
    },
    "results": {
      "type": "object",
      "description": "Check outcome data. Structure and required fields are defined by the specific check type."
    },
    "resolved_arguments": {
      "type": "object", 
      "description": "Arguments after JSONPath resolution. Each argument has a 'value' field containing the resolved value. JSONPath expressions also include an optional 'jsonpath' field showing the original expression.",
      "additionalProperties": true
    },
    "metadata": {
      "type": "object",
      "properties": {
        "check_version": {
          "type": "string (semver)",
          "description": "Version of the check definition."
        }
      },
      "additionalProperties": true,
      "description": "Check-specific metadata about execution, performance, configuration, etc."
    },
    "error": {
      "type": "object",
      "required": ["type", "message"],
      "properties": {
        "type": {
          "type": "string",
          "enum": ["jsonpath_error", "validation_error", "timeout_error", "unknown_error"],
          "description": "Category of error that occurred"
        },
        "message": {
          "type": "string",
          "description": "Human-readable error description"
        },
        "recoverable": {
          "type": "boolean",
          "default": false,
          "description": "Whether this error could be retried"
        }
      },
      "description": "Error details (only present when status is 'error')"
    }
  }
}
```

##### Required Fields

* `check_type`: Identifier for the type of check that was executed (e.g., `exact_match`, `threshold`)  
* `status`: Execution status indicating whether the check ran successfully (`completed`), encountered an error (`error`), or was skipped (`skip`)  
* `evaluated_at`: UTC timestamp in ISO 8601 format indicating when the check was executed  
* `results`: Check-specific result object. **Structure and required fields depend entirely on the check type.** Each check type defines its own results schema (e.g., `exact_match` returns `{passed: boolean}`, `semantic_similarity` returns `{score: number, passed?: boolean}`)  
* `resolved_arguments`: Shows the final values used by the check after JSONPath expressions are resolved, providing transparency into what data was actually compared or evaluated  
* `metadata`: Check-specific metadata about execution, performance, configuration, etc.  
  * `check_version`: Version of the check definition  
* `error`: Error details present only when status is "error", including error type, message, and whether the error is recoverable

##### Example

```
# failed match
check_type: "exact_match"
status: "completed"
evaluated_at: "2025-06-26T19:04:23Z"
results:
  passed: false
resolved_arguments:
  actual:
    jsonpath: "$.output.value"       # optional - only present if JSONPath was used
    value: "paris"                   # always present - the resolved value
  expected:
    jsonpath: "$.test_case.expected" # optional - only present if JSONPath was used  
    value: "Paris"                   # always present - the resolved value
  case_sensitive:
    value: true                      # no jsonpath field since it was literal

metadata:
  check_version: "1.0.0"
```

### 2.3.5 Standard Check Definitions {#2.3.5-standard-check-definitions}

Official standard check types that FEP-compliant systems should implement. These are part of the protocol specification with defined argument schemas.

#### **`exact_match`**

**Purpose**: Compares two text values for exact equality

##### Arguments Schema

```
{
  "type": "object",
  "required": ["actual", "expected"],
  "properties": {
    "actual": {
      "oneOf": [
        {"type": "string"},
        {"type": "string", "pattern": "^\\$\\."}
      ],
      "description": "Literal value or JSONPath expression for the value to check"
    },
    "expected": {
      "oneOf": [
        {"type": "string"},
        {"type": "string", "pattern": "^\\$\\."}
      ],
      "description": "Literal value or JSONPath expression to compare against"
    },
    "negate": {
      "type": "boolean",
      "default": false,
      "description": "If true, passes when values don't match"
    },
    "case_sensitive": {
      "type": "boolean",
      "default": true,
      "description": "Whether string comparison is case-sensitive"
    }
  }
}
```

##### Example

```
type: "exact_match"
arguments:
  actual: "$.output.value"
  expected: "$.test_case.expected"
  case_sensitive: false
  negate: false
```

##### Results Schema

```
{
  "type": "object",
  "required": ["passed"],
  "properties": {
    "passed": {
      "type": "boolean",
      "description": "Whether the exact match check passed. True if values match (or don't match when negate=true), false otherwise."
    }
  }
}
```

##### Results Example

```
# Arguments: actual="Paris", expected="Paris", case_sensitive=true, negate=false
results:
  passed: true
```

#### **`contains`**

**Purpose**: Checks if text contains all specific phrases or patterns

##### Arguments Schema

```
{
  "type": "object",
  "required": ["text", "phrases"],
  "properties": {
    "text": {
      "oneOf": [
        {"type": "string"},
        {"type": "string", "pattern": "^\\$\\."}
      ],
      "description": "Literal text or JSONPath expression for the text to search"
    },
    "phrases": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 1,
      "description": "Array of strings that must be present in the text"
    },
    "negate": {
      "type": "boolean",
      "default": false,
      "description": "If true, passes when the text contains none of the phrases. If false, passes when the text contains all of the phrases"
    },
    "case_sensitive": {
      "type": "boolean",
      "default": true,
      "description": "Whether phrase matching is case-sensitive"
    }
  }
}
```

##### Example

```
type: "contains"
arguments:
  text: "$.output.value"
  phrases: ["Paris", "France"]
```

##### Example

```
type: "contains"
arguments:
  text: "$.output.value.trace.status"  # JSONPath to trace status
  phrases: ["error", "failed", "exception"]
  negate: true  # Pass if none of these errors/phrases are found
  case_sensitive: false
```

##### Response Schema

```
{
  "type": "object",
  "required": ["passed"],
  "properties": {
    "passed": {
      "type": "boolean",
      "description": "Whether the contains check passed. When negate=false, true if ALL phrases are found. When negate=true, true if NONE of the phrases are found."
    }
  }
}
```

##### Example

```
# Arguments: text="Paris is the capital of France", phrases=["Paris", "France"], negate=false, case_sensitive=true
results:
  passed: true
```

####  **`regex`**

**Purpose**: Tests text against regular expression patterns

##### Arguments Schema

```
{
  "type": "object",
  "required": ["text", "pattern"],
  "properties": {
    "text": {
      "oneOf": [
        {"type": "string"},
        {"type": "string", "pattern": "^\\$\\."}
      ],
      "description": "Literal text or JSONPath expression for the text to test"
    },
    "pattern": {
      "type": "string",
      "description": "Regular expression pattern to match against the text"
    },
    "negate": {
      "type": "boolean",
      "default": false,
      "description": "If true, passes when pattern doesn't match"
    },
    "flags": {
      "type": "object",
      "properties": {
        "case_insensitive": {
          "type": "boolean",
          "default": false,
          "description": "If true, ignores case when matching"
        },
        "multiline": {
          "type": "boolean", 
          "default": false,
          "description": "If true, ^ and $ match line boundaries in addition to string boundaries"
        },
        "dot_all": {
          "type": "boolean",
          "default": false,
          "description": "If true, . matches newline characters"
        }
      },
      "description": "Regex matching options"
    }
  }
}
```

##### Example

```
# email verification
type: "regex"
arguments:
  text: "$.output.value"
  pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
  flags:
    case_insensitive: true
```

##### Example

```
# Multiline pattern matching
type: "regex"
arguments:
  text: "$.test_case.context.log_output"
  pattern: "^ERROR:"
  flags:
    case_insensitive: false
    multiline: true  # ^ matches start of any line
    dot_all: false
  negate: false
```

##### Response Schema

```
{
  "type": "object",
  "required": ["passed"],
  "properties": {
    "passed": {
      "type": "boolean",
      "description": "Whether the regex check passed. When negate=false, true if pattern matches the text. When negate=true, true if pattern doesn't match the text."
    }
  }
}
```

##### Example

```
# Arguments: text="user@example.com", pattern="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", negate=false
results:
  passed: true
```

####  **`threshold`**

**Purpose**: Checks if a numeric value meets minimum/maximum thresholds

##### Arguments Schema

```
{
  "type": "object", 
  "required": ["value"],
  "anyOf": [
    {"required": ["min_value"]},
    {"required": ["max_value"]},
    {"required": ["min_value", "max_value"]}
  ],
  "properties": {
    "value": {
      "oneOf": [
        {"type": "number"},
        {"type": "string", "pattern": "^\\$\\."}
      ],
      "description": "Literal number or JSONPath expression for the value to check"
    },
    "min_value": {
      "type": "number",
      "description": "Minimum acceptable value"
    },
    "max_value": {
      "type": "number",
      "description": "Maximum acceptable value"
    },
    "min_inclusive": {
      "type": "boolean",
      "default": true,
      "description": "If true, min_value is inclusive (>=), if false, exclusive (>)"
    },
    "max_inclusive": {
      "type": "boolean", 
      "default": true,
      "description": "If true, max_value is inclusive (<=), if false, exclusive (<)"
    },
    "negate": {
      "type": "boolean",
      "default": false,
      "description": "If true, passes when value is outside the specified range"
    }
  },
  "additionalProperties": false
}
```

##### Example

```
# Range check (inclusive bounds)
type: "threshold"
arguments:
  value: "$.output.confidence_score"
  # min_inclusive and max_inclusive default to true
  min_value: 0.8
  max_value: 1.0
```

##### Example

```
# Minimum only (exclusive)  
type: "threshold"
arguments:
  value: "$.test_case.context.latency"
  min_value: 0
  min_inclusive: false  # Must be > 0, not >= 0
```

##### Example

```
# Negated range (outside bounds)
type: "threshold" 
arguments:
  value: "$.output.temperature"
  min_value: 20
  max_value: 80
  negate: true  # Pass if temp < 20 or temp > 80
```

##### Response Schema

```
{
  "type": "object",
  "required": ["passed"],
  "properties": {
    "passed": {
      "type": "boolean",
      "description": "Whether the threshold check passed. When negate=false, true if value meets all specified threshold constraints. When negate=true, true if value violates at least one threshold constraint."
    }
  }
}
```

##### Example

```
# Arguments: value=0.85, min_value=0.8, max_value=1.0, min_inclusive=true, max_inclusive=true, negate=false
results:
  passed: true
```

### 2.3.6 Extended Check Definitions \- LLM/Agentic Evaluations {#2.3.6-extended-check-definitions---llm/agentic-evaluations}

Extended check types suitable for LLM & Agentic Workflow Evaluations. These are part of the protocol specification with defined argument schemas.

**`semantic_similarity`**  
**Purpose**: Measures semantic similarity between two texts using embeddings

##### Requirements

* **embedding model**: Access to embedding model API. Handled directly by FEP-compliant system

##### Arguments Schema

```
{
  "type": "object",
  "required": ["text", "reference"],
  "properties": {
    "text": {
      "oneOf": [
        {"type": "string"},
        {"type": "string", "pattern": "^\\$\\."}
      ],
      "description": "Literal text or JSONPath expression for the text to evaluate"
    },
    "reference": {
      "oneOf": [
        {"type": "string"}, 
        {"type": "string", "pattern": "^\\$\\."}
      ],
      "description": "Literal text or JSONPath expression for reference text"
    },
    "threshold": {
      "type": "object",
      "properties": {
        "min_value": {"type": "number", "minimum": 0, "maximum": 1},
        "max_value": {"type": "number", "minimum": 0, "maximum": 1},
        "min_inclusive": {"type": "boolean", "default": true},
        "max_inclusive": {"type": "boolean", "default": true},
        "negate": {"type": "boolean", "default": false}
      }
    },
    "provider_config": {
      "type": "object",
      "description": "Implementation-specific provider configuration (e.g. endpoints, API keys, etc.)"
    },
    "model_config": {
      "type": "object", 
      "description": "Implementation-specific model configuration (e.g. dimensions, encoding, etc.)"
    },
    "similarity_metric": {
      "type": "string",
      "default": "cosine",
      "description": "Distance metric for similarity calculation (implementation-specific)"
    }
  }
}
```

##### Example

```
type: "semantic_similarity"
arguments:
  text: "$.output.response"
  reference: "$.test_case.expected_response"
  threshold:
    min_value: 0.8
  provider_config:
    provider_name: "openai"
    base_url: "https://custom.api.endpoint/v1"
    timeout: 30
    max_retries: 3
  model_config:
    model: "text-embedding-3-small"
    dimensions: 1536
    encoding_format: "float"
  similarity_metric: "cosine"
```

##### Response Schema

```
{
  "type": "object",
  "description": "Semantic similarity results containing both similarity analysis and execution metadata",
  "required": ["similarity_response", "similarity_metadata"],
  "properties": {
    "response": {
      "type": "object",
      "required": ["score"],
      "properties": {
        "score": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Semantic similarity score between 0 (no similarity) and 1 (identical meaning)"
        },
        "passed": {
          "type": "boolean",
          "description": "Whether the similarity score meets the specified threshold criteria. Only present when threshold is defined in arguments."
        }
      },
      "additionalProperties": false
    },
    "metadata": {
      "type": "object",
      "description": "Implementation-specific execution metadata from the embedding API call (e.g., costs, performance metrics, model details). The exact fields depend on the embedding provider and implementation.",
      "additionalProperties": true
    }
  },
  "additionalProperties": false
}
```

##### Example

```
# Arguments: score=0.87, threshold.min_value=0.8, threshold.negate=false
results:
  response:
    score: 0.87
    passed: true
  metadata:
    cost_usd: 0.0001
    tokens_processed: 45
    response_time_ms: 120
    model_version: "text-embedding-3-small"
    dimensions_used: 1536
```

**`llm_judge`**  
**Purpose**: Uses an LLM to evaluate text quality based on specified criteria

##### Requirements

* **LLM model**: Access to embedding model API. Handled directly by FEP-compliant system

##### Arguments Schema

```
{
  "type": "object",
  "required": ["prompt", "response_format"],
  "properties": {
    "prompt": {
      "type": "string",
      "description": "Evaluation prompt with {{$.jsonpath}} placeholders"
    },
    "response_format": {
      "type": "object",
      "description": "JSON Schema defining expected response structure from the judge"
    },
    "provider_config": {
      "type": "object",
      "description": "Implementation-specific LLM provider configuration"
    },
    "model_config": {
      "type": "object",
      "description": "Implementation-specific model parameters"
    }
  }
}
```

##### Example

```
type: "llm_judge"
arguments:
  prompt: |
    Evaluate if the response fully addresses the user's question:
    
    User Input: `{{$.input.user_message}}`
    AI Response: `{{$.output.response}}`
  response_format:
    type: "object"
    required: ["is_addressed", "reasoning"]
    properties:
      is_addressed:
        type: "boolean"
        description: "True if the response fully addresses the user's question"
      reasoning:
        type: "string"
        description: "Brief explanation justifying `is_addressed` choice"
  provider_config:
    base_url: "https://api.openai.com/v1"
    api_key: "${OPENAI_API_KEY}"
  model_config:
    model: "gpt-4o"
    temperature: 0.0
```

##### Response Schema

**Note**: The results structure is entirely determined by the `response_format` defined in the `llm_judge` check arguments. FEP-compliant systems should validate the LLM response against the provided schema and return the structured result as-is.

```
{
  "type": "object",
  "description": "LLM judge results containing both evaluation results and execution metadata",
  "required": ["judge_response", "judge_metadata"],
  "properties": {
    "response": {
      "type": "object",
      "description": "Evaluation results matching the structure defined in arguments.response_format. The exact fields and their types depend on the response_format specification.",
      "additionalProperties": true
    },
    "metadata": {
      "type": "object",
      "description": "Implementation-specific execution metadata e.g. from the LLM API call (e.g., costs, performance metrics, model details). The exact fields depend on the LLM provider and implementation.",
      "additionalProperties": true
    }
  },
  "additionalProperties": false
}
```

##### Example

```
# LLM Judge results contain both evaluation and execution metadata
results:
  response:
    # dictated by response_format
    is_addressed: true
    reasoning: "The response directly answers the question about France's capital by stating 'Paris is the capital of France.'"
  metadata:
    # example of metadata returned
    cost_usd: 0.0023
    tokens_used: 150
    response_time_ms: 842
    model_version: "gpt-4o-mini-2024-07-18"
    finish_reason: "stop"
```

---

# 3\. Evaluation Interface {#3.-evaluation-interface}

## 3.1 Core Evaluation Function {#3.1-core-evaluation-function}

**Purpose**: Defines the standard interface that all FEP-compliant systems must implement for running evaluations.

All FEP-compliant systems must implement this interface:

```
EVALUATE(test_cases, outputs, checks, experiment_metadata) → EvaluationRunResult

PARAMETERS:
  test_cases: Array<TestCase>
  outputs: Array<Output>
  checks: Array<Check> OR Array<Array<Check>>
  experiment_metadata: ExperimentMetadata (optional)

RETURNS:
  EvaluationRunResult (as defined in Section 4.2)

CONSTRAINTS:
  - test_cases.length == outputs.length
  - test_cases[i] is associated with outputs[i]
  - If checks is Array<Check>: apply same checks to all test cases (Pattern 1)
  - If checks is Array<Array<Check>>: checks[i] applies to test_cases[i] (Pattern 2)
```

##### Example Evaluate Call (Input)

```
test_cases:
  - id: "test_001"
    input: "What is the capital of France?"
    expected: "Paris"

outputs:
  - value: "The capital of France is Paris."

checks:
  - type: "exact_match"
    arguments:
      actual: "$.output.value"
      expected: "$.test_case.expected"

experiment_metadata:
  name: "geography_test_v1"
```

##### Example Response Structure

```
# Returns EvaluationRunResult
evaluation_id: "eval_12345"
started_at: "2025-06-26T10:00:00Z"
completed_at: "2025-06-26T10:00:02Z"
status: "completed"
experiment:
  name: "geography_test_v1"
summary:
  total_test_cases: 1
  completed_test_cases: 1
  error_test_cases: 0
  skipped_test_cases: 0
results:
  - status: "completed"
    execution_context:
      test_case:
        id: "test_001"
        input: "What is the capital of France?"
        expected: "Paris"
      output:
        value: "The capital of France is Paris."
    check_results:
      - check_type: "exact_match"
        status: "completed"
        results:
          passed: true
        evaluated_at: "2025-06-26T10:00:01Z"
        resolved_arguments:
          actual:
            jsonpath: "$.output.value"
            value: "The capital of France is Paris."
          expected:
            jsonpath: "$.test_case.expected"
            value: "Paris"
        metadata:
          check_version: "1.0.0"
    summary:
      total_checks: 1
      completed_checks: 1
      error_checks: 0
      skipped_checks: 0
```

## 3.2 Experiment Metadata Format {#3.2-experiment-metadata-format}

**Purpose**: Provides optional context about the evaluation experiment for tracking and comparison purposes.

##### Schema

```
{
  "name": "string (optional)",
  "metadata": "object (optional)"
}
```

##### Optional Fields

* `name`: Human-readable experiment identifier  
* `metadata`: Additional experiment-specific information (open structure)

##### Example:

```
name: "gpt4_vs_claude_math"

metadata:
  baseline_experiment_id: "exp_001"    # Suggested / Not in Official Spec
  model_version: "gpt-4-turbo"         # Suggested / Not in Official Spec
  prompt_version: "v3.2"               # Suggested / Not in Official Spec
  dataset_version: "math_eval_v1.0"    # Suggested / Not in Official Spec
```

---

# 4\. Result Specifications {#4.-result-specifications}

## 4.1 Test Case Result Format {#4.1-test-case-result-format}

**Purpose**: Aggregates the results of all checks run against a single test case, providing both individual check results and summary statistics.

##### Schema

```
{
  "type": "object",
  "required": ["status", "execution_context", "check_results", "summary"],
  "properties": {
    "status": {
      "type": "string",
      "enum": ["completed", "error", "skip"],
      "description": "Computed overall status based on individual check statuses"
    },
    "execution_context": {
      "type": "object",
      "required": ["test_case", "output"],
      "properties": {
        "test_case": {
          "type": "TestCase",
          "description": "Complete test case that was evaluated (for full context and auditability)"
        },
        "output": {
          "type": "Output", 
          "description": "Complete output that was evaluated (for full context and auditability)"
        }
      },
      "additionalProperties": false,
      "description": "Complete execution context - the test case and output that were evaluated together"
    },
    "check_results": {
      "type": "array",
      "items": "CheckResult",
      "description": "Array of individual check execution results"
    },
    "summary": {
      "type": "object",
      "required": ["total_checks", "completed_checks", "error_checks", "skipped_checks"],
      "properties": {
        "total_checks": {"type": "integer", "minimum": 0},
        "completed_checks": {"type": "integer", "minimum": 0},
        "error_checks": {"type": "integer", "minimum": 0},
        "skipped_checks": {"type": "integer", "minimum": 0}
      },
      "description": "Aggregate statistics for all check results"
    },
    "metadata": {
      "type": "object",
      "additionalProperties": true,
      "description": "Optional implementation-specific metadata (performance, cost, etc.)"
    }
  },
  "additionalProperties": false
}
```

##### Status Field Logic

The `status` field is computed from individual check statuses using the following precedence rules:

* `completed`: All checks have status: `completed`  
* `error`: At least one check has status: `error`  
* `skip`: No errors, but at least one check has status: `skip`

This provides a convenient execution summary without analyzing individual check results or their semantic outcomes.

##### Example (Minimal Protocol Compliance)

```
status: "completed"
execution_context:
  test_case:
    id: "test_001"
    input: "What is the capital of France?"
    expected: "Paris"
    metadata:
      version: "1.0.1"
      tags: ["geography"]
  output:
    id: "out_001_run_123"
    value: "The capital of France is Paris."
    metadata:
      execution_time_ms: 245
      model_version: "gpt-4-turbo"
check_results:
  - check_type: "exact_match"
    status: "completed"
    results:
      passed: true
    evaluated_at: "2025-06-26T19:04:23Z"
    resolved_arguments:
      actual:
        jsonpath: "$.output.value"
        value: "Paris"
      expected:
        jsonpath: "$.test_case.expected"
        value: "Paris"
    metadata:
      check_version: "1.0.0"
summary:
  total_checks: 1
  completed_checks: 1
  error_checks: 0
  skipped_checks: 0
```

##### Example (Implementation Extension)

```
status: "completed"
execution_context:
  test_case:
    id: "test_001"
    input: "What is the capital of France?"
    expected: "Paris"
    metadata:
      version: "1.0.1"
      tags: ["geography"]
  output:
    id: "out_001_run_123"
    value: "The capital of France is Paris."
    metadata:
      execution_time_ms: 245
      model_version: "gpt-4-turbo"
check_results:
  - check_type: "exact_match"
    status: "completed"
    results:
      passed: true
    evaluated_at: "2025-06-26T19:04:23Z"
    resolved_arguments:
      actual:
        jsonpath: "$.output.value"
        value: "Paris"
      expected:
        jsonpath: "$.test_case.expected"
        value: "Paris"
    metadata:
      check_version: "1.0.0"
summary:
  total_checks: 1
  completed_checks: 1
  error_checks: 0
  skipped_checks: 0
metadata:
  execution_time_ms: 245
  cost_usd: 0.0023
  tokens_used: 150
  model_calls: 1
```

## 4.2 Evaluation Run Result Format {#4.2-evaluation-run-result-format}

**Purpose**: Provides comprehensive results for an entire evaluation run, including experiment context, summary statistics, and all individual test case results.

```
{
  "type": "object",
  "required": ["evaluation_id", "started_at", "completed_at", "status", "summary", "results"],
  "properties": {
    "evaluation_id": {
      "type": "string",
      "description": "Unique identifier for this evaluation run"
    },
    "started_at": {
      "type": "string",
      "format": "date-time",
      "description": "When the evaluation started (ISO 8601 UTC)"
    },
    "completed_at": {
      "type": "string", 
      "format": "date-time",
      "description": "When the evaluation completed (ISO 8601 UTC)"
    },
    "status": {
      "type": "string",
      "enum": ["completed", "error", "skip"],
      "description": "Overall evaluation execution status"
    },
    "summary": {
      "type": "object",
      "required": ["total_test_cases", "completed_test_cases", "error_test_cases", "skipped_test_cases"],
      "properties": {
        "total_test_cases": {"type": "integer", "minimum": 0},
        "completed_test_cases": {"type": "integer", "minimum": 0},
        "error_test_cases": {"type": "integer", "minimum": 0},
        "skipped_test_cases": {"type": "integer", "minimum": 0},
        "total_checks": {"type": "integer", "minimum": 0},
        "completed_checks": {"type": "integer", "minimum": 0},
        "error_checks": {"type": "integer", "minimum": 0},
        "skipped_checks": {"type": "integer", "minimum": 0}
      },
      "description": "Aggregate execution statistics across all test cases"
    },
    "results": {
      "type": "array",
      "items": {"$ref": "#/components/schemas/TestCaseResult"},
      "description": "Individual test case results"
    },
    "experiment": {
      "$ref": "#/components/schemas/ExperimentMetadata",
      "description": "Optional experiment metadata"
    },
    "metadata": {
      "type": "object",
      "additionalProperties": true,
      "description": "Optional implementation-specific metadata"
    }
  },
  "additionalProperties": false
}

```

##### Example (Protocol Compliance)

```
evaluation_id: "eval_001"
started_at: "2025-06-25T10:00:00Z"
completed_at: "2025-06-25T10:05:30Z"
status: "completed"
summary:
  total_test_cases: 100
  completed_test_cases: 100
  error_test_cases: 0
  skipped_test_cases: 0
results:
    status: "completed"
    execution_context: {...} 
    check_results: [# ... ]
    summary: {# ... }
  # ... more test case results

```

##### Example (Implementation Extension)

```
evaluation_id: "eval_001"
started_at: "2025-06-25T10:00:00Z"
completed_at: "2025-06-25T10:05:30Z"
status: "completed"
experiment:
  name: "geography_knowledge_test"
  metadata:
    dataset_version: "v1.2"
    model_version: "gpt-4-turbo"
summary:
  total_test_cases: 100
  completed_test_cases: 85
  error_test_cases: 10
  skipped_test_cases: 5
results: [# ... ]
metadata:
  total_cost_usd: 0.45
  execution_time_ms: 330000
  average_execution_time_ms: 3300
  total_tokens_used: 15000
  total_model_calls: 120
  parallelism: 4
```

---

# 5\. API Specification {#5.-api-specification}

## 5.1 REST API (OpenAPI 3.0) {#5.1-rest-api-(openapi-3.0)}

```
openapi: 3.0.3
info:
  title: Flexible Evaluation Protocol (FEP) API
  description: |
    The Flexible Evaluation Protocol (FEP) is a vendor-neutral, schema-driven standard for measuring the quality of any system that produces complex or variable outputs - whether they are deterministic APIs, non-deterministic large-language models, agentic workflows, or traditional software pipelines.
  version: 0.0.1
  contact:
    name: Shane Kercheval
  license:
    name: MIT

servers:
  - url: https://api.example.com/v1
    description: Production server
  - url: https://staging-api.example.com/v1
    description: Staging server

paths:
  /evaluate:
    post:
      summary: Run evaluation against test cases
      description: |
        Execute checks against test cases and their corresponding outputs. This is the core evaluation function that all FEP-compliant systems must implement.
      operationId: runEvaluation
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/EvaluationRequest'
      responses:
        '200':
          description: Evaluation completed successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EvaluationRunResult'
        '400':
          description: Invalid request format or validation errors
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: Internal server error during evaluation
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /evaluations/{evaluation_id}:
    get:
      summary: Retrieve evaluation results by ID
      description: Get the results of a previously run evaluation
      operationId: getEvaluation
      parameters:
        - name: evaluation_id
          in: path
          required: true
          schema:
            type: string
          description: Unique identifier for the evaluation run
      responses:
        '200':
          description: Evaluation results retrieved successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EvaluationRunResult'
        '404':
          description: Evaluation not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /health:
    get:
      summary: Health check endpoint
      description: Check if the FEP service is running and healthy
      operationId: healthCheck
      responses:
        '200':
          description: Service is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: "healthy"
                  version:
                    type: string
                    example: "0.0.1"

components:
  schemas:
    EvaluationRequest:
      type: object
      required:
        - test_cases
        - outputs
        - checks
      properties:
        test_cases:
          type: array
          items:
            $ref: '#/components/schemas/TestCase'
          description: Array of test cases to evaluate
        outputs:
          type: array
          items:
            $ref: '#/components/schemas/Output'
          description: Array of system outputs corresponding to test cases
        checks:
          oneOf:
            - type: array
              items:
                $ref: '#/components/schemas/Check'
              description: Array of checks to apply to all test cases
            - type: array
              items:
                type: array
                items:
                  $ref: '#/components/schemas/Check'
              description: Array of check arrays, where checks[i] applies to test_cases[i]
        experiment_metadata:
          $ref: '#/components/schemas/ExperimentMetadata'

    TestCase:
      type: object
      required:
        - id
        - input
      properties:
        id:
          type: string
          description: Unique identifier for the test case
        input:
          oneOf:
            - type: string
            - type: object
          description: The input provided to the system being evaluated
        expected:
          oneOf:
            - type: string
            - type: object
            - type: "null"
          description: Reference output for comparison or validation
        metadata:
          type: object
          description: Descriptive information about the test case
          additionalProperties: true

    Output:
      type: object
      required:
        - value
      properties:
        id:
          type: string
          description: Optional unique identifier for this output
        value:
          oneOf:
            - type: string
            - type: object
          description: The actual output from the system being evaluated
        metadata:
          type: object
          description: System-specific information about the output generation
          additionalProperties: true

    Check:
      type: object
      required:
        - type
        - arguments
      properties:
        type:
          type: string
          description: Identifier for the check implementation
          enum:
            - exact_match
            - contains
            - regex
            - threshold
        arguments:
          type: object
          description: Parameters passed to the check function - specific to each check type
          additionalProperties: true
        version:
          type: string
          pattern: '^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
          description: Semantic version of the check implementation

    ExperimentMetadata:
      type: object
      properties:
        name:
          type: string
          description: Human-readable experiment identifier
        metadata:
          type: object
          description: Additional experiment-specific information
          additionalProperties: true

    CheckResult:
      type: object
      required:
        - check_type
        - status
        - results
        - evaluated_at
        - metadata
      properties:
        check_type:
          type: string
          description: The type of check that was executed
        status:
          type: string
          enum: [completed, error, skip]
          description: Execution status of the check
        results:
          type: object
          description: Check outcome data. Structure depends on check type
          additionalProperties: true
        resolved_arguments:
          type: object
          description: |
            Arguments after JSONPath resolution. Each argument has a 'value' field containing the resolved value. 
            JSONPath expressions also include an optional 'jsonpath' field showing the original expression.
          additionalProperties: true
        evaluated_at:
          type: string
          format: date-time
          description: UTC timestamp when check was evaluated (ISO 8601)
        metadata:
          type: object
          properties:
            check_version:
              type: string
              description: Version of the check definition
          additionalProperties: true
          description: Optional dictionary with fields like check_version, execution_time_ms, and other check-specific metadata
        error:
          type: object
          required:
            - type
            - message
          properties:
            type:
              type: string
              enum: [jsonpath_error, validation_error, timeout_error, unknown_error]
              description: Category of error that occurred
            message:
              type: string
              description: Human-readable error description
            recoverable:
              type: boolean
              default: false
              description: Whether this error could be retried

    TestCaseResult:
      type: object
      required:
        - status
        - check_results
        - summary
      properties:
        status:
          type: string
          enum: [completed, error, skip]
          description: Computed overall status based on individual check result statuses
        execution_context:
          type: object
          required:
            - test_case
            - output
          properties:
            test_case:
              $ref: '#/components/schemas/TestCase'
              description: Complete test case that was evaluated
            output:
              $ref: '#/components/schemas/Output'
              description: Complete output that was evaluated
          description: Complete execution context - the test case and output that were evaluated together
        check_results:
          type: array
          items:
            $ref: '#/components/schemas/CheckResult'
          description: Array of individual check execution results
        summary:
          type: object
          required:
            - total_checks
            - completed_checks
            - error_checks
            - skipped_checks
          properties:
            total_checks:
              type: integer
              minimum: 0
            completed_checks:
              type: integer
              minimum: 0
            error_checks:
              type: integer
              minimum: 0
            skipped_checks:
              type: integer
              minimum: 0
        metadata:
          type: object
          description: Optional implementation-specific metadata
          additionalProperties: true

    EvaluationRunResult:
      type: object
      required:
        - evaluation_id
        - started_at
        - completed_at
        - status
        - summary
        - results
      properties:
        evaluation_id:
          type: string
          description: Unique identifier for this evaluation run
        started_at:
          type: string
          format: date-time
          description: When the evaluation started (ISO 8601)
        completed_at:
          type: string
          format: date-time
          description: When the evaluation completed (ISO 8601)
        status:
          type: string
          enum: [completed, error, skip]
          description: Overall evaluation execution status
        summary:
          type: object
          required:
            - total_test_cases
            - completed_test_cases
            - error_test_cases
            - skipped_test_cases
          properties:
            total_test_cases:
              type: integer
              minimum: 0
            completed_test_cases:
              type: integer
              minimum: 0
            error_test_cases:
              type: integer
              minimum: 0
            skipped_test_cases:
              type: integer
              minimum: 0
        results:
          type: array
          items:
            $ref: '#/components/schemas/TestCaseResult'
          description: Individual test case results
        experiment:
          $ref: '#/components/schemas/ExperimentMetadata'
          description: Optional experiment metadata
        metadata:
          type: object
          description: Optional implementation-specific metadata
          additionalProperties: true

    ErrorResponse:
      type: object
      required:
        - error
        - message
      properties:
        error:
          type: string
          description: Error type or code
        message:
          type: string
          description: Human-readable error message
        details:
          type: object
          description: Additional error details
          additionalProperties: true

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key

security:
  - BearerAuth: []
  - ApiKeyAuth: []
```

## 5.2 gRPC API (Protocol Buffers) {#5.2-grpc-api-(protocol-buffers)}

```
syntax = "proto3";

package fep.v1;

import "google/protobuf/struct.proto";
import "google/protobuf/timestamp.proto";
import "google/protobuf/any.proto";

option go_package = "github.com/example/fep/gen/go/fep/v1;fepv1";
option java_multiple_files = true;
option java_package = "com.example.fep.v1";
option csharp_namespace = "Fep.V1";

// ===== SERVICE DEFINITION =====

service EvaluationService {
  // Run evaluation against test cases and their corresponding outputs
  rpc RunEvaluation(EvaluationRequest) returns (EvaluationRunResult);
  
  // Retrieve evaluation results by ID
  rpc GetEvaluation(GetEvaluationRequest) returns (EvaluationRunResult);
  
  // Health check endpoint
  rpc HealthCheck(HealthCheckRequest) returns (HealthCheckResponse);
  
  // Stream evaluation results for long-running evaluations
  rpc StreamEvaluation(EvaluationRequest) returns (stream EvaluationProgress);
}

// ===== REQUEST/RESPONSE MESSAGES =====

message EvaluationRequest {
  repeated TestCase test_cases = 1;
  repeated Output outputs = 2;
  CheckConfiguration checks = 3;
  optional ExperimentMetadata experiment_metadata = 4;
}

message GetEvaluationRequest {
  string evaluation_id = 1;
}

message HealthCheckRequest {}

message HealthCheckResponse {
  string status = 1;
  string version = 2;
}

message EvaluationProgress {
  string evaluation_id = 1;
  string status = 2; // "running", "completed", "failed"
  int32 completed_test_cases = 3;
  int32 total_test_cases = 4;
  optional EvaluationRunResult final_result = 5; // Present when status is "completed"
}

// ===== CORE DATA STRUCTURES =====

message TestCase {
  string id = 1;
  InputValue input = 2;
  optional OutputValue expected = 3;
  optional google.protobuf.Struct metadata = 4;
}

message InputValue {
  oneof value {
    string string_value = 1;
    google.protobuf.Struct object_value = 2;
  }
}

message OutputValue {
  oneof value {
    string string_value = 1;
    google.protobuf.Struct object_value = 2;
  }
}

message Output {
  OutputValue value = 1;
  optional google.protobuf.Struct metadata = 2;
}

message CheckConfiguration {
  oneof configuration {
    SharedChecks shared_checks = 1;       // Same checks for all test cases
    PerTestCaseChecks per_test_case_checks = 2; // checks[i] applies to test_cases[i]
  }
}

message SharedChecks {
  repeated Check checks = 1;
}

message PerTestCaseChecks {
  repeated CheckList check_lists = 1;
}

message CheckList {
  repeated Check checks = 1;
}

message Check {
  string type = 1;
  google.protobuf.Struct arguments = 2;
  optional string version = 3;
}

message ExperimentMetadata {
  optional string name = 1;
  optional google.protobuf.Struct metadata = 2;
}

// ===== CHECK RESULT STRUCTURES =====

message CheckResult {
  string check_type = 1;
  CheckStatus status = 2;
  google.protobuf.Struct results = 3;
  optional google.protobuf.Struct resolved_arguments = 4;
  google.protobuf.Timestamp evaluated_at = 5;
  google.protobuf.Struct metadata = 6; // Optional dictionary with fields like check_version, execution_time_ms, etc.
  optional CheckError error = 7;
}

enum CheckStatus {
  CHECK_STATUS_UNSPECIFIED = 0;
  CHECK_STATUS_COMPLETED = 1;
  CHECK_STATUS_ERROR = 2;
  CHECK_STATUS_SKIP = 3;
}

// Note: metadata is now a flexible dictionary (google.protobuf.Struct) that can contain
// optional fields such as check_version, execution_time_ms, and other check-specific metadata

message CheckError {
  CheckErrorType type = 1;
  string message = 2;
  optional bool recoverable = 3;
}

enum CheckErrorType {
  CHECK_ERROR_TYPE_UNSPECIFIED = 0;
  CHECK_ERROR_TYPE_JSONPATH_ERROR = 1;
  CHECK_ERROR_TYPE_VALIDATION_ERROR = 2;
  CHECK_ERROR_TYPE_TIMEOUT_ERROR = 3;
  CHECK_ERROR_TYPE_UNKNOWN_ERROR = 4;
}

// ===== TEST CASE RESULT STRUCTURES =====

message ExecutionContext {
  TestCase test_case = 1;
  Output output = 2;
}

message TestCaseResult {
  TestCaseStatus status = 1;
  ExecutionContext execution_context = 2;
  repeated CheckResult check_results = 3;
  TestCaseSummary summary = 4;
  optional google.protobuf.Struct metadata = 5;
}

enum TestCaseStatus {
  TEST_CASE_STATUS_UNSPECIFIED = 0;
  TEST_CASE_STATUS_COMPLETED = 1;
  TEST_CASE_STATUS_ERROR = 2;
  TEST_CASE_STATUS_SKIP = 3;
}

message TestCaseSummary {
  int32 total_checks = 1;
  int32 completed_checks = 2;
  int32 error_checks = 3;
  int32 skipped_checks = 4;
}

// ===== EVALUATION RUN RESULT STRUCTURES =====

message EvaluationRunResult {
  string evaluation_id = 1;
  google.protobuf.Timestamp started_at = 2;
  google.protobuf.Timestamp completed_at = 3;
  EvaluationStatus status = 4;
  EvaluationSummary summary = 5;
  repeated TestCaseResult results = 6;
  optional ExperimentMetadata experiment = 7;
  optional google.protobuf.Struct metadata = 8;
}

enum EvaluationStatus {
  EVALUATION_STATUS_UNSPECIFIED = 0;
  EVALUATION_STATUS_COMPLETED = 1;
  EVALUATION_STATUS_ERROR = 2;
  EVALUATION_STATUS_SKIP = 3;
}

message EvaluationSummary {
  int32 total_test_cases = 1;
  int32 completed_test_cases = 2;
  int32 error_test_cases = 3;
  int32 skipped_test_cases = 4;
}

// ===== STANDARD CHECK TYPE DEFINITIONS =====

// Standard check arguments for type safety and validation
message ExactMatchArguments {
  CheckValue actual = 1;
  CheckValue expected = 2;
  optional bool negate = 3;
  optional bool case_sensitive = 4;
}

message ContainsArguments {
  CheckValue text = 1;
  repeated string phrases = 2;
  optional bool negate = 3;
  optional bool case_sensitive = 4;
}

message RegexArguments {
  CheckValue text = 1;
  string pattern = 2;
  optional bool negate = 3;
  optional RegexFlags flags = 4;
}

message RegexFlags {
  optional bool case_insensitive = 1;
  optional bool multiline = 2;
  optional bool dot_all = 3;
}

message ThresholdArguments {
  CheckValue value = 1;
  optional double min_value = 2;
  optional double max_value = 3;
  optional bool min_inclusive = 4;
  optional bool max_inclusive = 5;
  optional bool negate = 6;
}

message ThresholdConfig {
  optional double min_value = 1;
  optional double max_value = 2;
  optional bool min_inclusive = 3;
  optional bool max_inclusive = 4;
  optional bool negate = 5;
}

// Flexible value type for check arguments (literal or JSONPath)
message CheckValue {
  oneof value {
    string literal_string = 1;
    double literal_number = 2;
    bool literal_bool = 3;
    google.protobuf.Struct literal_object = 4;
    string jsonpath_expression = 5;
  }
}

// ===== STANDARD CHECK RESULT DEFINITIONS =====

message ExactMatchResult {
  bool passed = 1;
}

message ContainsResult {
  bool passed = 1;
}

message RegexResult {
  bool passed = 1;
}

message ThresholdResult {
  bool passed = 1;
}

// ===== ERROR HANDLING =====

message FepError {
  string code = 1;
  string message = 2;
  optional google.protobuf.Struct details = 3;
}

// ===== BATCH OPERATIONS =====

message BatchEvaluationRequest {
  repeated EvaluationRequest evaluations = 1;
  optional BatchOptions options = 2;
}

message BatchOptions {
  optional int32 max_concurrent = 1;
  optional int64 timeout_ms = 2;
  optional bool fail_fast = 3;
}

message BatchEvaluationResponse {
  repeated EvaluationRunResult results = 1;
  repeated FepError errors = 2;
  BatchSummary summary = 3;
}

message BatchSummary {
  int32 total_evaluations = 1;
  int32 successful_evaluations = 2;
  int32 failed_evaluations = 3;
  google.protobuf.Timestamp started_at = 4;
  google.protobuf.Timestamp completed_at = 5;
}

// ===== ASYNC OPERATIONS =====

service AsyncEvaluationService {
  // Start a long-running evaluation
  rpc StartEvaluation(EvaluationRequest) returns (EvaluationOperation);
  
  // Get operation status
  rpc GetOperation(GetOperationRequest) returns (EvaluationOperation);
  
  // List operations
  rpc ListOperations(ListOperationsRequest) returns (ListOperationsResponse);
  
  // Cancel operation
  rpc CancelOperation(CancelOperationRequest) returns (CancelOperationResponse);
}

message EvaluationOperation {
  string operation_id = 1;
  string status = 2; // "pending", "running", "completed", "failed", "cancelled"
  google.protobuf.Timestamp created_at = 3;
  optional google.protobuf.Timestamp started_at = 4;
  optional google.protobuf.Timestamp completed_at = 5;
  optional EvaluationProgress progress = 6;
  optional EvaluationRunResult result = 7;
  optional FepError error = 8;
  optional google.protobuf.Struct metadata = 9;
}

message GetOperationRequest {
  string operation_id = 1;
}

message ListOperationsRequest {
  optional string filter = 1;
  optional int32 page_size = 2;
  optional string page_token = 3;
}

message ListOperationsResponse {
  repeated EvaluationOperation operations = 1;
  optional string next_page_token = 2;
}

message CancelOperationRequest {
  string operation_id = 1;
}

message CancelOperationResponse {
  bool cancelled = 1;
}
```

---

# 6\. Implementation Requirements {#6.-implementation-requirements}

## 6.1 Compliance Levels {#6.1-compliance-levels}

### Level 1 \- Basic Compliance {#level-1---basic-compliance}

* Support Test Case Format with required fields (Section 2.1.1)  
* Support Test Case Checks format (Section 2.4)  
* Support both shared and per-test-case check patterns (Section 3.1)  
* Return results in specified format (Section 4\)  
* Support basic JSONPath evaluation for check arguments

### Level 2 \- Full Compliance {#level-2---full-compliance}

* Implement either REST or gRPC API (Section 5\)  
* Support parallel execution and error handling  
* Handle mixed check result types  
* Full JSONPath support for complex path expressions  
* Implement standard check types from Section 2.3.5

### Level 3 \- Extended Compliance {#level-3---extended-compliance}

* Support both REST and gRPC APIs  
* Implement custom check extension mechanism  
* Support real-time evaluation streaming  
* Advanced JSONPath features and optimization  
* Implement all standard check types from Section 2.3.5

## 6.2 JSONPath Implementation Notes {#6.2-jsonpath-implementation-notes}

* Implementations should support standard JSONPath syntax as defined by [RFC 9535](https://tools.ietf.org/rfc/rfc9535.txt)  
* String arguments beginning with `$.` should be interpreted as JSONPath expressions  
* String arguments beginning with `\\$.` should be treated as literal strings starting with `$.` (escape syntax)  
* When JSONPath expressions cannot be evaluated, checks should return status "error" with appropriate error message  
* Implementations may cache JSONPath compilation for performance

## 6.3 Versioning and Compatibility {#6.3-versioning-and-compatibility}

All protocol components must use semantic versioning. Breaking changes require major version increments. Implementations should support backward compatibility within major versions.

## 6.4 Security Considerations {#6.4-security-considerations}

* Authenticate API access using standard methods (API keys, OAuth2)  
* Validate all input data to prevent injection attacks  
* Sanitize JSONPath expressions to prevent potential security issues  
* Encrypt sensitive evaluation data in transit and at rest  
* Implement audit logging for compliance requirements

---

# 7\. References {#7.-references}

* [JSONPath RFC 9535](https://tools.ietf.org/rfc/rfc9535.txt)  
* [OpenAPI Specification](https://swagger.io/specification/)  
* [Protocol Buffers Language Guide](https://developers.google.com/protocol-buffers/docs/proto3)  
* [JSON Schema Specification](https://json-schema.org/)  
* [Semantic Versioning](https://semver.org/)
