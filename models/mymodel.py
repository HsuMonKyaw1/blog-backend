from flask import Flask
from pymongo import MongoClient
from mongoengine import Document,ListField,StringField, EmailField, ReferenceField, DateTimeField,IntField,EmbeddedDocument,EmbeddedDocumentField

# from controllers.follower_controller import Follower


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
    followers = ListField(ReferenceField("Follower"))
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
    title=StringField(required=True,max_length=100)
    content = StringField(required=True)
    user_id= ReferenceField(User, required=True)
    date_of_creation= DateTimeField()
    like_count = IntField(default=0)
    comment_count = IntField(default=0)
    comments = ListField(ReferenceField('Comment'))
    status=StringField(required=True)
    meta = {
        'collection':'posts' 
    }

# Comment model
class Comment(Document):
    text = StringField(required=True)
    user= ReferenceField(User, required=True)
    post = ReferenceField(Post, required=True)
    date_of_creation= DateTimeField()
    meta = {
        'collection':'comments' 
    }
    
class Bookmark(Document):
    user = ReferenceField(User, required=True)  # Reference to the user who created the bookmark
    post = ReferenceField(Post, required=True)  # Reference to the bookmarked post
    created_at = DateTimeField(required=True)    # Timestamp when the bookmark was created

    meta = {
        'collection': 'bookmarks'
    }


if __name__ == '__main__':
    app.run(debug=True)

