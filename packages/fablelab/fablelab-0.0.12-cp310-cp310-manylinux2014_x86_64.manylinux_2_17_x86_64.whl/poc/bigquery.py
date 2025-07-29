from google.cloud import bigquery

_client = None
APPEND = bigquery.WriteDisposition.WRITE_APPEND

def _get_client():
    global _client
    if _client is None:
        _client = bigquery.Client()
    return _client

def query_to_dataframe(query):        
    return _get_client().query(query).result().to_dataframe()

def load_from_dataframe(df, table, write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE):
    job_config = bigquery.LoadJobConfig(
        write_disposition=write_disposition,
        create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED
    )
    _get_client().load_table_from_dataframe(df, table, job_config=job_config).result()
    print(f'uploaded {len(df)} rows to {table}')