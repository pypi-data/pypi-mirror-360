from abc import ABC, abstractmethod
from typing import Optional

import numpy as np
from numpy.typing import NDArray


class TIPPBase(ABC):
    """Base class for TIPP implementations."""

    def __init__(
        self,
        capital: float,
        multiplier: float,
        rr: NDArray[np.float64],
        rf: NDArray[np.float64],
        lock_in: float,
        min_risk_req: float,
        min_capital_req: float,
    ) -> None:
        """
        Initialize TIPP model with parameters.

        Args:
            capital (float): Initial investment capital
            floor (float): Minimum acceptable portfolio value (protection level)
            multiplier (float): Risk multiplier that determines the aggressiveness of the strategy
            rr (np.ndarray): Return rate of the risky asset
            rf (np.ndarray): Risk-free rate of return
            br (np.ndarray): Benchmark return rate
            lock_in (float): Lock-in percentage for gains (0-1)
            min_risk_req (float): Minimum risk requirement for the portfolio
            min_capital_req (float): Minimum capital requirement for the portfolio

        Note:
            The TIPP strategy dynamically adjusts the allocation between risky and safe assets
            to protect against downside risk while maintaining upside potential. The floor
            represents the minimum acceptable portfolio value, and the multiplier determines
            how aggressively the strategy responds to market movements.
        """

        # Validate that all rate parameters have the same shape (1, N)
        assert rr.shape == rf.shape, "All rate parameters must have the same shape"
        assert len(rr.shape) == 1, "Rate parameters must have shape (N,)"

        self._capital = capital
        self._multiplier = multiplier
        self._rr = rr
        self._rf = rf
        self._lock_in = lock_in
        self._min_risk_req = min_risk_req
        self._min_capital_req = min_capital_req

        self._portfolio: Optional[NDArray[np.float64]] = None
        self._ref_capital: Optional[NDArray[np.float64]] = None
        self._margin_trigger: Optional[NDArray[np.float64]] = None
        self._floor: Optional[NDArray[np.float64]] = None

    @property
    def capital(self) -> float:
        return self._capital

    @property
    def portfolio(self) -> np.ndarray | None:
        return self._portfolio

    @property
    def ref_capital(self) -> np.ndarray | None:
        return self._ref_capital

    @property
    def margin_trigger(self) -> np.ndarray | None:
        return self._margin_trigger

    @property
    def floor(self) -> np.ndarray | None:
        return self._floor

    @property
    def min_risk_req(self) -> float:
        return self._min_risk_req

    @property
    def min_capital_req(self) -> float:
        return self._min_capital_req

    @property
    def lock_in(self) -> float:
        return self._lock_in

    @property
    def rr(self) -> np.ndarray:
        return self._rr

    @property
    def rf(self) -> np.ndarray:
        return self._rf

    @property
    def multiplier(self) -> float:
        return self._multiplier

    @abstractmethod
    def run(self) -> None:
        """Run the TIPP strategy."""
        pass

    def __str__(self) -> str:
        """Return a formatted string representation of the TIPP model."""
        return f"""
            TIPP Model Summary
            -----------------
            Capital: {self._capital:.2f}
            Lock-in rate: {self._lock_in:.2%}
            Minimum risk requirement: {self._min_risk_req:.2%}
            Minimum capital requirement: {self._min_capital_req:.2%}
            Multiplier: {self._multiplier:.2f}
            """.strip()

    def __repr__(self) -> str:
        """Return a concise string representation of the TIPP model."""
        return (
            f"TIPP(capital={self._capital:.2f}, "
            f"multiplier={self._multiplier:.2f}, "
            f"lock_in={self._lock_in:.2%}, "
            f"min_risk_req={self._min_risk_req:.2%}, "
            f"min_capital_req={self._min_capital_req:.2%})"
        )
