noetl-demo@impressive-mile-162105.iam.gserviceaccount.com

https://storage.googleapis.com

Access key
GOOG1EAXLYKGVESXKOPHOQPHWGFW6UM5J2PMA4I2W4XPQ6NBHB4YCW4DB3XAA

Secret
tEHpBhKTtOGm6+l194zMa3DEHJ6VgQfluxgppGB1


Access keys for your user account

Access key
GOOGVDR5JMHHL4PN3HE7IVUX

Secret
8ZWWvWeo31ktRuWb2mA2k+lsSYrxrTL19KDmV9Nr

gcloud auth application-default set-quota-project

gcloud config set project impressive-mile-162105

gcloud config get-value project

gcloud projects list

gcloud iam service-accounts add-iam-policy-binding noetl-demo@impressive-mile-162105.iam.gserviceaccount.com \
  --member="user:kadyapam@gmail.com" \
  --role="roles/iam.serviceAccountTokenCreator"

gcloud iam service-accounts keys create .secrets/noetl-demo.json \
  --iam-account=noetl-demo@impressive-mile-162105.iam.gserviceaccount.com

http://localhost:8888/lab?token=noetl

duckdb.sql("""
CREATE OR REPLACE SECRET my_gcs_secret (
    TYPE gcs,
    KEY_ID 'GOOGVDR5JMHHL4PN3HE7IVUX',
    SECRET '8ZWWvWeo31ktRuWb2mA2k+lsSYrxrTL19KDmV9Nr'
);
""")

pip show jupysql ipython-sql




import duckdb

duckdb.sql("INSTALL httpfs;")
duckdb.sql("LOAD httpfs;")

# Set the GCS endpoint and your HMAC credentials
duckdb.sql("SET s3_endpoint='storage.googleapis.com';")
duckdb.sql("SET s3_access_key_id='<YOUR_GCS_HMAC_KEY_ID>';")
duckdb.sql("SET s3_secret_access_key='<YOUR_GCS_HMAC_SECRET>';")


import duckdb

# Install and load the postgres extension
duckdb.sql("INSTALL ducklake;")
duckdb.sql("INSTALL postgres;")
duckdb.sql("LOAD ducklake;")
duckdb.sql("LOAD postgres;")


# Attach to your Postgres database (using your Docker Compose settings)
duckdb.sql("""
    ATTACH 'dbname=noetl user=noetl password=noetl host=db port=5434' AS pgdb (TYPE postgres)
""")

# Now you can query Postgres tables as if they were DuckDB tables
duckdb.sql("SELECT * FROM pgdb.test_data_table LIMIT 5;").df()


import duckdb
CREATE SECRET my_pg_secret (
  TYPE postgres,
  HOST 'db',
  PORT 5434,
  DATABASE 'noetl',
  USER 'noetl',
  PASSWORD 'noetl'
);

# %% [markdown]
# ## 2. Configure GCS Credentials for DuckDB
import duckdb
from fsspec import filesystem

# Enable GCS via HTTPFS and fsspec
duckdb.sql("INSTALL httpfs; LOAD httpfs;")
gcs_fs = filesystem("gcs")  # Uses default credentials or ~/.config/gcloud
duckdb.register_filesystem(gcs_fs)  # For `gs://` support

# Alternative: Use HMAC keys (if needed)
duckdb.sql("SET s3_endpoint='storage.googleapis.com';")
# duckdb.sql("""
# CREATE OR REPLACE SECRET gcs_secret (
#     TYPE gcs,
#     KEY_ID 'GCS_HMAC_KEY_ID',
#     SECRET 'GCS_HMAC_SECRET'
# );
# """)
duckdb.sql("SET s3_access_key_id='GOOG1EAXLYKGVESXKOPHOQPHWGFW6UM5J2PMA4I2W4XPQ6NBHB4YCW4DB3XAA';")
duckdb.sql("SET s3_secret_access_key='tEHpBhKTtOGm6+l194zMa3DEHJ6VgQfluxgppGB1';")
# duckdb.sql("""
# CREATE OR REPLACE SECRET gcs_secret (
#     TYPE gcs,
#     KEY_ID 'GOOGVDR5JMHHL4PN3HE7IVUX',
#     SECRET '8ZWWvWeo31ktRuWb2mA2k+lsSYrxrTL19KDmV9Nr'
# );
# """)

df_polars = duckdb.sql("""
    SELECT * FROM read_csv_auto('gs://noetl-examples/kaggle/stock-market-dataset/symbols_valid_meta.csv')
""").pl()
print(df_polars.head())


import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/secrets/noetl-demo.json"
!ls -l /app/secrets/noetl-demo.json
import duckdb
duckdb.sql("INSTALL httpfs; LOAD httpfs;")
df_polars = duckdb.sql("""
    SELECT * FROM read_csv_auto('gs://noetl-examples/kaggle/stock-market-dataset/symbols_valid_meta.csv')
""").pl()
print(df_polars.head())

from google.cloud import secretmanager
def get_secret(secret_id, project_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

project_id = "impressive-mile-162105"
s3_access_key_id = get_secret("noetl-demo-access-key-id", project_id)
s3_secret_access_key = get_secret("noetl-demo-secret-access-key", project_id)

import duckdb

duckdb.sql("INSTALL httpfs; LOAD httpfs;")
duckdb.sql("SET s3_endpoint='storage.googleapis.com';")
duckdb.sql(f"SET s3_access_key_id='{s3_access_key_id}';")
duckdb.sql(f"SET s3_secret_access_key='{s3_secret_access_key}';")

df_polars = duckdb.sql("""
    SELECT * FROM read_parquet('s3://noetl-examples/kaggle/stock-market-dataset/*.parquet')
""").pl()
print(df_polars.head())

# PostgreSQL connection (replace credentials as needed)
pg_user = "noetl"
pg_password = "noetl"
pg_host = "localhost"
pg_port = "5434"
pg_db = "noetl"
engine = create_engine(f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}")

# Upload to PostgreSQL, auto-creating the table based on df_polars schema
table_name = "symbols_valid_meta"
df_pandas.to_sql(table_name, engine, if_exists='replace', index=False)