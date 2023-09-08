from datetime import datetime,timezone
from bson import ObjectId
from flask import Blueprint, jsonify,request,session,json
from models.mymodel import User,Post,Comment
from flask_jwt_extended import jwt_required,decode_token
from auth import login_required
import cloudinary
import cloudinary.uploader
from mongoengine.queryset.visitor import Q
from controllers.noti_controller import create_notification

post_bp = Blueprint('post', __name__)

#post_create
@post_bp.route('/posts/<user_id>', methods=['POST'])
def create_post(user_id):
    user = User.objects(id=ObjectId(user_id)).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    if user:
        try:
            title = request.form['title']
            content = request.form['content']
            tags = request.form.get('tags')
            status = request.form.get('status')
             #   post_photo = request.files['post_photo']
            if request.form.get('post_photo') == '':
            # if request.files['cover_img'].filename == '':
                post_photo = None
            else:
                post_photo = request.files['post_photo']
            if post_photo:
                response = cloudinary.uploader.upload(post_photo)
                url = response['secure_url']
                post_photo= url
            if tags:
                tags = json.loads(tags)

        # Create a new post record in the database
            new_post = Post(title=title, content=content, post_photo=post_photo,user_id=user_id,date_of_creation = datetime.now(timezone.utc),tags = tags, status=status) 
            new_post.save()
        
            return jsonify({'message': 'Post published successfully'}), 201

        except Exception as e:
            return jsonify({'error': str(e)}), 500

#post_delete
@post_bp.route('/posts/<post_id>', methods=['DELETE'],endpoint='delete_post')
@jwt_required()
def delete_post(post_id):
    try:
        post = Post.objects.get(id=ObjectId(post_id))
        post_user_id=post.user_id.id
      
        jsontoken = request.json.get('access_token')
        data = decode_token(jsontoken)
        user = User.objects(id=data['sub']).first()
        if user:
          user=User.objects.get(id=ObjectId(user.id))
          if (user.id==post_user_id):
              comments = Comment.objects(post=post)
              comments.delete()
              
              post.delete()
              return jsonify({'message': 'Post and associated comments are deleted successfully'})
          else:
            return str(post_user_id), 403
        else:
            return jsonify({'error': 'Unauthorized to delete this comment'}), 403
    
    except Exception as e:
        return jsonify({'error': e}), 500
    
#post_update
@post_bp.route('/update_post/<post_id>', methods=['PUT'],endpoint='update_post')
def update_post(post_id):
    post = Post.objects.get(id=post_id)
    title = request.form['title']
    content = request.form['content']
    tags = request.form.get('tags')
    status = request.form.get('status')

    if request.form.get('post_photo') == '':
        post_photo = None
    else:
        if post.post_photo:
         cloudinary.uploader.destroy(post.post_photo)
        post_photo = request.files['post_photo']
    if title:
        post.title = title
    if content:
        post.content = content
    if post_photo:
        cover_response = cloudinary.uploader.upload(post_photo)
        url = cover_response['secure_url']
        post.post_photo = url
    if tags:
        post.tags = json.loads(tags)
    if status:
        post.status = status
    post.date_of_creation = datetime.now(timezone.utc)

    post.save()
    return jsonify({"message":"Post Updated Successfully"})
 

#get_all_posts
@post_bp.route('/posts',methods=['GET'])
def index():
    posts = Post.objects.all()
    post_list = []
    for post in posts:
        post_data = {
            'id': str(post.id),
            'title':post.title,
            'content': post.content,
            'user_id': str(post.user_id.id),
            'date_of_creation': post.date_of_creation,
            'like_count':post.like_count,
            'comment_count':post.comment_count
        }
        post_list.append(post_data)
    return jsonify(post_list)

#get_posts_by_user_id   
@post_bp.route('/user/<user_id>/posts', methods=['GET'])
def get_user_posts_by_uid(user_id):
    try:
        user = User.objects.get(id=ObjectId(user_id))
        if user:
            posts = Post.objects(user_id=user.id,status='Posted')

            post_list = []
            for post in posts:
                post_data = {
                    'id':str(post.id),
                    'title':post.title,
                    'like_count':post.like_count,
                    'comment_count':post.comment_count,
                    'date_of_creation':post.date_of_creation,
                    'post_photo':post.post_photo,
                    'tags':post.tags,
                    'status':post.status
                }
                post_list.append(post_data)

            return jsonify(post_list), 200
        else:
            return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        print(e)
        return jsonify({'message': 'An error occurred'}), 500
   
# Get all post for feed
@post_bp.route('/posts/feed/<user_id>/<sort_condition>/<page_number>', methods=['GET'])
def get_user_posts_for_feed(user_id,sort_condition,page_number):
    try:
        user = User.objects.get(id=ObjectId(user_id))
        if user:
            post_list = []
            following_list_id = []
            followings= user.followings
            for following in followings:
                following_list_id.append(ObjectId(following.id))
            posts = Post.objects( (Q(user_id__in = following_list_id) | Q(tags__exists = user.interests)) | Q(user_id__ne = user.id) & Q(status="Posted")).order_by(sort_condition).skip(int(page_number)*5).limit(5)
            for post in posts:
                post_data = {
                    'id':str(post.id),
                    'author':post.user_id.username,
                    'title':post.title,
                    'uid':str(post.user_id.id),
                    'like_count':post.like_count,
                    'comment_count':post.comment_count,
                    'date_of_creation':post.date_of_creation,
                    'post_photo':post.post_photo,
                    'tags':post.tags,
                    'status':post.status
                }
                post_list.append(post_data)
            # posts = Post.objects(user_id=user.id,status='Posted')
            return jsonify(post_list), 200
        else:
            return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        print(e)
        return jsonify({'message': 'An error occurred'}), 500
   

#get_draft_posts
@post_bp.route('/user/<user_id>/posts/draft', methods=['GET'])
def get_user_posts_by_uid_draft(user_id):
    try:
        user = User.objects.get(id=ObjectId(user_id))
        if user:
            posts = Post.objects(Q(user_id=user.id) & Q(status='Draft'))

            post_list = []
            for post in posts:
                post_data = {
                    'id':str(post.id),
                    'title':post.title,
                    'date_of_creation':post.date_of_creation,
                    'post_photo':post.post_photo,
                    'tags':post.tags,
                    'status':post.status,
                    'content':post.content
                }
                post_list.append(post_data)

            return jsonify(post_list), 200
        else:
            return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        print(e)
        return jsonify({'message': 'An error occurred'}), 500
   
#get_single_post
@post_bp.route('/post/<post_id>', methods=['GET'])
def get_post_by_id(post_id):
    try: 
        post = Post.objects(id=ObjectId(post_id)).first()
        user = User.objects(id=ObjectId(post.user_id.id)).first()
        post_data = {
            'id':str(post.id),
            'author':user.username,
            'title':post.title,
            'content': post.content,
            'date_of_creation': post.date_of_creation,
            'like_count':post.like_count,
            'comment_count':post.comment_count,
            'comments':post.comments,
            'post_photo':post.post_photo,
            'comments':post.comments,
            'status':post.status,
            'tags':post.tags      
        }
        return jsonify(post_data), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'An error occurred'}), 500

#get_posts_by_username 
@post_bp.route('/user/<username>/posts', methods=['GET'])
def get_user_posts_by_username(username):
    try:
        user = User.objects(username=username).first()
        if user:
            posts = Post.objects(user=user)

            post_list = []
            for post in posts:
                post_data = {
                    'title':post.title,
                    'content': post.content,
                    'created_at': post.date_of_creation,
                    'like_count':post.like_count,
                    'comment_count':post.comment_count,
                    'comments':post.comments              
                }
                post_list.append(post_data)

            return jsonify({'posts': post_list}), 200
        else:
            return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        print(e)
        return jsonify({'message': 'An error occurred'}), 500
    
@post_bp.route('/posts/<post_id>/like', methods=['POST'])
def like_post(post_id):
    try:
         # Get the current user
        username= request.json.get('username') 
        user = User.objects(username=username).first()

        post = Post.objects.get(id=post_id)

        # Check if the user has already liked the post
        if user.id in post.likes:
            return jsonify({'error': 'User has already liked this post'}), 400

        post.likes.append(user.id)
        post.like_count += 1
        post.save()

        # Create a notification
        notification_content = f'You have been liked by {user.username}.'
        create_notification(user.id, post.user_id, notification_content)

        return jsonify({'message': 'Post liked successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500