import boto3


FLOCI_URL : str = "http://localhost:4566"

def get_client(service_name : str):
    client = boto3.client(
        service_name,
        region_name = 'us-east-1',
        endpoint_url = FLOCI_URL,
        aws_access_key_id = 'floci',
        aws_secret_access_key = 'floci',
    )
    return client

if __name__ == '__main__':
    print(get_client('eks'))