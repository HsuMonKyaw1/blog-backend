from flask import Blueprint, request, jsonify, abort, session
from models.mymodel import User,Post

bookmark_bp = Blueprint('bookmark', __name__)

#bookmark a post
@bookmark_bp.route('/bookmark/<post_id>', methods=['POST'])
def bookmark_post(post_id):
    try:
     # Get the current user
     username= request.json.get('username') 
     user = User.objects(username=username).first()
     if user:
            # Retrieve the current user
            user = User.objects.get(username=username)

            # Retrieve the post to be bookmarked
            post = Post.objects.get(id=post_id)

            # Check if the post is not already bookmarked
            if post not in user.bookmarks:
                user.bookmarks.append(post)
                user.save()

                return jsonify({'message': 'Post bookmarked successfully'})

            return jsonify({'message': 'Post already bookmarked'})

     return jsonify({'error': 'User not authenticated'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500

#remove bookmarked post
@bookmark_bp.route('/remove-bookmark/<post_id>', methods=['POST'])
def remove_bookmark(post_id):
    try:
        # Retrieve the current user
        username= request.json.get('username')
        user = User.objects.get(username=username)

        # Retrieve the post to be removed from bookmarks
        post = Post.objects.get(id=post_id)

        # Check if the post is bookmarked
        if post in user.bookmarks:
            user.bookmarks.remove(post)
            user.save()

            return jsonify({'message': 'Post removed from bookmarks successfully'})

        return jsonify({'message': 'Post is not bookmarked'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#view bookmarks of a user
@bookmark_bp.route('/bookmarks/<user_id>', methods=['GET'])
def view_bookmarks(user_id):
    try:
        #get current user
        user = User.objects.get(id=user_id)

        # Get the user's bookmarked posts
        bookmarked_posts = user.bookmarks
        print(user.bookmarks)

        # Create a list to store the bookmarked post data (e.g., titles, content,post_cover)
        bookmarked_posts_data = []
        for post in bookmarked_posts:
            post_data = {
                'title': post.title,
                'content': post.content,
                'post_photo':post.post_photo,
                }
            bookmarked_posts_data.append(post_data)
        return jsonify({'bookmarked_posts':bookmarked_posts_data})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

