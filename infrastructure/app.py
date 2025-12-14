#!/usr/bin/env python3
import os
import aws_cdk as cdk

from stacks.compute_stack import ComputeStack
from stacks.storage_stack import StorageStack
from stacks.lambda_stack import LambdaStack
from stacks.frontend_stack import FrontendStack

app = cdk.App()

env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION")
)

app_name = "WikipediaRAG"

# Storage Stack (S3, DynamoDB)
storage = StorageStack(app, f"{app_name}-Storage", env=env)

# Compute Stack (EC2 for Ollama)
compute = ComputeStack(app, f"{app_name}-Compute",
                       vpc=storage.vpc,
                       env=env)

# Lambda Stack (API Gateway, Functions)
lambda_stack = LambdaStack(app, f"{app_name}-Lambda",
                           vpc=storage.vpc,
                           rag_bucket=storage.rag_bucket,
                           content_bucket=storage.content_bucket,
                           rag_table=storage.rag_table,
                           chunk_table=storage.chunk_table,
                           query_table=storage.query_table,
                           chat_table=storage.chat_table,
                           ollama_host=compute.instance.instance_private_ip,
                           env=env)

# Frontend Stack (CloudFront, S3 Hosting)
frontend = FrontendStack(app, f"{app_name}-Frontend",
                         api_gateway=lambda_stack.api,
                         env=env)

app.synth()
