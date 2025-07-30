import numpy as np
import pandas as pd
from scipy import stats
from typing import List, Union, Dict, Any


def robust_average(prices: Union[List[float], pd.Series], return_all_stats: bool = False) -> Dict[str, Any]:
    """
    Selects the most robust average (mean, median, or mode) for a list/Series of prices,
    based on outlier and skewness analysis.

    Parameters:
        prices (list or pd.Series): List or Series of numeric prices.
        return_all_stats (bool): If True, returns all computed statistics.

    Returns:
        dict: {
            'value': selected average value,
            'method': 'mean' | 'median' | 'mode',
            'mean': mean,
            'median': median,
            'mode': mode (or None),
            'std': standard deviation,
            'skew': skewness,
            'outliers': list of outlier values,
            ...
        }
    """
    # Convert to Series for convenience
    prices = pd.Series(prices).dropna()
    if prices.empty:
        raise ValueError("No valid prices provided.")

    mean = prices.mean()
    median = prices.median()
    mode = prices.mode().iloc[0] if not prices.mode().empty else None
    std = prices.std()
    skew = stats.skew(prices)

    # Outlier detection using IQR
    q1 = prices.quantile(0.25)
    q3 = prices.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = prices[(prices < lower_bound) | (prices > upper_bound)].tolist()

    # Decision logic
    if len(outliers) == 0 and abs(skew) < 0.5:
        selected_value = mean
        method = 'mean'
    elif len(outliers) > 0 or abs(skew) >= 0.5:
        selected_value = median
        method = 'median'
    elif mode is not None and (prices == mode).sum() > len(prices) // 2:
        selected_value = mode
        method = 'mode'
    else:
        selected_value = mean
        method = 'mean'

    result = {
        'value': selected_value,
        'method': method,
        'mean': mean,
        'median': median,
        'mode': mode,
        'std': std,
        'skew': skew,
        'outliers': outliers,
        'count': len(prices)
    }
    if return_all_stats:
        result['all_prices'] = prices.tolist()
    return result 