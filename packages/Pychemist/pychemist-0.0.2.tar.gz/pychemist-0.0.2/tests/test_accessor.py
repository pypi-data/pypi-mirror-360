import pandas as pd
import pytest
import pychemist

def test_pch_mutate_basic():
    df = pd.DataFrame({'A': [1, 2, 3, 4], 'B': ['x', 'y', 'x', 'y']})

    # Call the accessor method (returns new df by default)
    out = df.pch.mutate("B == 'x'", 'A', 10, other=0)

    # Check the mutated values
    assert list(out['A']) == [10, 0, 10, 0]

    # Original df is unchanged since inplace=False by default
    assert list(df['A']) == [1, 2, 3, 4]

def test_pch_mutate_inplace():
    df = pd.DataFrame({'A': [1, 2], 'B': ['x', 'y']})

    ret = df.pch.mutate("B == 'y'", 'A', 99, inplace=True)

    # Returns None on inplace=True
    assert ret is None

    # Original df is modified
    assert df.loc[1, 'A'] == 99

def test_pch_mutate_invalid_inplace():
    df = pd.DataFrame({'A': [1, 2]})

    with pytest.raises(TypeError):
        df.pch.mutate("A == 1", 'A', 10, inplace="no")

def test_pch_mutate_other_none():
    df = pd.DataFrame({'A': [1, 2, 3], 'B': ['x', 'x', 'y']})

    out = df.pch.mutate("B == 'x'", 'A', 100, inplace=False)

    # Rows with B != 'x' remain unchanged
    assert out.loc[2, 'A'] == 3

def test_pch_mutate_creates_column():
    df = pd.DataFrame({'A': [1, 2], 'B': ['x', 'y']})

    out = df.pch.mutate("B == 'x'", 'C', 50)

    # 'C' column created and updated correctly
    assert 'C' in out.columns
    assert out.loc[0, 'C'] == 50
    assert pd.isna(out.loc[1, 'C'])