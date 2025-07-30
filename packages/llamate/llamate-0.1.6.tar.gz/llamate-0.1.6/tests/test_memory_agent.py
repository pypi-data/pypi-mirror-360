import os
import pytest
import numpy as np
from llamate.agent import MemoryAgent
from llamate.vectorstore_postgres import PostgresVectorStore
from llamate.embedder import OpenAIEmbedder

@pytest.mark.skipif("postgres" not in os.getenv("LLAMATE_VECTOR_BACKEND", ""), reason="Postgres not selected")
def test_agent_postgres():
    embedder = OpenAIEmbedder()
    store = PostgresVectorStore(
        db_url=os.environ["LLAMATE_DATABASE_URL"],
        table="test_memory"
    )
    agent = MemoryAgent(user_id="test_user_pg", vectorstore=store, embedder=embedder)
    
    agent.chat("The launch event is in October.")
    response = agent.chat("When is the launch event?")
    assert "October" in response

