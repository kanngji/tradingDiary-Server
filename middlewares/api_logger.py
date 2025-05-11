from fastapi import Request, Response
from db.mongo import mongo_db
from datetime import datetime

async def log_middleware(request: Request, call_next):
    # 너무 자주 호출되는 체결량 웹소켓 제외
    exclude_paths = [
        "/api/coinvloumePower"
    ]
    if any(request.url.path.startswith(path) for path in exclude_paths):
        return await call_next(request)

    try:
        response = await call_next(request)
        status_code = response.status_code
        error_message = None
    except Exception as e:
        status_code = 500
        error_message = str(e)
        response = Response("Internal server error", status_code=500)

    log_doc = {
        "path": str(request.url.path),
        "method": request.method,
        "client_ip": request.client.host,
        "timestamp": datetime.utcnow(),
        "status_code": status_code,
        "error": error_message
    }

    await mongo_db.api_logs.insert_one(log_doc)

    if error_message:
        print(f"API 호출 실패 → {request.url.path} : {error_message}")

    return response