from . import db

class CodeTag(db.Model):
    __tablename__ = 'code_tags'
    
    code_id = db.Column(db.Integer, db.ForeignKey('codes.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)
