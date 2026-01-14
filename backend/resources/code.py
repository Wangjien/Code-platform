from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from flask import request, current_app
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, selectinload
from models.code import Code
from models.result import Result
from models.tag import Tag
from models.user import User
from models import db
from utils.cache import cached_response, CACHE_TTL, invalidate_cache

#############################
# Code API
#
# 该文件提供“代码分享”相关接口：
# - 代码列表：分页、筛选、搜索
# - 代码创建：绑定作者、写入标签与结果
# - 代码详情：读取并自增浏览量
# - 代码更新/删除：仅作者可操作
#
# 关键点：
# - 性能：列表/详情使用 joinedload/selectinload 预加载关系，避免 to_dict() 触发 N+1
# - 安全：写接口要求 JWT；更新/删除校验 author_id 防止越权；异常仅记录日志不回传细节
#############################

class CodeList(Resource):
    #############################
    # GET /api/codes
    #
    # 代码列表接口：支持分页与筛选。
    # - page/per_page：分页参数
    # - keyword：标题/描述模糊搜索
    # - language/category_id/tag：筛选条件
    #
    # 性能说明：
    # - 使用预加载，避免序列化时产生大量额外 SQL
    #############################
    @cached_response(ttl=CACHE_TTL['MEDIUM'], key_prefix="code_list")
    def get(self):
        # 获取代码列表，支持筛选和分页
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1, location='args', help='Page number')
        parser.add_argument('per_page', type=int, default=10, location='args', help='Items per page')
        parser.add_argument('keyword', type=str, location='args', help='Search keyword')
        parser.add_argument('language', type=str, location='args', help='Programming language')
        parser.add_argument('category_id', type=int, location='args', help='Category ID')
        parser.add_argument('user_category_id', type=int, location='args', help='User Category ID')
        parser.add_argument('tag', type=str, location='args', help='Tag name')
        args = parser.parse_args()

        user_id = None
        is_admin = False
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
        except Exception:
            user_id = None

        if user_id is not None:
            user = User.query.get(user_id)
            is_admin = bool(user and user.role == 'admin')
        
        # 构建查询
        # 预加载关联：category/author 使用 joinedload；tags/results 使用 selectinload
        query = Code.query.options(
            joinedload(Code.category),
            joinedload(Code.author),
            selectinload(Code.tags),
            selectinload(Code.results),
        )

        if not is_admin:
            if user_id is None:
                query = query.filter(or_(Code.status == 'approved', Code.status.is_(None)))
            else:
                query = query.filter(
                    or_(
                        Code.author_id == user_id,
                        Code.status == 'approved',
                        Code.status.is_(None),
                    )
                )
        
        if args['keyword']:
            # 优化搜索：使用多种搜索策略
            keyword = args['keyword'].strip()
            if len(keyword) >= 2:  # 避免过短关键词
                # 1. 精确匹配优先级最高
                exact_condition = or_(
                    Code.title == keyword,
                    Code.description.contains(keyword)
                )
                
                # 2. 前缀匹配
                prefix_condition = or_(
                    Code.title.like(f"{keyword}%"),
                    Code.description.like(f"{keyword}%")
                )
                
                # 3. 包含匹配（原LIKE逻辑）
                contains_condition = or_(
                    Code.title.like(f"%{keyword}%"),
                    Code.description.like(f"%{keyword}%")
                )
                
                # 组合查询条件，按优先级排序
                query = query.filter(or_(exact_condition, prefix_condition, contains_condition))
            else:
                # 短关键词只做精确匹配
                query = query.filter(
                    or_(
                        Code.title.contains(keyword),
                        Code.description.contains(keyword)
                    )
                )
        
        if args['language']:
            query = query.filter_by(language=args['language'])
        
        if args['category_id']:
            query = query.filter_by(category_id=args['category_id'])
        
        if args['user_category_id']:
            query = query.filter_by(user_category_id=args['user_category_id'])
        
        if args['tag']:
            # tag 筛选需要 join 多对多关系
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
        #############################
        # POST /api/codes
        #
        # 创建代码：绑定当前登录用户为 author，并写入 tags/results。
        # - 权限：JWT 必须
        # - 入参：JSON（title/description/content/language/category_id 等）
        #
        # 注意：
        # - tags/results 是在同一事务中写入
        # - 异常时回滚事务并记录日志
        #############################
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
            user_category_id=data.get('user_category_id'),  # 用户自定义分类（可选）
            author_id=current_user_id,
            environment=data.get('environment', ''),
            license=data.get('license', 'MIT'),
            status='pending',
        )
        
        # 添加标签
        tags = data.get('tags', [])
        for tag_name in tags:
            # 标签不存在则创建（后续可考虑：统一小写/去空格/限制长度）
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            code.tags.append(tag)
        
        # 添加结果
        results = data.get('results', [])
        for result_data in results:
            # 结果与 code 一并写入；Result.code 通过 relationship 关联
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
            current_app.logger.exception('Failed to create code')
            return {'message': 'Internal server error'}, 500

class CodeDetail(Resource):
    #############################
    # GET /api/codes/<code_id>
    #
    # 获取代码详情，并在同一请求中自增浏览量。
    # 性能：预加载序列化所需关系
    # 注意：高并发下 views 自增可能产生写竞争（后续可改为原子更新或异步计数）
    #############################
    def get(self, code_id):
        # 获取代码详情
        code = Code.query.options(
            joinedload(Code.category),
            joinedload(Code.author),
            selectinload(Code.tags),
            selectinload(Code.results),
        ).get(code_id)
        if not code:
            return {'message': 'Code not found'}, 404

        user_id = None
        is_admin = False
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
        except Exception:
            user_id = None

        if user_id is not None:
            user = User.query.get(user_id)
            is_admin = bool(user and user.role == 'admin')

        if not is_admin:
            is_approved = (code.status == 'approved') or (code.status is None)
            if not is_approved:
                if user_id is None or code.author_id != user_id:
                    return {'message': 'Code not found'}, 404
        
        # 增加浏览量
        code.views += 1
        db.session.commit()
        
        return code.to_dict(), 200
    
    @jwt_required()
    def put(self, code_id):
        #############################
        # PUT /api/codes/<code_id>
        #
        # 更新代码：仅作者可更新。
        # - 权限：JWT 必须
        # - 越权防护：author_id 必须等于当前用户
        #############################
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
            current_app.logger.exception('Failed to update code')
            return {'message': 'Internal server error'}, 500
    
    @jwt_required()
    def delete(self, code_id):
        #############################
        # DELETE /api/codes/<code_id>
        #
        # 删除代码：仅作者可删除。
        #############################
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
            current_app.logger.exception('Failed to delete code')
            return {'message': 'Internal server error'}, 500
