# mememo

![PyPI version](https://img.shields.io/badge/mememo-v1.1-5FC33B)
![Python version](https://img.shields.io/badge/python-2.5+-blue)
![Lightweight](https://img.shields.io/badge/lightweighter_than-numpy_or_statistics-red)
![Github](https://pypi-camo.freetls.fastly.net/23118282b10fb95911c44c745f183334700c10a4/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6f6e2d4769746875622d677265656e)

 The lightweight package to find the mean, median, and mode. (Hence the name MEanMEdianMOde)

---

## Benefits

- Most efficient and more lightweight than the `numpy` or `statistics` module.
- No need other 3rd-party modules to install.
- Only 3 functions.
---
#### Changelog: https://github.com/dUhEnC-39/mememo/blob/main/CHANGELOG.txt
#### Github repo: https://github.com/dUhEnC-39/mememo
## Documentation guide

## `mean()`

You can use the `mean()` function to find the mean of 2+ numbers.

```python
import mememo

a = mememo.mean([1, 2])
print(a) # Output: 1.5
```

#### Same way applies to the `median()` and `mode()` functions.

```python
a = mememo.median([1, 2])
print(a) # Output: 1.5
```
```python
a = mememo.mode([1, 2, 2])
print(a) # Output: 2
```

## Cruical note: The function must only take in one argument which is the list of numbers.

For example,
```python
mememo.mean(10, 15, 87)
```
will raise this error
```python
TypeError: mean() takes 1 positional argument but 3 were given
```
Any questions? Email [here](mailto:albeback01@gmail.com?subject=Python%20library%20mememo%20question.)