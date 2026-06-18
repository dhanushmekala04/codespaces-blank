pinecone.py

from pinecone import Pinecone
from app.config.settings import settings

pc = Pinecone(
    api_key=settings.PINECONE_API_KEY
)

index = pc.Index(
    settings.PINECONE_INDEX
)

def get_pinecone_index():
    return index