from datetime import datetime
from . import db

class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    code_id = db.Column(db.Integer, db.ForeignKey('codes.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 联合唯一约束，确保用户不能重复收藏同一代码
    __table_args__ = (db.UniqueConstraint('user_id', 'code_id', name='_user_code_uc'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'code_id': self.code_id,
            'created_at': self.created_at.isoformat()
        }
