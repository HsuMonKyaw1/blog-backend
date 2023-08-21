from datetime import datetime
from flask import Blueprint,jsonify,request,session
from models.mymodel import User,Post,Comment
from auth import login_required
comment_bp = Blueprint('comment', __name__)

@comment_bp.route('/comments', methods=['POST'])
@login_required  # Apply the login_required decorator
def create_comment():
    try:
        # Get the data from the request JSON
        data = request.get_json()

        # Extract the post_id and comment_text from the data
        post_id = data.get('post_id')
        text = data.get('text')

        # Retrieve the Post instance based on post_id
        post = Post.objects.get(id=post_id)

        # Get the authenticated user from the session
        user_id = session.get('user_id')

        if user_id:
            # Retrieve the authenticated user
            user = User.objects.get(id=user_id)

            # Create a new Comment and associate it with the User and Post
            new_comment = Comment(
                text=text,
                user=user,
                post=post,
                date_of_creation=datetime.now()
            )
            new_comment.save()

            # Return a success response
            return jsonify({'message': 'Comment created successfully'}), 201
        else:
            return jsonify({'error': 'User not authenticated'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500
  
@comment_bp.route('/comments/<comment_id>', methods=['DELETE'], endpoint='delete_comment')
@login_required  # Apply the login_required decorator
def delete_comment(comment_id):
    try:
        data = request.json
        comment=data.get('comment_id')
        comment = Comment.objects.get(id=comment_id)

        user_id = session.get('user_id')
        if user_id:
            # Retrieve the authenticated user
            user = User.objects.get(id=user_id)
            # Check if the authenticated user is the author of the comment or has appropriate permissions
            if comment.user == user:
            # Delete the comment
             comment.delete()

            # Return a success response
            return jsonify({'message': 'Comment deleted successfully'})

        return jsonify({'error': 'Unauthorized to delete this comment'}), 403

    except Comment.DoesNotExist:
        return jsonify({'error': 'Comment not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@comment_bp.route('/comments/<post_id>', methods=['GET'])
def get_comments_by_post_id(post_id):
    try:
        data = request.json
        post=data.get('post_id')
        post = Post.objects.get(id=post_id)

        # Query comments associated with the post
        comments = Comment.objects(post=post)

        # Create a list to store comment data
        comment_list = []

        # Iterate through the comments and retrieve relevant information
        for comment in comments:
            comment_data = {
                'comment_id': str(comment.id),
                'text': comment.text,
                'user_id': str(comment.user.id),
                'date_of_creation': comment.date_of_creation.strftime('%Y-%m-%d %H:%M:%S')
            }
            comment_list.append(comment_data)

        return jsonify(comment_list)

    except Post.DoesNotExist:
        return jsonify({'error': 'Post not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500