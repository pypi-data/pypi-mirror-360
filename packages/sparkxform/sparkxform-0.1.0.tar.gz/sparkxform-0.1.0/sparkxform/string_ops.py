from pyspark.sql import DataFrame
from pyspark.sql.functions import col, lower, trim

def clean_string_column(df: DataFrame, col_name: str, new_col: str = None) -> DataFrame:
    """
    Cleans a string column in a Spark DataFrame by trimming spaces and converting to lowercase.

    Parameters:
    ----------
    df : DataFrame
        The input Spark DataFrame.
    
    col_name : str
        The name of the column to be cleaned.

    new_col : str, optional
        The name of the output column. If None, the original column will be overwritten.

    Returns:
    -------
    DataFrame
        A new DataFrame with the cleaned string column.

    Example:
    -------
    >>> df = clean_string_column(df, col_name="Name")
    >>> df = clean_string_column(df, col_name="Name", new_col="cleaned_name")
    """
    new_col = new_col or col_name
    return df.withColumn(new_col, trim(lower(col(col_name))))
