from logging import Logger, getLogger
from typing import Callable

import httpx
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

app = FastAPI()

# 添加跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['GET', 'POST'],
    allow_headers=['*'],
)

# 代理路径
proxy_paths = {
    '/pgc/player/api/playurl': 'api.bilibili.com',  # 港澳台、中国大陆 播放地址
    '/intl/gateway/v2/ogv/playurl': 'api.global.bilibili.com',  # 泰国、东南亚 播放地址
    '/intl/gateway/v2/app/subtitle': 'app.global.bilibili.com',  # 泰国、东南亚 字幕
    '/intl/gateway/v2/app/search/type': 'app.global.bilibili.com',  # 泰国、东南亚 搜索结果
}

log: Logger = getLogger(__name__)
log.info = log.error = log.warning = print  # 临时


@app.middleware('http')
async def proxy(request: Request, _: Callable[[Request], any]) -> any:
    """代理中间件"""

    # 检查 哔哩漫游版本
    bili_roaming_version = request.headers.get('x-from-biliroaming')
    if not bili_roaming_version:
        return Response(status_code=403)
    log.info(f'x-from-biliroaming: {bili_roaming_version}')

    # 检查 url路径
    if request.url.path not in proxy_paths:
        log.error(f'request other path: {request.url.path}')
        return Response(status_code=404)

    # 检查 目标地区
    target_area = request.query_params.get('area')
    if not target_area:
        log.error(f'area参数缺失')
        return JSONResponse(status_code=200, content={'code': '-1', 'message': 'area参数缺失'})
    log.info(f'area: {target_area}')

    # 构造 目标url
    target_url = proxy_paths[request.url.path] + request.url.path
    if len(request.url.query) > 0:
        target_url += '?' + request.url.query
    target_url = 'https://' + target_url
    log.info(f'target_url: {target_url}')

    # 构造 header
    request_headers = dict()
    for k, v in request.headers.items():
        if k.startswith('x-') or 'biliroaming' in k:
            continue  # 删除不必要的字段
        request_headers[k] = v
    request_headers['host'] = proxy_paths[request.url.path]  # 替换host

    # 代理请求
    async with httpx.AsyncClient() as client:
        response: httpx.Response = await client.request(request.method, target_url, headers=request_headers)
    log.info(f'response_status: {response.status_code}')

    # 构造 header
    return_headers = dict(response.headers)
    return_headers.pop('content-encoding', None)  # 删除压缩算法
    return_headers.pop('date', None)  # 删除日期
    return_headers.pop('content-length', None)  # 删除content-length，一般不存在
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=return_headers,
        media_type=return_headers['content-type']
    )


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8888)
