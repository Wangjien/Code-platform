from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.tag import Tag
from models import db

class TagList(Resource):
    def get(self):
        # 获取标签列表
        tags = Tag.query.all()
        return [tag.to_dict() for tag in tags], 200
    
    @jwt_required()
    def post(self):
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
            return {'message': str(e)}, 500

class TagDetail(Resource):
    def get(self, tag_id):
        # 获取标签详情
        tag = Tag.query.get(tag_id)
        if not tag:
            return {'message': 'Tag not found'}, 404
        return tag.to_dict(), 200
    
    @jwt_required()
    def put(self, tag_id):
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
            return {'message': str(e)}, 500
    
    @jwt_required()
    def delete(self, tag_id):
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
            return {'message': str(e)}, 500
