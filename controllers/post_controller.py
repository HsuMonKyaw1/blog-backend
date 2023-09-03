from datetime import datetime
from bson import ObjectId
from flask import Blueprint, jsonify,request,session
from models.mymodel import Post,User,Comment
from auth import login_required
import cloudinary
import cloudinary.uploader

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

        # Create a new post record in the database
            new_post = Post(title=title, content=content, post_photo=post_photo,user_id=user_id) 
            new_post.save()
        
            return jsonify(response), 201

        except Exception as e:
            return jsonify({'error': str(e)}), 500

#post_delete
@post_bp.route('/posts/<post_id>', methods=['DELETE'],endpoint='delete_post')
@login_required
def delete_post(post_id):
    try:
      post = Post.objects.get(id=post_id)
      post_user_id=post.user_id
      
      user_id = session.get('user_id')
      if user_id:
          user=User.objects.get(id=user_id)
       
          if (user==post_user_id):
              
              comments = Comment.objects(post=post)
              comments.delete()
              
              post.delete()
              return jsonify({'message': 'Post and associated comments are deleted successfully'})
          else:
           return str(post_user_id), 403
      else:
         return jsonify({'error': 'Unauthorized to delete this comment'}), 403
    
    except Exception as e:
        return jsonify({'error': str(user_id)}), 500
    
#post_update
@post_bp.route('/update_post/<post_id>', methods=['PUT'],endpoint='update_post')
def update_post(post_id):
    post = Post.objects.get(id=post_id)
    # post_user_id=post.user_id
      
    # user_id = session.get('user_id')
    # if user_id:
    #     user=User.objects.get(id=user_id)
       
    #     if (user==post_user_id):
    title = request.form['title']
    content = request.form['content']
    post_photo = request.files['post_photo']
    if title:
        post.title = title
    if content:
        post.content = content
    if post_photo:
        response = cloudinary.uploader.upload(post_photo)
        public_id = response['public_id']
        post_photo= public_id

        post.save()

    return jsonify(response)
 

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
            'user_id': post.user_id,
            'date_of_creation': post.date_of_creation,
            'likes_count':post.likes_count,
            'comment_count':post.comment_count
        }
        post_list.append(post_data)
    return jsonify(post_list)

#get_posts_by_user_id   
@post_bp.route('/user/<user_id>/posts', methods=['GET'])
def get_user_posts_by_uid(user_id):
    try:
        user = User.objects.get(id=user_id)
        if user:
            posts = Post.objects(user=user)

            post_list = []
            for post in posts:
                post_data = {
                    'title':post.title,
                    'content': post.content,
                    'created_at': post.date_of_creation,
                    'likes_count':post.likes_count,
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
                    'likes_count':post.likes_count,
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