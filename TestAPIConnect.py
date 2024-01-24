# Import the required module from the fyers_apiv3 package
from fyers_apiv3 import fyersModel

client_id = "FAAAAAMMMMMMM-100"  # this values to be replaced
secret_key = "HHHHHHHHHH"    # this values to be replaced
redirect_uri = "https://www.google.co.in/" 
response_type = "code"  #  This value must always be “code”
grant_type = "authorization_code"  

# Create a session model with the provided credentials
session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key,
    redirect_uri=redirect_uri,
    response_type=response_type,
    grant_type=grant_type
)
# Generate the auth code using the session model
response = session.generate_authcode()
print(response)

auth_code = input("Enter Authcode: ")

# Set the authorization code in the session object
session.set_token(auth_code)
# Generate the access token using the authorization code
access_response = session.generate_token()
access_token = access_response['access_token']
print('access token is :',access_token)

fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")
profile = fyers.get_profile()

# Print the  profile details to make sure we got the connectivity working
print(' Profile is :',profile)

