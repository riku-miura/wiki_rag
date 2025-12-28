# Implementation Tasks: Wikipedia RAG System

**Feature**: 001-wikipedia-rag-system
**Created**: 2025-11-02
**Status**: Ready for Implementation

## Overview

This document provides a dependency-ordered, actionable task list for implementing the Wikipedia RAG System. Tasks are organized by phase and user story priority (P1 → P2 → P3) to enable incremental delivery and independent testing.

**Total Tasks**: 78 tasks across 6 phases

## Task Format

Each task follows this format:
```
- [ ] T### [P?] [Story?] Description with exact file path
```

- **Checkbox**: `- [ ]` for tracking completion
- **Task ID**: T001, T002, etc. (sequential)
- **[P] marker**: Present ONLY if task can run in parallel with adjacent tasks
- **[Story] label**: [US1], [US2], [US3] for user story tasks
- **Description**: Clear action + absolute file path

## Dependencies Summary

```
Phase 1: Setup
    ↓
Phase 2: Foundational (AWS Infrastructure) ← BLOCKS all user stories
    ↓
    ├─→ Phase 3: User Story 1 (P1) - Build RAG [Independent]
    ├─→ Phase 4: User Story 2 (P2) - Chat with RAG [Independent]
    └─→ Phase 3 + Phase 4 → Phase 5: User Story 3 (P3) - Profile Integration

Phase 6: Polish & Cross-Cutting (runs after all user stories)
```

**Key Points**:
- Phase 1 and Phase 2 are sequential and block everything
- Phase 3 (US1) and Phase 4 (US2) can start in parallel after Phase 2 completes
- Phase 5 (US3) requires Phase 3 and Phase 4 to be complete
- Phase 6 runs after all user stories are functional

---

## Phase 1: Setup (5 tasks)

**Goal**: Initialize project structure and development environment

- [ ] T001 [P] Create project directory structure (backend/, frontend/, infrastructure/, scripts/, docs/)
- [ ] T002 [P] Initialize Python project with pyproject.toml and requirements.txt at /home/riku-miura/project/wiki_rag/requirements.txt
- [ ] T003 [P] Initialize frontend with package.json and Svelte config at /home/riku-miura/project/wiki_rag/frontend/package.json
- [ ] T004 [P] Create .env.example file with AWS configuration templates at /home/riku-miura/project/wiki_rag/.env.example
- [ ] T005 Setup Python linting/formatting (black, flake8, mypy) with configuration files at /home/riku-miura/project/wiki_rag/.flake8

**Parallel Execution**: Tasks T001-T004 can run in parallel (independent file operations)

---

## Phase 2: Foundational Infrastructure (15 tasks)

**Goal**: Deploy AWS infrastructure (BLOCKS all user stories)

### AWS CDK Setup (2 tasks)

- [ ] T006 Initialize AWS CDK project at /home/riku-miura/project/wiki_rag/infrastructure/app.py
- [ ] T007 Create CDK configuration file at /home/riku-miura/project/wiki_rag/infrastructure/cdk.json

### Infrastructure Stacks (4 tasks)

- [ ] T008 [P] Create ComputeStack for EC2 Ollama instance at /home/riku-miura/project/wiki_rag/infrastructure/stacks/compute_stack.py
- [ ] T009 [P] Create StorageStack for S3 buckets and DynamoDB tables at /home/riku-miura/project/wiki_rag/infrastructure/stacks/storage_stack.py
- [ ] T010 [P] Create LambdaStack for Lambda functions and API Gateway at /home/riku-miura/project/wiki_rag/infrastructure/stacks/lambda_stack.py
- [ ] T011 [P] Create FrontendStack for S3 + CloudFront hosting at /home/riku-miura/project/wiki_rag/infrastructure/stacks/frontend_stack.py

**Parallel Execution**: Tasks T008-T011 can run in parallel (different stack files)

### EC2 and LLM Setup (3 tasks)

- [ ] T012 Create Ollama installation script at /home/riku-miura/project/wiki_rag/scripts/setup_ollama.sh
- [ ] T013 Configure EC2 user-data in ComputeStack to run setup_ollama.sh at /home/riku-miura/project/wiki_rag/infrastructure/stacks/compute_stack.py
- [ ] T014 Create VPC and security group configuration for EC2 instance at /home/riku-miura/project/wiki_rag/infrastructure/stacks/compute_stack.py

### Storage Configuration (3 tasks)

- [ ] T015 Define DynamoDB table schemas (rag_sessions, text_chunks, queries, chat_messages) at /home/riku-miura/project/wiki_rag/infrastructure/stacks/storage_stack.py
- [ ] T016 Configure S3 buckets with lifecycle policies (vector-indices, raw-content) at /home/riku-miura/project/wiki_rag/infrastructure/stacks/storage_stack.py
- [ ] T017 Set up S3 bucket versioning and encryption at /home/riku-miura/project/wiki_rag/infrastructure/stacks/storage_stack.py

### API Gateway and Networking (3 tasks)

- [ ] T018 Create API Gateway REST API configuration at /home/riku-miura/project/wiki_rag/infrastructure/stacks/lambda_stack.py
- [ ] T019 Configure API Gateway CORS settings for frontend access at /home/riku-miura/project/wiki_rag/infrastructure/stacks/lambda_stack.py
- [ ] T020 Deploy CDK stacks to AWS (cdk deploy --all)

---

## Phase 3: User Story 1 - Build RAG from Wikipedia URL (25 tasks)

**Priority**: P1 (MVP - Foundational capability)
**Goal**: User submits Wikipedia URL → receives session_id with "ready" status
**Independent Test**: Submit Wikipedia URL via API, verify session_id returned with "ready" status

### Data Models (2 tasks)

- [ ] T021 [P] [US1] Create RAG Session model at /home/riku-miura/project/wiki_rag/backend/src/models/rag_session.py
- [ ] T022 [P] [US1] Create Text Chunk model at /home/riku-miura/project/wiki_rag/backend/src/models/text_chunk.py

**Parallel Execution**: T021 and T022 can run in parallel (different model files)

### Utility Modules (3 tasks)

- [ ] T023 [P] [US1] Create S3 client wrapper at /home/riku-miura/project/wiki_rag/backend/src/utils/s3_client.py
- [ ] T024 [P] [US1] Create input validation module at /home/riku-miura/project/wiki_rag/backend/src/utils/validation.py
- [ ] T025 [P] [US1] Create error handling module at /home/riku-miura/project/wiki_rag/backend/src/utils/error_handling.py

**Parallel Execution**: T023-T025 can run in parallel (different utility files)

### Wikipedia Fetching Service (3 tasks)

- [ ] T026 [US1] Create Wikipedia fetcher service skeleton at /home/riku-miura/project/wiki_rag/backend/src/services/wikipedia_fetcher.py
- [ ] T027 [US1] Implement Wikipedia URL validation and parsing at /home/riku-miura/project/wiki_rag/backend/src/services/wikipedia_fetcher.py
- [ ] T028 [US1] Implement Wikipedia content fetching with error handling at /home/riku-miura/project/wiki_rag/backend/src/services/wikipedia_fetcher.py

### Embedding Service (3 tasks)

- [ ] T029 [US1] Create embedding service skeleton at /home/riku-miura/project/wiki_rag/backend/src/services/embedding_service.py
- [ ] T030 [US1] Implement all-MiniLM-L6-v2 model loading at /home/riku-miura/project/wiki_rag/backend/src/services/embedding_service.py
- [ ] T031 [US1] Implement batch embedding generation with optimization at /home/riku-miura/project/wiki_rag/backend/src/services/embedding_service.py

### Vector Store Service (4 tasks)

- [ ] T032 [US1] Create vector store service skeleton at /home/riku-miura/project/wiki_rag/backend/src/services/vector_store.py
- [ ] T033 [US1] Implement FAISS index creation (IndexFlatL2) at /home/riku-miura/project/wiki_rag/backend/src/services/vector_store.py
- [ ] T034 [US1] Implement FAISS index serialization/deserialization at /home/riku-miura/project/wiki_rag/backend/src/services/vector_store.py
- [ ] T035 [US1] Implement S3 upload/download for FAISS indices at /home/riku-miura/project/wiki_rag/backend/src/services/vector_store.py

### RAG Builder Orchestration (3 tasks)

- [ ] T036 [US1] Create RAG builder orchestration service at /home/riku-miura/project/wiki_rag/backend/src/services/rag_builder.py
- [ ] T037 [US1] Implement text chunking with RecursiveCharacterTextSplitter at /home/riku-miura/project/wiki_rag/backend/src/services/rag_builder.py
- [ ] T038 [US1] Implement end-to-end RAG build pipeline at /home/riku-miura/project/wiki_rag/backend/src/services/rag_builder.py

### Lambda Handler (3 tasks)

- [ ] T039 [US1] Create RAG builder Lambda handler at /home/riku-miura/project/wiki_rag/backend/src/api/lambda_handlers/rag_builder_handler.py
- [ ] T040 [US1] Implement POST /rag/build endpoint at /home/riku-miura/project/wiki_rag/backend/src/api/lambda_handlers/rag_builder_handler.py
- [ ] T041 [US1] Implement GET /rag/{session_id}/status endpoint at /home/riku-miura/project/wiki_rag/backend/src/api/lambda_handlers/rag_builder_handler.py

### Frontend Components (4 tasks)

- [ ] T042 [P] [US1] Create Wikipedia URL input component at /home/riku-miura/project/wiki_rag/frontend/src/components/WikipediaInput.svelte
- [ ] T043 [P] [US1] Create status indicator component at /home/riku-miura/project/wiki_rag/frontend/src/components/StatusIndicator.svelte
- [ ] T044 [P] [US1] Create session store for RAG session state at /home/riku-miura/project/wiki_rag/frontend/src/stores/session_store.js
- [ ] T045 [P] [US1] Create API client for RAG building endpoints at /home/riku-miura/project/wiki_rag/frontend/src/services/api_client.js

**Parallel Execution**: T042-T045 can run in parallel (different frontend files)

**Milestone**: At this point, User Story 1 is complete and can be independently tested

---

## Phase 4: User Story 2 - Chat with RAG Knowledge Base (20 tasks)

**Priority**: P2 (Primary value delivery)
**Goal**: User queries RAG with session_id → receives streamed LLM response
**Independent Test**: Use pre-created session_id, send query via API, verify streamed LLM response

### Data Models (2 tasks)

- [ ] T046 [P] [US2] Create Query model at /home/riku-miura/project/wiki_rag/backend/src/models/query.py
- [ ] T047 [P] [US2] Create Chat Message model at /home/riku-miura/project/wiki_rag/backend/src/models/chat_message.py

**Parallel Execution**: T046 and T047 can run in parallel (different model files)

### LLM Service (4 tasks)

- [ ] T048 [US2] Create LLM service skeleton at /home/riku-miura/project/wiki_rag/backend/src/services/llm_service.py
- [ ] T049 [US2] Implement Ollama HTTP client for Llama 3.2 3B at /home/riku-miura/project/wiki_rag/backend/src/services/llm_service.py
- [ ] T050 [US2] Implement prompt template for RAG context + query at /home/riku-miura/project/wiki_rag/backend/src/services/llm_service.py
- [ ] T051 [US2] Implement streaming response handling at /home/riku-miura/project/wiki_rag/backend/src/services/llm_service.py

### Chat Service (4 tasks)

- [ ] T052 [US2] Create chat service skeleton at /home/riku-miura/project/wiki_rag/backend/src/services/chat_service.py
- [ ] T053 [US2] Implement query embedding generation at /home/riku-miura/project/wiki_rag/backend/src/services/chat_service.py
- [ ] T054 [US2] Implement FAISS similarity search (top-k retrieval) at /home/riku-miura/project/wiki_rag/backend/src/services/chat_service.py
- [ ] T055 [US2] Implement RAG pipeline (retrieve + context assembly + LLM call) at /home/riku-miura/project/wiki_rag/backend/src/services/chat_service.py

### Lambda Handler (3 tasks)

- [ ] T056 [US2] Create chat Lambda handler at /home/riku-miura/project/wiki_rag/backend/src/api/lambda_handlers/chat_handler.py
- [ ] T057 [US2] Implement POST /chat/query endpoint with SSE streaming at /home/riku-miura/project/wiki_rag/backend/src/api/lambda_handlers/chat_handler.py
- [ ] T058 [US2] Implement GET /chat/{session_id}/history endpoint at /home/riku-miura/project/wiki_rag/backend/src/api/lambda_handlers/chat_handler.py

### Frontend Components (7 tasks)

- [ ] T059 [P] [US2] Create chat interface component at /home/riku-miura/project/wiki_rag/frontend/src/components/ChatInterface.svelte
- [ ] T060 [P] [US2] Create message list component at /home/riku-miura/project/wiki_rag/frontend/src/components/MessageList.svelte
- [ ] T061 [P] [US2] Create SSE handler for streaming responses at /home/riku-miura/project/wiki_rag/frontend/src/services/sse_handler.js
- [ ] T062 [P] [US2] Create chat store for message history at /home/riku-miura/project/wiki_rag/frontend/src/stores/chat_store.js
- [ ] T063 [P] [US2] Extend API client with chat endpoints at /home/riku-miura/project/wiki_rag/frontend/src/services/api_client.js
- [ ] T064 [P] [US2] Create chat page component at /home/riku-miura/project/wiki_rag/frontend/src/pages/Chat.svelte
- [ ] T065 [P] [US2] Create landing page component at /home/riku-miura/project/wiki_rag/frontend/src/pages/Index.svelte

**Parallel Execution**: T059-T065 can run in parallel (different frontend files)

**Milestone**: At this point, User Story 2 is complete and can be independently tested

---

## Phase 5: User Story 3 - Profile Page Integration (8 tasks)

**Priority**: P3 (Polished user experience)
**Goal**: User accesses chat UI from AWS-hosted profile page
**Dependencies**: Requires Phase 3 (US1) and Phase 4 (US2) to be complete
**Independent Test**: Navigate to profile page, verify chat UI loads and performs RAG + chat operations

### Frontend Deployment (5 tasks)

- [ ] T066 [US3] Configure Svelte build for production at /home/riku-miura/project/wiki_rag/frontend/vite.config.js
- [ ] T067 [US3] Build frontend production bundle (npm run build)
- [ ] T068 [US3] Configure S3 bucket for static site hosting in FrontendStack at /home/riku-miura/project/wiki_rag/infrastructure/stacks/frontend_stack.py
- [ ] T069 [US3] Configure CloudFront distribution with S3 origin at /home/riku-miura/project/wiki_rag/infrastructure/stacks/frontend_stack.py
- [ ] T070 [US3] Deploy frontend to S3 and invalidate CloudFront cache

### Subdirectory Configuration (New)
- [ ] T070b [US3] Configure Vite base path and CloudFront behavior for /projects/wiki_rag/ specific deployment

### Profile Page Integration (3 tasks)

- [ ] T071 [US3] Create embedded chat widget wrapper at /home/riku-miura/project/wiki_rag/frontend/src/components/EmbeddedChat.svelte
- [ ] T072 [US3] Configure CORS and CSP headers for embedded widget at /home/riku-miura/project/wiki_rag/infrastructure/stacks/frontend_stack.py
- [ ] T073 [US3] Update profile page to include chat widget script tag

**Milestone**: At this point, User Story 3 is complete and the full user experience is available

---

## Phase 6: Polish & Cross-Cutting Concerns (10 tasks)

**Goal**: Production readiness, observability, and documentation
**Dependencies**: Runs after all user stories are functional

### Logging and Monitoring (4 tasks)

- [ ] T074 [P] Implement CloudWatch Logs integration for all Lambda functions
- [ ] T075 [P] Create CloudWatch custom metrics for LLM latency tracking
- [ ] T076 [P] Configure AWS Budgets alerts ($40, $45, $50 thresholds)
- [ ] T077 [P] Create CloudWatch dashboard for system health monitoring

**Parallel Execution**: T074-T077 can run in parallel (different AWS configurations)

### Error Handling and Optimization (3 tasks)

- [ ] T078 Add retry logic with exponential backoff for Wikipedia fetching
- [ ] T079 Implement Lambda cold start optimization (provisioned concurrency)
- [ ] T080 Add comprehensive error logging with structured log format

### Documentation (3 tasks)

- [ ] T081 [P] Create architecture diagram at /home/riku-miura/project/wiki_rag/docs/architecture.md
- [ ] T082 [P] Create API usage examples at /home/riku-miura/project/wiki_rag/docs/api_usage.md
- [ ] T083 [P] Create project README at /home/riku-miura/project/wiki_rag/README.md

**Parallel Execution**: T081-T083 can run in parallel (different documentation files)

---

## Implementation Strategy

### MVP-First Approach

1. **Phase 1-2 First**: Complete setup and foundational infrastructure before any feature work
2. **User Story 1 (P1) Next**: Build the RAG construction pipeline - this is the MVP
3. **Validate US1**: Test independently before moving to US2
4. **User Story 2 (P2) Next**: Add chat functionality on top of working RAG
5. **Validate US2**: Test independently with pre-created sessions
6. **User Story 3 (P3) Last**: Polish with profile page integration
7. **Phase 6 Final**: Add observability and documentation

### Incremental Delivery Checkpoints

**Checkpoint 1**: After T020 (Infrastructure deployed)
- AWS resources are live
- Can manually test EC2 Ollama instance
- S3 buckets and DynamoDB tables exist

**Checkpoint 2**: After T045 (User Story 1 complete)
- **Independent Test**: Submit Wikipedia URL → get session_id with "ready" status
- RAG construction pipeline works end-to-end
- Can build knowledge bases from Wikipedia articles

**Checkpoint 3**: After T065 (User Story 2 complete)
- **Independent Test**: Query existing session → get streamed LLM response
- Chat functionality works end-to-end
- Can query RAG knowledge bases

**Checkpoint 4**: After T073 (User Story 3 complete)
- **Independent Test**: Navigate to profile page → use chat UI
- Full user experience is available
- System is feature-complete

**Checkpoint 5**: After T083 (All phases complete)
- Production-ready system
- Monitoring and logging in place
- Documentation complete

### Parallel Execution Examples

Within phases, many tasks can run in parallel:

```bash
# Phase 1 - All tasks can run in parallel
T001, T002, T003, T004 → Run in parallel

# Phase 2 - Infrastructure stacks can run in parallel
T008, T009, T010, T011 → Run in parallel

# Phase 3 - Models can run in parallel
T021 [RAG Session model] & T022 [Text Chunk model] → Run in parallel

# Phase 3 - Utilities can run in parallel
T023 [S3 client] & T024 [Validation] & T025 [Error handling] → Run in parallel

# Phase 3 - Frontend components can run in parallel
T042, T043, T044, T045 → Run in parallel

# Phase 4 - Models can run in parallel
T046 [Query model] & T047 [Chat Message model] → Run in parallel

# Phase 4 - All frontend components can run in parallel
T059, T060, T061, T062, T063, T064, T065 → Run in parallel

# Phase 6 - Monitoring tasks can run in parallel
T074, T075, T076, T077 → Run in parallel

# Phase 6 - Documentation can run in parallel
T081, T082, T083 → Run in parallel
```

### Dependency Chains

Some tasks must run sequentially:

```bash
# Wikipedia Fetching Service (sequential)
T026 → T027 → T028

# Embedding Service (sequential)
T029 → T030 → T031

# Vector Store Service (sequential)
T032 → T033 → T034 → T035

# RAG Builder Orchestration (sequential, depends on services)
T036 → T037 → T038

# Lambda Handler (sequential, depends on services)
T039 → T040 → T041

# LLM Service (sequential)
T048 → T049 → T050 → T051

# Chat Service (sequential, depends on LLM service)
T052 → T053 → T054 → T055

# Chat Lambda Handler (sequential, depends on chat service)
T056 → T057 → T058

# Frontend Deployment (sequential)
T066 → T067 → T068 → T069 → T070
```

---

## Progress Tracking

**Phase 1 (Setup)**: 0/5 tasks complete (0%)
**Phase 2 (Foundational)**: 0/15 tasks complete (0%)
**Phase 3 (User Story 1)**: 0/25 tasks complete (0%)
**Phase 4 (User Story 2)**: 0/20 tasks complete (0%)
**Phase 5 (User Story 3)**: 0/8 tasks complete (0%)
**Phase 6 (Polish)**: 0/10 tasks complete (0%)

**Overall Progress**: 0/83 tasks complete (0%)

---

## Success Criteria Mapping

Each task contributes to specific success criteria from spec.md:

| Success Criterion | Related Tasks | Validation |
|------------------|---------------|------------|
| SC-001: RAG build <60s for 50KB articles | T026-T038 | Time RAG build from API call to "ready" status |
| SC-002: Query response <2s first chunk | T048-T058 | Measure latency from query submission to first SSE event |
| SC-003: 10 concurrent RAG builds | T008-T020 | Load test with 10 parallel POST /rag/build requests |
| SC-004: 90% relevant responses | T052-T055 | Manual evaluation of response quality |
| SC-005: No external LLM APIs | T012-T014, T048-T051 | Verify all LLM calls go to EC2 Ollama instance |
| SC-006: <$50/month cost | T008-T020, T074-T076 | Monitor AWS Budgets dashboard |
| SC-007: UI loads <3s | T066-T070 | Lighthouse performance audit |

---

## Risk Mitigation

**High-Risk Tasks** (require careful attention):

1. **T020**: CDK deployment - First AWS deployment, may encounter permission issues
2. **T038**: End-to-end RAG pipeline - Complex integration of multiple services
3. **T051**: Streaming response handling - SSE implementation can be tricky
4. **T055**: RAG pipeline - Critical path for query performance (SC-002)
5. **T070**: Frontend deployment - CloudFront invalidation timing issues

**Mitigation Strategies**:
- Test each service independently before integration
- Use local development environment for rapid iteration
- Implement comprehensive error logging early (T080)
- Set up monitoring (T074-T077) as soon as infrastructure is live

---

## Notes

- **No Test Tasks**: As specified in the requirements, this task list focuses on implementation only. Tests are not included.
- **File Paths**: All file paths are absolute paths from the project root `/home/riku-miura/project/wiki_rag/`
- **Parallel Markers**: Tasks marked with [P] can be executed in parallel with adjacent tasks
- **User Story Labels**: All tasks contributing to user stories are labeled [US1], [US2], or [US3]
- **Total Task Count**: 83 tasks (within the 60-80 range specified)

---

## Next Steps

1. Review this task list with the team
2. Begin with Phase 1 (Setup) tasks T001-T005
3. After Phase 1, deploy Phase 2 (Foundational Infrastructure) - this is the critical blocker
4. Once infrastructure is live, begin parallel development of User Story 1 and User Story 2
5. Use the checkpoints to validate each phase before proceeding

---

**Last Updated**: 2025-11-02
**Generated By**: /speckit.tasks command
**Related Documents**: [spec.md](./spec.md), [plan.md](./plan.md), [data-model.md](./data-model.md)
