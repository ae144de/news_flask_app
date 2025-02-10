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

load_dotenv()

# Initialize colorama
init(autoreset=True)
app = Flask(__name__)

# Use asyncio as the async mode.
socketio = SocketIO(app)

# CORS(app, resources={r"/*":{"origins": "https://alert-bot-v3.vercel.app"}})
# CORS(app, resources={
#     r"/api/*": {
#         "origins": "https://alert-bot-v3.vercel.app",
#         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#         "allow_headers": ["Content-Type", "Authorization"],
#         "supports_credentials": True,
#     }
# })

# --- External WebSocket Settings ---
external_ws_url = "wss://wss.phoenixnews.io"  # Replace with your external WS URL
api_key = "vVFfrq5TZipcYV7lEOtKJ2NzH5Xg4HgUdK7CsZopwXi1uJciaYDSt6mcL7z1c7jO"                      # Replace with your API key
headers = {"x-api-key": api_key}


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
                        print(Fore.YELLOW + "Pong sent.")
                    else:
                        data = json.loads(message)
                        # print(f"[**Message]: {data["s"]}")
                        # print(f"[##SUBSCRIPTIONS]: {subscriptions}")
                        print(data)
                            
                            
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

@app.route('/news')
def index():
    return "News Flask App is running!"



if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8000 ,debug=False)