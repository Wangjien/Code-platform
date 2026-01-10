from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from flask import current_app
from models.tag import Tag
from models import db

#############################
# Tag API
#
# 该文件提供“标签”相关接口：
# - 标签列表 / 标签详情
# - 创建 / 更新 / 删除标签
#
# 注意：
# - 当前仅做 JWT 校验，并未区分管理员/普通用户
# - 异常仅记录日志，不向客户端泄露内部错误信息
#############################

class TagList(Resource):
    #############################
    # GET /api/tags
    #
    # 获取标签列表。
    #############################
    def get(self):
        # 获取标签列表
        tags = Tag.query.all()
        return [tag.to_dict() for tag in tags], 200
    
    @jwt_required()
    def post(self):
        #############################
        # POST /api/tags
        #
        # 创建标签。
        #############################
        # 创建新标签
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Name is required')
        parser.add_argument('description', type=str, help='Description')
        args = parser.parse_args()
        
        # 检查标签是否已存在
        if Tag.query.filter_by(name=args['name']).first():
            return {'message': 'Tag already exists'}, 400
        
        tag = Tag(name=args['name'], description=args['description'])
        
        try:
            db.session.add(tag)
            db.session.commit()
            return tag.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception('Failed to create tag')
            return {'message': 'Internal server error'}, 500

class TagDetail(Resource):
    #############################
    # GET /api/tags/<tag_id>
    #
    # 获取标签详情。
    #############################
    def get(self, tag_id):
        # 获取标签详情
        tag = Tag.query.get(tag_id)
        if not tag:
            return {'message': 'Tag not found'}, 404
        return tag.to_dict(), 200
    
    @jwt_required()
    def put(self, tag_id):
        #############################
        # PUT /api/tags/<tag_id>
        #
        # 更新标签。
        #############################
        # 更新标签
        tag = Tag.query.get(tag_id)
        if not tag:
            return {'message': 'Tag not found'}, 404
        
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, help='Name')
        parser.add_argument('description', type=str, help='Description')
        args = parser.parse_args()
        
        if args['name']:
            tag.name = args['name']
        if args['description']:
            tag.description = args['description']
        
        try:
            db.session.commit()
            return tag.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception('Failed to update tag')
            return {'message': 'Internal server error'}, 500
    
    @jwt_required()
    def delete(self, tag_id):
        #############################
        # DELETE /api/tags/<tag_id>
        #
        # 删除标签。
        #############################
        # 删除标签
        tag = Tag.query.get(tag_id)
        if not tag:
            return {'message': 'Tag not found'}, 404
        
        try:
            db.session.delete(tag)
            db.session.commit()
            return {'message': 'Tag deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception('Failed to delete tag')
            return {'message': 'Internal server error'}, 500
