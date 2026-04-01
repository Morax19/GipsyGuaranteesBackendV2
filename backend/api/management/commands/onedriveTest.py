import os
import requests
from django.core.management.base import BaseCommand
from api.onedrive import get_onedrive_headers

class Command(BaseCommand):
    help = 'Test OneDrive file upload'

    def handle(self, *args, **options):
        try:
            headers = get_onedrive_headers()
            FILE_PATH = "/home/danielhdez19/Work/GipsyGuaranteesBackendV2/backend/api/management/commands/media/invoice-template.png"
            ONEDRIVE_FOLDER = "GARANTIAS/Facturas"

            with open(FILE_PATH, 'rb') as f:
                file_content = f.read()

            file_name = os.path.basename(FILE_PATH)

            # Microsoft Graph API PUT URL
            url = f"https://graph.microsoft.com/v1.0/users/desarrollo@grupogipsy.com/drive/root:/{ONEDRIVE_FOLDER}/{file_name}:/content"

            response = requests.put(url, headers=headers, data=file_content)

            if response.status_code in [200, 201]:
                print("✅ Upload successful!")
                print("File URL:", response.json().get('webUrl'))
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(response.json())
        
        except Exception as e:
            print(f"An error occurred: {str(e)}")