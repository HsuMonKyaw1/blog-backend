from flask import Blueprint, jsonify, request,abort,session
from models.mymodel import User
from flask_jwt_extended import create_access_token,unset_jwt_cookies,jwt_required,decode_token
import jwt
from bson import json_util


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
            'interests':user.interests,
            'profile_info': {
                'profile_picture': user.profile_info.profile_picture if user.profile_info else None,
                'cover_photo': user.profile_info.cover_photo if user.profile_info else None,
                'bio': user.profile_info.bio if user.profile_info else None,
                'name': user.profile_info.name if user.profile_info else None
            }
        }
        user_list.append(user_data)
    return jsonify(user_list)

#register_user
@user_bp.route('/register', methods=['POST'])
def register_user():
    # Get registered user input
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    profile_info = data.get('profile_info')
    interests = data.get('interests')

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
        password=password,
        profile_info=profile_info, 
        interests=interests
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

    if user and user.password == password:
        # Store user information in the session to mark them as authenticated
        #  session['user_id'] =str(user.id) 
        user_data = {
        'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'profile_info': {
                'profile_picture': user.profile_info.profile_picture if user.profile_info else None,
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
    data = request.get_json()
    user = User.objects(id=user_id).first()
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
            }
        }
        return jsonify(profile_data)

    elif request.method == 'PUT':
           data = request.get_json()

          # Update user profile data      
           if 'username' in data:
            user.username = data['username']
           if 'email' in data:
            user.email = data['email']
           if 'password' in data:
            user.password = data['password']
           if 'profile_picture' in data:
            user.profile_info.profile_picture= data['profile_picture']
           if 'cover_photo' in data:
            user.profile_info.cover_photo= data['cover_photo']
           if 'bio' in data:
            user.profile_info.bio = data['bio']
           if 'name' in data:
            user.profile_info.name= data['name']
           
           user.save()  
 
           return jsonify({'message': 'Profile updated successfully'})

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
            'interests':user.interests,
            'profile_info': {
                'profile_picture': user.profile_info.profile_picture if user.profile_info else None,
                'cover_photo': user.profile_info.cover_photo if user.profile_info else None,
                'bio': user.profile_info.bio if user.profile_info else None,
                'name': user.profile_info.name if user.profile_info else None
            } 
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

