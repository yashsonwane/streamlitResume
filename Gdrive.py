import pandas as pd
import pickle
import os,io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from Google import Create_Service


# try:
#     CLIENT_SECRET_FILE = r'client_secrets.json'
#     API_NAME = 'drive'
#     API_VERSION = 'v3'
#     SCOPES = ['https://www.googleapis.com/auth/drive']


#     service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
# except:
#     pass


CLIENT_SECRET_FILE = r'client_secrets.json'
API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'

pickle_file = f'token_{API_SERVICE_NAME}_{API_VERSION}.pickle'

with open(pickle_file, 'rb') as token:
    cred = pickle.load(token)
print(f"creaddd  {cred}")
service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
print(service)
print(API_SERVICE_NAME, 'service created successfully')



def get_shareable_link(file_id):

    # Update Sharing Setting
    file_id = file_id

    #type for request. find all permision here "https://developers.google.com/drive/api/v3/reference/permissions/create#:~:text=and%20authorization%20page.-,Request%20body,that%20belong%20to%20a%20view.%20published%20is%20the%20only%20supported%20value.,-writable"
    request_body = {
        'role': 'reader',
        'type': 'anyone',
    }
    #create permission
    response_permission = service.permissions().create(
        fileId=file_id,
        body=request_body
    ).execute()

    # print(response_permission)
    
    # Print Sharing URL
    response_share_link = service.files().get(
        fileId=file_id,
        fields='webViewLink'
    ).execute()

    shareable_link = response_share_link.get('webViewLink')

    return shareable_link



def get_drive_folder_list(folder_id):
        
    folder = folder_id
    query = f"parents = '{folder}'"

    response = service.files().list(q=query).execute()
    # print(response)
    filess = response.get('files')

    nextPageToken = response.get('nextPageToken')

    # print(nextPageToken)
    # while nextPageToken:
    #     response = service.files().list(q=query).execute()
    #     filess.extend(response.get("files"))
    #     nextPageToken = response.get('nextPageToken')
    print("inside get_drive_folder")
    drive_list_df = pd.DataFrame(filess)
    return drive_list_df


#get shareable links for particular folder
def get_list_of_shareable_links(files_df):
    dict = {"Name":[],"Link":[]}
    for i in range(len(files_df)):
        link=get_shareable_link(files_df.iloc[i].id)
        dict["Name"].append(files_df.iloc[i]["name"])
        dict["Link"].append(link)
        print(link)
    return pd.DataFrame(dict)

#download files from drive
def download_file(file_id,file_name):
    file_id =[file_id]
    file_name =[file_name]

    for file_id, file_name in zip(file_id,file_name):
        request = service.files().get_media(fileId=file_id)

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fd=fh, request=request)
        done=False

        while not done:
            status, done = downloader.next_chunk()
            print(f'Download progress {status.progress() * 100}')

        fh.seek(0)

        with open(os.path.join(r'.\temp', file_name), 'wb') as f:
            f.write(fh.read())



