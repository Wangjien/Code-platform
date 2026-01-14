from functools import wraps
from flask import request, jsonify, current_app
from flask_limiter import RateLimitExceeded

def rate_limit(limit_string):
    """API限流装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                limiter = current_app.extensions.get('limiter')
                if limiter:
                    # 检查限流
                    limiter.check()
                return f(*args, **kwargs)
            except RateLimitExceeded:
                return {'message': '请求过于频繁，请稍后再试', 'error': 'rate_limit_exceeded'}, 429
            except Exception as e:
                # 限流器异常时不阻断正常请求
                current_app.logger.warning(f"Rate limiter error: {e}")
                return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_input(schema):
    """输入验证装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                from marshmallow import ValidationError
                data = request.get_json() or {}
                schema_instance = schema() if callable(schema) else schema
                validated_data = schema_instance.load(data)
                return f(validated_data, *args, **kwargs)
            except ValidationError as e:
                return {
                    'message': '输入数据验证失败', 
                    'errors': e.messages
                }, 400
            except Exception as e:
                current_app.logger.error(f"Validation error: {e}")
                return {'message': '数据验证失败'}, 400
        return decorated_function
    return decorator
