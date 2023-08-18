import datetime
from flask import Blueprint,jsonify,request
from mongoengine import Document, StringField, EmailField, ReferenceField, DateTimeField,IntField
from controllers.user_controller import User
from controllers.post_controller import Post
comment_bp = Blueprint('comment', __name__)

# Comment model
class Comment(Document):
    content = StringField(required=True)
    user_id = ReferenceField(User, required=True)
    post_id = ReferenceField(Post, required=True)
    date_of_creation= DateTimeField()

@comment_bp.route('/comments',methods=['POST'])
def create_comment(post_id):
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
    

@comment_bp.route('/comments/<post_id>',methods=['DELETE'])
def delete_comment(post_id):
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