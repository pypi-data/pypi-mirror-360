
# JICT DICT

**JICT** is a bidirectional dictionary with superpowers. It behaves like a normal Python `dict`, but with advanced features like **reverse lookup**, **support for unhashable keys/values**, and a fully extendable API — making it great for advanced data mapping, indexing, and transformation tasks.

---

## 🆚 Why Use `JICT` Over `dict`?

Here’s what `JICT` can do that regular `dict` **cannot**:

### 1. 🔁 Reverse Lookup

With `JICT`, you can instantly find all keys that map to a given value using `.index(value)` — something a regular `dict` does not support without looping.

```python
from jict_dict import JICT

j = JICT()
j['x'] = 10
j['y'] = 10
j['z'] = 5

print(j.index(10))  # {'x', 'y'}
print(j.index(5))   # {'z'}
```

### 2. 🧩 Use Unhashable Keys/Values (manually converted)

Regular `dict` requires all keys to be hashable. `JICT` supports unhashable types like `list`, `dict`, and `set` — as long as you **manually convert them** using `ELJIX.Convert()`.

```python
from jict_dict import JICT, ELJIX

j = JICT()
data = {'a': [1, 2]}
key = ELJIX.Convert(data)

j[key] = "stored!"
print(j[key])  # "stored!"
print(j.index("stored!"))  # {converted key}
```

> ✅ This allows you to safely use complex data structures as keys or values — something normal `dict`s will reject with `TypeError`.

### 3. 💥 True Bidirectional Mapping

When you assign a value, `JICT` tracks both key → value **and** value → key automatically, meaning `.index()` is always up-to-date.

If you delete or update keys, the reverse mappings are cleaned up too:

```python
j = JICT()
j['a'] = 1
j['b'] = 1

print(j.index(1))  # {'a', 'b'}

del j['a']
print(j.index(1))  # {'b'}
```

---

## 🚨 Important Note on Unhashables

`JICT` **does not automatically convert** unhashable types for you.  
If you want to use `list`, `dict`, or `set` as keys or values **in any context that requires hashing** (e.g., reverse lookup or hashing the entire object), **you must manually convert them using `ELJIX.Convert()`**.

```python
from jict_dict import JICT, ELJIX

j = JICT()

val = {'a': [1, 2]}
conv_val = ELJIX.Convert(val)

j['key'] = conv_val
print(j.index(conv_val))  # Works
```

---

## 📦 Installation

```bash
pip install jict_dict
```

---

## 🔧 Features Summary

- ✅ Reverse lookup: `j.index(value)` returns all keys for a value.
- ✅ Supports unhashable keys/values with `ELJIX.Convert()`.
- ✅ Custom `dict` API with `.fromkeys()`, `.update()`, `.copy()`, etc.
- ✅ Fast and safe key/value management.
- ✅ Optional full-object hashing via `ELJIX`.

---

## 🧪 Real-World Examples

### 🔍 Group keys by values (reverse lookup)

```python
j = JICT()
j['admin'] = 'group1'
j['bob'] = 'group2'
j['alice'] = 'group1'

print(j.index('group1'))  # {'admin', 'alice'}
```

### 🧬 Hash unhashable objects

```python
from jict_dict import ELJIX

data = {'x': [1, 2, 3]}
converted = ELJIX.Convert(data)
print(hash(converted))  # safe!

original = ELJIX.Unconvert(converted)
print(original)  # [1, 2, {'x': 3}]
```

### 🧼 Safe Deletion Keeps Index Clean

```python
j = JICT()
j['foo'] = 123
j['bar'] = 123

print(j.index(123))  # {'foo', 'bar'}
j.pop('foo')
print(j.index(123))  # {'bar'}
```

### ⚙️ Initialize with Converted Input

```python
from jict_dict import JICT, ELJIX

initial = {
    "sword": "meele",
    "bow": "ranged",
    "fists": "meele"
}

j = JICT(initial)
print(j.index("meele"))  # {'sword', 'fists'}
```

### ✨ Cleaner Code

```python
from jict_dict import JICT, ELJIX

RawItems = JICT({
    "sword": "melee",
    "bow": "ranged",
    "fists": "melee",
})

RawArmor = JICT({
    "iron": "chestplate",
    "gold": "chestplate",
})

# Convert JICT instances to hashable versions
Items = ELJIX.Convert(RawItems)
Armor = ELJIX.Convert(RawArmor)

# Store converted objects inside another JICT
Inventory = JICT({
    "Armor": Armor,
    "Items": Items,
})

# Unconvert 'Armor' to get back a JICT instance, then do reverse lookup
armor_obj = ELJIX.Unconvert(Inventory["Armor"])
print(armor_obj.index("chestplate"))  # Output: {'iron', 'gold'}
```
---

## ⏱ Time Complexities

### `JICT`

| Operation          | Time        | Description                            |
|--------------------|-------------|----------------------------------------|
| `j[key]`           | O(1)        | Dict-style access                      |
| `j[key] = value`   | O(1)        | Stores value and updates reverse map  |
| `j.index(value)`   | O(1)        | Reverse lookup (set of keys)          |
| `del j[key]`       | O(1)        | Removes key and cleans reverse map    |
| `j.copy()`         | O(N)        | Shallow copy                          |
| `update()`         | O(N)        | Batch insert                          |
| `hash(j)`          | O(N×C)      | With `ELJIX.Convert` (if used)        |

> `C` = cost of converting a value with `ELJIX`

---

### `ELJIX`

| Method             | Time    | Description                          |
|--------------------|---------|--------------------------------------|
| `Convert(obj)`     | O(N)    | Recursively converts to hashable    |
| `Unconvert(obj)`   | O(N)    | Recovers original data              |

---

## 🧠 ELJIX: Hashable Conversion

`ELJIX` is a utility class to make **anything** hashable — even if it's a list or dictionary.

### Conversion Types

| Type     | Converted To                  |
|----------|-------------------------------|
| `list`   | `tuple`                       |
| `dict`   | `frozenset` of key-value pairs|
| `set`    | `frozenset`                   |
| `tuple`  | Recursively converted         |
| `other`  | Left as-is (or fallback hash) |

```python
x = [1, 2, {"a": 3}]
converted = ELJIX.Convert(x)
print(hash(converted))  # safe!

original = ELJIX.Unconvert(converted)
print(original)  # [1, 2, {'a': 3}]
```

---

## 🧩 API Overview

### Class: `JICT`

| Method                 | Description                          |
|------------------------|--------------------------------------|
| `add(k, v)`            | Add key-value pair                   |
| `remove(k)`            | Remove key and reverse entry         |
| `index(v)`             | Get set of keys for value            |
| `get(k, default)`      | Like `dict.get()`                    |
| `setdefault(k, d)`     | Set default if key not found         |
| `update(...)`          | Add multiple key-value pairs         |
| `copy()`               | Shallow copy                         |
| `clear()`              | Remove all items                     |
| `fromkeys(iter, v)`    | Like `dict.fromkeys()`               |
| `pop(k)`               | Remove key and return value          |
| `popitem()`            | Remove & return arbitrary item       |

### Properties

| Property    | Description            |
|-------------|------------------------|
| `keys`      | All keys (like `dict`) |
| `values`    | All values             |
| `items`     | Key-value pairs        |

---

## 🛠 Compatibility

- ✅ Python 3.6+
- ✅ No external dependencies
- ✅ Cross-platform
- ✅ Lightweight (~2KB installed)

---

## 🔐 License

MIT License

---

## 👤 Author

Created and maintained by **[ElJeiForeal](https://github.com/ElJeiForeal)**
