import time
from datetime import datetime, timedelta
from threading import Thread

from logger import log
from model import ResolveRequest, ResolveResponse

cache_value_type = tuple[datetime, ResolveResponse]
cache_manager: dict[tuple, cache_value_type] = dict()  # 缓存管理器
cache_timeout: timedelta = timedelta(hours=1)  # 缓存过期时间


def _remove_timeout_cache() -> None:
    """删除过期缓存"""
    while True:
        current_time = datetime.now()
        keys_to_remove = list()
        for key, value in cache_manager.items():
            if (current_time - value[0]) >= cache_timeout:
                keys_to_remove.append(key)
        for key in keys_to_remove:
            cache_manager.pop(key)

        log.debug('缓存清理完成')
        time.sleep(60 * 30)  # 每30分钟清理一次


Thread(target=_remove_timeout_cache, daemon=True).start()  # 启动缓存清理线程


def _get_cache_key(request: ResolveRequest) -> tuple:
    """生成缓存key"""
    return (
        request.request_path,
        request.request_method,
        request.query_access_key,  # todo 大会员问题，包含该字段则为单用户缓存
        request.query_appkey,
        request.query_area,
        request.query_cid,
        request.query_device,
        request.query_ep_id,
        request.query_fnval,
        request.query_fnver,
        request.query_force_host,
        request.query_fourk,
        request.query_mobi_app,
        request.query_platform,
    )


async def create_cache(request: ResolveRequest, response: ResolveResponse) -> None:
    """创建缓存"""
    cache_manager[_get_cache_key(request)] = (datetime.now(), response)
    log.debug('缓存创建完成')


async def get_cache(request: ResolveRequest) -> ResolveResponse | None:
    """获取缓存"""
    cache_key = _get_cache_key(request)
    cache: cache_value_type = cache_manager.get(cache_key, None)
    if cache is None:
        return None
    if (datetime.now() - cache[0]) >= cache_timeout:
        cache_manager.pop(cache_key)  # 缓存过期
        return None
    return cache[1]
