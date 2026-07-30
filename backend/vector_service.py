import os
import chromadb
from typing import List, Dict, Any, Optional
from backend.config import settings

class VectorMemoryService:
    """ChromaDB Vector Store Manager for Semantic Chat Context Retrieval."""
    
    _client = None
    _collection = None

    @classmethod
    def get_collection(cls):
        if cls._collection is None:
            os.makedirs(settings.CHROMADB_DIR, exist_ok=True)
            cls._client = chromadb.PersistentClient(path=settings.CHROMADB_DIR)
            cls._collection = cls._client.get_or_create_collection(
                name="chat_vector_memory",
                metadata={"hnsw:space": "cosine"}
            )
        return cls._collection

    @classmethod
    def add_message(cls, user_id: str, chat_id: str, message_id: str, role: str, content: str, title: Optional[str] = None):
        """Index a chat message turn into ChromaDB vector store."""
        if not content or not content.strip():
            return
        
        try:
            collection = cls.get_collection()
            collection.add(
                documents=[content.strip()],
                metadatas=[{
                    "user_id": str(user_id),
                    "chat_id": str(chat_id),
                    "role": str(role),
                    "title": str(title or "Chat Thread"),
                }],
                ids=[str(message_id)]
            )
        except Exception as e:
            print(f"[Vector Memory Warning] Failed to index message {message_id}: {str(e)}")

    @classmethod
    def get_top_k_relevant_context(
        cls, user_id: str, chat_id: Optional[str], query_text: str, top_k: int = 5, enable_inter_chat: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Query ChromaDB for top-K semantically relevant historical messages.
        - If enable_inter_chat == True: Queries across ALL user threads (user_id).
        - If enable_inter_chat == False: Queries strictly within the current thread (chat_id).
        """
        if not query_text or not query_text.strip() or not user_id:
            return []

        try:
            collection = cls.get_collection()
            count = collection.count()
            if count == 0:
                return []

            # Dynamic filter based on user toggle preference
            if enable_inter_chat:
                where_filter = {"user_id": str(user_id)}
            else:
                if not chat_id:
                    return []
                where_filter = {"chat_id": str(chat_id)}

            results = collection.query(
                query_texts=[query_text.strip()],
                n_results=min(top_k, count),
                where=where_filter
            )

            relevant_turns = []
            if results and results.get("documents") and len(results["documents"]) > 0:
                documents = results["documents"][0]
                metadatas = results.get("metadatas", [[]])[0]

                for doc, meta in zip(documents, metadatas):
                    role = meta.get("role", "user") if meta else "user"
                    thread_title = meta.get("title", "Past Chat Thread") if meta else "Past Chat Thread"
                    relevant_turns.append({
                        "role": role,
                        "content": doc,
                        "title": thread_title
                    })

            return relevant_turns
        except Exception as e:
            print(f"[Vector Memory Warning] Query failed for user {user_id}: {str(e)}")
            return []
