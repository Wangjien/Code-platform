from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)

debug_mode = os.getenv('FLASK_DEBUG', '').lower() in {'1', 'true', 'yes', 'on'}

# 配置CORS (生产环境建议配置具体域名)
allowed_origins = os.getenv('ALLOWED_ORIGINS', '*')
if allowed_origins != '*':
    allowed_origins = allowed_origins.split(',')
CORS(app, resources={"/*": {"origins": allowed_origins}})

# 配置JWT
jwt_secret = os.getenv('JWT_SECRET_KEY')
if not jwt_secret and not debug_mode:
    raise RuntimeError('JWT_SECRET_KEY must be set in non-debug environments')
app.config['JWT_SECRET_KEY'] = jwt_secret or 'dev-secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # 开发环境不设置过期时间
app.config['JWT_ERROR_MESSAGE_KEY'] = 'message'

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'mysql+pymysql://root:password@localhost:3306/bio_code_share')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化扩展
api = Api(app)
jwt = JWTManager(app)

# 初始化限流器
from utils.rate_limiter import create_limiter
limiter = create_limiter(app)

# 导入数据库模型
from models import db
db.init_app(app)

# 导入API资源
from resources.user import UserRegister, UserLogin, UserCodes, UserFavorites, UserProfile, UserPassword
from resources.code import CodeList, CodeDetail
from resources.category import CategoryList, CategoryDetail
from resources.tag import TagList, TagDetail
from resources.comment import CommentList, CommentDetail
from resources.favorite import FavoriteList, FavoriteDetail
from resources.admin import (
    AdminUsers,
    AdminUserDetail,
    AdminCodes,
    AdminCodeReview,
    AdminComments,
    AdminCommentDetail,
)
from resources.user_category import UserCategoryList, UserCategoryDetail, UserCategorySortOrder
from resources.health import HealthCheck

# 注册API路由
api.add_resource(UserRegister, '/api/register')
api.add_resource(UserLogin, '/api/login')
api.add_resource(CodeList, '/api/codes')
api.add_resource(CodeDetail, '/api/codes/<int:code_id>')
api.add_resource(CategoryList, '/api/categories')
api.add_resource(CategoryDetail, '/api/categories/<int:category_id>')
api.add_resource(TagList, '/api/tags')
api.add_resource(TagDetail, '/api/tags/<int:tag_id>')
api.add_resource(CommentList, '/api/codes/<int:code_id>/comments')
api.add_resource(CommentDetail, '/api/comments/<int:comment_id>')
api.add_resource(FavoriteList, '/api/favorites')
api.add_resource(FavoriteDetail, '/api/favorites/<int:favorite_id>')
api.add_resource(UserCodes, '/api/user/codes')
api.add_resource(UserFavorites, '/api/user/favorites')
api.add_resource(UserProfile, '/api/user/profile')
api.add_resource(UserPassword, '/api/user/password')

# Admin APIs
api.add_resource(AdminUsers, '/api/admin/users')
api.add_resource(AdminUserDetail, '/api/admin/users/<int:user_id>')
api.add_resource(AdminCodes, '/api/admin/codes')
api.add_resource(AdminCodeReview, '/api/admin/codes/<int:code_id>/review')
api.add_resource(AdminComments, '/api/admin/comments')
api.add_resource(AdminCommentDetail, '/api/admin/comments/<int:comment_id>')

# User Category APIs
api.add_resource(UserCategoryList, '/api/user/categories')
api.add_resource(UserCategoryDetail, '/api/user/categories/<int:category_id>')
api.add_resource(UserCategorySortOrder, '/api/user/categories/sort')

# Health Check API
api.add_resource(HealthCheck, '/api/health', '/health')

if __name__ == '__main__':
    # 创建数据库表
    with app.app_context():
        db.create_all()
    app.run(debug=debug_mode, host='0.0.0.0', port=5001)
