from flask import Flask
from mongoengine import connect
from pymongo import MongoClient

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'db': 'social_platform',
    'host': 'mongodb+srv://hsumonk001:hsumonkyaw12345@cluster0.nzi4wje.mongodb.net/?retryWrites=true&w=majority'
}
db = connect(db=app.config['MONGODB_SETTINGS']['db'], host=app.config['MONGODB_SETTINGS']['host'])
print(db)
from controllers.post_controller import post_bp
from controllers.comment_controller import comment_bp
from controllers.user_controller import user_bp

app.register_blueprint(post_bp)
app.register_blueprint(comment_bp)
app.register_blueprint(user_bp)