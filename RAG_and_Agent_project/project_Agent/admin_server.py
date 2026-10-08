"""
后台管理服务启动入口

运行方式: python admin_server.py   （默认端口 8001）
"""

import os

import uvicorn


if __name__ == "__main__":
    port = int(os.environ.get("API_PORT", 8001))
    uvicorn.run(
        "admin_api.main:app",
        host="127.0.0.1",
        port=port,
        reload=False,
    )
