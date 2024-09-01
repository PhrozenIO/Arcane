![Main Logo](https://raw.githubusercontent.com/PhrozenIO/Arcane/main/resources/images/banner.png)

# Arcane (βeta)

**Arcane**, previously known as [PowerRemoteDesktop](https://github.com/PhrozenIO/PowerRemoteDesktop), is a remote desktop application distinguished by its server being entirely written in PowerShell.

The server is implemented as a single PowerShell script that can also be used as a module that can be run on any Windows machine with PowerShell 5.1 or later (higher versions are recommended for better performance). It has been tested on Windows 10 (both x86-32 and x86-64 architectures) and Windows 11 x86-32, x86-64 and ARM64.

The client/viewer is a cross-platform application developed in Python, using the power of QT (PyQt6) for its graphical interface.

The project was renamed to Arcane to avoid the generic nature of the previous name and to signify a major step in the project's development: the complete rewrite of the viewer to be cross-platform.

[![Demo Video](https://raw.githubusercontent.com/PhrozenIO/Arcane/main/resources/images/video.png)](https://www.youtube.com/watch?v=h6xePrsIcQY)

> Arcane is currently in beta and is not recommended for production environments. 

## Key Features

* **Remote Desktop Streaming**: This feature allows you to stream the desktop of the remote computer to your own device. The streaming supports HDPI and scaling, providing a high-quality display on various screens and resolutions.
* **Remote Control**: With this feature, you can control the mouse (including moves, clicks, and wheel) and keyboard of the remote computer as if you were sitting in front of it.
* **Secure**: To protect the privacy and security of your remote desktop sessions, the module uses TLSv1.2 or 1.3 to encrypt the network traffic. Access to the server is granted through a challenge-based authentication mechanism that requires a user-defined complex password.
* **Network Traffic Encryption**: The module supports encrypting the network traffic using either a default X509 certificate (which requires administrator privileges) or your own custom X509 certificate.
* **Mouse Cursor Icon Synchronization**: The module also synchronizes the state of the mouse cursor icon between the viewer (virtual desktop) and the server, providing a more seamless and intuitive remote desktop experience.
* **Clipboard Synchronization**: This feature allows you to synchronize the clipboard text between the viewer (your device) and the server (the remote computer). You can easily copy and paste text between the two systems.
* **Multi-Screen Support**: If the remote computer has more than one desktop screen, you can choose which screen to capture and stream to your device.
* **View Only Mode**: This feature allows you to disable remote control abilities and simply view the screen of the remote computer. It can be useful for demonstrations or presentations.
* **Session Concurrency**: Multiple viewers can connect to a single server at the same time, allowing multiple users to collaborate on the same remote desktop.
* **Sleep Mode Prevention**: To ensure that the remote desktop remains active and responsive, the module prevents the remote computer from entering sleep mode while it is waiting for viewers to connect.
* **Streaming Optimization**: To improve the streaming speed, the module only sends updated pieces of the desktop to the viewer, reducing the amount of data transmitted over the network.

## Coming Soon

* **Profiles Manager**: This feature will allow you to save and manage multiple remote desktop configurations, including the server address, port, and authentication credentials.
* **Mutual certificate authentication**: This feature will allow you to authenticate both the server and the viewer using X509 certificates.
* **File Transfer**: This feature will allow you to transfer files between the local and remote desktops.
* **File Manager**: This feature will allow you to browse and manage files on the remote desktop.

* And more...

## Version Table

## Version Table

| Version | Protocol Version | Release Date   | Compatible Servers |
|---------|------------------|----------------|--------------------|
| 1.0.5b  | 5.0.1            | 22 August 2024 | [1.0.4](https://github.com/PhrozenIO/ArcaneServer/releases/tag/1-0-4) |

> ⓘ You can use any version of the viewer with any version of the server, as long as the protocol version matches. The protocol version ensures compatibility between the viewer and the server.

> ⓘ It is recommended to always use the latest versions of both the viewer and the server whenever possible. This ensures compatibility between the two and provides the best experience.

## Quick Setup ([PyPi.org](https://pypi.org))

The recommended way to install and launch the Arcane viewer is to first create a virtual environment. This can be done using **virtualenv** as follows:

```bash
pip install virtualenv
python -m venv venv
source venv/bin/activate
```

You can either install the official package from PyPi.org:

```bash
pip install arcane-viewer
```

or download the latest release from the official repository and install it using pip:

```bash
pip install path/to/your/downloaded/whl/file
```

Finally, you can launch the viewer with the following command:

```bash
arcane-viewer
```

### Arcane Server

For detailed instructions on how to use and configure the Arcane Server, please refer to the [official Arcane Server repository](https://github.com/PhrozenIO/ArcaneServer). The repository contains comprehensive documentation, including setup guides, configuration options, and best practices for managing your server effectively.

## Screenshots

<p align="center">
    <img width="50%" src="https://raw.githubusercontent.com/PhrozenIO/Arcane/main/resources/images/screenshots/main.png" alt="Main Window"/>
</p>

<p align="center">
    <img width="50%" src="https://raw.githubusercontent.com/PhrozenIO/Arcane/main/resources/images/screenshots/server_fingerprint.png" alt="Server Fingerprint Validation"/>
</p>

<p align="center">
    <img width="50%" src="https://raw.githubusercontent.com/PhrozenIO/Arcane/main/resources/images/screenshots/virtual_desktop.png" alt="Server Fingerprint Validation"/>
</p>

<p align="center">
    <img width="50%" src="https://raw.githubusercontent.com/PhrozenIO/Arcane/main/resources/images/screenshots/options_rd.png" alt="Remote Desktop Options"/>
</p>

<p align="center">
    <img width="50%" src="https://raw.githubusercontent.com/PhrozenIO/Arcane/main/resources/images/screenshots/options_tc.png" alt="Server Trusted Certificates"/>
</p>

## Change Log

### Version 1.0.5 (Beta)

This release focuses on improving the code structure through extensive refactoring and resolving infrequent bugs caused by previously unhandled edge cases. Type hinting has been fully implemented, and the code is now nearly ready for production deployment.

### Version 1.0.4 (Beta)

- [x] Clipboard synchronization has been implemented, allowing users to copy and paste text between the viewer and the server.
- [x] Minor bug fixes and code improvements.

### Version 1.0.3 (Beta)

- [x] The connection window interface has been streamlined, with additional options now accessible in a dedicated settings window.
- [x] Server certificate validation has been introduced. When connecting to a server for the first time, users will be prompted to trust the certificate and can choose to remember their decision.
- [x] A new settings window has been implemented, offering support for additional remote desktop parameters and managing trusted server certificates, including options to add, edit, and remove certificates.
- [x] Various code refactoring and structural improvements have been made to enhance the overall performance and maintainability of the application.

### Version 1.0.0 (Beta 2)

- [x] The issue of the Arcane Viewer Virtual Desktop Window freezing when manually closing the connection with Remote Desktop has now been fixed.
- [x] The Arcane Viewer Virtual Desktop Window now has an icon on the taskbar.
- [x] HDPI and scaling support have been improved.
- [x] Arcane Viewer Virtual Desktop Window placement has been improved.

---

![HackTheBox Meetup France](https://raw.githubusercontent.com/PhrozenIO/Arcane/main/resources/images/htb_france.png)

<p align="center">
    I’m dedicating this project to the amazing HackTheBox France Meetup community! 🇫🇷
</p>
