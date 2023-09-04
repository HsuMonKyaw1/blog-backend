from flask import Blueprint, request, jsonify
from models.mymodel import User,Post

search_bp = Blueprint('search', __name__)

@search_bp.route('/search/users', methods=['GET'])
def search_users():
    try:
        # Get the search term from the query parameter
        search_term = request.args.get('q')

        # Perform a case-insensitive search for users by username
        users = User.objects(username__icontains=search_term)

        # Create a list to store user data
        user_data = []
        for user in users:
            user_info = {
                'user_id': str(user.id),
                'username': user.username,
                'email':user.email,
            }

            # Check if the user has a profile picture
            if user.profile_info and user.profile_info.profile_picture:
                user_info['profile_picture'] = user.profile_info.profile_picture
            if user.profile_info and user.profile_info.cover_photo:
                user_info['cover_photo'] = user.profile_info.cover_photo
            if user.profile_info and user.profile_info.bio:
                user_info['bio'] = user.profile_info.bio
            if user.profile_info and user.profile_info.name:
                user_info['name'] = user.profile_info.name

            user_data.append(user_info)

        return jsonify({'users': user_data})

    except Exception as e:
     return jsonify({'error': str(e)}), 500
    

@search_bp.route('/search/posts', methods=['GET'])
def search_posts():
    try:
        # Get the search term from the query parameter
        search_term = request.args.get('q')

        # Perform a case-insensitive search for users by username
        posts = Post.objects(title__icontains=search_term)

        # Create a list to store user data
        post_data = []
        for post in posts:
            post_info = {
               'post_id': str(post.id),
                'title': post.title,
                'content': post.content,
            }

            # Check if the user has a profile picture
            if post.post_photo:
                post_info['post_photo'] = post.post_photo
          

            post_data.append(post_info)

        return jsonify({'posts': post_data})

    except Exception as e:
     return jsonify({'error': str(e)}), 500