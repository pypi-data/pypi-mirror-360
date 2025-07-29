import numpy as np

from pyinsurance.portfolio.base import TIPPBase

OPEN_DAYS_PER_YEAR = 252.0


class TIPP(TIPPBase):
    """Time Invariant Portfolio Protection (TIPP) implementation.

    This class implements the core TIPP strategy logic, managing the dynamic
    allocation between risky and safe assets to protect against downside risk
    while maintaining upside potential.

    Attributes:
        capital: Initial investment capital
        multiplier: Risk multiplier that determines the aggressiveness
                    of the strategy
        rr: Return rate of the risky asset
        rf: Risk-free rate of return
        lock_in: Lock-in percentage for gains (0-1)
        min_risk_req: Minimum risk requirement for the portfolio
        min_capital_req: Minimum capital requirement for the portfolio
        portfolio: Portfolio value at each time step
        ref_capital: Reference capital at each time step
        margin_trigger: Margin trigger at each time step
        floor: Floor at each time step
        compounded_period: Compounded period
        discount: Discount at each time step
    """

    def run(self) -> None:
        """Run the TIPP strategy.

        This method executes the TIPP strategy by dynamically adjusting the portfolio
        allocation between risky and safe assets based on market conditions. It updates
        the floor, lock-in, and portfolio values at each time step.
        """

        compounded_period = self._rr.size / OPEN_DAYS_PER_YEAR
        discount = (1 + np.float64(self._rf[0])) ** compounded_period

        self._floor = (
            np.ones(self._rr.size) * self._capital * self._min_capital_req / discount
        )
        self._margin_trigger = np.zeros(self._rr.size)
        self._ref_capital = np.ones(self._rr.size) * self._capital
        self._portfolio = self._initialise_portfolio()

        for i in range(1, self._portfolio.size):
            compounded_period -= 1 / OPEN_DAYS_PER_YEAR
            discount = (1 + np.float64(self._rf[i])) ** compounded_period
            if self._should_update_lock_in(i - 1):
                self._ref_capital[i] = self._portfolio[i - 1]
            else:
                self._ref_capital[i] = self._ref_capital[i - 1]

            floor_cap = self._portfolio[i - 1] * self._min_capital_req / discount

            if self._should_update_floor(floor_cap, i - 1):
                self._floor[i] = floor_cap
            else:
                self._floor[i] = self._floor[i - 1]

            if self._should_inject_liquidity(i - 1):
                capital_to_inject = (
                    self._ref_capital[i - 1] * self._min_capital_req
                    - self._portfolio[i - 1]
                )
                self._ref_capital[i] = self._ref_capital[i - 1] - capital_to_inject
                self._portfolio[i - 1] += capital_to_inject
                self._margin_trigger[i] = capital_to_inject

            magnet = self._portfolio[i - 1] - self._floor[i - 1]
            risk_allocation = self._get_risk_allocation_mix(magnet, i - 1)
            risk_free_allocation = self._portfolio[i - 1] - risk_allocation
            self._portfolio[i] = self._update_portfolio_mix(
                risk_allocation, risk_free_allocation, i
            )

    def _initialise_portfolio(self) -> np.ndarray:
        return np.ones(self._rr.size) * self._capital * self._min_risk_req * (
            1 + self._rr[0]
        ) + self._capital * (1 - self._min_risk_req) * (1 + self._rf[0]) ** (
            1 / OPEN_DAYS_PER_YEAR
        )

    def _should_update_lock_in(self, n: int) -> bool:
        assert self._portfolio is not None and self._ref_capital is not None
        return self._portfolio[n] >= (1 + self._lock_in) * self._ref_capital[n]

    def _should_update_floor(self, floor_cap: float, n: int) -> bool:
        assert self._floor is not None
        return floor_cap > self._floor[n]

    def _should_inject_liquidity(self, n: int) -> bool:
        assert self._portfolio is not None and self._ref_capital is not None
        return self._portfolio[n] < self._ref_capital[n] * self._min_capital_req

    def _get_risk_allocation_mix(self, magnet: float, n: int) -> float:
        assert self._portfolio is not None
        return max(
            min(self._multiplier * magnet, self._portfolio[n]),
            self._min_risk_req * self._portfolio[n],
        )

    def _update_portfolio_mix(
        self, risk_alloc: float, risk_free_alloc: float, n: int
    ) -> float:
        return risk_alloc * (1 + self._rr[n]) + risk_free_alloc * (1 + self._rf[n]) ** (
            1 / OPEN_DAYS_PER_YEAR
        )
