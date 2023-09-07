from flask import Blueprint, request, jsonify
from models.mymodel import User,Post
from mongoengine.queryset.visitor import Q
from bson import ObjectId

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
                'userId': str(user.id),
                'username': user.username,
                'email':user.email,
                'profile_info':{
                   'profile_picture':user.profile_info.profile_picture
                } 
            }


            user_data.append(user_info)

        return jsonify(user_data)

    except Exception as e:
     return jsonify({'error': str(e)}), 500
    

@search_bp.route('/search/posts', methods=['GET'])
def search_posts():
    try:
        # Get the search term from the query parameter
        search_term = request.args.get('q')
        users = User.objects(username__icontains=search_term)
        userIdList = []
        for user in users:
                userIdList.append(ObjectId(user.id))

        # Perform a case-insensitive search for users by username
        posts = Post.objects(Q(user_id__in = userIdList) | Q(title__icontains=search_term)).order_by('date_of_creation').limit(10)

        # Create a list to store user data
        post_data = []
        for post in posts:
            post_info = {
               'post_id': str(post.id),
                'title': post.title,
                'author' : post.user_id.username,
                'post_photo':post.post_photo,
                'date_of_creation':post.date_of_creation,
                'tags':post.tags,
                'like_count':post.like_count,
                'comment_count':post.comment_count
            }

            # Check if the user has a profile picture
          

            post_data.append(post_info)

        return jsonify(post_data)

    except Exception as e:
     return jsonify({'error': str(e)}), 500