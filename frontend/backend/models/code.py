from datetime import datetime
from . import db

class Code(db.Model):
    __tablename__ = 'codes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)  # 代码内容，Base64编码或直接存储
    language = db.Column(db.String(20), nullable=False)  # Python, R, Shell
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    environment = db.Column(db.Text, nullable=True)  # 环境配置，如Dockerfile或conda环境
    license = db.Column(db.String(50), default='MIT')  # 开源协议
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    downloads = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    results = db.relationship('Result', backref='code', lazy=True, cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary='code_tags', backref=db.backref('codes', lazy='dynamic'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'language': self.language,
            'category_id': self.category_id,
            'category': self.category.to_dict() if self.category else {'name': '未分类'},
            'author_id': self.author_id,
            'author_username': self.author.username if self.author else '未知用户',
            'environment': self.environment,
            'license': self.license,
            'views': self.views,
            'likes': self.likes,
            'downloads': self.downloads,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'tags': [tag.name for tag in self.tags],
            'results': [result.to_dict() for result in self.results]
        }
