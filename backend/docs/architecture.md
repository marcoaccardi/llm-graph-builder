# LLM Graph Builder Backend Architecture

## Architecture Overview

The LLM Graph Builder backend is a FastAPI application that converts documents into knowledge graphs using LLMs and Neo4j as the graph database. The architecture follows a modular design with clear separation of concerns across different components.

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               LLM Graph Builder Backend Architecture                        │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   ASCII Architecture Diagram                              │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

API Layer
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ┌─────────────────┐                                                                       │
│  │   FastAPI App   │                                                                       │
│  │    score.py     │                                                                       │
│  └─────────────────┘                                                                       │
│            │                                                                               │
│            ▼                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐   │
│  │                           API Endpoints                                         │   │
│  ├─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┤   │
│  │    Upload API   │   Extract API   │  Chat Bot API   │   Schema API    │Post Processing  │   │
│  │                 │                 │                 │                 │      API        │   │
│  │   /upload       │   /extract      │   /chat_bot     │   /schema       │/post_processing │   │
│  └─────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
Core Processing Layer
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ┌─────────────┐     ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ src.main.py │     │           Document Processing Pipeline                        │   │
│  └─────────────┘     └─────────────────────────────────────────────────────────────────────┘   │
│        │             │                                                               │   │
│        ├─────────────┼─────────────────────────────────────────────────────────────────────┤   │
│        │             │  • Source Node Creation  ┌─────────────────────────────────────┐   │   │
│        │             │  • Chunk Creation &     │   create_chunks.py                │   │   │
│        │             │    Processing           └─────────────────────────────────────┘   │   │
│        │             │  • LLM Entity Extraction                                     │   │
│        │             │  • Knowledge Graph Creation                                  │   │
│        │             └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
Data Access Layer
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ┌─────────────────────────┐     ┌─────────────────────────────────────────────────────┐       │
│  │ graphDB_dataAccess.py │     │           Neo4jGraph Operations                 │       │
│  └─────────────────────────┘     └─────────────────────────────────────────────────────┘       │
│        │                     │                                                   │       │
│        ├─────────────────────┼───────────────────────────────────────────────────────┤       │
│        │                     │  • Document Node Management                       │       │
│        │                     │  • Entity Management                            │       │
│        │                     │  • Relationship Management                      │       │
│        │                     │  • Index Management                             │       │
│        │                     └───────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
LLM Integration Layer
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ┌─────────────┐     ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  src.llm.py │     │             LLM Model Selection                           │   │
│  └─────────────┘     └─────────────────────────────────────────────────────────────────────┘   │
│        │             │                                                               │   │
│        ├─────────────┼─────────────────────────────────────────────────────────────────────┤   │
│        │             │  • OpenAI Models (GPT-3.5, GPT-4)                            │   │
│        │             │  • Google Gemini                                       │   │
│        │             │  • Anthropic Claude                                    │   │
│        │             │  • AWS Bedrock Models                                  │   │
│        │             │  • Ollama Models (Local)                               │   │
│        │             │  • Diffbot API                                       │   │
│        │             └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

Document Sources
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐   │
│  │                           Document Sources                                    │   │
│  ├─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┤   │
│  │  Local Files    │   S3 Bucket     │   GCS Bucket    │   Web URLs      │   YouTube       │   │
│  │                 │                 │                 │                 │                 │   │
│  │  PDF, TXT       │  AWS S3         │  Google Cloud   │  Web pages     │  Transcripts    │   │
│  │  PyMuPDF        │  Integration     │  Storage        │  WebBaseLoader │  YouTubeLoader  │   │
│  │  Unstructured   │                 │                 │                 │                 │   │
│  └─────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

Data Processing Components
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐   │
│  │                    Chunk & Embedding Processing                               │   │
│  ├─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┤   │
│  │ create_chunks.py│make_relationship│ Embedding     │ Vector Index  │  Post Processing│   │
│  │                 │       s.py      │ Generation    │ Creation      │   (Communities) │   │
│  └─────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

Shared Utilities
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐   │
│  │                        Shared Components                                    │   │
│  ├─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┤   │
│  │ common_fn.py    │ constants.py    │ Exception     │ schema_extract│   Logger        │   │
│  │                 │                 │ Handling      │     ion.py      │                 │   │
│  └─────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

Database Layer
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐   │
│  │                         Neo4j GraphDB                                     │   │
│  ├─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┤   │
│  │ Document Nodes  │ Chunk Nodes     │ Entity Nodes    │ Relationships   │Vector Embeddings│   │
│  └─────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

Key Integration Flows:
• API Layer → Core Processing: Document processing requests
• Core Processing → LLM Integration: Entity extraction calls
• Core Processing → Document Sources: Document loading
• Core Processing → Data Processing: Chunk and relationship creation
• Core Processing → Shared Utilities: Utility function calls
• Data Access Layer → Database Layer: Neo4j operations
• Data Processing → Data Access: Database interactions
• Shared Utilities → Core Processing: Support functions

## Component Analysis

### 1. API Layer (`score.py`) - The Gateway
- **FastAPI Application**: Main entry point (3,800+ lines) that handles all HTTP requests with comprehensive error handling
- **API Endpoints**: Multiple endpoints for different operations:
  - `/upload` - Handle file chunk uploads with progress tracking
  - `/extract` - Extract knowledge graph from documents with retry mechanisms
  - `/url/scan` - Process various source types (S3, GCS, Web, YouTube, Wikipedia)
  - `/chat_bot` - Query interface for knowledge graphs with SSE support
  - `/post_processing` - Additional graph processing tasks (community detection, similarity)
  - `/sources_list` - Get list of processed documents with status tracking
  - `/schema` - Extract and manage graph schema
  - `/health` - Health check endpoints for monitoring
- **Features**: CORS, GZip compression, session management, security middleware, SSE for real-time updates

### 2. Core Processing (`src/main.py` - 41,802 lines) - The Brain
- **Document Processing Pipeline**: Handles the main flow from document ingestion to knowledge graph creation
- **Source Node Creation**: Creates initial document nodes in Neo4j with metadata (file size, type, source, etc.)
- **Chunk Processing**: Iterates through document chunks using token-based splitting with configurable chunk sizes
- **Retry Mechanism**: Supports three retry conditions:
  - `START_FROM_BEGINNING`: Full restart from first chunk
  - `START_FROM_LAST_PROCESSED_POSITION`: Resume from last successful chunk
  - `DELETE_ENTITIES_AND_START_FROM_BEGINNING`: Clear existing entities and restart
- **Multi-Source Integration**: Coordinates between local files, cloud storage, and web sources
- **LLM Orchestration**: Manages LLM calls for entity extraction with error handling and fallbacks

### 3. Data Access Layer (`src/graphDB_dataAccess.py` - 31,235 lines) - The Database Interface
- **Database Operations**: Encapsulates all Neo4j database interactions with transaction management
- **Source Node Management**: Create, update, and query document nodes with comprehensive metadata
- **Entity Management**: Handle entity nodes (persons, organizations, locations, concepts) and their relationships
- **Index Management**: Vector indexes, KNN graph updates, full-text search indexes, and schema operations
- **Error Handling**: Database transaction management, deadlock handling, and exception logging
- **Community Detection**: Identifies and creates communities of related entities using graph algorithms

### 4. LLM Integration (`src/llm.py` - 11,604 lines) - The Intelligence Layer
- **Multiple LLM Support**: Supports various providers with unified interface:
  - OpenAI Models (GPT-3.5, GPT-4) for general-purpose entity extraction
  - Google Gemini for multimodal understanding
  - Anthropic Claude for complex reasoning
  - AWS Bedrock Models for enterprise-grade processing
  - Ollama Models (Local) for on-premise/private deployments
  - Diffbot API for specialized entity extraction
- **Graph Transformation**: Uses `LLMGraphTransformer` to convert text to graph structures
- **Chunk Combination**: Combines multiple chunks for better context during entity extraction
- **Custom Instructions**: Supports additional instructions for domain-specific entity extraction
- **Cost Optimization**: Intelligent model selection based on requirements and budget

### 5. Document Sources (`src/document_sources/` - 6 modules) - The Input Layer
- **Multiple Source Types**: Handles files from various sources with specialized loaders
- **Local Files** (`local_file.py`): PDF, TXT processing with PyMuPDF and Unstructured loaders
- **Cloud Storage**:
  - S3 Bucket (`s3_bucket.py`): AWS S3 integration with credential management
  - GCS Bucket (`gcs_bucket.py`): Google Cloud Storage with project ID support
- **Web Sources**:
  - Web Pages (`web_pages.py`): WebBaseLoader for HTML content extraction
  - YouTube (`youtube.py`): Transcript extraction and processing
  - Wikipedia (`wikipedia.py`): Wikipedia article processing
- **Format Support**: Various document formats with appropriate loaders and preprocessing

### 6. Data Processing Components - The Processing Engine
- **Chunk Creation** (`src/create_chunks.py`): Token-based text splitting with overlap and size configuration
- **Relationship Management** (`src/make_relationships.py`): Creates relationships between chunks, entities, and documents
- **Embedding Generation**: Creates vector embeddings for semantic search and similarity detection
- **Index Creation**: Vector and full-text index management for fast querying
- **Post Processing** (`src/post_processing.py`): Community detection, similarity relationships, schema consolidation

### 7. Shared Utilities - The Support System
- **Constants** (`src/shared/constants.py` - 33,455 lines): Comprehensive configuration values, Cypher queries, and system settings
- **Common Functions** (`src/shared/common_fn.py`): Utility functions for graph operations, embeddings, and document handling
- **Schema Processing** (`src/shared/schema_extraction.py`): Extracts graph schema from text for validation and optimization
- **Exception Handling** (`src/shared/llm_graph_builder_exception.py`): Custom exception hierarchy with error codes
- **Logging** (`src/logger.py`): Custom logging framework with structured logging

### 8. Specialized Components
- **QA Integration** (`src/QA_integration.py`): Question answering capabilities over the knowledge graph
- **Graph Query** (`src/graph_query.py`): Advanced querying and visualization capabilities
- **Evaluation** (`src/ragas_eval.py`): RAG evaluation metrics and quality assessment
- **Community Detection** (`src/communities.py`): Advanced graph algorithms for community identification

## Data Flow - Step by Step

1. **Document Ingestion**: User uploads document or provides URL/source through API endpoints
2. **Source Node Creation**: Creates initial document node in Neo4j with comprehensive metadata
3. **Document Processing**: Load document content via appropriate loader (PyMuPDF, Unstructured, WebBaseLoader, etc.)
4. **Chunking**: Split document into manageable chunks using token-based splitting with configurable parameters
5. **Chunk Storage**: Create Chunk nodes in Neo4j with PART_OF relationships to Document
6. **Embedding Generation**: Create vector embeddings for each chunk using configured embedding models
7. **Entity Extraction**: Use LLM to extract entities and relationships from chunks with context awareness
8. **Graph Storage**: Store entities (persons, organizations, locations, concepts) and relationships in Neo4j
9. **Relationship Creation**: Create HAS_ENTITY relationships between chunks and entities with confidence scores
10. **Post Processing**: Optional community detection, similarity relationships, and schema optimization
11. **Index Creation**: Build vector and full-text indexes for fast querying and semantic search

## Key Features & Capabilities

- **Multi-source Support**: Handles local files, cloud storage (S3, GCS), web sources (URLs, YouTube, Wikipedia)
- **LLM Provider Agnostic**: Supports 6+ LLM providers with intelligent model selection
- **Scalable Processing**: Chunk-based processing allows handling large documents (100k+ tokens)
- **Vector Search**: Built-in vector embeddings and similarity search with configurable models
- **Community Detection**: Identifies and creates communities of related entities using graph algorithms
- **Error Resilience**: Comprehensive error handling, retry mechanisms, and transaction management
- **Real-time Monitoring**: Progress tracking via Server-Sent Events (SSE) endpoints
- **Batch Processing**: Support for processing multiple documents with status tracking
- **Schema Management**: Dynamic schema extraction and validation capabilities

## Architecture Benefits

1. **Modularity**: Clear separation of concerns makes the system maintainable and extensible - each component has well-defined responsibilities
2. **Flexibility**: Support for multiple data sources, LLM providers, and deployment options (cloud, on-premise)
3. **Scalability**: Chunk-based processing allows horizontal scaling and handling of large documents
4. **Robustness**: Comprehensive error handling, retry mechanisms, and transaction management ensure reliability
5. **Performance**: Vector indexes, optimized Cypher queries, and caching mechanisms for fast operations
6. **Maintainability**: Well-structured codebase with comprehensive documentation and error handling
7. **Extensibility**: Plugin-like architecture allows easy addition of new document sources and LLM providers

## Backend Folder Structure

```
backend/
├── score.py                    # Main FastAPI application (3,800+ lines)
├── requirements.txt           # Python dependencies (200+ packages)
├── Dockerfile               # Containerization configuration
├── docs/                    # Documentation
│   └── architecture.md      # This architecture documentation
├── src/                     # Main source code (27 files, 41,802+ lines)
│   ├── main.py             # Core processing logic
│   ├── graphDB_dataAccess.py# Neo4j database operations
│   ├── llm.py              # LLM integration and orchestration
│   ├── create_chunks.py    # Document chunking
│   ├── make_relationships.py# Relationship management
│   ├── post_processing.py  # Post-processing operations
│   ├── communities.py      # Community detection algorithms
│   ├── graph_query.py      # Advanced querying capabilities
│   ├── QA_integration.py   # Question answering integration
│   ├── ragas_eval.py       # RAG evaluation metrics
│   ├── chunkid_entities.py # Entity lookup by chunk ID
│   ├── neighbours.py       # Neighbor node operations
│   ├── api_response.py     # API response formatting
│   ├── logger.py           # Logging framework
│   ├── diffbot_transformer.py # Diffbot API integration
│   ├── document_sources/   # Document source handlers (6 files)
│   │   ├── local_file.py   # Local file processing
│   │   ├── s3_bucket.py    # AWS S3 integration
│   │   ├── gcs_bucket.py   # Google Cloud Storage
│   │   ├── web_pages.py    # Web page processing
│   │   ├── youtube.py      # YouTube transcript processing
│   │   └── wikipedia.py    # Wikipedia article processing
│   ├── entities/           # Entity definitions
│   │   ├── source_node.py  # Document metadata structure
│   │   └── user_credential.py # User credential management
│   └── shared/             # Shared utilities (4 files)
│       ├── constants.py    # Configuration and queries
│       ├── common_fn.py    # Common utility functions
│       ├── schema_extraction.py # Schema processing
│       └── llm_graph_builder_exception.py # Exception handling
└── tests/                  # Test suite (performance, integration, unit tests)
```

The architecture is well-designed to handle the complex task of converting unstructured documents into structured knowledge graphs, with multiple integration points and a clear separation of concerns between data processing, storage, and API layers. It's built for production use with comprehensive error handling, monitoring, and scalability features.