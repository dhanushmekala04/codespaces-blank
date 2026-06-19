"""Pinecone vector database client with lazy initialization."""

from typing import TYPE_CHECKING

from config.settings import settings

if TYPE_CHECKING:
    from pinecone import Index

_index = None


def get_pinecone_index():
    """
    Return the Pinecone index, initializing it on first call.

    Lazy init avoids crashing at import time when PINECONE_API_KEY
    is empty (e.g. during local development without vector search).
    """
    global _index
    if _index is None:
        if not settings.pinecone_api_key:
            raise RuntimeError(
                "PINECONE_API_KEY is not set. "
                "Configure it in .env to use vector search features."
            )
        from pinecone import Pinecone

        pc = Pinecone(api_key=settings.pinecone_api_key)
        _index = pc.Index(settings.pinecone_index)
    return _index


def close_pinecone() -> None:
    """Reset the Pinecone index reference (for testing / teardown)."""
    global _index
    _index = None
