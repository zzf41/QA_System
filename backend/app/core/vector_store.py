import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from app.config import VECTOR_DB_DIR
from app.core.embedding import Embedding

class VectorStore:
    _instance = None
    _client = None
    _collection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            # 初始化Chroma客户端
            self._client = chromadb.Client(
                Settings(
                    persist_directory=str(VECTOR_DB_DIR),
                    anonymized_telemetry=False
                )
            )
            # 获取或创建集合
            self._collection = self._client.get_or_create_collection(name="documents")
            # 初始化嵌入模型
            self.embedding = Embedding()
    
    def add_documents(self, document_id: str, chunks: List[tuple[str, int]]) -> None:
        """
        添加文档块到向量存储
        
        Args:
            document_id: 文档ID
            chunks: 文档块列表，每个元素是(文本, 页码)
        """
        # 先删除该文档已有的所有块
        self.delete_document(document_id)
        
        # 准备数据
        ids = []
        documents = []
        metadatas = []
        
        for i, (text, page_num) in enumerate(chunks):
            chunk_id = f"{document_id}_chunk_{i}"
            ids.append(chunk_id)
            documents.append(text)
            metadatas.append({
                "document_id": document_id,
                "page_number": page_num
            })
        
        # 生成嵌入向量
        embeddings = self.embedding.embed_texts(documents)
        
        # 添加到集合
        self._collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
        
        # 持久化
        self._client.persist()
    
    def search(self, query: str, n_results: int = 3, document_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        搜索与查询相关的文档块
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            document_ids: 可选，指定文档ID列表，只在这些文档中搜索
            
        Returns:
            搜索结果列表，每个结果包含文档块信息和元数据
        """
        # 生成查询向量
        query_embedding = self.embedding.embed_text(query)
        
        # 构建过滤条件
        where = None
        if document_ids:
            where = {"document_id": {"$in": document_ids}}
        
        # 搜索
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )
        
        # 整理结果
        formatted_results = []
        for i in range(len(results["ids"][0])):
            formatted_results.append({
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })
        
        return formatted_results
    
    def delete_document(self, document_id: str) -> None:
        """删除指定文档的所有块"""
        self._collection.delete(
            where={"document_id": document_id}
        )
        self._client.persist()
    
    def get_document_ids(self) -> List[str]:
        """获取所有文档ID"""
        results = self._collection.get(
            include=[]  # 只获取ID和元数据
        )
        
        # 从元数据中提取唯一的document_id
        document_ids = set()
        for metadata in results["metadatas"]:
            if metadata and "document_id" in metadata:
                document_ids.add(metadata["document_id"])
        
        return list(document_ids)
