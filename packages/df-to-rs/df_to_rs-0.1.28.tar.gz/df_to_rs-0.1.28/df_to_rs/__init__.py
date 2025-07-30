import csv
import io
import random
import string
import boto3
import time
import pandas as pd
import psycopg2
import json
from datetime import datetime

class df_to_rs:
    def __init__(self, region_name, s3_bucket, aws_access_key_id=None, aws_secret_access_key=None, redshift_c=None,iam_role_arn=None):
        """
        region_name: AWS region name, e.g., 'ap-south-1'.
        s3_bucket: Name of the S3 bucket to upload CSV files.
        aws_access_key_id: Optional AWS access key ID. If None, uses instance role
        aws_secret_access_key: Optional AWS secret access key. If None, uses instance role
        redshift_c: psycopg2 connection object to Redshift, e.g.,
        redshift_c = psycopg2.connect(dbname=, host="hostname.ap-south-1.redshift.amazonaws.com", port=1433, user='ankit.goel', password='xxxx')
        redshift_c.set_session(autocommit=True)
        iam_role_arn= Either use aws_access_key_id or iam role
        """
        self.region_name = region_name
        self.s3_bucket = s3_bucket
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.redshift_c = redshift_c
        self.iam_role_arn = iam_role_arn

    def _get_s3_client(self):
        """Helper method to get S3 client using either credentials or instance role"""
        if self.aws_access_key_id and self.aws_secret_access_key:
            return boto3.resource('s3',
                region_name=self.region_name,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
        else:
            return boto3.resource('s3', region_name=self.region_name)

    def upload_to_redshift(self, df, dest):
        """
        Uploads the given DataFrame to the specified destination in Redshift.
        df: pandas DataFrame to be uploaded.
        dest: Redshift destination table, including schema, e.g., 'analytics.ship_pen'.
        Now handles JSON columns intended for SUPER format.
        """
        s3 = None
        try:
            start_time = time.time()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] [{dest}] Generating randomized CSV filename...")
            csv_filename = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + '.csv'
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] [{dest}] Time taken: {int(time.time() - start_time)} seconds")

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] [{dest}] Converting DataFrame to CSV in-memory...")
            
            # ✦✦ A. DataFrame Cleanups ✦✦ 
            #================================================================
            # - Special Characters handled
            # - Long length handled
            # - JSON handled
            #================================================================
            def escape_special_chars_and_truncate(s):
                if isinstance(s, str):
                    s = s.replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace(',', '\\,').replace('\\n', ' ')
                    return s[:55000]
                return s
            string_columns = df.select_dtypes(include=['string']).columns
            df[string_columns] = df[string_columns].map(escape_special_chars_and_truncate)

            def json_to_super(s):
                if isinstance(s, (dict, list)):
                    s = json.dumps(s)[:55000]
                    return escape_special_chars_and_truncate(s)  # Ensure JSON strings are escaped
                return escape_special_chars_and_truncate(s)
            # Single map for all object columns
            object_columns = df.select_dtypes(include=['object']).columns
            df[object_columns] = df[object_columns].map(json_to_super)


            # ✦✦ B. Chunk and Upload ✦✦ 
            #================================================================
            chunk_size=1_000_000
            num_chunks = len(df) // chunk_size + (1 if len(df) % chunk_size else 0)
            if len(df) > chunk_size:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{timestamp}] [{dest}] DataFrame is large, splitting into {num_chunks} chunks.")


            s3 = self._get_s3_client()
            for chunk_num in range(num_chunks):
                chunk = df.iloc[chunk_num*chunk_size : (chunk_num+1)*chunk_size]
                csv_buffer = io.StringIO()
                chunk.to_csv(csv_buffer, index=False, quoting=csv.QUOTE_ALL, quotechar='"', na_rep="NULL")
                csv_buffer.seek(0)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{timestamp}] [{dest}] Time taken for preparing chunk {chunk_num}: {int(time.time() - start_time)} seconds")

                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{timestamp}] [{dest}] Uploading chunk {chunk_num} CSV to S3 bucket '{self.s3_bucket}'...")
                
                s3.Object(self.s3_bucket, csv_filename).put(Body=csv_buffer.getvalue())
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{timestamp}] [{dest}] Time taken for uploading chunk {chunk_num}: {int(time.time() - start_time)} seconds")

                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{timestamp}] [{dest}] Preparing Redshift COPY command for chunk {chunk_num}...")
                columns = ','.join(df.columns)

                if self.aws_access_key_id and self.aws_secret_access_key:
                    credentials_part = f"""
                    ACCESS_KEY_ID '{self.aws_access_key_id}'
                    SECRET_ACCESS_KEY '{self.aws_secret_access_key}'
                    """
                elif self.iam_role_arn:
                    credentials_part = f"IAM_ROLE '{self.iam_role_arn}'"
                else:
                    raise ValueError("Either AWS credentials or IAM role ARN must be provided")

                copy_query = f"""
                COPY {dest} ({columns})
                FROM 's3://{self.s3_bucket}/{csv_filename}'
                {credentials_part}
                DELIMITER ','
                IGNOREHEADER 1
                REMOVEQUOTES
                NULL AS 'NULL'
                REGION '{self.region_name}';
                """
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{timestamp}] [{dest}] Executing Redshift COPY command for chunk {chunk_num}...")
                self.redshift_c.cursor().execute(copy_query)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{timestamp}] [{dest}] Time taken for COPY command execution for chunk {chunk_num}: {int(time.time() - start_time)} seconds")

        except Exception as e:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] [{dest}] An error occurred: {e}")

        finally:
            if s3:  # Only attempt cleanup if s3 was created
                try:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"[{timestamp}] [{dest}] Deleting CSV file '{csv_filename}' from S3...")
                    s3.Object(self.s3_bucket, csv_filename).delete()
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"[{timestamp}] [{dest}] Time taken: {int(time.time() - start_time)} seconds")
                except Exception as e:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"[{timestamp}] [{dest}] An error occurred during cleanup: {e}")

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] [{dest}] Upload to Redshift process completed.")


    def upsert_to_redshift(self, df, dest_table, upsert_columns, clear_dest_table=False):
        """
        Upserts the given DataFrame to the specified destination table in Redshift.
        Optionally clears the destination table if clear_dest_table is True.
        Optimized to handle NULL values in upsert columns efficiently.
        
        Parameters:
        - df: pandas DataFrame to be upserted.
        - dest_table: Redshift destination table, including schema, e.g., 'analytics.ship_pen'.
        - upsert_columns: List of columns to use for the upsert condition, e.g., ['id', 'name'].
        - clear_dest_table: Boolean, if True, clears the destination table before upserting.
        """
        cursor = self.redshift_c.cursor()
        staging_table = dest_table + "_stgg"
        
        try:
            # ✦✦ A. Create Staging Table ✦✦ 
            #================================================================
            # - Drop if exists and recreate empty staging table
            # - This provides clean workspace for current operation
            #================================================================
            start_time = time.time()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] [{dest_table}] Creating staging table...")
            create_staging_query = f"DROP TABLE IF EXISTS {staging_table}; CREATE TABLE {staging_table} AS SELECT * FROM {dest_table} WHERE 1 = 0;"
            cursor.execute(create_staging_query)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] [{dest_table}] Time taken: {int(time.time() - start_time)} seconds")

            # ✦✦ B. Analyze and Prepare Data ✦✦ 
            #================================================================
            # - Identify records with NULL values in key columns
            # - Split processing for better efficiency
            #================================================================
            # Clean column names for proper processing
            clean_upsert_columns = [col.replace('"','') for col in upsert_columns]
            
            # Separate handling of records based on NULL values in upsert columns
            null_mask = df[clean_upsert_columns].isnull().any(axis=1)
            df_with_nulls = df[null_mask]
            df_without_nulls = df[~null_mask]
            
            # Identify which columns have NULL values
            null_columns = []
            for col in clean_upsert_columns:
                if df[col].isnull().any():
                    null_columns.append(col)

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] [{dest_table}] Total records: {len(df)}, Records with NULL keys: {len(df_with_nulls)}, Records without NULL keys: {len(df_without_nulls)}")
            
            # ✦✦ C. Upload Data to Staging ✦✦ 
            #================================================================
            # - Upload all data to staging table first
            # - Handles both NULL and non-NULL records
            #================================================================
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] [{dest_table}] Uploading data to staging table...")
            self.upload_to_redshift(df, dest=staging_table)
            
            # ✦✦ D. Perform Upsert Operations ✦✦ 
            #================================================================
            # - Begin transaction for atomicity
            # - Process clear_dest_table or delete matching records
            # - Insert all records from staging
            #================================================================
            cursor.execute("BEGIN;")
            start_time = time.time()

            if clear_dest_table:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{timestamp}] [{dest_table}] Truncating destination table...")
                cursor.execute(f"TRUNCATE TABLE {dest_table};")
            else:
                # Process non-NULL records first (simpler condition)
                if not df_without_nulls.empty:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"[{timestamp}] [{dest_table}] Deleting matching rows (without NULL keys) from main table...")
                    where_condition = " AND ".join([f"({dest_table}.{col} = staging.{col})" for col in upsert_columns])
                    
                    # Additional filter to only process non-NULL records in this query
                    if null_columns:
                        null_filter = " AND ".join([f"staging.{col} IS NOT NULL" for col in null_columns])
                    else:
                        null_filter = "1=1"
                    
                    delete_query = f"""
                    DELETE FROM {dest_table} 
                    USING {staging_table} AS staging 
                    WHERE {where_condition} AND {null_filter};
                    """
                    cursor.execute(delete_query)
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"[{timestamp}] [{dest_table}] Time taken for non-NULL deletion: {int(time.time() - start_time)} seconds")
                
                # Process NULL records with optimized condition
                if not df_with_nulls.empty:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"[{timestamp}] [{dest_table}] Deleting matching rows (with NULL keys) from main table...")
                    
                    # Join on non-NULL columns with equality conditions
                    where_condition = " AND ".join([f"({dest_table}.{col} = staging.{col})" for col in upsert_columns if col not in null_columns])
                    # For NULL columns, ensure both sides are NULL
                    null_filter = " AND ".join([f"{dest_table}.{col} IS NULL AND staging.{col} IS NULL" for col in null_columns])
                    
                    delete_query = f"""
                    DELETE FROM {dest_table} 
                    USING {staging_table} AS staging 
                    WHERE {where_condition} AND ({null_filter});
                    """
                    cursor.execute(delete_query)
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"[{timestamp}] [{dest_table}] Time taken for NULL deletion: {int(time.time() - start_time)} seconds")

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] [{dest_table}] Inserting new rows from staging table into main table...")
            insert_query = f"INSERT INTO {dest_table} SELECT * FROM {staging_table};"
            cursor.execute(insert_query)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] [{dest_table}] Total time taken: {int(time.time() - start_time)} seconds")

            cursor.execute("COMMIT;")

        except Exception as e:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] [{dest_table}] An error occurred: {str(e)}. Rolling back transaction...")
            cursor.execute("ROLLBACK;")
            raise
        finally:
            # ✦✦ E. Cleanup ✦✦ 
            #================================================================
            # - Drop staging table
            # - Ensures no temporary artifacts remain
            #================================================================
            try:
                start_time = time.time()
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{timestamp}] [{dest_table}] Dropping staging table...")
                drop_staging_query = f"DROP TABLE IF EXISTS {staging_table};"
                cursor.execute(drop_staging_query)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{timestamp}] [{dest_table}] Time taken: {int(time.time() - start_time)} seconds")
            except Exception as e:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{timestamp}] [{dest_table}] An error occurred during staging table cleanup: {e}")

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{dest_table}] Upsert to Redshift completed successfully.")


    def delete_and_insert_to_redshift(self, df, dest_table, filter_cond, min_timestamp=None, timestamp_col=None):
        """
        Deletes data from the specified destination table in Redshift based on the filter condition,
        and then inserts new data from the DataFrame into the table.

        Parameters:
        - df: pandas DataFrame to be inserted.
        - dest_table: Redshift destination table, including schema, e.g., 'schema_name.table_name'.
        - filter_cond: Condition to filter the data for deletion, e.g., "create_date >= CURRENT_DATE - 10".
        - min_timestamp: Optional, minimum timestamp value from the DataFrame to ensure no duplicates.
        - timestamp_col: The column to use for timestamp filtering.
        """
        cursor = self.redshift_c.cursor()
        try:
            # Deleting data from Redshift table based on filter_cond
            cursor.execute("BEGIN;")  # Add transaction start
            
            # First delete based on the original filter condition
            delete_query = f"DELETE FROM {dest_table} WHERE {filter_cond};"
            cursor.execute(delete_query)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] [{dest_table}] Data deletion based on filter condition completed.")
            
            # Second delete to ensure no duplicates, if min_timestamp is provided
            if min_timestamp is not None and timestamp_col is not None:
                # The second delete uses the exact minimum timestamp from the DataFrame
                second_delete_query = f"DELETE FROM {dest_table} WHERE {timestamp_col} >= '{min_timestamp}';"
                cursor.execute(second_delete_query)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{timestamp}] [{dest_table}] Additional data deletion with min_timestamp {min_timestamp} completed.")
            self.upload_to_redshift(df, dest_table)
            cursor.execute("COMMIT;")
        except Exception as e:
            cursor.execute("ROLLBACK;")
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] [{dest_table}] An error occurred: {e}")
            raise # Reraising the exception for external handling if necessary
        finally:
            cursor.close()