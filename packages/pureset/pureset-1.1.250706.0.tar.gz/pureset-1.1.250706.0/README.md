
<p align="center">
<img src="https://raw.githubusercontent.com/gabrielmsilva00/pureset/e920683cd8f19ac740eb1f06cc4df1a30a5fe5d1/img/PureSet.svg"><br/>
<a href="https://python.org/downloads"><img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python Version" width=256 style="vertical-align:middle;margin:5px"><br/>
<a href="https://www.apache.org/licenses/LICENSE-2.0.txt"><img src="https://img.shields.io/badge/License-Apache%202.0-green.svg" alt="License" width=256 style="vertical-align:middle;margin:5px"><br/>
<a href="https://github.com/gabrielmsilva00/pureset"><img src="https://img.shields.io/badge/GitHub-Repository-2A3746?logo=github" width=256 style="vertical-align:middle;margin:5px"><br/>
<a href="https://pypi.org/project/pureset"><img src="https://img.shields.io/pypi/v/pureset.svg?logo=pypi" alt="Version" width=256 style="vertical-align:middle;margin:5px"><br/>
</p>
<p align="center">
<h1 align="center">PureSet</h1>
<h6 align="center">For general Python development matters, being this package or any, contact me at<br/><a href="mailto:gabrielmaia.silva00@gmail.com">gabrielmaia.silva00@gmail.com<a/><h6>
</p>


---

#### PureSet is an immutable, ordered, and hashable collection type for Python.

It ensures **type homogeneity** across elements, making it a robust **replacement for both sets and sequences** in production applications.

**PureSet** offers _accuracy, predictability_, and _clarity_ in managing **homogeneous data structures**.

###### v1.1 NOTE: Now with Numpy and Pandas data type support (see below)! Check changelog (TBA) for details.

---

## **Core Features**

- **Immutability:** Elements cannot be changed after creation; assures data integrity and reproducibility.
- **Ordering:** Retains insertion sequence—predictable for iteration, exporting, or display use cases.
- **Hashability:** Collections of hashable (and even nested) objects are themselves hashable; can be dictionary keys.
- **Uniqueness:** Removes duplicates according to standard Python object equality.
- **Deep Type & Schema Homogeneity:** Strict enforcement that all elements are of the same type and "shape" (for nested dicts, arrays, pandas or custom classes: attributes/properties and value types are all enforced).
- **Performance:** Optimized for high efficiency in membership, intersection, union, and set-like operations—even with very large sets.
- **Signature Inspection:** `.signature` property represents the canonical type/structure of the set’s contents, for debugging, documentation, and dynamic runtime/schema checks.
- **Universal Container:** Works seamlessly with primitives, tuples, dicts, custom classes, numpy arrays, pandas DataFrames/Series, UserString/UserList/etc., and even many mixed nested containers.
- **Extensible:** Transparent support for new types via the "freeze/restore" protocol.
- **Serialization Ready:** Supports pickling, as well as custom freeze/restore for efficient export/import (including cross-version/cross-platform).
- **Advanced API:** Full set operations (`|`, `&`, `-`, `^`), mapping/filtering, slices, composition, custom schema validation patterns, and more.

---

## **Installation & Requirements**

To install the latest `PureSet` package, use pip:

```bash
pip install -U pureset
```

- **Python Versions:** Compatible with Python 3.9 and above.
- **Dependencies:** Pure Python, no required dependencies. Numpy|Pandas are *optional* for enhanced functionality.

---

## **Usage & API Overview**

This section presents realistic, production-focused examples that go well beyond simple unique containers.

---

### **Basic Example Usage**

```pycon
>>> from pureset import PureSet

>>> PureSet(1, 2, 3)
PureSet(1, 2, 3)

>>> PureSet(1, 2, 2, 3)
PureSet(1, 2, 3)

>>> PureSet("a", "b", "b")
PureSet('a', 'b')

>>> len(PureSet(8, 8, 9))
2
```

---

### **Robust Enum Replacement | State Management**

Type-safe, ordered, and immutable replacement for sets of valid states/options.

```pycon
>>> ORDER_STATES = PureSet("Pending", "Processing", "Shipped", "Delivered", "Cancelled")
>>> "Processing" in ORDER_STATES
True
>>> "Returned" in ORDER_STATES
False
>>> print(ORDER_STATES)
PureSet('Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled')
```

---

### **Contracts & API Schema Checking**

PureSet as a runtime type-and-shape schema enforcer.

```pycon
>>> user_profiles = PureSet(
...     {"id": 1, "name": "Alice Smith", "age": 28, "email": "alice@example.com"},
...     {"id": 2, "name": "Bob Johnson", "age": 35, "email": "bob@example.com"},
... )
>>> user_profiles.signature
(<class 'dict'>, {'age': <class 'int'>, 'email': <class 'str'>, 'id': <class 'int'>, 'name': <class 'str'>})

>>> # Mismatched schema!
>>> PureSet(
...     {"id": 1, "name": "Alice", "age": 28, "email": "alice@a.com"},
...     {"id": 2, "name": "Bob", "years_old": 35}           # will fail!
... )
Traceback (most recent call last):
    ...
TypeError: Incompatible element type or shape at position 2:
Exp: (<class 'dict'>, {'age': <class 'int'>, 'email': <class 'str'>, 'id': <class 'int'>, 'name': <class 'str'>});
Got: (<class 'dict'>, {'id': <class 'int'>, 'name': <class 'str'>, 'years_old': <class 'int'>})
```

---

### **Validated Nested Data for ML|DL Pipelines**

Reliable, transparent structure-checking for data with deep/complex layout.

```pycon
>>> batch = PureSet(
...   ([1.4, 2.8, 3.1], 'class_a'),
...   ([0.9, 2.2, 3.5], 'class_b'),
... )
>>> batch.signature
(<class 'tuple'>, ((<class 'list'>, (<class 'float'>, 3)), <class 'str'>))
```

---

### **Deduplication and Set Algebra**

Entries are always unique, preserving original order.

```pycon
>>> a = PureSet(1, 2, 3)
>>> b = PureSet(3, 4, 2)
>>> (a | b).to_list()
[1, 2, 3, 4]
>>> (a & b).to_list()
[2, 3]
>>> (a - b).to_list()
[1]
>>> (a ^ b).to_list()
[1, 4]
```

---

### **Using PureSet with Numpy and Pandas**

```pycon
>>> import numpy as np, pandas as pd
>>> arr = np.array([1, 2, 3])
>>> ps = PureSet(arr)
>>> ps[0].shape
(3,)

>>> df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
>>> PureSet(df)[0].equals(df)
True
>>> idx = pd.Index([5, 7, 9])
>>> PureSet(idx)[0].equals(idx)
True
```
Mixing non-matching types (ndarray with list/tuple, DataFrame with list) will raise a `TypeError`.

---

### **Complex Custom Objects, NamedTuples, UserList, UserDict**

```pycon
>>> from collections import namedtuple, UserList, UserDict
>>> Pt = namedtuple("Pt", "x y")
>>> PureSet(Pt(2,3), Pt(3,4))[1]
Pt(x=3, y=4)
>>> ul = UserList([1,2,3])
>>> PureSet(ul)[0]
[1, 2, 3]
>>> ud = UserDict({'foo': 99})
>>> PureSet(ud)[0]
{'foo': 99}
```

---

### **Freeze/Restore: Reliable, Deep Immutability and Serialization**

```pycon
>>> x = [{'a': [1, 2]}, {'a': [3, 4]}]
>>> frozen = PureSet.freeze(x)
>>> PureSet.restore(frozen)
[{'a': [1, 2]}, {'a': [3, 4]}]
```

---

## **Advanced Features and Extensibility**

- **Rich Set Algebra:** `|`, `&`, `-`, `^` ops (union, intersection, difference, symmetric difference).
- **Slicing and Indexing:** Supports all Pythonic sequence semantics, including negative and slice indexing.
- **Compatibility Checking:** `.compatible(other)` method ensures two sets are structurally equivalent before combining/operating.
- **Signature Inspection:** `.signature` provides a Python-type-based schema, invaluable for API contracts, docs, and dynamic validation.
- **Freeze/Restore API:** PureSet can be losslessly frozen to a hashable representation, and restored—even across Python versions.
- **Protocol for New Types:** Pluggable mechanism for custom freeze/restore for advanced user classes, numpy, pandas, and beyond.
- **Mixes with UserString, Counter, ChainMap, deque, array.array, memoryview, and more (see full list in docs/tests).**

---

## **Performance and Scalability**

- **Highly optimized** for large scale: construction, lookup, and set algebra achieve competitive performance even for sets of tens of millions of elements.
- **Performance gap** to built-in set is logarithmically bounded (see docs for latest benchmarks).
- PureSet’s internal caching and O(1) hash-based fast paths guarantee speed for all practical workloads.

---

## **Testing**

##### v1.1.250706.0: 56 tests; 0 Failures; 0 Errors

The current testing suite is only available through the GitHub repository.

You can check its code [here](https://github.com/gabrielmsilva00/pureset/blob/main/tests/unittest_pureset.py).

- Full test suite includes:
  - Edge cases for numpy, pandas, UserDict/UserList/UserString, Counter, deque, ChainMap
  - Deeply nested and empty structures, custom and standard containers
  - Type and schema enforcement for real-world mixed and homogeneous datasets
  - Serialization and "restoration" safety

---

## **License**

This project is released under the **Apache License 2.0**. Please review the [LICENSE](LICENSE) file for further details.

---

> **PureSet is engineered to give your Python code safety, consistency, integrity and high power for production-scale scenarios across APIs, analytics, ML, and beyond!**