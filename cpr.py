# Import the required module from the fyers_apiv3 package
from fyers_apiv3 import fyersModel
from fyers_apiv3.FyersWebsocket import data_ws
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from tabulate import tabulate
import os,  json
import pandas as pd

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
    print(' access token newly generated is =============== :',access_token)

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
print('Saved token is +++++++++++++++++++:',saved_token)


def generate_cpr():

    today = datetime.now()
    yesterday = (datetime.now() - timedelta(days=1))

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    today_of_week = days[today.weekday()]
    yesterday_of_week =days[yesterday.weekday()]

    today_date = today.strftime('%Y-%m-%d')
    yesterday_date = yesterday.strftime('%Y-%m-%d')
    # Date format : yyyy-mm-dd
    # today_date ="2024-02-09"
    # yesterday_date="2024-02-23"

    print(f"Today is : {today_date}, {today_of_week},  ")
    print(f"Yesterday is : {yesterday_date}, {yesterday_of_week}")

    
    if today_of_week == 0:
        friday = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        print("since today is monday, assigning previous market day as friday")
        yesterday_date = friday

 
    hdata = {
    "symbol":"NSE:NIFTY50-INDEX",
    "resolution":"1D", 
    "date_format":"1",
    "range_from":yesterday_date,
    "range_to":yesterday_date,
    "cont_flag":"1"
    }
    response = fyers.history(data=hdata) # fetching the data for the timeframe
    for candle in response['candles']:
        epoch_time = candle[0]
        timestamp = datetime.fromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M:%S')
        candle[0] = timestamp

    print(" Time :",candle[0])

    high_price = candle[2]
    low_price = candle[3]
    close_price = candle[4]
    cpr=   round((high_price + low_price + close_price) / 3.0, 2) 
    bc =  round (((high_price + low_price) / 2.0),2)
    tc=   round ((cpr + (cpr - bc)),2)

    r1= round((2*cpr-low_price),2)
    s1= round((2*cpr-high_price),2)
    r2=round((cpr+(high_price-low_price)),2)
    s2=round((cpr-(high_price-low_price)),2)

    r3 = round((high_price + 2* (cpr - low_price)),2)
    s3 =  round((low_price- 2*(high_price-cpr)),2)

  
    print("CPR:", cpr)
    print("BC:", bc)
    print("TC:", tc)
    print ("R1:",r1)
    print ("S1:",s1)
    print ("R2:",r2)
    print ("S2:",s2)
    print ("R3:",r3)
    print ("S3:",s3)

 
if saved_token:
    print('Token loaded from file')
    fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=saved_token, log_path="")
    generate_cpr()

else:
    print('access token not found. so generating a new access token')
    access_token = generateAccessToken()
    writeAccessCodeToFile(access_token)
