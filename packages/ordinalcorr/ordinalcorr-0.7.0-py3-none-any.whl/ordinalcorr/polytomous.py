import warnings
import numpy as np
from scipy.stats import norm, multivariate_normal
from scipy.optimize import minimize_scalar
from ordinalcorr.validation import (
    ValidationError,
    check_if_zero_variance,
    check_length_are_same,
)
from ordinalcorr.types import ArrayLike


def univariate_cdf(lower, upper):
    """Compute the univariate cumulative distribution function (CDF) for a standard normal distribution.

    P(lower < X <= upper) = Φ(upper) - Φ(lower)

    where Φ is the CDF of the standard normal distribution.
    """
    mean = 0.0
    var = 1.0
    std = np.sqrt(var)
    return norm.cdf(upper, loc=mean, scale=std) - norm.cdf(lower, loc=mean, scale=std)


def bivariate_cdf(lower, upper, rho: float) -> float:
    """Compute the bivariate cumulative distribution function (CDF) for a standard normal distribution.

    P(lower_x < X <= upper_x, lower_y < Y <= upper_y)
        = Φ₂(upper_x, upper_y) - Φ₂(lower_x, upper_y) - Φ₂(upper_x, lower_y) + Φ₂(lower_x, lower_y)

    where Φ₂ is the CDF of the bivariate normal distribution with correlation coefficient ρ.
    """
    var = 1
    cov = np.array([[var, rho], [rho, var]])
    Phi2 = multivariate_normal(mean=[0, 0], cov=cov, allow_singular=True).cdf
    return (
        Phi2(upper)
        - Phi2([upper[0], lower[1]])
        - Phi2([lower[0], upper[1]])
        + Phi2(lower)
    )


def estimate_thresholds(values):
    """Estimate thresholds from empirical marginal proportions"""
    inf = 100  # to make log-likelihood smooth, use large value instead of np.inf
    thresholds = []
    levels = np.sort(np.unique(values))
    for level in levels[:-1]:  # exclude top category
        p = np.mean(values <= level)
        thresholds.append(norm.ppf(p))  # τ_i = Φ⁻¹(P(X ≤ i))
    return np.concatenate(([-inf], thresholds, [inf]))


def normalize_ordinal(x: np.ndarray[int]) -> np.ndarray[int]:
    """Normalize ordinal variable to be integer-coded starting from 0."""
    unique_values = np.unique(x)
    value_to_code = {value: code for code, value in enumerate(unique_values)}
    return np.vectorize(value_to_code.get)(x)


def polychoric(x: ArrayLike[int], y: ArrayLike[int]) -> float:
    """
    Estimate the polychoric correlation coefficient between two ordinal variables.

    The polychoric correlation assumes that the two observed ordinal variables
    are thresholded representations of underlying continuous variables that follow
    a bivariate normal distribution.


    Parameters
    ----------
    x : array_like (int)
        Ordinal variable.
    y : array_like (int)
        Ordinal variable.

    Returns
    -------
    float
        Estimated polychoric correlation coefficient.

    Examples
    --------
    >>> from ordinalcorr import polychoric
    >>> x = [1, 1, 2, 2, 3, 3]
    >>> y = [0, 0, 0, 1, 1, 1]
    >>> polychoric(x, y)

    References
    ----------
    .. [1] Olsson, U. (1979). Maximum likelihood estimation of the polychoric correlation coefficient. Psychometrika, 44(4), 443-460.
    .. [2] Drasgow, F. (1986). Polychoric and polyserial correlations In: Kotz S, Johnson N, editors. The Encyclopedia of Statistics.
    """
    x = np.asarray(x)
    y = np.asarray(y)

    try:
        check_length_are_same(x, y)
        check_if_zero_variance(x)
        check_if_zero_variance(y)
    except ValidationError as e:
        warnings.warn(str(e))
        return np.nan

    x_levels = np.sort(np.unique(x))
    y_levels = np.sort(np.unique(y))

    if x_levels.size <= 1 or y_levels.size <= 1:
        Warning("Both x and y must have at least two unique ordinal levels.")
        return np.nan

    tau_x = estimate_thresholds(x)  # thresholds for X: τ_X
    tau_y = estimate_thresholds(y)  # thresholds for Y: τ_Y

    contingency = np.zeros((len(tau_x) - 1, len(tau_y) - 1), dtype=int)
    for i, xi in enumerate(x_levels):
        for j, yj in enumerate(y_levels):
            contingency[i, j] = np.sum((x == xi) & (y == yj))  # n_ij

    def neg_log_likelihood(rho):
        log_likelihood = 0.0
        for i in range(len(tau_x) - 1):
            for j in range(len(tau_y) - 1):
                if contingency[i, j] == 0:
                    continue

                lower = [tau_x[i], tau_y[j]]
                upper = [tau_x[i + 1], tau_y[j + 1]]

                p_ij = bivariate_cdf(lower, upper, rho)
                p_ij = max(p_ij, 1e-6)  # soft clipping

                if np.isnan(p_ij):
                    continue

                log_likelihood += contingency[i, j] * np.log(p_ij)

        return -log_likelihood

    result = minimize_scalar(neg_log_likelihood, bounds=(-1, 1), method="bounded")
    return result.x


def polyserial(x: ArrayLike[float | int], y: ArrayLike[int]) -> float:
    """
    Estimate the polyserial correlation coefficient between a continuous variable x
    and an ordinal variable y using the two-step maximum likelihood estimation.

    The polyserial correlation assumes that the ordinal variable y is a thresholded
    representation of latent continuous variable that follows a normal distribution.


    Parameters
    ----------
    x : array_like (float | int)
        Continuous variable.
    y : array_like (int)
        Ordinal variable.

    Returns
    -------
    float
        Estimated polyserial correlation coefficient.

    Examples
    --------
    >>> from ordinalcorr import polyserial
    >>> x = [0.1, 0.1, 0.2, 0.2, 0.3, 0.3]
    >>> y = [0, 0, 0, 1, 1, 2]
    >>> polyserial(x, y)

    References
    ----------
    .. [1] Drasgow, F. (1986). Polychoric and polyserial correlations In: Kotz S, Johnson N, editors. The Encyclopedia of Statistics.
    """
    x = np.asarray(x)
    y = np.asarray(y)

    try:
        check_length_are_same(x, y)
        check_if_zero_variance(x)
        check_if_zero_variance(y)
    except ValidationError as e:
        warnings.warn(str(e))
        return np.nan

    z = (x - np.mean(x)) / np.std(x, ddof=0)
    y = normalize_ordinal(y)
    tau = estimate_thresholds(y)

    def neg_log_likelihood(rho):
        log_likelihood = 0.0
        for i in range(len(z)):
            j = y[i]
            tau_lower = (tau[j] - rho * z[i]) / np.sqrt(1 - rho**2)
            tau_upper = (tau[j + 1] - rho * z[i]) / np.sqrt(1 - rho**2)
            p_i = univariate_cdf(tau_lower, tau_upper)

            p_i = max(p_i, 1e-6)  # soft clipping
            if np.isnan(p_i):
                continue

            log_likelihood += np.log(p_i)

        return -log_likelihood

    result = minimize_scalar(neg_log_likelihood, bounds=(-1, 1), method="bounded")
    return result.x
