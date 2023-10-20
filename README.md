# BiliRoaming Python 解析服务器

[哔哩漫游](https://github.com/yujincheng08/BiliRoaming)解析服务器的 Python 实现，
参考[自建解析服务器](https://github.com/yujincheng08/BiliRoaming/wiki/%E8%87%AA%E5%BB%BA%E8%A7%A3%E6%9E%90%E6%9C%8D%E5%8A%A1%E5%99%A8)。

## 使用

使用 `Python 3.11` 开发。
运行后需要使用带有 `SSL` 的 HTTP 服务器转发请求。

### 安装依赖

```shell
pip install -r requirements.txt
```

### 运行

```shell
python main.py
```

## TODO

- [ ] 允许使用代理请求服务器
- [ ] 响应缓存
- [ ] 请求校验
- [ ] 请求速率限制
- [ ] 用户校验
- [ ] 番剧校验
- [ ] 区域校验
- [ ] 哔哩漫游版本校验
