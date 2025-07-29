![PureSet](./img/PureSet.svg)
# **PureSet**
![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)
![Version](https://img.shields.io/badge/Version-1.0.250704.0-brightgreen.svg)

**PureSet** is an immutable, ordered, and hashable collection type for Python.
It ensures **type homogeneity** across elements, making it a robust replacement for both sets and sequences in production applications.
**PureSet** offers accuracy, predictability, and clarity in managing homogeneous data structures.

---

## **Core Features**
- **Immutability:** Elements cannot be changed after creation; assures data integrity.
- **Ordering:** Retains insertion sequence, making it predictable for iteration, exporting, or display use cases.
- **Hashability:** Collections of hashable objects are themselves hashable; can be used as dictionary keys.
- **Uniqueness:** Removes duplicates according to standard Python object equality.
- **Type and Schema Homogeneity:** Strict enforcement that all elements are of not only the same type, but also of the same shape (for dicts and custom objects—by attribute/property names and types).
- **Performance:** Optimized for high efficiency in membership, intersection, union, and set-like operations.
- **Signature Inspection:** Provides a `.signature` property representing the canonical type/structure of the set’s contents, critical for debugging, API contracts, and documentation.
- **Universal Container:** Works seamlessly with primitives, tuples, dicts, custom classes, and even mixed nested containers.
---

## **Installation & Requirements**
To install the `PureSet` package, simply use pip:
```bash
pip install pureset
```
*   **Python Versions**: Compatible with Python 3.9 and above.
*   **Dependencies**: Pure Python, with no external dependencies.
---

## **API Overview**
This section presents expanded, realistic examples of `PureSet` in production-grade scenarios, demonstrating its capabilities beyond simple collections.

### **Real-World Usability**
- **Contracts in APIs:** Require or emit only valid structures to callers; enforce contract at runtime.
- **Data Pipelines (ETL):** Guarantee all records are clean, normalized, and of valid shape before aggregation or transformation.
- **State Machines:** Prevent illegal state transitions by checking membership in a `PureSet` of allowed values.
- **Unique Entity Sets:** Model deduplicated entities (users, objects, configurations) with order preserved and structure enforced.
- **Distributed Computing:** Share, serialize, or hash-combine validated and immutable data blocks across processes or systems.

**PureSet’s** `.signature` is especially useful for audits, logging, debugging mismatches, and can be serialized for external schema verification.

```python
from pureset import PureSet
```

### **1. Robust Enum Replacement and State Management**
`PureSet` provides a type-safe, ordered, and immutable alternative for defining a finite set of states or options, offering clear advantages over traditional string literals or basic tuples. It's particularly useful for defining state machine transitions or valid configuration options.

```python
# Define a set of valid order states for an e-commerce system
# The order guarantees a predictable sequence for UI display or reporting.
ORDER_STATES = PureSet("Pending", "Processing", "Shipped", "Delivered", "Cancelled")

def process_order_status_update(order_id: str, new_status: str) -> None:
    if new_status not in ORDER_STATES:
        raise ValueError(
            f"Invalid order status '{new_status}' for order {order_id}.\n"
            f"Allowed states are: [{ORDER_STATES.join(' | ')}]"
        )

    # In a real system, this would interact with a database or external service
    print(f"Order {order_id}: Status updated to '{new_status}'.")


# Simulate a valid status update
process_order_status_update("ORD12345", "Shipped")

# Simulate an invalid status update
try:
    process_order_status_update("ORD12346", "Returned")
except ValueError as e:
    print(e)
    # Invalid order status 'Returned' for order ORD12346. 
    # Allowed states are: [Pending | Processing | Shipped | Delivered | Cancelled]
```

### **2. Validating Homogeneity and Schema Consistency for Complex Data Structures**
When dealing with collections of dictionaries or custom objects in data processing pipelines or API interactions, ensuring all elements conform to a specific schema is paramount. `PureSet` enforces not just type homogeneity but also structural consistency, raising errors for schema mismatches.
**NOTE:** `PureSet` always refers to the first element as a **validator** of all other elements given afterwards. You can always check the validator schema by using the `.signature` property.

```python
# Define a PureSet of user profiles, each represented by a dictionary.
# PureSet ensures all dictionaries have the same keys and value types.
user_profiles = PureSet(
    {"id": 1, "name": "Alice Smith", "age": 28, "email": "alice@example.com"},
    {"id": 2, "name": "Bob Johnson", "age": 35, "email": "bob@example.com"},
)

# Attempt to add a profile with a mismatched schema (e.g., missing 'email' or different key)
try:
    mismatched_profiles = PureSet(
        {"id": 3, "name": "Charlie Brown", "age": 42, "email": "charlie@example.com"},
        {"id": 4, "name": "Diana Prince", "years_old": 30},  # Schema mismatch
    )
except TypeError as e:
    print(e)
    # Incompatible element type or shape at position 2:
    # Exp: (<class 'dict'>, {'age': <class 'int'>, 'email': <class 'str'>, 'id': <class 'int'>, 'name': <class 'str'>});
    # Got: (<class 'dict'>, {'id': <class 'int'>, 'name': <class 'str'>, 'years_old': <class 'int'>})


# Example with nested tuples: PureSet enforces consistency for tuples with consistent internal types.
data_points = PureSet((1, "x_coord", 10.5), (2, "y_coord", 20.3))

# Attempt to create a PureSet with inconsistent tuple element types
try:
    invalid_data_points = PureSet(
        (1, "x_coord", 10.5),
        (2, "y_coord", "invalid_value"),  # Type mismatch within tuple
    )
except TypeError as e:
    print(e)
    # Incompatible element type or shape at position 2:
    # Exp: (<class 'tuple'>, (<class 'int'>, <class 'str'>, <class 'float'>));
    # Got: (<class 'tuple'>, (<class 'int'>, <class 'str'>, <class 'str'>))
```

### **6. Layer Validation in ML/DL Model Pipelines or Validation of Nested Containers**
Handling sequences, matrix input, or data layer validation:

```python
batch = PureSet(
    ([1.4, 2.8, 3.1], 'class_a'),
    ([0.9, 2.2, 3.5], 'class_b'),
)
print(batch.signature)
# Output: (tuple, ([float, float, float], str))
```

---

## **Testing**

---

## **License**
This project is released under the **Apache License 2.0**. Please review the [LICENSE](LICENSE) file for further details.

---

PureSet is engineered to give your Python data code the safety, transparency, and power required for production-scale scenarios—across API, analytics, ML, and system development!