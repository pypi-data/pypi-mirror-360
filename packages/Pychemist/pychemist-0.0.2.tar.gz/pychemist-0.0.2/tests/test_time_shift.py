import pandas as pd
import numpy as np
import pandas.testing as pdt
from pychemist import time_shift

def test_time_shift_expected_output():
    data = {
        'company': ['ZENTECH', 'ZENTECH', 'ZENTECH', 'ZENTECH', 'ZENTECH',
                    'CHICORE', 'CHICORE', 'CHICORE', 'CHICORE',
                    'CYBERMICRO', 'CYBERMICRO', 'CYBERMICRO', 'CYBERMICRO',
                    'QUANTZ', 'QUANTZ', 'QUANTZ', 'QUANTZ', 'QUANTZ'],
        'year': [2017, 2018, 2019, 2020, 2021,
                 2017, 2018, 2019, 2021,
                 2017, 2018, 2019, 2021,
                 2020, 2021, 2018, 2017, 2019],
        'profit': [84, 95, 105, 85, 109,
                   76, 79, 83, 87,
                   250, 230, 224, 290,
                   512, 580, 490, 502, 502],
        'assets': [500, 550, 600, 630, 680,
                   1000, 1050, 1100, 1150,
                   750, 800, 820, 870,
                   2200, 2400, 2100, 2000, 2300],
        'leverage': [1.5, 1.4, 1.6, 1.5, 1.7,
                     1.8, 1.7, 1.6, 1.5,
                     2.0, 1.9, 1.8, 1.7,
                     1.3, 1.2, 1.4, 1.5, 1.3],
        'revenue': [200, 220, 240, 250, 270,
                    400, 420, 440, 460,
                    500, 520, 540, 600,
                    1000, 1100, 900, 950, 1050],
        'expenses': [116, 125, 135, 165, 161,
                     324, 341, 357, 373,
                     250, 290, 316, 310,
                     488, 520, 410, 448, 548],
    }

    expected = pd.DataFrame(data)
    expected["assets_lag"] = [np.nan, 500.0, 550.0, 600.0, 630.0,
                              np.nan, 1000.0, 1050.0, np.nan,
                              np.nan, 750.0, 800.0, np.nan,
                              2300.0, 2200.0, 2000.0, np.nan, 2100.0]
    expected["profit_lag"] = [np.nan, 84.0, 95.0, 105.0, 85.0,
                              np.nan, 76.0, 79.0, np.nan,
                              np.nan, 250.0, 230.0, np.nan,
                              502.0, 512.0, 502.0, np.nan, 490.0]

    result = time_shift(pd.DataFrame(data), variables=["assets", "profit"], id="company", time="year", shift=1)

    result.sort_values(by=["company", "year"], inplace=True)
    expected.sort_values(by=["company", "year"], inplace=True)

    result.reset_index(drop=True, inplace=True)
    expected.reset_index(drop=True, inplace=True)

    pdt.assert_frame_equal(result, expected)