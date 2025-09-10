import requests
import json
from typing import List, Dict, Any
from app.config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL

class Generation:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or DEEPSEEK_API_KEY
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未配置，请先设置API密钥")
    
    def generate_answer(
        self, 
        question: str, 
        context_chunks: List[Dict[str, Any]]
    ) -> str:
        """
        调用DeepSeek API生成基于上下文的答案
        
        Args:
            question: 用户问题
            context_chunks: 检索到的相关上下文块
            
        Returns:
            生成的答案
        """
        # 构建上下文
        context = "\n\n".join([
            f"文档片段 {i+1}：{chunk['document']}" 
            for i, chunk in enumerate(context_chunks)
        ])
        
        # 构建提示词
        prompt = f"""基于以下提供的上下文信息，回答用户的问题。
如果上下文信息不足以回答问题，请明确说明无法回答，不要编造信息。
回答应简洁明了，并且基于上下文内容。

上下文：
{context}

用户问题：
{question}

回答：
"""
        
        # 调用DeepSeek API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一个帮助用户解答问题的助手，只根据提供的上下文回答问题。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        try:
            response = requests.post(
                DEEPSEEK_API_URL,
                headers=headers,
                data=json.dumps(data)
            )
            
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        except Exception as e:
            return f"调用DeepSeek API时出错：{str(e)}"
