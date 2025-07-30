# **NullPlus**

[![PyPI version](https://badge.fury.io/py/nullplus.svg)](https://pypi.org/project/NullPlus/)

A lightweight, robust implementation of the Null Object pattern that silently absorbs **all operations** while optionally carrying diagnostic data, plus an `Unset` class for differentiating between explicit None values and unset states.

```python
# Instead of:
result = None
if result is None: 
    handle_error()

# Simply:
result = Null()
result.anything().you.want()  # No crashes, no fuss

# Differentiate unset vs explicit None:
config_value = Unset() if missing else value
```

---

## **Key Features**

### **Universal Operation Absorption (Null)**

* Attribute access (`obj.anything`) → returns `self`
* Method calls (`obj.method(arg)`) → returns `self`
* Mathematical operations (`obj + 10`) → returns `self`
* Item access (`obj["key"]`) → returns `self`
* Iteration (`for x in obj`) → empty iterator
* Context managers (`with obj:`) → no-op
* Boolean context (`if obj:`) → always `False`

### **Unset Sentinel Value**

* Explicitly represents **unset/undefined** states
* Differentiates between explicit `None` and missing values
* Safe equality checks: `Unset() == Unset()` → `True`
* Distinct from all other values including `None` and `Null`

### **Easy Detection & Intentional Usage**

```python
if isinstance(result, Null):  # Explicit error check
    log_errors(result.data)   # Access stored diagnostics

if value is Unset():          # Detect unset state
    load_default_config()
```

### **Diagnostic Data Carrier (Null)**

```python
n = Null("Error: File not found", debug_id=42)
print(n)  # <Null: ("Error: File not found", {'debug_id': 42})>
```

### **Type-Safe Behavior (Null)**

* `len(Null())` → `0`
* `int(Null())` → `-1`
* `float(Null())` → `nan`
* `list(Null())` → `[]`

### **Asynchronous Support (Null)**

```python
async with Null() as n:
    await n.some_operation()  # No errors

async for x in Null():
    print("Never runs")
```

---

## **Installation**

```bash
pip install NullPlus
```

---

## **Usage Guide**

### **Basic Error Handling (Null)**

```python
from NullPlus import Null

def safe_parser(data):
    try:
        return complex_operation(data)
    except Exception as e:
        return Null(e, original_data=data)

result = safe_parser(invalid_input)
print(result.anything)  # <Null: (ValueError('...'), {...})>
```

### **Unset Value Detection**

```python
from NullPlus import Unset

def process_config(config=Unset()):
    if config is Unset():
        print("Using default configuration")
        config = load_defaults()
    elif config is None:
        print("Explicitly disabled configuration")
    
    # Normal processing...
```

### **API Response Handling (Null)**

```python
def fetch_user_data():
    try:
        return api.get("/user")
    except ConnectionError as e:
        return Null(e, status_code=503)

data = fetch_user_data()
for item in data.get('items', Null()):
    # Safely handles either real data or Null
    process(item)
```

### **Mathematical Resilience (Null)**

```python
def calculate_metrics():
    return Null("Metrics unavailable") if error else real_metrics

result = calculate_metrics() * 10 / 5
print(result)  # <Null: 'Metrics unavailable'>
```

### **Advanced Diagnostics (Null)**

```python
error_state = Null(
    "Database connection failed",
    error_code=502,
    timestamp=datetime.now(),
    query_params=request.params
)

# Preserves complex diagnostic data
your_log_function(error_state.data)
```

---

## **Technical Highlights**

### **Truthiness & Equality**

```python
# Null behavior
bool(Null())  # False
Null() == Null("different data")  # True
Null() == None  # False

# Unset behavior
Unset() == Unset()  # True
Unset() == None     # False
Unset() == Null()   # False
bool(Unset())       # True (normal object truthiness)
```

### **Operation Absorption Matrix (Null)**

| Operation        | Example               | Result   |
| ---------------- | --------------------- | -------- |
| Attribute access | `Null().missing_attr` | `<Null>` |
| Method call      | `Null()()`            | `<Null>` |
| Item access      | `Null()['key']`       | `<Null>` |
| Arithmetic       | `Null() + 10`         | `<Null>` |
| Iteration        | `list(Null())`        | `[]`     |
| Context manager  | `with Null(): ...`    | No-op    |
| Async operations | `await Null()`        | `<Null>` |

### **Unset Key Properties**
| Property          | Description |
|-------------------|-------------|
| Operation Safety | **Not** operation-absorbing (normal attribute rules apply) |
| Primary Use Case | Sentinel value for missing/undefined state |
| Distinct From    | `None`, `Null()`, empty containers, and falsey values |
| Serialization    | Represents as `<Unset Value>` |

---

## **Why Choose NullPlus?**

1. **Clear State Differentiation**
   - `Null` for controlled error absorption
   - `Unset` for detecting unconfigured/missing values
   - Both distinct from `None`

2. **Eliminate Expensive Mistakes**
   Avoid `AttributeError`, `TypeError`, and `NoneType` crashes with `Null`

3. **Debugging-Friendly**
   Preserve error context without disrupting control flow (`Null`)
   Explicit state tracking (`Unset`)

4. **Context-Aware (Null)**
   Works in sync/async contexts, math operations, and iterations

5. **Semantic API**
   Clearly signals intentional states in your codebase

6. **Zero Dependencies**
   Pure Python implementation