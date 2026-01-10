from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from flask import current_app
from models.category import Category
from models import db

#############################
# Category API
#
# 该文件提供“分类”相关接口：
# - 分类列表 / 分类详情
# - 创建 / 更新 / 删除分类（当前只做了 JWT 校验）
#
# 注意：
# - 代码里写了“仅管理员”，但目前未实现 role 校验（如需可在此处补充权限判断）
# - 异常仅记录日志，不向客户端泄露内部错误信息
#############################

class CategoryList(Resource):
    #############################
    # GET /api/categories
    #
    # 获取分类列表。
    #############################
    def get(self):
        # 获取分类列表
        categories = Category.query.all()
        return [category.to_dict() for category in categories], 200
    
    @jwt_required()
    def post(self):
        #############################
        # POST /api/categories
        #
        # 创建分类（代码注释标注“仅管理员”，目前仅做 JWT 校验）。
        #############################
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
            current_app.logger.exception('Failed to create category')
            return {'message': 'Internal server error'}, 500

class CategoryDetail(Resource):
    #############################
    # GET /api/categories/<category_id>
    #
    # 获取分类详情。
    #############################
    def get(self, category_id):
        # 获取分类详情
        category = Category.query.get(category_id)
        if not category:
            return {'message': 'Category not found'}, 404
        return category.to_dict(), 200
    
    @jwt_required()
    def put(self, category_id):
        #############################
        # PUT /api/categories/<category_id>
        #
        # 更新分类（代码注释标注“仅管理员”，目前仅做 JWT 校验）。
        #############################
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
            current_app.logger.exception('Failed to update category')
            return {'message': 'Internal server error'}, 500
    
    @jwt_required()
    def delete(self, category_id):
        #############################
        # DELETE /api/categories/<category_id>
        #
        # 删除分类（代码注释标注“仅管理员”，目前仅做 JWT 校验）。
        #############################
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
            current_app.logger.exception('Failed to delete category')
            return {'message': 'Internal server error'}, 500
