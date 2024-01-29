# Import the required module from the fyers_apiv3 package
from fyers_apiv3 import fyersModel
from fyers_apiv3.FyersWebsocket import data_ws
import datetime
from tabulate import tabulate
import os
import pandas as pd
import csv


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


def savehistorytoFile(histrorical_response):
    # Open the CSV file for writing
    with open('C:\codebase\Python\Algo\historical data\BN_5minsData_Q4_2023.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write the headers to the CSV file
        writer.writerow(['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        # Write the data to the CSV file
        for candle in histrorical_response['candles']:
            epoch_time = candle[0]
            timestamp = datetime.datetime.fromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M:%S')
            candle[0] = timestamp
            writer.writerow(candle)


def generate_history(symbol,from_date, to_date,time_frame ):
    data = {"symbol":symbol,"resolution":time_frame,"date_format":"1","range_from":from_date,"range_to":to_date,"cont_flag":"1"}
    historical_response = fyers.history(data)
    savehistorytoFile(historical_response)


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
    f_date = "2024-01-01"
    t_date = "2024-01-02"
    t_frame =5
    symbol ="NSE:NIFTYBANK-INDEX"
    generate_history(symbol =symbol, from_date=f_date,to_date=t_date,time_frame=t_frame)

else:
    access_token = generateAccessToken()
    writeAccessCodeToFile(access_token)

# profile = fyers.get_profile()
# funds = fyers.funds()
# print(profile)
# print(funds)

