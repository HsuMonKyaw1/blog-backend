from datetime import datetime
from flask import Flask
from pymongo import MongoClient
from mongoengine import BooleanField,PULL,Document,ListField,StringField, EmailField, ReferenceField, DateTimeField,IntField,EmbeddedDocument,EmbeddedDocumentField

app = Flask(__name__)

# User model
class ProfileInfo(EmbeddedDocument):
    profile_picture = StringField()
    cover_photo=StringField()
    bio = StringField()
    name = StringField()


class User(Document):
    username = StringField(required=True, unique=True, max_length=50)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    profile_info = EmbeddedDocumentField(ProfileInfo)
    followers = ListField(ReferenceField('self'))
    followings = ListField(ReferenceField('self'))
    followerCount = IntField(default = 0)
    interests = ListField(IntField())
    bookmarks = ListField(StringField())
    def __str__(self):
        return self.username
    def get_profile_picture(self):
        return self.profile_info.profile_picture if self.profile_info else None
    def get_cover_photo(self):
        return self.profile_info.cover_photo if self.profile_info else None
    def get_bio(self):
        return self.profile_info.bio if self.profile_info else None

    def get_name(self):
        return self.profile_info.name if self.profile_info else None
    
    meta = {
        'collection':'users'
    }
# Post model
class Post(Document):
    title=StringField(max_length=100)
    content = StringField(required=False)
    user_id= ReferenceField(User)
    date_of_creation= DateTimeField()
    post_photo = StringField(required=False)
    like_count = IntField(default=0)
    likes = ListField(ReferenceField(User))
    comment_count = IntField(default=0)
    comments = ListField(ReferenceField('Comment'))
    tags = ListField(IntField(default=[]))
    status=StringField(required=False)
    meta = {
        'collection':'posts' 
    }


if __name__ == '__main__':
    app.run(debug=True)

# Comment model
class Comment(Document):
    text = StringField(required=True)
    user= ReferenceField(User, required=True)
    post = ReferenceField(Post, required=True)
    date_of_creation= DateTimeField()
    meta = {
        'collection':'comments' 
    }
class Notification(Document):
    sender = ReferenceField(User, required=True)  # Reference to the user who triggered the notification
    recipient = ReferenceField(User, required=True)  # Reference to the user who will receive the notification
    message = StringField(required=True)  
    is_read = BooleanField(default=False) 
    created_at = DateTimeField(default=datetime.utcnow) 

    meta = {
        'collection': 'notifications'
    }
