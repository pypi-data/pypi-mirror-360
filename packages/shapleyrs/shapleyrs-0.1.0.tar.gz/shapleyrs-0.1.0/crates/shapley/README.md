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
use shapley::Shapley;

let shapley = Shapley::new(players: [1, 2], coalition_worth: {
    (): 0,
    (1,): 10,
    (2,): 20,
    (1, 2): 30,
});

println!("{}", shapley.shapley_value(1)); // 10
println!("{}", shapley.shapley_value(2)); // 20
```
