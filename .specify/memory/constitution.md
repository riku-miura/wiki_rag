<!--
Sync Impact Report:
- Version change: Template → 1.0.0 (initial version)
- Modified principles: N/A (initial creation)
- Added sections: All core principles, Technology Stack, Deployment Standards, Governance
- Removed sections: None
- Templates requiring updates:
  ✅ plan-template.md (reviewed - Constitution Check section present)
  ✅ spec-template.md (reviewed - aligns with requirements approach)
  ✅ tasks-template.md (reviewed - supports modular implementation)
- Follow-up TODOs: None
-->

# Wiki RAG Constitution

## Core Principles

### I. Modularity

RAG construction and chat functionality MUST be implemented as separate, independently
deployable components. This enables:
- Independent scaling of RAG builder and chat inference
- Easier testing and maintenance
- Flexibility to replace or upgrade components without system-wide impact

**Rationale**: Separation allows cost optimization (spot instances for batch RAG building
vs stable instances for user-facing chat) and reduces blast radius of changes.

### II. Privacy First

The system MUST NOT send user data or queries to external LLM APIs. All inference MUST
occur on AWS infrastructure controlled by the project owner.

**Requirements**:
- Local LLM deployment (e.g., Llama.cpp, Ollama) on EC2/ECS
- No API calls to OpenAI, Anthropic, or similar external services
- User Wikipedia URLs and chat history remain within AWS VPC

**Rationale**: Full control over data privacy and compliance; no external API costs or
rate limits.

### III. Cost Efficiency

Infrastructure choices MUST prioritize cost optimization while meeting functional
requirements.

**Requirements**:
- Use serverless (Lambda, API Gateway, S3) for low-traffic components
- Start with small EC2/ECS instances for LLM inference
- Implement auto-scaling only when proven necessary
- Use S3 for storage instead of expensive managed databases where appropriate
- Monitor and report AWS costs regularly

**Rationale**: Personal project constraints require lean infrastructure; premature
optimization for scale wastes resources.

### IV. Infrastructure as Code

All AWS infrastructure MUST be defined as code and version-controlled.

**Requirements**:
- Use Terraform or AWS CDK for infrastructure definitions
- All infrastructure changes MUST be reviewed as code
- No manual AWS console changes for production resources
- Infrastructure code MUST be in the same repository as application code

**Rationale**: Reproducibility, disaster recovery, and collaboration require
infrastructure to be treated as code, not as manual configuration.

### V. Observability

The system MUST provide basic monitoring and logging for debugging and performance
analysis.

**Requirements**:
- Structured logging to CloudWatch Logs for all components
- Basic CloudWatch metrics for LLM inference latency and RAG build status
- Error tracking for failed Wikipedia fetches and LLM inference failures
- Cost monitoring dashboard

**Rationale**: Without visibility into system behavior, debugging production issues
becomes impossible. Basic observability is non-negotiable.

## Technology Stack

The following technology choices are mandated for this project:

**Cloud Platform**: AWS
- EC2 or ECS for LLM hosting
- Lambda + API Gateway for backend APIs
- S3 + CloudFront for frontend hosting
- CloudWatch for logging and monitoring

**Backend**:
- Python 3.11+ as primary language
- LangChain for RAG orchestration
- Local LLM: Llama.cpp or Ollama
- Vector database: FAISS or Chroma (local file-based)

**Frontend**:
- Svelte or Next.js (developer choice)
- Hosted on S3 + CloudFront as static site

**Data Storage**:
- S3 for document storage and vector indices
- No relational database required initially

**Infrastructure as Code**:
- Terraform OR AWS CDK (pick one, document choice in plan.md)

## Deployment Standards

**Public Code Repository**: All source code MUST be published on GitHub under an open
source license (MIT or Apache 2.0).

**Frontend Deployment**: Chat UI MUST be accessible via the developer's AWS-hosted
profile page (integration details to be specified in feature spec).

**Security**:
- No hardcoded credentials in code or IaC
- Use AWS IAM roles and Secrets Manager for credentials
- S3 buckets MUST NOT be publicly writable
- API Gateway MUST implement rate limiting

**Documentation**:
- README.md MUST include setup instructions and architecture diagram
- Each component MUST have a quickstart guide for local development

## Governance

This constitution supersedes all other practices and conventions. Any deviation from
these principles MUST be documented with explicit justification in plan.md under the
"Complexity Tracking" section.

**Amendment Process**:
- Constitution changes require explicit discussion and approval
- Version bumps follow semantic versioning (MAJOR.MINOR.PATCH)
- All amendments MUST document rationale and migration impact

**Compliance Review**:
- All feature specs MUST reference relevant constitutional principles
- Implementation plans MUST include a "Constitution Check" section
- Code reviews MUST verify adherence to mandated principles
- Any complexity that violates principles MUST be justified before implementation

**Version**: 1.0.0 | **Ratified**: 2025-11-02 | **Last Amended**: 2025-11-02
