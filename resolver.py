import asyncio
import time
from threading import Thread

from httpx import AsyncClient, Response

from config import proxy_paths
from logger import log
from model import ResolveRequest, ResolveResponse


def is_request_legal(request: ResolveRequest) -> str | None:
    """检查请求是否合法"""

    # 检查 area
    if request.query_area.lower() not in ['cn', 'hk', 'tw', 'th']:
        return 'area参数错误'

    return None


cache_loop = asyncio.new_event_loop()
Thread(target=cache_loop.run_forever, daemon=True).start()


async def revolve_request(request: ResolveRequest) -> ResolveResponse:
    """解析请求"""

    # 构造 目标url
    target_url = f'https://{proxy_paths[request.request_path]}{request.request_path}'
    if request.request_query and len(request.request_query) > 0:
        target_url += f'?{request.request_query}'
    log.info(f'target_url: {target_url}')

    # 构造 header
    new_headers = dict()
    for k, v in request.request_headers.items():
        if k.startswith('x-') or 'biliroaming' in k:
            continue  # 删除不必要的字段
        if k == 'build':
            continue
        new_headers[k] = v
    new_headers['host'] = proxy_paths[request.request_path]  # 替换host

    # 代理请求
    async with AsyncClient() as client:
        response: Response = await client.request(request.request_method, target_url, headers=new_headers)
    log.info(f'response_status: {response.status_code}')

    # 构造 header
    return_headers = dict(response.headers)
    return_headers.pop('content-encoding', None)  # 删除压缩算法
    return_headers.pop('date', None)  # 删除日期
    return_headers.pop('content-length', None)  # 删除content-length，一般不存在

    resolve_response = ResolveResponse(
        content=response.content,
        status_code=response.status_code,
        headers=return_headers,
        media_type=response.headers.get('content-type')
    )

    asyncio.run_coroutine_threadsafe(create_cache(request, resolve_response), cache_loop)
    return resolve_response


async def create_cache(request: ResolveRequest, response: ResolveResponse) -> None:
    """创建缓存"""
    log.debug('创建缓存')
    time.sleep(5)
    log.debug('缓存创建完成')
