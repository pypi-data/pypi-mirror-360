# Shapley


[![Crates.io](https://img.shields.io/crates/v/shapley)](https://crates.io/crates/shapley)
[![docs.rs](https://img.shields.io/docsrs/shapley)](https://docs.rs/shapley/latest/shapley/)
[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)


[`shapley`](https://github.com/shenxiangzhuang/shapley)
is a fast shapley value calculator written in rust.


## Quick Start

### Install

```bash
cargo add shapley
```

### Usage

```rust
use std::collections::HashMap;

use shapley::{Coalition, Shapley};

fn main() {
    let players = vec![1, 2];
    let coalition_worth = HashMap::from([
        (Coalition::new(vec![]), 0.0),
        (Coalition::new(vec![1]), 10.0),
        (Coalition::new(vec![2]), 20.0),
        (Coalition::new(vec![1, 2]), 30.0),
    ]);
    let shapley = Shapley::new(players, coalition_worth);
    println!("player1: {}", shapley.shapley_value(1).unwrap());  // 10
    println!("player2: {}", shapley.shapley_value(2).unwrap());  // 20
}
```
