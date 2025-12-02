from flask_sqlalchemy import SQLAlchemy

# 创建SQLAlchemy实例
db = SQLAlchemy()

# 导入所有模型，确保它们被注册
from .user import User
from .code import Code
from .result import Result
from .category import Category
from .tag import Tag
from .code_tag import CodeTag
from .comment import Comment
from .favorite import Favorite
