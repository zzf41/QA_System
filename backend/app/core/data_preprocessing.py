import re
from typing import List, Tuple

class DataPreprocessing:
    @staticmethod
    def clean_text(text: str) -> str:
        """清洗文本，去除多余空白和特殊字符"""
        # 去除多余的空白字符
        text = re.sub(r'\s+', ' ', text).strip()
        # 去除特殊字符
        text = re.sub(r'[^\w\s.,!?;:\'-]', '', text)
        return text
    
    @staticmethod
    def split_text_into_chunks(
        pages_text: List[str], 
        chunk_size: int = 300, 
        chunk_overlap: int = 50
    ) -> List[Tuple[str, int]]:
        """
        将文本分割成块，同时保留页码信息
        
        Args:
            pages_text: 每页的文本内容列表
            chunk_size: 每个块的大致长度（字符数）
            chunk_overlap: 块之间的重叠长度（字符数）
            
        Returns:
            元组列表，每个元组包含(文本块, 页码)
        """
        chunks = []
        
        for page_num, page_text in enumerate(pages_text, 1):
            cleaned_text = DataPreprocessing.clean_text(page_text)
            if not cleaned_text:
                continue
            
            # 按段落分割
            paragraphs = re.split(r'\n\s*\n', cleaned_text)
            
            for para in paragraphs:
                if len(para) <= chunk_size:
                    chunks.append((para, page_num))
                else:
                    # 如果段落过长，进一步分割
                    start = 0
                    while start < len(para):
                        end = start + chunk_size
                        # 找到合适的分割点（空格处）
                        if end < len(para):
                            end = para.rfind(' ', start, end)
                            if end == -1:  # 如果没有找到空格，就硬分割
                                end = start + chunk_size
                        
                        chunk = para[start:end].strip()
                        if chunk:
                            chunks.append((chunk, page_num))
                        
                        # 下一次开始位置，考虑重叠
                        start = end - chunk_overlap
                        if start <= 0:
                            start = end
        
        return chunks
