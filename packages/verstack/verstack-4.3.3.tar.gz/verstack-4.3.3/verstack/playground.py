
import pandas as pd
df = pd.read_csv('/Users/danil/Downloads/Technographic Data .csv')

from verstack import DateParser

dp = DateParser()
dp.fit_transform(df)



date_pattern = (
    r"^(?!\d+\.\d+$)\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}"  # Date part
    r"(?:[ T]\d{1,2}:\d{1,2}(?::\d{1,2})?)?"          # Optional time part with T or space
    r"(?:Z|(?:[ ]?(?:[A-Z]{1,5}(?:[+-]\d{1,2})?|[+-]\d{2}(?::?\d{2})?)))?$"  # All timezone formats
)
non_null_series = df['First Seen At'].dropna()

non_null_series.astype(str).str.contains(date_pattern, regex=True)



encoded_df[self._colname].fillna(self.__global_mean, inplace = True)

df.insert(0, 'number', range(1, len(df) + 1))

import numpy as np

df.loc[1, 'number'] = np.nan
df['number'].fillna(0, inplace = True)
# pandas 3.0 will have a new method for filling NaN values
df.loc[1, 'number'] = np.nan
df.fillna({'number': 0}, inplace = True)

