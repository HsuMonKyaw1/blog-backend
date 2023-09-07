from flask import Blueprint, request, jsonify
from datetime import datetime
from models.mymodel import Notification
from models.mymodel import User

noti_bp = Blueprint('noti', __name__)

def create_notification(user_id, content):
    try:
        # Find the user by user_id
        user = User.objects.get(id=user_id)

        # Create a new notification
        notification = Notification(
            user_id=user,
            content=content,
            created_at=datetime.utcnow()
        )

        # Save the notification to the database
        notification.save()
        return True  
    except User.DoesNotExist:
        return False  

    except Exception as e:
        return False 
    
@noti_bp.route('/notifications/<user_id>', methods=['GET'])
def view_notifications(user_id):
    try:
        # Retrieve all notifications for the specified user
        notifications = Notification.objects(recipient=user_id).order_by('-created_at')

        # Prepare the notification data for response
        notification_list = []
        for notification in notifications:
            notification_data = {
                'id': str(notification.id),
                'sender': str(notification.sender),  
                'content': notification.content,
                'is_read': notification.is_read,
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            notification_list.append(notification_data)

        return jsonify(notification_list)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@noti_bp.route('/mark_notification_as_read/<notification_id>', methods=['POST'])
def mark_notification_as_read(notification_id):
    try:
        # Retrieve the notification by its ID
        notification = Notification.objects.get(id=notification_id)

        # Mark the notification as read
        notification.is_read = True
        notification.save()

        return jsonify({'message': 'Notification marked as read'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
