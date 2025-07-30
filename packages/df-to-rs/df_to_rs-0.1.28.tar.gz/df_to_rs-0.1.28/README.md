# df_to_rs

`df_to_rs` is a Python package that provides efficient methods to upload, upsert and manage Pandas DataFrames in Amazon Redshift using S3 as an intermediary.

## Key Features

- Direct DataFrame to Redshift upload
- Upsert functionality (update + insert)
- Delete and insert operations
- Large dataset handling with chunking
- Support for JSON/dict/list columns (Redshift SUPER)
- AWS IAM Role support for secure authentication
- Automatic cleanup of temporary S3 files
- Optimized NULL handling in upsert operations
- Proper NULL value preservation across all data types

## Installation

```bash
pip install df_to_rs
```

## Usage

### 1. Initialize with AWS Credentials

```python
from df_to_rs import df_to_rs
import psycopg2

# Connect to Redshift
redshift_conn = psycopg2.connect(
    dbname='your_db',
    host='your-cluster.region.redshift.amazonaws.com',
    port=1433,
    user='your_user',
    password='your_password'
)
redshift_conn.set_session(autocommit=True)

# Initialize with explicit credentials
uploader = df_to_rs(
    region_name='ap-south-1',
    s3_bucket='your-s3-bucket',
    aws_access_key_id='your-access-key-id',
    aws_secret_access_key='your-secret-access-key',
    redshift_c=redshift_conn
)
```

### 2. Initialize using EC2 Instance Role (Recommended)

```python
# No AWS credentials needed when using instance role
uploader = df_to_rs(
    region_name='ap-south-1',
    s3_bucket='your-s3-bucket',
    redshift_c=redshift_conn
)
```

### 3. Basic Upload

Upload a DataFrame to a Redshift table:

```python
# Simple upload
uploader.upload_to_redshift(
    df=your_dataframe,
    dest='schema.table_name'
)
```

### 4. Upsert Operation

Update existing records and insert new ones based on key columns:

```python
# Upsert based on specific columns
uploader.upsert_to_redshift(
    df=your_dataframe,
    dest_table='schema.table_name',
    upsert_columns=['id', 'unique_key'],  # Columns to match existing records
    clear_dest_table=False  # Set True to truncate table before insert
)
```

#### Optimized NULL Handling in Upserts

The package includes optimized handling for NULL values in upsert key columns:

- Automatically splits processing for records with and without NULL values in key columns
- Uses simplified SQL for non-NULL records (better performance)
- Correctly matches records where keys contain NULL values
- Handles compound keys with a mix of NULL and non-NULL values
- Preserves NULL values in all data types (including numeric columns) during transfer

```python
# Example with NULL values in key columns
df = pd.DataFrame({
    'id': [1, 2, 3, None],
    'code': ['A', 'B', None, 'D'],
    'value': [100, 200, 300, 400]
})

# Correctly handles NULL matching in any key column
# and preserves NULLs in all column types
uploader.upsert_to_redshift(
    df=df,
    dest_table='schema.table_name',
    upsert_columns=['id', 'code']
)
```

### 5. Delete and Insert

Delete records matching a condition and insert new data:

```python
# Delete and insert with condition
uploader.delete_and_insert_to_redshift(
    df=your_dataframe,
    dest_table='schema.table_name',
    filter_cond="date >= CURRENT_DATE - 7"  # SQL condition for deletion
)

# Delete and insert with timestamp precision
uploader.delete_and_insert_to_redshift(
    df=your_dataframe,
    dest_table='schema.table_name',
    filter_cond="date >= CURRENT_DATE - 7",  # SQL condition for broad deletion
    min_timestamp='2024-06-01 00:00:00',     # Minimum timestamp value from DataFrame
    timestamp_col='created_at'               # Column to use for timestamp filtering
)
```

## Special Data Types

### NULL Value Handling

The package properly preserves NULL values in all data types:

```python
# DataFrame with NULL values in different data types
df = pd.DataFrame({
    'id': [1, 2, None, 4],                       # Integer with NULL
    'value': [10.5, None, 30.75, 40.25],         # Float with NULL
    'code': ['A', 'B', None, 'D'],               # String with NULL
    'date': [date(2025,1,1), None, date(2025,3,1), date(2025,4,1)]  # Date with NULL
})

# All NULL values will be properly preserved in Redshift
uploader.upload_to_redshift(df, 'schema.table_name')
```

### JSON/Dictionary Columns

The package automatically handles JSON/dict/list columns for Redshift SUPER type:

```python
# DataFrame with JSON column
df = pd.DataFrame({
    'id': [1, 2],
    'json_data': [{'key': 'value'}, {'other': 'data'}]
})

# Will be automatically converted for Redshift SUPER column
uploader.upload_to_redshift(df, 'schema.table_name')
```

## Large Dataset Handling

The package automatically handles large datasets by:

- Chunking data into 1 million row segments
- Streaming to S3 in memory
- Automatic cleanup of temporary files
- Progress tracking with timestamps

## Error Handling

- Automatic transaction rollback on errors
- S3 temporary file cleanup
- Detailed error messages and timestamps
- Safe staging table management for upserts

## AWS IAM Role Requirements

When using instance roles, ensure your role has these permissions:

- S3: PutObject, GetObject, DeleteObject on the specified bucket
- Redshift: COPY command permissions
- IAM: AssumeRole permissions if needed

## Best Practices

1. Use instance roles instead of access keys when possible
2. Set appropriate column types in Redshift, especially for SUPER columns
3. Create tables with appropriate sort and dist keys before uploading
4. Monitor the Redshift query logs for performance optimization

## License

This project is licensed under the MIT License - see the LICENSE file for details