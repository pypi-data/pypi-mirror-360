#
# Copyright (c) 2024-2025 ABXR Labs, Inc.
# Released under the MIT License. See LICENSE file for details.
#

import re
import subprocess
import time
import json
from pathlib import Path
import tempfile
import zipfile

from abxr.apk import get_package_name

from abxr.configuration_package import AbxrClientApk, ConfigurationPackage
from abxr.device_commands import BootsrapViaAuthenticationToken, BootstrapViaJsonFile, RemoveDeviceOwnership

# create custom exception for apk install failure
class DeviceInstallException(Exception):
    pass

class DeviceUninstallException(Exception):
    pass

class DeviceConfigureException(Exception):
    pass

class DeviceSetDeviceOwnerException(Exception):
    pass

class DeviceSetEnvironmentException(Exception):
    pass

class DeviceRemoveDeviceOwnerException(Exception):
    pass

class DeviceConfigureApiTokenException(Exception):
    pass

class DeviceConfigurationObjectException(Exception):
    pass



class Version:
    def __init__(self, version_str):
        parts = version_str.split('.')
        self.major = int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else 0
        self.minor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        self.build = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
        self.revision = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0

    def __repr__(self):
        return f"Version(major={self.major}, minor={self.minor}, build={self.build}, revision={self.revision})"


class SystemVersion:
    @staticmethod
    def sanitize(version):
        sanitized = re.sub(r'[^0-9.]', '', version)
        parts = sanitized.split('.')
        parts = parts[:4]
        
        return '.'.join(parts)

    @staticmethod
    def parse(version):
        try:
            sanitized_version = SystemVersion.sanitize(version)
            version_obj = Version(sanitized_version)
            return version_obj
        except Exception:
            return None    
    

class Device:
    def __init__(self, serial):
        self.serial = serial

        self.manufacturer_name = None
        self.model_name = None
        self.firmware_version = None
        self.system_version = None
        self.abi = None

        self._load_manufacturer_name()
        self._load_model_name()
        self._load_firmware_and_system_version()
        self._load_abi()

    def is_quest(self):
        return "Quest" in self.model_name
    
    def is_vive_flow(self):
        return "VIVE Flow" in self.model_name
    
    def is_pico(self):
        return "Pico" in self.model_name
    
    def is_vive_xr_elite(self):
        return "VIVE XR Series" in self.model_name
    
    def is_vive_focus_3(self):
        return "Focus 3" in self.model_name
    
    def is_magic_leap_2(self):
        return "Magic Leap 2" in self.model_name
    
    def prop(self, prop_name):
        result = subprocess.run(["adb", "-s", self.serial, "shell", "getprop", prop_name], capture_output=True, text=True)
        return result.stdout.strip()

    def _load_manufacturer_name(self):
        self.manufacturer_name = self.prop("ro.product.manufacturer")

    def _load_model_name(self):
        model_name = self.prop("pxr.vendorhw.product.model")
        
        if not model_name:
            model_name = self.prop("ro.product.model")
        
        self.model_name = model_name
    
    def _load_firmware_and_system_version(self):
        if self.is_vive_flow() or self.is_vive_xr_elite() or self.is_vive_focus_3():
            self.firmware_version = self.prop("ro.product.version")
        elif self.is_magic_leap_2():
            self.firmware_version = self.prop("ro.build.version.lumin")
        elif self.is_quest():
            self.firmware_version = self.get_installed_version("com.oculus.vrshell")
        else:
            self.firmware_version = self.get_installed_version("com.htc.mobilevr.launcher")

        if not self.firmware_version:
            self.firmware_version = self.prop("ro.build.display.id")

        self.system_version = SystemVersion.parse(self.firmware_version)

    def _load_abi(self):
        self.abi = self.prop("ro.product.cpu.abi")
    
    def is_abxr_provisioned(self):
        if self.abxr_client_version() is not None:
            return True
        return False
    
    def mkdir(self, path):
        proc = subprocess.run(["adb", "-s", self.serial, "shell", "mkdir", "-p", path])
        if proc.returncode:
            raise Exception(f"Failed to create directory {path} on device {self.serial}")
    
    def install_apk_obb_package(self, package_name):
        if type(package_name) == str:
            package_name = Path(package_name)

        if not package_name.suffix == ".zip":
            print(f"Skipping non-ZIP packaged file. {package_name}")
            raise DeviceInstallException(f"non-ZIP packaged file. {package_name}")
        
        with tempfile.TemporaryDirectory() as extract_path:
            try:
                zipfile.ZipFile(package_name, 'r').extractall(extract_path)
                package_name = None
                for file in Path(extract_path).rglob("*.apk"):
                    if not file.name.startswith("."):
                        package_name = get_package_name(file)
                        self.install_apk(file)

                for file in Path(extract_path).rglob("*.obb"):
                    if not file.name.startswith("."):
                        print(f"Installing OBB: {file}")
                        self.mkdir(f"/sdcard/Android/obb/{package_name}")
                        self.push_file(file, f"/sdcard/Android/obb/{package_name}/{file.name}")        
            
            except NotImplementedError:
                print(f"Skipping invalid zip package format. {package_name}")            
        
    
    def install_apk(self, package_name):
        if type(package_name) == str:
            package_name = Path(package_name)

        if not package_name.suffix == ".apk":
            print(f"Skipping non-APK file. {package_name}")
            raise DeviceInstallException(f"non-APK file. {package_name}")

        print(f"Installing APK: {package_name}")
        proc = subprocess.run(["adb", "-s", self.serial, "install", "-r", "-t", "-g", package_name], capture_output=True, text=True)
        if proc.returncode:
            raise DeviceInstallException(f"Failed to install {package_name} on device {self.serial} - {proc.stderr}")
        
    def push_file(self, local_file, remote_file):
        proc = subprocess.run(["adb", "-s", self.serial, "push", local_file, remote_file])
        if proc.returncode:
            raise DeviceInstallException(f"Failed to push {local_file} to {remote_file} on device {self.serial}")
        
    def set_google_play_protect(self, enable):
        if enable:
            proc = subprocess.run(["adb", "-s", self.serial, "shell", "settings", "put", "global", "verifier_verify_adb_installs", "1", "&&", "settings", "put", "global", "package_verifier_enable", "1"])
        else:
            proc = subprocess.run(["adb", "-s", self.serial, "shell", "settings", "put", "global", "verifier_verify_adb_installs", "0", "&&", "settings", "put", "global", "package_verifier_enable", "0"])
        
        if proc.returncode:
            raise Exception("Failed to toggle Google Play Protect.")
        
    def set_quest_sleep_enabled(self, enable):
        if enable:
            proc = subprocess.run(["adb", "-s", self.serial, "shell", "am", "broadcast", "-a", "com.oculus.vrpowermanager.automation_disable", "&&", "svc", "power", "stayon", "false"])
        else:
            proc = subprocess.run(["adb", "-s", self.serial, "shell", "svc", "power", "stayon", "true", "&&", "am", "broadcast", "-a", "com.oculus.vrpowermanager.prox_close"])   
        
        if proc.returncode:
            raise Exception("Failed to toggle Quest sleep.")
        
    def set_quest_guardian_enabled(self, enable):
        if enable:
            proc = subprocess.run(["adb", "-s", self.serial, "shell", "setprop", "debug.oculus.guardian_pause", "0"])
        else:
            proc = subprocess.run(["adb", "-s", self.serial, "shell", "setprop", "debug.oculus.guardian_pause", "1"])
        
        if proc.returncode:
            raise Exception("Failed to toggle Guardian.")
    
    def device_sleep(self, seconds):
        proc = subprocess.run(["adb", "-s", self.serial, "shell", "sleep", str(seconds)])
        if proc.returncode:
            raise Exception("Failed to sleep device.")
        
    def send_keycode_and_sleep(self, keycode, seconds):
        proc = subprocess.run(["adb", "-s", self.serial, "shell", "input", "keyevent", str(keycode)])
        if proc.returncode:
            raise Exception("Failed to send keycode.")
        
        self.device_sleep(seconds)

    def set_package_enabled(self, package_name, enable):
        if enable:
            proc = subprocess.run(["adb", "-s", self.serial, "shell", "pm", "disable-user", "--user 0", package_name])
        else:
            proc = subprocess.run(["adb", "-s", self.serial, "shell", "pm", "enable", "--user 0", package_name])
        
        if proc.returncode:
            raise Exception(f"Failed to toggle {package_name} enablement.")

    def delete_quest_accounts(self):
        home = (3, 3)
        up = (19, 0.5)
        down = (20, 0.5)
        right = (22, 0.5)
        enter = (66, 0.5)

    
        requires_extra_down = False
        if self.system_version and self.system_version.major >= 62:
            requires_extra_down = True

        account_delete_steps = [
            home,
            "am start -n 'com.android.settings/.Settings$AccountDashboardActivity'",
            "sleep 5",
            down,
            up,
            down,
        ]

        if requires_extra_down:
            account_delete_steps.append(down)

        account_delete_steps += [
            enter,
            down,
            down,
            enter,
            down,
            right,
            enter,
            enter,
            down,
            down,
            enter,
            down,
            right,
            enter,
            enter,
            down,
            down,
            enter,
            down,
            right,
            enter,
            enter,
            down,
            down,
            enter,
            down,
            right,
            enter,
            "sleep 5",
        ]

        for step in account_delete_steps:
            if type(step) == tuple:
                self.send_keycode_and_sleep(*step)
            elif type(step) == str:
                proc = subprocess.run(["adb", "-s", self.serial, "shell", step])
                if proc.returncode:
                    raise Exception(f"Failed to execute step: {step}")
            else:
                raise Exception(f"Invalid step: {step}")


    def send_configuration_package(self, config_pkg):
        if not type(config_pkg) == ConfigurationPackage:
            raise Exception("You must provide a ConfigurationPackage object.")
        
        if type(config_pkg) == str|Path:
            config_pkg = ConfigurationPackage(config_pkg)

        if config_pkg.is_xrdm2:
            client_settings_file_location = "/sdcard/Setup/settings.json"
        else:
            client_settings_file_location = "/sdcard/ArborXR/Settings/settings.json"

        for app in config_pkg.apps:
            with tempfile.TemporaryDirectory() as extract_path:
                item = config_pkg.extract_item(app, extract_path)
                self.install_apk(item)

        for obb_packaged_app in config_pkg.obb_packaged_apps:
            with tempfile.TemporaryDirectory() as extract_path:
                item = config_pkg.extract_item(obb_packaged_app, extract_path)
                self.install_apk_obb_package(item)

        for file in config_pkg.files:
            with tempfile.TemporaryDirectory() as extract_path:
                item = config_pkg.extract_item(file, extract_path)
                target_file_location = file.split("/files")[-1]
                if target_file_location.startswith("/~"):
                    target_file_location = target_file_location.split("/~")[-1]
           
                self.push_file(item, target_file_location)

        for video in config_pkg.videos:
            with tempfile.TemporaryDirectory() as extract_path:
                item = config_pkg.extract_item(video, extract_path)
                target_file_location = video.split("/videos")[-1]
                if target_file_location.startswith("/~"):
                    target_file_location = target_file_location.split("/~")[-1]
                    
                self.push_file(item, f"/sdcard/ArborXR/videos{target_file_location}")

        for launcher_media in config_pkg.launcher_media:
            with tempfile.TemporaryDirectory() as extract_path:
                item = config_pkg.extract_item(launcher_media, extract_path)
                target_file_location = launcher_media.split("/launcher-media")[-1]
                self.push_file(item, f"/sdcard/launcher-media{target_file_location}")

        # Config package v2 only
        for images in config_pkg.images:
            with tempfile.TemporaryDirectory() as extract_path:
                item - config_pkg.extract_item(images, extract_path)
                target_file_location = images.split("/images")[-1]
                self.push_file(item, f"/sdcard/ArborXR/Media{target_file_location}")
        

        with tempfile.NamedTemporaryFile() as f:
            f.write(config_pkg.read_settings_json_from_zip())
            f.flush()
            self.push_file(f.name, client_settings_file_location)
        
        if config_pkg.is_xrdm2:
            command = BootstrapViaJsonFile(client_settings_file_location)
            command_json = json.dumps(command.to_dict())

            proc = subprocess.run(["adb", "-s", self.serial, "shell", "dumpsys", "activity", "service", "xrdm.adb.AdbService",  f"'''{command_json}'''"])
            if proc.returncode:
                raise DeviceConfigureException("Failed to configure device with settings.json")
        else:
            proc = subprocess.run(["adb", "-s", self.serial, "shell", "am", "broadcast", "-n", "app.xrdm.client/.SetupDeviceReceiver", "-a", "CONFIGURE_DEVICE", "-e", "ClientSettingsFile", client_settings_file_location])
            if proc.returncode:
                raise DeviceConfigureException("Failed to configure device with settings.json")

    def force_stop_and_sleep(self, package_name, seconds):
        proc = subprocess.run(["adb", "-s", self.serial, "shell", "am", "force-stop", package_name])
        if proc.returncode:
            raise Exception(f"Failed to force stop {package_name} on device {self.serial}")
        
        self.device_sleep(seconds)

    def reboot(self):
        proc = subprocess.run(["adb", "-s", self.serial, "reboot"])
        if proc.returncode:
            raise Exception(f"Failed to reboot device {self.serial}")

    def set_device_owner(self):
        proc = subprocess.run(["adb", "-s", self.serial, "shell", "dpm", "set-device-owner", "app.xrdm.client/.AdminReceiver"], capture_output=True, text=True)
        if proc.returncode:
            if "Not allowed to set the device owner because there are already some accounts on the device" in proc.stderr:
                if self.is_quest():
                    self.force_stop_and_sleep("com.oculus.shellenv", 10.0)
                    self.delete_quest_accounts()
                    self.set_device_owner()

                elif self.is_vive_flow():
                    htcLauncherPackageName = "com.htc.vrs.launcher"

                    self.set_package_enabled(htcLauncherPackageName, False)
                    time.sleep(1)
                    self.set_device_owner()
                    self.set_package_enabled(htcLauncherPackageName, True)
                    self.send_keycode_and_sleep(3, 0.0)

            else:
                raise DeviceSetDeviceOwnerException("Failed to set device owner." + proc.stderr)

    def set_production_environment(self):
        proc = subprocess.run(["adb", "-s", self.serial, "shell", "echo production > /sdcard/.xrdm-environment"])
        if proc.returncode:
            raise DeviceSetEnvironmentException("Failed to set production environment.")

    def remove_device_owner(self):
        proc = subprocess.run(["adb", "-s", self.serial, "shell", "am", "broadcast", "-n", "app.xrdm.client/.AdminRemover", "-a", "REMOVE_DEVICE_OWNER"])
        max_wait_sec = 10
        wait_sec = 0
        if proc.returncode == 0:
            while True and wait_sec < max_wait_sec:
                proc = subprocess.run(["adb", "-s", self.serial, "shell", "dumpsys", "device_policy", "|", "grep", "\"app.xrdm.client/.AdminReceiver\""], capture_output=True, text=True)
                if proc.stdout == "":
                    break
                print("Waiting for device owner removal...")
                time.sleep(1)
                wait_sec += 1
            
            print("Device owner removal complete.")
            return True
        raise DeviceRemoveDeviceOwnerException("Failed to remove device owner.")
    
    def remove_device_owner_v2(self):
        command = RemoveDeviceOwnership()
        command_json = json.dumps(command.to_dict())

        proc = subprocess.run(["adb", "-s", self.serial, "shell", "dumpsys", "activity", "service", "xrdm.adb.AdbService",  f"'''{command_json}'''"])
        max_wait_sec = 10
        wait_sec = 0
        if proc.returncode == 0:
            while True and wait_sec < max_wait_sec:
                proc = subprocess.run(["adb", "-s", self.serial, "shell", "dumpsys", "device_policy", "|", "grep", "\"app.xrdm.client/.AdminReceiver\""], capture_output=True, text=True)
                if proc.stdout == "":
                    break
                print("Waiting for device owner removal...")
                time.sleep(1)
                wait_sec += 1
            
            print("Device owner removal complete.")
            return True
        raise DeviceRemoveDeviceOwnerException("Failed to remove device owner.")

    def uninstall_apk(self, package_name):
        proc = subprocess.run(["adb", "-s", self.serial, "uninstall", package_name], capture_output=True, text=True)
        if proc.returncode:
            raise DeviceUninstallException(f"Failed to uninstall {package_name} on device {self.serial} - {proc.stderr}")

    def configure_api_token_authentication(self, config_pkg):
        if not type(config_pkg) == ConfigurationPackage:
            raise Exception("You must provide a ConfigurationPackage object.")
        
        if type(config_pkg) == str|Path:
            config_pkg = ConfigurationPackage(config_pkg)

        settings = config_pkg.settings

        if settings.is_xrdm2:
            token = settings["token"]
            group = settings["group"]
            configurations = settings["configurations"]

            command = BootsrapViaAuthenticationToken(token, group, configurations)

            command_json = json.dumps(command.to_dict())

            proc = subprocess.run(["adb", "-s", self.serial, "shell", "dumpsys", "activity", "service", "xrdm.adb.AdbService",  f"'''{command_json}'''"])

            if proc.returncode:
                raise DeviceConfigurationObjectException("Failed to configuration device with object from config package")
        else:
            api_token_auth = {}
            api_token_auth["apiToken"] = settings["apiToken"]
            api_token_auth["deviceGroup"] = {}
            api_token_auth["deviceGroup"]["id"] = settings["deviceGroup"]["id"]
            api_token_auth_json = json.dumps(api_token_auth)

            proc = subprocess.run(["adb", "-s", self.serial, "shell", "am", "broadcast", "-n", "app.xrdm.client/.SetupDeviceReceiver", "-a", "CONFIGURE_API_TOKEN", "-e", "ApiTokenAuth", f"'''{api_token_auth_json}'''"])
            if proc.returncode:
                raise DeviceConfigureApiTokenException("Failed to configure device with API token authentication.")
            
    def get_installed_version(self, package_name):
        result = subprocess.run(["adb", "-s", self.serial, "shell", "dumpsys", "package", package_name], capture_output=True, text=True)
        if result.returncode != 0:
            return None
        
        for line in result.stdout.split("\n"):
            if "versionName=" in line:
                return line.split("=")[1].strip()
    
        return None
    
    def abxr_client_version(self):
        return self.get_installed_version(AbxrClientApk.PACKAGE_NAME)
    
    def is_packaged_installed(self, package_name):
        return self.get_installed_version(package_name) is not None
    
    def __str__(self):
        return self.serial

