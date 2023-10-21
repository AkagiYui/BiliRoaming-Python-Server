from logging import DEBUG
from typing import Callable

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from config import proxy_paths
from logger import log
from model import ResolveRequest
from resolver import is_request_legal, revolve_request

app = FastAPI()

# 添加跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['GET', 'POST'],
    allow_headers=['*'],
)


@app.middleware('http')
async def proxy(request: Request, _: Callable[[Request], any]) -> any:
    """代理中间件"""
    request_headers = dict(request.headers)
    request_params = dict(request.query_params)
    request_path = request.url.path
    request_ip = request_headers.get('x-forwarded-for') or request.client.host
    request_query = request.url.query
    request_method = request.method

    # 检查 哔哩漫游版本
    bili_roaming_version = request_headers.get('x-from-biliroaming')
    if not bili_roaming_version:
        return Response(status_code=403)

    # 检查 url路径
    if request_path not in proxy_paths:
        log.error(f'request other path: {request_path}')
        return Response(status_code=404)

    # 校验请求合法性
    resolve_request = ResolveRequest(
        request_ip=request_ip,
        request_path=request_path,
        request_user_agent=request_headers.get('user-agent'),
        request_method=request_method,
        request_headers=request_headers,
        request_query=request_query,
        biliroming_build=int(request_headers.get('build')),
        biliroming_version=bili_roaming_version,
        biliroming_platform=request_headers.get('platform-from-biliroaming'),
        query_access_key=request_params.get('access_key'),
        query_appkey=request_params.get('appkey'),
        query_area=request_params.get('area'),
        query_bilibili_build=int(request_params.get('build')),
        query_cid=int(request_params.get('cid')),
        query_device=request_params.get('device'),
        query_ep_id=int(request_params.get('ep_id')),
        query_fnval=int(request_params.get('fnval')),
        query_fnver=int(request_params.get('fnver')),
        query_force_host=int(request_params.get('force_host')),
        query_fourk=request_params.get('fourk'),
        query_mobi_app=request_params.get('mobi_app'),
        query_platform=request_params.get('platform'),
        query_qn=int(request_params.get('qn')),
        query_ts=int(request_params.get('ts')),
        query_sign=request_params.get('sign'),
    )
    if msg := is_request_legal(resolve_request):
        log.error(f'请求不合法: {msg}')
        return JSONResponse(status_code=200, content={'code': '-1', 'message': msg})

    # 解析请求
    resolve_response = await revolve_request(resolve_request)
    return Response(
        content=resolve_response.content,
        status_code=resolve_response.status_code,
        headers=resolve_response.headers,
        media_type=resolve_response.media_type,
    )


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8888, log_level=DEBUG)
