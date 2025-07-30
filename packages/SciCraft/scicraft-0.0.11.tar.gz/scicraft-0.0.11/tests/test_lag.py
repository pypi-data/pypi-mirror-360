import pandas as pd
from timeshift_utils import lag

def test_lag():
    df = pd.DataFrame({
        'id': [1, 1, 1, 2, 2],
        'time': [1, 2, 3, 1, 2],
        'value': [10, 20, 30, 40, 50]
    })
    result = lag(["value"], dataframe=df, id="id", time="time", shift=1)
    assert "value_lag" in result.columns
