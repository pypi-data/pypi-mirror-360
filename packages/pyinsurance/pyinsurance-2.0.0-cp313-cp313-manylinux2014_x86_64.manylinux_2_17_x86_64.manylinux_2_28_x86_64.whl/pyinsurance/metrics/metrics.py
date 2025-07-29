from typing import Optional

import numpy as np
import scipy
from statsmodels.distributions.empirical_distribution import ECDF  # type: ignore


class Metrics:
    """
    Compute metrics and ratios for a portfolio
    """

    def __init__(
        self, rr: np.ndarray, br: np.ndarray, rf: np.ndarray, freq: float
    ) -> None:
        self._rr = rr
        self._rf = rf
        self._br = br
        self._freq = freq

    def sharp(self, ret: Optional[np.ndarray] = None) -> float:
        if not ret:
            ret = self._rr
        er = np.mean(ret - self._rf)
        er_std = np.std(er) * self._freq**0.5
        return er / er_std

    def sortino(self) -> float:
        sortino_std = np.std(self._rf[np.where(self._rr > 0)]) * self._freq**0.5
        er = np.mean(self._rr - self._rf)
        return er / sortino_std

    def information(self) -> float:
        information_er = np.mean(self._rr - self._br)
        volatility = np.std(information_er) * self._freq**0.5
        return information_er / volatility

    def modigliani(self) -> float:
        benchmark_volatility = np.std(self._br) * self._freq**0.5
        return self.sharp() * benchmark_volatility + self._rf[-1]

    def omega(self) -> float:
        ecdf = ECDF(self._rr)
        return (1 - ecdf(0)) / ecdf(0)

    def psharp(self) -> float:
        br_sharp = self.sharp(self._br)
        return scipy.stats.norm.cdf((self.sharp() - br_sharp) / self._sharp_std())

    def cagr(self) -> float:
        N = self._rf.size / self._freq
        return self.cum_ret() ** (1 / N) - 1

    def std(self) -> float:
        return np.std(self._rr) * self._freq**0.5

    def cum_ret(self):
        return np.cumprod(1 + self._rr)

    def drawdown(self, in_percent: bool = False):
        cum_ret = self.cum_ret()
        dd = cum_ret / np.maximum.accumulate(cum_ret, axis=0) - 1
        if in_percent:
            dd *= 100
        return dd

    def _sharp_std(self):
        sk = scipy.stats.skew(self._rr)
        kurt = scipy.stats.kurtosis(self._rr)
        sharp = self.sharp()
        return (
            np.sqrt(
                (1 + (0.5 * sharp**2) - (sk * sharp) + (((kurt - 3) / 4) * sharp**2))
                / (self._rr.size - 1)
            )
            * self._freq
        )
