from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app
from models.comment import Comment
from models import db

#############################
# Comment API
#
# 该文件提供“评论”相关接口：
# - 获取某个 code 的评论列表
# - 创建评论（需要登录）
# - 更新/删除评论（仅作者可操作）
#
# 关键点：
# - 权限：写接口均要求 JWT
# - 越权防护：更新/删除时校验 comment.author_id
# - 安全：异常仅记录日志，不回传内部错误信息
#############################

class CommentList(Resource):
    #############################
    # GET /api/codes/<code_id>/comments
    #
    # 获取指定 code 的评论列表（按时间倒序）。
    #############################
    def get(self, code_id):
        # 获取代码的所有评论
        comments = Comment.query.filter_by(code_id=code_id).order_by(Comment.created_at.desc()).all()
        return [comment.to_dict() for comment in comments], 200
    
    @jwt_required()
    def post(self, code_id):
        #############################
        # POST /api/codes/<code_id>/comments
        #
        # 创建评论：author_id 取自 JWT。
        #############################
        # 创建新评论
        parser = reqparse.RequestParser()
        parser.add_argument('content', type=str, required=True, help='Content is required')
        args = parser.parse_args()
        
        current_user_id = get_jwt_identity()
        
        comment = Comment(
            content=args['content'],
            author_id=current_user_id,
            code_id=code_id
        )
        
        try:
            db.session.add(comment)
            db.session.commit()
            return comment.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            # 记录异常但不回传细节
            current_app.logger.exception('Failed to create comment')
            return {'message': 'Internal server error'}, 500

class CommentDetail(Resource):
    @jwt_required()
    def put(self, comment_id):
        #############################
        # PUT /api/comments/<comment_id>
        #
        # 更新评论：仅作者可更新。
        #############################
        # 更新评论
        comment = Comment.query.get(comment_id)
        if not comment:
            return {'message': 'Comment not found'}, 404
        
        # 检查权限
        current_user_id = get_jwt_identity()
        if comment.author_id != current_user_id:
            return {'message': 'Permission denied'}, 403
        
        parser = reqparse.RequestParser()
        parser.add_argument('content', type=str, required=True, help='Content is required')
        args = parser.parse_args()
        
        comment.content = args['content']
        
        try:
            db.session.commit()
            return comment.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            # 记录异常但不回传细节
            current_app.logger.exception('Failed to update comment')
            return {'message': 'Internal server error'}, 500
    
    @jwt_required()
    def delete(self, comment_id):
        #############################
        # DELETE /api/comments/<comment_id>
        #
        # 删除评论：仅作者可删除。
        #############################
        # 删除评论
        comment = Comment.query.get(comment_id)
        if not comment:
            return {'message': 'Comment not found'}, 404
        
        # 检查权限
        current_user_id = get_jwt_identity()
        if comment.author_id != current_user_id:
            return {'message': 'Permission denied'}, 403
        
        try:
            db.session.delete(comment)
            db.session.commit()
            return {'message': 'Comment deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            # 记录异常但不回传细节
            current_app.logger.exception('Failed to delete comment')
            return {'message': 'Internal server error'}, 500
