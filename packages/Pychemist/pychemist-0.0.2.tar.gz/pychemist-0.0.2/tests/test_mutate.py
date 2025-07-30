import pandas as pd
import numpy as np
import pytest

from pychemist import mutate  # Adjust import if needed

def test_mutate_basic():
    df = pd.DataFrame({
        'A': [1, 2, 3, 4],
        'B': ['x', 'y', 'x', 'y']
    })

    # Update rows where B == 'x' in column 'A' to 100
    result = mutate(df, "B == 'x'", 'A', 100)

    # Original df unchanged
    assert (df['A'] == [1, 2, 3, 4]).all()

    # Result has updated values
    expected = [100, 2, 100, 4]
    assert (result['A'] == expected).all()

def test_mutate_with_other():
    df = pd.DataFrame({
        'A': [1, 2, 3, 4],
        'B': ['x', 'y', 'x', 'y']
    })

    # Update rows where B == 'x' to 10, others to 0
    result = mutate(df, "B == 'x'", 'A', 10, other=0)

    expected = [10, 0, 10, 0]
    assert (result['A'] == expected).all()

def test_mutate_inplace():
    df = pd.DataFrame({
        'A': [1, 2, 3, 4],
        'B': ['x', 'y', 'x', 'y']
    })

    # Update inplace
    ret = mutate(df, "B == 'y'", 'A', 99, inplace=True)

    # Return is None for inplace
    assert ret is None

    expected = [1, 99, 3, 99]
    assert (df['A'] == expected).all()

def test_mutate_invalid_inplace():
    df = pd.DataFrame({'A': [1]})

    with pytest.raises(TypeError):
        mutate(df, "A == 1", 'A', 10, inplace="yes")