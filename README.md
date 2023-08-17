# RAG using LangChain with Amazon Bedrock Titan text, and embedding, using OpenSearch vector engine

This sample repository provides a sample code for using RAG (Retrieval augmented generation) method relaying on [Amazon Bedrock](https://aws.amazon.com/bedrock/) [Titan text embedding](https://aws.amazon.com/bedrock/titan/) LLM (Large Language Model), for creating text embedding that will be stored in [Amazon OpenSearch](https://aws.amazon.com/opensearch-service/) with [vector engine support](https://aws.amazon.com/about-aws/whats-new/2023/07/vector-engine-amazon-opensearch-serverless-preview/) for assisting with the prompt engineering task for more accurate response from LLMs.

After we successfully loaded embeddings into OpenSearch, we will then start querying our LLM, by using [LangChain](https://www.langchain.com/). We will ask questions, retrieving similar embedding for a more accurate prompt.

## Prerequisites

1. This was tested on Python 3.11.4
2. It is advise to work on a clean environment, use `virtualenv` or any other virtual environment packages.

    ```bash
    pip install virtualenv
    python -m virtualenv venv
    source ./venv/bin/activate
    ```

3. Run `./download-beta-sdk.sh` to download the beta SDK for using Amazon Bedrock
4. Install requirements `pip install -r requirements.txt`
5. Install [terraform](https://developer.hashicorp.com/terraform/downloads?product_intent=terraform) to create the OpenSearch cluster

    ```bash
    brew tap hashicorp/tap
    brew install hashicorp/tap/terraform
    ```

## Steps for using this sample code

1. In the first step we will launch an OpenSearch cluster using Terraform.

    ```bash
    cd ./terraform
    terraform init
    terraform apply -auto-approve
    ```

    >>This cluster configuration is for testing proposes only, as it's endpoint is public for simplifying the use of this sample code.

2. Now that we have a running OpenSearch cluster with vector engine support we will start uploading our data that will help us with prompt engineering. For this sample, we will use a data source from [Hugging Face](https://huggingface.co) [embedding-training-data](https://huggingface.co/datasets/sentence-transformers/embedding-training-data) [gooaq_pairs](https://huggingface.co/datasets/sentence-transformers/embedding-training-data/resolve/main/gooaq_pairs.jsonl.gz), we will download it, and invoke Titan embedding to get a text embedding, that we will store in OpenSearch for next steps.

    ```bash
    python load-data-to-opensearch.py --recreate 1 --early-stop 1
    ```

    >>Optional arguments: `--recreate` for recreating the index in OpenSearch, and `--early-stop` to load only 100 embedded documents into OpenSearch

3. Now that we have embedded text, into our OpenSearch cluster, we can start querying our LLM model Titan text in Amazon Bedrock with RAG

    ```bash
    python ask-titan-with-rag.py --ask "your question here"
    ```

### Cleanup

```bash
cd ./terraform
terraform destroy # When prompt for confirmation, type yes, and press enter.
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
