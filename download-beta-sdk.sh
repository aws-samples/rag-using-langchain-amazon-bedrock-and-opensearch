#!/bin/sh

echo "Creating directory"
mkdir -p ./dependencies && \
cd ./dependencies && \
echo "Downloading dependencies"
curl -sS https://d2eo22ngex1n9g.cloudfront.net/Documentation/SDK/bedrock-python-sdk.zip > sdk.zip && \
echo "Unpacking dependencies"
unzip -o -q sdk.zip && \
rm sdk.zip

pip install --force-reinstall --no-cache-dir awscli-1.29.21-py3-none-any.whl
pip install --force-reinstall --no-cache-dir boto3-1.28.21-py3-none-any.whl 
pip install --force-reinstall --no-cache-dir botocore-1.31.21-py3-none-any.whl 