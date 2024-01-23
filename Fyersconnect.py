# Import the required module from the fyers_apiv3 package
from fyers_apiv3 import fyersModel
import os


global fyers
client_id = "FAAAAAMMMMMMM-100"  # this values to be replaced
secret_key = "HHHHHHHHHH"    # this values to be replaced
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
    print('Token loaded from file:', saved_token)
    fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=saved_token, log_path="")

else:
    access_token = generateAccessToken()
    writeAccessCodeToFile(access_token)

# profile = fyers.get_profile()
# funds = fyers.funds()
# print(profile)
# print(funds)

data = {
    "symbol":"NSE:SBIN-EQ",
    "resolution":"D",
    "date_format":"1",
    "range_from":"2023-12-01",
    "range_to":"2023-12-31",
    "cont_flag":"1"
}

hist_data = fyers.history(data=data)
print(hist_data)



