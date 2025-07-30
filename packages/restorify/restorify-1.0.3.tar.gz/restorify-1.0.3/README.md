# Restorify
Convert json objects and files into python objects of type that you need.

## Quick guide

### Simple conversions
The code below will convert json list into `list`, `tuple` and `set` respectively.
```python
from restorify import restore

j1 = """
[
	1, 2, 3, 1
]
"""
print( restore(j1, list[float]) )
print( restore(j1, tuple[float]) )
print( restore(j1, set[float]) )
```
Output:
```
[1.0, 2.0, 3.0, 1.0]
(1.0, 2.0, 3.0, 1.0)
{1.0, 2.0, 3.0}
```
### Collections conversions
You can easily convert collections outside of simple built-ins. Note how nested `tuple` and `set` are accounted for.
```python

from restorify import restore
from collections import OrderedDict

j2 = """
{
	"key1" : [1, 2, 3]
}
"""
print( restore(j2, OrderedDict[str, tuple]) )
print( restore(j2, OrderedDict[str, set]) )
```
 Output:
 ```
OrderedDict({'key1': (1, 2, 3)})
OrderedDict({'key1': {1, 2, 3}})
```
 ### Dataclasses
`Dataclass`es (and everything type-annotated really) can be converted too.
```python
from restorify import restore
from dataclasses import dataclass

@dataclass
class TestClass1:
	id: str
	data: list[int]

j3 = """
{
	"id" : "MyId",
	"data": [ 1, 42, 69 ]
}
"""

@dataclass
class TestClassNested:
	test1_list: list[TestClass1]

j4 = """
{
	"test1_list": [
		{
			"id" : "MyId1",
			"data": [ 1, 42, 69 ]
		},
		{
			"id" : "MyId2",
			"data": [ 321, 421, 3011 ]
		}
	]
}
"""
print( restore(j4, TestClassNested) )
print( restore(j3, TestClass1) )
```
Output:
```
TestClass1(id='MyId', data=[1, 42, 69])
TestClassNested(test1_list=[TestClass1(id='MyId1', data=[1, 42, 69]), TestClass1(id='MyId2', data=[321, 421, 3011])])
```
### Implicit file path conversions 
Why loading jsons manually if you can just get and object from a file path? Note the use of `@restorable` decorator and `RestorableClass.json_name` class member. In the end, the new file is `dump`ed into new directory (but with the same name).
```python
from restorify import restore
from dataclasses import dataclass
from pathlib import Path

@dataclass
@restorable
class RestorableClass:
	field: int
	another_filed: list[list]

p1 = Path(RestorableClass.json_name)
obj = restore(p1)
print(obj)

p2 = Path('another_dir')
p2.mkdir()
obj.dump(p2)
```
Output:
```
RestorableClass(field=5, another_filed=[[1, 1.0, 'str'], [[4, 5, 6], 'hello!']])
```
The `restorable_class.json` file contents is the following:
```json
{
    "field": 5,
    "another_filed": [
        [
            1,
            1.0,
            "str"
        ],
        [
            [
                4,
                5,
                6
            ],
            "hello!"
        ]
    ]
}
```

## Failed conversion
Upon failed conversion `TypeError` is raised.