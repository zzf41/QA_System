from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from pathlib import Path
from app.config import DEEPSEEK_API_KEY, TOP_K, ROOT_DIR
from app.models.settings import Settings, SettingsUpdateRequest

router = APIRouter()

# 环境变量文件路径
ENV_FILE = ROOT_DIR / ".env"

@router.get("/", response_model=Settings)
async def get_settings():
    """获取当前系统设置"""
    return Settings(
        deepseek_api_key=DEEPSEEK_API_KEY if DEEPSEEK_API_KEY else "",
        top_k=TOP_K
    )

@router.put("/", response_model=Settings)
async def update_settings(settings: SettingsUpdateRequest):
    """更新系统设置"""
    try:
        # 更新环境变量文件
        env_content = ""
        if ENV_FILE.exists():
            with open(ENV_FILE, "r") as f:
                env_content = f.read()
        
        # 更新DEEPSEEK_API_KEY
        if "DEEPSEEK_API_KEY" in env_content:
            env_content = re.sub(
                r"DEEPSEEK_API_KEY=.*",
                f"DEEPSEEK_API_KEY={settings.deepseek_api_key}",
                env_content
            )
        else:
            env_content += f"\nDEEPSEEK_API_KEY={settings.deepseek_api_key}"
        
        # 更新TOP_K
        if "TOP_K" in env_content:
            env_content = re.sub(
                r"TOP_K=.*",
                f"TOP_K={settings.top_k}",
                env_content
            )
        else:
            env_content += f"\nTOP_K={settings.top_k}"
        
        with open(ENV_FILE, "w") as f:
            f.write(env_content)
        
        # 更新配置（需要重启应用才能生效）
        from app.config import DEEPSEEK_API_KEY as config_api_key
        from app.config import TOP_K as config_top_k
        
        # 注意：这只是为了返回更新后的值，实际配置需要重启应用
        return Settings(
            deepseek_api_key=settings.deepseek_api_key,
            top_k=settings.top_k
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
