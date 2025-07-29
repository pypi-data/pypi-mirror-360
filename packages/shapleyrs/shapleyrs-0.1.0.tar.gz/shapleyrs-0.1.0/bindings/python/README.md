# Shapley


[![PyPI - Version](https://img.shields.io/pypi/v/shapleyrs)](https://pypi.org/project/shapleyrs/)
[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)


[`shapley`](https://github.com/shenxiangzhuang/shapley)
is a fast Shapley value calculator written in rust.


## Quick Start

### Install

```bash
pip install shapleyrs
```


### Usage

```python
from shapleyrs import Shapley

shapley = Shapley(players=[1, 2], coalition_worth={
    (): 0,
    (1,): 10,
    (2,): 20,
    (1, 2): 30,
})

print(shapley.shapley_value(1)) # 10
print(shapley.shapley_value(2)) # 20
```
