from typing import Literal

from pydantic import BaseModel


class ResolveRequest(BaseModel):
    """解析请求"""
    request_ip: str  # 用户ip
    request_path: str  # 请求路径
    request_user_agent: str   # UA
    request_method: Literal['GET']  # 请求方法
    request_headers: dict[str, str]  # 请求头
    request_query: str  # 请求参数

    biliroming_build: int  # 哔哩漫游版本
    biliroming_version: str  # 哔哩漫游版本
    biliroming_platform: str  # 哔哩漫游平台

    query_access_key: str  # 用户访问密钥
    query_appkey: str  # appkey 1d8b6e7d45233436
    query_area: Literal['cn', 'hk', 'tw', 'th']  # 请求地区 cn 中国大陆, hk 香港, tw 台湾, th 泰国/东南亚
    query_bilibili_build: int  # 哔哩哔哩版本
    query_cid: int  # 视频id
    query_device: str  # 设备 android
    query_ep_id: int  # 剧集id
    query_fnval: int  # 视频流格式 4048 https://github.com/SocialSisterYi/bilibili-API-collect/blob/7873a79022a5606e2391d93b411a05576a0df111/docs/bangumi/videostream_url.md?plain=1#L32
    query_fnver: int  # 视频流版本 0
    query_force_host: int  # 强制使用host 2
    query_fourk: str  # 4K 1
    query_mobi_app: str  # android
    query_platform: str  # android
    query_qn: int  # 清晰度 https://github.com/SocialSisterYi/bilibili-API-collect/blob/7873a79022a5606e2391d93b411a05576a0df111/docs/bangumi/videostream_url.md?plain=1#L7
    query_ts: int  # 时间戳 10位
    query_sign: str  # 请求签名


class ResolveResponse(BaseModel):
    content: bytes
    status_code: int
    headers: dict[str, str]
    media_type: str
