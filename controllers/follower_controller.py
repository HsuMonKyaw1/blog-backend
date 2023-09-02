import datetime
from flask import Flask,Blueprint, abort, session,jsonify,request
from models.mymodel import User
follower_bp = Blueprint('follower', __name__)

#follow user
@follower_bp.route('/follow/<user_id>', methods=['POST'])
def follow_user(user_id):
    # Get the current user
    username= request.json.get('username') 
    user = User.objects(username=username).first()

    # Get the user to follow with user_id
    user_to_follow = User.objects(id=user_id).first()

    # Check if the user exists
    if user_to_follow:
        # Check if the user is not already followed
        if user_to_follow not in user.followers:
            # Add the user to the follower list
            user.followers.append(user_to_follow)
            user.save()
            return jsonify({'message': f'You are now following {user_to_follow.username}'}), 200
        else:
            return jsonify({'message': f'You are already following {user_to_follow.username}'}), 400
    else:
        return jsonify({'message': 'User not found'}), 404

#unfollow user
@follower_bp.route('/unfollow/<user_id>', methods=['POST'])
def unfollow_user(user_id):
    # Get the current user
    username= request.json.get('username') 
    user = User.objects(username=username).first()

    # Get the user to unfollow
    user_to_unfollow = User.objects(id=user_id).first()

    # Check if the user exists
    if user_to_unfollow:
        # Check if the user is in the follower list
        if user_to_unfollow in user.followers:
            # Remove the user from the follower list
            user.followers.remove(user_to_unfollow)
            user.save()
            return jsonify({'message': f'You have unfollowed {user_to_unfollow.username}'}), 200
        else:
            return jsonify({'message': f'You are not following {user_to_unfollow.username}'}), 400
    else:
        return jsonify({'message': 'User not found'}), 404

#get followers of a user
@follower_bp.route('/followers/<user_id>', methods=['GET'])
def get_followers(user_id):
    try:
      
        user = User.objects.get(id=user_id)

        # Get the followers of the user
        followers = user.followers

        # Create a list to store follower usernames
        follower_usernames = [follower.username for follower in followers]

        return jsonify({'followers': follower_usernames})

    except Exception as e:
     return jsonify({'error': str(e)}), 500
