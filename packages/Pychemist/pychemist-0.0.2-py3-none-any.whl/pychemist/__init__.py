import pandas as pd
from scipy.stats import ttest_ind

def time_shift(dataframe, variables, id='id', time='time', shift=1):
    """
    Creates lagged or lead variables for the specified variables in the time series data.

    This function generates lagged (_lag, _lag2, etc.) or lead (_lead, _lead2, etc.) variables based on the 
    specified `shift` value. Positive values of `shift` generate lagged variables, while negative values 
    generate lead variables.

    Parameters:
    ----------
    dataframe : pandas.DataFrame
        The input DataFrame containing time-series data.

    id : str, optional, default='id'
        The unit or company identifier column name in the DataFrame.

    time : str, optional, default='time'
        The time period identifier column name in the DataFrame.

    variables : list of str
        A list of column names for which lagged or lead variables will be created.

    shift : int, optional, default=1
        The number of time periods to shift. A positive integer creates lagged variables, while a negative 
        integer creates lead variables.

    Returns:
    -------
    pandas.DataFrame
        A DataFrame with the original columns plus the new lagged or lead variables.

    Raises:
    ------
    Exception
        If `shift` is not an integer or if `shift` is 0.
    
    Notes:
    -----
    - Lagged variables are created by shifting data backwards (positive `shift`).
    - Lead variables are created by shifting data forwards (negative `shift`).
    """
    
    if not isinstance(shift, int):
        raise Exception("Shift value needs to be an integer")
    if shift == 0:
        raise Exception("Shift value cannot be equal to 0, as it would not change the data.")
    
    df_lag = dataframe[[time] + [id] + variables].copy()
    df_lag[time] = df_lag[time] + shift

    # Handle suffixes for lag/lead columns
    if shift > 0:  # Lag
        suffix = f'_lag{shift}' if shift > 1 else '_lag'
    elif shift < 0:  # Lead
        suffix = f'_lead{abs(shift)}' if abs(shift) > 1 else '_lead'
    
    # Identify the new columns that will be created (for the conflict check)
    new_columns = [var + suffix for var in variables]

    # Check if any of the new columns already exist in the dataframe
    conflict_columns = [col for col in new_columns if col in dataframe.columns]
    
    if conflict_columns:
        raise ValueError(f"The following lag/lead columns already exist: {', '.join(conflict_columns)}")
    
    # Perform the merge if no conflicts
    df_merged = pd.merge(dataframe, df_lag, how="left", left_on=[id, time], right_on=[id, time], suffixes=['', suffix])

    return df_merged

def convert_pipe_list(x):
    try:
        return [int(i) for i in x.split("|") if i]
    except:
        return [i for i in x.split("|") if i]

def ttest(dataframe,variable,treatment):
    """
    Input: variable to test, and group variable, dataframe
    Print variable name, mean treatment group (1), mean base group (0), difference between groups, t-value and significance
    """
    group1=dataframe[dataframe[treatment]==1]
    group0=dataframe[dataframe[treatment]==0]
    t,p=ttest_ind(group1[variable], group0[variable])
    diff=(group1[variable].mean()-group0[variable].mean())
    print(f"T-test for {variable}, grouped by {treatment}:\n")
    print(f"Mean for {treatment} (1): {group1[variable].mean():.3f}")
    print(f"Mean for {treatment} (0): {group0[variable].mean():.3f}\n")
    print(f"Difference: {diff:.3f}")
    print(f"T-value: {t:.3f}")
    print(f"Signficance: {p:.3f}")

def summary_no_fe(model):
    summary_str = model.summary().as_text()

    # Filter out lines that start with 'C(' (for fixed effects)
    filtered_summary = "\n".join([line for line in summary_str.split('\n') if not line.startswith('C(')])

    # Print the filtered summary
    return filtered_summary

def mutate(dataframe, query_str, column, value, other=None, *, inplace=False):
    """
    Conditionally update values in a DataFrame column based on a query string.

    Parameters:
    -----------
    dataframe : pd.DataFrame
        The DataFrame to update.
    column : str
        The name of the column to update or create.
    query_str : str
        A pandas query string defining the condition for rows to update.
    value : scalar or array-like
        The new value(s) to assign to rows where the condition is True.
    other : scalar or array-like, optional
        The new value(s) to assign to rows where the condition is False.	
    inplace : bool, default False
        If True, modify the DataFrame in place and return None.
        If False, return a modified copy of the DataFrame.

    Returns:
    --------
    pd.DataFrame or None
        Returns the modified copy if `inplace=False`, otherwise returns None.
    """

    if not isinstance(inplace, bool):
        raise TypeError(f"'inplace' must be a bool, got {type(inplace).__name__}")

    df = dataframe if inplace else dataframe.copy()

    match_idx = df.query(query_str).index
    non_match_idx = df.index.difference(match_idx)


    df.loc[match_idx, column] = value
    if other is not None:
        df.loc[non_match_idx, column] = other

    if not inplace:
        return df
    
# Define the custom accessor
@pd.api.extensions.register_dataframe_accessor("pch")
class Pd_Pychemist:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj
    
    def mutate(self, query_str, column, value, other=None, *, inplace=False):
        """
        Conditionally update values in a DataFrame column based on a query string.

        Parameters:
        -----------
        column : str
            The name of the column to update or create.
        query_str : str
            A pandas query string defining the condition for rows to update.
        value : scalar or array-like
            The new value(s) to assign to rows where the condition is True.
        other : scalar or array-like, optional
            The new value(s) to assign to rows where the condition is False.
        inplace : bool, default False
            If True, modify the DataFrame in place and return None.
            If False, return a modified copy of the DataFrame.

        Returns:
        --------
        pd.DataFrame or None
            Returns the modified copy if `inplace=False`, otherwise returns None.
        """
        if not isinstance(inplace, bool):
            raise TypeError(f"'inplace' must be a bool, got {type(inplace).__name__}")

        df = self._obj
        
        if not inplace:
            df = df.copy()

        match_idx = df.query(query_str).index
        non_match_idx = df.index.difference(match_idx)

        df.loc[match_idx, column] = value
        if other is not None:
            df.loc[non_match_idx, column] = other

        if not inplace:
            return df