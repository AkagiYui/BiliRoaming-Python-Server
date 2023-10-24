import asyncio
from threading import Thread

from httpx import AsyncClient, Response

from cache import create_cache, get_cache
from config import proxy_paths
from logger import log
from model import ResolveRequest, ResolveResponse


def is_request_legal(request: ResolveRequest) -> str | None:
    """检查请求是否合法"""
    log.info(f'{request}')

    # 检查 area
    if request.query_area.lower() not in ['cn', 'hk', 'tw', 'th']:
        return 'area参数错误'

    # 禁止解析 天官赐福
    if request.query_ep_id == 778998:
        return '下载原神以观看天官赐福'

    return None


cache_loop = asyncio.new_event_loop()
Thread(target=cache_loop.run_forever, daemon=True).start()


async def revolve_request(request: ResolveRequest) -> ResolveResponse:
    """解析请求"""

    if cache_response := await get_cache(request):
        log.debug('命中缓存')
        return cache_response

    # 构造 目标url
    target_url = f'https://{proxy_paths[request.request_path]}{request.request_path}'
    if request.request_query and len(request.request_query) > 0:
        target_url += f'?{request.request_query}'

    # 构造 header
    new_headers = dict()
    for k, v in request.request_headers.items():
        # 过滤不必要的字段
        if k.startswith('x-') or 'biliroaming' in k:
            continue
        if k in ['build', 'host']:
            continue
        new_headers[k] = v
    new_headers['host'] = proxy_paths[request.request_path]  # 替换host

    # 代理请求
    async with AsyncClient(proxies={
        'http://': 'http://127.0.0.1:7890',
        'https://': 'http://127.0.0.1:7890',
    }) as client:
        response: Response = await client.request(request.request_method, target_url, headers=new_headers)

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
