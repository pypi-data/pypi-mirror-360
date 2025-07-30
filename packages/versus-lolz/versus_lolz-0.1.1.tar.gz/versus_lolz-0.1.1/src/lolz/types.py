from typing import Literal, Iterable, Any


__all__ = [
    "TagId",
    "Origin",
    "UserId",
    "EmailProvider",
    "Array",
    "Bool",
    "Page",
    "Price",
    "String",
    "Any",
    "Object",
    "Matters",
    "TimeNot",
    "Currency",
]


TagId = int
Origin = str
UserId = int
EmailProvider = str
Array = Iterable
Bool = bool
Page = int
Price = int
String = str

TimeNot = Literal[
    "day",
    "month",
    "year",
]

Matters = Literal[
    "yes",
    "no",
    "nomatter",
]

OrderBy = Literal[
    "price_to_up",
    "price_to_down",
    "pdate_to_up",
    "pdate_to_down",
    "pdate_to_up_upload",
    "pdate_to_down_upload",
    "edate_to_up",
    "edate_to_down",
    "ddate_to_up",
    "ddate_to_down",
]

Show = Literal[
    "active",
    "paid",
    "deleted",
    "awaiting",
    "closed",
    "discount_request",
    "stickied",
    "pre_active",
]

Currency = Literal[
    "rub",
    "uah",
    "kzt",
    "byn",
    "usd",
    "eur",
    "gbp",
    "cny",
    "try",
    "jpy",
    "brl",
]


EmailType = Literal[
    "autoreg",
    "native",
    "no",
    "no_market",
]


def _objectize_list(lst: list):
    for i, item in enumerate(lst):
        if isinstance(item, dict):
            lst[i] = Object(item)
        elif isinstance(item, list):
            _objectize_list(item)


def _deobjectify_list(lst: list):
    for i, item in enumerate(lst):
        if isinstance(item, Object):
            lst[i] = item.to_dict()
        elif isinstance(item, list):
            lst[i] = _deobjectify_list(item.copy())
    
    return lst


class Object:
    def __init__(self, dct: dict):
        self.__dict = {}
        # разбиение на две строки имеет смысл в данной ситуации! @Vi
        self.__dict.update(dct)

        for key, value in dct.items():
            if isinstance(value, dict):
                self[key] = Object(value)
            elif isinstance(value, list):
                _objectize_list(value)
    
    def to_dict(self):
        rv = {}

        for key, value in self.__dict.items():
            if isinstance(value, Object):
                rv[key] = value.to_dict()
            elif isinstance(value, list):
                rv[key] = _deobjectify_list(value.copy())
            rv[key] = value
        
        return rv

    def __getattr__(self, name):
        if name[0] == '_' or name in ("to_dict", "attrs", "union"):
            return object.__getattribute__(self, name)
        return self.__dict[name]
    
    def __str__(self):
        import pprint
        return pprint.pformat(self.__dict, indent=4)
    
    def __repr__(self):
        import json
        return json.dumps(self.__dict)
    
    def __getitem__(self, key):
        return self.__dict[key]
    
    def __setitem__(self, key, value):
        self.__dict[key] = value
    
    def __delitem__(self, key):
        del self.__dict[key]
    
    def __iter__(self):
        return iter(self.__dict)
    
    def __len__(self):
        return len(self.__dict)
    
    def __eq__(self, value):
        return self.__dict == value
    
    def __ne__(self, value):
        return self.__dict != value
    
    def __lt__(self, value):
        return self.__dict < value
    
    def __le__(self, value):
        return self.__dict <= value
    
    def __gt__(self, value):
        return self.__dict > value
    
    def __ge__(self, value):
        return self.__dict >= value
    
    def __contains__(self, key):
        return key in self.__dict
    
    def union(self, other):
        if isinstance(other, Object):
            self.__dict.update(other.__dict)
        elif isinstance(other, dict):
            self.__dict.update(other)
        else:
            raise TypeError("Object.union() argument should be an Object or dict")
    
    def attrs(self):
        return tuple(self.__dict.keys())
