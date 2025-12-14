from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3_deployment as s3deploy,
    aws_apigateway as apigateway,
)
from constructs import Construct

class FrontendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, api_gateway: apigateway.RestApi, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 Bucket for Frontend Hosting
        self.frontend_bucket = s3.Bucket(self, "FrontendBucket",
            website_index_document="index.html",
            website_error_document="index.html",
            public_read_access=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False
            )
        )

        # CloudFront Distribution
        self.distribution = cloudfront.Distribution(self, "FrontendDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(self.frontend_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            additional_behaviors={
                "/api/*": cloudfront.BehaviorOptions(
                    origin=origins.RestApiOrigin(api_gateway),
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER_EXCEPT_HOST_HEADER
                )
            }
        )
