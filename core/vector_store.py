from typing import List, Dict, Optional
from config.settings import settings
import json
import os


class VectorStore:
    """Simplified vector database using in-memory storage"""

    def __init__(self):
        self.documents = []
        self.brand_voice_docs = []
        self.research_docs = []

    def add_documents(self, documents: List[str], metadatas: List[Dict], ids: List[str]):
        """Add documents to the vector store"""
        for doc, meta, doc_id in zip(documents, metadatas, ids):
            entry = {
                "id": doc_id,
                "document": doc,
                "metadata": meta
            }
            self.documents.append(entry)

            # Categorize for easier retrieval
            if meta.get("type") == "brand_voice":
                self.brand_voice_docs.append(entry)
            elif meta.get("type") == "research":
                self.research_docs.append(entry)

    def search(self, query: str, n_results: int = 5, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """Search for similar documents (simple keyword matching)"""
        results = {"documents": [[]], "metadatas": [[]], "ids": [[]]}

        # Filter documents
        filtered_docs = self.documents
        if filter_dict:
            doc_type = filter_dict.get("type")
            if doc_type == "brand_voice":
                filtered_docs = self.brand_voice_docs
            elif doc_type == "research":
                filtered_docs = self.research_docs

        # Simple keyword search
        query_lower = query.lower()
        scored_docs = []
        for entry in filtered_docs:
            doc_lower = entry["document"].lower()
            # Count keyword matches
            score = sum(1 for word in query_lower.split() if word in doc_lower)
            if score > 0:
                scored_docs.append((score, entry))

        # Sort by score and return top results
        scored_docs.sort(reverse=True, key=lambda x: x[0])
        top_docs = scored_docs[:n_results]

        for _, entry in top_docs:
            results["documents"][0].append(entry["document"])
            results["metadatas"][0].append(entry["metadata"])
            results["ids"][0].append(entry["id"])

        return results

    def get_brand_voice_examples(self, n_examples: int = 3) -> List[str]:
        """Retrieve brand voice examples"""
        examples = [doc["document"] for doc in self.brand_voice_docs[:n_examples]]
        return examples

    def add_brand_voice_example(self, content: str, doc_id: str):
        """Add a brand voice example"""
        self.add_documents(
            documents=[content],
            metadatas=[{"type": "brand_voice"}],
            ids=[doc_id]
        )

    def store_research(self, topic: str, content: str, source: str, doc_id: str):
        """Store research results"""
        self.add_documents(
            documents=[content],
            metadatas=[{"type": "research", "topic": topic, "source": source}],
            ids=[doc_id]
        )

    def retrieve_research(self, topic: str, n_results: int = 5) -> List[Dict]:
        """Retrieve research on a topic"""
        return self.search(
            query=topic,
            n_results=n_results,
            filter_dict={"type": "research"}
        )


# Singleton instance
vector_store = VectorStore()
