import dropbox

APP_KEY = ""
APP_SECRET = ""

# Create an OAuth2 flow with offline access
flow = dropbox.DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET, token_access_type='offline')
authorize_url = flow.start()

# Redirect the user to authorize the app
print("1. Go to: " + authorize_url)
print("2. Click 'Allow' (you might have to log in first).")
print("3. Copy the authorization code.")
code = input("Enter the authorization code here: ")

try:
    # Exchange the authorization code for an access token and refresh token
    result = flow.finish(code)
    access_token, refresh_token = result.access_token, result.refresh_token

    print("Access token:", access_token)
    print("Refresh token:", refresh_token)

    # Store the refresh token securely (e.g., in a file, database, or environment variable)
    # ...

    # Create a Dropbox client using the refresh token
    dbx = dropbox.Dropbox(oauth2_refresh_token=refresh_token, app_key=APP_KEY)

    # Use the Dropbox client to make API calls
    try:
        metadata = dbx.files_get_metadata('/path/to/file')
        print("File metadata:", metadata)
    except dropbox.exceptions.AuthError as err:
        if err.error.is_expired_access_token():
            print("Access token expired, refreshing...")
            dbx.refresh_access_token()
except Exception as err:
    print(f"Exception: {err}")
