'''
Author: Wangjien2 1569399536@qq.com
Date: 2025-12-01 23:12:23
LastEditors: Wangjien2 1569399536@qq.com
LastEditTime: 2025-12-01 23:36:53
FilePath: /代码分享平台/frontend/backend/resources/user.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import User
from models.code import Code
from models import db

class UserRegister(Resource):
    def post(self):
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
            return {'message': str(e)}, 500

class UserLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help='Email is required')
        parser.add_argument('password', type=str, required=True, help='Password is required')
        args = parser.parse_args()
        
        # 查找用户
        user = User.query.filter_by(email=args['email']).first()
        
        if not user or not user.check_password(args['password']):
            return {'message': 'Invalid email or password'}, 401
        
        # 创建访问令牌
        access_token = create_access_token(identity=user.id)
        
        return {
            'access_token': access_token,
            'user': user.to_dict()
        }, 200


class UserCodes(Resource):
    """获取用户发布的代码"""
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        codes = Code.query.filter_by(author_id=user_id).order_by(Code.created_at.desc()).all()
        return {'codes': [code.to_dict() for code in codes]}, 200


class UserFavorites(Resource):
    """获取用户收藏的代码"""
    @jwt_required()
    def get(self):
        # 暂时返回空列表，后续可以实现收藏功能
        return {'favorites': []}, 200


class UserProfile(Resource):
    """用户资料管理"""
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        return user.to_dict(), 200
    
    @jwt_required()
    def put(self):
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
            return {'message': str(e)}, 500


class UserPassword(Resource):
    """修改密码"""
    @jwt_required()
    def put(self):
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
            return {'message': str(e)}, 500
