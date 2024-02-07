# Import the required module from the fyers_apiv3 package
from fyers_apiv3 import fyersModel
from fyers_apiv3.FyersWebsocket import data_ws
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from tabulate import tabulate
import os,json, time
import pandas as pd 
import numpy as np

global fyers
position =0
stop_loss=0
flag =0
exit =0
target =0
strike =''

# reading from config file 
def read_config(file_path):
    config = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            config[key.strip()] = value.strip()
    return config

config_file_path = 'config.ini'
config = read_config(config_file_path)

# Access the values by attribute name
client_id = config['client_id']  #client id and secret key are fetched from config file 
secret_key = config['secret_key']
print("Client ID : ",client_id)
print("Secreat Key : ",secret_key)
redirect_uri = "https://www.google.co.in/" 
response_type = "code"  #  This value must always be “code”
grant_type = "authorization_code"  

# Initialize a pandas DataFrame to store live data
# live_data = pd.DataFrame(columns=['timestamp', 'symbol', 'last_price'])


def generateAccessToken() :
    # response_type = "code"  # This value must always be “code”
    # grant_type = "authorization_code"  

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
    # print(' access token newly generated is =============== :',access_token)

    return access_token


def writeAccessCodeToFile(token):
    with open('authcode.ini', 'w') as file:
        file.write(token)

def readAccessCodeFromFile():
    try:
        with open('authcode.ini', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return None
    
saved_token = readAccessCodeFromFile()
# print('Saved token is +++++++++++++++++++:',saved_token)

def getEMAData():
    today_date = datetime.now().strftime('%Y-%m-%d')
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    # print(f"Yesterday's date: {yesterday_date}")
    # print(f"Today's date: {today_date}")

    hdata = {
    "symbol":"NSE:NIFTY50-INDEX",
    "resolution":5,
    "date_format":"1",
    "range_from":yesterday_date,
    "range_to":today_date,
    "cont_flag":"1"
    }
    response = fyers.history(data=hdata)
    # print("History Response :",response)
   
    for candle in response['candles']:
        epoch_time = candle[0]
        timestamp = datetime.fromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M:%S')
        candle[0] = timestamp
    
    
    data = pd.DataFrame.from_dict(response['candles'])
    cols = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
    data.columns = cols
    data['EMA_5'] = data['Close'].ewm(span=5, adjust=False).mean()
    # data['EMA_10'] = data['Close'].ewm(span=10, adjust=False).mean()
    # data['EMA_15'] = data['Close'].ewm(span=15, adjust=False).mean()
    global emadata
    emadata =data
     


if saved_token:
    print('Token loaded from file')
    fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=saved_token, log_path="")
    # getData()

else:
    print('access token not found. so generating a new access token')
    access_token = generateAccessToken()
    writeAccessCodeToFile(access_token)

# def identify_Trend(emadata):
#     print("******** Identifying the trend ************")
#     nine_ema_current = emadata['EMA_9'].iloc[-1]
#     nine_ema_previous= emadata['EMA_9'].iloc[-2]
#     print("9 Ema current :",nine_ema_current, "9_ema_previous:",nine_ema_previous )
#     percentage_change = ((nine_ema_current - nine_ema_previous) / nine_ema_previous) * 100
#     print("Percentage chnage is",percentage_change )
#     if abs(percentage_change) > 40:
#         print("Percentage chnage is significant Percentage Change")
#     else:
#         print("Percentage chnage is neutral")


# def identify_trend(data):
#     trends = []
#     for i in range(len(data)):
#         close = data.loc[i, 'Close']
#         ema_9 = data.loc[i, 'EMA_9']
#         ema_15 = data.loc[i, 'EMA_15']

#         # Calculate vectors for angle calculation
#         vector_9_ema = np.array([ema_9, close - ema_9])
#         vector_15_ema = np.array([ema_15, close - ema_15])

#         # Calculate angles
#         angle_9_ema = np.degrees(np.arccos(np.dot(vector_9_ema, [1, 0]) / (np.linalg.norm(vector_9_ema) * np.linalg.norm([1, 0]))))
#         angle_15_ema = np.degrees(np.arccos(np.dot(vector_15_ema, [1, 0]) / (np.linalg.norm(vector_15_ema) * np.linalg.norm([1, 0]))))

#         # Determine trend based on angles
#         if ema_9 > ema_15 and angle_9_ema > 30:
#             trend = "Upper Trend=============== : can buy CE"
#         elif ema_15 > ema_9 and angle_9_ema > 30:
#             trend = "Down Trend ================: can buy PE"
#         else:
#             trend = "No Clear Trend"

#         trends.append(trend)

#     data['Trend'] = trends
#     return data
 
def onmessage(message):
    f_flag =0
    local_time = time.localtime()
    formatted_time = time.strftime("%b %d , %H:%M:%S", local_time)    
    current_minute = local_time.tm_min
    current_second = local_time.tm_sec
    # print("Time ",formatted_time)
    # print(message)
    ltp =message['ltp']
    print("ltp: ",ltp)
    if (current_minute % 5 == 0 and 5 <= current_second < 7  and f_flag == 0):
        getEMAData()
        print(emadata)
        # Store the EMA data for the last 5 values in a new array
        last_5_ema_data = emadata.tail(5)[['Timestamp',  'EMA_5', ]].values.tolist()
        print(last_5_ema_data)
        
        # checking the condition for short 
        if (emadata['Open'].iloc[-2] > emadata['EMA_5'].iloc[-2]
            and emadata['High'].iloc[-2] > emadata['EMA_5'].iloc[-2]
            and emadata['Low'].iloc[-2] > emadata['EMA_5'].iloc[-2]
            and emadata['Close'].iloc[-2] > emadata['EMA_5'].iloc[-2]
            and ltp < emadata['Low'].iloc[-2]):
            
            strike_price = int(round(ltp -2))
            print("conditions for shorting met ")

            if (position==0 and flag ==0):
                strike_price = int(round(ltp -2))
                pe_strike  = "NSE:NIFTY24208"+strike_price+"PE"
                print(" ATM price :-----",pe_strike)
       
                data = {
                        "symbol":str(pe_strike),
                        "qty":15,
                        "type":2,
                        "side":1,
                        "productType":"MARGIN",
                        "limitPrice":0,
                        "stopPrice":0,
                        "validity":"DAY",
                        "disclosedQty":0,
                        "offlineOrder":False,
                        "orderTag":"tag1"
                        }
                response = fyers.place_order(data=data)



    # formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    # Print the current local time, minute, and second
    # print("Current Local Time:", formatted_time)
    # print("Current Minute:", current_minute)
    # print("Current Second:", current_second)
    # print("Cflag:",f_flag)
    # print(emadata)
  
    # print("******** 10 ema data updated************")
    # getEMAData()
    # nine_ema = emadata['EMA_9'].iloc[-1]
    # ten_ema = emadata['EMA_10'].iloc[-1]
    # df = pd.DataFrame(emadata)
    # # result_df = identify_trend(df)
    # print(df[['Timestamp','Open' ,'Close', 'EMA_9','EMA_10','EMA_15']].iloc[-1])

    # if (current_minute % 5 == 0 and 5 <= current_second < 15  and f_flag == 0):
    #     print("******** 5 ema data updated************")
    #     getEMAData("NSE:NIFTY50-INDEX",5,"","")
    #     # nine_ema = emadata['EMA_9'].iloc[-1]
    #     # fiteen_ema = emadata['EMA_15'].iloc[-1]
    #     # low =  emadata['Low'].iloc[-1]
    #     # last_ema= emadata.iloc[-1]
    #     # print("Last  EMA:",last_ema)
    #     # identify_Trend(emadata)
    #     df = pd.DataFrame(emadata)
    #     result_df = identify_trend(df)
    #     print(result_df[['Timestamp','Open' ,'Close', 'EMA_9', 'EMA_15', 'Trend']])
       


def onerror(message):
    print("Error:", message)

def onclose(message):
    print("Connection closed:", message)

def onopen():
    # Specify the data type and symbols you want to subscribe to
    data_type = "SymbolUpdate"
    # Subscribe to the specified symbols and data type
    symbols = ["NSE:NIFTY50-INDEX"]
    ws_fyers.subscribe(symbols=symbols, data_type=data_type)
    # Keep the socket running to receive real-time data
    ws_fyers.keep_running()

# Replace the sample access token with your actual access token obtained from Fyers
ws_access_token = f"{client_id}:{saved_token}"
# print('ws_access_token is ++++++++++++++++:',ws_access_token)
# Create a FyersDataSocket instance with the provided parameters
ws_fyers = data_ws.FyersDataSocket(
    access_token=ws_access_token,       # Access token in the format "appid:accesstoken"
    log_path="",                     # Path to save logs. Leave empty to auto-create logs in the current directory.
    litemode=False,                  # Lite mode disabled. Set to True if you want a lite response.
    write_to_file=False,             # Save response in a log file instead of printing it.
    reconnect=True,                  # Enable auto-reconnection to WebSocket on disconnection.
    on_connect=onopen,               # Callback function to subscribe to data upon connection.
    on_close=onclose,                # Callback function to handle WebSocket connection close events.
    on_error=onerror,                # Callback function to handle WebSocket errors.
    on_message=onmessage             # Callback function to handle incoming messages from the WebSocket.
)
# Establish a connection to the Fyers WebSocket
ws_fyers.connect()

