import numpy as np
import pandas as pd
from scipy.stats import multivariate_normal
from ordinalcorr import polychoric


def test_known_result():
    x = np.repeat([1, 2, 3], 10)
    y = np.repeat([1, 2, 3], 10)
    rho = polychoric(x, y)
    assert 0.9 < rho < 1.0, f"Expected high rho, got {rho}"


def test_inverse_correlation():
    x = np.tile([1, 2, 3], 10)
    y = np.tile([6, 4, 2], 10)
    rho = polychoric(x, y)
    assert -1.0 < rho < -0.9, f"Expected strong negative rho, got {rho}"


def test_no_correlation():
    x = np.tile([1, 2, 3], 20)
    y = np.repeat([1, 2, 3], 20)
    rho = polychoric(x, y)
    assert -0.1 < rho < 0.1, f"Expected close to zero rho, got {rho}"


def test_single_category():
    x = np.repeat([1], 10)
    y = np.repeat([0], 10)
    rho = polychoric(x, y)
    assert (
        np.isnan(rho) or abs(rho) < 1e-6
    ), f"Expected undefined or near-zero rho, got {rho}"


def test_different_length():
    x = np.repeat([0, 1, 2], 10)
    y = np.repeat([2, 0, 1], 11)
    rho = polychoric(x, y)
    assert np.isnan(rho), f"Expected nan, got {rho}"


def test_different_rho():
    for bins in [2, 3]:
        for rho in np.arange(-1, 1, 0.1):
            # change tolerance because estimation error is large for small rho
            tolerance = 0.3 if rho < 0.5 else 0.1

            df = gen_data_for_polychoric(rho=rho, bins=bins, size=1000)
            rho_hat = polychoric(df["x1"], df["x2"])
            # print(f"{bins=} {rho=:>.3f} {rho_hat=:>.3f}")
            assert np.isclose(
                rho, rho_hat, atol=tolerance
            ), f"Expected rho close to {rho}, got {rho_hat}"


def gen_data_for_polychoric(rho=0.5, bins=3, size=1000):
    # Generate data by standard normal distribution
    mean = [0, 0]
    std = [1, 1]
    cov = rho * std[0] * std[1]
    Cov = np.array([[std[0] ** 2, cov], [cov, std[1] ** 2]])
    X = multivariate_normal.rvs(mean=mean, cov=Cov, size=size, random_state=0)
    df = pd.DataFrame(X, columns=["x1", "x2"])
    for col in df.columns:
        df[col] = pd.cut(df[col], bins=bins, labels=range(bins)).astype(int)
    return df
