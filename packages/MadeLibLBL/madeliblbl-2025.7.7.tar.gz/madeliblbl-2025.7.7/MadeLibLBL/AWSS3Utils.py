import pandas as pd
from io import BytesIO
from typing import Any

def load_parquet_from_s3(s3_client: Any, file_name: str, bucket_name: str) -> pd.DataFrame:
    """
    Loads a Parquet file from an S3 bucket and returns it as a DataFrame.
    
    Args
    ----
        s3_client (Any): boto3 client for AWS S3
        file_name (str): Name of the Parquet file (include path within bucket if needed).
        bucket_name (str): S3 bucket name.
    
    Returns
    -------
        pd.DataFrame: DataFrame containing the Parquet file data.
    """
    # Download Parquet file from S3 to memory
    response = s3_client.get_object(Bucket=bucket_name, Key=file_name)
    parquet_buffer = BytesIO(response['Body'].read())
    
    # Read the Parquet file into a DataFrame
    dataframe = pd.read_parquet(parquet_buffer, engine='pyarrow')
    
    return dataframe

def save_parquet_to_s3(s3_client: Any, dataframe: pd.DataFrame, file_name: str, bucket_name:str, region_name='us-east-1') -> str:
    """
    Saves a DataFrame as a Parquet file in an S3 bucket.
    
    Args
    ----
        s3_client (Any): boto3 client for AWS S3
        dataframe (pd.DataFrame): DataFrame to be saved.
        file_name (str): Name of the Parquet file (include path within bucket if needed).
        bucket_name (str): S3 bucket name.
        region_name (str): S3 region (default is 'us-east-1').
    
    Returns
    -------
        str: URL of the saved file in S3.
    """    
    # Convert DataFrame to in-memory Parquet
    parquet_buffer = BytesIO()
    dataframe.to_parquet(parquet_buffer, index=False, engine='pyarrow')
    parquet_buffer.seek(0)
    
    # Save Parquet to S3 bucket
    s3_client.put_object(
        Bucket=bucket_name,
        Key=file_name,
        Body=parquet_buffer.getvalue(),
        ContentType='application/octet-stream'
    )
    
    # Returns the URL of the file in S3
    file_url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{file_name}"
    return file_url