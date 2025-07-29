from pandas import DataFrame

from pyinsurance.data.utils import load_file


def load() -> DataFrame:
    """
    Load the irx data used in the examples

    Returns
    -------
    data : DataFrame
        Data set containing OHLC, adjusted close and the trading volume.
    """
    return load_file(__file__, "irx.csv.gz")
