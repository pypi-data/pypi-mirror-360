# 📦 Stash - Memory Optimisation Class-Decorator

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![PyPI - 0.1.0](https://img.shields.io/badge/PyPI-coming--soon-yellow)](https://pypi.org/)

---

## What is Stash?

Stash is a '__slots__'-based Python class-decorator developed to assist Python developers in 
significantly reducing memory overhead when initiating individual classes. It dynamically creates a new optimised class with necessary dunder-methods behind the scene (__init__, __repr__, __eq__), and also adds user-specified methods to ensure custom functionality. The application also supports immutability through 'Freeze' parameter, disabling user's ability to set attribute values post-initialisation for better memory efficiency.

## ❓ Why use Stash?

Python's default class instances store attributes in a `__dict__`, which provides general flexibility but at the cost of significant memory overhead - Especially when constructing large numbers of objects. Stash helps to eliminate this fact by replacing this traditional memory storage with `__slots__` resulting in:

* ⚡ **Lower Memory Usage**: Substantially reduces per-instance memory overhead.
* 🚀 **Faster Attribute Access**: Slots-based storage supports faster lookup than ordinary `__dict__`.
* 🔐 **Optional Immutability**: Prevents unintended mutations by freezing attributes post-init.
* 🧼 **Clean API**: Less boilerplate code as `Stash` automatically generates `__init__`, `__repr__`, `__eq__`.
* 🧩 **Selective Method Preservation**: Use `@conserve` to explicitly preserve methods - only keep what's essential.
* 🧠 **Better for Large Datasets**: Ideal for performance-critical application like data science, simulations, and high-volume APIs.

**Stash is designed to help you write lean, efficient and Pythonic code**

## 📋 Key Features
* 🎁 Simple-to-use Python class decorator for memory optimisation.
* 🛠️ Dynamically creates __slots__-based classes to minimize memory overhead.
* ⚗️ Adds essential dunder methods (__init__, __repr__, __eq__).
* 🔄 Allows user to specify class-methods to preserve and inherit.
* ❄️ Supports attribute Freeze-functionality (_frozen) for increased memory efficiency.
* 📊 Retains original class metadata for analysis, debugging and introspection.

---

## 🧠 Installation

Install Stash using your preferred Package Manager.
```bash
pip install stash-memory
# or
poetry add stash-memory
# or
conda install stash-memory
```

## #️⃣ Quickstart Example

```python
from Stash import Stash

@Stash
class Example:
    name: str
    age: int
    is_single: bool

example1 = Example(
    name="Tony Stark",
    age=34,
    is_single=False
)

print(example1.name)        # Tony Stark
print(example1.age)         # 34
print(example1.is_single)   # False
```
*NOTE*: An `__init__` method is automatically created similarly to `@dataclass`

## 🧊 Freeze mechanic

Stash also supports immutability by disabling modifications to instance attributes after initialization. By setting `freeze=True`, individual instances become read-only. Any attempts to modify or change attributes raises an `AttributeError`.

```python
from Stash import Stash

@Stash(freeze=True)
class Example:
    name: str
    age: int
    is_villain: bool

example1 = Example(
    name="Otto Octavius",
    age=52, 
    is_villain=True
)

example1.name = "Norman Osborn"     # Raises an AttributeError, as values are immutable.
```

## 🔒 Preserve Methods

Utilise the `@conserve` decorator to explicitly mark methods for preservation in the new __slots__-based class. Individual methods NOT marked will not be present in new class.

```python
from Stash import Stash, conserve

@Stash
class Example:
    name: str
    age: int
    is_superhero: bool

    # Method is preserved
    @conserve
    def smash(self):
        print(f"{self.name} SMASH!")

    # Method is NOT preserved, due to lack of @conserve-decorator
    def surrender(self):     
        print(f"{self.name} surrenders!")

example1 = Example(
    name="Bruce Banner",
    age=39,
    is_superhero=True
)

example1.smash()                # Successfully runs and prints message.

try:                            # Raises AttributeError: Instance has no atribute 'surrender'
    example1.surrender()
except AttributeError as e:
    print(f"Method missing {e}")
```

---

## 📈 Benchmark Results

To validate Stash's memory optimisation, I performed a benchmark test utilising a `@Stash` decorated class against a standard Python class using `tracemalloc`.

### 🧪 Test Setup
* **Test**: Instantiating 10,000 objects with 3 attributes.
* **Compared**:
    * ✅ `RegularClass` - Traditional class utilising `__dict__` for attribute storage.
    * ✅ `StashClass` - Optimised class using `@Stash`
* **Tool**: `tracemalloc`, `sys.getsizeof`, `pympler.asizeof` for memory tracking.

### 💡 Results Summary

| **Measurement**                       | **RegularClass** | **StashClass** | **Notes**                                                 |
|---------------------------------------|------------------|----------------|-----------------------------------------------------------|
| Total memory used (Tracemalloc)       | 1.5 MiB          | 1.5 MiB        | Snapshot difference for 10,000 instances                  |
| Avg. memory per instance              | 154 B            | 155 B          | Similar values, but granularity might affect final result |
| Shallow object size (`sys.getsizeof`) | 48 B             | 65 B           | Memory size of instance container only                    |
| Deep object size (`pympler.asizeof`)  | 360 B            | 168 B          | Includes all attributes: Stash saves >50% memory          |

## ⚙️ Advanced Usage
* **Inheritance**: Preserved methods marked with `@conserve` are correctly inherited.
* **Caching**: Stash automatically caches generated classes for improved performance.
* **Interning**: String attributes are automatically interned to ensure memory efficiency.

## 🧪 Testing
Stash provides a full testing suite covering preservation, immutability, caching and general performance metrics. Run tests via:

```python
pytest
```

## 📜 Licensing
This project is licensed under the MIT License - see the LICENSE section for further details.

## 👥 Collaboration
If you have any suggestions for improvements to the codebase, future app extensions or you simply wish to help expand Stash's functionality further, please do not hesitate to reach out at: `HysingerDev@gmail.com`