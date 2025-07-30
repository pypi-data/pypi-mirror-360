class ELJIX:
    @staticmethod
    def Convert(obj):
        if isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        elif isinstance(obj, JICT):
            return ("JICT", frozenset((ELJIX.Convert(k), ELJIX.Convert(v)) for k, v in obj.items))
        elif isinstance(obj, dict):
            return ("dict", frozenset((ELJIX.Convert(k), ELJIX.Convert(v)) for k, v in obj.items()))
        elif isinstance(obj, list):
            return ("list", tuple(ELJIX.Convert(e) for e in obj))
        elif isinstance(obj, tuple):
            return ("tuple", tuple(ELJIX.Convert(e) for e in obj))
        elif isinstance(obj, set):
            return ("set", frozenset(ELJIX.Convert(e) for e in obj))
        elif hasattr(obj, "items"):
            items = obj.items
            if callable(items):
                return ("dict_like", frozenset((ELJIX.Convert(k), ELJIX.Convert(v)) for k, v in items()))
            else:
                return ("dict_like", frozenset((ELJIX.Convert(k), ELJIX.Convert(v)) for k, v in items))
        else:
            return id(obj)


    @staticmethod
    def Unconvert(obj):
        if isinstance(obj, tuple) and len(obj) == 2 and isinstance(obj[0], str):
            type_tag, data = obj
            if type_tag == "JICT":
                return JICT({ELJIX.Unconvert(k): ELJIX.Unconvert(v) for k, v in data})
            elif type_tag == "dict":
                return {ELJIX.Unconvert(k): ELJIX.Unconvert(v) for k, v in data}
            elif type_tag == "dict_like":
                # fallback to dict
                return {ELJIX.Unconvert(k): ELJIX.Unconvert(v) for k, v in data}
            elif type_tag == "list":
                return [ELJIX.Unconvert(e) for e in data]
            elif type_tag == "tuple":
                return tuple(ELJIX.Unconvert(e) for e in data)
            elif type_tag == "set":
                return set(ELJIX.Unconvert(e) for e in data)
            else:
                return obj
        else:
            return obj




class JICT:
    def __init__(self, initial=None):
        self.__key_to_value = {}
        self.__value_to_keys = {}

        if initial is not None:
            self.update(initial)

    def __getitem__(self, key):
        return self.__key_to_value[key]

    def __setitem__(self, key, value):
        self.add(key, value)

    def __delitem__(self, key):
        self.remove(key)
    
    def __hash__(self):
        return hash(ELJIX.Convert(self))

    def __contains__(self, key):
        return key in self.__key_to_value

    def __iter__(self):
        return iter(self.__key_to_value)

    def __repr__(self):
        return repr(self.__key_to_value)

    def __len__(self):
        return len(self.__key_to_value)

    def add(self, key, value):
        if key in self.__key_to_value:
            self.remove(key)

        self.__key_to_value[key] = value
        if value not in self.__value_to_keys:
            self.__value_to_keys[value] = set()
        self.__value_to_keys[value].add(key)

    def index(self, value):
        return self.__value_to_keys.get(value)

    def remove(self, key):
        value = self.__key_to_value.pop(key)
        key_set = self.__value_to_keys[value]
        key_set.remove(key)
        if not key_set:
            del self.__value_to_keys[value]

    def pop(self, key, default=None):
        if key in self.__key_to_value:
            value = self.__key_to_value[key]
            self.remove(key)
            return value
        if default is not None:
            return default
        raise KeyError(key)

    def popitem(self):
        key, value = next(iter(self.__key_to_value.items()))
        self.remove(key)
        return key, value

    def clear(self):
        self.__key_to_value.clear()
        self.__value_to_keys.clear()

    def copy(self):
        new_obj = JICT()
        new_obj.__key_to_value = self.__key_to_value.copy()
        new_obj.__value_to_keys = {k: v.copy() for k, v in self.__value_to_keys.items()}
        return new_obj

    def get(self, key, default=None):
        return self.__key_to_value.get(key, default)

    def setdefault(self, key, default):
        if key in self.__key_to_value:
            return self.__key_to_value[key]
        self.add(key, default)
        return default

    def update(self, other=(), **kwargs):
        if hasattr(other, "items"):
            for k, v in other.items():
                self.add(k, v)
        else:
            for k, v in other:
                self.add(k, v)
        for k, v in kwargs.items():
            self.add(k, v)

    @property
    def Keys(self):
        return self.__key_to_value.keys()

    @property
    def items(self):
        return self.__key_to_value.items()

    @property
    def values(self):
        return self.__key_to_value.values()

    @classmethod
    def fromkeys(cls, iterable, value=None):
        new_obj = cls()
        for key in iterable:
            new_obj.add(key, value)
        return new_obj
