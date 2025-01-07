import argparse
from utils import opensearch, secret
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import BedrockChat
import boto3
from loguru import logger
import sys
import os


# logger
logger.remove()
logger.add(sys.stdout, level=os.getenv("LOG_LEVEL", "INFO"))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ask", type=str, default="What is the meaning of <3?")
    parser.add_argument("--index", type=str, default="rag")
    parser.add_argument("--region", type=str, default="us-east-1")
    parser.add_argument("--tenant-id", type=str, default=None)
    parser.add_argument("--bedrock-model-id", type=str, default="anthropic.claude-3-sonnet-20240229-v1:0")
    parser.add_argument("--bedrock-embedding-model-id", type=str, default="amazon.titan-embed-text-v1")
    
    return parser.parse_known_args()


def get_bedrock_client(region):
    bedrock_client = boto3.client("bedrock-runtime", region_name=region)
    return bedrock_client
    

def create_langchain_vector_embedding_using_bedrock(bedrock_client, bedrock_embedding_model_id):
    bedrock_embeddings_client = BedrockEmbeddings(
        client=bedrock_client,
        model_id=bedrock_embedding_model_id)
    return bedrock_embeddings_client
    

def create_opensearch_vector_search_client(index_name, opensearch_password, bedrock_embeddings_client, opensearch_endpoint, _is_aoss=False):
    docsearch = OpenSearchVectorSearch(
        index_name=index_name,
        embedding_function=bedrock_embeddings_client,
        opensearch_url=f"https://{opensearch_endpoint}",
        http_auth=(index_name, opensearch_password),
        is_aoss=_is_aoss
    )
    return docsearch


def create_bedrock_llm(bedrock_client, model_version_id):
    bedrock_llm = BedrockChat(
        model_id=model_version_id, 
        client=bedrock_client,
        model_kwargs={'temperature': 0}
        )
    return bedrock_llm
    

def main():
    logger.info("Starting...")
    args, _ = parse_args()
    region = args.region
    index_name = args.index
    bedrock_model_id = args.bedrock_model_id
    bedrock_embedding_model_id = args.bedrock_embedding_model_id
    question = args.ask
    tenant_id = args.tenant_id
    logger.info(f"Question provided: {question}")
    
    # Creating all clients for chain
    bedrock_client = get_bedrock_client(region)
    bedrock_llm = create_bedrock_llm(bedrock_client, bedrock_model_id)
    bedrock_embeddings_client = create_langchain_vector_embedding_using_bedrock(bedrock_client, bedrock_embedding_model_id)
    opensearch_endpoint = opensearch.get_opensearch_endpoint(index_name, region)
    opensearch_password = secret.get_secret(index_name, region)
    opensearch_vector_search_client = create_opensearch_vector_search_client(index_name, opensearch_password, bedrock_embeddings_client, opensearch_endpoint)
    
    # LangChain prompt template
    prompt = ChatPromptTemplate.from_template("""If the context is not relevant, please answer the question by using your own knowledge about the topic. If you don't know the answer, just say that you don't know, don't try to make up an answer. don't include harmful content

    {context}

    Question: {input}
    Answer:""")
    
    docs_chain = create_stuff_documents_chain(bedrock_llm, prompt)

    search_kwargs = {}
    if tenant_id: 
        search_kwargs["filter"] = {
            "term": {
                "tenant_id": tenant_id
        }
    }

    retrieval_chain = create_retrieval_chain(
        retriever=opensearch_vector_search_client.as_retriever(search_kwargs=search_kwargs),
        combine_docs_chain = docs_chain
    )
    
    logger.info(f"Invoking the chain with KNN similarity using OpenSearch, Bedrock FM {bedrock_model_id}, and Bedrock embeddings with {bedrock_embedding_model_id}")
    response = retrieval_chain.invoke({"input": question})
    
    logger.info("These are the similar documents from OpenSearch based on the provided query:")
    source_documents = response.get('context')
    for d in source_documents:
        logger.info(f"Text: {d.page_content}")
    
    print("")
    logger.info(f"The answer from Bedrock!!!!! {bedrock_model_id} is: {response.get('answer')}")
    

if __name__ == "__main__":
    main()