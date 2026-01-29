use pyo3::prelude::*;

fn sturges(n: usize) -> usize {
    if n <= 1 {
        return 1;
    }
    (1.0 + 3.322 * (n as f64).log10()).round() as usize
}

fn compute_intervals(data: &[f64]) -> Vec<(f64, f64)> {
    if data.is_empty() {
        return Vec::new();
    }
    
    let min_val = data.iter().fold(f64::INFINITY, |acc, &x| acc.min(x));
    let max_val = data.iter().fold(f64::NEG_INFINITY, |acc, &x| acc.max(x));

    if min_val == max_val {
        return vec![(min_val, max_val)];
    }

    let k = sturges(data.len());
    let group_width = (max_val - min_val) / k as f64;

    let mut intervals = Vec::with_capacity(k);

    for i in 0..k {
        let start = min_val + i as f64 * group_width;
        
        let end = if i == k - 1 {
            max_val
        } else {
            min_val + (i + 1) as f64 * group_width
        };
        intervals.push((start, end));
    }
    intervals
}

fn count_frequencies(data: &[f64], intervals: &[(f64, f64)]) -> Vec<usize> {
    if intervals.is_empty() {
        return Vec::new();
    }
    
    let mut freqs = vec![0; intervals.len()];
    let last_index = intervals.len() - 1;

    for &value in data {
        let mut assigned = false;
        for (i, &(start, end)) in intervals.iter().enumerate() {
            if (i != last_index && value >= start && value < end) ||
               (i == last_index && value >= start && value <= end) {
                freqs[i] += 1;
                assigned = true;
                break;
            }
        }
        if !assigned {
            for (i, &(start, end)) in intervals.iter().enumerate() {
                if value >= start && value <= end {
                    freqs[i] += 1;
                    break;
                }
            }
        }
    }
    freqs
}

fn compute_xi(intervals: &[(f64, f64)]) -> Vec<f64> {
    intervals
        .iter()
        .map(|&(start, end)| (start + end) / 2.0)
        .collect()
}

fn compute_si(freqs: &[usize]) -> Vec<usize> {
    freqs.iter()
        .scan(0, |acc, &freq| {
            *acc += freq;
            Some(*acc)
        })
        .collect()
}

fn compute_xi_ni(xi: &[f64], ni: &[usize]) -> Vec<f64> {
    xi.iter()
        .zip(ni.iter())
        .map(|(&x, &n)| x * n as f64)
        .collect()
}

fn compute_mean(xi_ni: &[f64], total_n: usize) -> f64 {
    if total_n == 0 {
        return 0.0;
    }
    let sum_xi_ni: f64 = xi_ni.iter().sum();
    sum_xi_ni / total_n as f64
}

fn compute_xi_minus_mean(xi: &[f64], mean: f64) -> Vec<f64> {
    xi.iter()
        .map(|&x| x - mean)
        .collect()
}

fn compute_abs_xi_minus_mean_ni(xi_minus_mean: &[f64], ni: &[usize]) -> Vec<f64> {
    xi_minus_mean.iter()
        .zip(ni.iter())
        .map(|(&diff, &n)| diff.abs() * n as f64)
        .collect()
}

fn compute_squared_xi_minus_mean_ni(xi_minus_mean: &[f64], ni: &[usize]) -> Vec<f64> {
    xi_minus_mean.iter()
        .zip(ni.iter())
        .map(|(&diff, &n)| diff.powi(2) * n as f64)
        .collect()
}

fn compute_cubed_xi_minus_mean_ni(xi_minus_mean: &[f64], ni: &[usize]) -> Vec<f64> {
    xi_minus_mean.iter()
        .zip(ni.iter())
        .map(|(&diff, &n)| diff.powi(3) * n as f64)
        .collect()
}

fn compute_fourth_power_xi_minus_mean_ni(xi_minus_mean: &[f64], ni: &[usize]) -> Vec<f64> {
    xi_minus_mean.iter()
        .zip(ni.iter())
        .map(|(&diff, &n)| diff.powi(4) * n as f64)
        .collect()
}

fn sum_ni(ni: &[usize]) -> usize {
    ni.iter().sum()
}

fn sum_xi_ni(xi_ni: &[f64]) -> f64 {
    xi_ni.iter().sum()
}

fn sum_abs_xi_minus_mean_ni(abs_xi_minus_mean_ni: &[f64]) -> f64 {
    abs_xi_minus_mean_ni.iter().sum()
}

fn sum_squared_xi_minus_mean_ni(squared_xi_minus_mean_ni: &[f64]) -> f64 {
    squared_xi_minus_mean_ni.iter().sum()
}

fn sum_cubed_xi_minus_mean_ni(cubed_xi_minus_mean_ni: &[f64]) -> f64 {
    cubed_xi_minus_mean_ni.iter().sum()
}

fn sum_fourth_power_xi_minus_mean_ni(fourth_power_xi_minus_mean_ni: &[f64]) -> f64 {
    fourth_power_xi_minus_mean_ni.iter().sum()
}

fn compute_variance(sum_squared: f64, total_n: usize) -> f64 {
    if total_n == 0 {
        return 0.0;
    }
    sum_squared / total_n as f64
}

fn compute_std(variance: f64) -> f64 {
    variance.sqrt()
}

fn compute_mean_linear_deviation(sum_abs: f64, total_n: usize) -> f64 {
    if total_n == 0 {
        return 0.0;
    }
    sum_abs / total_n as f64
}

fn compute_variation_coefficient(std: f64, mean: f64) -> f64 {
    if mean == 0.0 {
        0.0
    } else {
        (std / mean) * 100.0
    }
}

fn compute_asymmetry(sum_cubed: f64, total_n: usize, std: f64) -> f64 {
    if total_n == 0 || std == 0.0 {
        0.0
    } else {
        sum_cubed / (total_n as f64 * std.powi(3))
    }
}

fn compute_excess(sum_fourth: f64, total_n: usize, variance: f64) -> f64 {
    if total_n == 0 || variance == 0.0 {
        0.0
    } else {
        sum_fourth / (total_n as f64 * variance.powi(2)) - 3.0
    }
}

fn calculate_medians(intervals: &[(f64, f64)], ni: &[usize], si: &[usize]) -> Vec<f64> {
    let mut medians = Vec::new();
    let total_n: usize = ni.iter().sum();
    
    if total_n == 0 || intervals.is_empty() {
        return medians;
    }
    
    for i in 0..intervals.len() {
        let (lower, upper) = intervals[i];
        let freq = ni[i] as f64;
        
        let accum_before = if i == 0 { 0.0 } else { si[i-1] as f64 };
        
        let median = if freq > 0.0 {
            let h = upper - lower;
            lower + ((total_n as f64 / 2.0 - accum_before) / freq) * h
        } else {
            (lower + upper) / 2.0
        };
        
        medians.push(median);
    }
    
    medians
}

fn calculate_modes(intervals: &[(f64, f64)], ni: &[usize]) -> Vec<f64> {
    let mut modes = Vec::new();
    
    if intervals.is_empty() {
        return modes;
    }
    
    for i in 0..intervals.len() {
        let (lower, upper) = intervals[i];
        let freq = ni[i] as f64;
        
        let freq_prev = if i > 0 { ni[i-1] as f64 } else { 0.0 };
        let freq_next = if i < ni.len()-1 { ni[i+1] as f64 } else { 0.0 };
        
        let delta1 = freq - freq_prev;
        let delta2 = freq - freq_next;
        
        let mode = if delta1 + delta2 > 0.0 {
            let h = upper - lower;
            lower + (delta1 / (delta1 + delta2)) * h
        } else {
            (lower + upper) / 2.0
        };
        
        modes.push(mode);
    }
    
    modes
}

#[pyclass]
struct GroupStatsResult {
    intervals: Vec<(f64, f64)>,
    ni: Vec<usize>,
    xi: Vec<f64>,
    si: Vec<usize>,
    xi_ni: Vec<f64>,
    xi_minus_mean: Vec<f64>,
    abs_xi_minus_mean_ni: Vec<f64>,
    squared_xi_minus_mean_ni: Vec<f64>,
    cubed_xi_minus_mean_ni: Vec<f64>,
    fourth_power_xi_minus_mean_ni: Vec<f64>,
    sum_ni: f64,
    sum_xi_ni: f64,
    sum_abs: f64,
    sum_squared: f64,
    sum_cubed: f64,
    sum_fourth: f64,
    mean: f64,
    variance: f64,
    std: f64,
    mean_linear_dev: f64,
    variation_coef: f64,
    asymmetry: f64,
    excess: f64,
    medians: Vec<f64>,
    modes: Vec<f64>,
    midpoints: Vec<f64>,
    accumulated_frequencies: Vec<f64>,
}

#[pymethods]
impl GroupStatsResult {
    #[getter]
    fn intervals(&self) -> Vec<(f64, f64)> {
        self.intervals.clone()
    }
    
    #[getter]
    fn ni(&self) -> Vec<usize> {
        self.ni.clone()
    }
    
    #[getter]
    fn xi(&self) -> Vec<f64> {
        self.xi.clone()
    }
    
    #[getter]
    fn si(&self) -> Vec<usize> {
        self.si.clone()
    }
    
    #[getter]
    fn xi_ni(&self) -> Vec<f64> {
        self.xi_ni.clone()
    }
    
    #[getter]
    fn xi_minus_mean(&self) -> Vec<f64> {
        self.xi_minus_mean.clone()
    }
    
    #[getter]
    fn abs_xi_minus_mean_ni(&self) -> Vec<f64> {
        self.abs_xi_minus_mean_ni.clone()
    }
    
    #[getter]
    fn squared_xi_minus_mean_ni(&self) -> Vec<f64> {
        self.squared_xi_minus_mean_ni.clone()
    }
    
    #[getter]
    fn cubed_xi_minus_mean_ni(&self) -> Vec<f64> {
        self.cubed_xi_minus_mean_ni.clone()
    }
    
    #[getter]
    fn fourth_power_xi_minus_mean_ni(&self) -> Vec<f64> {
        self.fourth_power_xi_minus_mean_ni.clone()
    }
    
    #[getter]
    fn sum_ni(&self) -> f64 {
        self.sum_ni
    }
    
    #[getter]
    fn sum_xi_ni(&self) -> f64 {
        self.sum_xi_ni
    }
    
    #[getter]
    fn sum_abs(&self) -> f64 {
        self.sum_abs
    }
    
    #[getter]
    fn sum_squared(&self) -> f64 {
        self.sum_squared
    }
    
    #[getter]
    fn sum_cubed(&self) -> f64 {
        self.sum_cubed
    }
    
    #[getter]
    fn sum_fourth(&self) -> f64 {
        self.sum_fourth
    }
    
    #[getter]
    fn mean(&self) -> f64 {
        self.mean
    }
    
    #[getter]
    fn variance(&self) -> f64 {
        self.variance
    }
    
    #[getter]
    fn std(&self) -> f64 {
        self.std
    }
    
    #[getter]
    fn mean_linear_dev(&self) -> f64 {
        self.mean_linear_dev
    }
    
    #[getter]
    fn variation_coef(&self) -> f64 {
        self.variation_coef
    }
    
    #[getter]
    fn asymmetry(&self) -> f64 {
        self.asymmetry
    }
    
    #[getter]
    fn excess(&self) -> f64 {
        self.excess
    }
    
    #[getter]
    fn medians(&self) -> Vec<f64> {
        self.medians.clone()
    }
    
    #[getter]
    fn modes(&self) -> Vec<f64> {
        self.modes.clone()
    }
    
    #[getter]
    fn midpoints(&self) -> Vec<f64> {
        self.midpoints.clone()
    }
    
    #[getter]
    fn accumulated_frequencies(&self) -> Vec<f64> {
        self.accumulated_frequencies.clone()
    }
}

#[pyfunction]
fn group_stats(data: Vec<f64>) -> PyResult<GroupStatsResult> {
    let total_n = data.len();

    let intervals = compute_intervals(&data);
    let ni = count_frequencies(&data, &intervals);
    let xi = compute_xi(&intervals);
    let si = compute_si(&ni);
    
    let accumulated_frequencies: Vec<f64> = si.iter().map(|&x| x as f64).collect();
    let medians = calculate_medians(&intervals, &ni, &si);
    let modes = calculate_modes(&intervals, &ni);
    
    let xi_ni = compute_xi_ni(&xi, &ni);
    let mean = compute_mean(&xi_ni, total_n);
    let xi_minus_mean = compute_xi_minus_mean(&xi, mean);
    let abs_xi_minus_mean_ni = compute_abs_xi_minus_mean_ni(&xi_minus_mean, &ni);
    let squared_xi_minus_mean_ni = compute_squared_xi_minus_mean_ni(&xi_minus_mean, &ni);
    let cubed_xi_minus_mean_ni = compute_cubed_xi_minus_mean_ni(&xi_minus_mean, &ni);
    let fourth_power_xi_minus_mean_ni = compute_fourth_power_xi_minus_mean_ni(&xi_minus_mean, &ni);
    
    // Calculate sums
    let sum_ni_val = sum_ni(&ni) as f64;
    let sum_xi_ni_val = sum_xi_ni(&xi_ni);
    let sum_abs_val = sum_abs_xi_minus_mean_ni(&abs_xi_minus_mean_ni);
    let sum_squared_val = sum_squared_xi_minus_mean_ni(&squared_xi_minus_mean_ni);
    let sum_cubed_val = sum_cubed_xi_minus_mean_ni(&cubed_xi_minus_mean_ni);
    let sum_fourth_val = sum_fourth_power_xi_minus_mean_ni(&fourth_power_xi_minus_mean_ni);
    
    // Calculate statistics
    let variance = compute_variance(sum_squared_val, total_n);
    let std = compute_std(variance);
    let mean_linear_dev = compute_mean_linear_deviation(sum_abs_val, total_n);
    let variation_coef = compute_variation_coefficient(std, mean);
    let asymmetry = compute_asymmetry(sum_cubed_val, total_n, std);
    let excess = compute_excess(sum_fourth_val, total_n, variance);

    Ok(GroupStatsResult {
        intervals,
        ni,
        xi: xi.clone(),
        si,
        xi_ni,
        xi_minus_mean,
        abs_xi_minus_mean_ni,
        squared_xi_minus_mean_ni,
        cubed_xi_minus_mean_ni,
        fourth_power_xi_minus_mean_ni,
        sum_ni: sum_ni_val,
        sum_xi_ni: sum_xi_ni_val,
        sum_abs: sum_abs_val,
        sum_squared: sum_squared_val,
        sum_cubed: sum_cubed_val,
        sum_fourth: sum_fourth_val,
        mean,
        variance,
        std,
        mean_linear_dev,
        variation_coef,
        asymmetry,
        excess,
        medians,
        modes,
        midpoints: xi,
        accumulated_frequencies,
    })
}

#[pymodule]
fn rust_stats(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<GroupStatsResult>()?;
    m.add_function(wrap_pyfunction!(group_stats, m)?)?;
    Ok(())
}