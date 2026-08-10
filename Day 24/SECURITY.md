# Day 24 Security Documentation

## Input Validation

The FastAPI API uses strict Pydantic validation to validate user input before it reaches the machine learning model.

The API validates:

- Data types
- Required fields
- Numeric ranges
- String length
- Regex patterns
- Unexpected fields

Invalid requests are rejected with HTTP 422 responses.

## Out-of-Distribution Detection

The API uses statistical OOD detection to identify abnormal numerical inputs.

The z-score is calculated using:

z = |x - mean| / standard deviation

A z-score greater than 3 is treated as an unusual input.

OOD detection is applied to numerical prediction inputs such as Age, Quantity, and Price_per_Unit.

When an abnormal value is detected, the API returns HTTP 400:

{
  "detail": "Data Out of Bounds: OOD input detected."
}

OOD detection helps prevent unusual values from being passed to the machine learning model.

## Why Z-Score is Used

Z-score measures how far a value is from the mean in terms of standard deviations.

A small z-score represents a value close to the expected distribution.

A large z-score indicates that the value may be unusual or abnormal.

Therefore, z-score can be used as a simple statistical guardrail for detecting unexpected inputs.

## Pydantic Security

Pydantic protects the API by validating incoming requests before model inference.

The API rejects:

- Invalid data types
- Negative values outside allowed ranges
- Extremely large values
- Missing required fields
- Invalid text patterns
- Unexpected fields

This prevents malformed data from reaching the machine learning model.

## Prompt Injection Protection

Prompt injection is an attack where an attacker attempts to manipulate an AI system by providing instructions designed to override its intended behavior.

Examples include attempts to:

- Ignore previous instructions
- Reveal system instructions
- Bypass security rules
- Manipulate application behavior

This API applies strict input validation, field length limits, regex constraints, and suspicious input checks before processing user data.

These controls help reduce the risk of suspicious text being accepted as trusted input.

## Security Testing

The API was tested using:

- SQL injection-style input
- Script injection attempts
- Prompt injection attempts
- Negative numerical values
- Extremely large numerical values
- Invalid data types
- Missing fields
- Unexpected fields
- Out-of-Distribution values

The tested invalid requests returned controlled HTTP 400 or HTTP 422 responses.

No unhandled HTTP 500 error was observed during the performed security tests.

## Secure Processing Flow

Client Request

↓

Pydantic Validation

↓

Security Checks

↓

OOD Detection

↓

Validated Input

↓

Machine Learning Model

↓

Prediction Response

## Conclusion

The security improvements implemented in Day 24 help protect the FastAPI machine learning API from malformed, suspicious, and abnormal inputs.

Input validation ensures that only valid data reaches the model, while OOD detection provides an additional statistical safety layer.
## Key Concepts

### How Pydantic Field Validation Works

Pydantic validates incoming API data before it reaches the machine learning model. It checks data types, numeric ranges, string lengths, regex patterns, required fields, and unexpected fields.

For example, an invalid Age value such as -10 is rejected with HTTP 422 instead of being passed to the model.

### How OOD Detection Identifies Abnormal Data

Out-of-Distribution detection checks whether incoming numerical values are significantly different from the expected data distribution.

The API uses statistical checks such as z-score to identify unusual values. Abnormal inputs are rejected with HTTP 400 before reaching the machine learning model.

### Why Z-Score Detects Unusual Values

Z-score measures how far a value is from the mean in terms of standard deviations.

z = |x - mean| / standard deviation

A larger z-score indicates that a value is farther from the expected distribution. A commonly used threshold is 3 for identifying potential outliers.

### How Prompt Injection Attacks Affect AI Systems

Prompt injection attacks attempt to manipulate an AI system by providing instructions that conflict with its intended behavior.

Examples include attempts to ignore previous instructions, reveal system instructions, or bypass security controls.

Input validation and security checks help prevent suspicious or malformed input from being accepted by the application.

### How Secure Input Validation Improves API Reliability

Secure input validation ensures that only expected and valid data reaches the machine learning model.

It helps prevent malformed payloads, reduce unexpected model behavior, reject suspicious requests, and return controlled HTTP 400 or HTTP 422 responses instead of allowing invalid data to cause unexpected failures.