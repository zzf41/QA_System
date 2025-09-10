import os
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量
load_dotenv()

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent

# 数据存储目录
DATA_DIR = ROOT_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
VECTOR_DB_DIR = DATA_DIR / "vector_db"

# 创建目录（如果不存在）
for dir_path in [DATA_DIR, DOCUMENTS_DIR, VECTOR_DB_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")

# 嵌入模型配置
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# 检索配置
TOP_K = 3  # 检索最相关的3个片段
