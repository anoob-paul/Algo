# Import the required module from the fyers_apiv3 package
from fyers_apiv3 import fyersModel
from fyers_apiv3.FyersWebsocket import data_ws
from datetime import datetime, timedelta
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

config_file_path = 'config.ini'
config = read_config(config_file_path)

# Access the values by attribute name

global fyers
client_id = config['client_id']  #client id and secret key are fetched from config file 
secret_key = config['secret_key']  
redirect_uri = "https://www.google.co.in/"  # we can give any url here. the authcode will be appended to this link and we need this authocode to proceed
response_type = "code"  #  This value must always be “code”
grant_type = "authorization_code"  

#below function save the authocode to a txt file. 1 authocode is enough for a trading day. so once its generated we are saving to a file 
# and fetch it. When next day starts we need to delete the authcode.txt file to generate and save the new toaken
def writeAccessCodeToFile(token):
    with open('authcode.txt', 'w') as file:
        file.write(token)

#function to read the token from file 
def readAccessCodeFromFile():
    try:
        with open('authcode.txt', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

saved_token = readAccessCodeFromFile()


# function which calls the hostrical data and save to a .csv file time fram, from date, to date and symbol are loaded from config.ini file 
def generate_history(symbol,from_date, to_date,time_frame ):
    # Convert from_date and to_date to datetime objects
    from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
    to_date = datetime.strptime(to_date, "%Y-%m-%d").date()

    # Define the maximum number of days per API call
    max_days_per_call = 100

    # Calculate the number of API calls needed based on the date range
    delta_days = (to_date - from_date).days + 1
    num_api_calls = (delta_days // max_days_per_call) + (1 if delta_days % max_days_per_call != 0 else 0)

    folder_name= config['folder_location']
    folder_name= config['folder_location']
    file_ext= '.csv'
    file_name = input("Enter the file name to be given: ")
    file_path =  file_name.join([folder_name, file_ext])

    # Open the CSV file for writing 
    with open(file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        for api_call in range(num_api_calls):
            # Calculate the date range for the current API call
            start_date = from_date + timedelta(days=api_call * max_days_per_call)
            end_date = min(to_date, start_date + timedelta(days=max_days_per_call - 1))

            #  data dictionary for API call
            data = {"symbol": symbol, "resolution": time_frame, "date_format": "1", "range_from": start_date, "range_to": end_date, "cont_flag": "1"}
            # Make API call for the current date range
            historical_response = fyers.history(data)
           
            # save data as needed.
            for candle in historical_response['candles']:
                epoch_time = candle[0]
                timestamp = datetime.fromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M:%S')
                candle[0] = timestamp
                writer.writerow(candle)

#function to generate the access token for a new day. called once in a day and the access tiken will be save in the txt file 
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
    # print(' access token is :',access_token)

    return access_token


if saved_token:
    print('Token loaded from file')
    fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=saved_token, log_path="")
    f_date = config['from_date'] 
    t_date = config['to_date'] 
    t_frame = config['time_frame']
    symbol = config['symbol']
    generate_history(symbol =symbol, from_date=f_date,to_date=t_date,time_frame=t_frame)

else:
    access_token = generateAccessToken()
    writeAccessCodeToFile(access_token)


