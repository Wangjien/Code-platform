from marshmallow import Schema, fields, validate, ValidationError
import re

class UserRegistrationSchema(Schema):
    username = fields.Str(
        required=True, 
        validate=[
            validate.Length(min=3, max=20, error="用户名长度必须在3-20字符之间"),
            validate.Regexp(r'^[a-zA-Z0-9_]+$', error="用户名只能包含字母、数字和下划线")
        ]
    )
    email = fields.Email(required=True, error_messages={'invalid': '邮箱格式无效'})
    password = fields.Str(
        required=True, 
        validate=[
            validate.Length(min=6, max=50, error="密码长度必须在6-50字符之间"),
            validate.Regexp(
                r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]+$', 
                error="密码必须包含至少一个字母和一个数字"
            )
        ]
    )

class UserLoginSchema(Schema):
    email = fields.Email(required=True, error_messages={'invalid': '邮箱格式无效'})
    password = fields.Str(required=True, validate=validate.Length(min=1, error="密码不能为空"))

class CodeCreateSchema(Schema):
    title = fields.Str(
        required=True, 
        validate=validate.Length(min=1, max=200, error="标题长度必须在1-200字符之间")
    )
    description = fields.Str(
        required=True, 
        validate=validate.Length(min=1, max=2000, error="描述长度必须在1-2000字符之间")
    )
    content = fields.Str(
        required=True, 
        validate=validate.Length(min=1, max=50000, error="代码内容长度不能超过50000字符")
    )
    language = fields.Str(
        required=True, 
        validate=validate.OneOf(['Python', 'R', 'Shell', 'JavaScript', 'Java'], error="不支持的编程语言")
    )
    category_id = fields.Int(required=True, validate=validate.Range(min=1, error="分类ID无效"))
    user_category_id = fields.Int(missing=None, validate=validate.Range(min=1, error="用户分类ID无效"))
    environment = fields.Str(missing="", validate=validate.Length(max=5000, error="环境配置过长"))
    license = fields.Str(
        missing="MIT", 
        validate=validate.OneOf(['MIT', 'GPL-3.0', 'Apache-2.0', 'BSD-3-Clause'], error="不支持的开源协议")
    )
    tags = fields.List(
        fields.Str(validate=validate.Length(min=1, max=50)), 
        missing=[], 
        validate=validate.Length(max=10, error="最多只能添加10个标签")
    )
    results = fields.List(fields.Dict(), missing=[])

class CommentCreateSchema(Schema):
    content = fields.Str(
        required=True, 
        validate=validate.Length(min=1, max=1000, error="评论长度必须在1-1000字符之间")
    )

def sanitize_html(content):
    """基础HTML净化，移除潜在危险标签"""
    import re
    # 移除script、iframe、object等危险标签
    dangerous_tags = ['script', 'iframe', 'object', 'embed', 'form', 'input']
    for tag in dangerous_tags:
        content = re.sub(rf'<{tag}[^>]*>.*?</{tag}>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(rf'<{tag}[^>]*/?>', '', content, flags=re.IGNORECASE)
    return content

def validate_file_upload(file):
    """文件上传验证"""
    if not file:
        raise ValidationError("文件不能为空")
    
    # 检查文件大小 (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    file.seek(0, 2)  # 移动到文件末尾
    size = file.tell()
    file.seek(0)  # 重置到文件开头
    
    if size > MAX_FILE_SIZE:
        raise ValidationError("文件大小不能超过10MB")
    
    # 检查文件类型
    allowed_extensions = {'.py', '.r', '.sh', '.js', '.java', '.txt', '.md', '.yml', '.yaml', '.json'}
    filename = file.filename or ''
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        raise ValidationError("不支持的文件类型")
    
    return True
