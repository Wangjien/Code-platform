from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request

def get_user_id():
    """获取用户ID用于限流，未登录用户使用IP"""
    from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        return f"user_{user_id}" if user_id else get_remote_address()
    except Exception:
        return get_remote_address()

def create_limiter(app):
    """创建限流器"""
    return Limiter(
        app=app,
        key_func=get_user_id,
        default_limits=["1000 per hour"],  # 默认每小时1000次请求
        storage_uri="memory://"  # 使用内存存储，生产环境可用Redis
    )

# 预定义限流规则
RATE_LIMITS = {
    'auth': "10 per minute",      # 登录注册限制
    'upload': "20 per minute",    # 上传限制
    'search': "100 per minute",   # 搜索限制
    'api': "200 per minute"       # 一般API限制
}
