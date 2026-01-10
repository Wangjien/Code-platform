from datetime import datetime

from flask import current_app, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, selectinload

from models import db
from models.code import Code
from models.comment import Comment
from models.user import User


def _require_admin() -> User:
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return None
    return user


class AdminUsers(Resource):
    method_decorators = [jwt_required()]

    def get(self):
        admin = _require_admin()
        if not admin:
            return {'message': 'Permission denied'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1, location='args')
        parser.add_argument('per_page', type=int, default=20, location='args')
        parser.add_argument('keyword', type=str, location='args')
        args = parser.parse_args()

        query = User.query
        if args['keyword']:
            pattern = f"%{args['keyword']}%"
            query = query.filter(or_(User.username.like(pattern), User.email.like(pattern)))

        pagination = query.order_by(User.created_at.desc()).paginate(
            page=args['page'], per_page=args['per_page'], error_out=False
        )

        return {
            'users': [u.to_dict() for u in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
        }, 200


class AdminUserDetail(Resource):
    method_decorators = [jwt_required()]

    def patch(self, user_id: int):
        admin = _require_admin()
        if not admin:
            return {'message': 'Permission denied'}, 403

        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404

        data = request.get_json() or {}
        role = data.get('role')
        is_active = data.get('is_active')

        if role is not None:
            if role not in {'user', 'admin'}:
                return {'message': 'Invalid role'}, 400
            user.role = role

        if is_active is not None:
            user.is_active = bool(is_active)

        try:
            db.session.commit()
            return {'message': 'Updated', 'user': user.to_dict()}, 200
        except Exception:
            db.session.rollback()
            current_app.logger.exception('Failed to update user')
            return {'message': 'Internal server error'}, 500


class AdminCodes(Resource):
    method_decorators = [jwt_required()]

    def get(self):
        admin = _require_admin()
        if not admin:
            return {'message': 'Permission denied'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1, location='args')
        parser.add_argument('per_page', type=int, default=20, location='args')
        parser.add_argument('keyword', type=str, location='args')
        parser.add_argument('status', type=str, location='args')
        args = parser.parse_args()

        query = Code.query.options(
            joinedload(Code.category),
            joinedload(Code.author),
            selectinload(Code.tags),
            selectinload(Code.results),
        )

        if args['keyword']:
            pattern = f"%{args['keyword']}%"
            query = query.filter(or_(Code.title.like(pattern), Code.description.like(pattern)))

        if args['status']:
            query = query.filter(Code.status == args['status'])

        pagination = query.order_by(Code.created_at.desc()).paginate(
            page=args['page'], per_page=args['per_page'], error_out=False
        )

        return {
            'codes': [c.to_dict() for c in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
        }, 200


class AdminCodeReview(Resource):
    method_decorators = [jwt_required()]

    def patch(self, code_id: int):
        admin = _require_admin()
        if not admin:
            return {'message': 'Permission denied'}, 403

        code = Code.query.get(code_id)
        if not code:
            return {'message': 'Code not found'}, 404

        data = request.get_json() or {}
        action = data.get('action')
        reason = data.get('reason')

        if action not in {'approve', 'reject', 'disable'}:
            return {'message': 'Invalid action'}, 400

        if action == 'approve':
            code.status = 'approved'
            code.review_reason = None
        elif action == 'reject':
            code.status = 'rejected'
            code.review_reason = reason or ''
        elif action == 'disable':
            code.status = 'disabled'
            code.review_reason = reason or ''

        code.reviewed_by = admin.id
        code.reviewed_at = datetime.utcnow()

        try:
            db.session.commit()
            return {'message': 'Updated', 'code': code.to_dict()}, 200
        except Exception:
            db.session.rollback()
            current_app.logger.exception('Failed to review code')
            return {'message': 'Internal server error'}, 500


class AdminComments(Resource):
    method_decorators = [jwt_required()]

    def get(self):
        admin = _require_admin()
        if not admin:
            return {'message': 'Permission denied'}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1, location='args')
        parser.add_argument('per_page', type=int, default=20, location='args')
        parser.add_argument('keyword', type=str, location='args')
        args = parser.parse_args()

        query = Comment.query
        if args['keyword']:
            pattern = f"%{args['keyword']}%"
            query = query.filter(Comment.content.like(pattern))

        pagination = query.order_by(Comment.created_at.desc()).paginate(
            page=args['page'], per_page=args['per_page'], error_out=False
        )

        return {
            'comments': [c.to_dict() for c in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
        }, 200


class AdminCommentDetail(Resource):
    method_decorators = [jwt_required()]

    def delete(self, comment_id: int):
        admin = _require_admin()
        if not admin:
            return {'message': 'Permission denied'}, 403

        comment = Comment.query.get(comment_id)
        if not comment:
            return {'message': 'Comment not found'}, 404

        try:
            db.session.delete(comment)
            db.session.commit()
            return {'message': 'Deleted'}, 200
        except Exception:
            db.session.rollback()
            current_app.logger.exception('Failed to delete comment')
            return {'message': 'Internal server error'}, 500
