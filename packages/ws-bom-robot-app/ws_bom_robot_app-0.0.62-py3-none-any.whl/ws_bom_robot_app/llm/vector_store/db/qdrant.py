from langchain_qdrant import QdrantVectorStore as QDRANT, FastEmbedSparse, RetrievalMode
from qdrant_client import QdrantClient
from langchain_core.documents import Document
from typing import Any, Optional
import asyncio, gc, logging, os
from langchain_core.embeddings import Embeddings
from ws_bom_robot_app.llm.utils.chunker import DocumentChunker
from ws_bom_robot_app.llm.vector_store.db.base import VectorDBStrategy


class Qdrant(VectorDBStrategy):
    async def create(
        self,
        embeddings: Embeddings,
        documents: list[Document],
        storage_id: str,
        **kwargs
    ) -> Optional[str]:
        try:
            chunked_docs = DocumentChunker.chunk(documents)
            if not os.path.exists(storage_id):
                os.makedirs(storage_id)

            def _create():
              QDRANT.from_documents(
                  documents=chunked_docs,
                  embedding=embeddings,
                  sparse_embedding=kwargs['sparse_embedding'] if 'sparse_embedding' in kwargs else FastEmbedSparse(),
                  collection_name="default",
                  path=storage_id,
                  retrieval_mode=RetrievalMode.HYBRID
              )

            await asyncio.to_thread(_create)
            self._clear_cache(storage_id)
            return storage_id
        except Exception as e:
            logging.error(f"{Qdrant.__name__} create error: {e}")
            raise e
        finally:
            del documents
            gc.collect()

    def get_loader(
        self,
        embeddings: Embeddings,
        storage_id: str,
        **kwargs
    ) -> QDRANT:
        if storage_id not in self._CACHE:
            self._CACHE[storage_id] = QDRANT(
                client=QdrantClient(path=storage_id),
                collection_name="default",
                embedding=embeddings,
                sparse_embedding=FastEmbedSparse(),
                retrieval_mode=RetrievalMode.HYBRID,
            )
        return self._CACHE[storage_id]
