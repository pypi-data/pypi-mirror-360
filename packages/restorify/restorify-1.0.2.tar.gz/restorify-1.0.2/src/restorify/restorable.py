import dataclasses
import json
from pathlib import Path
from contextlib import contextmanager

import restorify.utils as _u


@contextmanager
def all_exceptions_caught(*args, **kwargs):
    try:
        yield None
    except:
        pass


__classes_map = {}
def restorable(cls):
    cls = _jsonable(cls)
    cls.dump = _dump_object
    cls.load = classmethod(lambda c, p: c.from_json( _u.read_text(p)) )
    __classes_map[cls.__name__] = cls
    return cls

def restore(param: any, cls = None) -> object:
    if cls: 
        if isinstance(param, Path):
            return cls.load(param)
        else:
            return _from_object(cls, json.loads(param) )
    else:
        return _get_object(param)
    
def _get_object(where_from: Path) -> object:
    file_name  = where_from.parts[-1].split('.')[0]
    class_name = _u.snake_to_camel(file_name)
    if class_name not in __classes_map:
        return None
    cls = __classes_map[class_name]
    return cls.load(where_from)
 
def _dump_object(self, where: Path):
    d = self.to_dict()
    _u.write_json(d, where.joinpath(self.json_name))


def _jsonable(cls):
    cls = _dictable(cls)
    cls.to_json = _to_json
    cls.from_json = classmethod(_from_json)
    cls.json_name =  _u.camel_to_snake(cls.__name__) + ".json"
    return cls

def _dictable(cls):
    cls.to_dict = _to_dict
    cls.from_dict = classmethod(_from_dict)
    return cls


def _to_json(self):
    return json.dumps(_to_dict(self), indent=4)

def _from_json(cls, j: str):
    return _from_dict( cls, json.loads(j) )

def _to_dict(self):
    if dataclasses.is_dataclass(self):
        return dataclasses.asdict(self)
    return vars(self)

def _from_dict(cls, val: dict):
    return _from_object(cls, val)

def _from_object(cls, val: object):
    with all_exceptions_caught():
        ann_dict = cls.__annotations__
        with all_exceptions_caught():
            #classable is made from args and kwargs
            args, kwargs = val #implicit check for two elements
            args   = _from_object(list, args)
            kwargs = _from_object(dict, kwargs)
            with all_exceptions_caught():
                return cls( *args, **kwargs )
            with all_exceptions_caught():
                return cls(args, kwargs)
        with all_exceptions_caught():
            #classable is made from dict
            types_list = [ ann_dict[k] if k in ann_dict else type(val[k]) for k in val.keys() ]
            d = {  k:_from_object(t,v) for k, v, t in zip(val.keys(), val.values(), types_list) }
            return cls(**d)
        with all_exceptions_caught():
            #classable is made from list
            return cls( *_from_object(list, val) )

    with all_exceptions_caught():
        view = val.items()
        _ = iter(view) #safelly check if the view is iterable
        with all_exceptions_caught():
            type_of_dict_key, type_of_dict_val = cls.__args__[0:2]
            return cls({ _from_object(type_of_dict_key, k):_from_object(type_of_dict_val, v) for k,v in view })
        with all_exceptions_caught():
            type_of_dict_key = cls.__args__[0]
            return cls({ _from_object(type_of_dict_key, k):_from_object(type(v), v) for k,v in view })
        with all_exceptions_caught():
            return cls({ _from_object(type(k), k):_from_object(type(v), v) for k,v in view })

    with all_exceptions_caught():
        _ = iter(val) #safelly check if val is iterable
        types_list = list(cls.__args__)
        if len(types_list) == 1:
            types_list *= len(val)
        elif len(types_list) > len(val):
            types_list = types_list[0:len(val)]
        else:
            types_list += [ type(v) for v in val[len(types_list):] ]
        return cls( [ _from_object(t, v) for t, v in zip(types_list, val) ] )

    with all_exceptions_caught():
        return cls(val) #base case

    raise TypeError(f"Cannot create class of type {cls.__name__} with value {str(val)}.") #whaaaaaaa...?
