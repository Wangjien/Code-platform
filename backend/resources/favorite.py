from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app
from sqlalchemy.orm import joinedload, selectinload
from models.favorite import Favorite
from models.code import Code
from models import db

#############################
# Favorite API
#
# 该文件提供“收藏”相关接口：
# - 获取当前用户收藏列表
# - 收藏代码
# - 取消收藏
#
# 关键点：
# - 权限：所有接口均要求 JWT（@jwt_required）
# - 性能：收藏列表接口避免 N+1（一次性查询所有 code 并预加载关系）
# - 安全：异常不向客户端泄露内部错误细节，仅记录日志
#############################

class FavoriteList(Resource):
    #############################
    # GET /api/favorites
    #
    # 返回当前用户的收藏列表（包含对应代码详情）。
    #
    # 性能说明：
    # - 先查 favorites 拿到 code_id 集合
    # - 再用 IN(...) 一次性拉取 codes，并预加载 to_dict 依赖的关系
    #############################
    @jwt_required()
    def get(self):
        # 获取当前用户的所有收藏
        current_user_id = get_jwt_identity()
        favorites = Favorite.query.filter_by(user_id=current_user_id).all()

        # 将 favorites 映射到 code_ids，避免后续循环逐个查 Code（N+1）
        code_ids = [f.code_id for f in favorites]
        codes_by_id = {}
        if code_ids:
            # 预加载关联，避免 Code.to_dict() 中访问关系时触发额外查询
            codes = (
                Code.query.options(
                    joinedload(Code.category),
                    joinedload(Code.author),
                    selectinload(Code.tags),
                    selectinload(Code.results),
                )
                .filter(Code.id.in_(code_ids))
                .all()
            )
            codes_by_id = {c.id: c for c in codes}

        # 仅返回仍然存在的 code（如果历史数据中 code 被删除，则自动跳过）
        return [
            {
                'favorite_id': f.id,
                'code': codes_by_id[f.code_id].to_dict(),
            }
            for f in favorites
            if f.code_id in codes_by_id
        ], 200
    
    @jwt_required()
    def post(self):
        #############################
        # POST /api/favorites
        #
        # 收藏指定代码。
        # - 入参：code_id
        # - 约束：同一用户不可重复收藏同一代码（业务层 + DB 唯一约束双保险）
        #############################
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
            # 记录异常（例如唯一约束冲突、数据库连接问题），但不向客户端暴露细节
            current_app.logger.exception('Failed to create favorite')
            return {'message': 'Internal server error'}, 500

class FavoriteDetail(Resource):
    @jwt_required()
    def delete(self, favorite_id):
        #############################
        # DELETE /api/favorites/<favorite_id>
        #
        # 取消收藏。
        # - 权限：只能删除自己的收藏记录
        #############################
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
            # 记录异常但不回传内部错误信息
            current_app.logger.exception('Failed to delete favorite')
            return {'message': 'Internal server error'}, 500
