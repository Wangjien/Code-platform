from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models.code import Code
from models.result import Result
from models.tag import Tag
from models import db

class CodeList(Resource):
    def get(self):
        # 获取代码列表，支持筛选和分页
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1, location='args', help='Page number')
        parser.add_argument('per_page', type=int, default=10, location='args', help='Items per page')
        parser.add_argument('keyword', type=str, location='args', help='Search keyword')
        parser.add_argument('language', type=str, location='args', help='Programming language')
        parser.add_argument('category_id', type=int, location='args', help='Category ID')
        parser.add_argument('tag', type=str, location='args', help='Tag name')
        args = parser.parse_args()
        
        # 构建查询
        query = Code.query
        
        if args['keyword']:
            query = query.filter(Code.title.like(f"%{args['keyword']}%") | Code.description.like(f"%{args['keyword']}%"))
        
        if args['language']:
            query = query.filter_by(language=args['language'])
        
        if args['category_id']:
            query = query.filter_by(category_id=args['category_id'])
        
        if args['tag']:
            query = query.join(Code.tags).filter(Tag.name == args['tag'])
        
        # 分页
        pagination = query.order_by(Code.created_at.desc()).paginate(page=args['page'], per_page=args['per_page'], error_out=False)
        
        return {
            'codes': [code.to_dict() for code in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        }, 200
    
    @jwt_required()
    def post(self):
        # 创建新代码 - 直接从 JSON 获取数据
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['title', 'description', 'content', 'language', 'category_id']
        for field in required_fields:
            if not data.get(field):
                return {'message': f'{field} is required'}, 400
        
        # 获取当前用户ID
        current_user_id = get_jwt_identity()
        
        # 创建代码
        code = Code(
            title=data['title'],
            description=data['description'],
            content=data['content'],
            language=data['language'],
            category_id=data['category_id'],
            author_id=current_user_id,
            environment=data.get('environment', ''),
            license=data.get('license', 'MIT')
        )
        
        # 添加标签
        tags = data.get('tags', [])
        for tag_name in tags:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            code.tags.append(tag)
        
        # 添加结果
        results = data.get('results', [])
        for result_data in results:
            result = Result(
                code=code,
                type=result_data.get('type', 'text'),
                content=result_data.get('content', ''),
                description=result_data.get('description', '')
            )
            db.session.add(result)
        
        try:
            db.session.add(code)
            db.session.commit()
            return code.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

class CodeDetail(Resource):
    def get(self, code_id):
        # 获取代码详情
        code = Code.query.get(code_id)
        if not code:
            return {'message': 'Code not found'}, 404
        
        # 增加浏览量
        code.views += 1
        db.session.commit()
        
        return code.to_dict(), 200
    
    @jwt_required()
    def put(self, code_id):
        # 更新代码
        code = Code.query.get(code_id)
        if not code:
            return {'message': 'Code not found'}, 404
        
        # 检查权限
        current_user_id = get_jwt_identity()
        if code.author_id != current_user_id:
            return {'message': 'Permission denied'}, 403
        
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, help='Title')
        parser.add_argument('description', type=str, help='Description')
        parser.add_argument('content', type=str, help='Content')
        parser.add_argument('language', type=str, help='Language')
        parser.add_argument('category_id', type=int, help='Category ID')
        parser.add_argument('environment', type=str, help='Environment configuration')
        parser.add_argument('license', type=str, help='License')
        parser.add_argument('tags', type=list, help='Tags list')
        args = parser.parse_args()
        
        # 更新字段
        if args['title']:
            code.title = args['title']
        if args['description']:
            code.description = args['description']
        if args['content']:
            code.content = args['content']
        if args['language']:
            code.language = args['language']
        if args['category_id']:
            code.category_id = args['category_id']
        if args['environment']:
            code.environment = args['environment']
        if args['license']:
            code.license = args['license']
        
        # 更新标签
        if args['tags']:
            code.tags.clear()
            for tag_name in args['tags']:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                code.tags.append(tag)
        
        try:
            db.session.commit()
            return code.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500
    
    @jwt_required()
    def delete(self, code_id):
        # 删除代码
        code = Code.query.get(code_id)
        if not code:
            return {'message': 'Code not found'}, 404
        
        # 检查权限
        current_user_id = get_jwt_identity()
        if code.author_id != current_user_id:
            return {'message': 'Permission denied'}, 403
        
        try:
            db.session.delete(code)
            db.session.commit()
            return {'message': 'Code deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500
