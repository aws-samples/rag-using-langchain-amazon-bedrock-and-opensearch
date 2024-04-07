import requests
import gzip
import json
import tempfile
from loguru import logger
import sys
import os


# logger
logger.remove()
logger.add(sys.stdout, level=os.getenv("LOG_LEVEL", "INFO"))


def download_dataset(url):
    # download the dataset and store it to tmp dir
    try:
        logger.info("Downloading dataset")
        response = requests.get(url)
        if response.status_code == 200:
            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.write(response.content)
            temp.close()
            return temp.name
        else:
            logger.error("Failed to download dataset")
            return None
    except Exception as e:
        logger.error(e)
        return None
        
    

def decompress_dataset(file_path):
    # decompress the dataset
    temp_fd, temp_path = tempfile.mkstemp()
    logger.info(f"Decompressing dataset {file_path} to new file {temp_path}") 
    try:    
        with gzip.open(file_path, 'rb') as compressed:
            with open(temp_path, 'wb') as decompressed:
                decompressed.write(compressed.read())
        logger.info("Decompression complete") 
        return temp_path
    except Exception as e:
        logger.error(e)
        return None


def prep_for_put(file_path):
    logger.info(f"Loading file {file_path}")
    all_records = []
    with open(file_path, 'r') as f:
        for line in f:
            row = json.loads(line)
            text = f"question: {row[0]}, answer: {row[1]}"
            all_records.append(text)
        return all_records


def delete_file(file_path):
    logger.info(f"Deleting file {file_path}")
    try:
        os.remove(file_path)
    except Exception as e:
        logger.error(e)
