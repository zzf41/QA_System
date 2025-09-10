from pydantic import BaseModel
from typing import List, Optional
from fastapi import APIRouter, HTTPException

router = APIRouter()

# 数据模型
class QueryRequest(BaseModel):
    question: str

class ReferenceSource(BaseModel):
    document_id: str
    filename: str
    page_number: int
    content: str

class QueryResponse(BaseModel):
    answer: str
    references: List[ReferenceSource]


# 处理查询请求
@router.post("/", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")
    
    # 模拟回答（实际项目需对接RAG逻辑）
    return QueryResponse(
        answer=f"这是针对问题「{request.question}」的回答（模拟数据）",
        references=[
            ReferenceSource(
                document_id="test123",
                filename="示例文档.pdf",
                page_number=2,
                content="这是文档中与问题相关的内容片段..."
            )
        ]
    )

# 在main.py中随便加一行注释，比如：
# 这是一个测试修改，用于触发提交