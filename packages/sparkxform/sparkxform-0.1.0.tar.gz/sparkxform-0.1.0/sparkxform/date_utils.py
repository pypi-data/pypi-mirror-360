from pyspark.sql import DataFrame
from pyspark.sql.functions import to_date, col

def convert_to_date(df: DataFrame, col_name: str, fmt: str = 'yyyy-MM-dd') -> DataFrame:
    """
    Converts a string column in a Spark DataFrame to a date column using the specified format.

    Parameters:
    ----------
    df : DataFrame
        The input Spark DataFrame containing the column to convert.

    col_name : str
        The name of the column to convert to a date.

    fmt : str, optional
        The date format of the input string column. Default is 'yyyy-MM-dd'.

    Returns:
    -------
    DataFrame
        A new DataFrame with the specified column cast to a date type.

    Example:
    -------
    >>> df = convert_to_date(df, 'order_date', fmt='MM/dd/yyyy')
    >>> df.printSchema()
    """
    return df.withColumn(col_name, to_date(col(col_name), fmt))
