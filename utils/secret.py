import boto3


def get_secret(secret_prefix, region):
    client = boto3.client('secretsmanager', region_name=region)
    secret_arn = locate_secret_arn(secret_prefix, client)
    secret_value = client.get_secret_value(SecretId=secret_arn)
    return secret_value['SecretString']
    
    
def locate_secret_arn(secret_tag_value, client):
    response = client.list_secrets(
        Filters=[
            {
                'Key': 'tag-key',
                'Values': ['Name']
            },
            {
                'Key': 'tag-value',
                'Values': [secret_tag_value]
            }
        ]
    )
    return response['SecretList'][0]['ARN']