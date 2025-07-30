# mlslib/display_utils.py

from pyspark.sql import DataFrame as SparkDataFrame
from pyspark.sql import SparkSession # Used for type hinting and checking config
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, DoubleType,
    DateType, BooleanType, TimestampType, ArrayType, MapType
) # Included for completeness, though not directly used in the function itself
import pandas as pd
from IPython.display import display, HTML
import sys

def display_df(df: SparkDataFrame, limit_rows: int = 10000, title: str = "DataFrame Display"):
    """
    Displays a PySpark DataFrame beautifully like Databricks' display,
    limited to a specified number of rows, with PyArrow optimization.

    Args:
        df (pyspark.sql.DataFrame): The PySpark DataFrame to display.
        limit_rows (int): The maximum number of rows to display. Defaults to 10000.
        title (str): An optional title to display above the table.
    """
    if not isinstance(df, SparkDataFrame):
        print(f"Input is not a PySpark DataFrame. Received type: {type(df)}", file=sys.stderr)
        return

    spark_session = df.sparkSession # Get the current SparkSession

    # Check if PyArrow is enabled
    arrow_enabled = spark_session.conf.get("spark.sql.execution.arrow.pyspark.enabled", "false") == "true"

    if not arrow_enabled:
        print("Warning: PyArrow optimization is NOT enabled. Conversion to Pandas might be slower.", file=sys.stderr)
        print("To enable, set `spark.conf.set('spark.sql.execution.arrow.pyspark.enabled', 'true')` in your SparkSession config.", file=sys.stderr)
    else:
        print("PyArrow optimization is enabled for PySpark to Pandas conversion.")

    df_count = df.count()
    if df_count == 0:
        print("DataFrame is empty.")
        return

    # Limit the DataFrame rows
    limited_df = df.limit(limit_rows)

    # Convert to Pandas DataFrame. This brings data to driver's memory.
    try:
        pandas_df = limited_df.toPandas()
    except Exception as e:
        print(f"Error converting to Pandas (possibly PyArrow related or OutOfMemory): {e}", file=sys.stderr)
        print(f"Falling back to default show() for first {limit_rows} rows or consider reducing limit_rows.", file=sys.stderr)
        df.show(limit_rows, truncate=False) # Fallback to show if conversion fails
        return

    # Customize pandas display options for better visualization
    original_max_columns = pd.get_option('display.max_columns')
    original_max_rows = pd.get_option('display.max_rows')
    original_width = pd.get_option('display.width')

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', limit_rows)
    pd.set_option('display.width', 1000)

    # Convert pandas DataFrame to HTML
    html_table = pandas_df.to_html(
        index=False,
        classes=['dataframe', 'table', 'table-striped', 'table-hover'],
        border=0
    )

    # Restore pandas display options
    pd.set_option('display.max_columns', original_max_columns)
    pd.set_option('display.max_rows', original_max_rows)
    pd.set_option('display.width', original_width)

    # Add a title and wrap in a scrollable div for wide tables with enhanced styling
    full_html = f"""
    <h3>{title} (First {min(limit_rows, df_count)} Rows)</h3>
    <div style="max-height: 400px; overflow-y: auto; overflow-x: auto; border: 1px solid #ddd; border-radius: 8px;">
        {html_table}
    </div>
    <style>
        .dataframe table {{
            width: 100%;
            border-collapse: collapse;
            font-family: 'Inter', sans-serif;
        }}
        .dataframe th, .dataframe td {{
            padding: 8px 12px;
            border: 1px solid #e2e8f0;
            text-align: left;
        }}
        .dataframe th {{
            background-color: #f1f5f9;
            font-weight: 600;
        }}
        .dataframe tr:nth-child(even) {{
            background-color: #f8fafc;
        }}
        .dataframe tr:hover {{
            background-color: #e2e8f0;
        }}
        h3 {{
            font-family: 'Inter', sans-serif;
            color: #1a202c;
            margin-bottom: 15px;
        }}
    </style>
    """
    display(HTML(full_html))