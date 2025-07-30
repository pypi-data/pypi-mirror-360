# Pychemist

**Transform raw data into insights.**

Pychemist is a lightweight Python library designed to simplify and enrich your data science workflow. Inspired by the ancient craft of alchemy, it helps you turn raw data into analytical gold through expressive, intuitive tools built on top of `pandas`, `statsmodels`, and other popular Python data science libraries.

---

## Features

- Create lagged or lead variables for time-series and panel data
- Run quick, readable t-tests on treatment groups
- Filter model summaries to hide fixed effects
- Conditional mutation of DataFrames (similar to `dplyr::mutate` in R)
- Pandas accessor (`.pch`) for fluent, chainable workflows

## Installation

```bash
pip install pychemist
```

## Usage
```python
import pychemist as pch
```

# Example 1: Lagging a variable
```python
df = pch.time_shift(variables=["sales"], dataframe=data, id="company", time="year", shift=1)
```

# Example 2: Conditional mutation
```python
df = pch.mutate(df, query_str='division == 24 & managerID==15014', "bonus", 1000)
```

# Example 3: Conditional mutation using the DataFrame accessor
```python
df=df.pch.mutate('company_id == "8ga62sav" & year==2025', "total_assets", 82000000)
```

# Example 4: T-test between treated and control groups
```python
pch.ttest(df, variable="outcome", treatment="treated")
```

# Example 5: Model summary without fixed effects
```python
import statsmodels.formula.api as smf
model = smf.ols("y ~ x + C(firm)", data=df).fit()
print(pch.summary_no_fe(model))
```


MIT License
Copyright (c) Jeroen van Raak (2025)