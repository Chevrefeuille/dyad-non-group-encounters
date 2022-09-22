import numpy as np
from statsmodels.stats.proportion import proportions_ztest
from scipy import stats


def proportions_ztest2(p1, n1, p2, n2):
    return (p1 / n1 - p2 / n2) / (
        ((p1 + p2) / (n1 + n2)) * (1 - (p1 + p2) / (n1 + n2)) * (1 / n1 + 1 / n2)
    ) ** 0.5


z_stat = proportions_ztest2(5, 83, 12, 99)

count = np.array([5, 12, 2])
nobs = np.array([83, 99, 100])
stat, pval = proportions_ztest(count, nobs)

print(stat, z_stat, pval, stats.norm.sf(abs(stat)) * 2)
