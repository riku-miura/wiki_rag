import json
import os
import boto3
from typing import Dict, Any

from ...services.chat_service import ChatService
from ...models.rag_session import RagStatus

# Environment variables
RAG_BUCKET = os.environ.get("RAG_BUCKET")
QUERY_TABLE = os.environ.get("QUERY_TABLE")
CHAT_TABLE = os.environ.get("CHAT_TABLE")

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for Chat operations.
    - POST /chat/query: Process a user query (Aggregated response for REST API)
    - GET /chat/{session_id}/history: Get chat history
    
    Note: Standard REST API Gateway buffers responses, so true SSE streaming 
     requires Lambda Function URL or API Gateway HTTP API.
     This handler aggregates the mocked stream from the service.
    """
    print(f"Received event: {json.dumps(event)}")
    
    path = event.get('path', '')
    http_method = event.get('httpMethod', '')
    
    if path.endswith('/query') and http_method == 'POST':
        return handle_query_request(event)
    elif '/history' in path and http_method == 'GET':
        return handle_history_request(event)
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Not Found'})
        }

def handle_query_request(event: Dict[str, Any]) -> Dict[str, Any]:
    try:
        body = json.loads(event.get('body', '{}'))
        session_id = body.get('session_id')
        query_text = body.get('query')
        
        if not session_id or not query_text:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing session_id or query'})
            }
            
        # Initialize Service
        chat_service = ChatService(session_id, RAG_BUCKET)
        
        # Process Query
        # Note: ChatService returns a generator for streaming. 
        # We consume it here for the REST API response.
        response_chunks = []
        for chunk in chat_service.process_query(query_text):
            response_chunks.append(chunk)
            
        full_response = "".join(response_chunks)
        
        # Construct response object
        response_data = {
            "session_id": session_id,
            "response": full_response,
            "metadata": {
                "streaming_supported": False, # Flag for frontend
                "model": chat_service.llm_service.model
            }
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def handle_history_request(event: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Extract session_id from path parameters
        path_params = event.get('pathParameters', {})
        session_id = path_params.get('session_id') if path_params else None
        
        # Fallback parsing from path string if pathParameters missing
        if not session_id:
            # Expected path: /chat/{session_id}/history
            parts = event.get('path', '').split('/')
            if 'chat' in parts and 'history' in parts:
                idx = parts.index('chat')
                if idx + 2 < len(parts) and parts[idx+2] == 'history':
                    session_id = parts[idx+1]

        if not session_id:
             return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing session_id'})
            }

        # TODO: Retrieve real history from DynamoDB (CHAT_TABLE)
        # For Phase 4 MVP, return empty list or mock
        mock_history = [
            {"role": "system", "content": "Chat history not yet persistent (Phase 4 MVP)"}
        ]
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({"history": mock_history})
        }
        
    except Exception as e:
        print(f"Error retrieving history: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
