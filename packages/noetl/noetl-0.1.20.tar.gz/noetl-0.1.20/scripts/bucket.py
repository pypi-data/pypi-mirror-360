import boto3

s3_client = boto3.client('s3',
    aws_access_key_id='GOOG1ECU7SYM76ZCRVHWX7K3OSW4KGIMDBHIHFJDVVV2DTXSXL6KL37RJA4XM',
    aws_secret_access_key='vagbFF5fct9K7bhwQfEm9jliGzhZ1N9vJSNc6MpR',
    endpoint_url='https://storage.googleapis.com'
)

try:
    response = s3_client.list_objects_v2(Bucket='noetl-demo-19700101')
    for obj in response.get('Contents', []):
        print(obj['Key'])
except Exception as e:
    print(f"Error: {e}")

