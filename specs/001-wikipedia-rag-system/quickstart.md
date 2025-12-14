# Quickstart Guide: Wikipedia RAG System

**Feature**: 001-wikipedia-rag-system
**Last Updated**: 2025-11-02
**Estimated Setup Time**: 30-60 minutes

## Overview

This guide will help you set up the Wikipedia RAG System on your local machine for development and testing, then deploy it to AWS for production use.

---

## Prerequisites

Before you begin, ensure you have the following tools installed:

### Required Software

1. **Python 3.11+**
   ```bash
   python --version  # Should show 3.11 or higher
   ```
   - Download from: https://www.python.org/downloads/

2. **Docker** (for running Ollama locally)
   ```bash
   docker --version  # Should show 20.10 or higher
   ```
   - Download from: https://docs.docker.com/get-docker/

3. **AWS CLI v2**
   ```bash
   aws --version  # Should show aws-cli/2.x
   ```
   - Installation: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
   - Configure with your credentials:
     ```bash
     aws configure
     # Enter your AWS Access Key ID
     # Enter your AWS Secret Access Key
     # Enter default region (e.g., us-east-1)
     # Enter default output format (json)
     ```

4. **Node.js 18+** (for AWS CDK)
   ```bash
   node --version  # Should show v18 or higher
   npm --version
   ```
   - Download from: https://nodejs.org/

5. **Poetry** (Python dependency manager, recommended)
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   poetry --version
   ```
   - Alternative: Use `pip` and `requirements.txt`

### Optional Tools

- **Git** (for version control)
- **VS Code** or your preferred IDE
- **Postman** or **curl** (for API testing)

---

## Local Development Setup

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/your-org/wiki_rag.git
cd wiki_rag

# Verify you're in the correct directory
ls -la
# Should see: README.md, specs/, infrastructure/, src/, etc.
```

### Step 2: Install Python Dependencies

#### Option A: Using Poetry (Recommended)

```bash
# Install dependencies from pyproject.toml
poetry install

# Activate the virtual environment
poetry shell

# Verify installation
python -c "import langchain; print('LangChain installed successfully')"
```

#### Option B: Using pip

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import langchain; print('LangChain installed successfully')"
```

### Step 3: Run Ollama Locally with Llama 3.2 3B

Ollama is the LLM platform that runs Llama 3.2 3B for inference.

#### Start Ollama Server

```bash
# Pull and run Ollama using Docker
docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ollama_data:/root/.ollama \
  ollama/ollama:latest

# Verify Ollama is running
curl http://localhost:11434/api/version
# Should return: {"version":"0.x.x"}
```

#### Download Llama 3.2 3B Model

```bash
# Pull the Llama 3.2 3B Instruct model (Q4 quantization)
docker exec ollama ollama pull llama3.2:3b-instruct

# Verify the model is downloaded
docker exec ollama ollama list
# Should show: llama3.2:3b-instruct
```

#### Test Ollama

```bash
# Test LLM inference
curl -X POST http://localhost:11434/api/generate -d '{
  "model": "llama3.2:3b-instruct",
  "prompt": "What is Python?",
  "stream": false
}'
# Should return a JSON response with the generated text
```

### Step 4: Set Up Local FAISS

FAISS is already included in the Python dependencies. No additional setup required.

```bash
# Verify FAISS installation
python -c "import faiss; print(f'FAISS version: {faiss.__version__}')"
```

### Step 5: Configure Environment Variables

Create a `.env` file in the project root with the following configuration:

```bash
# .env file
# Copy this template and fill in your values

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b-instruct

# Embedding Model Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# FAISS Configuration
FAISS_INDEX_TYPE=IndexFlatL2  # or IndexIVFFlat for larger datasets

# AWS Configuration (for local development)
AWS_REGION=us-east-1
AWS_PROFILE=default

# S3 Configuration
S3_BUCKET_NAME=wiki-rag-dev-indices  # Will be created during deployment
S3_PREFIX=indices/

# DynamoDB Configuration
DYNAMODB_SESSIONS_TABLE=rag_sessions_dev
DYNAMODB_QUERIES_TABLE=queries_dev
DYNAMODB_MESSAGES_TABLE=chat_messages_dev

# Application Configuration
LOG_LEVEL=INFO
RAG_SESSION_TTL_DAYS=30
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K=3
LLM_TEMPERATURE=0.7
MAX_TOKENS=512

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Create the file:**

```bash
# Copy the template
cat > .env << 'EOF'
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b-instruct
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
AWS_REGION=us-east-1
S3_BUCKET_NAME=wiki-rag-dev-indices
LOG_LEVEL=INFO
API_PORT=8000
EOF

# Load environment variables
source .env  # or use `export $(cat .env | xargs)` on Linux
```

---

## Running Services Locally

### Step 1: Start LLM Service (Ollama)

If not already running from Step 3:

```bash
# Start Ollama container
docker start ollama

# Verify it's running
docker ps | grep ollama
curl http://localhost:11434/api/version
```

### Step 2: Start Backend API

The backend API is built with FastAPI and handles RAG building and chat queries.

```bash
# Navigate to the backend directory
cd src/backend

# Run the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Alternative: Use the provided script
# chmod +x scripts/run_local.sh
# ./scripts/run_local.sh
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify the API is running:**
```bash
# In a new terminal
curl http://localhost:8000/health
# Should return: {"status":"healthy","ollama":"connected","embedding":"loaded"}
```

### Step 3: Start Frontend Dev Server

The frontend is built with Svelte and provides a chat UI.

```bash
# Navigate to the frontend directory
cd src/frontend

# Install dependencies (first time only)
npm install

# Start the dev server
npm run dev

# Alternative port
# npm run dev -- --port 3000
```

**Expected output:**
```
  VITE v5.x ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**Access the UI:**
- Open your browser: http://localhost:5173
- You should see the Wikipedia RAG chat interface

---

## Testing RAG Pipeline

### Step 1: Submit a Test Wikipedia URL

Use the API or the frontend UI to build a RAG session.

#### Using curl:

```bash
# Build a RAG session from a Wikipedia article
curl -X POST http://localhost:8000/v1/rag/build \
  -H "Content-Type: application/json" \
  -d '{
    "source_url": "https://en.wikipedia.org/wiki/Python_(programming_language)"
  }'
```

**Expected response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "created_at": "2025-11-02T10:30:00Z",
  "source_url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
  "estimated_completion": "2025-11-02T10:30:30Z"
}
```

**Save the `session_id` for the next steps.**

### Step 2: Verify Embeddings Created

Check the status of the RAG build:

```bash
# Replace SESSION_ID with the actual value from Step 1
SESSION_ID="550e8400-e29b-41d4-a716-446655440000"

# Check status
curl http://localhost:8000/v1/rag/${SESSION_ID}/status
```

**Expected response (when ready):**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "ready",
  "created_at": "2025-11-02T10:30:00Z",
  "updated_at": "2025-11-02T10:30:25Z",
  "source_url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
  "chunk_count": 58,
  "embedding_dimension": 384,
  "metadata": {
    "article_title": "Python (programming language)",
    "language": "en",
    "content_size": 52340,
    "processing_time_ms": 15240
  }
}
```

**Status should be `ready` before proceeding.**

### Step 3: Test Chat Query

Submit a natural language question:

```bash
# Submit a query
curl -X POST http://localhost:8000/v1/chat/query \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "query_text": "What is Python'\''s main design philosophy?"
  }'
```

**Expected response:**
```json
{
  "query_id": "770e8400-e29b-41d4-a716-446655440002",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "query_text": "What is Python's main design philosophy?",
  "response_text": "Python's main design philosophy emphasizes code readability and simplicity. The language follows the principle of 'There should be one-- and preferably only one --obvious way to do it,' as stated in the Zen of Python.",
  "retrieved_chunks": [
    {
      "chunk_id": "880e8400-e29b-41d4-a716-446655440003",
      "position": 5,
      "similarity_score": 0.87,
      "preview": "The Zen of Python is a collection of 19 guiding principles..."
    }
  ],
  "created_at": "2025-11-02T11:15:30Z",
  "latency_ms": {
    "retrieval": 120,
    "llm_inference": 1850,
    "total": 2010
  }
}
```

**Verify:**
- Response is relevant to the question
- Latency is under 2 seconds (Success Criteria SC-002)
- Retrieved chunks have high similarity scores (>0.7)

### Step 4: Test Frontend UI

1. Open http://localhost:5173 in your browser
2. Click "Build RAG" button
3. Enter Wikipedia URL: `https://en.wikipedia.org/wiki/Python_(programming_language)`
4. Wait for "Ready" status
5. Type a question: "What is Python's main design philosophy?"
6. Verify the response is streamed and displayed correctly

---

## Deployment to AWS

### Step 1: AWS CDK Bootstrap

Bootstrap your AWS account for CDK (first time only):

```bash
# Navigate to infrastructure directory
cd infrastructure

# Install CDK globally
npm install -g aws-cdk

# Verify CDK installation
cdk --version

# Bootstrap your AWS account
cdk bootstrap aws://ACCOUNT_ID/us-east-1

# Replace ACCOUNT_ID with your actual AWS account ID
# Get your account ID:
aws sts get-caller-identity --query Account --output text
```

**Expected output:**
```
⏳  Bootstrapping environment aws://123456789012/us-east-1...
✅  Environment aws://123456789012/us-east-1 bootstrapped.
```

### Step 2: Install Infrastructure Dependencies

```bash
# Install CDK dependencies
npm install

# Install Python dependencies for Lambda functions
cd lambda/rag-builder
poetry install
cd ../chat-query
poetry install
cd ../..
```

### Step 3: Configure Deployment Parameters

Edit `infrastructure/cdk.json` to configure your deployment:

```json
{
  "app": "python app.py",
  "context": {
    "@aws-cdk/core:enableStackNameDuplicates": false,
    "environment": "dev",
    "project_name": "wiki-rag",
    "region": "us-east-1",
    "ec2": {
      "instance_type": "t4g.medium",
      "key_pair_name": "your-key-pair-name",
      "use_spot": false
    },
    "s3": {
      "bucket_name": "wiki-rag-dev-indices-ACCOUNT_ID",
      "lifecycle_days": 30
    },
    "dynamodb": {
      "ttl_days": 30
    },
    "lambda": {
      "architecture": "arm64",
      "memory_mb": 1024,
      "timeout_seconds": 300
    }
  }
}
```

### Step 4: Deploy Infrastructure

```bash
# Synthesize CloudFormation template (dry run)
cdk synth

# Review the changes
cdk diff

# Deploy all stacks
cdk deploy --all

# Or deploy individual stacks
# cdk deploy WikiRagVpcStack
# cdk deploy WikiRagStorageStack
# cdk deploy WikiRagComputeStack
# cdk deploy WikiRagApiStack
```

**Deployment takes 10-15 minutes.**

**Expected output:**
```
✅  WikiRagVpcStack
✅  WikiRagStorageStack
✅  WikiRagComputeStack
✅  WikiRagApiStack

Outputs:
WikiRagApiStack.ApiEndpoint = https://abc123.execute-api.us-east-1.amazonaws.com/prod
WikiRagComputeStack.OllamaInstanceId = i-0123456789abcdef0
WikiRagStorageStack.S3BucketName = wiki-rag-dev-indices-123456789012

Stack ARN:
arn:aws:cloudformation:us-east-1:123456789012:stack/WikiRagApiStack/...
```

### Step 5: Configure Secrets

Store sensitive configuration in AWS Secrets Manager:

```bash
# Store Ollama endpoint (internal EC2 IP)
aws secretsmanager create-secret \
  --name wiki-rag/ollama-endpoint \
  --secret-string "http://10.0.1.50:11434" \
  --region us-east-1

# Store API keys (for Phase 2 authentication)
aws secretsmanager create-secret \
  --name wiki-rag/api-keys \
  --secret-string '{"admin":"your-secure-api-key"}' \
  --region us-east-1
```

### Step 6: Test Deployed API

```bash
# Get the API endpoint from CDK outputs
API_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name WikiRagApiStack \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text)

echo "API Endpoint: $API_ENDPOINT"

# Test health endpoint
curl ${API_ENDPOINT}/health

# Build a RAG session
curl -X POST ${API_ENDPOINT}/v1/rag/build \
  -H "Content-Type: application/json" \
  -d '{
    "source_url": "https://en.wikipedia.org/wiki/Python_(programming_language)"
  }'
```

### Step 7: Deploy Frontend to CloudFront

```bash
# Build the frontend for production
cd src/frontend
npm run build

# Upload to S3
aws s3 sync dist/ s3://wiki-rag-frontend-ACCOUNT_ID/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"
```

**Access your production app:**
- Frontend: https://YOUR_CLOUDFRONT_DOMAIN
- API: https://YOUR_API_GATEWAY_ENDPOINT

---

## Troubleshooting

### Common Issues

#### 1. Ollama Connection Failed

**Symptom:**
```
Error: Could not connect to Ollama at http://localhost:11434
```

**Solution:**
```bash
# Check if Ollama container is running
docker ps | grep ollama

# If not running, start it
docker start ollama

# Check logs
docker logs ollama

# Test connection
curl http://localhost:11434/api/version
```

#### 2. Model Not Found

**Symptom:**
```
Error: model 'llama3.2:3b-instruct' not found
```

**Solution:**
```bash
# Pull the model
docker exec ollama ollama pull llama3.2:3b-instruct

# Verify
docker exec ollama ollama list
```

#### 3. FastAPI Server Won't Start

**Symptom:**
```
ImportError: No module named 'langchain'
```

**Solution:**
```bash
# Ensure virtual environment is activated
poetry shell  # or source venv/bin/activate

# Reinstall dependencies
poetry install  # or pip install -r requirements.txt

# Verify
python -c "import langchain; print('OK')"
```

#### 4. FAISS Index Not Found

**Symptom:**
```
Error: FAISS index not found at s3://bucket/indices/session_id/index.faiss
```

**Solution:**
```bash
# Check if RAG session is ready
curl http://localhost:8000/v1/rag/${SESSION_ID}/status

# If status is 'failed', check the error message
# Rebuild the session if necessary
```

#### 5. AWS CDK Deployment Failed

**Symptom:**
```
Error: Account has not been bootstrapped
```

**Solution:**
```bash
# Bootstrap your account
cdk bootstrap aws://ACCOUNT_ID/us-east-1

# If already bootstrapped, check your AWS credentials
aws sts get-caller-identity
```

#### 6. Out of Memory on EC2

**Symptom:**
```
Error: OOM killed (Out of Memory)
```

**Solution:**
```bash
# Check instance memory usage
ssh ec2-user@YOUR_EC2_IP
free -h

# Upgrade to t4g.large if needed
# Edit infrastructure/stacks/compute_stack.py
# Change instance_type to 't4g.large'
# Redeploy:
cdk deploy WikiRagComputeStack
```

#### 7. Slow Query Response

**Symptom:**
- Queries take >5 seconds to respond

**Solution:**
```bash
# Check LLM performance
time curl -X POST http://localhost:11434/api/generate -d '{
  "model": "llama3.2:3b-instruct",
  "prompt": "Hello",
  "stream": false
}'

# If slow, consider:
# 1. Use Q4 quantization (already default)
# 2. Reduce max_tokens parameter
# 3. Upgrade EC2 instance to t4g.large
```

#### 8. Wikipedia Fetch Failed

**Symptom:**
```
Error: Failed to fetch Wikipedia content: 404
```

**Solution:**
```bash
# Verify the URL is valid
curl -I https://en.wikipedia.org/wiki/Python_(programming_language)
# Should return HTTP 200

# Check for typos in the article name
# Ensure proper URL encoding for special characters
```

---

## Next Steps

Congratulations! You now have a working Wikipedia RAG System.

### Recommended Next Steps:

1. **Explore the API**: Review the OpenAPI specs in `specs/001-wikipedia-rag-system/contracts/`
2. **Customize Chunking**: Experiment with different chunk sizes in `.env`
3. **Monitor Performance**: Set up CloudWatch dashboards for latency metrics
4. **Add Authentication**: Implement API key validation (Phase 2)
5. **Scale Up**: Test with larger Wikipedia articles and multiple concurrent users
6. **Contribute**: Read `CONTRIBUTING.md` and submit improvements

### Additional Resources:

- **Data Model**: See `specs/001-wikipedia-rag-system/data-model.md`
- **API Contracts**: See `specs/001-wikipedia-rag-system/contracts/`
- **Research**: See `specs/001-wikipedia-rag-system/research.md`
- **Constitution**: See `.specify/constitution.md`

---

## Cost Monitoring

To ensure you stay within the $50/month budget:

### Set Up AWS Budgets

```bash
# Create a budget alert at $40 (80% of $50)
aws budgets create-budget \
  --account-id ACCOUNT_ID \
  --budget file://budget.json \
  --notifications-with-subscribers file://notifications.json
```

**budget.json:**
```json
{
  "BudgetName": "WikiRAG-Monthly-Budget",
  "BudgetLimit": {
    "Amount": "50",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
```

**notifications.json:**
```json
[
  {
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80
    },
    "Subscribers": [
      {
        "SubscriptionType": "EMAIL",
        "Address": "your-email@example.com"
      }
    ]
  }
]
```

### Monitor Costs

```bash
# View current month costs
aws ce get-cost-and-usage \
  --time-period Start=$(date -d "$(date +%Y-%m-01)" +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics "UnblendedCost" \
  --region us-east-1
```

### Cost Optimization Tips

1. **Use Spot Instances**: 70% savings on EC2 (set `use_spot: true` in `cdk.json`)
2. **Stop EC2 at Night**: Save 50% by running only 12 hours/day
3. **Minimize S3 Requests**: Cache FAISS indices in memory
4. **Use ARM Lambda**: 20% cheaper than x86
5. **Delete Old Sessions**: Let TTL expire unused RAG sessions

---

## Development Workflow

### Make Code Changes

```bash
# Edit backend code
vim src/backend/services/rag_builder.py

# Test locally
pytest tests/

# Run linting
ruff check src/

# Format code
black src/
```

### Deploy Updates

```bash
# Deploy backend changes (Lambda)
cd infrastructure
cdk deploy WikiRagApiStack

# Deploy frontend changes
cd src/frontend
npm run build
aws s3 sync dist/ s3://wiki-rag-frontend-ACCOUNT_ID/
```

### View Logs

```bash
# Local logs (FastAPI)
tail -f logs/app.log

# AWS Lambda logs
aws logs tail /aws/lambda/rag-builder --follow

# EC2 Ollama logs
ssh ec2-user@YOUR_EC2_IP
docker logs -f ollama
```

---

## Support

If you encounter issues not covered in this guide:

1. Check the troubleshooting section above
2. Review the data model and API contracts
3. Search existing GitHub issues
4. Create a new issue with detailed error logs
5. Contact the development team

---

**Happy Building!**
