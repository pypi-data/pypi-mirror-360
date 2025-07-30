from functools import lru_cache
import json
import os
import re
from urllib.parse import quote
import time
import requests
from cryptography.fernet import Fernet
from dotenv import load_dotenv

try:
    from lb_tech_handler.api_handler import download_file_in_chunk_by_url
    from lb_tech_handler.common_methods import display_indented_text
except:
    from api_handler import download_file_in_chunk_by_url
    from common_methods import display_indented_text

load_dotenv()

SHAREPOINT_KEY_PATH = "sharepoint_decryption.key"

ENCRYPTED_TOKEN_PATH = ".token.enc"

GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"

DEFAULT_DRIVE_NAME = "Documents"

def generate_fernet_decryption_key():
    print("🔐 Generating new decryption key")
    key = Fernet.generate_key()
    with open(SHAREPOINT_KEY_PATH, "wb") as key_file:
        key_file.write(key)
    return key

@lru_cache(maxsize=1)
def load_fernet_decryption_key():
    
    if not os.path.exists(SHAREPOINT_KEY_PATH):
        return generate_fernet_decryption_key()
    
    with open(SHAREPOINT_KEY_PATH, "rb") as key_file:
        return key_file.read()

class SharePointClient:
    def __init__(self, tenant_id, client_id, client_secret, sharepoint_host_url):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.sharepoint_host_url = sharepoint_host_url
        self.session = requests.Session()
        self.headers = self.get_headers()
        self.session.headers = self.headers

    def authenticate(self):
        token_url = f'https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token'

        token_data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }

        response = self.session.post(token_url, data=token_data)
        if response.status_code != 200:
            raise Exception(f'Error obtaining token: {response.text}')

        token_json = response.json()

        # Add expiry timestamp
        expires_in = token_json.get("expires_in", 3600)
        token_json["expires_at"] = int(time.time()) + int(expires_in)

        self._encrypt_and_save_token(token_json)

        return token_json

    def _encrypt_and_save_token(self, token_json):
        fernet_key = load_fernet_decryption_key()
        fernet = Fernet(fernet_key)
        token_bytes = json.dumps(token_json).encode()
        encrypted_token = fernet.encrypt(token_bytes)
        with open(ENCRYPTED_TOKEN_PATH, 'wb') as f:
            f.write(encrypted_token)

    def _decrypt_token(self):
        
        fernet_key = load_fernet_decryption_key()
        fernet = Fernet(fernet_key)
        
        with open(ENCRYPTED_TOKEN_PATH, 'rb') as f:
            encrypted_token = f.read()
        decrypted_token = fernet.decrypt(encrypted_token).decode()
        return json.loads(decrypted_token)

    def get_token_json(self):
        
        if not os.path.exists(ENCRYPTED_TOKEN_PATH):
            return self.authenticate()

        try:
            token_json = self._decrypt_token()
            
            if int(time.time()) >= token_json.get("expires_at", 0):
                return self.authenticate()

            return token_json
        
        except Exception as e:
            return self.authenticate()


    def get_headers(self):
        token_json = self.get_token_json()
        
        token = token_json.get('access_token', None)
        
        if not token:
            raise Exception("No token found")
        
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }


    def get_site_id(self, site_name):
        """Get the site ID for a given SharePoint site name"""
        
        url = f'{GRAPH_API_ENDPOINT}/sites/{self.sharepoint_host_url}:/sites/{site_name}'
        
        result = self.session.get(url, headers=self.get_headers())

        if result.status_code != 200:
            raise Exception(f"Error fetching site ID: {result.text}")

        site_info = result.json()
        return site_info['id']
    
    def get_all_drives_by_site_id(self, site_id):
        
        url = f'{GRAPH_API_ENDPOINT}/sites/{site_id}/drives'
        
        result = self.session.get(url, headers=self.get_headers())
        
        if result.status_code != 200:
            raise Exception(f"Error fetching drives: {result.text}")
        
        drives = result.json()
        
        return drives
    
    def get_all_drives_by_site_name(self, site_name):
        
        site_id = self.get_site_id(site_name)
        
        return self.get_all_drives_by_site_id(site_id)
    
    def get_drive_id_by_site_id_and_drive_name(self, site_id, drive_name:str=DEFAULT_DRIVE_NAME):
        
        drives = self.get_all_drives_by_site_id(site_id)
        
        for drive in drives['value']:
            if drive['name'] == drive_name:
                return drive['id']
                    
        raise Exception(f"Drive {drive_name} not found in site {site_id}")
    
    def get_drive_id_by_site_name_and_drive_name(self, site_name, drive_name:str=DEFAULT_DRIVE_NAME):
        
        site_id = self.get_site_id(site_name)
        
        return self.get_drive_id_by_site_id_and_drive_name(site_id, drive_name)
    
    def get_folder_id_by_drive_id_and_folder_name(self, drive_id, folder_name:str):
        
        url = f'{GRAPH_API_ENDPOINT}/drives/{drive_id}/root:/{folder_name}'
        
        result = self.session.get(url, headers=self.get_headers())
        
        if result.status_code != 200:   
            raise Exception(f"Error fetching folder: {result.text}")
        
        folder = result.json()

        
        return folder['id']
    
    def list_folder_content_by_drive_id_and_folder_id(self, drive_id, folder_id:str):
        
        url = f'{GRAPH_API_ENDPOINT}/drives/{drive_id}/items/{folder_id}/children'
        
        result = self.session.get(url, headers=self.get_headers())
        
        if result.status_code != 200:
            raise Exception(f"Error fetching file: {result.text}")

        files = result.json()

        return files
    
    def get_folder_content_by_site_name_drive_name_and_folder_path(self, site_name, folder_path ,drive_name:str=DEFAULT_DRIVE_NAME):
        
        drive_id = self.get_drive_id_by_site_name_and_drive_name(site_name=site_name, drive_name=drive_name)
        
        folder_id = self.get_folder_id_by_drive_id_and_folder_name(drive_id=drive_id, folder_name=folder_path)
        
        return self.list_folder_content_by_drive_id_and_folder_id(drive_id=drive_id, folder_id=folder_id)
    
    def get_file_id_by_drive_id_and_file_name(self, drive_id, file_name:str):
        
        encoded_file_name = quote(file_name)
        
        url = f'{GRAPH_API_ENDPOINT}/drives/{drive_id}/root:/{encoded_file_name}'
                
        result = self.session.get(url, headers=self.get_headers())
        
        if result.status_code != 200:
            raise Exception(f"Error fetching file: {result.text}")
        
        file = result.json()
        
        return file['id']
    
    def get_file_id_by_site_name_drive_name_and_file_name(self, site_name, file_name:str, drive_name:str=DEFAULT_DRIVE_NAME):
        
        drive_id = self.get_drive_id_by_site_name_and_drive_name(site_name=site_name, drive_name=drive_name)
        
        return self.get_file_id_by_drive_id_and_file_name(drive_id=drive_id, file_name=file_name)
    
    def get_file_content_json_by_drive_id_and_file_id(self, drive_id, file_id:str):
        
        url = f'{GRAPH_API_ENDPOINT}/drives/{drive_id}/items/{file_id}'
        
        result = self.session.get(url, headers=self.get_headers())
        
        if result.status_code != 200:
            raise Exception(f"Error fetching file: {result.text}")
        
        file_content = result.json()
        
        return file_content
    
    def get_file_content_json_by_site_name_drive_name_and_file_name(self, site_name,file_name:str, drive_name:str=DEFAULT_DRIVE_NAME):
        
        drive_id = self.get_drive_id_by_site_name_and_drive_name(site_name=site_name, drive_name=drive_name)
        
        file_id = self.get_file_id_by_drive_id_and_file_name(drive_id=drive_id, file_name=file_name)
        
        return self.get_file_content_json_by_drive_id_and_file_id(drive_id=drive_id, file_id=file_id)
    
    def download_file_by_site_name_drive_name_and_file_name(self, site_name, file_name:str, drive_name:str=DEFAULT_DRIVE_NAME, output_path:str='',chunk_size: int = 1024 * 1024,is_download_in_chunks:bool=True,is_print_progress:bool=True):
        
        if output_path == '':
            output_path = file_name
        
        file_content_json = self.get_file_content_json_by_site_name_drive_name_and_file_name(site_name=site_name, file_name=file_name, drive_name=drive_name)
        
        download_url = file_content_json['@microsoft.graph.downloadUrl']
        
        download_file_in_chunk_by_url(
            download_url=download_url,
            output_path=output_path,
            chunk_size=chunk_size,
            headers=self.get_headers(),
            is_download_in_chunks=is_download_in_chunks,
            is_print_progress=is_print_progress
        )

        return True
    
    def get_file_version_history_by_drive_id_and_file_id(self, drive_id, file_id:str):
        
        url = f'{GRAPH_API_ENDPOINT}/drives/{drive_id}/items/{file_id}/versions'
        
        result = self.session.get(url, headers=self.get_headers())
        
        if result.status_code != 200:
            raise Exception(f"Error fetching file version history: {result.text}")
        
        file_version_history = result.json()
        
        return file_version_history
    
    def get_file_version_history_by_site_name_drive_name_and_file_name(self, site_name, file_name:str, drive_name:str=DEFAULT_DRIVE_NAME):
        
        drive_id = self.get_drive_id_by_site_name_and_drive_name(site_name=site_name, drive_name=drive_name)
        
        file_id = self.get_file_id_by_drive_id_and_file_name(drive_id=drive_id, file_name=file_name)
        
        return self.get_file_version_history_by_drive_id_and_file_id(drive_id=drive_id, file_id=file_id)
    
    def download_file_version_history_by_drive_id_and_file_id_and_version_id(self, drive_id, file_id:str, version_id:str, output_path:str='',chunk_size: int = 1024 * 1024,is_download_in_chunks:bool=True,is_print_progress:bool=True):
        
        url = f'{GRAPH_API_ENDPOINT}/drives/{drive_id}/items/{file_id}/versions/{version_id}'
        
        result = self.session.get(url, headers=self.get_headers())
        
        if result.status_code != 200:
            raise Exception(f"Error fetching file version history: {result.text}")
        
        file_content_json = result.json()
        
        download_url = file_content_json['@microsoft.graph.downloadUrl']
        
        download_file_in_chunk_by_url(
            download_url=download_url,
            output_path=output_path,
            chunk_size=chunk_size,
            headers=self.get_headers(),
            is_download_in_chunks=is_download_in_chunks,
            is_print_progress=is_print_progress
        )
        
    def download_file_version_history_by_site_name_drive_name_and_file_name_and_version_id(self, site_name, file_name:str, version_id:str, drive_name:str=DEFAULT_DRIVE_NAME, output_path:str='',chunk_size: int = 1024 * 1024,is_download_in_chunks:bool=True,is_print_progress:bool=True):
        
        drive_id = self.get_drive_id_by_site_name_and_drive_name(site_name=site_name, drive_name=drive_name)
        
        file_id = self.get_file_id_by_drive_id_and_file_name(drive_id=drive_id, file_name=file_name)
        
        return self.download_file_version_history_by_drive_id_and_file_id_and_version_id(drive_id=drive_id, file_id=file_id, version_id=version_id, output_path=output_path, chunk_size=chunk_size, is_download_in_chunks=is_download_in_chunks, is_print_progress=is_print_progress)
        
    def upload_file_by_drive_id_and_file_id_and_file_path(self, drive_id, local_file_path:str,sharepoint_file_path:str,is_print_progress:bool=False):
        
        file_size = os.path.getsize(local_file_path)
        
        if is_print_progress:
            print(f"file_size: {file_size}")
        
        if file_size > 4 * 1024 * 1024 :
            
            # upload in chunks
            
            chunk_size = 1024 * 1024 * 5
            
            upload_session = requests.Session()
            
            upload_session_url = f'{GRAPH_API_ENDPOINT}/drives/{drive_id}/root:/{sharepoint_file_path}:/createUploadSession'
            
            
            json_body = {
                "item": {
                    "@microsoft.graph.conflictBehavior": "replace",  # or "fail" or "rename"
                    "name": sharepoint_file_path.split('/')[-1]
                }
            }
            
            upload_session_result = upload_session.post(upload_session_url, headers=self.get_headers(),json=json_body)
            
            if upload_session_result.status_code != 200:
                raise Exception(f"Error creating upload session: {upload_session_result.text}")
            
            upload_session_json = upload_session_result.json()
            
            upload_url = upload_session_json['uploadUrl']
            
            
            with open(local_file_path, 'rb') as f:
                start = 0
                while start < file_size:
                    
                    print(f"Uploaded {start} bytes / {file_size} bytes",end='\r')
                    
                    end = min(start + chunk_size - 1, file_size - 1)
                    
                    f.seek(start)
                    
                    chunk_data = f.read(end - start + 1)

                    chunk_headers = self.get_headers()
                    
                    chunk_headers['Content-Length'] = str(end - start + 1)
                    
                    chunk_headers['Content-Range'] = f"bytes {start}-{end}/{file_size}"
                    
                    content_type = 'application/octet-stream'
                    
                    chunk_headers['Content-Type'] = content_type
                    
                    chunk_response = upload_session.put(upload_url, headers=chunk_headers, data=chunk_data)
                    
                    
                    
                    if chunk_response.status_code not in [200, 201, 202]:
                        raise Exception(f"Chunk upload failed: {chunk_response.status_code} - {chunk_response.text}")

                    start = end + 1
                    
            return True
        
        else:
            
            upload_url = f'{GRAPH_API_ENDPOINT}/drives/{drive_id}/root:/{sharepoint_file_path}/content'
            
            with open(local_file_path, 'rb') as f:
                file_content = f.read()
                
            result = self.session.put(upload_url, headers=self.get_headers(), data=file_content)
            
            if result.status_code != 200:
                raise Exception(f"Error uploading file: {result.text}")
            
            return True
            
        
    def upload_file_by_site_name_drive_name_and_file_path(self, site_name, local_file_path:str,sharepoint_file_path:str='', drive_name:str=DEFAULT_DRIVE_NAME,is_print_progress:bool=False):
        
        drive_id = self.get_drive_id_by_site_name_and_drive_name(site_name=site_name, drive_name=drive_name)
        
        if sharepoint_file_path == '':  
            sharepoint_file_path = local_file_path
        
        return self.upload_file_by_drive_id_and_file_id_and_file_path(drive_id=drive_id, local_file_path=local_file_path,sharepoint_file_path=sharepoint_file_path,is_print_progress=is_print_progress)
        

        
    
if __name__ == "__main__":
    TENANT_ID = os.getenv('TENANT_ID')
    
    CLIENT_ID = os.getenv('CLIENT_ID')
    
    CLIENT_SECRET = os.getenv('LOGIN_SECRET')
    
    SHAREPOINT_HOST_NAME = os.getenv('SHAREPOINT_HOST_NAME')

    client = SharePointClient(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        sharepoint_host_url=SHAREPOINT_HOST_NAME
    )

    site_name='Math-NCERT' 
    
    file_name = "Class 7/Chapter 17 - Data Handling/Questions/C7M17 - Q - Data Handling - Combined.pptx"
    
    file_history = client.get_file_version_history_by_site_name_drive_name_and_file_name(site_name=site_name, file_name=file_name)
    
    # print(file_history)
    
    display_indented_text(file_history)
    
    
     
    