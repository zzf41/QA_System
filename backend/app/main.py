from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

# 正确导入路由实例（使用别名）
from app.api.documents import router as documents_router
from app.api.queries import router as queries_router
from app.api.settings import router as settings_router

# 创建FastAPI应用
app = FastAPI(title="轻量化RAG知识库问答系统")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 关键修正：使用导入的别名注册路由（而非模块名）
app.include_router(documents_router, prefix="/api/documents", tags=["documents"])
app.include_router(queries_router, prefix="/api/queries", tags=["queries"])
app.include_router(settings_router, prefix="/api/settings", tags=["settings"])

# 挂载静态文件
frontend_dir = Path(__file__).parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount(
        path="/",
        app=StaticFiles(directory=str(frontend_dir), html=True),
        name="frontend"
    )
    print(f"✅ 静态文件目录已挂载：{frontend_dir}")
else:
    print(f"⚠️  警告：前端目录 {frontend_dir} 不存在")

# 健康检查接口
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 在main.py中随便加一行注释，比如：
# 这是一个测试修改，用于触发提交