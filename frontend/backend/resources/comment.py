from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.comment import Comment
from models import db

class CommentList(Resource):
    def get(self, code_id):
        # 获取代码的所有评论
        comments = Comment.query.filter_by(code_id=code_id).order_by(Comment.created_at.desc()).all()
        return [comment.to_dict() for comment in comments], 200
    
    @jwt_required()
    def post(self, code_id):
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
            return {'message': str(e)}, 500

class CommentDetail(Resource):
    @jwt_required()
    def put(self, comment_id):
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
            return {'message': str(e)}, 500
    
    @jwt_required()
    def delete(self, comment_id):
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
            return {'message': str(e)}, 500
