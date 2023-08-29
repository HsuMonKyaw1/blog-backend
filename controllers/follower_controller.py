from curses import flash
import datetime
from flask import Flask,Blueprint, abort, session,jsonify,request
from models.mymodel import User
from auth import login_required
follower_bp = Blueprint('follower', __name__)

from mongoengine import Document,ListField,StringField, EmailField, ReferenceField, DateTimeField,IntField,EmbeddedDocument,EmbeddedDocumentField
class Follower(Document):
    follower_user = ReferenceField(User, required=True, reverse_delete_rule=2)
    following_user = ReferenceField(User, required=True)
    followed_at = DateTimeField(required=True)

    meta = {
        'collection': 'followers'
    }

@follower_bp.route('/follow/<user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    current_user_id = session['user_id']
    
    current_user = User.objects(id=current_user_id).first()
    target_user = User.objects(id=user_id).first()

    if not current_user or not target_user:
        abort(404, "User not found")

    if current_user == target_user:
        return jsonify(message="You cannot follow yourself")

    # Check if the current user is already following the target user
    if target_user in current_user.following:
        return jsonify(message="You are already following this user")

    # Add the target user to the current user's following list
    current_user.following.append(target_user)
    current_user.save()

    # You can also update the target user's followers list here if needed
    target_user.followers.append(current_user)
    target_user.save()

    return jsonify(message="You are now following this user")

# Route to unfollow a user
@follower_bp.route('/unfollow/<user_id>', methods=['POST'])
@login_required
def unfollow_user(user_id):
    current_user_id = session['user_id']

    current_user = User.objects(id=current_user_id).first()
    target_user = User.objects(id=user_id).first()

    if not current_user or not target_user:
        abort(404, "User not found")

    if current_user == target_user:
        return jsonify(message="You cannot unfollow yourself")

    # Check if the current user is following the target user
    if target_user not in current_user.following:
        return jsonify(message="You are not following this user")

    # Remove the target user from the current user's following list
    current_user.following.remove(target_user)
    current_user.save()

    # You can also update the target user's followers list here if needed
    target_user.followers.remove(current_user)
    target_user.save()

    return jsonify(message="You have unfollowed this user")

from models import User, Follower  # Import the User and Follower models

def get_followers(user_id):
    # Find the user for whom you want to retrieve followers
    user = User.objects(id=user_id).first()

    if not user:
        return None  # User not found

    # Find the Follower document associated with the user
    follower_doc = Follower.objects(user=user).first()

    if not follower_doc:
        return []  # No followers

    # Retrieve the list of followers from the Follower document
    followers = follower_doc.followers

    return followers

@follower_bp.route('/api/get_followers/<user_id>', methods=['GET'])
def api_get_followers(user_id):
    followers = get_followers(user_id)
    if followers is not None:
        # Return followers as JSON
        return jsonify(followers=[follower.username for follower in followers])
    else:
        return jsonify(message="User not found or has no followers."), 404