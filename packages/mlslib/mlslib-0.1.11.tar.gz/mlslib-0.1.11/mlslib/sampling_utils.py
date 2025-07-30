import pandas as pd
from pyspark.sql import DataFrame as SparkDataFrame
import pyspark.sql.functions as F

def sample_by_session(df, session_column: str, fraction: float, seed: int = 42):
    """
    Performs session-based sampling on a PySpark or Pandas DataFrame.

    This function first identifies all unique session keys in the specified column,
    samples a fraction of these keys, and then returns a new DataFrame
    containing all rows for the sampled sessions.

    Args:
        df (pd.DataFrame or pyspark.sql.DataFrame): The input DataFrame.
        session_column (str): The name of the column containing the session identifier.
        fraction (float): The fraction of unique sessions to sample (e.g., 0.01 for 1%).
                          Must be between 0.0 and 1.0.
        seed (int, optional): A random seed for reproducibility. Defaults to 42.

    Returns:
        (pd.DataFrame or pyspark.sql.DataFrame): A new DataFrame containing the sampled sessions.
                                                 The type will match the input DataFrame type.
    
    Raises:
        ValueError: If the input df is not a Pandas or PySpark DataFrame,
                    or if the fraction is not between 0.0 and 1.0.
        KeyError: If the session_column does not exist in the DataFrame.
    """
    if fraction < 0.0 or fraction > 1.0:
        raise ValueError("Fraction must be between 0.0 and 1.0")

    if session_column not in df.columns:
        raise KeyError(f"Column '{session_column}' not found in the DataFrame.")

    if isinstance(df, SparkDataFrame):
        # PySpark DataFrame implementation
        unique_session_keys = df.select(session_column).distinct()
        sampled_session_keys = unique_session_keys.sample(withReplacement=False, fraction=fraction, seed=seed)
        
        # Use a broadcast join for performance, as in your example
        sampled_df = df.join(F.broadcast(sampled_session_keys), on=session_column, how="inner")
        return sampled_df

    elif isinstance(df, pd.DataFrame):
        # Pandas DataFrame implementation
        unique_session_keys = df[session_column].unique()
        
        # Create a Series to use the .sample() method
        sampled_session_keys_series = pd.Series(unique_session_keys).sample(frac=fraction, random_state=seed)
        
        sampled_df = df[df[session_column].isin(sampled_session_keys_series)]
        return sampled_df
        
    else:
        raise ValueError(f"Unsupported DataFrame type: {type(df)}. This function supports both Pandas and PySpark DataFrames.")