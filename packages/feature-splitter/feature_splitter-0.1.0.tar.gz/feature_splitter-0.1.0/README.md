# feature_splitter

A simple package to split a pandas DataFrame into parts sorted by the column with the highest variance.

## Installation

```bash
pip install feature_splitter
```

## Usage

```python
import pandas as pd
from feature_splitter import split_df_by_variation

df = pd.read_csv('your_data.csv')
split_dfs = split_df_by_variation(df, n_splits=4, prefix='Client')
```