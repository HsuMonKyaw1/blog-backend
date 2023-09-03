from venv import logger
from flask import Blueprint, jsonify, request,abort,session,json
from models.mymodel import User
from flask_jwt_extended import create_access_token,unset_jwt_cookies,jwt_required,decode_token
import jwt
from bson import json_util,ObjectId
# from bson import ObjectId
from flask_bcrypt import bcrypt
import cloudinary
import cloudinary.uploader
import os

user_bp = Blueprint('user', __name__)


from app import db

#get_all_users
@user_bp.route('/users',methods=['GET'])
def index():
    users = User.objects.all()
    user_list = []
    for user in users:
        user_data = {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            # 'interests':user.interests,
            'profile_info': {
                'profile_picture': user.profile_info.profile_picture if user.profile_info else None,
                'cover_photo': user.profile_info.cover_photo if user.profile_info else None,
                'bio': user.profile_info.bio if user.profile_info else None,
                'name': user.profile_info.name if user.profile_info else None
            }
        }
        user_list.append(user_data)
    return jsonify(user_list)

#get_top_users_by_followers_count
@user_bp.route('/suggestedUsers',methods=['GET'])
def suggestedUser():
    users = User.objects.all()
    user_list = []
    response_list = []
    for user in users:
        user_data = {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'profile_info': {
                'profile_picture': user.profile_info.profile_picture if user.profile_info else None,
            },
            'followers' : user.followers,
            'followerCount': user.followerCount,
        }
        user_list.append(user_data)
    user_list=sorted(user_list,key = lambda d: d['followerCount'],reverse=True)
    for i in range(10):
        response_list.append(user_list[i])
    return jsonify(json.dumps(response_list))

#register_user
@user_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    profile_info = {
       "bio" : '',
       "profile_picture":'',
       "name":'',
       "cover_photo":''
    }
    # interests = data.get('interests')
    

    # Validate the user input
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Username, email, and password are required'}), 400

    # Check if the username is already in use
    existing_username = User.objects(username=username).first()
    if existing_username:
        return jsonify({'message': 'Username is already in use'}), 409

    # Check if the email is already in use
    existing_email = User.objects(email=email).first()
    if existing_email:
        return jsonify({'message': 'Email is already in use'}), 409
    # Create a new user record
    new_user = User(
        username=username,
        email=email,
        password=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt(12)),
        profile_info=profile_info,
        interests= []
        # interests=interests
    )
    new_user.save()

    return jsonify({'message': 'User registered successfully'}), 201

#user_login
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Validate the user input
    if 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Username and password are required'}), 400

    username = request.json.get('username')
    password = request.json.get('password')

    # Find the user by username and check the password
    user = User.objects(username=username).first()
    # user.pop('_id')

    if user and bcrypt.checkpw(password.encode('utf-8'),user.password.encode('utf-8')):
        # Store user information in the session to mark them as authenticated
        #  session['user_id'] =str(user.id) 
        user_data = {
        'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'profile_info': {
                'profile_picture': user.profile_info.profile_picture if user.profile_info else None,
                'cover_photo': user.profile_info.cover_photo if user.profile_info else None,
                'bio': user.profile_info.bio if user.profile_info else None,
                'name': user.profile_info.name if user.profile_info else None
            } 
    }
        access_token = create_access_token(identity=str(user.id))
        response = {"access_token" : access_token,"message":"Login Successful","user":user_data}
        
        return jsonify(response)

    
    return jsonify({'error': 'Invalid credentials'}), 401

#user_logout
@user_bp.route('/logout', methods=['POST'])
def logout():
    # session.clear()
    response = jsonify({"message":"Logout Successful"})
    unset_jwt_cookies(response)
    return response

#user_profile
@user_bp.route('/profile/<user_id>', methods=['GET', 'POST', 'PUT'])
def user_profile(user_id):
    # Find the user by username
    user = User.objects(id=ObjectId(user_id)).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if request.method == 'GET':
         # Return user profile data
        profile_data = {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'profile_info': {
                'profile_picture': user.profile_info.profile_picture if user.profile_info else None,
                'cover_photo': user.profile_info.cover_photo if user.profile_info else None,
                'bio': user.profile_info.bio if user.profile_info else None,
                'name': user.profile_info.name if user.profile_info else None
            },
            'interests':user.interests
        }
        return jsonify(profile_data)

    elif request.method == 'PUT':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        bio = request.form.get('bio')
        name = request.form.get('name')
        interests = request.form.get('interests')
        if request.form.get('profile_img') == None or request.form.get('profile_img') == '':
            # if request.files['profile_img'].filename == '':
                profile_pic = None
        else:
            if user.profile_info.profile_picture:
                cloudinary.uploader.destroy(user.profile_info.profile_picture)
            profile_pic = request.files['profile_img']
        
        if request.form.get('cover_img') == '' or request.form.get('cover_img') == None:
            # if request.files['cover_img'].filename == '':
                cover_photo = None
        else:
            if user.profile_info.cover_photo:
                cloudinary.uploader.destroy(user.profile_info.cover_photo)
            cover_photo = request.files['cover_img']

        # Update user profile data
        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.password = password
        if bio:
            user.profile_info.bio = bio
        if name:
            user.profile_info.name = name
        if interests:
            user.interests = json.loads(interests)

        # Upload profile picture and cover photo
        if profile_pic:
            profile_response = cloudinary.uploader.upload(profile_pic)
            url = profile_response['secure_url']
            user.profile_info.profile_picture = url
        if cover_photo:
            cover_response = cloudinary.uploader.upload(cover_photo)
            url = cover_response['secure_url']
            user.profile_info.cover_photo = url
        
        response = {
            # "profile_response": profile_response,
            # "cover_response": cover_response,
            # "username" : user.username
            "message" : "Updated Successfully"
        }
        user.save()
        logger.info(response)
        return jsonify(response)
    else:
        return jsonify({"error": "User not found"})

@user_bp.route('/profile/<user_id>/changePassword', methods=['PUT'])
def passwordChange(user_id):
    # Find the user by username
    user = User.objects(id=ObjectId(user_id)).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    current_password = request.form.get('currentPassword')
    new_password = request.form.get('newPassword')
    email = request.form.get('email')
    if user and bcrypt.checkpw(current_password.encode('utf-8'),user.password.encode('utf-8')):
        user.password = bcrypt.hashpw(new_password.encode('utf-8'),bcrypt.gensalt(12)).decode('utf-8')
        user.email = email

        response = {
            # "profile_response": profile_response,
            # "cover_response": cover_response,
            # "username" : user.username
            "message" : "Updated Password Successfully"
        }
        user.save()
        return jsonify(response)
    
    return jsonify({'error':'Passwords do not match'}), 401

#get_user_by_id  
# @user_bp.route('/users/<user_id>', methods=['GET'])
# @jwt_required()
# def get_user_by_id(user_id):
#     user = User.objects(id=user_id).first()

#     if not user:
#         return jsonify({'message': 'User not found'}), 404
#     user_data = {
#         'id': str(user.id),
#             'username': user.username,
#             'email': user.email,
#             'profile_info': {
#                 'profile_picture': user.profile_info.profile_picture if user.profile_info else None,
#                 'bio': user.profile_info.bio if user.profile_info else None,
#                 'name': user.profile_info.name if user.profile_info else None
#             } 
#     }

#     return jsonify(user_data)

@user_bp.route('/currentuser', methods=['POST'])
@jwt_required()
def get_current_user():
    jsontoken = request.json.get('access_token')
    data = decode_token(jsontoken)
    user = User.objects(id=data['sub']).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404
    response = {
        'id': str(user.id),
            'username': user.username,
            'email': user.email,
            # 'interests':user.interests,
            'profile_info': {
                'profile_picture': user.profile_info.profile_picture if user.profile_info else None,
                'cover_photo': user.profile_info.cover_photo if user.profile_info else None,
                'bio': user.profile_info.bio if user.profile_info else None,
                'name': user.profile_info.name if user.profile_info else None
            },
            "interests":user.interests,
            "followers":user.followers,
            "bookmarks":user.bookmarks
    }
    # response.headers.add('Access-Control-Allow-Credentials', '*')
    return jsonify(response)

#get_user_by_username
@user_bp.route('/users/<username>', methods=['GET'])
def get_user_by_username(username):
    user = User.objects(username=username).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404
    user_data = {
    'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'interests':user.interests,
            'profile_info': {
                'profile_picture': user.profile_info.profile_picture if user.profile_info else None,
                'cover_photo': user.profile_info.cover_photo if user.profile_info else None,
                'bio': user.profile_info.bio if user.profile_info else None,
                'name': user.profile_info.name if user.profile_info else None
            }
    }
    return jsonify(user_data)

