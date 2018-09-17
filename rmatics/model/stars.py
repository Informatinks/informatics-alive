import datetime

from rmatics.model import db


class Stars(db.Model):
    __table_args__ = {'schema': 'moodle'}
    __tablename__ = 'mdl_stars'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_user.id'))
    title = db.Column(db.Text)
    link = db.Column(db.Text)

    def __init__(self, user, title, link):
        self.link = link
        self.title = title
        self.user_id = user.id

    def __json__(self, request):
        return {
            'id' :  self.id,
            'user_id' : self.user_id,
            'title' : self.title,
            'link' : self.link,
        }
