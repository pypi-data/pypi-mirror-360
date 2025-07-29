import subprocess
import sys
import pexpect
import platform
import getpass

sudo_password = None
sudo_password_label = "🔐Password:"
MAX_RETRIES = 3


def run(cmd: str) -> tuple[bool, str]:
    global sudo_password
    global sudo_password_label

    if platform.system() == "Windows":
        try:
            res = subprocess.run(cmd, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out = (res.stdout + res.stderr).strip()
            return 0, out
        except subprocess.CalledProcessError as e:
            print(e)
            out = (e.stdout or '') + (e.stderr or '')
            return e.returncode, out.strip()

    if cmd.strip().startswith("sudo"):
        for attempt in range(MAX_RETRIES):
            if sudo_password is None:
                try:
                    sudo_password = getpass.getpass(sudo_password_label)
                except Exception as e:
                    print(f"Failed to read the password: {str(e)}", file=sys.stderr)
                    sys.exit(10)

            try:
                child = pexpect.spawn(f"sudo -S {cmd[5:].strip()}")
                child.expect("Password:")
                child.sendline(sudo_password)
                i = child.expect([pexpect.EOF, "Sorry, try again."])
                if i == 1:
                    sudo_password_label = "🔐 Incorrect password, try again:"
                    sudo_password = None
                    continue
                return 0, child.before.decode().strip()
            except Exception as e:
                print(e)
                return 1, str(e)
        print("❌Too many incorrect password attempts.", file=sys.stderr)
        sys.exit(10)
    else:
        try:
            res = subprocess.run(cmd, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out = (res.stdout + res.stderr).strip()
            return 0, out
        except subprocess.CalledProcessError as e:
            print(e)
            out = (e.stdout or '') + (e.stderr or '')
            return e.returncode, out.strip()
