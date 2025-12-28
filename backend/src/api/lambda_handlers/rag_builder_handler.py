import json
import os
from datetime import datetime

# Import services - assuming Lambda layer or packages are correct
from ...services.rag_builder import RagBuilderService
from ...models.rag_session import RagSession

# Initialize outside handler for warm starts
RAG_BUCKET = os.environ.get("RAG_BUCKET")
builder_service = RagBuilderService(RAG_BUCKET)

def handler(event, context):
    """
    Lambda handler for RAG building operations.
    Supports POST /rag/build
    """
    print(f"Received event: {json.dumps(event)}")
    
    path = event.get('path', '')
    http_method = event.get('httpMethod', '')
    
    if path.endswith('/rag/build') and http_method == 'POST':
        return handle_build_request(event)
    elif path.endswith('/status') and http_method == 'GET':
        # TODO: Implement status check (requires DynamoDB integration)
        return {
            'statusCode': 501,
            'body': json.dumps({'error': 'Not Implemented'})
        }
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Not Found'})
        }

def handle_build_request(event):
    try:
        body = json.loads(event.get('body', '{}'))
        source_url = body.get('url')
        
        if not source_url:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing url parameter'})
            }
            
        # Run sync build for now (Phase 1 simplicity)
        # In production, this might trigger an async Step Function
        session = builder_service.build_rag_session(source_url)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': session.json()
        }
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
