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

| Version        | Protocol Version | Release Date   |
|----------------|------------------|----------------|
| 1.0.0b1 (Beta) | 5.0.0b1          | 01 August 2024 |
| 1.0.0b2 (Beta) | 5.0.0b1          | 05 August 2024 |
| 1.0.3 (Beta)   | 5.0.0b1          | 12 August 2024 |
| 1.0.4 (Beta)   | 5.0.1            | 15 August 2024 |

> You can use any version of the viewer with any version of the server, as long as the protocol version matches. The protocol version ensures compatibility between the viewer and the server.

## Components

### Arcane Viewer

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

#### Fast Use

The easiest way to install and run the server is by installing the PowerShell module from the PowerShell Gallery:

> Please note that you must have administrative privileges to install a new module. To do this, open an elevated PowerShell prompt and execute the following command:

```powershell
Install-Module -Name Arcane_Server
```

Before running the server, you must import the module into your PowerShell session:

> Please note that depending on your system configuration, you may need to run the following command to temporarily bypass the execution policy in order to run an unsigned script:
> `powershell.exe -executionpolicy bypass`

```powershell
Import-Module Arcane_Server
```

Once the module is installed, you can run the server using the following command:
    
```powershell
Invoke-ArcaneServer
```

That's it, you're ready to go! 🚀

#### Available Module Functions

```powershell
Invoke-ArcaneServer
```

##### ⚙️ Supported Options:
 
| Parameter              | Type             | Default    | Description  |
|------------------------|------------------|------------|--------------|
| ServerAddress          | String           | 0.0.0.0    | IP address representing the local machine's IP address |
| ServerPort             | Integer          | 2801       | The port number on which to listen for incoming connections |
| SecurePassword         | SecureString     | None       | SecureString object containing the password used for authenticating remote viewers (recommended) |
| Password               | String           | None       | Plain-text password used for authenticating remote viewers (not recommended; use SecurePassword instead) |
| DisableVerbosity       | Switch           | False      | If specified, the program will suppress verbosity messages |
| UseTLSv1_3             | Switch           | False      | If specified, the program will use TLS v1.3 instead of TLS v1.2 for encryption (recommended if both systems support it) |
| Clipboard              | Enum             | Both       | Specify the clipboard synchronization mode (options include 'Both', 'Disabled', 'Send', and 'Receive'; see below for more detail) |
| CertificateFile        | String           | None       | A file containing valid certificate information (x509) that includes the private key  |
| EncodedCertificate     | String           | None       | A base64-encoded representation of the entire certificate file, including the private key |
| ViewOnly               | Switch           | False      | If specified, the remote viewer will only be able to view the desktop and will not have access to the mouse or keyboard |
| PreventComputerToSleep | Switch           | False      | If specified, this option will prevent the computer from entering sleep mode while the server is active and waiting for new connections |
| CertificatePassword    | SecureString     | None       | Specify the password used to access a password-protected x509 certificate provided by the user | 

##### Server Address Examples

| Value             | Description                                                              | 
|-------------------|--------------------------------------------------------------------------|
| 127.0.0.1         | Only listen for connections from the localhost (usually for debugging purposes) |
| 0.0.0.0           | Listen for connections on all network interfaces, including the local network and the internet                       |

##### Clipboard Mode Enum Properties

| Value             | Description                                        | 
|-------------------|----------------------------------------------------|
| Disabled          | Clipboard synchronization is disabled on both the viewer and server sides |
| Receive           | Only incoming clipboard data is allowed                |
| Send              | Only outgoing clipboard data is allowed                 |
| Both              | Clipboard synchronization is allowed on both the viewer and server sides  |

##### ⚠️ Important Notices

1. It is recommended to use SecurePassword instead of a plain-text password, even if the plain-text password is being converted to a SecureString.
2. If you do not specify a custom certificate using 'CertificateFile' or 'EncodedCertificate', a default self-signed certificate will be generated and installed for the local user.
3. If you do not specify a SecurePassword or Password, a random, complex password will be generated and displayed in the terminal (this password is temporary).

##### Examples

```powershell
Invoke-ArcaneServer -ListenAddress "0.0.0.0" -ListenPort 2801 -SecurePassword (ConvertTo-SecureString -String "urCompl3xP@ssw0rd" -AsPlainText -Force)

Invoke-ArcaneServer -ListenAddress "0.0.0.0" -ListenPort 2801 -SecurePassword (ConvertTo-SecureString -String "urCompl3xP@ssw0rd" -AsPlainText -Force) -CertificateFile "c:\certs\phrozen.p12"
```

##### Generate your Certificate

```
openssl req -x509 -sha512 -nodes -days 365 -newkey rsa:4096 -keyout phrozen.key -out phrozen.crt
```

Then export the new certificate (**must include private key**).

```
openssl pkcs12 -export -out phrozen.p12 -inkey phrozen.key -in phrozen.crt
```

##### Integrate to server as a file

Use `CertificateFile`. Example: `c:\tlscert\phrozen.crt`

##### Integrate to server as a base64 representation

Encode an existing certificate using PowerShell

```powershell
[convert]::ToBase64String((Get-Content -path "c:\tlscert\phrozen.crt" -Encoding byte))
```
or on Linux / Mac systems

```
base64 -i /tmp/phrozen.p12
```

You can then pass the output base64 certificate file to parameter `EncodedCertificate` (One line)

## Viewer Screenshots

<p align="center">
    <img width="50%" src="https://raw.githubusercontent.com/PhrozenIO/Arcane/main/resources/images/screenshots/main.png" alt="Main Window"/>
</p>

<p align="center">
    <img width="50%" src="https://raw.githubusercontent.com/PhrozenIO/Arcane/main/resources/images/screenshots/server_fingerprint.png" alt="Server Fingerprint Validation"/>
</p>

<p align="center">
    <img width="50%" src="https://raw.githubusercontent.com/PhrozenIO/Arcane/main/resources/images/screenshots/options_rd.png" alt="Remote Desktop Options"/>
</p>

<p align="center">
    <img width="50%" src="https://raw.githubusercontent.com/PhrozenIO/Arcane/main/resources/images/screenshots/options_tc.png" alt="Server Trusted Certificates"/>
</p>

## Change Log

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

I’m dedicating this project to the amazing HackTheBox France Meetup community! 🇫🇷

![HackTheBox Meetup France](https://raw.githubusercontent.com/PhrozenIO/Arcane/main/resources/images/htb_france.png)
