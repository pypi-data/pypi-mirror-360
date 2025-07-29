# Auterion CLI

Command line utility to interact with Auterion Devices and Apps


**Type `auterion-cli --help` in your command line to get help.**<br/>
For help for a sub-command, type `auterion-cli <subcommand> --help`



### Contents

- [Installation](#installation)
- [Command reference](#command-reference)
- [Example usage - app development](#app-dev-workflow)


## Installation
<a name="installation"></a>

Use pip

```
pip3 install auterion-cli
```

This will install in your local user directory. 

**Note:** Make sure your `~/.local/bin` directory is in the `PATH` to access it.

## Command reference
<a name="command-reference"></a>

### Discover / select devices

"Selecting" a device makes auterion-cli perform all actions against that selected device. 
In case no device is selected, auterion-cli will default to any device reachable on `10.41.1.1`

- `auterion-cli device discover`: Discover reachable Auterion devices
- `auterion-cli device select <serial>`: Select a reachable device to connect to
- `auterion-cli device deselect`: De-select any currently selected device

### Device information

- `auterion-cli info`: Get information about the selected device
- `auterion-cli report`: Download diagnostic report from selected device

### App management

- `auterion-cli app list`: List all currently installed apps on the device
- `auterion-cli app start <app name>`: Start a stopped app
- `auterion-cli app stop <app name>`: Stop a running app
- `auterion-cli app restart <app name>`: Restart an app
- `auterion-cli app enable <app name>`: Enable autostart for an app
- `auterion-cli app disable <app name>`: Disable autostart for an app
- `auterion-cli app status <app name>`: Get current status for an app
- `auterion-cli app logs <app name> [-f]`: Display logs for an app. `-f` for live log feed

### Development workflow

- `auterion-cli app init`: Create a new app project
- `auterion-cli app build`: Build the app project in current folder. Creates *.auterionos* file in build folder.
- `auterion-cli app install <file>`: Install the *.auterionos* app file to Skynode
- `auterion-cli app remove <app name>`: Remove an app from Skynode

#### Incremental updates

- `auterion-cli app patch --create-config` to create a default config. If no `-c my-config.yml` is specified, `app-patch.yml` will be used
- Modify config. Add directory/files per app service image listed in the config. E.g.
  ```
  # fast-update config for auterion-cli app fast-update command
  services:
    my-service:
      files:
      - /ros_ws
      - /sdk_ws
  ```
  Paths are absolute to the root directory of the docker image for the related service.
- `auterion-cli app patch` for skynode
- `auterion-cli app patch -c my-config.yml --ip 10.41.200.2 --simulation` for simulation


## Workflow - App development
<a name="app-dev-workflow"></a>


### Step 1: Bootstrap a new app

In the first step, we instantiate a base template for our app.

```
auterion-cli app init
```

This creates a directory named `app-template-cpp` with a base application structure.
You can open this directory and look and edit the files.

### Step 2: Build the app

> **Tip:** Install [`pigz`](https://zlib.net/pigz/) on your system to significantly speed up compression of the app. `sudo apt install pigz` (Debian/Ubuntu) or `brew install pigz` (macOS).

Go to the directory where you bootstrapped your app. Run

```
auterion-cli app build
```

To build your app. If this succeeds, it will generate a `.auterionos` file in a `build` sub-directory


### Step 3: Make sure the app-base is installed on your Skynode

In case the app build command notified you with a message like this:

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                      │
│  Your app requires the Auterion app-base-v2 to be installed on your device.          │
│                                                                                      │
│  Get app-base-v2.auterionos from Auterion Suite.                                     │
│                                                                                      │
│  NOTE: The app-base has to be installed on the Skynode before you install your app.  │
│        You can install the app-base like an app:                                     │
│        `auterion-cli app install <path to app-base-v2.auterionos>`                   │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

You need an *app-base* to be installed on your Skynode for your app to run.
To verify that you have the app-base installed, you can run

```
auterion-cli app list
```

In case you don't have the app base installed yet, download it from the link indicted, and install it with 

```
auterion-cli app install <PATH TO>/app-base-v0.auterionos

```



### Step 4: Install your app

You can install your app with 

```
auterion-cli app install build/<YOUR APP>.auterionos
```

This will install the app on your Skynode.


### Step 5: Verify that your app is working

To see if your app is installed and running, you can run

```
auterion-cli app list
```


You can get a live feed of the logs of your app with

```
auterion-cli app logs <YOUR APP> -f
```

## Hardware Support
<a name="hardware-support"></a>

When adding new device targets (as defined per AuterionOS targets), it shall be integrated to `auterion-cli`:
* `AUTERION_DEVICES`
* `PLATFORM_ALIAS` - whether its arm64/amd64 device
* `DEVICE_ALIAS` - optionally if `auterion-cli` should translate between user friendly name to actual target, eg. `ainode` to `jetson`.

Once the following changes are in place, the app may be build for the respective target by adding it `target-platform: ` in `auterion-app.yml`.

_ATTENTION:_ As most of Auterion Apps by design depend on `app-base`, it has to be installed on target. If new target was added, existing `app-base` will fail to install, as the device is not present in the header. There is no need to tag a new release (eg. `v3`) of the `app-base`, but rather repack the mender artifact to update header with the new target name. This can be done as following:
* Download current `app-base` mender artifact.
* Rename it from `app-base*.auterionos` to `app-base*.tar`
* Open live archive (eg. with File Roller on Ubuntu)
* Open `headers.tar`, open header file, and append new target name to the array
* Save & close `headers.tar`
* Recompute `sha256` of `header.tar`, and update `manifest` file accordinly
* Save & close `app-base*.tar`
* Rename it from `app-base*.tar` to `app-base*.auterionos`
* Reupload the app to Cloudsmith with the same name (eg. `app-base-v2`) but under new _Cloudsmith_ version (eg. `4`)

## Run tests

Run all python tests locally by

```
python -m pytest -s auterioncli/commands/app_sdk/tests/
```