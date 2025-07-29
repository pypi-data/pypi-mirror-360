from restorify import restore


from collections import *


j = """
[1, 2, 3]
"""

print( restore(j, list) )
print( restore(j, list[float]) )
print( restore(j, list[float, str]) )
print( restore(j, list[float, str, float]) )
print( restore(j, list[float, str, float, str]) )

j = """
{
    "one" : 1,
    "two" : 2
}
"""

print( restore(j, dict) )
print( restore(j, dict[int]) )
print( restore(j, dict[str, float]) )
print( restore(j, dict[str, float, int]) )

print( restore(j, OrderedDict) )
print( restore(j, OrderedDict[int]) )
print( restore(j, OrderedDict[str, float]) )
print( restore(j, OrderedDict[str, float, int]) )

j = """
[
    null,
    [        
        ["one", 1],
        ["two", 2]       
    ]
]
"""

print( restore(j, defaultdict) )
print( restore(j, defaultdict[int]) )
print( restore(j, defaultdict[str, float]) )
print( restore(j, defaultdict[str, float, int]) )

j = """
[
    [ 1, 2, 3 ], 
    [ 4, 5, 6 ] 
]
"""

class A:
    def __init__(self, a, b, c):
        print(a, b, c)

print( restore(j, list[A]) )

j = """
[
    [ [ 1, 2, 3], {"one": 1, "two": 2} ],
    [ [ 4, 5, 6], {"one": 4, "two": 5} ]
]
"""

j = """
    [ [1,2,3], [4,5,6] ]
"""

class A:
    def __init__(self, l1, l2):
        print(l1)
        print(l2)

print( restore(j, A) )

j = """
    { "l1" : [ 1 ] }
"""

class A:
    def __init__(self, l1):
        print(l1)

print( restore(j, A) )