from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from svc_user_auth_zxw.apis import api_用户权限_增加
from svc_user_auth_zxw.apis import api_JWT, api_用户权限_验证
from svc_user_auth_zxw.apis.api_登录注册 import 微信H5快捷登录, 账号密码注册登录, 手机注册登录
from svc_user_auth_zxw.apis.api_登录注册 import logout
from svc_user_auth_zxw.apis import api_会员类型管理, api_用户会员管理, api_会员权限验证
from svc_user_auth_zxw.apis import api_邀请管理
import logging
from fastapi.responses import JSONResponse
from svc_user_auth_zxw.db import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动: 在 FastAPI 应用启动时创建表结构
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("All tables created if not existing.")

    # 使用Yield，控制程序回到FastAPI服务
    yield

    # 关闭逻辑: close connections, etc.
    await engine.dispose()


router = APIRouter(lifespan=lifespan)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# @router.exception_handler(Exception)
# async def global_exception_handler(request, exc):
#     logger.error(f"Unhandled exception: {exc}")
#     return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# Register API routers
router.include_router(api_用户权限_增加.router, tags=["用户权限管理"])
router.include_router(api_用户权限_验证.router, tags=["用户权限管理"])
router.include_router(api_JWT.router, tags=["JWT"])
router.include_router(手机注册登录.api_注册登录.router, tags=["注册登录-手机邮箱"])
router.include_router(微信H5快捷登录.api_注册登录.router, tags=["登录注册-微信公众号"])
router.include_router(账号密码注册登录.api_注册登录.router, tags=["登录注册-账号密码"])
router.include_router(logout.router, tags=["退出登录"])

# 会员管理相关路由
router.include_router(api_会员类型管理.router, tags=["会员类型管理"])
router.include_router(api_用户会员管理.router, tags=["用户会员管理"])
router.include_router(api_会员权限验证.router, tags=["会员权限验证"])

# 邀请管理相关路由
router.include_router(api_邀请管理.router, tags=["邀请管理"])

# Run the application
if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)

    uvicorn.run(app, host="localhost", port=8101)
