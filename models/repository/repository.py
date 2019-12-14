from mongoengine import Document, StringField, DateTimeField, IntField
from datetime import datetime


class Repository(Document):
    clone_timestamp = DateTimeField(default=datetime.now)
    clone_duration = IntField()
    remote_url = StringField()
    name = StringField()
    path = StringField()
