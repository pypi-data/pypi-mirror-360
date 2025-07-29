try:
    from ._tipp import TIPP
except ImportError:
    from .tipp import TIPP  # type: ignore


__all__ = ["TIPP"]
