# 🦙 Llamate

Llamate is a memory-augmented agent framework for Large Language Models (LLMs) that provides persistent, retrievable memory for AI conversations.

## What is Llamate?

Llamate solves a fundamental limitation of current LLMs: their inability to remember past conversations beyond a single context window. It creates a vector database of memories that can be semantically searched and retrieved during conversations, allowing LLMs to maintain continuity and context over extended interactions.

## How It Works

1. **Memory Storage**: Llamate stores important pieces of conversation as vector embeddings in a database (either FAISS or PostgreSQL).
2. **Semantic Retrieval**: When new queries come in, Llamate searches for semantically relevant past memories.
3. **Context Enhancement**: Retrieved memories are injected into the conversation context, allowing the LLM to access and utilize past information.
4. **User Identification**: Each user gets a unique memory space, ensuring personalized conversation history.

## Key Features

- **Multiple Backend Support**: Works with FAISS (file-based) or PostgreSQL (with pgvector)
- **Persistence**: Memories remain available between sessions and application restarts
- **Simple API**: Easy-to-use Python interface that works with any LLM
- **CLI Interface**: Command-line tool for quick testing and interaction
- **Production Ready**: Designed for both development and production environments


## Quick Start

Follow these steps to set up, use, and view data in Llamate with PostgreSQL:

### 1. Install Llamate

```bash
pip install llamate
```

### 2. Start PostgreSQL Container

```bash
docker run --name llamate-postgres -e POSTGRES_USER=llamate -e POSTGRES_PASSWORD=llamate -e POSTGRES_DB=llamate -p 5432:5432 -d ankane/pgvector
```

### 3. Initialize Llamate

```bash
llamate --init
# Select 'postgres' as your vector store backend
# Enter connection string: postgresql://llamate:llamate@localhost:5432/llamate
```

### 4. Run a Test Script to Store Data

Create a file `test_llamate.py`:

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

### 5. View Data in PostgreSQL

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
