# RAG using LangChain with Amazon Bedrock Titan text, and embedding, using OpenSearch vector engine

This sample repository provides a sample code for using RAG (Retrieval augmented generation) method relaying on [Amazon Bedrock](https://aws.amazon.com/bedrock/) [Titan Embeddings Generation 1 (G1)](https://aws.amazon.com/bedrock/titan/) LLM (Large Language Model), for creating text embedding that will be stored in [Amazon OpenSearch](https://aws.amazon.com/opensearch-service/) with [vector engine support](https://aws.amazon.com/about-aws/whats-new/2023/07/vector-engine-amazon-opensearch-serverless-preview/) for assisting with the prompt engineering task for more accurate response from LLMs.

After we successfully loaded embeddings into OpenSearch, we will then start querying our LLM, by using [LangChain](https://www.langchain.com/). We will ask questions, retrieving similar embedding for a more accurate prompt.

You can use `--bedrock-model-id` parameter, to seamlessly choose one of the available foundation model in Amazon Bedrock, that defaults to [Anthropic Claude v2](https://aws.amazon.com/bedrock/claude/) and can be replaced to any other model from any other model provider to choose your best performing foundation model.

Anthropic:

- Claude v2 `python ./ask-bedrock-with-rag.py --ask "How will AI will change our every day life?"`
- Claude v1.3 `python ./ask-bedrock-with-rag.py --bedrock-model-id anthropic.claude-v1 --ask "How will AI will change our every day life?"`
- Claude Instance v1.2 `python ./ask-bedrock-with-rag.py --bedrock-model-id anthropic.claude-instant-v1 --ask "How will AI will change our every day life?"`

AI21 Labs:

- Jurassic-2 Ultra `python ./ask-bedrock-with-rag.py --bedrock-model-id ai21.j2-ultra-v1 --ask "How will AI will change our every day life?"`
- Jurassic-2 Mid `python ./ask-bedrock-with-rag.py --bedrock-model-id ai21.j2-mid-v1 --ask "How will AI will change our every day life?"`

## Prerequisites

1. This was tested on Python 3.11.4
2. It is advise to work on a clean environment, use `virtualenv` or any other virtual environment manager.

    ```bash
    pip install virtualenv
    python -m virtualenv venv
    source ./venv/bin/activate
    ```

3. Install requirements `pip install -r requirements.txt`
4. Install [terraform](https://developer.hashicorp.com/terraform/downloads?product_intent=terraform) to create the OpenSearch cluster

    ```bash
    brew tap hashicorp/tap
    brew install hashicorp/tap/terraform
    ```

5. Go to the Model Access [page](https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess) and enable the foundation models you want to use.

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

    >>Optional arguments:
    >>- `--recreate` for recreating the index in OpenSearch
    >>- `--early-stop` to load only 100 embedded documents into OpenSearch
    >>- `--index` to use a different index than the default **rag**
    >>- `--region` in case you are not using the default **us-east-1**

3. Now that we have embedded text, into our OpenSearch cluster, we can start querying our LLM model Titan text in Amazon Bedrock with RAG

    ```bash
    python ask-bedrock-with-rag.py --ask "your question here"
    ```

    >>Optional arguments:
    >>- `--index` to use a different index than the default **rag**
    >>- `--region` in case you are not using the default **us-east-1**
    >>- `--bedrock-model-id` to choose different models than Anthropic's Claude v2

### Cleanup

```bash
cd ./terraform
terraform destroy # When prompt for confirmation, type yes, and press enter.
```

## Contributing

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
