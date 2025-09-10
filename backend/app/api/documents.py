from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
import uuid
from pathlib import Path

router = APIRouter()

# 文档存储路径（指向 backend/data/documents）
DOCS_DIR = Path(__file__).parent.parent.parent / "data" / "documents"
DOCS_DIR.mkdir(parents=True, exist_ok=True)  # 自动创建目录


# 数据模型
class DocumentMetadata(BaseModel):
    id: str
    filename: str
    size: int
    created_at: datetime
    page_count: int

class DocumentListResponse(BaseModel):
    documents: List[DocumentMetadata]

class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    message: str

class DocumentDeleteResponse(BaseModel):
    id: str
    message: str


# 1. 获取所有文档列表
@router.get("/", response_model=DocumentListResponse)
async def get_all_documents():
    documents = []
    for file in DOCS_DIR.glob("*.pdf"):  # 只处理PDF文件
        # 提取文档ID（文件名前缀，不含后缀）
        doc_id = file.stem
        # 获取文件信息
        stat = file.stat()
        # 简单起见，页码默认为1（实际项目需用pdfplumber读取）
        documents.append(DocumentMetadata(
            id=doc_id,
            filename=file.name,
            size=stat.st_size,
            created_at=datetime.fromtimestamp(stat.st_ctime),
            page_count=1
        ))
    return DocumentListResponse(documents=documents)


# 2. 上传文档
@router.post("/", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="仅支持PDF文件")
    
    # 生成唯一ID
    doc_id = str(uuid.uuid4())
    save_path = DOCS_DIR / f"{doc_id}.pdf"
    
    # 保存文件
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return DocumentUploadResponse(
        id=doc_id,
        filename=file.filename,
        message="文档上传成功"
    )


# 3. 删除文档
@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(document_id: str):
    # 查找对应文件
    for file in DOCS_DIR.glob(f"{document_id}*.pdf"):
        file.unlink()  # 删除文件
        return DocumentDeleteResponse(
            id=document_id,
            message="文档已删除"
        )
    
    raise HTTPException(status_code=404, detail="文档不存在")