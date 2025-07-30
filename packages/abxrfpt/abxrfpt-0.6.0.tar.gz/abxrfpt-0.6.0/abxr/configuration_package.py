#
# Copyright (c) 2024-2025 ABXR Labs, Inc.
# Released under the MIT License. See LICENSE file for details.
#

import json
import re
from pathlib import Path
import zipfile

class AbxrClientApk:
    PACKAGE_NAME = "app.xrdm.client"

    def __init__(self, path):
        if type(path) == str:
            path = Path(path)

        if not path.exists():
            raise Exception(f"Error: {path} does not exist.")
        
        self.path = path
        self.version = None

        self._load_version()

    def _load_version(self):
        self.version = self.get_client_version_from_filename(self.path)

    def get_client_version_from_filename(self, filename):
        pattern = r'(\d{4}\.\d{1,2}\.\d+)'
        match = re.search(pattern, str(filename))
        if match:
            return match.group(1)
        return None
    
class AbxrLauncherApk:
    PACKAGE_NAME = "app.xrdm.launcher"

    def __init__(self, path):
        if type(path) == str:
            path = Path(path)

        if not path.exists():
            raise Exception(f"Error: {path} does not exist.")
        
        self.path = path
        self.version = None

        self._load_version()

    def _load_version(self):
        self.version = self.get_launcher_version_from_filename(self.path)

    def get_launcher_version_from_filename(self, apk_filename):
        pattern = r'(\d{4}\.\d{1,2}\.\d+)'
        match = re.search(pattern, str(apk_filename))
        if match:
            return match.group(1)
        return None


class ConfigurationPackage:
    def __init__(self, path):
        if type(path) == str:
            path = Path(path)

        self.path = path
        self.version = None
        self.is_xrdm2 = False
        self.settings = None
        self.zip_file = None
        self.client_apk = None
        self.launcher_apk = None

        self.apps = []
        self.obb_packaged_apps = []
        self.files = []
        self.videos = []
        self.launcher_media = []

        self._open()
        self._load_settings_json()

        self._find_client_apk()
        self._find_launcher_apk()
        self._find_apps()
        self._find_files()
        self._find_videos()
        self._find_launcher_media()
        self._find_images()

        self._split_obb_packaged_apps_from_apps()

    def _open(self):
        try:
            self.zip_file = zipfile.ZipFile(self.path, 'r')
        except zipfile.BadZipFile:
            raise Exception(f"Error: {self.path} is not a valid zip file")

    def _load_settings_json(self):
        try:
            self.settings = json.loads(self.read_settings_json_from_zip().decode('utf-8'))
            self.version = self.settings.get("version", None)
            if self.version == "2.0.0":
                self.is_xrdm2 = True
                print("Found a v2 config package")
        except Exception as e:
            raise Exception(f"Error parsing settings.json: {e}")
        
    def _find_client_apk(self):
        client_apk = [f for f in self.zip_file.namelist() if 'client/app.xrdm.client' in f]
        
        if len(client_apk) > 1:
            raise Exception("Multiple ArborXR APK files found in the zip file.")
        elif len(client_apk) == 0:
            raise Exception("ArborXR Client APK not found in the zip file.")

        self.client_apk = client_apk[0]

    def _find_launcher_apk(self):
        launcher_apk = [f for f in self.zip_file.namelist() if 'launcher/app.xrdm.launcher' in f]

        if len(launcher_apk) > 1:
            raise Exception("Multiple ArborXR APK files found in the zip file.")
        elif len(launcher_apk) == 1:         
            self.launcher_apk = launcher_apk[0]
        else:
            self.launcher_apk = None

    def _find_apps(self):
        self.apps = [f for f in self.zip_file.namelist() if 'apps/' in f]

    def _find_files(self):
        self.files = [f for f in self.zip_file.namelist() if 'files/' in f]

    def _find_videos(self):
        self.videos = [f for f in self.zip_file.namelist() if 'videos/' in f]

    def _find_launcher_media(self):
        self.launcher_media = [f for f in self.zip_file.namelist() if 'launcher-media/' in f]

    def _find_images(self):
        self.images = [f for f in self.zip_file.namelist() if 'images/' in f]

    def _split_obb_packaged_apps_from_apps(self):
        self.obb_packaged_apps = [f for f in self.apps if '.zip' in f]
        self.apps = [f for f in self.apps if '.zip' not in f]

    def created_at(self):
        try:
            return self.settings["createdAt"]
        except Exception as e:
            print("Error getting created at: {e}")
            return None

    def device_group(self):
        try:
            if self.is_xrdm2:
                return self.settings["group"]
            else:
                return self.settings["deviceGroup"]
        except Exception as e:
            print("Error getting device group: {e}")
            return None

    def model_name(self):
        try:
            return self.settings["deviceModel"]["name"]
        except Exception as e:
            print("Error getting device model name: {e}")
            return None
        
    def model_names(self):
        try:
            if self.is_xrdm2:
                return self.settings["deviceModel"]["enrollmentIdentifiers"]
            else:
                return self.settings["deviceModel"]["modelNames"]
        except Exception as e:
            print("Error getting device model names: {e}")
            return None
        
    def extract_item(self, item, output_path):
        try:
            path = self.zip_file.extract(item, output_path)
            return path
        except Exception as e:
            raise Exception(f"Error extracting {item} to {output_path}: {e}")
        
    def extract_client_apk_from_zip(self, output_path):        
        try:
            path = self.extract_item(self.client_apk, output_path)
            return AbxrClientApk(path)
        except Exception as e:
            raise Exception(f"Error extracting ArborXR APK from zip: {e}")
    
    def read_settings_json_from_zip(self):
        try:
            settings_json_locations = [f for f in self.zip_file.namelist() if 'settings.json' in f]
            if len(settings_json_locations) > 1:
                raise Exception("Multiple settings.json files found in the zip file.")
            
            settings_json_location = settings_json_locations[0]

            if settings_json_location:
                with self.zip_file.open(settings_json_location) as settings_file:
                    return settings_file.read()
            else:
                raise Exception("settings.json not found in the zip file.")
        except Exception as e:
            raise Exception(f"Error reading settings.json from zip: {e}")
        