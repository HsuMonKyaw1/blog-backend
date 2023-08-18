from flask import Blueprint, jsonify, request,abort
from mongoengine import Document, StringField, EmailField, ReferenceField, DateTimeField,IntField,connect,EmbeddedDocument,EmbeddedDocumentField

user_bp = Blueprint('user', __name__)

from app import db

class ProfileInfo(EmbeddedDocument):
    profile_picture = StringField()
    bio = StringField()
    name = StringField()

# User model
class User(Document):
    username = StringField(required=True, unique=True, max_length=50)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    profile_info = EmbeddedDocumentField(ProfileInfo)
    def get_profile_picture(self):
        return self.profile_info.profile_picture if self.profile_info else None

    def get_bio(self):
        return self.profile_info.bio if self.profile_info else None

    def get_name(self):
        return self.profile_info.name if self.profile_info else None
    
    meta = {
        'collection':'users' # Replace 'users' with your desired collection name
    }


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

@user_bp.route('/register', methods=['POST'])
def register_user():
    #get registered_user input
     data = request.get_json()

     username=data.get('username')
     password=data.get('password')
     email=data.get('email')

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

    # If the username or email is not unique, return an error response

    # Create a new user record
     new_user = User(
        username=data['username'],
        email=data['email'],
        password=data['password']
    )

    # Save the new user record to the database
     new_user.save()
     return jsonify({'message': 'User registered successfully'}), 201

@user_bp.route('/login', methods=['POST'])
def login():
    # Handle user login logic here
    data = request.get_json()

    # Validate the user input
    if 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Username and password are required'}), 400

    # Find the user by username
    user = User.objects(username=data['username']).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Verify password
    if user.password != data['password']:
        return jsonify({'message': 'Invalid password'}), 401

    return jsonify({'message': 'Login successful'}), 200

@user_bp.route('/profile', methods=['GET', 'POST', 'PUT'])
def user_profile():
      # Find the user by username
    data = request.get_json()
    user = User.objects(username=data['username']).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    if request.method == 'GET':
        # Return user profile data
        profile_data = {
            'username': user.username,
            'email': user.email,
            # Include other profile attributes as needed
        }
        return jsonify(profile_data)

    elif request.method == 'PUT':
        data = request.get_json()

        # Update user profile data
        if 'email' in data:
            user.email = data['email']
        if 'password' in data:
            user.password = data['password']

        user.save()  # Save the updated user record

        return jsonify({'message': 'Profile updated successfully'})
    
@user_bp.route('/users/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    # Retrieve user information by user_id
    print(user_id)
    user = User.objects(id=user_id).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Return user data
    user_data = {
        'id': str(user.id),
        'username': user.username,
        'email': user.email,
        # Include other user attributes as needed
    }

    return jsonify(user_data)

@user_bp.route('/users/<username>', methods=['GET'])
def get_user_by_username(username):
    # Retrieve user information by username
    user = User.objects(username=username).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Return user data
    user_data = {
        'id': str(user.id),
        'username': user.username,
        'email': user.email,
        # Include other user attributes as needed
    }

    return jsonify(user_data)

