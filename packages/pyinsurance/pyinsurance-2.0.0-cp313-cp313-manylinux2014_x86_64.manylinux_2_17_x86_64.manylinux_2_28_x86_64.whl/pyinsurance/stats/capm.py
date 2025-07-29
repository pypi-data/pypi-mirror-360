from typing import Optional

import numpy as np
import statsmodels.api as sm  # type: ignore


class CAPM:
    """
    Compute the Beta and alpha of the investment under the CAPM
    """

    def __init__(self, rr: np.float64, br: np.float64, freq: float) -> None:
        self._rr = rr
        self._br = br
        self._freq = freq
        self._alpha = None
        self._beta = None

    @property
    def alpha(self) -> Optional[float]:
        return self._alpha

    @property
    def beta(self) -> Optional[float]:
        return self._beta

    @property
    def rr(self) -> np.float64:
        return self._rr

    @property
    def br(self) -> np.float64:
        return self._br

    @property
    def freq(self) -> float:
        return self._freq

    def run(self) -> None:
        """
        Compute the Beta and alpha of the investment under the CAPM
        """
        var = sm.add_constant(self._br)
        model = sm.OLS(self._rr, var).fit()
        self._alpha, self._beta = model.params[0] * self._freq, model.params[1]
