from flask import Flask,request,jsonify
from flask_session import Session
from mongoengine import connect
from pymongo import MongoClient
import cloudinary
from bson import json_util
import cloudinary.uploader
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity,unset_jwt_cookies,jwt_required,JWTManager
from flask_bcrypt import Bcrypt
import json
import os
# from flask.json import JSONEncoder
from mongoengine.base import BaseDocument
from mongoengine.queryset.base import BaseQuerySet
# from flask_marshmallow import Marshmallow, Schema, fields

# class MongoEngineJSONEncoder(JSONEncoder):
#     def default(self,obj):
#         if isinstance(obj,BaseDocument):
#             return json_util._json_convert(obj.to_mongo())
#         elif isinstance(obj,BaseQuerySet):
#             return json_util._json_convert(obj.as_pymongo())
#         return JSONEncoder.default(self, obj)

if os.getenv("environment") == 'developement':
    origin = ["localhost:3000","localhost:5000","127.0.0.1"]
else:
    origin = "https://leaflet-uit.netlify.app/"

app = Flask(__name__)
# app.secret_key = 'fe5923c7a4782927f60de714f7fed01ded1cec5656fc1e5c'
app.config["JWT_SECRET_KEY"] = 'secret'
jwt = JWTManager(app)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
Session(app)
bcrypt = Bcrypt(app)
cors= CORS(app, supports_credentials=True,origins=origin)
app.config['CORS_HEADERS'] = 'Content-Type','Authorization','Access-Control-Allow-Credentials'

app.config['MONGODB_SETTINGS'] = {
    'db': 'social_platform',
    'host': 'mongodb+srv://hsumonk001:hsumonkyaw12345@cluster0.nzi4wje.mongodb.net/?retryWrites=true&w=majority'
}
# ma= Marshmallow(app)

# ma.Schema.TYPE_MAPPING[ObjectId] = fields.fields.String
# class UserSchema(ma.Schema):
#     id = fields.fields.String()
#     class Meta:
#         additional = ('email','followerCount','followers')
db = connect(db=app.config['MONGODB_SETTINGS']['db'], host=app.config['MONGODB_SETTINGS']['host'])
print(db)

cloudinary.config(cloud_name = os.getenv('CLOUD_NAME'), api_key=os.getenv('API_KEY'), 
    api_secret=os.getenv('API_SECRET'))

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token 
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response

from controllers.post_controller import post_bp
from controllers.comment_controller import comment_bp
from controllers.user_controller import user_bp
from controllers.follower_controller import follower_bp
from controllers.bookmark_controller import bookmark_bp
from controllers.search_controller import search_bp
from controllers.noti_controller import noti_bp

# app.json_encoder = MongoEngineJSONEncoder

app.register_blueprint(post_bp)
app.register_blueprint(comment_bp)
app.register_blueprint(user_bp)
app.register_blueprint(follower_bp)
app.register_blueprint(bookmark_bp)
app.register_blueprint(search_bp)
app.register_blueprint(noti_bp)

