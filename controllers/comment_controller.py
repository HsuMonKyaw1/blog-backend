from datetime import datetime,timezone
from bson import ObjectId
from flask import Blueprint,jsonify,request,session
from flask_jwt_extended import create_access_token,unset_jwt_cookies,jwt_required,decode_token
from models.mymodel import User,Post,Comment
from auth import login_required
from controllers.noti_controller import create_notification

comment_bp = Blueprint('comment', __name__)

#comment_create
@comment_bp.route('/comments/<post_id>', methods=['POST'])
@jwt_required()
def create_comment(post_id):
    try:
        # Get the current user
        username= request.json.get('username') 
        text = request.json.get('text')
        user = User.objects(username=username).first()
        if user:
         user = User.objects.get(username=username)
         post = Post.objects.get(id=str(post_id))
         new_comment = Comment(
            text=text,
            user=user,
            post=post,
            date_of_creation=datetime.now(timezone.utc)
         )
         post.comment_count += 1
         post.save()
         new_comment.save()

         # Notify the post owner that their post has been commented on
         post_owner_id = post.user_id.id  # Get the user ID of the post owner
         notification_content = f'Your post "{post.title}" has been commented by {user.username}.'
         create_notification(user.id, post_owner_id,post.id,notification_content)

        return jsonify({'message': 'Comment created successfully'}), 201
    except Exception as e:
   
        return jsonify({'error': str(e)}), 500

#comment_delete
@comment_bp.route('/comments/<post_id>/<comment_id>', methods=['DELETE'], endpoint='delete_comment')
@jwt_required()
def delete_comment(post_id,comment_id):
    try:
        data = request.json
        comment=data.get('comment_id')
        comment = Comment.objects.get(id=comment_id)
        username= request.json.get('username')
        user = User.objects(username=username).first()
        if user:
            post = Post.objects.get(id=str(post_id))
            # Check if the authenticated user is the author of the comment or has appropriate permissions
            if comment.user == user:
             post.comment_count -= 1
             comment.delete()
             post.save()
            return jsonify({'message': 'Comment deleted successfully'})

        return jsonify({'error': 'Unauthorized to delete this comment'}), 403

    except Comment.DoesNotExist:
        return jsonify({'error': 'Comment not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

#comment_update
@comment_bp.route('/update_comment/<comment_id>', methods=['PUT'],endpoint='update_comment')
@jwt_required()
def update_comment(comment_id):
    comment = Comment.objects.get(id=comment_id)
    comment_user_id=comment.user
    username= request.json.get('username')
    user = User.objects(username=username).first()
    if user:
       
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
        # data = request.json
        # post=data.get('post_id')
        post = Post.objects.get(id=post_id)

        comments = Comment.objects(post=post).order_by('-date_of_creation')

        # Create a list to store comment data
        comment_list = []

        # Iterate through the comments and retrieve relevant information
        for comment in comments:
            comment_data = {
                'comment_id': str(comment.id),
                'text': comment.text,
                'user_id': str(comment.user.id),
                'author': comment.user.username,
                'profile_photo':comment.user.profile_info.profile_picture,
                'date_of_creation': comment.date_of_creation
            }
            comment_list.append(comment_data)

        return jsonify(comment_list)

    except Post.DoesNotExist:
        return jsonify({'error': 'Post not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500