// Copyright 2025 EvoBandits
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

use crate::arm::{Arm, OptimizationFn};
use crate::genetic::GeneticAlgorithm;
use crate::sorted_multi_map::{FloatKey, SortedMultiMap};
use rand::prelude::SliceRandom;
use rand::rngs::StdRng;
use rand::{RngCore, SeedableRng};
use std::collections::HashMap;

#[derive(Debug, PartialEq, Clone)]
pub struct GMAB {
    sample_average_tree: SortedMultiMap<FloatKey, i32>,
    arm_memory: Vec<Arm>,
    lookup_table: HashMap<Vec<i32>, i32>,
    genetic_algorithm: GeneticAlgorithm,
}

impl GMAB {
    pub fn new(genetic_algorithm: GeneticAlgorithm) -> GMAB {
        let arm_memory: Vec<Arm> = Vec::new();
        let lookup_table: HashMap<Vec<i32>, i32> = HashMap::new();
        let sample_average_tree: SortedMultiMap<FloatKey, i32> = SortedMultiMap::new();

        GMAB {
            sample_average_tree,
            arm_memory,
            lookup_table,
            genetic_algorithm,
        }
    }

    fn get_arm_index(&self, individual: &Arm) -> i32 {
        match self
            .lookup_table
            .get(&individual.get_action_vector().to_vec())
        {
            Some(&index) => index,
            None => -1,
        }
    }

    fn max_number_pulls(&self) -> i32 {
        let mut max_number_pulls = 0;
        for arm in &self.arm_memory {
            if arm.get_n_evaluations() > max_number_pulls {
                max_number_pulls = arm.get_n_evaluations();
            }
        }
        max_number_pulls
    }

    fn find_best_ucb(&self, simulations_used: usize) -> i32 {
        let arm_index_ucb_norm_min: i32 = *self.sample_average_tree.iter().next().unwrap().1;
        let ucb_norm_min: f64 = self.arm_memory[arm_index_ucb_norm_min as usize].get_value();

        let max_number_pulls = self.max_number_pulls();

        let mut ucb_norm_max: f64 = ucb_norm_min;

        for (_ucb_norm, arm_index) in self.sample_average_tree.iter() {
            ucb_norm_max = f64::max(
                ucb_norm_max,
                self.arm_memory[*arm_index as usize].get_value(),
            );

            // checks if we are still in the non dominated-set (current mean <= mean_max_pulls)
            if self.arm_memory[*arm_index as usize].get_n_evaluations() == max_number_pulls {
                break;
            }
        }

        // find the solution of non-dominated set with the lowest associated UCB value
        let mut best_arm_index: i32 = 0;
        let mut best_ucb_value: f64 = f64::MAX;

        for (_ucb_norm, arm_index) in self.sample_average_tree.iter() {
            if ucb_norm_max == ucb_norm_min {
                best_arm_index = *arm_index;
            }

            // transform sample mean to interval [0,1]
            let transformed_sample_mean: f64 = (self.arm_memory[*arm_index as usize].get_value()
                - ucb_norm_min)
                / (ucb_norm_max - ucb_norm_min);
            let penalty_term: f64 = (2.0 * (simulations_used as f64).ln()
                / self.arm_memory[*arm_index as usize].get_n_evaluations() as f64)
                .sqrt();
            let ucb_value: f64 = transformed_sample_mean + penalty_term;

            // new best solution found
            if ucb_value < best_ucb_value {
                best_arm_index = *arm_index;
                best_ucb_value = ucb_value;
            }

            // checks if we are still in the non dominated-set (current mean <= mean_max_pulls)
            if self.arm_memory[*arm_index as usize].get_n_evaluations() == max_number_pulls {
                break;
            }
        }

        best_arm_index
    }

    fn sample_and_update<F: OptimizationFn>(
        &mut self,
        arm_index: i32,
        mut individual: Arm,
        opti_function: &F,
    ) {
        if arm_index >= 0 {
            self.sample_average_tree.delete(
                &FloatKey::new(self.arm_memory[arm_index as usize].get_value()),
                &arm_index,
            );
            self.arm_memory[arm_index as usize].pull(opti_function);
            self.sample_average_tree.insert(
                FloatKey::new(self.arm_memory[arm_index as usize].get_value()),
                arm_index,
            );
        } else {
            individual.pull(opti_function);
            self.arm_memory.push(individual.clone());
            self.lookup_table.insert(
                individual.get_action_vector().to_vec(),
                self.arm_memory.len() as i32 - 1,
            );
            self.sample_average_tree.insert(
                FloatKey::new(individual.get_value()),
                self.arm_memory.len() as i32 - 1,
            );
        }
    }

    fn initialize_population<F: OptimizationFn>(&mut self, seed: u64, opti_function: &F) {
        let mut initial_population = self.genetic_algorithm.generate_new_population(seed);

        for (index, individual) in initial_population.iter_mut().enumerate() {
            individual.pull(opti_function);
            self.arm_memory.push(individual.clone());
            self.lookup_table
                .insert(individual.get_action_vector().to_vec(), index as i32);
            self.sample_average_tree
                .insert(FloatKey::new(individual.get_value()), index as i32);
        }
    }

    fn extract_best_arms(&mut self, used_trials: usize, mut n_best: usize) -> Vec<Arm> {
        let mut best_arms: Vec<Arm> = Vec::new();
        while n_best > 0 {
            // Return early if there are no more arms to extract
            if self.sample_average_tree.is_empty() {
                println!(
                    "Population ({}) is smaller than n_best ({}). Returning all arms instead.",
                    best_arms.len(),
                    n_best
                );
                break;
            }

            // Find the next best arm, and remove it from SAT to continue extraction
            let best_arm_index = self.find_best_ucb(used_trials);
            let best_arm = self.arm_memory[best_arm_index as usize].clone();

            self.sample_average_tree
                .delete(&FloatKey::new(best_arm.get_value()), &best_arm_index);

            best_arms.push(best_arm);
            n_best -= 1;
        }

        best_arms
    }

    pub fn optimize<F: OptimizationFn>(
        &mut self,
        opti_function: F,
        bounds: Vec<(i32, i32)>,
        n_trials: usize,
        n_best: usize,
        seed: Option<u64>,
    ) -> Vec<Arm> {
        // Unwrap seed or fall back to system entropy
        let seed = seed.unwrap_or_else(|| rand::rng().next_u64());
        let mut rng: StdRng = SeedableRng::seed_from_u64(seed);

        // Set the bounds and check the algorithm configuration
        self.genetic_algorithm.set_bounds(bounds);
        self.genetic_algorithm.validate();

        assert!(
            n_trials >= self.genetic_algorithm.population_size,
            "n_trials must be at least population_size ({})",
            self.genetic_algorithm.population_size
        );
        assert!(n_best >= 1, "n_best must be at least 1. ({})", n_best);

        // Initialize the Population for the Optimization
        let next_seed = rng.next_u64();
        self.initialize_population(next_seed, &opti_function);

        // Run Optimization
        let verbose = false;
        let mut used_trials: usize = self.genetic_algorithm.population_size;
        loop {
            let mut current_indexes: Vec<i32> = Vec::new();
            let mut population: Vec<Arm> = Vec::new();

            // get first self.population_size elements from sorted tree and use value to get arm
            self.sample_average_tree
                .iter()
                .take(self.genetic_algorithm.population_size)
                .for_each(|(_key, arm_index)| {
                    population.push(self.arm_memory[*arm_index as usize].clone());
                    current_indexes.push(*arm_index);
                });

            // shuffle population
            population.shuffle(&mut rng);

            let next_seed = rng.next_u64();
            let crossover_pop = self.genetic_algorithm.crossover(next_seed, &population);

            // mutate automatically removes duplicates
            let next_seed = rng.next_u64();
            let mutated_pop = self.genetic_algorithm.mutate(next_seed, &crossover_pop);

            for individual in mutated_pop {
                if used_trials >= n_trials {
                    return self.extract_best_arms(used_trials, n_best);
                }

                let arm_index = self.get_arm_index(&individual);

                // check if arm is in current population
                if current_indexes.contains(&arm_index) {
                    continue;
                }

                self.sample_and_update(arm_index, individual.clone(), &opti_function);
                used_trials += 1;
            }

            for individual in population {
                if used_trials >= n_trials {
                    return self.extract_best_arms(used_trials, n_best);
                }

                let arm_index = self.get_arm_index(&individual);
                self.sample_and_update(arm_index, individual.clone(), &opti_function);
                used_trials += 1;
            }

            if verbose {
                let best_arm_index = self.find_best_ucb(used_trials);
                print!(
                    "x: {:?}",
                    self.arm_memory[best_arm_index as usize].get_action_vector()
                );
                // get averaged function value over 50 simulations
                let mut sum = 0.0;
                for _ in 0..50 {
                    sum +=
                        self.arm_memory[best_arm_index as usize].get_function_value(&opti_function);
                }
                print!(" f(x): {:.3}", sum / 50.0);

                print!(" n: {}", used_trials);
                // print number of pulls of best arm
                println!(
                    " n(x): {}",
                    self.arm_memory[best_arm_index as usize].get_n_evaluations()
                );
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::RefCell;

    fn mock_opti_function(_vec: &[i32]) -> f64 {
        0.0
    }

    #[test]
    fn test_gmab_new() {
        let ga = GeneticAlgorithm {
            population_size: 10,
            mutation_rate: 0.5,
            crossover_rate: 0.9,
            mutation_span: 0.1,
            dimension: 2,
            lower_bound: vec![0, 0],
            upper_bound: vec![10, 10],
        };
        let mut gmab = GMAB::new(ga);
        gmab.initialize_population(0, &mock_opti_function);

        assert_eq!(gmab.genetic_algorithm.population_size, 10);
        assert_eq!(gmab.arm_memory.len(), 10);
        assert_eq!(gmab.lookup_table.len(), 10);

        // check if there are 10  elements in sample_average_tree
        let mut count = 0;
        for _ in gmab.sample_average_tree.iter() {
            count += 1;
        }
        assert_eq!(count, 10);
    }

    #[test]
    fn test_gmab_get_arm_index_with_existing() {
        let ga = GeneticAlgorithm {
            population_size: 10,
            mutation_rate: 0.5,
            crossover_rate: 0.9,
            mutation_span: 0.1,
            dimension: 2,
            lower_bound: vec![0, 0],
            upper_bound: vec![10, 10],
        };
        let mut gmab = GMAB::new(ga);
        let arm = Arm::new(&vec![1, 2]);
        gmab.arm_memory.push(arm.clone());
        gmab.lookup_table
            .insert(arm.get_action_vector().to_vec(), 0);
        assert_eq!(gmab.get_arm_index(&arm), 0);
    }

    #[test]
    fn test_gmab_max_number_pulls() {
        let ga = GeneticAlgorithm {
            population_size: 10,
            mutation_rate: 0.5,
            crossover_rate: 0.9,
            mutation_span: 0.1,
            dimension: 2,
            lower_bound: vec![0, 0],
            upper_bound: vec![10, 10],
        };
        let mut gmab = GMAB::new(ga);
        gmab.initialize_population(0, &mock_opti_function);
        assert_eq!(gmab.max_number_pulls(), 1);
    }

    #[test]
    fn test_gmab_find_best_ucb() {
        let ga = GeneticAlgorithm {
            population_size: 10,
            mutation_rate: 0.5,
            crossover_rate: 0.9,
            mutation_span: 0.1,
            dimension: 2,
            lower_bound: vec![0, 0],
            upper_bound: vec![10, 10],
        };
        let mut gmab = GMAB::new(ga);
        gmab.initialize_population(0, &mock_opti_function);
        assert_eq!(gmab.find_best_ucb(100), 0);
    }

    #[test]
    fn test_gmab_find_best_ucb_with_existing() {
        let ga = GeneticAlgorithm {
            population_size: 10,
            mutation_rate: 0.5,
            crossover_rate: 0.9,
            mutation_span: 0.1,
            dimension: 2,
            lower_bound: vec![0, 0],
            upper_bound: vec![10, 10],
        };
        let mut gmab = GMAB::new(ga);

        let arm = Arm::new(&vec![1, 2]);
        gmab.arm_memory.push(arm.clone());
        gmab.lookup_table
            .insert(arm.get_action_vector().to_vec(), 0);

        let arm2 = Arm::new(&vec![1, 2]);
        gmab.arm_memory.push(arm2.clone());
        gmab.lookup_table
            .insert(arm2.get_action_vector().to_vec(), 1);

        gmab.sample_and_update(0, arm.clone(), &mock_opti_function);
        gmab.sample_and_update(1, arm2.clone(), &mock_opti_function);

        assert_eq!(gmab.find_best_ucb(100), 0);
    }

    #[test]
    fn test_gmab_sample_and_update_with_existing() {
        let ga = GeneticAlgorithm {
            population_size: 10,
            mutation_rate: 0.5,
            crossover_rate: 0.9,
            mutation_span: 0.1,
            dimension: 2,
            lower_bound: vec![0, 0],
            upper_bound: vec![10, 10],
        };
        let mut gmab = GMAB::new(ga);
        gmab.initialize_population(0, &mock_opti_function);

        let arm = Arm::new(&vec![1, 2]);
        gmab.arm_memory.push(arm.clone());
        gmab.lookup_table
            .insert(arm.get_action_vector().to_vec(), 0);

        gmab.sample_and_update(0, arm.clone(), &mock_opti_function);

        assert_eq!(gmab.arm_memory[0].get_n_evaluations(), 2);
        assert_eq!(gmab.arm_memory[0].get_value(), 0.0);
        assert_eq!(
            gmab.lookup_table.get(&arm.get_action_vector().to_vec()),
            Some(&0)
        );
    }

    #[test]
    fn test_reproduction_with_seeding() {
        // Mock the optimization function
        fn mock_opti_function(vec: &[i32]) -> f64 {
            vec.iter().map(|&x| x as f64).sum()
        }

        // Helper function that generates a result based on a specific seed.
        fn generate_result(seed: Option<u64>) -> Vec<i32> {
            let bounds = vec![(1, 100), (1, 100)];
            let mut gmab = GMAB::new(Default::default());
            let result = gmab.optimize(mock_opti_function, bounds, 100, 1, seed);
            return result[0].get_action_vector().to_vec();
        }

        // The same seed should lead to the same result
        let seed = 42;
        assert_eq!(generate_result(Some(seed)), generate_result(Some(seed)));

        // A different seed should not lead to the same result
        assert_ne!(generate_result(Some(seed)), generate_result(Some(seed + 1)));
    }

    #[test]
    #[should_panic = "population_size"]
    fn test_panic_on_invalid_options() {
        // Mock bounds for testing
        let bounds = vec![(1, 100), (1, 100)];

        // Construct invalid GA (with population size 0)
        let ga = GeneticAlgorithm {
            population_size: 0,
            ..Default::default()
        };

        // Panics only, if validation from GmabOptions is integrated
        let mut gmab = GMAB::new(ga);
        gmab.optimize(mock_opti_function, bounds, 1, 1, None);
    }

    #[test]
    fn test_gmab_adheres_to_n_trials() {
        // Mock opti_function that keeps track of used simulations
        let used_trials = RefCell::new(0);
        let mock_opti_function = |_: &[i32]| {
            *used_trials.borrow_mut() += 1;
            0.0
        };

        // Run the optimization, then check if used_trials matches n_trials
        let n_trials = 1000;
        let bounds = vec![(1, 100), (1, 100)];
        let mut gmab = GMAB::new(Default::default());
        gmab.optimize(mock_opti_function, bounds, n_trials, 1, None);

        assert_eq!(n_trials, *used_trials.borrow_mut());
    }

    #[test]
    #[should_panic = "n_trials"]
    fn test_panic_on_invalid_n_trials() {
        // Explicity set a simulation n_trials that prohibits sampling an initial population
        let n_trials = 20;
        let ga = GeneticAlgorithm {
            population_size: n_trials + 1,
            ..Default::default()
        };

        // Panics only, if n_trials is validated
        let bounds = vec![(1, 100), (1, 100)];
        let mut gmab = GMAB::new(ga);
        gmab.optimize(mock_opti_function, bounds, n_trials, 1, None);
    }

    #[test]
    #[should_panic = "n_best"]
    fn test_panic_on_invalid_n_best() {
        let n_best = 0; // top 0 results makes no sense, but fits in usize
        let bounds = vec![(1, 100), (1, 100)];
        let mut gmab = GMAB::new(Default::default());
        gmab.optimize(mock_opti_function, bounds, 20, n_best, None);
    }

    #[test]
    fn test_gmab_extract_n_best_arms() {
        // Mock a GMAB instance with 20 unique arms (distinct action vector and reward, one pull each)
        fn mock_opti_function(vec: &[i32]) -> f64 {
            vec.iter()
                .enumerate()
                .map(|(i, &x)| (x as f64) * 10f64.powi(i as i32))
                .sum()
        }

        let population_size = 20;
        let ga = GeneticAlgorithm {
            population_size: population_size,
            dimension: 3,
            lower_bound: vec![0, 0, 0],
            upper_bound: vec![9, 9, 9],
            ..Default::default()
        };
        let mut gmab = GMAB::new(ga);
        gmab.initialize_population(0, &mock_opti_function);

        // Copy and sort all arms
        let mut sorted_arms = gmab.arm_memory.clone();
        sorted_arms.sort_by(|a, b| a.get_value().partial_cmp(&b.get_value()).unwrap());

        // Get n_best arms
        let n_best = 3;
        let best_arms = gmab.extract_best_arms(population_size, n_best);

        // Ensure the number of best arms returned matches n_best
        assert_eq!(best_arms.len(), n_best);

        // Ensure the best arms match the ones with the lowest reward.
        for i in 0..n_best {
            assert_eq!(
                best_arms[i].get_action_vector(),
                sorted_arms[i].get_action_vector()
            );
        }
    }

    #[test]
    fn test_gmab_extract_all_arms() {
        // Mock a GMAB instance with 20 unique arms (distinct action vector and reward, one pull each)
        fn mock_opti_function(vec: &[i32]) -> f64 {
            vec.iter()
                .enumerate()
                .map(|(i, &x)| (x as f64) * 10f64.powi(i as i32))
                .sum()
        }

        let population_size = 20;
        let ga = GeneticAlgorithm {
            population_size: population_size,
            dimension: 3,
            lower_bound: vec![0, 0, 0],
            upper_bound: vec![9, 9, 9],
            ..Default::default()
        };
        let mut gmab = GMAB::new(ga);
        gmab.initialize_population(0, &mock_opti_function);

        // Copy and sort all arms
        let mut sorted_arms = gmab.arm_memory.clone();
        sorted_arms.sort_by(|a, b| a.get_value().partial_cmp(&b.get_value()).unwrap());

        // Try to get more best arms than available
        let n_best = population_size + 1;
        let best_arms = gmab.extract_best_arms(population_size, n_best);

        // Ensure the number of best arms returned matches the population size
        assert_eq!(best_arms.len(), sorted_arms.len());
    }
}
