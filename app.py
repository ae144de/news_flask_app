import eventlet
eventlet.monkey_patch()
from flask import Flask, request, jsonify
import threading
import asyncio
import json
import firebase_admin
from firebase_admin import credentials, db
import websockets
from datetime import datetime, timezone, timedelta
import uuid
from flask_cors import CORS
# from auth import token_required
from dotenv import load_dotenv
import os
from functools import wraps
import jwt
from flask_jwt_extended import JWTManager, verify_jwt_in_request
from colorama import init, Fore, Style, Back
import time
from flask_socketio import SocketIO, emit
import google.oauth2.id_token
import google.auth.transport.requests
import websockets.connection
from database import init_db, insert_news_item, get_all_news
import firebase_admin
from firebase_admin import credentials
from notifications import send_push_notification

load_dotenv()

# Initialize colorama
init(autoreset=True)
app = Flask(__name__)

async_loop = None
ws_connection = None

# Use asyncio as the async mode.
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

FIREBASE_CREDENTIAL = "/opt/secrets/firebase_au_key.json"

# Replace 'path/to/serviceAccountKey.json' with the actual path to your service account JSON file.
cred = credentials.Certificate(FIREBASE_CREDENTIAL)

# Initialize the default Firebase app
firebase_admin.initialize_app(cred)

# CORS(app, resources={r"/*":{"origins": "https://alert-bot-v3.vercel.app"}})
# CORS(app, resources={
#     r"/api/*": {
#         "origins": "https://alert-bot-v3.vercel.app",
#         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#         "allow_headers": ["Content-Type", "Authorization"],
#         "supports_credentials": True,
#     }
# })

# Initialize the SQLite table
init_db()

# --- External WebSocket Settings ---
external_ws_url = "wss://wss.phoenixnews.io"  # Replace with your external WS URL
api_key = "vVFfrq5TZipcYV7lEOtKJ2NzH5Xg4HgUdK7CsZopwXi1uJciaYDSt6mcL7z1c7jO"                      # Replace with your API key
headers = {"x-api-key": api_key}
device_token = "cxCOgLYMRYajlll3OozvAS:APA91bEHfrtGGM2qey8_qIM1-dIDyJOEcYI0X5VJTjTElBCwZzMtLEKDiiRrCOOXZnPABF4zpY5oF4s312MGo_BdQdnLNhOBeEckHqe8w7CftU76uI2dMsQ"

async def websocket_handler():
    global subscriptions, ws_connection, subscribed_symbols
    #Establish single base connection.
    while True:
        try:
            async with websockets.connect(external_ws_url, ping_interval=None, ping_timeout=40, close_timeout=5, additional_headers=headers) as ws:
                ws_connection = ws
                print("Websocket base connection established.")
                # After connection, subscribe to all symbols from existing alerts.
                
                #Keep listening for incoming messages.
                async for message in ws:
                    print(f"Message received: {message}")
                    if message == 'ping':
                        await ws.send('pong')
                        # print(Fore.YELLOW + "Pong sent.")
                    else:
                        try:
                            data = json.loads(message)
                            print("Parsed data:", data)
                            insert_news_item(data)
                            # Emit the parsed data to all connected Socket.IO clients
                            socketio.emit('news', {"msg":"msg_rcv"})
                            title=f"sonarBOT News({data['source']})"
                            body=f"{data['body']}" if data['source'] == 'Twitter' else data['title']
                            print("Title: ", title)
                            send_push_notification(token=device_token, title=title, body=body)
                            # socketio.emit('news', {"msg":data})
                            
                            print("Emitted 'news' event with data.")
                        except Exception as parse_error:
                            print("Error parsing message:", parse_error)
                            
                            
        except websockets.ConnectionClosedError:
            print("Connection closed. Reconnecting...")
            
            await asyncio.sleep(5)


        except Exception as e:
            print(f"Websocket error: {str(e)}")
           
            await asyncio.sleep(5)


def start_async_loop():
    global async_loop
    async_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(async_loop)
    async_loop.run_until_complete(websocket_handler())

threading.Thread(target=start_async_loop, daemon=True).start()

@app.route('/api/news', methods=['GET'])
def fetch_news():
    """Return all stored news (up to 20) in newest-first order."""
    news_items = get_all_news()
    print("FETCH ALL THE NEWS REQUESTED!!!")
    return jsonify(news_items)

@app.route('/api/test', methods=['GET'])
def test_news():
    return "Test endpoint is working !!!"


# @app.route('/news/')
# def index_news():
#     return "News Flask NEWS App is running!"

# @app.route('/')
# def index():
#     return "News Flask App is running"


# @socketio.on('connect')
# def handle_connect():
#     print("Client connected via Socket.IO!")
#     emit('news', {'data': 'Welcome to the News App!'})


if __name__ == '__main__':
    socketio.run(app, host="127.0.0.1", port=8000 ,debug=False)