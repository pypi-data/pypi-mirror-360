def load_bigquery_table_spark(
    spark,
    sql_query: str,
    table_name: str,
    project_id: str,
    dataset_id: str
):
    """
    Loads a BigQuery table into Spark.

    Args:
        spark: SparkSession object
        sql_query (str): SQL query to execute after loading the table
        table_name (str): Name of the BigQuery table (without dataset/project)
        project_id (str): GCP project ID
        dataset_id (str): BigQuery dataset ID

    Returns:
        pyspark.sql.DataFrame: Result of the SQL query
    """
    full_table_path = f"{project_id}.{dataset_id}.{table_name}"
    
    spark.read.format("bigquery") \
        .option("table", full_table_path) \
        .load() \
        .createOrReplaceTempView(table_name)
    
    return spark.sql(sql_query)
