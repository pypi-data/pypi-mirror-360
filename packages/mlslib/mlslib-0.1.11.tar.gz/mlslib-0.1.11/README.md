# mlslib

[![PyPI version](https://badge.fury.io/py/mlslib.svg)](https://badge.fury.io/py/mlslib)
[![Python 3](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight utility library to simplify working with Google Cloud Storage and BigQuery on Google Cloud Platform (GCP). This library provides a set of high-level functions to streamline common data engineering and data science workflows.

## 🚀 Key Features

- **Google Cloud Storage Integration**: Upload pandas or Spark DataFrames to GCS
- **File Management**: Upload any local file (CSV, Parquet, Pickle, etc.) to GCS
- **Public Access**: Make GCS files public and get downloadable links
- **BigQuery Integration**: Query BigQuery tables directly into Spark DataFrames
- **Notebook Display**: Beautifully display PySpark DataFrames in Jupyter notebooks
- **Data Sampling**: Perform session-based sampling on pandas and Spark DataFrames

## 📦 Installation

Install `mlslib` directly from PyPI:

```bash
pip install mlslib
```

### Dependencies

The library requires the following Python packages:
- `ipython>=7.0.0` - For notebook display functionality
- `pyarrow>=6.0.0` - For efficient data serialization

**Note**: The library's functions assume that `google-cloud-storage` and `pyspark` are installed and configured in your environment.

## 🔧 Setup

Before using `mlslib`, ensure you have:

1. **Google Cloud SDK** installed and configured
2. **Authentication** set up (service account key or gcloud auth)
3. **Required packages** installed:
   ```bash
   pip install google-cloud-storage pyspark
   ```

## 📖 Usage

### Google Cloud Storage Utilities (`gcs_utils`)

#### Upload Local Files to GCS

```python
from mlslib.gcs_utils import upload_file_to_gcs

# Upload any local file to GCS
gcs_uri = upload_file_to_gcs(
    file_path="/path/to/your/local/model.pkl",
    bucket_name="my-gcp-bucket",
    gcs_path="models/model.pkl"
)
print(f"File uploaded to: {gcs_uri}")
```

#### Upload DataFrames to GCS

```python
from mlslib.gcs_utils import upload_df_to_gcs

# Upload pandas DataFrame
gcs_path_pandas = upload_df_to_gcs(
    my_pandas_df,
    bucket_name="my-gcp-bucket",
    gcs_path="data/pandas_export.parquet",
    format="parquet"
)

# Upload Spark DataFrame
gcs_path_spark = upload_df_to_gcs(
    my_spark_df,
    bucket_name="my-gcp-bucket",
    gcs_path="data/spark_export.csv",
    format="csv"
)
```

#### Make Files Public and Get Download Links

```python
from mlslib.gcs_utils import download_csv

# Make a GCS file public and get HTTPS download link
public_url = download_csv(
    bucket_name="my-gcp-bucket",
    file_path="data/public_file.csv"
)
print(f"Public URL: {public_url}")
```

### BigQuery Utilities (`bigquery_utils`)

#### Load BigQuery Data into Spark DataFrames

```python
from mlslib.bigquery_utils import load_bigquery_table_spark

# Load data from BigQuery table into Spark DataFrame
sql = "SELECT user_id, event_name FROM my_table WHERE event_date = '2025-06-22'"
df = load_bigquery_table_spark(
    spark=spark,  # Your SparkSession object
    sql_query=sql,
    table_name="my_table",
    project_id="my-gcp-project",
    dataset_id="my_analytics_dataset"
)
df.show()
```

### Display Utilities (`display_utils`)

#### Beautiful DataFrame Display in Notebooks

```python
from mlslib.display_utils import display_df

# Display Spark DataFrame as styled HTML table
display_df(df, limit_rows=50, title="User Events Preview")
```

### Sampling Utilities (`sampling_utils`)

#### Session-Based Data Sampling

```python
from mlslib.sampling_utils import sample_by_session

# Sample 1% of unique sessions from a DataFrame
sampled_df = sample_by_session(
    df=my_dataframe,
    session_column="user_session_id",
    fraction=0.01,
    seed=42
)

# Works with both pandas and Spark DataFrames
sampled_pandas = sample_by_session(pandas_df, "session_id", 0.05)
sampled_spark = sample_by_session(spark_df, "session_id", 0.05)
```

### Date Utilities (`date_utils`)

#### Generate Periodic Date Ranges

```python
from mlslib.date_utils import generate_periodic_date_ranges

# Generate 4 weekly (7-day) date ranges
weekly_batches = generate_periodic_date_ranges(
    start_date_str="2025-07-01", 
    num_periods=4, 
    period_days=7
)
# Returns: [('2025-07-01', '2025-07-07'), ('2025-07-08', '2025-07-14'), ...]
print(weekly_batches)
```

#### Get Relative Date Ranges

```python
from mlslib.date_utils import get_relative_day_range

# Get the date range for the last 30 days, ending yesterday
# Assuming today is 2025-06-29
last_30_days = get_relative_day_range(days=30, offset_days=-1)
# Returns: ('2025-05-30', '2025-06-28')
print(last_30_days)
```


## 📁 Project Structure

```
mlslib/
├── __init__.py          # Package initialization and exports
├── gcs_utils.py         # Google Cloud Storage utilities
├── bigquery_utils.py    # BigQuery integration utilities
├── display_utils.py     # Notebook display utilities
└── sampling_utils.py    # Data sampling utilities
```

## 🔍 API Reference

### `gcs_utils` Module

- `upload_file_to_gcs(file_path, bucket_name, gcs_path)` - Upload local file to GCS
- `upload_df_to_gcs(df, bucket_name, gcs_path, format='parquet')` - Upload DataFrame to GCS
- `download_csv(bucket_name, file_path)` - Make GCS file public and get download URL

### `bigquery_utils` Module

- `load_bigquery_table_spark(spark, sql_query, table_name, project_id, dataset_id)` - Load BigQuery data into Spark DataFrame

### `display_utils` Module

- `display_df(df, limit_rows=100, title=None)` - Display Spark DataFrame in notebook

### `sampling_utils` Module

- `sample_by_session(df, session_column, fraction, seed=42)` - Perform session-based sampling on pandas or Spark DataFrames

### `date_utils` Module

- `generate_periodic_date_ranges(start_date_str, num_periods, period_days)` - Generate sequential date ranges of N days each.

- `get_relative_day_range(days, offset_days, base_date_str)` - Get date range for N days relative to a base date.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Raj Jha** - [rjha4@wayfair.com](mailto:rjha4@wayfair.com)

## 🔗 Links

- **PyPI**: [https://pypi.org/project/mlslib/](https://pypi.org/project/mlslib/)
- **Repository**: [https://github.com/wayfair-sandbox/mlslib](https://github.com/wayfair-sandbox/mlslib)

---

**Note**: This library is designed to work with Google Cloud Platform services. Make sure you have proper authentication and permissions set up before using these utilities.