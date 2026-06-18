from app.db.pinecone import get_pinecone_index

class PineconeService:

    def search(self, vector, namespace):

        index = get_pinecone_index()

        return index.query(
            vector=vector,
            top_k=5,
            namespace=namespace,
            include_metadata=True
        )