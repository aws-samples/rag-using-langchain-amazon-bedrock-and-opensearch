import logging
import coloredlogs
import json
import argparse
from utils.bedrock import get_bedrock_client
import sys
import os
from utils import bedrock, dataset, secret, opensearch, iam

coloredlogs.install(fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level='INFO')
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--recreate", type=bool, default=0)
    parser.add_argument("--early-stop", type=bool, default=0)
    
    return parser.parse_known_args()



def get_bedrock_client(region, account_id):
    module_path = "."
    sys.path.append(os.path.abspath(module_path))
    os.environ['AWS_DEFAULT_REGION'] = region

    boto3_bedrock = bedrock.get_bedrock_client(
        assumed_role=f'arn:aws:iam::{account_id}:role/bedrock',
        region=region, 
        )
    return boto3_bedrock


def create_vector_embedding_with_bedrock(text, name, bedrock_client):
    payload = {"inputText": f"{text}"}
    body = json.dumps(payload)
    modelId = "amazon.titan-e1t-medium"
    accept = "application/json"
    contentType = "application/json"

    response = bedrock_client.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    response_body = json.loads(response.get("body").read())

    embedding = response_body.get("embedding")
    return {"_index": name, "text": text, "vector_field": embedding}

            
def main():
    logging.info("Starting")
    # vars
    region = "us-west-2"
    name = 'rag'
    dataset_url = "https://huggingface.co/datasets/sentence-transformers/embedding-training-data/resolve/main/gooaq_pairs.jsonl.gz"
    early_stop_record_count = 100
    args, _ = parse_args()
    
    # Prepare OpenSearch index with vector embeddings index mapping
    logging.info(f"recreating opensearch index: {args.recreate}, using early stop: {args.early_stop} to insert only {early_stop_record_count} records")
    logging.info("Preparing OpenSearch Index")
    opensearch_password = secret.get_secret(name, region)
    opensearch_client =  opensearch.get_opensearch_cluster_client(name, opensearch_password, region)
    
    # Check if to delete OpenSearch index with the argument passed to the script --recreate 1
    if args.recreate:
        response = opensearch.delete_opensearch_index(opensearch_client, name)
        if response:
            logging.info("OpenSearch index successfully deleted")
    
    logging.info(f"Checking if index {name} exists in OpenSearch cluster")
    exists = opensearch.check_opensearch_index(opensearch_client, name)    
    if not exists:
        logging.info("Creating OpenSearch index")
        success = opensearch.create_index(opensearch_client, name)
        if success:
            logging.info("Creating OpenSearch index mapping")
            success = opensearch.create_index_mapping(opensearch_client, name)
            logging.info(f"OpenSearch Index mapping created")
    
    # Download sample dataset from HuggingFace 
    logging.info("Downloading dataset from HuggingFace")        
    compressed_file_path = dataset.download_dataset(dataset_url)
    if compressed_file_path is not None:
        file_path = dataset.decompress_dataset(compressed_file_path)
        if file_path is not None:
            all_records = dataset.prep_for_put(file_path)
    
    # Initialize bedrock client
    account_id = iam.get_account_id()
    bedrock_client = get_bedrock_client(region, account_id)
    
    # Vector embedding using Amazon Bedrock Titan text embedding
    all_json_records = []
    logging.info(f"Creating embeddings for records")
    
    # using the arg --early-stop
    i = 0
    for record in all_records:
        i += 1
        if args.early_stop:
            if i > early_stop_record_count:
                # Bulk put all records to OpenSearch
                success, failed = opensearch.put_bulk_in_opensearch(all_json_records, opensearch_client)
                logging.info(f"Documents saved {success}, documents failed to save {failed}")
                break
        records_with_embedding = create_vector_embedding_with_bedrock(record, name, bedrock_client)
        logging.info(f"Embedding for record {i} created")
        all_json_records.append(records_with_embedding)
        if i % 500 == 0 or i == len(all_records)-1:
            # Bulk put all records to OpenSearch
            success, failed = opensearch.put_bulk_in_opensearch(all_json_records, opensearch_client)
            all_json_records = []
            logging.info(f"Documents saved {success}, documents failed to save {failed}")
            
    logging.info("Finished creating records using Amazon Bedrock Titan text embedding")
    
    logging.info("Cleaning up")
    dataset.delete_file(compressed_file_path)
    dataset.delete_file(file_path)
    
    logging.info("Finished")
        
if __name__ == "__main__":
    main()