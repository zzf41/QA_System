from typing import List, Dict, Any, Optional
from app.core.vector_store import VectorStore
from app.config import TOP_K

class Retrieval:
    def __init__(self):
        self.vector_store = VectorStore()
    
    def retrieve_relevant_chunks(
        self, 
        query: str, 
        n_results: int = TOP_K,
        document_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        检索与查询相关的文档块
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            document_ids: 可选，指定文档ID列表，只在这些文档中搜索
            
        Returns:
            相关文档块列表
        """
        return self.vector_store.search(
            query=query,
            n_results=n_results,
            document_ids=document_ids
        )
