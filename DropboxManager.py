"""
Created by Samba Chennamsetty on 6/14/2023.
"""

import configparser
import os
from datetime import date, timedelta

import dropbox


def remove_folder():
    today_date = date.today() + timedelta(days=1)
    today_date_str = today_date.strftime("%Y-%m-%d")

    # Delete the local folder
    if os.path.exists(today_date_str):
        try:
            os.rmdir(today_date_str)
        except OSError as e:
            print(f"Error while removing a folder: {today_date_str}: {e}")
    else:
        print(f"The folder {today_date_str} doesn't exists.")


class DropboxManager:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.properties')

        # Get the access token from config file by section and key
        access_token = config['dropbox']['access.token']
        self.dbx = dropbox.Dropbox(access_token)

    def create_folder(self, folder_path):
        try:

            # removes dropbox yesterday folder
            self._remove_dropbox_folder()

            # create local folder
            os.makedirs(f'{folder_path}', exist_ok=True)

            # create dropbox folder
            self.dbx.files_create_folder_v2(f"/{folder_path}")
            print(f"Folder created: {folder_path}")
        except dropbox.exceptions.ApiError as e:
            if e.error.is_path() and e.error.get_path().is_conflict():
                print(f"Folder already exists: {folder_path}")
            else:
                print(f"Error while creating a folder: {folder_path}: {e}")

    def _remove_dropbox_folder(self):
        today_date = date.today()
        today_date_str = today_date.strftime("%Y-%m-%d")

        try:
            metadata = self.dbx.files_get_metadata(f"/{today_date_str}")
        except dropbox.exceptions.ApiError as e:
            print(f"Folder doesn't exists: {today_date_str}")
            return

        # Delete the dropbox folder
        self.dbx.files_delete_v2(f"/{today_date_str}")
        print(f"The folder {today_date_str} has been successfully deleted.")

    def upload_files(self, folder_path):
        try:
            for root, dirs, files in os.walk(folder_path):
                for filename in files:
                    if filename.lower().endswith('.pdf'):  # Filter for PDF files
                        local_file_path = os.path.join(root, filename)
                        print(f"Uploading {local_file_path} file")
                        dropbox_file_path = os.path.join(f'/{folder_path}', filename).replace("\\", "/")
                        with open(local_file_path, 'rb') as f:
                            self.dbx.files_upload(f.read(), dropbox_file_path, mode=dropbox.files.WriteMode.overwrite)
                        os.remove(local_file_path)

        except dropbox.exceptions.ApiError as e:
            print(f"Exception while uploading a file to Dropbox: {e}")
