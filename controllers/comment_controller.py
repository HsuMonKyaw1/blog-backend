from datetime import datetime
from flask import Blueprint,jsonify,request,session
from models.mymodel import User,Post,Comment
from auth import login_required
comment_bp = Blueprint('comment', __name__)

#comment_create
@comment_bp.route('/comments', methods=['POST'])
@login_required 
def create_comment():
    try:
        data = request.get_json()
        post_id = data.get('post_id')
        text = data.get('text')

        post = Post.objects.get(id=post_id)
        user_id = session.get('user_id')

        if user_id:
            user = User.objects.get(id=user_id)
            new_comment = Comment(
                text=text,
                user=user,
                post=post,
                date_of_creation=datetime.now()
            )
            new_comment.save()
            return jsonify({'message': 'Comment created successfully'}), 201
        else:
            return jsonify({'error': 'User not authenticated'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500

#comment_delete
@comment_bp.route('/comments/<comment_id>', methods=['DELETE'], endpoint='delete_comment')
@login_required
def delete_comment(comment_id):
    try:
        data = request.json
        comment=data.get('comment_id')
        comment = Comment.objects.get(id=comment_id)

        user_id = session.get('user_id')
        if user_id:
            user = User.objects.get(id=user_id)
            # Check if the authenticated user is the author of the comment or has appropriate permissions
            if comment.user == user:
             comment.delete()
            return jsonify({'message': 'Comment deleted successfully'})

        return jsonify({'error': 'Unauthorized to delete this comment'}), 403

    except Comment.DoesNotExist:
        return jsonify({'error': 'Comment not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

#comment_update
@comment_bp.route('/update_comment/<comment_id>', methods=['PUT'],endpoint='update_comment')
@login_required
def update_comment(comment_id):
    comment = Comment.objects.get(id=comment_id)
    comment_user_id=comment.user

    user_id = session.get('user_id')
    if user_id:
        user=User.objects.get(id=user_id)
       
        if (user==comment_user_id):
           data = request.get_json()
           if 'text' in data:
             comment.text= data['text']
             comment.save()

           return jsonify({'message': 'Post updated successfully'})
        else:
         return jsonify({'error': 'User not authenticated'}), 401
        
#get_comments_by_post_id
@comment_bp.route('/comments/<post_id>', methods=['GET'])
def get_comments_by_post_id(post_id):
    try:
        data = request.json
        post=data.get('post_id')
        post = Post.objects.get(id=post_id)

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