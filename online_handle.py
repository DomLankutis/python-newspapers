import onedrivesdk
from onedrivesdk.helpers import GetAuthCodeServer

'''
Authentication for the OneDrive app
Set the following to:
    redirect_uri:       - Set according to platform you want to use with you app
    client_secret:      - The password used by your app
    app_id:             - The ID used by your app (Token)
'''

redirect_uri = 'http://localhost'
client_secret = ''
app_id = ''

scopes = ['wl.signin', 'wl.offline_access', 'onedrive.readwrite']

client = onedrivesdk.get_default_client(
        client_id=app_id, scopes=scopes)
auth_url = client.auth_provider.get_auth_url(redirect_uri)
code = GetAuthCodeServer.get_auth_code(auth_url, redirect_uri)
client.auth_provider.authenticate(code, redirect_uri, client_secret)

def upload(file):
    """Uploads the desired file to the users OneDrive"""
    client.item(drive='me', id='root').children[file].upload(file)
    print("Uploaded file {}".format(file))

def dowload(file):
    """Downloads the desired file to the root of the application"""
    try:
        root = client.item(drive='me', id='root').children[file].get()
        client.item(drive='me', id=root.id).download(file)
        print("Got file {}".format(file))
    except:
        pass
