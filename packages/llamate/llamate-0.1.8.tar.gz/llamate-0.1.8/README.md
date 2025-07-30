# 🦙 Llamate

Llamate is a memory-augmented agent framework for Large Language Models (LLMs) that provides persistent, retrievable memory for AI conversations.

## What is Llamate?

Llamate solves a fundamental limitation of current LLMs: their inability to remember past conversations beyond a single context window. It creates a vector database of memories that can be semantically searched and retrieved during conversations, allowing LLMs to maintain continuity and context over extended interactions.

## How It Works

1. **Memory Storage**: Llamate stores important pieces of conversation as vector embeddings in a database (either FAISS or PostgreSQL).
2. **Semantic Retrieval**: When new queries come in, Llamate searches for semantically relevant past memories.
3. **Memory Filtering**: The system automatically filters out the current query from search results to prevent echo effects.
4. **Context Enhancement**: Retrieved memories are injected into the conversation context, allowing the LLM to access and utilize past information.
5. **User Identification**: Each user gets a unique memory space, ensuring personalized conversation history.

## Key Features

- **Multiple Backend Support**: Works with FAISS (file-based) or PostgreSQL (with pgvector)
- **Persistence**: Memories remain available between sessions and application restarts
- **Simple API**: Easy-to-use Python interface that works with any LLM
- **CLI Interface**: Command-line tool for quick testing and interaction
- **Production Ready**: Designed for both development and production environments


## Quick Start

### Local Development

The following steps guide you through setting up Llamate for local development:

#### 1. Install Package

```bash
pip install llamate
```

### 2. OpenAI API Requirements

Llamate requires access to the following OpenAI models in your account:

- **Embedding models** (at least one of):
  - `text-embedding-3-small` (default, 1536 dimensions) - Faster, smaller embeddings, cost-effective
  - `text-embedding-3-large` (3072 dimensions) - Higher accuracy, larger embeddings
- `gpt-4` - Recommended for high-quality responses

Make sure these models are enabled in your OpenAI account.

## Environment Variables

Llamate is configured primarily through environment variables, making it easy to integrate with any backend deployment. The following environment variables are supported:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLAMATE_OPENAI_API_KEY` | None (Required) | Your OpenAI API key |
| `LLAMATE_VECTOR_BACKEND` | `postgres` | Vector store backend (`postgres` or `faiss`) |
| `LLAMATE_DATABASE_URL` | `postgresql://llamate:llamate@localhost:5432/llamate` | PostgreSQL connection string (when using postgres backend) |
| `LLAMATE_EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model to use (`text-embedding-3-small` or `text-embedding-3-large`) |

Example configuration for production deployment:

```bash
# Required
LLAMATE_OPENAI_API_KEY=sk-your-api-key

# Optional overrides
LLAMATE_VECTOR_BACKEND=postgres
LLAMATE_DATABASE_URL=postgresql://user:password@your-db-host:5432/dbname
LLAMATE_EMBEDDING_MODEL=text-embedding-3-large
```

> **Note:** While you can use `llamate --init` for local development to generate a `.env` file, in production environments you should configure these variables directly in your deployment platform.

### 3. Start PostgreSQL Container

```bash
docker run --name llamate-postgres -e POSTGRES_USER=llamate -e POSTGRES_PASSWORD=llamate -e POSTGRES_DB=llamate -p 5432:5432 -d ankane/pgvector
```

### 4. Initialize Llamate

```bash
llamate --init
# Select 'postgres' as your vector store backend
# Enter connection string: postgresql://llamate:llamate@localhost:5432/llamate
```

### 5. Test Llamate locally

```python
from llamate import MemoryAgent, get_vectorstore_from_env

# Set user ID
user_id = "test_user"

# Initialize components
vectorstore = get_vectorstore_from_env(user_id=user_id)
agent = MemoryAgent(user_id=user_id, vectorstore=vectorstore)

# Add memories
agent.chat("The capital of France is Paris.")
agent.chat("The Eiffel Tower is 324 meters tall.")
agent.chat("Python is a programming language created by Guido van Rossum.")

# Test retrieval
response = agent.chat("Tell me about Paris.")
print("Response:", response)
```

## Production Integration

For production applications, you'll typically integrate Llamate directly into your backend services:

```python
from llamate import MemoryAgent, get_vectorstore_from_env
import os

# In production, set environment variables directly in your deployment platform
# os.environ["LLAMATE_OPENAI_API_KEY"] = "your-key-here" # Set in platform instead
# os.environ["LLAMATE_DATABASE_URL"] = "connection-string" # Set in platform instead

def create_llamate_agent(user_id):
    """Factory function to create a memory-augmented agent for a specific user"""
    vectorstore = get_vectorstore_from_env(user_id=user_id)
    return MemoryAgent(user_id=user_id, vectorstore=vectorstore)

# Example API endpoint
def handle_chat_request(user_id, user_message):
    agent = create_llamate_agent(user_id)
    return agent.chat(user_message)
```

### 6. View Data in PostgreSQL

Connect to the database:

```bash
docker exec -it llamate-postgres psql -U llamate -d llamate
```

List tables to find your memory table (it will use your user_id):

```sql
\dt
```

View table structure:

```sql
\d memory_test_user
```

Display memory records (omitting the large vector field):

```sql
SELECT id, text FROM memory_test_user;
```

Count records:

```sql
SELECT COUNT(*) FROM memory_test_user;
```

Query specific memories (using text search):

```sql
SELECT id, text FROM memory_test_user WHERE text LIKE '%Paris%';
```

Delete test memories (if needed):

```sql
DELETE FROM memory_test_user WHERE text LIKE '%test%';
```

Exit the PostgreSQL shell:

```sql
\q
```

## Features

- Persistent memory for AI using vector embeddings
- Multiple vector store backends (FAISS and PostgreSQL)
- Easy integration into existing applications
- Simple CLI for testing and demonstration
