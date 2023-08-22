from flask import Blueprint, jsonify, request,abort,session
from models.mymodel import User

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
            'profile_info': {
                'profile_picture': user.profile_info.profile_picture if user.profile_info else None,
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
        profile_info=profile_info 
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

    if user and user.password == password:
        # Store user information in the session to mark them as authenticated
         session['user_id'] =str(user.id) 
         return jsonify({'message': 'Login successful'})

    return jsonify({'error': 'Invalid credentials'}), 401

#user_logout
@user_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout successful'})

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
           if 'bio' in data:
            user.profile_info.bio = data['bio']
           if 'name' in data:
            user.profile_info.name= data['name']
           
           user.save()  # Save the updated user record
 
           return jsonify({'message': 'Profile updated successfully'})
#get_user_by_id  
@user_bp.route('/users/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    user = User.objects(id=user_id).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404
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

    return jsonify(user_data)

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
            'profile_info': {
                'profile_picture': user.profile_info.profile_picture if user.profile_info else None,
                'bio': user.profile_info.bio if user.profile_info else None,
                'name': user.profile_info.name if user.profile_info else None
            }
    }
    return jsonify(user_data)

