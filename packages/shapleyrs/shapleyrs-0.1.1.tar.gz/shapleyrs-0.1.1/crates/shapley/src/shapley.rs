use anyhow::{Context, Error, Result};
use rayon::prelude::*;
use statrs::function::factorial::binomial;
use std::collections::{BTreeSet, HashMap};

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Coalition {
    members: BTreeSet<u64>,
}

impl Coalition {
    pub fn new(members: Vec<u64>) -> Self {
        Coalition {
            members: members.into_iter().collect(),
        }
    }

    fn size(&self) -> usize {
        self.members.len()
    }

    fn contains(&self, player: u64) -> bool {
        self.members.contains(&player)
    }

    fn subtract(&self, player: u64) -> Self {
        let mut new_members = self.members.clone();
        new_members.remove(&player);
        Coalition {
            members: new_members,
        }
    }
}

#[derive(Debug)]
pub struct Shapley {
    coalition_worth: HashMap<Coalition, f64>,
    coalition_size_weights: HashMap<usize, f64>,
}

impl Shapley {
    pub fn new(players: Vec<u64>, mut coalition_worth: HashMap<Coalition, f64>) -> Self {
        let n = players.len();
        // Ensure empty coalition exists (value = 0.0)
        coalition_worth.entry(Coalition::new(vec![])).or_insert(0.0);

        // Precompute combinatorial weights
        let mut weights = HashMap::new();
        for s in 0..n {
            // s = coalition size without player i
            let binom = binomial((n - 1) as u64, s as u64);
            weights.insert(s, (1.0 / n as f64) / binom);
        }

        Shapley {
            coalition_worth,
            coalition_size_weights: weights,
        }
    }

    pub fn shapley_value(&self, player: u64) -> Result<f64> {
        let (total_contribution, total_weight) = self
            .coalition_worth
            .par_iter()
            .map(|(coalition, &value_with)| {
                // Consider only coalitions containing player
                match coalition.contains(player) {
                    false => Ok::<(f64, f64), Error>((0.0, 0.0)),
                    true => {
                        let without = coalition.subtract(player);
                        let value_without = self.coalition_worth.get(&without);
                        match value_without {
                            None => Ok((0.0, 0.0)),
                            Some(value_without) => {
                                let s = without.size();
                                let weight = self
                                    .coalition_size_weights
                                    .get(&s)
                                    .context("Missing combinatorial weight")?;

                                let contribution = weight * (value_with - value_without);
                                Ok((contribution, weight.clone()))
                            }
                        }
                    }
                }
            })
            .filter_map(|x: Result<_, _>| x.ok())
            .reduce_with(|a, b| (a.0 + b.0, a.1 + b.1))
            .unzip();

        match (total_weight, total_contribution) {
            (Some(weight), Some(contribution)) if weight.abs() >= f64::EPSILON => {
                Ok(contribution / weight)
            }
            _ => anyhow::bail!("Insufficient data for player {}", player),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use maplit::hashmap;
    use statrs::assert_almost_eq;

    #[test]
    fn test_empty_coalition_handling() {
        let coalition_worth = hashmap! {
            Coalition::new(vec![1]) => 5.0,
        };
        let shapley = Shapley::new(vec![1], coalition_worth);
        // Should contain empty coalition automatically
        assert_eq!(
            shapley.coalition_worth.get(&Coalition::new(vec![])),
            Some(&0.0)
        );
    }

    #[test]
    fn test_missing_data() {
        let coalition_worth = hashmap! {
            Coalition::new(vec![1, 2]) => 10.0,
        };
        let shapley = Shapley::new(vec![1, 2], coalition_worth);
        assert!(shapley.shapley_value(1).is_err());
    }

    #[test]
    fn test_simple_shapley_value() {
        let coalition_worth = hashmap! {
            Coalition::new(vec![]) => 0.0,
            Coalition::new(vec![1]) => 10.0,
            Coalition::new(vec![2]) => 20.0,
            Coalition::new(vec![1, 2]) => 30.0,
        };

        let shapley = Shapley::new(vec![1, 2], coalition_worth);
        assert_eq!(shapley.shapley_value(1).unwrap(), 10.0);
        assert_eq!(shapley.shapley_value(2).unwrap(), 20.0);
    }

    // https://gtl.csa.iisc.ac.in/gametheory/ln/web-cp5-shapley.pdf
    // 2.1 Example 1: Divide the Dollar Game
    #[test]
    fn test_divide_dollar_game() {
        let coalition_worth = hashmap! {
            Coalition::new(vec![1]) => 0.0,
            Coalition::new(vec![2]) => 0.0,
            Coalition::new(vec![3]) => 0.0,
            Coalition::new(vec![2, 3]) => 0.0,

            Coalition::new(vec![1, 2]) => 300.0,
            Coalition::new(vec![1, 3]) => 300.0,
            Coalition::new(vec![1, 2, 3]) => 300.0,
        };

        let shapley = Shapley::new(vec![1, 2, 3], coalition_worth);
        assert_almost_eq!(shapley.shapley_value(1).unwrap(), 200.0, 1e-10);
        assert_almost_eq!(shapley.shapley_value(2).unwrap(), 50.0, 1e-10);
        assert_almost_eq!(shapley.shapley_value(3).unwrap(), 50.0, 1e-10);
    }

    // https://gtl.csa.iisc.ac.in/gametheory/ln/web-cp5-shapley.pdf
    // 2.4 Example 4: A Logistics Game(the doc maybe give wrong result)
    #[test]
    fn test_logistics_game() {
        let coalition_worth = hashmap! {
            Coalition::new(vec![1]) => 0.0,
            Coalition::new(vec![2]) => 0.0,
            Coalition::new(vec![3]) => 0.0,
            Coalition::new(vec![4]) => 0.0,

            Coalition::new(vec![1, 2]) => 0.0,
            Coalition::new(vec![1, 3]) => 0.0,
            Coalition::new(vec![1, 4]) => 0.0,
            Coalition::new(vec![2, 3]) => 0.0,
            Coalition::new(vec![2, 4]) => 0.0,
            Coalition::new(vec![3, 4]) => 0.0,

            Coalition::new(vec![1, 2, 3]) => 0.0,
            Coalition::new(vec![2, 3, 4]) => 0.0,

            Coalition::new(vec![1, 2, 4]) => 45.0,
            Coalition::new(vec![1, 3, 4]) => 40.0,
            Coalition::new(vec![1, 2, 3, 4]) => 65.0,
        };

        let shapley = Shapley::new(vec![1, 2, 3, 4], coalition_worth);
        assert_almost_eq!(shapley.shapley_value(1).unwrap(), 23.333333333333332, 1e-10);
        assert_almost_eq!(shapley.shapley_value(2).unwrap(), 10.0, 1e-10);
        assert_almost_eq!(shapley.shapley_value(3).unwrap(), 8.333333333333332, 1e-10);
        assert_almost_eq!(shapley.shapley_value(4).unwrap(), 23.333333333333332, 1e-10);
    }
}
