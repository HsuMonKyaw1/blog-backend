from datetime import datetime
from flask import Blueprint, jsonify,request,session
from models.mymodel import Post,User,Comment
from auth import login_required

post_bp = Blueprint('post', __name__)

@post_bp.route('/posts/<post_id>', methods=['DELETE'],endpoint='delete_post')
@login_required
def delete_post(post_id):
    try:
      post = Post.objects.get(id=post_id)
      post_user_id=post.user_id
      
      user_id = session.get('user_id')
      if user_id:
          user=User.objects.get(id=user_id)
          print(user_id,post)
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

@post_bp.route('/posts', methods=['POST'])
@login_required  # Apply the login_required decorator
def create_post():
    try:
        # Get the data from the request JSON
        data = request.get_json()

        # Extract the title and content from the data
        title = data.get('title')
        content = data.get('content')

        # Get the authenticated user from the session
        user_id = session.get('user_id')

        if user_id:
            # Retrieve the authenticated user
            user = User.objects.get(id=user_id)

            # Create a new Post
            new_post = Post(
                title=title,
                content=content,
                user_id=user,
                date_of_creation=datetime.now()
            )
            new_post.save()

            # Return a success response
            return jsonify({'message': 'Post created successfully'}), 201
        else:
            return jsonify({'error': 'User not authenticated'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
                    'comment_count':post.comment_count
                }
                post_list.append(post_data)

            return jsonify({'posts': post_list}), 200
        else:
            return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        print(e)
        return jsonify({'message': 'An error occurred'}), 500

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
                    'comment_count':post.comment_count
                    
                }
                post_list.append(post_data)

            return jsonify({'posts': post_list}), 200
        else:
            return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        print(e)
        return jsonify({'message': 'An error occurred'}), 500
    
@post_bp.route('/posts/<post_id>', methods=['PUT'],endpoint='update_post')
@login_required  # Apply the login_required decorator
def update_post(post_id):
    try:
        # Get the data from the request JSON
        data = request.get_json()

        # Extract the post_id and comment_text from the data
        updated_title = data.get('title')
        updated_content= data.get('content')

        # Retrieve the Post instance based on post_id
        post = Post.objects.get(id=post_id)

        # Get the authenticated user from the session
        user_id = session.get('user_id')

        if user_id:
            # Retrieve the authenticated user
            user = User.objects.get(id=user_id)

            # Create a new Comment and associate it with the User and Post
            updated_post = Post(
                title=updated_title,
                content=updated_content,
                date_of_creation=datetime.now()
            )
            updated_post.save()

            # Return a success response
            return jsonify({'message': 'Comment created successfully'}), 201
        else:
            return jsonify({'error': 'User not authenticated'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500