# Time Shift

A simple Python utility to create lagged and lead variables for panel or time series data.

## Installation

```bash
pip install scicraft
```

## Usage

### Time_shift:

```python
from scicraft import time_shift

df_new = time_shift(variables=["sales", "price"], dataframe=df, id="firm", time="year", shift=1)
```

### Mutate (function):
``` python
from scicraft import mutate
df=mutate(df, 'price>104','new_var',4)
```

### Mutate (pandas api):
``` python
import scicraft as sc
df=df.sc.mutate('price>104','new_var',4)
```