import pdfplumber
import os
import uuid
from datetime import datetime
from pathlib import Path
from app.config import DOCUMENTS_DIR
from app.models.document import DocumentMetadata

class DataCollection:
    @staticmethod
    def save_uploaded_file(file) -> str:
        """保存上传的文件并返回文件ID"""
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        file_path = DOCUMENTS_DIR / f"{file_id}{file_extension}"
        
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
            
        return file_id
    
    @staticmethod
    def read_pdf(file_id: str) -> tuple[list[str], int]:
        """读取PDF文件内容，返回每页文本和总页数"""
        # 查找文件
        for file in DOCUMENTS_DIR.glob(f"{file_id}.*"):
            if file.suffix.lower() == ".pdf":
                pages_text = []
                with pdfplumber.open(file) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text() or ""
                        pages_text.append(text)
                return pages_text, len(pages_text)
        
        raise FileNotFoundError(f"PDF文件 {file_id} 未找到")
    
    @staticmethod
    def get_document_metadata(file_id: str) -> DocumentMetadata:
        """获取文档元数据"""
        for file in DOCUMENTS_DIR.glob(f"{file_id}.*"):
            # 获取文件创建时间
            created_at = datetime.fromtimestamp(file.stat().st_ctime)
            
            # 如果是PDF，获取页数
            page_count = 0
            if file.suffix.lower() == ".pdf":
                with pdfplumber.open(file) as pdf:
                    page_count = len(pdf.pages)
            
            return DocumentMetadata(
                id=file_id,
                filename=file.name,
                size=file.stat().st_size,
                created_at=created_at,
                page_count=page_count
            )
        
        raise FileNotFoundError(f"文件 {file_id} 未找到")
    
    @staticmethod
    def get_all_documents() -> list[DocumentMetadata]:
        """获取所有文档的元数据"""
        documents = []
        # 获取所有文件ID（不带扩展名）
        file_ids = set()
        for file in DOCUMENTS_DIR.iterdir():
            if file.is_file():
                file_id = file.stem
                file_ids.add(file_id)
        
        # 为每个文件ID获取元数据
        for file_id in file_ids:
            try:
                metadata = DataCollection.get_document_metadata(file_id)
                documents.append(metadata)
            except FileNotFoundError:
                continue
        
        # 按创建时间排序（最新的在前）
        documents.sort(key=lambda x: x.created_at, reverse=True)
        return documents
    
    @staticmethod
    def delete_document(file_id: str) -> bool:
        """删除文档及其相关文件"""
        deleted = False
        for file in DOCUMENTS_DIR.glob(f"{file_id}.*"):
            file.unlink()
            deleted = True
        return deleted
