use pyo3::prelude::*;

mod indicators;

use indicators::*;

/// A Python module implemented in Rust.
#[pymodule]
fn jesse_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    // Indicators
    m.add_function(wrap_pyfunction!(rsi, m)?)?;
    m.add_function(wrap_pyfunction!(kama, m)?)?;
    m.add_function(wrap_pyfunction!(ichimoku_cloud, m)?)?;
    m.add_function(wrap_pyfunction!(srsi, m)?)?;
    m.add_function(wrap_pyfunction!(adx, m)?)?;
    m.add_function(wrap_pyfunction!(tema, m)?)?;
    m.add_function(wrap_pyfunction!(macd, m)?)?;
    m.add_function(wrap_pyfunction!(bollinger_bands_width, m)?)?;
    m.add_function(wrap_pyfunction!(bollinger_bands, m)?)?;
    
    // Utility functions (now in indicators.rs)
    m.add_function(wrap_pyfunction!(shift, m)?)?;
    m.add_function(wrap_pyfunction!(moving_std, m)?)?;
    m.add_function(wrap_pyfunction!(sma, m)?)?;
    m.add_function(wrap_pyfunction!(smma, m)?)?;
    m.add_function(wrap_pyfunction!(alligator, m)?)?;
    m.add_function(wrap_pyfunction!(di, m)?)?;
    m.add_function(wrap_pyfunction!(chop, m)?)?;
    m.add_function(wrap_pyfunction!(atr, m)?)?;
    m.add_function(wrap_pyfunction!(indicators::chande, m)?)?;
    m.add_function(wrap_pyfunction!(indicators::donchian, m)?)?;
    
    // New optimized indicators
    m.add_function(wrap_pyfunction!(willr, m)?)?;
    m.add_function(wrap_pyfunction!(wma, m)?)?;
    m.add_function(wrap_pyfunction!(vwma, m)?)?;
    
    // Performance optimized indicators
    m.add_function(wrap_pyfunction!(stoch, m)?)?;
    m.add_function(wrap_pyfunction!(stochf, m)?)?;
    m.add_function(wrap_pyfunction!(dm, m)?)?;
    m.add_function(wrap_pyfunction!(dema, m)?)?;
    
    Ok(())
}
