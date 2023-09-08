from flask import Blueprint, request, jsonify
from datetime import datetime
from models.mymodel import Notification
from models.mymodel import User

noti_bp = Blueprint('noti', __name__)

def create_notification(sender, recipient,post, message):
    try:
        notification = Notification(
            sender=sender,  
            recipient=recipient,
            post=post,
            message=message,
            is_read=False, 
            created_at=datetime.utcnow()  
        )
        notification.save() 
        
        return jsonify({'message': 'Notification created successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@noti_bp.route('/notifications/<notification_id>', methods=['GET'])
def view_notification(notification_id):
    try:
        # Retrieve the notification by its ID
        notification = Notification.objects.get(id=notification_id)

        # Return the notification data as JSON
        notification_data = {
            'id': str(notification.id),
            'sender': str(notification.sender),
            'recipient': str(notification.recipient),
            'message': notification.message,
            'is_read': notification.is_read,
            'created_at': notification.created_at
        }

        return jsonify(notification_data), 200

    except Notification.DoesNotExist:
        return jsonify({'error': 'Notification not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@noti_bp.route('/notifications_user/<user_id>', methods=['GET'])
def view_notifications(user_id):
    try:
        # Retrieve all notifications for the specified user
        notifications = Notification.objects(recipient=user_id).order_by('is_read','-created_at')

        # Prepare the notification data for response
        notification_list = []
        for notification in notifications:
            notification_data = {
                'id': str(notification.id),
                'sender': str(notification.sender.id),
                'post':str(notification.post.id) if notification.post else None, 
                'message': notification.message,
                'is_read': notification.is_read,
                'created_at': notification.created_at,
                'profile_photo':notification.sender.profile_info.profile_picture,
                'post_photo':notification.post.post_photo if notification.post else None
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
