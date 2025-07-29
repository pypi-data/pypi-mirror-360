import numpy as np
cimport numpy as np
from libc.math cimport fmax, fmin, pow

ctypedef np.float64_t DTYPE_t
cdef np.float64_t OPEN_DAYS_PER_YEAR = 252.0

cdef class TIPP:
    """Time Invariant Portfolio Protection (TIPP) implementation.

    This class implements a dynamic portfolio protection strategy that adjusts the allocation
    between risky and safe assets to protect against downside risk while maintaining upside potential.
    """

    cdef:
        DTYPE_t _capital
        DTYPE_t _multiplier
        np.ndarray _rr
        np.ndarray _rf
        DTYPE_t _lock_in
        DTYPE_t _min_risk_req
        DTYPE_t _min_capital_req
        np.ndarray _portfolio
        np.ndarray _ref_capital
        np.ndarray _margin_trigger
        np.ndarray _floor

    def __init__(
        self,
        DTYPE_t capital,
        DTYPE_t multiplier,
        np.ndarray[DTYPE_t, ndim=1] rr,
        np.ndarray[DTYPE_t, ndim=1] rf,
        DTYPE_t lock_in,
        DTYPE_t min_risk_req,
        DTYPE_t min_capital_req
    ) -> None:
        """Initialize TIPP model with parameters."""

        # Validate that all rate parameters have the same length
        cdef Py_ssize_t rr_len = rr.shape[0]
        cdef Py_ssize_t rf_len = rf.shape[0]

        if rr_len != rf_len:
            raise ValueError("All rate parameters must have the same length")

        self._capital = capital
        self._multiplier = multiplier
        self._rr = rr
        self._rf = rf
        self._lock_in = lock_in
        self._min_risk_req = min_risk_req
        self._min_capital_req = min_capital_req
        self._portfolio = None
        self._ref_capital = None
        self._margin_trigger = None
        self._floor = None

    property capital:
        def __get__(self):
            return self._capital

    property multiplier:
        def __get__(self):
            return self._multiplier

    property portfolio:
        def __get__(self):
            return self._portfolio

    property ref_capital:
        def __get__(self):
            return self._ref_capital

    property margin_trigger:
        def __get__(self):
            return self._margin_trigger

    property floor:
        def __get__(self):
            return self._floor

    property min_risk_req:
        def __get__(self):
            return self._min_risk_req

    property min_capital_req:
        def __get__(self):
            return self._min_capital_req

    property lock_in:
        def __get__(self):
            return self._lock_in

    property rr:
        def __get__(self):
            return self._rr

    property rf:
        def __get__(self):
            return self._rf

    def run(self) -> None:
        """Run the TIPP strategy simulation."""
        cdef:
            Py_ssize_t i, n
            DTYPE_t floor_cap, magnet, risk_allocation, risk_free_allocation
            DTYPE_t[::1] rr_view = self._rr
            DTYPE_t[::1] rf_view = self._rf
            DTYPE_t[::1] portfolio_view
            DTYPE_t[::1] ref_capital_view
            DTYPE_t[::1] margin_trigger_view
            DTYPE_t[::1] floor_view
            DTYPE_t lock_in
            DTYPE_t min_capital_req
            DTYPE_t compounded_period

        # Calculate initial discount factor
        n = self._rr.shape[0]
        compounded_period = n / OPEN_DAYS_PER_YEAR
        discount = pow(1 + rf_view[0], compounded_period)

        # Get memoryviews for efficient access
        portfolio_view = np.ones(n, dtype=np.float64) * (self._capital * self._min_risk_req * (1 + self._rr[0]) + self._capital * (1 - self._min_risk_req) * (1 + self._rf[0]) ** (1 / OPEN_DAYS_PER_YEAR))
        ref_capital_view = np.ones(n, dtype=np.float64) * self._capital
        margin_trigger_view = np.zeros(n, dtype=np.float64)
        floor_view =  np.ones(self._rr.size, dtype=np.float64) * self._capital * self._min_capital_req / discount
        min_capital_req = self._min_capital_req
        multiplier = self._multiplier
        lock_in = self._lock_in
        min_risk_req = self._min_risk_req

        for i in range(1, n):
            compounded_period -= 1 / OPEN_DAYS_PER_YEAR
            discount = pow(1 + rf_view[i], compounded_period)

            # Update reference capital
            if portfolio_view[i-1] >= (1 + lock_in) * ref_capital_view[i-1]:
                ref_capital_view[i] = portfolio_view[i-1]
            else:
                ref_capital_view[i] = ref_capital_view[i-1]

            # Update floor
            floor_cap = portfolio_view[i-1] * min_capital_req / discount
            if floor_cap > floor_view[i - 1]:
                floor_view[i] = floor_cap
            else:
                floor_view[i] = floor_view[i-1]

            # Check for liquidity injection
            if portfolio_view[i-1] < ref_capital_view[i-1] * min_capital_req:
                capital_to_inject = ref_capital_view[i-1] * min_capital_req - portfolio_view[i-1]
                ref_capital_view[i] = ref_capital_view[i-1] - capital_to_inject
                portfolio_view[i - 1] += capital_to_inject
                margin_trigger_view[i] = capital_to_inject

            # Calculate allocations
            magnet = portfolio_view[i-1] - floor_view[i-1]
            risk_allocation = fmax(
                fmin(multiplier * magnet, portfolio_view[i-1]),
                min_risk_req * portfolio_view[i-1]
            )
            risk_free_allocation = portfolio_view[i-1] - risk_allocation

            # Update portfolio
            portfolio_view[i] = risk_allocation * (1 + rr_view[i]) + risk_free_allocation * pow(1 + rf_view[i], 1 / OPEN_DAYS_PER_YEAR)

        self._portfolio = np.asarray(portfolio_view)
        self._ref_capital = np.asarray(ref_capital_view)
        self._margin_trigger = np.asarray(margin_trigger_view)
        self._floor = np.asarray(floor_view)

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
