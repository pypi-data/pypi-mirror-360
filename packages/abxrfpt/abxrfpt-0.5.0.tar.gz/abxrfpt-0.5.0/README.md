# ArborXR Field Provisioning Tools

This project is a collection of tools to help provision and recover Android devices on ArborXR's XRDM. The provisioning tools can be used interactively on a computer, or deployed onto the ArborXR Field Provisioning Device (FPD). The tools are intended to be used without the need for network connectivity to the ArborXR XRDM backend.

### Features
- Provision new Android devices (XR, Phone, Tablet) with an XRDM configuration package.
- Re-provision existing devices with a configuration package.
- Replace an XRDM client with an older or newer version.


## Table of Contents
- [Features](#features)
- [Field Provisioning Device (FPD)](#field-provisioning-device-fpd)
  - [Hardware Information](#hardware-information)
  - [Setup Mode](#setup-mode)
  - [Provision Mode](#provision-mode)
- [Development Environment Setup](#development-environment-setup)
- [Running the Provisioning Tool](#running-the-provisioning-tool)

## Field Provisioning Device (FPD)

The ArborXR Field Provisioning Device is a headless computer which can deploy XRDM1 Configuration Packages without the need for internet access. 

### Hardware Information

Currently supported hardware is currently a Raspberry Pi Zero 2 W running RBPI OS 64-bit. There are custom modifications made to the base image to support the dual mode USB (host/gadget). The image customizations are currenly not well documented, and in the future should be captured in code to be able to apply to a fresh RBPI OS image. 

`device_start.sh` - This is a specific script which is launched by `systemd` to automatically start the provisioning tool on the FPD. There is a check to see if a certain GPIO is set to check for "Setup" or "Provision" mode is set.

### Setup Mode

When the FPD selector switch is in "Setup" Mode, the device can be connected to any computer and will show up as a "Mass Storage Device". This is where the user can place XRDM Configuration Packages and/or an alternate client build. 

You must follow a specific directory structure:
```
/configuration-packages
```
Place XRDM configuration packages here. Currently undetermined behavior if you place multiple configuration packages which apply to the same device. We don't have logic which can select the "best" package. Make sure you only place one per device type
```
/client
```
(Optional) You can place an alternate client to use instead of what's included in the configuration package. This can be used when needing to downgrade the client version to recover a device.
```
field-provisioning-tools-update.zip
```
This is the update package. It will be read as soon as the device boots into "Provision" mode. It will automatically be deleted as soon as its applied.

### Provision Mode

When the FPD selector switch is in "Provision" Mode, the device can be connected to any Android device which USB debugging is enabled, and it will automatically start provisioning the device with any available configuration package that matches the device model connected.

This all happens in a headless manner, but once the device is provisioned the FPD will stop, and wont start another provisioning run until a new device is detected.

Currently XR devices require USB power injection due to the FPD HW not being able to supply enough current. Please use the included wall outlet and connector.

## Development Environment Setup

Python 3.x is required. 

1. Clone the repository:

2. Create and activate a virtual environment:
    ```sh
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Running the Provisioning Tool

To run the provisioning tool, use the following command to install it into the path:

```sh
install.sh
```

Then it can be run using

```sh
abxr-provision
```
On non-Linux systems (MacOS/Windows) will start the provisioner in "single shot mode". It loads with the default options:
- Searches for configuration packages in $HOME/abxr/configuration-packages
- Searches for any special client APK overrides in $HOME/abxr/client

You can override the base path by setting the `ABXR_ARCHIVE_PATH` environment variable before starting the provisioning tool.

You can also pass arguments to the application which allow to specify exact locations of the configuration packages, client, or specific device serial numbers to match. This is useful when using the application in a multi-device environment

```sh
abxr-provision --config-package <path-to-config-packages> --client <path-to-client-for-override> --device-serial <specific-device-to-target> --force-upgrade
```
All of the command line switches are optional, and can be used interchangably. The force upgrade option will always reinstall the client even if the versions match.

## Building a update package for the provisioning hardware

```sh
build_update_package.sh
```
This will package the project into a zip archive called `field-provisioning-tools-update.zip` that can be placed in the root directory of the HW provisioning device when mounted in "Setup Mode". When the device is booted back in provisioning mode, the update will automatically be applied.