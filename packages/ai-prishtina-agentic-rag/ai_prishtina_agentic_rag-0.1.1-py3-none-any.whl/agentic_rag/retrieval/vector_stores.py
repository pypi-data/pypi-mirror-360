"""Vector store implementations for the Agentic RAG library."""

import asyncio
import json
import os
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from pydantic import BaseModel, Field

from ..utils.exceptions import VectorStoreError
from ..utils.logging import LoggerMixin


class Document(BaseModel):
    """Document representation for vector stores."""
    
    id: str = Field(description="Document ID")
    content: str = Field(description="Document content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    embedding: Optional[List[float]] = Field(default=None, description="Document embedding")


class SearchResult(BaseModel):
    """Search result from vector store."""
    
    document: Document = Field(description="Retrieved document")
    score: float = Field(description="Similarity score")
    rank: int = Field(description="Result rank")


class BaseVectorStore(ABC, LoggerMixin):
    """Abstract base class for vector stores."""
    
    def __init__(self, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.embedding_model = embedding_model
        self._embedding_function = None
        self._initialize_embeddings()
    
    def _initialize_embeddings(self) -> None:
        """Initialize embedding function."""
        try:
            from sentence_transformers import SentenceTransformer
            self._embedding_function = SentenceTransformer(self.embedding_model)
            self.logger.info(f"Initialized embedding model: {self.embedding_model}")
        except ImportError:
            self.logger.warning("sentence-transformers not available, embeddings disabled")
    
    def _embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text."""
        if not self._embedding_function:
            raise VectorStoreError("Embedding function not initialized")
        
        try:
            embedding = self._embedding_function.encode(text)
            return embedding.tolist()
        except Exception as e:
            raise VectorStoreError(f"Failed to generate embedding: {e}")
    
    @abstractmethod
    async def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the vector store."""
        pass
    
    @abstractmethod
    async def search(
        self, 
        query: str, 
        top_k: int = 5, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar documents."""
        pass
    
    @abstractmethod
    async def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents from the vector store."""
        pass
    
    @abstractmethod
    async def update_document(self, document: Document) -> bool:
        """Update a document in the vector store."""
        pass
    
    @abstractmethod
    async def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID."""
        pass
    
    @abstractmethod
    async def count_documents(self) -> int:
        """Get the total number of documents."""
        pass


class ChromaVectorStore(BaseVectorStore):
    """ChromaDB vector store implementation."""
    
    def __init__(
        self, 
        collection_name: str = "agentic_rag",
        persist_directory: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self._client = None
        self._collection = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize ChromaDB client."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            if self.persist_directory:
                self._client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(anonymized_telemetry=False)
                )
            else:
                self._client = chromadb.EphemeralClient()
            
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            self.logger.info(f"Initialized ChromaDB collection: {self.collection_name}")
            
        except ImportError:
            raise VectorStoreError("chromadb not installed. Install with: pip install chromadb")
        except Exception as e:
            raise VectorStoreError(f"Failed to initialize ChromaDB: {e}")
    
    async def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to ChromaDB."""
        if not self._collection:
            raise VectorStoreError("ChromaDB collection not initialized")

        if not documents:
            return []

        try:
            ids = []
            contents = []
            metadatas = []
            embeddings = []

            for doc in documents:
                if not doc or not doc.content:
                    continue

                doc_id = doc.id or str(uuid.uuid4())
                ids.append(doc_id)
                contents.append(doc.content)
                # Ensure metadata is not empty for ChromaDB
                metadata = doc.metadata if doc.metadata else {"source": "unknown"}
                metadatas.append(metadata)

                if doc.embedding:
                    embeddings.append(doc.embedding)
                else:
                    embedding = self._embed_text(doc.content)
                    embeddings.append(embedding)

            if not ids:
                return []

            self._collection.add(
                ids=ids,
                documents=contents,
                metadatas=metadatas,
                embeddings=embeddings
            )

            self.logger.info(f"Added {len(ids)} documents to ChromaDB")
            return ids

        except Exception as e:
            raise VectorStoreError(f"Failed to add documents to ChromaDB: {e}")
    
    async def search(
        self, 
        query: str, 
        top_k: int = 5, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search ChromaDB for similar documents."""
        if not self._collection:
            raise VectorStoreError("ChromaDB collection not initialized")
        
        try:
            # Check if we have any documents first
            count = self._collection.count()
            if count == 0:
                return []

            # Try embedding-based search first, fallback to text search
            try:
                query_embedding = self._embed_text(query)
                results = self._collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=filters,
                    include=["documents", "metadatas", "distances"]
                )
            except Exception as embedding_error:
                # Fallback to text-based search if embedding dimensions don't match
                self.logger.warning(f"Embedding search failed, using text search: {embedding_error}")
                results = self._collection.query(
                    query_texts=[query],
                    n_results=top_k,
                    where=filters,
                    include=["documents", "metadatas", "distances"]
                )
            
            search_results = []
            if not (results.get("documents", []) and results.get("metadatas", []) and
                    results.get("distances", []) and results.get("ids", [])):
                return []
            if not (results["documents"] and results["documents"][0] and
                    results["metadatas"] and results["metadatas"][0] and
                    results["distances"] and results["distances"][0] and
                    results["ids"] and results["ids"][0]):
                return []

            for i, (doc_id, content, metadata, distance) in enumerate(zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )):
                document = Document(
                    id=doc_id,
                    content=content,
                    metadata=dict(metadata)
                )
                
                # Convert distance to similarity score (ChromaDB uses cosine distance)
                similarity_score = 1.0 - distance
                
                search_results.append(SearchResult(
                    document=document,
                    score=similarity_score,
                    rank=i + 1
                ))
            
            return search_results
            
        except Exception as e:
            raise VectorStoreError(f"Failed to search ChromaDB: {e}")
    
    async def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents from ChromaDB."""
        if not self._collection:
            raise VectorStoreError("ChromaDB collection not initialized")
        
        try:
            self._collection.delete(ids=document_ids)
            self.logger.info(f"Deleted {len(document_ids)} documents from ChromaDB")
            return True
        except Exception as e:
            raise VectorStoreError(f"Failed to delete documents from ChromaDB: {e}")
    
    async def update_document(self, document: Document) -> bool:
        """Update a document in ChromaDB."""
        try:
            # ChromaDB doesn't have direct update, so we delete and re-add
            await self.delete_documents([document.id])
            await self.add_documents([document])
            return True
        except Exception as e:
            raise VectorStoreError(f"Failed to update document in ChromaDB: {e}")
    
    async def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID from ChromaDB."""
        if not self._collection:
            raise VectorStoreError("ChromaDB collection not initialized")
        
        try:
            results = self._collection.get(
                ids=[document_id],
                include=["documents", "metadatas"]
            )
            
            # Guard clause to prevent None is not subscriptable errors
            if not (isinstance(results.get("ids"), list) and results["ids"] and results["ids"][0] is not None and
                    isinstance(results.get("documents"), list) and results["documents"] and results["documents"][0] is not None and
                    isinstance(results.get("metadatas"), list) and results["metadatas"] and results["metadatas"][0] is not None):
                return None
            return Document(
                id=results["ids"][0],
                content=results["documents"][0],
                metadata=dict(results["metadatas"][0])
            )
            
        except Exception as e:
            raise VectorStoreError(f"Failed to get document from ChromaDB: {e}")
    
    async def count_documents(self) -> int:
        """Get the total number of documents in ChromaDB."""
        if not self._collection:
            raise VectorStoreError("ChromaDB collection not initialized")
        
        try:
            return self._collection.count()
        except Exception as e:
            raise VectorStoreError(f"Failed to count documents in ChromaDB: {e}")


class FAISSVectorStore(BaseVectorStore):
    """FAISS vector store implementation."""
    
    def __init__(
        self,
        dimension: int = 384,
        index_type: str = "flat",
        persist_path: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        if dimension <= 0:
            raise VectorStoreError("Dimension must be positive")
        self.dimension = dimension
        self.index_type = index_type
        self.persist_path = persist_path
        self._index = None
        self._documents = {}
        self._initialize_index()
    
    def _initialize_index(self) -> None:
        """Initialize FAISS index."""
        try:
            import faiss
            
            if self.index_type == "flat":
                self._index = faiss.IndexFlatIP(self.dimension)  # Inner product (cosine similarity)
            elif self.index_type == "ivf":
                quantizer = faiss.IndexFlatIP(self.dimension)
                self._index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
            else:
                raise VectorStoreError(f"Unsupported index type: {self.index_type}")
            
            # Load existing index if persist_path exists
            if self.persist_path and os.path.exists(self.persist_path):
                self._load_index()
            
            self.logger.info(f"Initialized FAISS index: {self.index_type}")
            
        except ImportError:
            raise VectorStoreError("faiss not installed. Install with: pip install faiss-cpu")
        except Exception as e:
            raise VectorStoreError(f"Failed to initialize FAISS: {e}")
    
    def _save_index(self) -> None:
        """Save FAISS index to disk."""
        if not self.persist_path or not self._index:
            return
        
        try:
            import faiss
            
            os.makedirs(os.path.dirname(self.persist_path), exist_ok=True)
            faiss.write_index(self._index, self.persist_path)
            
            # Save documents metadata
            docs_path = self.persist_path + ".docs"
            with open(docs_path, 'w') as f:
                json.dump({k: v.model_dump() for k, v in self._documents.items()}, f)
            
        except Exception as e:
            self.logger.error(f"Failed to save FAISS index: {e}")
    
    def _load_index(self) -> None:
        """Load FAISS index from disk."""
        try:
            import faiss
            
            self._index = faiss.read_index(self.persist_path)
            
            # Load documents metadata
            if self.persist_path is not None:
                docs_path = self.persist_path + ".docs"
                if os.path.exists(docs_path):
                    with open(docs_path, 'r') as f:
                        docs_data = json.load(f)
                        self._documents = {k: Document(**v) for k, v in docs_data.items()}
            
        except Exception as e:
            self.logger.error(f"Failed to load FAISS index: {e}")
    
    async def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to FAISS."""
        if not self._index:
            raise VectorStoreError("FAISS index not initialized")
        
        try:
            embeddings = []
            
            for doc in documents:
                if doc.embedding:
                    embeddings.append(doc.embedding)
                else:
                    embedding = self._embed_text(doc.content)
                    embeddings.append(embedding)
                    doc.embedding = embedding
                
                self._documents[doc.id] = doc
            
            # Normalize embeddings for cosine similarity
            embeddings_array = np.array(embeddings, dtype=np.float32)

            # Import faiss here to handle import errors gracefully
            try:
                import faiss
                if embeddings_array.shape[0] == 0:
                    raise VectorStoreError("No embeddings to add to FAISS index")
                if embeddings_array.ndim == 1:
                    embeddings_array = embeddings_array.reshape(1, -1)
                if self.index_type == "ivf":
                    nlist = getattr(self._index, "nlist", None)
                    if nlist is not None:
                        if embeddings_array.shape[0] < nlist:
                            raise VectorStoreError(f"IVF index requires at least {nlist} vectors to train, got {embeddings_array.shape[0]}")
                        if not self._index.is_trained:
                            self._index.train(embeddings_array)  # type: ignore
                self._index.add(embeddings_array)  # type: ignore
            except ImportError:
                raise VectorStoreError("faiss not installed. Install with: pip install faiss-cpu")
            
            if self.persist_path:
                self._save_index()
            
            self.logger.info(f"Added {len(documents)} documents to FAISS")
            return [doc.id for doc in documents]
            
        except Exception as e:
            raise VectorStoreError(f"Failed to add documents to FAISS: {e}")
    
    async def search(
        self, 
        query: str, 
        top_k: int = 5, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search FAISS for similar documents."""
        if not self._index:
            raise VectorStoreError("FAISS index not initialized")
        
        try:
            import faiss

            query_embedding = np.array([self._embed_text(query)], dtype=np.float32)
            faiss.normalize_L2(query_embedding)
            if query_embedding.ndim == 1:
                query_embedding = query_embedding.reshape(1, -1)
            scores, indices = self._index.search(query_embedding, top_k)  # type: ignore
            
            search_results = []
            doc_list = list(self._documents.values())
            
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(doc_list):
                    document = doc_list[idx]
                    
                    # Apply filters if provided
                    if filters:
                        if not all(document.metadata.get(k) == v for k, v in filters.items()):
                            continue
                    
                    search_results.append(SearchResult(
                        document=document,
                        score=float(score),
                        rank=i + 1
                    ))
            
            return search_results
            
        except Exception as e:
            raise VectorStoreError(f"Failed to search FAISS: {e}")
    
    async def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents from FAISS."""
        # FAISS doesn't support direct deletion, would need to rebuild index
        # For now, just remove from documents dict
        try:
            for doc_id in document_ids:
                if doc_id in self._documents:
                    del self._documents[doc_id]
            
            self.logger.warning("FAISS doesn't support direct deletion. Documents removed from metadata only.")
            return True
            
        except Exception as e:
            raise VectorStoreError(f"Failed to delete documents from FAISS: {e}")
    
    async def update_document(self, document: Document) -> bool:
        """Update a document in FAISS."""
        # Similar to delete, FAISS doesn't support direct updates
        try:
            self._documents[document.id] = document
            self.logger.warning("FAISS doesn't support direct updates. Document metadata updated only.")
            return True
        except Exception as e:
            raise VectorStoreError(f"Failed to update document in FAISS: {e}")
    
    async def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID from FAISS."""
        return self._documents.get(document_id)
    
    async def count_documents(self) -> int:
        """Get the total number of documents in FAISS."""
        return len(self._documents)


class PineconeVectorStore(BaseVectorStore):
    """Pinecone vector store implementation."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        environment: Optional[str] = None,
        index_name: str = "agentic-rag",
        dimension: int = 384,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        self.environment = environment or os.getenv("PINECONE_ENVIRONMENT")
        self.index_name = index_name
        self.dimension = dimension
        self._index = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize Pinecone client."""
        try:
            import pinecone

            if not self.api_key:
                raise VectorStoreError("Pinecone API key not provided")
            if not self.environment:
                raise VectorStoreError("Pinecone environment not provided")

            # Pinecone client version mismatch: init, list_indexes, create_index, and Index are not available.
            # Please update this code to match your installed pinecone-client version.
            raise VectorStoreError("The installed pinecone-client version is not compatible with this code. Please update the code or install a compatible pinecone-client version.")

        except ImportError:
            raise VectorStoreError("pinecone-client not installed. Install with: pip install pinecone-client")
        except Exception as e:
            raise VectorStoreError(f"Failed to initialize Pinecone: {e}")

    async def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to Pinecone."""
        if not self._index:
            raise VectorStoreError("Pinecone index not initialized")

        try:
            vectors = []

            for doc in documents:
                if doc.embedding:
                    embedding = doc.embedding
                else:
                    embedding = self._embed_text(doc.content)

                vectors.append({
                    "id": doc.id,
                    "values": embedding,
                    "metadata": {
                        "content": doc.content[:1000],  # Pinecone metadata size limit
                        **doc.metadata
                    }
                })

            # Upsert vectors in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self._index.upsert(vectors=batch)

            self.logger.info(f"Added {len(documents)} documents to Pinecone")
            return [doc.id for doc in documents]

        except Exception as e:
            raise VectorStoreError(f"Failed to add documents to Pinecone: {e}")

    async def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search Pinecone for similar documents."""
        if not self._index:
            raise VectorStoreError("Pinecone index not initialized")

        try:
            query_embedding = self._embed_text(query)

            # Build filter for Pinecone
            pinecone_filter = None
            if filters:
                pinecone_filter = {k: {"$eq": v} for k, v in filters.items()}

            response = self._index.query(
                vector=query_embedding,
                top_k=top_k,
                filter=pinecone_filter,
                include_metadata=True
            )

            search_results = []
            for i, match in enumerate(response.matches):
                metadata = match.metadata
                content = metadata.pop("content", "")

                document = Document(
                    id=match.id,
                    content=content,
                    metadata=metadata
                )

                search_results.append(SearchResult(
                    document=document,
                    score=float(match.score),
                    rank=i + 1
                ))

            return search_results

        except Exception as e:
            raise VectorStoreError(f"Failed to search Pinecone: {e}")

    async def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents from Pinecone."""
        if not self._index:
            raise VectorStoreError("Pinecone index not initialized")

        try:
            self._index.delete(ids=document_ids)
            self.logger.info(f"Deleted {len(document_ids)} documents from Pinecone")
            return True
        except Exception as e:
            raise VectorStoreError(f"Failed to delete documents from Pinecone: {e}")

    async def update_document(self, document: Document) -> bool:
        """Update a document in Pinecone."""
        try:
            # Pinecone updates via upsert
            await self.add_documents([document])
            return True
        except Exception as e:
            raise VectorStoreError(f"Failed to update document in Pinecone: {e}")

    async def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID from Pinecone."""
        if not self._index:
            raise VectorStoreError("Pinecone index not initialized")

        try:
            response = self._index.fetch(ids=[document_id])

            if document_id not in response.vectors:
                return None

            vector_data = response.vectors[document_id]
            metadata = vector_data.metadata
            content = metadata.pop("content", "")

            return Document(
                id=document_id,
                content=content,
                metadata=metadata,
                embedding=vector_data.values
            )

        except Exception as e:
            raise VectorStoreError(f"Failed to get document from Pinecone: {e}")

    async def count_documents(self) -> int:
        """Get the total number of documents in Pinecone."""
        if not self._index:
            raise VectorStoreError("Pinecone index not initialized")

        try:
            stats = self._index.describe_index_stats()
            return stats.total_vector_count
        except Exception as e:
            raise VectorStoreError(f"Failed to count documents in Pinecone: {e}")


class WeaviateVectorStore(BaseVectorStore):
    """Weaviate vector store implementation for weaviate-client 4.15.4+ (v4 API)."""

    def __init__(
        self,
        url: str = "http://localhost:8080",
        api_key: Optional[str] = None,
        class_name: str = "AgenticRAG",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.url = url
        self.api_key = api_key
        self.class_name = class_name
        self._client = None
        self._collection = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize Weaviate client using v4 API."""
        try:
            import weaviate
            from weaviate.classes.config import Configure

            # Initialize client with v4 API
            if self.api_key:
                self._client = weaviate.connect_to_local(
                    host=self.url.replace("http://", "").replace("https://", ""),
                    headers={"X-OpenAI-Api-Key": self.api_key}
                )
            else:
                self._client = weaviate.connect_to_local(
                    host=self.url.replace("http://", "").replace("https://", "")
                )

            # Create collection if it doesn't exist
            if not self._client.collections.exists(self.class_name):
                self._client.collections.create(
                    name=self.class_name,
                    vectorizer_config=Configure.Vectorizer.none(),
                    properties=[
                        weaviate.classes.config.Property(
                            name="content",
                            data_type=weaviate.classes.config.DataType.TEXT
                        ),
                        weaviate.classes.config.Property(
                            name="source",
                            data_type=weaviate.classes.config.DataType.TEXT
                        )
                    ]
                )

            self._collection = self._client.collections.get(self.class_name)
            self.logger.info(f"Initialized Weaviate client with collection: {self.class_name}")

        except ImportError:
            raise VectorStoreError("weaviate-client>=4.15.4 not installed. Install with: pip install weaviate-client>=4.15.4")
        except Exception as e:
            raise VectorStoreError(f"Failed to initialize Weaviate: {e}")

    async def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to Weaviate using v4 API."""
        if not self._collection:
            raise VectorStoreError("Weaviate collection not initialized")

        try:
            ids = []
            for doc in documents:
                # Prepare properties
                properties = {
                    "content": doc.content,
                    "source": doc.metadata.get("source", "unknown")
                }

                # Add other metadata as additional properties
                for k, v in doc.metadata.items():
                    if k != "source":
                        properties[k] = str(v)

                # Get or generate embedding
                if doc.embedding:
                    vector = doc.embedding
                else:
                    vector = self._embed_text(doc.content)

                # Insert document with vector
                obj_uuid = self._collection.data.insert(
                    properties=properties,
                    vector=vector,
                    uuid=doc.id if doc.id else None
                )

                ids.append(str(obj_uuid))

            self.logger.info(f"Added {len(ids)} documents to Weaviate")
            return ids

        except Exception as e:
            raise VectorStoreError(f"Failed to add documents to Weaviate: {e}")

    async def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search Weaviate for similar documents using v4 API."""
        if not self._collection:
            raise VectorStoreError("Weaviate collection not initialized")

        try:
            # Generate query embedding
            query_vector = self._embed_text(query)

            # Build where filter if provided
            where_filter = None
            if filters:
                import weaviate.classes.query as wq
                filter_conditions = []
                for key, value in filters.items():
                    filter_conditions.append(wq.Filter.by_property(key).equal(value))

                if len(filter_conditions) == 1:
                    where_filter = filter_conditions[0]
                else:
                    where_filter = wq.Filter.all_of(filter_conditions)

            # Perform vector search with correct v4 API
            from weaviate.classes.query import MetadataQuery

            response = self._collection.query.near_vector(
                near_vector=query_vector,
                limit=top_k,
                where=where_filter,
                return_metadata=MetadataQuery(distance=True)
            )

            search_results = []
            for i, obj in enumerate(response.objects):
                # Convert UUID to string and handle properties safely
                document = Document(
                    id=str(obj.uuid),
                    content=str(obj.properties.get("content", "")),
                    metadata={
                        "source": str(obj.properties.get("source", "unknown")),
                        **{k: str(v) for k, v in obj.properties.items() if k not in ["content", "source"]}
                    }
                )

                # Convert distance to similarity score
                distance = obj.metadata.distance if obj.metadata and hasattr(obj.metadata, 'distance') else 0.0
                similarity_score = 1.0 / (1.0 + distance)  # Convert distance to similarity

                search_results.append(SearchResult(
                    document=document,
                    score=similarity_score,
                    rank=i + 1
                ))

            return search_results

        except Exception as e:
            raise VectorStoreError(f"Failed to search Weaviate: {e}")

    async def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents from Weaviate using v4 API."""
        if not self._collection:
            raise VectorStoreError("Weaviate collection not initialized")

        try:
            from uuid import UUID

            for doc_id in document_ids:
                # Convert string ID to UUID if needed
                try:
                    uuid_id = UUID(doc_id) if isinstance(doc_id, str) else doc_id
                    self._collection.data.delete_by_id(uuid_id)
                except ValueError:
                    # If doc_id is not a valid UUID, try deleting by string
                    self._collection.data.delete_by_id(doc_id)

            self.logger.info(f"Deleted {len(document_ids)} documents from Weaviate")
            return True

        except Exception as e:
            raise VectorStoreError(f"Failed to delete documents from Weaviate: {e}")

    async def update_document(self, document: Document) -> bool:
        """Update a document in Weaviate using v4 API."""
        if not self._collection:
            raise VectorStoreError("Weaviate collection not initialized")

        try:
            from uuid import UUID

            # Prepare properties
            properties = {
                "content": document.content,
                "source": document.metadata.get("source", "unknown")
            }

            # Add other metadata
            for k, v in document.metadata.items():
                if k != "source":
                    properties[k] = str(v)

            # Convert string ID to UUID if needed
            try:
                uuid_id = UUID(document.id) if isinstance(document.id, str) else document.id
            except ValueError:
                uuid_id = document.id

            # Update with vector if available
            if document.embedding:
                self._collection.data.update(
                    uuid=uuid_id,
                    properties=properties,
                    vector=document.embedding
                )
            else:
                self._collection.data.update(
                    uuid=uuid_id,
                    properties=properties
                )

            self.logger.info(f"Updated document {document.id} in Weaviate")
            return True

        except Exception as e:
            raise VectorStoreError(f"Failed to update document in Weaviate: {e}")

    async def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID from Weaviate using v4 API."""
        if not self._collection:
            raise VectorStoreError("Weaviate collection not initialized")

        try:
            from uuid import UUID

            # Convert string ID to UUID if needed
            try:
                uuid_id = UUID(document_id) if isinstance(document_id, str) else document_id
            except ValueError:
                uuid_id = document_id

            # Get object by ID with vector
            obj = self._collection.query.fetch_object_by_id(
                uuid=uuid_id,
                include_vector=True
            )

            if not obj:
                return None

            return Document(
                id=str(obj.uuid),
                content=str(obj.properties.get("content", "")),
                metadata={
                    "source": str(obj.properties.get("source", "unknown")),
                    **{k: str(v) for k, v in obj.properties.items() if k not in ["content", "source"]}
                },
                embedding=obj.vector.get("default") if obj.vector and isinstance(obj.vector.get("default"), list) else None
            )

        except Exception as e:
            raise VectorStoreError(f"Failed to get document from Weaviate: {e}")

    async def count_documents(self) -> int:
        """Get the total number of documents in Weaviate using v4 API."""
        if not self._collection:
            raise VectorStoreError("Weaviate collection not initialized")

        try:
            # Use aggregate query to count objects
            result = self._collection.aggregate.over_all(total_count=True)
            return result.total_count if result.total_count else 0

        except Exception as e:
            raise VectorStoreError(f"Failed to count documents in Weaviate: {e}")
