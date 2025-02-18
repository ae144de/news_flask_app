import json
from firebase_admin import messaging


def send_push_notification(token, title, body):
    
    # Create a message payload.
    message = messaging.Message(
        notification = messaging.Notification(
            title = title,
            body = body,
        ),
        
        # Optionally include extra data as a JSON string.
        # data = {
            
        # }
        token = token,
    )
    
    try:
        response = messaging.send(message)
        print('Successfully sent message: ', response)
        return response
    except Exception as e:
        print('Error sending message: ', e)
        return None
    