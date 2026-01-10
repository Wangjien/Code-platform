from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app
from models.user_category import UserCategory
from models import db

#############################
# UserCategory API
#
# 该文件提供"用户自定义分类"相关接口：
# - 获取用户分类列表
# - 创建、更新、删除用户分类
# - 分类排序
#
# 关键点：
# - 权限：所有接口均要求 JWT 认证
# - 安全：用户只能管理自己的分类
# - 业务：删除分类前检查是否有代码引用
#############################

class UserCategoryList(Resource):
    @jwt_required()
    def get(self):
        """获取当前用户的分类列表"""
        user_id = get_jwt_identity()
        categories = UserCategory.query.filter_by(user_id=user_id).order_by(UserCategory.sort_order.asc()).all()
        return [category.to_dict() for category in categories], 200
    
    @jwt_required()
    def post(self):
        """创建新的用户分类"""
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='分类名称必填')
        parser.add_argument('description', type=str, help='分类描述')
        parser.add_argument('color', type=str, help='分类颜色')
        args = parser.parse_args()
        
        user_id = get_jwt_identity()
        
        # 检查同名分类是否存在
        existing = UserCategory.query.filter_by(user_id=user_id, name=args['name']).first()
        if existing:
            return {'message': '该分类名称已存在'}, 400
        
        # 获取当前最大排序值
        max_sort = db.session.query(db.func.max(UserCategory.sort_order)).filter_by(user_id=user_id).scalar() or 0
        
        category = UserCategory(
            name=args['name'],
            description=args.get('description', ''),
            color=args.get('color', '#409EFF'),
            sort_order=max_sort + 1,
            user_id=user_id
        )
        
        try:
            db.session.add(category)
            db.session.commit()
            return category.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception('Failed to create user category')
            return {'message': '创建分类失败'}, 500

class UserCategoryDetail(Resource):
    @jwt_required()
    def get(self, category_id):
        """获取分类详情"""
        user_id = get_jwt_identity()
        category = UserCategory.query.filter_by(id=category_id, user_id=user_id).first()
        if not category:
            return {'message': '分类不存在'}, 404
        return category.to_dict(), 200
    
    @jwt_required()
    def put(self, category_id):
        """更新分类信息"""
        user_id = get_jwt_identity()
        category = UserCategory.query.filter_by(id=category_id, user_id=user_id).first()
        if not category:
            return {'message': '分类不存在'}, 404
        
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, help='分类名称')
        parser.add_argument('description', type=str, help='分类描述')
        parser.add_argument('color', type=str, help='分类颜色')
        args = parser.parse_args()
        
        # 检查名称冲突（排除自己）
        if args.get('name') and args['name'] != category.name:
            existing = UserCategory.query.filter_by(user_id=user_id, name=args['name']).first()
            if existing:
                return {'message': '该分类名称已存在'}, 400
        
        # 更新字段
        if args.get('name'):
            category.name = args['name']
        if args.get('description') is not None:
            category.description = args['description']
        if args.get('color'):
            category.color = args['color']
        
        try:
            db.session.commit()
            return category.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception('Failed to update user category')
            return {'message': '更新分类失败'}, 500
    
    @jwt_required()
    def delete(self, category_id):
        """删除分类"""
        user_id = get_jwt_identity()
        category = UserCategory.query.filter_by(id=category_id, user_id=user_id).first()
        if not category:
            return {'message': '分类不存在'}, 404
        
        # 检查是否有代码引用此分类
        if category.codes:
            return {'message': f'无法删除，该分类下还有 {len(category.codes)} 个代码'}, 400
        
        try:
            db.session.delete(category)
            db.session.commit()
            return {'message': '分类删除成功'}, 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception('Failed to delete user category')
            return {'message': '删除分类失败'}, 500

class UserCategorySortOrder(Resource):
    @jwt_required()
    def post(self):
        """批量更新分类排序"""
        parser = reqparse.RequestParser()
        parser.add_argument('category_orders', type=list, required=True, help='分类排序列表必填')
        args = parser.parse_args()
        
        user_id = get_jwt_identity()
        
        try:
            # 批量更新排序
            for index, category_id in enumerate(args['category_orders']):
                category = UserCategory.query.filter_by(id=category_id, user_id=user_id).first()
                if category:
                    category.sort_order = index + 1
            
            db.session.commit()
            return {'message': '排序更新成功'}, 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception('Failed to update category sort order')
            return {'message': '排序更新失败'}, 500
