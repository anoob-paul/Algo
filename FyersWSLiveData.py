# Import the required module from the fyers_apiv3 package
from fyers_apiv3 import fyersModel
from fyers_apiv3.FyersWebsocket import data_ws
from datetime import datetime
from tabulate import tabulate
import os
import pandas as pd


# reading from config file 
def read_config(file_path):
    config = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            config[key.strip()] = value.strip()
    return config

config_file_path = 'config.txt'
config = read_config(config_file_path)

# Access the values by attribute name

global fyers
client_id = config['client_id']  #client id and secret key are fetched from config file 
secret_key = config['secret_key']  
redirect_uri = "https://www.google.co.in/" 
response_type = "code"  #  This value must always be “code”
grant_type = "authorization_code"  




def writeAccessCodeToFile(token):
    with open('authcode.txt', 'w') as file:
        file.write(token)


def readAccessCodeFromFile():
    try:
        with open('authcode.txt', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

saved_token = readAccessCodeFromFile()



def generateAccessToken() :

    response_type = "code"  # This value must always be “code”
    grant_type = "authorization_code"  

    # Create a session model with the provided credentials
    session = fyersModel.SessionModel(
        client_id=client_id,
        secret_key=secret_key,
        redirect_uri=redirect_uri,
        response_type=response_type,
        grant_type=grant_type
    )
    res_redirect_URL = session.generate_authcode()
    print(res_redirect_URL)
    auth_code = input("Enter Authcode: ")
    # Set the authorization code in the session object
    session.set_token(auth_code)
    # Generate the access token using the authorization code
    auth_response = session.generate_token()
    access_token = auth_response['access_token']
    print(' access token is :',access_token)

    return access_token


if saved_token:
    print('Token loaded from file')
    fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=saved_token, log_path="")

else:
    access_token = generateAccessToken()
    writeAccessCodeToFile(access_token)

profile = fyers.get_profile()
# funds = fyers.funds()
# print(profile)
# print(funds)




def onmessage(message):
    print("Response:", message)


def onerror(message):
    print("Error:", message)


def onclose(message):
    print("Connection closed:", message)


def onopen():
    # Specify the data type and symbols you want to subscribe to
    data_type = "SymbolUpdate"

    # Subscribe to the specified symbols and data type
    symbols = ["NSE:WTICRUDE24FEBFUT"]
    ws_fyers.subscribe(symbols=symbols, data_type=data_type)

    # Keep the socket running to receive real-time data
    ws_fyers.keep_running()

# Replace the sample access token with your actual access token obtained from Fyers
ws_access_token = f"{client_id} : {saved_token}"

# Create a FyersDataSocket instance with the provided parameters
ws_fyers = data_ws.FyersDataSocket(
    access_token=ws_access_token,       # Access token in the format "appid:accesstoken"
    log_path="",                     # Path to save logs. Leave empty to auto-create logs in the current directory.
    litemode=True,                  # Lite mode disabled. Set to True if you want a lite response.
    write_to_file=False,              # Save response in a log file instead of printing it.
    reconnect=True,                  # Enable auto-reconnection to WebSocket on disconnection.
    on_connect=onopen,               # Callback function to subscribe to data upon connection.
    on_close=onclose,                # Callback function to handle WebSocket connection close events.
    on_error=onerror,                # Callback function to handle WebSocket errors.
    on_message=onmessage             # Callback function to handle incoming messages from the WebSocket.
)

# Establish a connection to the Fyers WebSocket
ws_fyers.connect()
