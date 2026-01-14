'''
Author: Wangjien2 1569399536@qq.com
Date: 2025-12-01 23:12:23
LastEditors: Wangjien2 1569399536@qq.com
LastEditTime: 2025-12-01 23:36:53
FilePath: /代码分享平台/backend/resources/user.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import check_password_hash
from flask import current_app
from models.user import User
from models.code import Code
from models.favorite import Favorite
from models import db
from utils.rate_limiter import RATE_LIMITS

#############################
# User API
#
# 该文件提供“用户”相关接口：
# - 注册 / 登录
# - 获取当前用户发布的代码
# - 获取/更新用户资料
# - 修改密码
#
# 关键点：
# - 权限：除注册/登录外均需要 JWT
# - 性能：UserCodes 预加载 Code 相关关系，避免 to_dict() 触发 N+1
# - 安全：密码使用哈希（见 User.set_password/check_password）；异常仅记录日志不回传细节
#############################

class UserRegister(Resource):
    #############################
    # POST /api/register
    #
    # 用户注册：校验 username/email 唯一性后创建用户。
    #############################
    def post(self):
        # 应用限流：注册接口每分钟最多10次
        from flask import current_app
        limiter = current_app.extensions.get('limiter')
        if limiter:
            limiter.limit(RATE_LIMITS['auth'])(lambda: None)()
        
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='Username is required')
        parser.add_argument('email', type=str, required=True, help='Email is required')
        parser.add_argument('password', type=str, required=True, help='Password is required')
        args = parser.parse_args()
        
        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=args['username']).first():
            return {'message': 'Username already exists'}, 400
        
        if User.query.filter_by(email=args['email']).first():
            return {'message': 'Email already exists'}, 400
        
        # 创建新用户
        user = User(username=args['username'], email=args['email'])
        user.set_password(args['password'])
        
        try:
            db.session.add(user)
            db.session.commit()
            return {'message': 'User created successfully'}, 201
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception('Failed to register user')
            return {'message': 'Internal server error'}, 500

class UserLogin(Resource):
    #############################
    # POST /api/login
    #
    # 用户登录：验证邮箱+密码，成功后签发 JWT access_token。
    #############################
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help='Email is required')
        parser.add_argument('password', type=str, required=True, help='Password is required')
        args = parser.parse_args()
        
        # 查找用户
        user = User.query.filter_by(email=args['email']).first()
        
        if not user or not user.check_password(args['password']):
            return {'message': 'Invalid email or password'}, 401

        if hasattr(user, 'is_active') and not user.is_active:
            return {'message': 'Account disabled'}, 403
        
        # 创建访问令牌
        access_token = create_access_token(identity=str(user.id))
        
        return {
            'access_token': access_token,
            'user': user.to_dict()
        }, 200


class UserCodes(Resource):
    """获取用户发布的代码"""
    @jwt_required()
    def get(self):
        #############################
        # GET /api/user/codes
        #
        # 获取当前登录用户发布的代码列表。
        # - 性能：预加载 category/author/tags/results，避免序列化时 N+1
        #############################
        user_id = get_jwt_identity()
        codes = (
            Code.query.options(
                joinedload(Code.category),
                joinedload(Code.author),
                selectinload(Code.tags),
                selectinload(Code.results),
            )
            .filter_by(author_id=user_id)
            .order_by(Code.created_at.desc())
            .all()
        )
        return {'codes': [code.to_dict() for code in codes]}, 200


class UserFavorites(Resource):
    """获取用户收藏的代码"""
    @jwt_required()
    def get(self):
        #############################
        # GET /api/user/favorites
        #
        # 当前版本占位：返回空列表。
        # 注意：实际收藏功能已在 /api/favorites 中实现。
        #############################
        # 暂时返回空列表，后续可以实现收藏功能
        return {'favorites': []}, 200


class UserProfile(Resource):
    """用户资料管理"""
    @jwt_required()
    def get(self):
        #############################
        # GET /api/user/profile
        #
        # 获取当前用户资料。
        #############################
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        return user.to_dict(), 200
    
    @jwt_required()
    def put(self):
        #############################
        # PUT /api/user/profile
        #
        # 更新当前用户资料：支持更新 username/bio。
        # - 越权：只允许改自己的资料（由 JWT identity 保证）
        # - 唯一性：username 需要排除自己后检查冲突
        #############################
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str)
        parser.add_argument('bio', type=str)
        args = parser.parse_args()
        
        if args['username']:
            # 检查用户名是否被其他人使用
            existing = User.query.filter_by(username=args['username']).first()
            if existing and existing.id != user_id:
                return {'message': 'Username already exists'}, 400
            user.username = args['username']
        
        if args['bio'] is not None:
            user.bio = args['bio']
        
        try:
            db.session.commit()
            return {'message': 'Profile updated', 'user': user.to_dict()}, 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception('Failed to update profile')
            return {'message': 'Internal server error'}, 500


class UserPassword(Resource):
    """修改密码"""
    @jwt_required()
    def put(self):
        #############################
        # PUT /api/user/password
        #
        # 修改当前用户密码：先校验 old_password，再写入新密码哈希。
        #############################
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        
        parser = reqparse.RequestParser()
        parser.add_argument('old_password', type=str, required=True)
        parser.add_argument('new_password', type=str, required=True)
        args = parser.parse_args()
        
        if not user.check_password(args['old_password']):
            return {'message': '当前密码错误'}, 400
        
        user.set_password(args['new_password'])
        
        try:
            db.session.commit()
            return {'message': '密码修改成功'}, 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception('Failed to update password')
            return {'message': 'Internal server error'}, 500
