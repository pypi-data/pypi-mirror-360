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

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::panic;

use evobandits_rust::arm::{Arm as RustArm, OptimizationFn};
use evobandits_rust::evobandits::GMAB as RustGMAB;
use evobandits_rust::genetic::{
    GeneticAlgorithm, CROSSOVER_RATE_DEFAULT, MUTATION_RATE_DEFAULT, MUTATION_SPAN_DEFAULT,
    POPULATION_SIZE_DEFAULT,
};

struct PythonOptimizationFn {
    py_func: PyObject,
}

impl PythonOptimizationFn {
    fn new(py_func: PyObject) -> Self {
        Self { py_func }
    }
}

impl OptimizationFn for PythonOptimizationFn {
    fn evaluate(&self, action_vector: &[i32]) -> f64 {
        Python::with_gil(|py| {
            let py_list = PyList::new(py, action_vector);
            let result = self
                .py_func
                .call1(py, (py_list.unwrap(),))
                .expect("Failed to call Python function");
            result.extract::<f64>(py).expect("Failed to extract f64")
        })
    }
}

#[pyclass]
struct Arm {
    arm: RustArm,
}

#[pymethods]
impl Arm {
    #[new]
    fn new(action_vector: Vec<i32>) -> PyResult<Self> {
        let arm = RustArm::new(&action_vector);
        Ok(Arm { arm })
    }

    #[getter]
    fn n_evaluations(&self) -> i32 {
        self.arm.get_n_evaluations()
    }

    #[getter]
    fn value(&self) -> f64 {
        self.arm.get_value()
    }

    #[getter]
    fn value_std_dev(&self) -> f64 {
        self.arm.get_value_std_dev()
    }

    #[getter]
    fn action_vector(&self) -> Vec<i32> {
        self.arm.get_action_vector().to_vec()
    }

    #[getter]
    fn to_dict(&self, py: Python) -> Py<PyDict> {
        let dict = PyDict::new(py);
        dict.set_item("action_vector", self.arm.get_action_vector().to_vec())
            .unwrap();
        dict.set_item("value", self.arm.get_value()).unwrap();
        dict.set_item("value_std_dev", self.arm.get_value_std_dev())
            .unwrap();
        dict.set_item("n_evaluations", self.arm.get_n_evaluations())
            .unwrap();
        dict.into()
    }
}

// Wraps a RustArm as python-compatible Arm instance.
// Required, since RustArm isn't a #[pyclass] and we want to keep evobandits as clean rust crate.
impl From<RustArm> for Arm {
    fn from(arm: RustArm) -> Self {
        Arm { arm }
    }
}

#[pyclass(eq)]
#[derive(Debug, PartialEq, Clone)]
struct GMAB {
    gmab: RustGMAB,
}

#[pymethods]
impl GMAB {
    #[new]
    #[pyo3(signature = (
        population_size=POPULATION_SIZE_DEFAULT,
        mutation_rate=MUTATION_RATE_DEFAULT,
        crossover_rate=CROSSOVER_RATE_DEFAULT,
        mutation_span=MUTATION_SPAN_DEFAULT,
    ))]
    fn new(
        population_size: Option<usize>,
        mutation_rate: Option<f64>,
        crossover_rate: Option<f64>,
        mutation_span: Option<f64>,
    ) -> PyResult<Self> {
        let genetic_algorithm = GeneticAlgorithm {
            population_size: population_size.unwrap(),
            mutation_rate: mutation_rate.unwrap(),
            crossover_rate: crossover_rate.unwrap(),
            mutation_span: mutation_span.unwrap(),
            ..Default::default()
        };
        let gmab = RustGMAB::new(genetic_algorithm);
        Ok(GMAB { gmab })
    }

    #[pyo3(signature = (
        py_func,
        bounds,
        n_trials,
        n_best,
        seed=None,
    ))]
    fn optimize(
        &mut self,
        py_func: PyObject,
        bounds: Vec<(i32, i32)>,
        n_trials: usize,
        n_best: usize,
        seed: Option<u64>,
    ) -> PyResult<Vec<Arm>> {
        let py_opti_function = PythonOptimizationFn::new(py_func);

        let result = panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            self.gmab
                .optimize(py_opti_function, bounds, n_trials, n_best, seed)
        }));

        match result {
            // Convert rust-only Vec<RustArm> into Python-compatible Vec<Arm> wrappers,
            // so PyO3 can safely return them across the FFI boundary.
            Ok(result) => {
                let py_result: Vec<Arm> = result.into_iter().map(Arm::from).collect();
                Ok(py_result)
            }
            Err(err) => {
                if let Some(s) = err.downcast_ref::<&str>() {
                    Err(PyRuntimeError::new_err(format!("{}", s)))
                } else if let Some(s) = err.downcast_ref::<String>() {
                    Err(PyRuntimeError::new_err(format!("{}", s)))
                } else {
                    Err(PyRuntimeError::new_err(
                        "EvoBandits Core raised an Error with unknown cause.",
                    ))
                }
            }
        }
    }

    fn clone(&self) -> PyResult<Self> {
        let gmab = self.gmab.clone(); // Uses the derived clone() from Clone trait
        Ok(GMAB { gmab })
    }
}

#[pymodule]
fn evobandits(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<GMAB>()?;
    m.add_class::<Arm>()?;

    m.add("POPULATION_SIZE_DEFAULT", POPULATION_SIZE_DEFAULT)?;
    m.add("MUTATION_RATE_DEFAULT", MUTATION_RATE_DEFAULT)?;
    m.add("CROSSOVER_RATE_DEFAULT", CROSSOVER_RATE_DEFAULT)?;
    m.add("MUTATION_SPAN_DEFAULT", MUTATION_SPAN_DEFAULT)?;

    Ok(())
}
