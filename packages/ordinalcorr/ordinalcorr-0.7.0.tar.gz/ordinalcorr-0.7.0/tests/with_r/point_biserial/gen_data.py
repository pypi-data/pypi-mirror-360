import numpy as np
import pandas as pd
from scipy.stats import multivariate_normal
from pathlib import Path

data_dir = Path("./data")


def generate_data(rho=0.5, bins=3):
    # Generate data by standard normal distribution
    n = 1000
    mean = [0, 0]
    std = [1, 1]
    cov = rho * std[0] * std[1]
    Cov = np.array([[std[0] ** 2, cov], [cov, std[1] ** 2]])
    X = multivariate_normal.rvs(mean=mean, cov=Cov, size=n, random_state=0)
    df = pd.DataFrame(X, columns=["x", "y"])
    df["y"] = pd.cut(df["y"], bins=bins, labels=range(bins)).astype(int)
    return df


if __name__ == "__main__":
    data_dir.mkdir()
    bins = 2
    for rho in np.arange(-1, 1, 0.1):
        df = generate_data(rho=rho, bins=bins)
        df.to_csv(data_dir / f"normal_rho={rho:.2f}_bins={bins}.csv", index=False)
