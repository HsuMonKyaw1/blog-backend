from flask import Blueprint, request, jsonify, abort, session
from models import User, Post, Bookmark 
from models.mymodel import User
from auth import login_required

# Create a blueprint for the bookmark controller
bookmark_bp = Blueprint('bookmark', __name__)

# Route to add a bookmark
@bookmark_bp.route('/add/<post_id>', methods=['POST'])
@login_required
def add_bookmark(post_id):
    user_id = session['user_id']

    user = User.objects(id=user_id).first()
    post = Post.objects(id=post_id).first()

    if not user or not post:
        abort(404, "User or Post not found")

    existing_bookmark = Bookmark.objects(user=user, post=post).first()

    if existing_bookmark:
        return jsonify(message="Bookmark already exists")

    bookmark = Bookmark(user=user, post=post)
    bookmark.save()

    return jsonify(message="Bookmark added successfully")

# Route to remove a bookmark
@bookmark_bp.route('/remove/<post_id>', methods=['POST'])
@login_required
def remove_bookmark(post_id):
    user_id = session['user_id']

    user = User.objects(id=user_id).first()
    post = Post.objects(id=post_id).first()

    if not user or not post:
        abort(404, "User or Post not found")

    bookmark = Bookmark.objects(user=user, post=post).first()

    if not bookmark:
        return jsonify(message="Bookmark not found")

    bookmark.delete()

    return jsonify(message="Bookmark removed successfully")

# Route to list bookmarks for the currently logged-in user
@bookmark_bp.route('/list', methods=['GET'])
@login_required
def list_bookmarks():
    user_id = session['user_id']
    user = User.objects(id=user_id).first()

    if not user:
        abort(404, "User not found")

    bookmarks = Bookmark.objects(user=user)

    bookmark_list = [
        {
            'post_id': str(bookmark.post.id),
            'title': bookmark.post.title,
            'content': bookmark.post.content,
        }
        for bookmark in bookmarks
    ]

    return jsonify(bookmarks=bookmark_list)
