import pandas as pd
import importlib.resources

def load(name: str) -> pd.DataFrame:
    with importlib.resources.files("dsf.data").joinpath(f"{name}.parquet").open("rb") as f:
        return pd.read_parquet(f)
    
def mutate(dataframe, column, query_str, new_value, inplace=False):
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
    new_value : scalar or array-like
        The new value(s) to assign to the selected rows in `column`.
    inplace : bool, default False
        If True, modify the DataFrame in place and return None.
        If False, return a modified copy of the DataFrame.

    Returns:
    --------
    pd.DataFrame or None
        Returns the modified copy if `inplace=False`, otherwise returns None.
    """

    if not inplace:
        dataframe=dataframe.copy()

    condition = dataframe.query(query_str).index
    dataframe.loc[condition, column] = new_value
    
    if not inplace:
        return dataframe