from functools import wraps
from flask import current_app, request
import json
import hashlib
import time
from typing import Any, Optional

class SimpleMemoryCache:
    """简单内存缓存实现"""
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key in self._cache:
            timestamp, ttl = self._timestamps.get(key, (0, 0))
            if ttl == 0 or (time.time() - timestamp) < ttl:
                return self._cache[key]
            else:
                # 过期删除
                self.delete(key)
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """设置缓存值，ttl为过期时间（秒）"""
        self._cache[key] = value
        self._timestamps[key] = (time.time(), ttl)
        
        # 简单的内存清理：超过1000条时清理过期项
        if len(self._cache) > 1000:
            self._cleanup_expired()
    
    def delete(self, key: str) -> None:
        """删除缓存项"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
    
    def clear(self) -> None:
        """清空所有缓存"""
        self._cache.clear()
        self._timestamps.clear()
    
    def _cleanup_expired(self) -> None:
        """清理过期缓存项"""
        now = time.time()
        expired_keys = []
        
        for key, (timestamp, ttl) in self._timestamps.items():
            if ttl > 0 and (now - timestamp) >= ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            self.delete(key)

# 全局缓存实例
_memory_cache = SimpleMemoryCache()

def cached_response(ttl: int = 300, key_prefix: str = ""):
    """API响应缓存装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 生成缓存键
            cache_key = _generate_cache_key(f.__name__, key_prefix, request)
            
            # 尝试从缓存获取
            cached_result = _memory_cache.get(cache_key)
            if cached_result is not None:
                current_app.logger.debug(f"Cache hit: {cache_key}")
                return cached_result
            
            # 执行原函数
            result = f(*args, **kwargs)
            
            # 只缓存成功的响应
            if isinstance(result, tuple):
                data, status_code = result
                if 200 <= status_code < 300:
                    _memory_cache.set(cache_key, result, ttl)
                    current_app.logger.debug(f"Cache set: {cache_key}")
            elif isinstance(result, dict):
                _memory_cache.set(cache_key, result, ttl)
                current_app.logger.debug(f"Cache set: {cache_key}")
            
            return result
        return decorated_function
    return decorator

def _generate_cache_key(func_name: str, prefix: str, request_obj) -> str:
    """生成缓存键"""
    # 基础键
    key_parts = [prefix or func_name]
    
    # 添加查询参数
    if request_obj.args:
        sorted_params = sorted(request_obj.args.items())
        params_str = "&".join([f"{k}={v}" for k, v in sorted_params])
        key_parts.append(params_str)
    
    # 添加用户ID（对于需要用户权限的接口）
    try:
        from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            key_parts.append(f"user_{user_id}")
    except Exception:
        pass
    
    # 生成最终键
    cache_key = ":".join(key_parts)
    
    # 如果键太长，使用hash
    if len(cache_key) > 200:
        cache_key = hashlib.md5(cache_key.encode()).hexdigest()
    
    return cache_key

def invalidate_cache(pattern: str = None):
    """清理缓存"""
    if pattern:
        # 模式匹配清理（简单实现）
        keys_to_delete = [key for key in _memory_cache._cache.keys() if pattern in key]
        for key in keys_to_delete:
            _memory_cache.delete(key)
    else:
        _memory_cache.clear()

# 预定义缓存时间常量
CACHE_TTL = {
    'SHORT': 60,      # 1分钟
    'MEDIUM': 300,    # 5分钟  
    'LONG': 900,      # 15分钟
    'HOUR': 3600,     # 1小时
    'DAY': 86400      # 1天
}
