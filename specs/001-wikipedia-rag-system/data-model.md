# Data Model: Wikipedia RAG System

**Feature**: 001-wikipedia-rag-system
**Created**: 2025-11-02
**Status**: Draft

## Overview

This document defines the core data models for the Wikipedia RAG System. The system uses a combination of S3 (for vector indices and metadata), DynamoDB (for session state and query history), and in-memory FAISS indices for vector search.

## Core Data Models

### 1. RAG Session Model

Represents an indexed Wikipedia article that can be queried through the RAG system.

#### Schema

```python
{
    "session_id": "uuid",           # Primary key
    "source_url": "string",         # Wikipedia article URL
    "status": "enum",               # processing | ready | failed | expired
    "created_at": "timestamp",      # ISO 8601 format
    "updated_at": "timestamp",      # ISO 8601 format
    "chunk_count": "integer",       # Number of text chunks
    "embedding_dimension": "integer", # Vector dimension (384 for all-MiniLM-L6-v2)
    "s3_index_path": "string",      # S3 path to FAISS index file
    "metadata": {
        "article_title": "string",  # Wikipedia article title
        "language": "string",       # Article language code (e.g., "en")
        "content_size": "integer",  # Original content size in bytes
        "processing_time_ms": "integer", # Time to build RAG
        "model_version": "string"   # Embedding model version
    }
}
```

#### Field Descriptions

- **session_id**: UUID v4 generated when RAG build is initiated
- **source_url**: Full Wikipedia URL (e.g., `https://en.wikipedia.org/wiki/Python_(programming_language)`)
- **status**: Current processing state (see State Transitions below)
- **created_at**: Timestamp when RAG build was initiated
- **updated_at**: Timestamp of last status update
- **chunk_count**: Total number of text chunks created from the article
- **embedding_dimension**: Vector dimension (always 384 for all-MiniLM-L6-v2)
- **s3_index_path**: S3 URI to FAISS index (e.g., `s3://bucket/indices/{session_id}/index.faiss`)
- **metadata.article_title**: Extracted from Wikipedia page title
- **metadata.language**: Language code from Wikipedia URL
- **metadata.content_size**: Original article text size in bytes
- **metadata.processing_time_ms**: Total time to process and index
- **metadata.model_version**: Embedding model identifier (e.g., `all-MiniLM-L6-v2`)

#### Validation Rules

1. **session_id**:
   - Must be valid UUID v4 format
   - Must be unique across all sessions

2. **source_url**:
   - Must be valid URL format
   - Must match pattern: `https?://(en|[a-z]{2})\.wikipedia\.org/wiki/.+`
   - Must return HTTP 200 when fetched
   - Maximum length: 2048 characters

3. **status**:
   - Must be one of: `processing`, `ready`, `failed`, `expired`
   - Initial value must be `processing`

4. **created_at / updated_at**:
   - Must be ISO 8601 format with timezone
   - `updated_at` must be >= `created_at`

5. **chunk_count**:
   - Must be positive integer
   - Typical range: 10-500 for standard Wikipedia articles
   - Maximum: 10,000 chunks

6. **embedding_dimension**:
   - Must be 384 (for all-MiniLM-L6-v2)
   - Future models may use different dimensions

7. **s3_index_path**:
   - Must be valid S3 URI format
   - Must point to existing object when status is `ready`

8. **metadata.language**:
   - Must be valid ISO 639-1 language code
   - Phase 1 supports: `en` only

9. **metadata.content_size**:
   - Must be positive integer
   - Maximum: 10 MB (10,485,760 bytes)

#### State Transitions

```
[Initial] --> processing --> ready
                    |
                    +--> failed

ready --> expired (after 30 days)
```

**State Descriptions**:

1. **processing**: RAG build in progress
   - Wikipedia content is being fetched
   - Text is being chunked
   - Embeddings are being generated
   - FAISS index is being created and uploaded to S3

2. **ready**: RAG session is ready for queries
   - All chunks have been embedded
   - FAISS index is stored in S3
   - Session can accept chat queries

3. **failed**: RAG build encountered an error
   - Invalid Wikipedia URL
   - Network timeout during fetch
   - Embedding generation failure
   - S3 upload failure
   - Metadata includes error details in `error_message` field

4. **expired**: Session exceeded retention period
   - 30 days since `created_at`
   - S3 objects may be archived or deleted
   - Queries will return 404

**Transition Rules**:

- `processing` can only transition to `ready` or `failed`
- `ready` can only transition to `expired`
- `failed` and `expired` are terminal states (no further transitions)
- `updated_at` must be set on every state transition

#### Storage

- **Primary Store**: DynamoDB table `rag_sessions`
- **Partition Key**: `session_id`
- **TTL**: 30 days from `created_at` (auto-deletion)
- **Secondary Index**: GSI on `status` for querying active sessions

---

### 2. Text Chunk Model

Represents a segment of Wikipedia article content with its embedding vector.

#### Schema

```python
{
    "chunk_id": "uuid",             # Primary key
    "session_id": "uuid",           # Foreign key to RAG Session
    "content": "string",            # Text content
    "position": "integer",          # Order in document (0-based)
    "embedding_vector": [float],    # 384-dimensional vector
    "metadata": {
        "section_title": "string",  # Section heading (if any)
        "word_count": "integer",    # Number of words in chunk
        "char_count": "integer"     # Number of characters
    }
}
```

#### Field Descriptions

- **chunk_id**: UUID v4 generated when chunk is created
- **session_id**: Reference to parent RAG Session
- **content**: Raw text content of the chunk
- **position**: Sequential position in original document (0 = first chunk)
- **embedding_vector**: 384-dimensional float vector from all-MiniLM-L6-v2
- **metadata.section_title**: Wikipedia section heading (e.g., "History", "Etymology")
- **metadata.word_count**: Number of words in chunk
- **metadata.char_count**: Number of characters in chunk

#### Validation Rules

1. **chunk_id**:
   - Must be valid UUID v4 format
   - Must be unique within session

2. **session_id**:
   - Must reference existing RAG Session
   - Session must be in `processing` or `ready` state

3. **content**:
   - Must be non-empty string
   - Length: 100-2000 characters (typical)
   - Maximum length: 5000 characters

4. **position**:
   - Must be non-negative integer
   - Must be unique within session
   - Should form continuous sequence: 0, 1, 2, ...

5. **embedding_vector**:
   - Must have exactly 384 elements
   - Each element must be float32
   - Vector should be normalized (L2 norm ≈ 1.0)

6. **metadata.section_title**:
   - Optional field
   - Maximum length: 500 characters

7. **metadata.word_count**:
   - Must be positive integer
   - Typical range: 50-400 words

8. **metadata.char_count**:
   - Must be positive integer
   - Must match `len(content)`

#### Chunking Strategy

Chunks are created using `RecursiveCharacterTextSplitter`:

```python
chunk_size = 1000          # Target characters per chunk
chunk_overlap = 200        # Overlap to preserve context
separators = ["\n\n", "\n", " ", ""]  # Split on paragraphs first
```

**Example**:
- 50KB article → ~50-60 chunks
- Each chunk: ~200-250 words
- Overlap ensures no context is lost at boundaries

#### Storage

- **Primary Store**: Embedded within FAISS index file in S3
- **Format**: FAISS IndexFlatL2 or IndexIVFFlat
- **S3 Path**: `s3://bucket/indices/{session_id}/index.faiss`
- **Metadata Store**: DynamoDB table `text_chunks` (for debugging/analytics)
  - Partition Key: `session_id`
  - Sort Key: `position`

---

### 3. Query Model

Represents a user question submitted to the RAG system.

#### Schema

```python
{
    "query_id": "uuid",             # Primary key
    "session_id": "uuid",           # Foreign key to RAG Session
    "query_text": "string",         # User's question
    "retrieved_chunks": [           # Top-k chunks used for context
        {
            "chunk_id": "uuid",
            "position": "integer",
            "similarity_score": "float"
        }
    ],
    "response_text": "string",      # LLM generated answer
    "created_at": "timestamp",      # Query timestamp
    "latency_ms": {
        "retrieval": "integer",     # Time to retrieve chunks
        "llm_inference": "integer", # Time to generate response
        "total": "integer"          # End-to-end latency
    },
    "metadata": {
        "model": "string",          # LLM model used
        "top_k": "integer",         # Number of chunks retrieved
        "temperature": "float"      # LLM temperature setting
    }
}
```

#### Field Descriptions

- **query_id**: UUID v4 generated when query is submitted
- **session_id**: Reference to RAG Session being queried
- **query_text**: User's natural language question
- **retrieved_chunks**: Array of chunks retrieved from FAISS
  - **chunk_id**: Reference to Text Chunk
  - **position**: Position in original document
  - **similarity_score**: Cosine similarity (0.0-1.0)
- **response_text**: Answer generated by Llama 3.2 3B
- **created_at**: Timestamp when query was received
- **latency_ms**: Performance metrics
  - **retrieval**: Time to search FAISS and retrieve chunks
  - **llm_inference**: Time for LLM to generate response
  - **total**: End-to-end request latency
- **metadata.model**: LLM model identifier (e.g., `llama3.2:3b-instruct`)
- **metadata.top_k**: Number of chunks retrieved (typically 3-5)
- **metadata.temperature**: LLM temperature parameter (0.0-1.0)

#### Validation Rules

1. **query_id**:
   - Must be valid UUID v4 format
   - Must be unique across all queries

2. **session_id**:
   - Must reference existing RAG Session
   - Session status must be `ready`

3. **query_text**:
   - Must be non-empty string
   - Maximum length: 1000 characters
   - Minimum length: 3 characters

4. **retrieved_chunks**:
   - Array must contain 1-10 elements
   - Typical size: 3-5 chunks (top_k parameter)
   - Must be sorted by similarity_score (descending)

5. **retrieved_chunks[].similarity_score**:
   - Must be float in range [0.0, 1.0]
   - Higher score = more relevant

6. **response_text**:
   - Must be non-empty string
   - Typical length: 100-500 words
   - Maximum length: 4000 characters

7. **latency_ms.retrieval**:
   - Must be positive integer
   - Typical range: 50-500ms
   - Success Criteria: < 2000ms

8. **latency_ms.llm_inference**:
   - Must be positive integer
   - Typical range: 500-3000ms

9. **latency_ms.total**:
   - Must equal retrieval + llm_inference + overhead
   - Success Criteria SC-002: < 2000ms for first chunk

10. **metadata.top_k**:
    - Must be integer in range [1, 10]
    - Default: 3

11. **metadata.temperature**:
    - Must be float in range [0.0, 1.0]
    - Default: 0.7

#### Query Processing Flow

1. **Validation**: Verify session exists and is ready
2. **Embedding**: Generate query embedding using all-MiniLM-L6-v2
3. **Retrieval**: Search FAISS index for top-k similar chunks
4. **Context Assembly**: Combine retrieved chunks into context
5. **LLM Inference**: Call Llama 3.2 3B with context + query
6. **Response Streaming**: Stream tokens back to user
7. **Persistence**: Save query record to DynamoDB

#### Storage

- **Primary Store**: DynamoDB table `queries`
- **Partition Key**: `session_id`
- **Sort Key**: `created_at` (for chronological ordering)
- **TTL**: 30 days from `created_at`

---

### 4. Chat Message Model

Represents a single message in the conversation history.

#### Schema

```python
{
    "message_id": "uuid",           # Primary key
    "session_id": "uuid",           # Foreign key to RAG Session
    "query_id": "uuid",             # Foreign key to Query (if assistant)
    "content": "string",            # Message text
    "role": "enum",                 # user | assistant
    "created_at": "timestamp",      # Message timestamp
    "metadata": {
        "streamed": "boolean",      # Whether response was streamed
        "token_count": "integer"    # Number of tokens (if assistant)
    }
}
```

#### Field Descriptions

- **message_id**: UUID v4 generated when message is created
- **session_id**: Reference to RAG Session
- **query_id**: Reference to Query (null for user messages)
- **content**: Message text content
- **role**: Message sender (user or assistant)
- **created_at**: Timestamp when message was created
- **metadata.streamed**: Whether this was a streamed response
- **metadata.token_count**: Token count for LLM responses

#### Validation Rules

1. **message_id**:
   - Must be valid UUID v4 format
   - Must be unique across all messages

2. **session_id**:
   - Must reference existing RAG Session

3. **query_id**:
   - Required if role is `assistant`
   - Must be null if role is `user`

4. **content**:
   - Must be non-empty string
   - Maximum length: 10,000 characters

5. **role**:
   - Must be `user` or `assistant`
   - Messages should alternate (user → assistant → user)

6. **metadata.streamed**:
   - Boolean flag
   - Default: true for assistant messages

7. **metadata.token_count**:
   - Positive integer
   - Only present for assistant messages

#### Chat History Structure

Messages are organized chronologically per session:

```
[
  { role: "user", content: "What is Python?" },
  { role: "assistant", content: "Python is a high-level...", query_id: "..." },
  { role: "user", content: "When was it created?" },
  { role: "assistant", content: "Python was created in 1991...", query_id: "..." }
]
```

#### Storage

- **Primary Store**: DynamoDB table `chat_messages`
- **Partition Key**: `session_id`
- **Sort Key**: `created_at`
- **Query Pattern**: Fetch all messages for a session, ordered by time
- **TTL**: 30 days from `created_at`

---

## Relationships

### Entity Relationship Diagram

```
RAG Session (1) ──── (N) Text Chunk
     │
     │
     └── (N) Query
            │
            └── (N) Retrieved Chunks (references Text Chunk)
     │
     │
     └── (N) Chat Message
```

### Foreign Key Constraints

1. **Text Chunk → RAG Session**:
   - `session_id` must reference valid `RAG Session`
   - Cascade delete: When session is deleted, all chunks are deleted

2. **Query → RAG Session**:
   - `session_id` must reference valid `RAG Session` with status `ready`
   - Cascade delete: When session is deleted, all queries are deleted

3. **Query.retrieved_chunks → Text Chunk**:
   - Each `chunk_id` must reference valid `Text Chunk` in the same session
   - No cascade (queries retain chunk references for analytics)

4. **Chat Message → RAG Session**:
   - `session_id` must reference valid `RAG Session`
   - Cascade delete: When session is deleted, all messages are deleted

5. **Chat Message → Query**:
   - `query_id` must reference valid `Query` (if role is `assistant`)
   - No cascade (messages can exist without queries)

---

## Data Lifecycle

### RAG Session Lifecycle

1. **Creation** (0s):
   - User submits Wikipedia URL
   - `session_id` generated
   - Status: `processing`
   - Lambda triggers RAG build

2. **Processing** (10-60s):
   - Wikipedia content fetched
   - Text chunked into segments
   - Embeddings generated
   - FAISS index created
   - Index uploaded to S3

3. **Ready** (0-30 days):
   - Status: `ready`
   - Accepts chat queries
   - FAISS index in S3
   - DynamoDB record active

4. **Expiration** (30 days):
   - Status: `expired`
   - S3 objects archived to Glacier
   - DynamoDB record deleted (TTL)
   - Queries return 404

### Query Lifecycle

1. **Submission** (0s):
   - User submits query with `session_id`
   - `query_id` generated
   - Validation checks

2. **Processing** (0.5-2s):
   - Query embedded
   - FAISS search executed
   - Context assembled
   - LLM inference

3. **Response** (1-5s):
   - Tokens streamed to client
   - `response_text` accumulated
   - Latency metrics recorded

4. **Persistence** (immediate):
   - Query record saved to DynamoDB
   - Chat messages created

5. **Retention** (30 days):
   - Query stored for analytics
   - Deleted by TTL after 30 days

---

## Indexing Strategy

### DynamoDB Indices

**Table: `rag_sessions`**
- Primary Key: `session_id` (partition key)
- GSI: `status-index`
  - Partition Key: `status`
  - Sort Key: `created_at`
  - Use Case: List all sessions by status

**Table: `text_chunks`** (optional, for debugging)
- Primary Key: `session_id` (partition key), `position` (sort key)
- Use Case: Retrieve chunks in order

**Table: `queries`**
- Primary Key: `session_id` (partition key), `created_at` (sort key)
- Use Case: Fetch query history for a session

**Table: `chat_messages`**
- Primary Key: `session_id` (partition key), `created_at` (sort key)
- Use Case: Fetch conversation history

### FAISS Index Configuration

**Index Type**: `IndexFlatL2` (Phase 1) or `IndexIVFFlat` (Phase 2)

**Phase 1 (Small datasets < 10K vectors)**:
```python
import faiss

dimension = 384
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)  # Add all chunk embeddings
```

**Phase 2 (Large datasets > 10K vectors)**:
```python
# Use IVF for faster search with slight accuracy tradeoff
nlist = 100  # Number of clusters
quantizer = faiss.IndexFlatL2(dimension)
index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
index.train(embeddings)
index.add(embeddings)
```

---

## Performance Considerations

### Storage Estimates

**Per RAG Session** (50KB Wikipedia article):
- DynamoDB record: ~1KB
- Text chunks: 50-60 chunks × 1KB = 50-60KB (DynamoDB)
- FAISS index: ~2MB (S3)
- Total: ~2.1MB per session

**Per Query**:
- DynamoDB record: ~2KB
- Chat messages: 2 messages × 0.5KB = 1KB
- Total: ~3KB per query

**100 Sessions + 1000 Queries**:
- DynamoDB: 100 × 61KB + 1000 × 3KB = 9.1MB
- S3: 100 × 2MB = 200MB
- Total: ~209MB

### Query Performance Targets

Based on Success Criteria:

- **SC-001**: RAG build < 60s for 50KB articles
  - Fetch: 2-5s
  - Chunking: 1-2s
  - Embedding: 3-10s
  - FAISS build: 1-2s
  - S3 upload: 1-3s
  - **Total**: 8-22s (buffer: 60s)

- **SC-002**: First response chunk < 2s
  - S3 download: 100-300ms
  - FAISS search: 50-200ms
  - LLM first token: 500-1500ms
  - **Total**: 650-2000ms

---

## Error Handling

### Failed RAG Sessions

When status is `failed`, metadata includes:

```python
{
    "error_code": "string",      # FETCH_FAILED | EMBED_FAILED | S3_FAILED
    "error_message": "string",   # Human-readable error
    "error_timestamp": "timestamp",
    "retry_count": "integer"     # Number of retry attempts
}
```

**Error Codes**:

1. **FETCH_FAILED**: Could not retrieve Wikipedia content
   - Invalid URL (404)
   - Network timeout
   - Wikipedia API error

2. **EMBED_FAILED**: Embedding generation error
   - Model loading failure
   - Out of memory
   - Malformed content

3. **S3_FAILED**: Could not upload to S3
   - Permissions error
   - Network timeout
   - Bucket not found

4. **INVALID_CONTENT**: Content validation failed
   - Empty article
   - Non-text content
   - Unsupported language

### Query Errors

When query fails, response includes:

```python
{
    "error": true,
    "error_code": "string",
    "error_message": "string",
    "query_id": "uuid"  # Still generated for tracking
}
```

**Error Codes**:

1. **SESSION_NOT_FOUND**: Invalid or expired session_id
2. **SESSION_NOT_READY**: Session status is not `ready`
3. **RETRIEVAL_FAILED**: FAISS search error
4. **LLM_UNAVAILABLE**: Ollama service down
5. **TIMEOUT**: Query exceeded timeout threshold

---

## Compliance with Constitution

This data model adheres to the project constitution:

- **Modularity**: Clear separation between RAG building and query processing
- **Privacy First**: All data stored in private AWS account (S3, DynamoDB)
- **Cost Efficiency**: TTL for auto-deletion, S3 lifecycle policies
- **Observability**: Latency metrics in Query model for monitoring

---

## Next Steps

1. Implement DynamoDB table definitions in AWS CDK
2. Create S3 bucket structure with lifecycle policies
3. Define API contracts that use these data models
4. Implement validation logic in Lambda functions
5. Set up CloudWatch alarms for error rates and latency
