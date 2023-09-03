import datetime
from flask import Flask,Blueprint, abort, session,jsonify,request
from models.mymodel import User
from bson import json_util,ObjectId
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
        if user not in user_to_follow.followers:
            # Add the user to the follower list
            user_to_follow.followers.append(user)
            user.followings.append(user_to_follow)
            user_to_follow.followerCount +=1
            user_to_follow.save()
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
        if user in user_to_unfollow.followers:
            # Remove the user from the follower list
            user_to_unfollow.followers.remove(user)
            user.followings.remove(user_to_unfollow)
            user_to_unfollow.followerCount -= 1
            user_to_unfollow.save()
            user.save()
            return jsonify({'message': f'You have unfollowed {user_to_unfollow.username}'}), 200
        else:
            return jsonify({'message': f'You are not following {user_to_unfollow.username}'}), 400
    else:
        return jsonify({'message': 'User not found'}), 404

#get followers of a user
@follower_bp.route('/follower/<user_id>', methods=['GET'])
def get_followers(user_id):
    try:
      
        user = User.objects.get(id=user_id)

        # Get the followers of the user
        followers = user.followers

        # Create a list to store follower usernames
        follower_list = []
        for follower in followers:
            followerData = User.objects.get(id = ObjectId(follower.id))
            follower_data = {
                'id': str(followerData.id),
                'username': followerData.username,
                'email': followerData.email,
                # 'interests':user.interests,
                'profile_info': {
                    'profile_picture': followerData.profile_info.profile_picture if user.profile_info else None,
                }
            }
            follower_list.append(follower_data)
        return jsonify(follower_list)
    
    except Exception as e:
     return jsonify({'error': str(e)}), 500
    
@follower_bp.route('/following/<user_id>', methods=['GET'])
def get_followings(user_id):
    try:
      
        user = User.objects.get(id=user_id)

        # Get the followers of the user
        followings= user.followings

        # Create a list to store follower usernames
        follower_list = []
        for following in followings:
            followingData = User.objects.get(id = ObjectId(following.id))
            follower_data = {
                'id': str(followingData.id),
                'username': followingData.username,
                'email': followingData.email,
                # 'interests':user.interests,
                'profile_info': {
                    'profile_picture': followingData.profile_info.profile_picture if user.profile_info else None,
                }
            }
            follower_list.append(follower_data)
        return jsonify(follower_list)
    
    except Exception as e:
     return jsonify({'error': str(e)}), 500
