from datetime import datetime
from . import db

class Result(db.Model):
    __tablename__ = 'results'
    
    id = db.Column(db.Integer, primary_key=True)
    code_id = db.Column(db.Integer, db.ForeignKey('codes.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # image, text, chart, table
    content = db.Column(db.Text, nullable=False)  # 结果内容，图片URL、文本或图表数据
    description = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'code_id': self.code_id,
            'type': self.type,
            'content': self.content,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }
