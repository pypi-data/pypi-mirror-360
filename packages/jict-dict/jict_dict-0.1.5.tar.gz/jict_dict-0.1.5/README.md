# JICT

**JICT** is a bidirectional dictionary that supports **reverse lookups** and behaves like a standard `dict` — but with a key difference: it lets you use **unhashable keys and values** (like lists or dicts), provided you manage them carefully.

---

## 🚨 Important Note on Unhashables

`JICT` **does not automatically convert** unhashable types for you.  
If you want to use `list`, `dict`, or `set` as keys or values **in any context that requires hashing** (e.g., reverse lookup or hashing the entire object), **you must manually convert them using `ELJIX.Convert()`**.

```python
from jict import JICT, ELJIX

j = JICT()

val = {'a': [1, 2]}
conv_val = ELJIX.Convert(val)

j['key'] = conv_val
print(j.index(conv_val))  # Works
```

---

## Installation

```bash
pip install jict_dict
```

---

## Features

- ✅ Fast reverse lookup via `.index(value)`
- ✅ Supports unhashable types (manual conversion required)
- ✅ Full `dict`-like API
- ✅ Custom `.copy()`, `.update()`, `.fromkeys()`, etc.
- ✅ Optional hash support via `ELJIX`

---

## Usage

```python
from jict import JICT, ELJIX

j = JICT()

j['a'] = 42
j['b'] = ELJIX.Convert([1, 2, 3])  # manual conversion

print(j['a'])               # 42
print(j.index(42))          # {'a'}
print(j.index(ELJIX.Convert([1, 2, 3])))  # {'b'}

# Use like a normal dict
del j['a']
print('a' in j)             # False
print(list(j.keys))         # ['b']
```

---

## Time Complexities

### 🔁 `JICT`

| Operation                | Time        | Notes                                              |
|--------------------------|-------------|----------------------------------------------------|
| `j[key]`                 | O(1)        | Dict-style access                                  |
| `j[key] = value`         | O(1)        | Raw value is stored directly                       |
| `del j[key]`             | O(1)        | Cleans reverse index                               |
| `j.index(value)`         | O(1)        | Requires value to be hashable                      |
| `j.pop(key)`             | O(1)        | Removes key + reverse entry                        |
| `j.popitem()`            | O(1)        | Removes arbitrary item (KeyError if empty)         |
| `j.update(...)`          | O(N)        | Adds multiple entries                              |
| `hash(j)`                | O(N × C)    | Uses `ELJIX.Convert(self)`                         |
| `j.copy()`               | O(N)        | Shallow copy                                       |

> 🔹 `C` = cost of `ELJIX.Convert`

---

### 🧠 `ELJIX`

| Method                | Time         | Description                                        |
|------------------------|--------------|----------------------------------------------------|
| `Convert(obj)`         | O(N)         | Recursively makes object hashable                 |
| `Unconvert(obj)`       | O(N)         | Recovers original structure                       |

---

## API Reference

### Class: `JICT`

#### Constructor

```python
JICT(initial=None)
```

#### Methods

| Method                  | Description                                    |
|-------------------------|------------------------------------------------|
| `add(key, value)`       | Add a key-value pair                          |
| `remove(key)`           | Remove a key and its reverse entry            |
| `pop(key, default)`     | Like `dict.pop()`                             |
| `popitem()`             | Like `dict.popitem()`                          |
| `clear()`               | Empties both key-value and reverse maps       |
| `copy()`                | Returns a shallow copy                        |
| `get(key, default)`     | Get value or default                          |
| `setdefault(k, default)`| Insert if key doesn’t exist                   |
| `update(other, **kw)`   | Accepts dicts or iterable of pairs            |
| `index(value)`          | Returns set of keys for a given value         |
| `fromkeys(iterable, v)` | Like `dict.fromkeys()`                        |

#### Properties

| Property    | Description                     |
|-------------|---------------------------------|
| `keys`      | All keys                        |
| `values`    | All values                      |
| `items`     | All key-value pairs             |

---

### Class: `ELJIX`

Helper class to convert complex/unhashable objects into hashable formats (used mostly for hashing).

#### Methods

```python
ELJIX.Convert(obj)
ELJIX.Unconvert(obj)
```

| Type       | Converted To   |
|------------|----------------|
| `list`     | `tuple`        |
| `set`      | `frozenset`    |
| `dict`     | `frozenset` of pairs |
| `tuple`    | recursively converted |
| other      | stays the same or becomes `id(obj)` |

---

## Example with Manual Conversion

```python
j = JICT()

data = {'x': [1, 2]}
converted = ELJIX.Convert(data)

j['a'] = converted
print(j.index(converted))  # {'a'}

# Avoid using raw dicts/lists in index() or reverse maps
```

---

## License

MIT License

---

## Author

Created by [ElJeiForeal](https://github.com/ElJeiForeal)  
Maintained independently.

