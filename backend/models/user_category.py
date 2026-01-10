from datetime import datetime
from . import db

class UserCategory(db.Model):
    __tablename__ = 'user_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # 分类名称
    description = db.Column(db.String(200), nullable=True)  # 分类描述
    color = db.Column(db.String(20), default='#409EFF')  # 分类颜色标识
    sort_order = db.Column(db.Integer, default=0)  # 排序顺序
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 所属用户
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    codes = db.relationship('Code', backref='user_category', lazy=True)
    
    # 唯一约束：同一用户下的分类名称不能重复
    __table_args__ = (
        db.UniqueConstraint('user_id', 'name', name='uq_user_category_name'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'sort_order': self.sort_order,
            'user_id': self.user_id,
            'code_count': len(self.codes) if self.codes else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
