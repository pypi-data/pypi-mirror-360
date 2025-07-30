import pandas as pd
import subprocess
import tempfile
import os
from google.cloud import storage

def download_csv(bucket_name: str, file_path: str) -> str:
    """
    Makes the specified file in GCS public and returns the HTTPS download link.
    
    Parameters:
        bucket_name (str): GCS bucket name
        file_path (str): Path inside the bucket (e.g., "folder/file.csv")

    Returns:
        str: HTTPS link to the file
    """
    gcs_uri = f"gs://{bucket_name}/{file_path}"

    # Make the file public using gsutil
    subprocess.run(["gsutil", "acl", "ch", "-u", "AllUsers:R", gcs_uri], check=True)

    # Generate public HTTPS link
    url = f"https://storage.googleapis.com/{bucket_name}/{file_path}"
    return url

def upload_df_to_gcs_csv(df: pd.DataFrame, bucket_name: str, gcs_path: str, project_id: str = None) -> str:
    """
    Save a DataFrame as a CSV file and upload it to a GCS bucket.

    Args:
        df (pd.DataFrame): The DataFrame to upload.
        bucket_name (str): GCS bucket name.
        gcs_path (str): Destination path in GCS (e.g., 'folder/file.csv').
        project_id (str, optional): GCP project ID for the storage client.

    Returns:
        str: Public or authenticated GCS path where the file was uploaded.
    """
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        df.to_csv(tmp.name, index=False)
        temp_path = tmp.name
    print(temp_path)

    # Upload to GCS
    client = storage.Client(project=project_id)
    print(client)
    bucket = client.bucket(bucket_name)
    print(bucket)
    blob = bucket.blob(gcs_path)
    print(blob)
    blob.upload_from_filename(temp_path)
    os.remove(temp_path)

    return f"gs://{bucket_name}/{gcs_path}"

def upload_df_to_gcs(
    df,
    bucket_name: str,
    gcs_path: str,
    format: str = "csv",
    repartition: int = None,
    project_id: str = None
) -> str:
    """
    Save a DataFrame in the specified format and upload it to a GCS bucket.

    Args:
        df (pd.DataFrame or pyspark.sql.DataFrame): DataFrame to upload.
        bucket_name (str): Name of the GCS bucket.
        gcs_path (str): Path inside the bucket (e.g. "exports/my_file.csv").
        format (str): File format: "csv", "parquet", or "txt".
        repartition (int): If using Spark, optionally set number of partitions.
        project_id (str): GCP project ID for authentication.

    Returns:
        str: GCS URI of the uploaded file.
    """
    is_spark = "pyspark" in str(type(df))

    if is_spark:
        # Handle Spark DataFrame
        if repartition:
            df = df.repartition(repartition)

        tmp_dir = tempfile.mkdtemp()
        output_path = os.path.join(tmp_dir, "output")

        if format == "parquet":
            df.write.mode("overwrite").parquet(output_path)
            file_to_upload = os.path.join(output_path, "_SUCCESS")  # dummy marker
        elif format == "csv":
            df.write.mode("overwrite").option("header", "true").csv(output_path)
            file_to_upload = os.path.join(output_path, "_SUCCESS")  # dummy marker
        elif format == "txt":
            df.write.mode("overwrite").text(output_path)
            file_to_upload = os.path.join(output_path, "_SUCCESS")
        else:
            raise ValueError("Unsupported format for Spark DataFrame.")
    else:
        # Handle Pandas DataFrame
        suffix = "." + format
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            if format == "csv":
                df.to_csv(tmp.name, index=False)
            elif format == "parquet":
                df.to_parquet(tmp.name, index=False)
            elif format == "txt":
                df.to_csv(tmp.name, index=False, sep="\t", header=False)
            else:
                raise ValueError("Unsupported format for Pandas DataFrame.")
            file_to_upload = tmp.name

    # Upload to GCS
    client = storage.Client(project=project_id)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(file_to_upload)

    # Clean up
    if not is_spark:
        os.remove(file_to_upload)

    return f"gs://{bucket_name}/{gcs_path}"

def upload_file_to_gcs(
    file_path: str,
    bucket_name: str,
    gcs_path: str,
    project_id: str = None
) -> str:
    """
    Upload any file to a GCS bucket.

    Args:
        file_path (str): Local file path to upload.
        bucket_name (str): GCS bucket name.
        gcs_path (str): Path inside GCS (e.g., 'folder/file.pkl').
        project_id (str, optional): GCP project ID.

    Returns:
        str: The full GCS URI of the uploaded file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    client = storage.Client(project=project_id)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(gcs_path)

    blob.upload_from_filename(file_path)

    return f"gs://{bucket_name}/{gcs_path}"