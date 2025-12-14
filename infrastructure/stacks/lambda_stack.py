from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
)
from constructs import Construct

class LambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, 
                 vpc: ec2.Vpc, 
                 rag_bucket: s3.Bucket,
                 content_bucket: s3.Bucket,
                 rag_table: dynamodb.Table,
                 chunk_table: dynamodb.Table,
                 query_table: dynamodb.Table,
                 chat_table: dynamodb.Table,
                 ollama_host: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Shared Lambda Layer (dependencies)
        # Note: In a real scenario, this would be built from requirements.txt
        # For now, we assume a pre-built layer or just use the code
        
        # RAG Builder Lambda
        self.rag_builder_fn = _lambda.Function(self, "RagBuilderFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_handlers.rag_builder_handler.handler",
            code=_lambda.Code.from_asset("../backend/src/api"),
            architecture=_lambda.Architecture.ARM_64,
            memory_size=1024,
            timeout=Duration.seconds(300),
            vpc=vpc,
            environment={
                "RAG_BUCKET": rag_bucket.bucket_name,
                "CONTENT_BUCKET": content_bucket.bucket_name,
                "RAG_TABLE": rag_table.table_name,
                "CHUNK_TABLE": chunk_table.table_name,
                "OLLAMA_HOST": f"http://{ollama_host}:11434"
            }
        )

        # Chat Lambda
        self.chat_fn = _lambda.Function(self, "ChatFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_handlers.chat_handler.handler",
            code=_lambda.Code.from_asset("../backend/src/api"),
            architecture=_lambda.Architecture.ARM_64,
            memory_size=512,
            timeout=Duration.seconds(60),
            vpc=vpc,
            environment={
                "RAG_BUCKET": rag_bucket.bucket_name,
                "QUERY_TABLE": query_table.table_name,
                "CHAT_TABLE": chat_table.table_name,
                "OLLAMA_HOST": f"http://{ollama_host}:11434"
            }
        )

        # Grant permissions
        rag_bucket.grant_read_write(self.rag_builder_fn)
        rag_bucket.grant_read(self.chat_fn)
        content_bucket.grant_read_write(self.rag_builder_fn)
        
        rag_table.grant_read_write_data(self.rag_builder_fn)
        rag_table.grant_read_data(self.chat_fn)
        chunk_table.grant_read_write_data(self.rag_builder_fn)
        
        query_table.grant_read_write_data(self.chat_fn)
        chat_table.grant_read_write_data(self.chat_fn)

        # API Gateway
        self.api = apigateway.RestApi(self, "WikipediaRagApi",
            rest_api_name="Wikipedia RAG API",
            description="API for Wikipedia RAG System",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS
            )
        )

        # API Routes
        rag = self.api.root.add_resource("rag")
        rag_build = rag.add_resource("build")
        rag_build.add_method("POST", apigateway.LambdaIntegration(self.rag_builder_fn))

        rag_status = rag.add_resource("{session_id}").add_resource("status")
        rag_status.add_method("GET", apigateway.LambdaIntegration(self.rag_builder_fn))

        chat = self.api.root.add_resource("chat")
        chat_query = chat.add_resource("query")
        chat_query.add_method("POST", apigateway.LambdaIntegration(self.chat_fn))
