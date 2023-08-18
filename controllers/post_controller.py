from datetime import datetime
from flask import Blueprint, jsonify,request
from controllers.user_controller import User
from mongoengine import Document, StringField, ReferenceField, DateTimeField,IntField

post_bp = Blueprint('post', __name__)
# Post model
class Post(Document):
    content = StringField(required=True)
    user_id= ReferenceField(User, required=True)
    date_of_creation= DateTimeField()
    likes_count = IntField(default=0)
    comments_count = IntField(default=0)
    meta = {
        'collection':'posts' # Replace 'users' with your desired collection name
    }

@post_bp.route('/posts',methods=['POST'])
def create_post(post_id):
    data = request.json
    content = data.get('content')
    user_id = data.get('user_id')  # Assuming you're sending the user's ID in the request
    
    if not content or not user_id:
        return jsonify({"error": "Content and user_id are required"}), 400

    try:
        user = User.objects.get(id=user_id)
        new_post = Post(content=content, user=user, date_of_creation=datetime.now())
        new_post.save()
        
        return jsonify({"message": "Post created successfully"}), 201
    except User.DoesNotExist:
         return jsonify({"error": "user not found"}), 404
    

@post_bp.route('/posts/<post_id>',methods=['DELETE'])
def delete_post(post_id):
    data = request.json
    content = data.get('content')
    user_id = data.get('user_id')
    post_id=data.get('id')

    try:
        post = Post.objects.get(id=post_id)
        post.delete()
        return jsonify({"message": "Post deleted successfully"}), 200
    except Post.DoesNotExist:
        return jsonify({"error": "Post not found"}), 404
    
    
# @post_bp.route('/posts', methods=['GET', 'POST', 'PUT'])
# def posts():
#       # Find the user by username
#       data = request.json
#       content = data.get('content')
#       user_id = data.get('user_id')
#       post_id=data.get('id')

#       if not user:
#         return jsonify({'message': 'User not found'}), 404

#     if request.method == 'GET':
#         # Return user profile data
#         profile_data = {
#             'username': user.username,
#             'email': user.email,
#             # Include other profile attributes as needed
#         }
#         return jsonify(profile_data)

#     elif request.method == 'PUT':
#         data = request.get_json()

#         # Update user profile data
#         if 'email' in data:
#             user.email = data['email']
#         if 'password' in data:
#             user.password = data['password']

#         user.save()  # Save the updated user record

#         return jsonify({'message': 'Profile updated successfully'})