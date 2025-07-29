# JSONexpr for Python

This document describes using JSONexpr with Python.
For the language overview, see the [main page](https://github.com/markuskimius/jsonexpr).


## Installation

```sh
pip3 install jsonexpr
```

Python 3.8 and later are supported.


## Example

```python
import jsonexpr as je

instance = je.instance()
parsed = instance.parse("""
    PRINT("I have " + LEN(grades) + " students");
    PRINT("Alice's grade is " + grades.alice);
    grades
""")
symmap = instance.symmap({
    "grades" : {
        "alice"   : "A",
        "bob"     : "B",
        "charlie" : "B",
    }
})

result = parsed.eval(symmap)
```

Output:

```
I have 2 students
Alice's grade is A
```


## License

[Apache 2.0](https://github.com/markuskimius/jsonexpr/blob/main/LICENSE)
