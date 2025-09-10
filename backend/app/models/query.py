from fastapi import APIRouter, HTTPException, Query
from app.core.retrieval import Retrieval
from app.core.generation import Generation
from app.core.data_collection import DataCollection
from app.models.query import QueryRequest, QueryResponse, ReferenceSource
from app.config import TOP_K, DEEPSEEK_API_KEY

router = APIRouter()

@router.post("/", response_model=QueryResponse)
async def process_query(
    query: QueryRequest,
    top_k: int = Query(default=TOP_K, ge=1, le=10),
    document_ids: list[str] = Query(default=None)
):
    """处理用户查询并返回答案"""
    try:
        # 检查API密钥
        if not DEEPSEEK_API_KEY:
            raise HTTPException(status_code=400, detail="请先配置DeepSeek API密钥")
        
        # 检索相关文档块
        retrieval = Retrieval()
        relevant_chunks = retrieval.retrieve_relevant_chunks(
            query=query.question,
            n_results=top_k,
            document_ids=document_ids
        )
        
        if not relevant_chunks:
            return QueryResponse(
                answer="未找到相关文档内容来回答这个问题。",
                references=[]
            )
        
        # 生成答案
        generator = Generation()
        answer = generator.generate_answer(
            question=query.question,
            context_chunks=relevant_chunks
        )
        
        # 准备引用来源
        references = []
        for chunk in relevant_chunks:
            metadata = chunk["metadata"]
            try:
                doc_metadata = DataCollection.get_document_metadata(metadata["document_id"])
                references.append(ReferenceSource(
                    document_id=metadata["document_id"],
                    filename=doc_metadata.filename,
                    page_number=metadata["page_number"],
                    content=chunk["document"]
                ))
            except Exception:
                continue
        
        return QueryResponse(
            answer=answer,
            references=references
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
