from typing import Optional

import numpy as np
from numpy.typing import NDArray

class TIPP:
    """Time Invariant Portfolio Protection (TIPP) implementation in Cython."""

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
        """Initialize TIPP model with parameters."""
        ...

    @property
    def portfolio(self) -> Optional[NDArray[np.float64]]:
        """Get the portfolio values."""
        ...

    @property
    def ref_capital(self) -> Optional[NDArray[np.float64]]:
        """Get the reference capital values."""
        ...

    @property
    def margin_trigger(self) -> Optional[NDArray[np.float64]]:
        """Get the margin trigger values."""
        ...

    @property
    def floor(self) -> Optional[NDArray[np.float64]]:
        """Get the floor values."""
        ...

    @property
    def min_risk_req(self) -> float:
        """Get the minimum risk requirement."""
        ...

    @property
    def min_capital_req(self) -> float:
        """Get the minimum capital requirement."""
        ...

    @property
    def lock_in(self) -> float:
        """Get the lock-in rate."""
        ...

    @property
    def multiplier(self) -> float:
        """Get the multiplier."""
        ...

    @property
    def rr(self) -> NDArray[np.float64]:
        """Get the return rate array."""
        ...

    @property
    def rf(self) -> NDArray[np.float64]:
        """Get the risk-free rate array."""
        ...

    @property
    def capital(self) -> float:
        """Get the capital."""
        ...

    def run(self) -> None:
        """Run the TIPP strategy simulation."""
        ...

    def __str__(self) -> str:
        """Return a formatted string representation of the TIPP model."""
        ...

    def __repr__(self) -> str:
        """Return a concise string representation of the TIPP model."""
        ...
