from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.core.data_collection import DataCollection
from app.core.data_preprocessing import DataPreprocessing
from app.core.vector_store import VectorStore
from app.models.document import (
    DocumentListResponse,
    DocumentUploadResponse,
    DocumentDeleteResponse
)

router = APIRouter()

@router.get("/", response_model=DocumentListResponse)
async def get_all_documents():
    """获取所有文档的列表"""
    try:
        documents = DataCollection.get_all_documents()
        return DocumentListResponse(documents=documents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """上传文档并处理"""
    try:
        # 检查文件类型
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="只支持PDF文件上传")
        
        # 保存文件
        file_id = DataCollection.save_uploaded_file(file)
        
        # 读取PDF内容
        pages_text, page_count = DataCollection.read_pdf(file_id)
        
        # 预处理文本（分割成块）
        chunks = DataPreprocessing.split_text_into_chunks(pages_text)
        
        # 存储向量
        vector_store = VectorStore()
        vector_store.add_documents(file_id, chunks)
        
        return DocumentUploadResponse(
            id=file_id,
            filename=file.filename,
            message=f"文档上传成功，共 {page_count} 页"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(document_id: str):
    """删除指定文档"""
    try:
        # 删除文档文件
        file_deleted = DataCollection.delete_document(document_id)
        
        # 删除向量存储中的文档
        vector_store = VectorStore()
        vector_store.delete_document(document_id)
        
        if file_deleted:
            return DocumentDeleteResponse(
                id=document_id,
                message="文档删除成功"
            )
        else:
            raise HTTPException(status_code=404, detail="文档未找到")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
