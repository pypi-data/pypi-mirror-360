use pyo3::prelude::*;
use std::collections::HashMap;

#[derive(Debug)]
#[pyclass]
struct Shapley {
    inner: shapley::shapley::Shapley,
}

#[pymethods]
impl Shapley {
    #[new]
    fn py_new(players: Vec<u64>, coalition_worth: HashMap<Vec<u64>, f64>) -> PyResult<Self> {
        let mut converted_worth = HashMap::new();
        for (members, worth) in coalition_worth {
            let coalition = shapley::shapley::Coalition::new(members);
            converted_worth.insert(coalition, worth);
        }

        let inner = shapley::shapley::Shapley::new(players, converted_worth);
        Ok(Self { inner })
    }

    fn shapley_value(&self, player: u64) -> PyResult<f64> {
        self.inner
            .shapley_value(player)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn _shapley(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add_class::<Shapley>()?;
    Ok(())
}
