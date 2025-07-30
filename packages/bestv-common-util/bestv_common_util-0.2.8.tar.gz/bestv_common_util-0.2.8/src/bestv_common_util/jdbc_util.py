from urllib.parse import urlparse, parse_qs


def parse_jdbc_url(jdbc_url):
    """
    解析 MySQL JDBC URL 并返回 PyMySQL 连接所需的参数
    支持格式：
      1. jdbc:mysql://user:pass@host:port/database
      2. jdbc:mysql://host:port/database?user=xxx&password=xxx
    """
    if not (jdbc_url.startswith("jdbc:") or jdbc_url.startswith("mysql+")):
        raise ValueError("Invalid JDBC URL: Must start with 'jdbc:' or 'mysql+'")

    # 去掉 jdbc: 前缀并解析
    parsed = urlparse(jdbc_url[5:])  # 移除 "jdbc:"

    # 验证必要参数
    if not parsed.hostname:
        raise ValueError("Invalid JDBC URL: Host not found")

    # 提取基础参数
    host = parsed.hostname
    port = parsed.port or 3306  # 默认端口 3306
    database = parsed.path[1:] if parsed.path else None  # 移除开头的 '/'

    # 优先使用 URL 中的用户认证 (user:pass@host)
    user = parsed.username
    password = parsed.password

    # 次优使用查询参数 (?user=xx&password=xx)
    query_params = parse_qs(parsed.query)
    if user is None and "user" in query_params:
        user = query_params["user"][0]
    if password is None and "password" in query_params:
        password = query_params["password"][0]

    return {
        "host": host,
        "port": port,
        "database": database,
        "user": user,
        "password": password
    }

