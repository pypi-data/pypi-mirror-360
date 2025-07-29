from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import lit

def assign_next_id(spark: SparkSession, df: DataFrame, table_name: str, column_name: str = 'storage_id') -> DataFrame:
    """
    Assigns the next available incremental ID to a specified column in a Spark DataFrame.

    This function fetches the maximum value of a column (default: 'storage_id') from an external
    Hive or Spark SQL-compatible table, increments it by one, and assigns the same value to
    all rows in the input DataFrame.

    Parameters:
    ----------
    spark : SparkSession
        The active Spark session used to query the table.
    
    df : DataFrame
        The input Spark DataFrame to which the new ID will be assigned.
    
    table_name : str
        The name of the table (should be accessible via Spark SQL) from which to get the max ID.
    
    column_name : str, optional
        The name of the column to create or overwrite in the DataFrame. Default is 'storage_id'.

    Returns:
    -------
    DataFrame
        A new DataFrame with the added column containing the next available ID.

    Example:
    -------
    >>> df = assign_next_id(spark, my_df, "my_table", "my_id")
    >>> df.show()
    
    Notes:
    -----
    - This assigns the **same** ID to all rows.
    - The table `table_name` must exist and be accessible to Spark.
    - This function is typically used for tracking or incremental inserts in batch processes.
    """
    
    # Run SQL to get the max ID from the external table
    result = spark.sql(f"SELECT MAX({column_name}) AS max_id FROM {table_name}").first()
    
    # Determine the current max ID; handle null case
    max_id = result['max_id'] if result and result['max_id'] is not None else 0

    # Compute the next ID
    next_id = max_id + 1 if max_id else 1

    # Assign the same ID to all rows in the DataFrame
    return df.withColumn(column_name, lit(next_id))
