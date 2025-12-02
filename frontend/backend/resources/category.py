from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.category import Category
from models import db

class CategoryList(Resource):
    def get(self):
        # 获取分类列表
        categories = Category.query.all()
        return [category.to_dict() for category in categories], 200
    
    @jwt_required()
    def post(self):
        # 创建新分类（仅管理员）
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Name is required')
        parser.add_argument('description', type=str, help='Description')
        args = parser.parse_args()
        
        # 检查分类是否已存在
        if Category.query.filter_by(name=args['name']).first():
            return {'message': 'Category already exists'}, 400
        
        category = Category(name=args['name'], description=args['description'])
        
        try:
            db.session.add(category)
            db.session.commit()
            return category.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

class CategoryDetail(Resource):
    def get(self, category_id):
        # 获取分类详情
        category = Category.query.get(category_id)
        if not category:
            return {'message': 'Category not found'}, 404
        return category.to_dict(), 200
    
    @jwt_required()
    def put(self, category_id):
        # 更新分类（仅管理员）
        category = Category.query.get(category_id)
        if not category:
            return {'message': 'Category not found'}, 404
        
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, help='Name')
        parser.add_argument('description', type=str, help='Description')
        args = parser.parse_args()
        
        if args['name']:
            category.name = args['name']
        if args['description']:
            category.description = args['description']
        
        try:
            db.session.commit()
            return category.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500
    
    @jwt_required()
    def delete(self, category_id):
        # 删除分类（仅管理员）
        category = Category.query.get(category_id)
        if not category:
            return {'message': 'Category not found'}, 404
        
        try:
            db.session.delete(category)
            db.session.commit()
            return {'message': 'Category deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500
