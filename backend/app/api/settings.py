from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import re
from dotenv import load_dotenv  # 用于读取.env文件
from pathlib import Path

# 1. 关键：创建APIRouter实例（必须有这行，否则main.py找不到router）
router = APIRouter()

# 2. 加载环境变量（从backend根目录的.env文件读取）
# 先确定.env文件路径：backend根目录 → 即 app/api/../.. 目录
env_file_path = Path(__file__).parent.parent.parent / ".env"
# 加载.env文件（如果不存在，不会报错，后续用默认值）
load_dotenv(dotenv_path=env_file_path)


# 3. 定义数据模型（前端传参/后端返回的格式，必须与前端匹配）
class SettingsResponse(BaseModel):
    """后端返回给前端的设置格式"""
    deepseek_api_key: str  # 脱敏后的API密钥（避免泄露）
    top_k: int             # 检索相关片段数量（默认3）

class SettingsUpdateRequest(BaseModel):
    """前端提交设置的格式"""
    deepseek_api_key: str  # 完整API密钥
    top_k: int             # 1-10之间的整数


# 4. 核心接口1：获取当前设置（前端初始化时调用，这是报错的关键接口）
@router.get("/", response_model=SettingsResponse)
async def get_current_settings():
    try:
        # 从.env文件读取配置（没有则用默认值）
        api_key = os.getenv("DEEPSEEK_API_KEY", "")  # 读取API密钥
        top_k = int(os.getenv("TOP_K", 3))           # 读取检索数量，默认3
        
        # API密钥脱敏（仅显示前5位+***，避免前端显示完整密钥）
        masked_api_key = ""
        if len(api_key) >= 5:
            masked_api_key = api_key[:5] + "***"
        elif len(api_key) > 0:
            masked_api_key = api_key + "***"
        
        # 返回符合前端预期的格式
        return SettingsResponse(
            deepseek_api_key=masked_api_key,
            top_k=top_k
        )
    
    except Exception as e:
        # 捕获所有异常，返回明确的错误信息
        raise HTTPException(status_code=500, detail=f"获取设置失败：{str(e)}")


# 5. 核心接口2：保存设置（前端修改后提交调用）
@router.put("/", response_model=SettingsResponse)
async def update_settings(request: SettingsUpdateRequest):
    try:
        # 验证参数：top_k必须在1-10之间（避免检索数量异常）
        if not (1 <= request.top_k <= 10):
            raise HTTPException(status_code=400, detail="检索数量（top_k）必须是1-10之间的整数")
        
        # 读取现有.env文件内容（如果不存在，创建空内容）
        env_content = ""
        if env_file_path.exists():
            env_content = env_file_path.read_text(encoding="utf-8")
        
        # 替换或添加DEEPSEEK_API_KEY（处理已有配置的情况）
        if re.search(r"^DEEPSEEK_API_KEY=.*$", env_content, re.MULTILINE):
            # 替换已有行
            env_content = re.sub(
                pattern=r"^DEEPSEEK_API_KEY=.*$",
                repl=f"DEEPSEEK_API_KEY={request.deepseek_api_key}",
                string=env_content,
                flags=re.MULTILINE
            )
        else:
            # 添加新行（如果文件为空，先去掉换行符）
            env_content = env_content.strip() + f"\nDEEPSEEK_API_KEY={request.deepseek_api_key}"
        
        # 替换或添加TOP_K
        if re.search(r"^TOP_K=.*$", env_content, re.MULTILINE):
            env_content = re.sub(
                pattern=r"^TOP_K=.*$",
                repl=f"TOP_K={request.top_k}",
                string=env_content,
                flags=re.MULTILINE
            )
        else:
            env_content += f"\nTOP_K={request.top_k}"
        
        # 保存到.env文件（确保有写入权限）
        env_file_path.write_text(env_content.strip(), encoding="utf-8")
        
        # 重新加载环境变量（使新设置立即生效）
        load_dotenv(dotenv_path=env_file_path, override=True)
        
        # 返回脱敏后的设置（与前端格式匹配）
        masked_api_key = request.deepseek_api_key[:5] + "***" if len(request.deepseek_api_key)>=5 else ""
        return SettingsResponse(
            deepseek_api_key=masked_api_key,
            top_k=request.top_k
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存设置失败：{str(e)}")