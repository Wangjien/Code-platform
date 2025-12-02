from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.favorite import Favorite
from models.code import Code
from models import db

class FavoriteList(Resource):
    @jwt_required()
    def get(self):
        # 获取当前用户的所有收藏
        current_user_id = get_jwt_identity()
        favorites = Favorite.query.filter_by(user_id=current_user_id).all()
        
        # 构建包含代码详情的收藏列表
        favorite_codes = []
        for favorite in favorites:
            code = Code.query.get(favorite.code_id)
            if code:
                favorite_codes.append({
                    'favorite_id': favorite.id,
                    'code': code.to_dict()
                })
        
        return favorite_codes, 200
    
    @jwt_required()
    def post(self):
        # 收藏代码
        parser = reqparse.RequestParser()
        parser.add_argument('code_id', type=int, required=True, help='Code ID is required')
        args = parser.parse_args()
        
        current_user_id = get_jwt_identity()
        
        # 检查代码是否存在
        code = Code.query.get(args['code_id'])
        if not code:
            return {'message': 'Code not found'}, 404
        
        # 检查是否已经收藏
        if Favorite.query.filter_by(user_id=current_user_id, code_id=args['code_id']).first():
            return {'message': 'Code already favorited'}, 400
        
        favorite = Favorite(
            user_id=current_user_id,
            code_id=args['code_id']
        )
        
        try:
            db.session.add(favorite)
            db.session.commit()
            return favorite.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

class FavoriteDetail(Resource):
    @jwt_required()
    def delete(self, favorite_id):
        # 取消收藏
        favorite = Favorite.query.get(favorite_id)
        if not favorite:
            return {'message': 'Favorite not found'}, 404
        
        # 检查权限
        current_user_id = get_jwt_identity()
        if favorite.user_id != current_user_id:
            return {'message': 'Permission denied'}, 403
        
        try:
            db.session.delete(favorite)
            db.session.commit()
            return {'message': 'Favorite deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500
